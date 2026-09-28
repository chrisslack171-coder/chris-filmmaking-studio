import json
import unittest
from unittest.mock import patch
import test_studio
from test_studio import studio
import uuid

class ImageTests(unittest.TestCase):
    setUp = test_studio.StudioTests.setUp
    make_quote = test_studio.StudioTests.make_quote
    def image_quote(self):
        self.manifest.write_text(json.dumps({"jobs":[{"model":"xai/grok-imagine-image-2.0","media_type":"image","input":{"prompt":"A character sheet","quality":"medium","resolution":"2k"}}]}))
        return self.make_quote("0.09")

    def test_explicit_image_receipt(self):
        q=self.image_quote()
        rid=str(uuid.uuid4())
        response={"request_id":rid,"status_url":"https://api.higgsfield.ai/requests/"+rid+"/status","status":"completed","images":[{"url":"https://example.org/image.png"}]}
        with patch.object(studio,"api",side_effect=[{"usd":"0.09"},response]):
            receipt=studio.run(q,"0.09")
        self.assertEqual(receipt["clips"][0]["output"]["images"],response["images"])
        self.assertEqual(receipt["clips"][0]["media_type"],"image")
        self.assertEqual(receipt["clips"][0]["settings"]["quality"],"medium")
        with patch.object(studio,"api") as api:
            with self.assertRaises(studio.StudioError): studio.run(q,"0.09")
            api.assert_not_called()

    def test_image_price_increase(self):
        q=self.image_quote()
        with patch.object(studio,"api",return_value={"usd":"0.10"}) as api:
            with self.assertRaises(studio.StudioError): studio.run(q,"0.09")
            self.assertTrue(all(c.args[1].startswith("/estimate/") for c in api.call_args_list))

    def test_explicit_image_rejects_url(self):
        with self.assertRaises(studio.StudioError):studio.validate_model("https://evil.test/image","image")

    def test_unknown_media_type(self):
        with self.assertRaises(studio.StudioError):studio.validate_model("a/b","other")
