#!/usr/bin/env python3
"""Higgsfield API Studio: private onboarding, live quotes and durable receipts.

Python 3.10+, standard library only. Never automatically retries a paid POST.
"""
import argparse
import getpass
import http.server as http_server
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from decimal import Decimal, InvalidOperation

API = "https://api.higgsfield.ai"
TERMINAL = {"completed", "failed", "nsfw", "canceled", "cancelled"}
QUOTE_TTL = 900


class StudioError(Exception):
    pass


def home():
    override = os.environ.get("HF_STUDIO_HOME")
    if override:
        return Path(override)
    legacy = Path.home() / ".config/higgsfield-api-studio"
    if os.name == "nt" and not (legacy / "credentials.json").exists():
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "HiggsfieldAPIStudio"
    return legacy


def private_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name + "." + secrets.token_hex(8) + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def money(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise StudioError("Price must be a finite, nonnegative USD amount.") from None
    if not result.is_finite() or result < 0:
        raise StudioError("Price must be a finite, nonnegative USD amount.")
    return result


def validate_key(key):
    if not isinstance(key, str) or not re.fullmatch(r"[^\s:]+:[^\s:]+", key):
        raise StudioError("Use the full KEY_ID:KEY_SECRET value from the API console.")
    return key


def credentials():
    key = os.environ.get("HF_KEY") or os.environ.get("HF_CREDENTIALS")
    if not key:
        kid = os.environ.get("HF_API_KEY_ID") or os.environ.get("HF_API_KEY")
        secret = os.environ.get("HF_API_KEY_SECRET") or os.environ.get("HF_API_SECRET")
        if kid and secret:
            key = kid + ":" + secret
    if not key:
        path = home() / "credentials.json"
        if not path.exists():
            raise StudioError("What's your Higgsfield API key? Run onboard --web for private entry.")
        if os.name == "posix" and path.stat().st_mode & 0o077:
            raise StudioError("Credential file permissions must be 600. Fix permissions before continuing.")
        key = json.loads(path.read_text())["key"]
    return validate_key(key)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def https_url(url, authenticated=False):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise StudioError("Expected an HTTPS URL without embedded credentials.")
    if authenticated and (parts.netloc != "api.higgsfield.ai" or parts.fragment):
        raise StudioError("Refusing to send credentials outside api.higgsfield.ai.")
    return url


def http(method, url, data=None, key=None, headers=None):
    https_url(url, authenticated=key is not None)
    request_headers = {"User-Agent": "higgsfield-api-studio/1.0.0"}
    request_headers.update(headers or {})
    if key is not None:
        request_headers["Authorization"] = "Key " + validate_key(key)
    if isinstance(data, dict):
        data = json.dumps(data).encode()
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=60) as response:
            body = response.read()
            return json.loads(body) if body and method != "PUT" else {}
    except urllib.error.HTTPError as error:
        # Do not print provider bodies: they may reflect sensitive input.
        hints = {401: "Check API credentials.", 402: "Check API balance.",
                 403: "Check account/model access.", 422: "Check the model's input schema.",
                 429: "Rate limited; do not automatically resubmit paid jobs."}
        raise StudioError(f"API HTTP {error.code}. {hints.get(error.code, 'Check the console; no automatic retry was made.')}") from None
    except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError):
        raise StudioError("Network or response error. Submission may have succeeded; inspect the console before trying again.") from None


def api(method, path, data=None):
    url = path if path.startswith("https://") else API + path
    return http(method, url, data, credentials())


def validate_model(model, media_type="video"):
    if not isinstance(model, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_.-]+)+", model):
        raise StudioError("Use the exact production model slug, not a URL.")
    if any(part in {".", ".."} for part in model.split("/")):
        raise StudioError("Invalid model slug.")
    if media_type not in {"video", "image"}:
        raise StudioError("media_type must be video or image.")
    if media_type == "video" and not any(token in model for token in ("to-video", "motion-transfer", "video-reference", "image-reference")):
        raise StudioError("For explicit API image requests set media_type to image. Otherwise verify the documented video endpoint.")
    return model


def load_manifest(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise StudioError("Manifest must be an object containing jobs.")
    jobs = data.get("jobs")
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 100:
        raise StudioError("Manifest needs 1-100 jobs; one entry per generation.")
    for job in jobs:
        if not isinstance(job, dict) or set(job) - {"model", "input", "label", "media_type"}:
            raise StudioError("Each job accepts model, input, optional label and media_type.")
        validate_model(job.get("model"), job.get("media_type", "video"))
        if not isinstance(job.get("input"), dict):
            raise StudioError("Each job needs a model-specific input object.")
    return jobs


def estimate(job):
    result = api("POST", "/estimate/" + validate_model(job["model"], job.get("media_type", "video")), job["input"])
    if not isinstance(result, dict) or "usd" not in result:
        raise StudioError("Estimate did not return usd. No paid generation was submitted.")
    return money(result["usd"])


def record_path(identifier):
    try:
        identifier = str(uuid.UUID(identifier))
    except (ValueError, AttributeError):
        raise StudioError("Expected a quote/run UUID.") from None
    return home() / "runs" / (identifier + ".json")


def read_record(identifier):
    path = record_path(identifier)
    if not path.exists():
        raise StudioError("Quote/run not found on this machine.")
    return json.loads(path.read_text())


def quote(path):
    jobs = load_manifest(path)
    quoted = []
    for job in jobs:
        quoted.append({**job, "quoted_usd": str(estimate(job)), "state": "not_submitted"})
    record = {"id": str(uuid.uuid4()), "created_at": time.time(), "currency": "USD",
              "state": "quoted", "jobs": quoted,
              "total_quoted_usd": str(sum((money(j["quoted_usd"]) for j in quoted), Decimal(0)))}
    private_write(record_path(record["id"]), record)
    return receipt(record)


def receipt(record):
    rows = []
    expected = Decimal(0)
    for i, job in enumerate(record["jobs"], 1):
        state = job["state"]
        no_charge = state in {"failed", "nsfw", "canceled", "cancelled"}
        quoted = job.get("submit_quoted_usd", job["quoted_usd"])
        if state == "completed":
            expected += money(quoted)
        rows.append({"clip": i, "label": job.get("label", f"Clip {i}"), "model": job["model"], "media_type": job.get("media_type", "video"),
                     "settings": {k: v for k, v in job["input"].items() if k in
                                  {"duration", "resolution", "aspect_ratio", "generate_audio", "sound", "mode", "quality"}},
                     "status": state, "request_id": job.get("request_id"),
                     "quoted_usd": quoted, "billed_usd": None,
                     "cost_note": "No charge expected under provider refund policy; verify billing." if no_charge else
                                  "Authenticated estimate; final billed amount is not exposed by this client.",
                     "output": job.get("output")})
    return {"run_id": record["id"], "state": record["state"], "currency": "USD", "clips": rows,
            "batch_quoted_usd": record["total_quoted_usd"],
            "completed_estimated_usd": str(expected), "final_billed_usd": None,
            "billing": "https://console.higgsfield.ai", "quote_expires_at": record["created_at"] + QUOTE_TTL}


def run(identifier, max_usd):
    path = record_path(identifier)
    lock = path.with_suffix(".lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
    except FileExistsError:
        raise StudioError("This run is locked. Use status; do not submit it again.") from None
    try:
        record = read_record(identifier)
        if record["state"] != "quoted":
            raise StudioError("Quote already used. Use status to resume tracking without new charges.")
        if not 0 <= time.time() - record["created_at"] <= QUOTE_TTL:
            raise StudioError("Quote expired. Request a fresh quote before generating.")
        cap = min(money(max_usd), money(record["total_quoted_usd"]))
        prices = [estimate(job) for job in record["jobs"]]
        if sum(prices, Decimal(0)) > cap:
            raise StudioError("Current estimate exceeds the quote or spending ceiling. No jobs submitted; quote again.")
        record["state"] = "submitting"
        record["max_usd"] = str(cap)
        private_write(path, record)
        for job, price in zip(record["jobs"], prices):
            # Persist before POST. A crash/time-out must never cause blind resubmission.
            job["state"] = "submission_unknown"
            job["submit_quoted_usd"] = str(price)
            private_write(path, record)
            try:
                result = api("POST", "/" + job["model"], job["input"])
                rid = result["request_id"]
                uuid.UUID(rid)
                job["request_id"] = rid
                # Save the ID before validating URLs, preserving recovery information.
                private_write(path, record)
                job["status_url"] = https_url(result["status_url"], authenticated=True)
                if result.get("cancel_url"):
                    job["cancel_url"] = https_url(result["cancel_url"], authenticated=True)
                job["state"] = result.get("status", "queued")
                if job["state"] in TERMINAL:
                    job["output"] = {k: result[k] for k in ("video", "videos", "audio", "audios", "image", "images") if k in result}
                private_write(path, record)
            except (StudioError, KeyError, ValueError):
                record["state"] = "needs_reconciliation"
                private_write(path, record)
                raise StudioError(f"Batch stopped. Run {identifier} needs reconciliation in the console. Use status; do not resubmit. Some clips may already be charged.") from None
        record["state"] = "submitted"
        private_write(path, record)
        return receipt(record)
    finally:
        lock.unlink(missing_ok=True)


def status(identifier):
    record = read_record(identifier)
    if record["state"] in {"quoted", "submitting"}:
        if record["state"] == "quoted":
            return receipt(record)
        if record_path(identifier).with_suffix(".lock").exists():
            raise StudioError("Submission is running. Wait for it before polling.")
    for job in record["jobs"]:
        if job.get("request_id") and job["state"] not in TERMINAL:
            url = job.get("status_url", API + "/requests/" + str(uuid.UUID(job["request_id"])) + "/status")
            result = api("GET", url)
            job["state"] = result["status"]
            job["output"] = {k: result[k] for k in ("video", "videos", "audio", "audios", "image", "images") if k in result}
            private_write(record_path(identifier), record)
    if all(j["state"] in TERMINAL for j in record["jobs"]):
        record["state"] = "finished"
    private_write(record_path(identifier), record)
    return receipt(record)


def upload(path):
    path = Path(path)
    mime = mimetypes.guess_type(path.name)[0]
    if mime not in {"image/jpeg", "image/png", "image/webp", "image/gif", "audio/wav", "audio/x-wav", "video/mp4"}:
        raise StudioError("Use PNG, JPEG, WEBP, GIF, WAV or MP4 input media.")
    data = path.read_bytes()
    slot = api("POST", "/files/generate-upload-url", {"content_type": mime})
    headers = slot.get("upload_headers") or {"Content-Type": mime}
    if any(k.lower() in {"authorization", "cookie", "host"} for k in headers):
        raise StudioError("Unexpected sensitive upload header; upload stopped.")
    http("PUT", https_url(slot["upload_url"]), data, headers=headers)
    return {"public_url": https_url(slot["public_url"]), "note": "Uploaded input media to Higgsfield; no generation submitted."}


def save_key(key):
    private_write(home() / "credentials.json", {"key": validate_key(key.strip())})


def onboard_web(timeout=600):
    token = secrets.token_urlsafe(32)
    saved = []

    class Handler(http_server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code, body):
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body.encode())

        def valid(self):
            return self.path == "/" + token and self.headers.get("Host") == host

        def do_GET(self):
            if not self.valid():
                return self.reply(404, "Not found")
            self.reply(200, """<!doctype html><meta name="viewport" content="width=device-width"><title>Chris Filmmaking Studio</title>
<style>body{font:18px system-ui;background:#f6f3ec;color:#182b23;max-width:580px;margin:10vh auto;padding:24px}h1{font-size:38px}input,button{font:inherit;padding:15px;box-sizing:border-box;width:100%;margin:10px 0;border-radius:10px;border:1px solid #becbc3}button{background:#146345;color:white;cursor:pointer}small{color:#53645b}</style>
<p>CHRIS FILMMAKING STUDIO - PRIVATE SETUP</p><h1>What's your Higgsfield API key?</h1>
<p>Paste the full <b>KEY_ID:KEY_SECRET</b> value from your API console.</p>
<form method="post"><input name="key" type="password" required autocomplete="off" aria-label="Higgsfield API key"><button>Save key privately</button></form>
<small>Saved on this computer with restricted file permissions. Not encrypted at rest. Never sent to GitHub or the chat. Saving does not generate content or spend credits.</small>""")

        def do_POST(self):
            if not self.valid() or self.headers.get("Origin") != "http://" + host:
                return self.reply(403, "Invalid origin")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 8192:
                    return self.reply(400, "Invalid request size")
                data = urllib.parse.parse_qs(self.rfile.read(length).decode())
                save_key(data.get("key", [""])[0])
            except (StudioError, ValueError):
                return self.reply(400, "Use KEY_ID:KEY_SECRET. Go back and try again.")
            saved.append(True)
            self.reply(200, "<title>Key saved</title><h1>Key saved privately.</h1><p>Return to ChatGPT and say: Ready.</p><p>No generation was run. The first live quote will verify account access.</p>")

    server = http_server.HTTPServer(("127.0.0.1", 0), Handler)
    host = f"127.0.0.1:{server.server_port}"
    server.timeout = 1
    print(json.dumps({"question": "What's your Higgsfield API key?", "private_setup_url": f"http://{host}/{token}",
                      "note": "Open on the same computer. Enter the key in the form, not in chat."}), flush=True)
    deadline = time.monotonic() + timeout
    try:
        while not saved and time.monotonic() < deadline:
            server.handle_request()
    finally:
        server.server_close()
    if not saved:
        raise StudioError("Private setup expired. Run onboard --web again.")
    return {"configured": True, "verified": False, "next": "Request a live quote; saving the key does not verify it."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    onboarding = commands.add_parser("onboard", help="Ask for the key privately; no paid requests")
    onboarding.add_argument("--web", action="store_true", help="Private localhost password form (same computer only)")
    commands.add_parser("doctor", help="Check local key presence without printing it or making requests")
    q = commands.add_parser("quote", help="Estimate every job with authenticated account pricing")
    q.add_argument("manifest")
    r = commands.add_parser("run", help="Submit an authorized quoted batch once")
    r.add_argument("quote_id")
    r.add_argument("--max-usd", required=True)
    s = commands.add_parser("status", help="Resume tracking; never resubmit")
    s.add_argument("run_id")
    u = commands.add_parser("upload", help="Upload a reference image/video for generation")
    u.add_argument("path")
    args = parser.parse_args(argv)
    try:
        if args.command == "onboard":
            if args.web:
                result = onboard_web()
            else:
                if not sys.stdin.isatty():
                    raise StudioError("Use a user-operated terminal or onboard --web; do not pass keys as command arguments.")
                save_key(getpass.getpass("What's your Higgsfield API key? "))
                result = {"configured": True, "verified": False}
        elif args.command == "doctor":
            credentials()
            result = {"configured": True, "verified": False, "python": sys.version.split()[0],
                      "next": "A successful authenticated quote verifies access without generating content."}
        elif args.command == "quote":
            result = quote(args.manifest)
        elif args.command == "run":
            result = run(args.quote_id, args.max_usd)
        elif args.command == "status":
            result = status(args.run_id)
        else:
            result = upload(args.path)
        print(json.dumps(result, indent=2), flush=True)
        return 0
    except (StudioError, OSError, ValueError, KeyError) as error:
        message = str(error) if isinstance(error, StudioError) else "Local file or data error. Check the input files and permissions."
        print(json.dumps({"error": message}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
