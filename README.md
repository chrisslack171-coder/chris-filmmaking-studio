# Chris Filmmaking Studio

**Create photos in ChatGPT. Turn them into videos with the Higgsfield API. See the quoted cost before you generate.**

Chris Filmmaking Studio brings these steps into one guided workflow in a supported local Codex environment:

1. **Create your photos:** make a character, product image or scene with ChatGPT's built-in image tool.
2. **Plan your video:** choose what happens, how long it runs and the visual style.
3. **See the price:** get a live Higgsfield API quote for the exact settings before approving paid generation.
4. **Make your video:** send the approved reference and prompt to Higgsfield using your own API key.
5. **Review your receipt:** see the result, request status and quoted cost. Final billed amounts remain unverified unless checked separately.

Native ChatGPT images have **$0 Higgsfield API charge**; your ChatGPT plan and limits still apply. This toolkit does not report your entire ChatGPT bill or guarantee a final API charge.

Independent adaptation of [Higgsfield API Studio](https://github.com/Samin12/higgsfield-api-studio) by Samin Yasar, under the MIT license. Not affiliated with or endorsed by Higgsfield or OpenAI.

## Do students need this?

**No. The Higgsfield API is an online service, not something you download.** Students create their own API account and key, then use a compatible app, SDK or script to call it.

Install this toolkit if you want to follow Chris's guided Codex lessons: private key setup, character references, live cost quotes, video requests and receipts. Students following that particular workflow should install it; students using another API client do not need it.

Each student uses their own account, API key and balance. Never use an instructor's key. A Higgsfield website subscription and API billing are separate; this toolkit does not provide credits, subscriptions or unlimited generation.

## What you need

- A local Codex environment with skill support, shell execution and outbound HTTPS.
- Python 3.10 or newer. Git is optional if you download the repository ZIP.
- Your own [Higgsfield API account](https://console.higgsfield.ai), model access and balance.
- A built-in image tool for native image creation, or your own reference images. The skill cannot add a missing image tool.
- Blender only for optional editable 3D scene lessons. It is not required for API videos.

Ordinary ChatGPT web/mobile chat cannot execute this local Python client merely by receiving the skill prompt.

## Install with one prompt

Open a local Codex task and paste this prompt. No coding knowledge is needed. The assistant checks requirements and guides setup; missing dependencies or permissions can still require your action.

```text
Install Chris Filmmaking Studio from:
https://github.com/chrisslack171-coder/chris-filmmaking-studio

Read the README, download and extract the repository ZIP, and inspect
scripts/install.py before running it. Check the local requirements, including
Python 3.10 or newer. If something is missing, explain it and guide me through
setup. Do not overwrite an existing customized skill.

Install the skill, then use $chris-filmmaking-studio. Reuse my existing
Higgsfield API credentials if configured. Otherwise open the private local
setup form so I can enter my own key there, not in this chat.

Use ChatGPT's built-in image tool for photos when available and the direct
Higgsfield API for videos. Show the live quote before paid generation and
provide a receipt afterward. Do not run paid generation during installation.
If the package cannot be downloaded or a required tool is unavailable,
explain the blocker instead of claiming success.
```

Restart Codex if the installed skill is not listed. See **Manual setup** below only if needed.

## Connect privately

Use `$chris-filmmaking-studio` and ask: “Help me connect my own Higgsfield API account.”

Or, from the extracted repository:

```sh
python skills/chris-filmmaking-studio/scripts/studio.py onboard --web
```

Use `py -3` on Windows or `python3` on macOS/Linux if `python` is unavailable. Open the printed localhost link on the same computer and enter your key in the private form—not in chat, a lesson recording, or GitHub.

Credentials are stored locally, not encrypted at rest. Windows uses `%LOCALAPPDATA%/HiggsfieldAPIStudio` unless an existing legacy store is present; other platforms use `~/.config/higgsfield-api-studio`. Existing API Studio credentials can be reused. Keep your computer account protected.

## First lesson: quote before you generate

1. Create or supply a character reference.
2. Ask for a short shot plan with exact duration, aspect ratio, resolution and audio settings.
3. Request a live quote. An estimate does not submit a generation or prove model access.
4. Approve the disclosed spend, then generate once.
5. Review the output and its receipt. An estimate is not a verified final charge.

Example request:

> Use $chris-filmmaking-studio to plan a short cinematic scene using my character reference. Quote one short video before generating. Show the model, settings and total USD.

If a request returns an access error such as 403, check account/model access. Never repeatedly submit a paid request to resolve a timeout; use the saved request ID and status command.

## Included

- VHS bistro, character continuity, sitcom and love-letter scene presets.
- Native images by default; explicit direct-API image requests through `media_type: "image"`.
- Live quotes, price rechecks, spending guards and duplicate-submission protection.
- Image, video and audio output fields retained in receipts.
- Separate guidance for Blender and subscription MCP workflows.

The API ceiling guards estimates, not the provider's final invoice. Model IDs, access and prices must be checked against current documentation. No generation success or discount is guaranteed.

## Manual setup

On this repository, choose **Code → Download ZIP** and extract it. In the extracted folder run `py -3 scripts/install.py` on Windows or `python3 scripts/install.py` on macOS/Linux. Python 3.10+ is required behind the scenes. The installer preserves existing customized skills.

## Development and attribution

Run `python -m unittest discover -s tests`. Tests use mocked API generation responses and dummy onboarding credentials; they do not spend API credits. Paid end-to-end generation was not used for release validation.

See [LICENSE](LICENSE). The repository includes `skills/chris-filmmaking-studio/SKILL.md` and `references/api-and-costs.md` for the complete workflow.

Preserve the original MIT attribution when sharing. Never distribute credentials, run records or private reference media.

