import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/chris-filmmaking-studio/scripts/studio.py"
spec = importlib.util.spec_from_file_location("studio", SCRIPT)
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name)
        env = patch.dict(os.environ, {**{k:v for k,v in os.environ.items() if k.upper() in {"SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE"}}, "HF_STUDIO_HOME": str(self.state / "state")}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.manifest = self.state / "batch.json"
        self.job = json.loads((ROOT / "examples/one-clip.json").read_text())["jobs"][0]
        self.manifest.write_text(json.dumps({"jobs": [self.job, {**self.job, "label": "Second"}]}))

    def make_quote(self, price="0.123"):
        with patch.object(studio, "api", return_value={"usd": price}):
            return studio.quote(self.manifest)["run_id"]

    def test_decimal_total_and_no_generation(self):
        with patch.object(studio, "api", return_value={"usd": "0.123"}) as call:
            result = studio.quote(self.manifest)
        self.assertEqual(result["batch_quoted_usd"], "0.246")
        self.assertTrue(all(c.args[1].startswith("/estimate/") for c in call.call_args_list))
        self.assertNotIn("prompt", json.dumps(result))
        self.assertIsNone(result["final_billed_usd"])

    def test_bad_prices_block_quote(self):
        for price in ("NaN", "Infinity", "-1", "nonsense", True, None):
            with self.subTest(price=price), patch.object(studio, "api", return_value={"usd": price}):
                with self.assertRaises(studio.StudioError):
                    studio.quote(self.manifest)

    def test_missing_usd_blocks(self):
        with patch.object(studio, "api", return_value={"credits": "1.2"}):
            with self.assertRaises(studio.StudioError):
                studio.quote(self.manifest)

    def test_image_and_path_injection_rejected(self):
        for slug in ("provider/model/text-to-image", "https://evil.test/to-video", "a/../text-to-video", "a/text-to-video?x=1"):
            with self.subTest(slug=slug), self.assertRaises(studio.StudioError):
                studio.validate_model(slug)

    def test_price_increase_submits_nothing(self):
        identifier = self.make_quote("0.10")
        with patch.object(studio, "api", return_value={"usd": "0.11"}) as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "10")
        self.assertTrue(all(c.args[1].startswith("/estimate/") for c in call.call_args_list))
        self.assertEqual(studio.read_record(identifier)["state"], "quoted")

    def test_lower_budget_submits_nothing(self):
        identifier = self.make_quote("0.10")
        with patch.object(studio, "api", return_value={"usd": "0.10"}) as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "0.19")
        self.assertEqual(call.call_count, 2)

    def test_expired_quote_submits_nothing(self):
        identifier = self.make_quote()
        record = studio.read_record(identifier)
        record["created_at"] -= 901
        studio.private_write(studio.record_path(identifier), record)
        with patch.object(studio, "api") as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "1")
        call.assert_not_called()

    def accepted(self):
        rid = str(uuid.uuid4())
        return {"request_id": rid, "status": "queued", "status_url": studio.API + f"/requests/{rid}/status"}

    def test_submit_then_resume_without_duplicate_charge(self):
        identifier = self.make_quote("0.10")
        accepted = [self.accepted(), self.accepted()]
        with patch.object(studio, "api", side_effect=[{"usd": "0.10"}, {"usd": "0.10"}, *accepted]) as call:
            result = studio.run(identifier, "0.20")
        self.assertEqual(call.call_count, 4)
        self.assertEqual(result["state"], "submitted")
        with patch.object(studio, "api") as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "0.20")
        call.assert_not_called()
        with patch.object(studio, "api", side_effect=[{"status": "completed", "video": {"url": "https://cdn.example/one.mp4"}}, {"status": "failed"}]) as call:
            result = studio.status(identifier)
        self.assertTrue(all(c.args[0] == "GET" for c in call.call_args_list))
        self.assertEqual(result["state"], "finished")
        self.assertEqual(result["completed_estimated_usd"], "0.10")
        self.assertIsNone(result["clips"][1]["billed_usd"])
        self.assertIn("No charge expected", result["clips"][1]["cost_note"])

    def test_uncertain_submission_is_not_retried_and_preserves_partial(self):
        identifier = self.make_quote("0.10")
        with patch.object(studio, "api", side_effect=[{"usd": "0.10"}, {"usd": "0.10"}, self.accepted(), studio.StudioError("timeout")]) as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "0.20")
        self.assertEqual(call.call_count, 4)
        record = studio.read_record(identifier)
        self.assertEqual(record["state"], "needs_reconciliation")
        self.assertEqual(record["jobs"][0]["state"], "queued")
        self.assertEqual(record["jobs"][1]["state"], "submission_unknown")
        with patch.object(studio, "api") as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "1")
        call.assert_not_called()

    def test_untrusted_status_url_preserves_id(self):
        identifier = self.make_quote("0.10")
        accepted = self.accepted()
        accepted["status_url"] = "https://evil.example/status"
        with patch.object(studio, "api", side_effect=[{"usd": "0.10"}, {"usd": "0.10"}, accepted]):
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "0.20")
        self.assertEqual(studio.read_record(identifier)["jobs"][0]["request_id"], accepted["request_id"])

    def test_host_allowlist(self):
        for url in ("http://api.higgsfield.ai/x", "https://api.higgsfield.ai.evil.test/x", "https://api.higgsfield.ai@evil.test/x", "https://api.higgsfield.ai:444/x"):
            with self.subTest(url=url), self.assertRaises(studio.StudioError):
                studio.http("GET", url, key="example:dummy")

    def test_redirect_is_not_followed(self):
        self.assertIsNone(studio.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test"))

    def test_private_key_file_and_doctor_no_secret(self):
        studio.save_key("example:dummy")
        path = studio.home() / "credentials.json"
        if os.name == "posix":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), patch.object(studio, "api") as call:
            self.assertEqual(studio.main(["doctor"]), 0)
        call.assert_not_called()
        self.assertNotIn("example", out.getvalue())
        self.assertIn('"verified": false', out.getvalue())

    def test_upload_never_forwards_api_credentials(self):
        image = self.state / "reference.png"
        image.write_bytes(b"test-fixture-not-a-real-image")
        slot = {"upload_url": "https://storage.example/upload", "public_url": "https://cdn.example/image.png", "upload_headers": {"Content-Type": "image/png", "x-amz-tagging": "retention=temporary"}}
        with patch.object(studio, "api", return_value=slot), patch.object(studio, "http", return_value={}) as call:
            result = studio.upload(image)
        self.assertNotIn("key", call.call_args.kwargs)
        self.assertEqual(call.call_args.kwargs["headers"]["x-amz-tagging"], "retention=temporary")
        self.assertEqual(result["public_url"], slot["public_url"])

    def test_lock_blocks_duplicate_submission(self):
        identifier = self.make_quote()
        studio.record_path(identifier).with_suffix(".lock").touch()
        with patch.object(studio, "api") as call:
            with self.assertRaises(studio.StudioError):
                studio.run(identifier, "1")
        call.assert_not_called()

    def test_private_onboarding_http(self):
        env = dict(os.environ, HF_STUDIO_HOME=str(self.state / "web-state"))
        proc = subprocess.Popen([sys.executable, str(SCRIPT), "onboard", "--web"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        def cleanup():
            if proc.poll() is None:
                proc.kill()
            proc.communicate()
        self.addCleanup(cleanup)
        line = proc.stdout.readline()
        self.assertTrue(line, proc.stderr.read() if proc.poll() is not None else "No setup response")
        info = json.loads(line)
        url = info["private_setup_url"]
        with urllib.request.urlopen(url) as response:
            page = response.read().decode()
            self.assertIn('type="password"', page)
            self.assertEqual((response.headers["Cache-Control"], response.headers["Referrer-Policy"]), ("no-store", "same-origin"))
        payload = b"key=fixture-id%3Afixture-secret"
        bad = urllib.request.Request(url, data=payload, headers={"Origin": "https://evil.example"})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(bad)
        self.assertEqual(caught.exception.code, 403)
        origin = url.rsplit("/", 1)[0]
        good = urllib.request.Request(url, data=payload, headers={"Origin": origin})
        with urllib.request.urlopen(good) as response:
            self.assertEqual(response.status, 200)
        stdout, stderr = proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, 0, stderr)
        self.assertNotIn("fixture-secret", line + stdout + stderr)
        self.assertTrue((self.state / "web-state/credentials.json").exists())


class InstallerTests(unittest.TestCase):
    def test_install_is_idempotent_and_preserves_changed_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            cmd = [sys.executable, str(ROOT / "scripts/install.py"), "--destination", temp]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0)
            target = Path(temp) / "chris-filmmaking-studio/SKILL.md"
            target.write_text(target.read_text() + "\nUser customization\n")
            third = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(third.returncode, 0)
            self.assertIn("User customization", target.read_text())


if __name__ == "__main__":
    unittest.main()
