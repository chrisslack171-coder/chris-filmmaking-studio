# API and cost reference

Verified against official documentation on 2026-09-18. Recheck the selected model's live reference before creating inputs. No fixed price table is bundled; pricing is account-specific and can change.

## Sources

- [Model discovery and documentation index](https://docs.higgsfield.ai/docs/llms.txt)
- [Model console](https://console.higgsfield.ai)
- [Billing, estimates and refunds](https://docs.higgsfield.ai/docs/concepts/billing-and-retention)
- [Request lifecycle](https://docs.higgsfield.ai/docs/concepts/requests)
- [File uploads](https://docs.higgsfield.ai/docs/concepts/file-uploads)
- [Authentication](https://docs.higgsfield.ai/docs/authentication)

## Requests

The production base is `https://api.higgsfield.ai`. Authentication is `Authorization: Key KEY_ID:KEY_SECRET`. Credentials never go to a storage/CDN URL.

Estimate: `POST /estimate/{model-slug}` with the **exact generation input**. Documented response: `{"credits":"1.500","usd":"0.094"}`. These are example values, not a price promise. The script requires `usd`, uses decimal arithmetic and fails closed on missing/invalid prices.

Generate: `POST /{model-slug}` with the same input. Save `request_id` immediately, and poll the returned `status_url`. Normal states: queued, in_progress, completed, failed, nsfw, canceled. A completed video is usually in `video.url`. The client preserves image/images/video/videos/audio/audios output fields.

Upload: create a slot with `POST /files/generate-upload-url` and `{"content_type":"image/png"}`; PUT bytes to `upload_url` with `upload_headers`, **without** API authorization; use `public_url` in the model input. Uploading does not itself submit a generation.

## Batch manifest

One explicit entry equals one generation. Store manifests in private project output/state, outside the public repo and installed skill.

```json
{
  "jobs": [
    {
      "label": "Coastal road",
      "model": "bytedance/seedance-2.0/text-to-video",
      "input": {
        "prompt": "A cinematic tracking shot along a sunlit coastal road",
        "resolution": "720p",
        "generate_audio": true,
        "duration": 5,
        "aspect_ratio": "16:9"
      }
    }
  ]
}
```

This input comes from Higgsfield's public API introduction. Validate against the current model page before reuse. For another model, fetch its actual schema rather than reusing these fields blindly.

## CLI sequence

```text
studio.py doctor
studio.py onboard --web
studio.py upload /absolute/path/reference.png
studio.py quote /absolute/path/batch.json
studio.py run QUOTE_UUID --max-usd AUTHORIZED_USD
studio.py status QUOTE_UUID
```

Run each through Python 3.10+. `quote` saves a private run record and prints a redacted receipt without prompts or credentials. It expires after 15 minutes. `run` re-estimates the entire batch before any submission and refuses a higher total. It does **not** reserve prices at the provider or enforce an invoice-level cap. Each quote is single-use. Jobs are submitted sequentially without waiting for completion, then polled separately.

State lives under the local credential directory in `runs/`: `%LOCALAPPDATA%/HiggsfieldAPIStudio/runs/` on Windows unless a legacy store exists, or `~/.config/higgsfield-api-studio/runs/` elsewhere. Do not delete or edit records to retry a paid batch. If a process dies during submission, a lock/unknown state intentionally stops another submission. Reconcile accepted IDs and the console; create a new manifest only for confirmed unsubmitted work after the user authorizes it.

## Honest cost reporting

- `quoted_usd`: authenticated estimate, potentially reflecting eligible discounts.
- `completed_estimated_usd`: sum of quotes for completed clips.
- `billed_usd` / `final_billed_usd`: null until billing is separately verified; this client does not reconcile invoices.
- Do not assume promotional credits reduce the model's price to $0. They are a payment balance. Distinguish generation cost from out-of-pocket cash.
- Do not stack a launch percentage on the estimate. Do not promise launch eligibility, duration or concurrency; use the account's current console terms.
- Failed and NSFW requests are documented as uncharged/refunded, and successfully canceled queued requests refunded. Report the policy separately from observed refund settlement.
- ChatGPT native images incur **$0 Higgsfield API charge**; ChatGPT plan pricing/limits still apply. The skill does not call the OpenAI image API.
- Download important output promptly. Higgsfield documents at least seven days of output availability, not permanent hosting.

## Explicit API image requests
Add `"media_type": "image"` beside `model`, `label` and `input`. Verify the model schema first. Quote and run use the same safeguards as videos. Image receipts include image outputs and quality. An HTTP 403 indicates denied access; a prior successful estimate is not proof of generation permission.
