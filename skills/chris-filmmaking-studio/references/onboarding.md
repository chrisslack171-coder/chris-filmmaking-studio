# Private onboarding

The desired flow is install → “What's your Higgsfield API key?” → private entry → create content.

## Local browser flow

Run `python3 <skill-path>/scripts/studio.py onboard --web` using a tool that can leave a process running. Its first output provides `private_setup_url`. Open it on the same computer or give the user a clickable link. Wait for them to enter `KEY_ID:KEY_SECRET` themselves. Do not inspect or screenshot the password field. The localhost server is single-use, expires after ten minutes, requires its random path and same origin, and does not log requests. It binds only to 127.0.0.1.

Do not use this localhost flow from a remote/cloud sandbox: the user's browser cannot reach that sandbox's loopback address. Use a host-provided secret manager if one is available to the user, mapping `HF_KEY` to the client, or move to local desktop execution. Do not improvise a public credential form, tunnel or chat-based key transfer.

## Hidden terminal flow

The **user**, in their own terminal, runs:

```bash
python3 ~/.codex/skills/chris-filmmaking-studio/scripts/studio.py onboard
```

The key is entered into a hidden password prompt. Do not pass it as a command argument, inline environment assignment or shell-history entry. `HF_KEY`, `HF_CREDENTIALS`, or the documented key-ID/secret environment pairs are also supported when supplied by a private secret manager.

## Storage and verification

Windows uses `%LOCALAPPDATA%/HiggsfieldAPIStudio/credentials.json` unless a legacy store exists. Other systems use `~/.config/higgsfield-api-studio/credentials.json`, outside the repo, with mode 600 on POSIX. This is restricted local storage, **not encryption at rest**. The state directory is created with mode 700. Use a dedicated key and rotate it in the Higgsfield console if exposed. Environment credentials take precedence over the local file.

Saving checks the key's format; `doctor` checks local availability. Neither proves live access. A successful authenticated `quote` verifies API access without submitting a generation. Distinguish these outcomes in user-facing replies.

The installed skill is instructions plus a Python script. Availability and invocation depend on the host. It cannot inject itself into every ChatGPT conversation or enable tools absent from that account. Explicitly selecting the skill is the most reliable way to use it.
