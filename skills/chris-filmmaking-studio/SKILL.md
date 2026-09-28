---
name: chris-filmmaking-studio
description: Chris's filmmaking workflow for consistent characters, 1990s VHS scenes, sitcoms and love stories, with native image creation and live-quoted Higgsfield API generation. Use for Chris Studio media requests and reusable scene templates.
---

# Chris Filmmaking Studio

Personal adaptation of Samin Yasar's MIT-licensed Higgsfield API Studio. Preserve attribution and LICENSE when sharing.

## Route the request
- Images and character sheets: use the host's built-in image tool by default. Use supplied references, preserve identity and wardrobe, and explain that unseen details are inferred. Report $0 Higgsfield API charge for native generation; the host plan and limits still apply.
- Explicit Higgsfield API image requests: supported through the included client with `media_type: "image"`. Check the live model schema first. An estimate does not prove submission access.
- Videos: direct Higgsfield production API using `scripts/studio.py`. Do not silently switch to subscription MCP generation, Agent API, or another provider.
- Blender scene requests: resolve the installed Higgsfield `/use-blender` and `/Scene-Builder` instructions. Verify the actual local connection before editing. A generated character sheet is a visual reference, not a rigged 3D model. Ask for source assets/project paths before editing existing work.
- MCP recipes can inform prompts, but their tools and billing do not automatically transfer to the direct API.
- Website changes are separate: use the site's own tools and source; this skill neither deploys the Academy nor changes visitor credentials.

## Creative direction
Read [creative-presets.md](references/creative-presets.md) when the user asks for Chris's established styles. These are optional presets, not requirements for unrelated briefs. Reuse the approved characters, story, aspect ratio and aesthetic from the conversation.
For a broad story request, propose a concrete short scene and shot plan before the spending decision. Keep action feasible within the chosen duration. Do not invent a fixed default spend.
Use character sheets as identity references, not as literal opening frames: instruct the video model not to display panels, labels or duplicate figures. For start-frame-only models, create a single scene still first.

## API workflow
Read [api-and-costs.md](references/api-and-costs.md) for manifests, commands and recovery. Before new setup read [onboarding.md](references/onboarding.md).
1. Reuse existing local credentials; `doctor` never prints them or makes a paid call. The included client uses the existing HiggsfieldAPIStudio store on Windows. Do not copy keys into the skill or website. If permissions block access, request only the necessary path.
2. Check the chosen model's current documentation through https://console.higgsfield.ai. Use the exact production endpoint and supported settings. Do not infer availability from promotional names or stale catalogs.
3. Upload references with `upload`, telling the user they go to Higgsfield. Keep manifests and run receipts outside the distributed skill/repository.
4. Quote the exact jobs with `quote`. Report model, count, duration (video), resolution, audio, aspect ratio and USD total. Never subtract a promotion a second time.
5. Use existing authorization for the specific disclosed spend. Otherwise get approval for the concrete quote. Then `run QUOTE_ID --max-usd CEILING` rechecks the estimate and submits once. The ceiling is an estimate guard, not an invoice-level cap.
6. Poll with `status`; never resubmit to resume. For access denial, unknown submissions or timeouts, retain records, report the issue and reconcile before any paid retry.
7. Display output and receipt: request ID, status, quoted USD and final billed amount only if separately verified. Otherwise say final billed amount not yet verified.

API image manifests add `media_type: "image"` to each image job. This explicit flag permits image models; it does not validate a model's schema or account access. Video jobs retain the original validator. Both kinds share quote, ceiling, durable status and duplicate-submission safeguards.

