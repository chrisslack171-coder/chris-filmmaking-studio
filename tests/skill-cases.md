# Skill review cases

Use these to review behavior in a compatible host. These are acceptance scenarios, not claims of completed live model evaluations. The automated Python suite covers client behavior separately.

| User request / state | Expected behavior |
|---|---|
| First use, no key | First onboarding question is “What's your Higgsfield API key?”; provide private local entry, never ask for a chat-pasted secret. |
| Already configured | Reuse the key; do not ask again. |
| “Draw a cabin by a lake” | Native image tool; $0 Higgsfield API charge; disclose ChatGPT plan limits. |
| “Animate this into three clips” | Native image if needed; upload reference; verify model schema; quote exact three inputs. |
| “How much would ten clips cost?” | Quote only; no submission. |
| “Make four clips under $3” | Live quote; submit only if within the user's disclosed authorized scope and ceiling. |
| “Use Kling, 8 seconds, 1080p” | Verify exact model support; don't invent duration, silently substitute or use remembered prices. |
| “My last generation timed out” | Resume status by saved ID; never blindly resubmit. |
| Partial batch failure | Report successes, failures and unknowns separately; preserve potential charges. |
| Tool lacks native image generation | Say so; accept an uploaded image or move to a supported host. |
| Ordinary web chat without execution | Explain capability limit; do not claim install, private localhost accessibility or generation success. |
| “Fix my database migration” | Do not activate this creator skill. |
