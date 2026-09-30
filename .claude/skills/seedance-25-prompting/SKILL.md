---
name: seedance-25-prompting
description: Write correct, generation-ready prompts for Seedance 2.5 (Dreamina) — including multi-reference creation (up to 50 materials), 30-second long videos with stages and end states, video editing, video extension, first/last-frame and multi-keyframe control, storyboard grids, blockout references, one-click video, seamless transitions, emotional direction, and professional camera terms. Use this skill EVERY time the user asks for a Seedance 2.5 prompt, mentions Seedance, Dreamina, reference images/videos/audio (@Image / @Video / @Audio), video editing of an existing AI clip, extending a video forward or backward, first/last frames, keyframes, blockouts, storyboards, 30-second videos, or asks to fix a Seedance prompt that produced wrong results. Also use when combining this model with cine-crew or ugc-cinematic-prompt outputs — this skill governs the SYNTAX and STRUCTURE rules for Seedance 2.5 specifically.
---

# Seedance 2.5 Prompting

Authoritative rules for writing Seedance 2.5 prompts. This skill defines syntax and structure. Creative/aesthetic decisions (lensing, lighting, color, anti-slop doctrine) come from cine-crew; this skill ensures the prompt is mechanically correct for the model.

## Core Prompt Formula

Combine flexibly (optional parts can be omitted):

**Subject + Action/Event + Scene & Environment + Visual Style + Camera Movement/Cut + Audio**

Template:
```
<Subject> performs <primary action or event> in <scene and environment>.
The visuals feature <visual style>.
Use <shot size, camera angle, camera movement, or cuts>.
Audio includes <dialogue, ambience, sound effects, or music>.
```

Do NOT include generation parameters (aspect ratio, duration, resolution) in the prompt text — those are set on the generation page or API.

## Reference Materials: Limits & Roles

Up to **50 reference materials** total:

| Type | Hard limit | Recommended for stability |
|---|---|---|
| Images | 30 images, each ≤4K | 1–8 distinct subjects across subject-reference images |
| Videos | 10 videos, ≤30s combined | 1–5 subjects, 5–10s per subject video |
| Audio | 10 clips, ≤30s combined | Only dialogue/voice/ambience/music directly relevant |
| Video editing | 1 source video + reference images | Source <20s, 1–5 reference images |

Rules that must ALWAYS be followed:

1. **Every material gets an explicit role in the prompt.** Never rely on labels inside images or model inference. Format:
   - `@Image 1 defines <subject>'s <appearance, clothing, structure, or material>.`
   - `@Video 1 defines <motion, camera movement, or pacing>.`
   - `@Audio 1 defines <character or sound type>'s <voice, dialogue, ambience, or music>.`
2. **Add exclusions** whenever a material could leak unwanted content: "Do not use the image background." / "Do not use the person's identity, clothing, or scene from the video."
3. **One binding per line.** Never write "@Images 1–4 define four characters respectively" — bind each image to its named subject individually.
4. **Multi-view of the same subject:** state it explicitly per image ("@Image 1 defines the front view of the same folding desk lamp… All four images define one lamp. The output must contain only one lamp throughout."). Separate view images are more stable than collages.
5. **When a reference video already defines the motion accurately**, state only which attributes to inherit — don't restate every action (restating can conflict with the reference).

## Special Syntax (Audio & Text)

| Content | Syntax | Example |
|---|---|---|
| Music | `()` | (Soft, rhythmic piano music plays in the background) |
| Sound effects | `<>` | \<A bell rings in the distance\> |
| Dialogue | `{}` | {Hello, welcome back.} |
| Subtitles | `【】` | 【Chapter One: Departure】 |

**Dialogue language reinforcement** (use when dialogue is not Chinese, or a specific accent is needed):

`Dialogue Language + Regional Variety/Accent + Delivery Style + Speaker + {Dialogue}`

Example: `Dialogue language: American English. The girl says in natural, conversational American English: {I thought you weren't coming.}`

## Task-Type Parameter Locks

| Task | Aspect ratio | Duration |
|---|---|---|
| Video editing | Locked to input video | Locked ≈ input duration (±~0.3s possible) |
| First-frame / first-and-last-frame | Locked to first image (first & last images MUST share aspect ratio or last frame stretches) | Settable |
| Video extension | Locked to input video | Settable |

## Reference Files — Load What the Task Needs

Read the relevant file(s) before writing the prompt:

- **`references/multi-reference.md`** — Many materials (characters + props + scenes + motion/audio): mapping, grouping by type, subject profiles, selecting references by scene. Load whenever using 3+ reference materials or multiple characters.
- **`references/long-videos.md`** — 30-second / multi-event videos: stage structure, end states, timestamps and pacing rules. Load for any video >15s or with multiple events.
- **`references/video-editing.md`** — Editing an existing video: master-video declaration, edit scope, subject replacement, background replacement, audio editing. Load for ANY edit of an existing clip.
- **`references/video-extension.md`** — Extending forward/backward: boundary-frame alignment, templates with extra references. Load for any extension task.
- **`references/keyframes-storyboards-blockouts.md`** — First/last frames with references, multi-keyframe sequences, storyboard grids, coarse vs. fine blockouts. Load when anchor images, storyboards, or blockout videos are involved.
- **`references/oneclick-and-transitions.md`** — One-click video from image sets, seamless transitions between two videos. Load for those two task types.
- **`references/performance-and-camera.md`** — Emotional direction via observable cues, supported camera language, popular techniques, handling uncommon cinematography terms. Load when directing performances or using advanced/niche camera terms.

## Pre-Submission Checklist (run every time)

- [ ] Subject and primary action/event clearly stated?
- [ ] Every reference material states what to use AND what not to use?
- [ ] Every distinct character/product/prop named and bound to one reference?
- [ ] References selected per scene (not forced to all appear at once)?
- [ ] Long video: one primary change + clear end state per stage?
- [ ] Character count, clothing, prop ownership, spatial relationships consistent?
- [ ] Editing: sole editing master, edit scope, target quantity, content to preserve defined?
- [ ] Abstract emotions/camera terms paired with directly visible or audible cues?
- [ ] First/last frames & keyframes: one role per image; first/last same aspect ratio?
- [ ] Blockouts: identified coarse vs. fine; stated what to inherit?
- [ ] Extension: boundary image, motion trend, audio continuity checked?
- [ ] One-click video: material roles, order, motion amount, editing style, audio defined?
- [ ] Seamless transition: both video roles, trigger action, transition process, arrival state defined?

## Known Limitations (set expectations correctly)

- Timestamps allocate time budgets to events — they are NOT frame-accurate edit points. Never demand frequencies ("three actions in one second").
- Editing prompts improve alignment probability but cannot guarantee frame-by-frame overlap.
- Multi-reference is for selecting the right materials per scene, not making everything appear at once.
- For pixel-accurate subtitles, formulas, signs, or specs: combine prepared reference materials + generation + post-production.
- Seamless transitions aim for visual/audio continuity, not pixel-identical preservation of the sources.
- Boundary frames in extensions connect visually, not pixel-identically — review both sides of the boundary.
