# How to Set Up Higgsfield API for AI Video Creation

**Format:** beginner screen-recording tutorial, approximately 4–6 minutes.  
**Goal:** help students set up the tools they need—not teach video generation in this lesson.

**Instructor note:** Publish and verify the toolkit download at the GitHub link before recording. No paid generation is needed for this setup tutorial.

## 1. What this setup does

**Show:** A simple slide: ChatGPT photos → Higgsfield API videos → live price estimates.

**Say:**

“If you want to start creating AI videos, you don’t have to begin by subscribing to every separate video platform. In this tutorial, I’ll show you how to set up access to the Higgsfield API and connect my Studio workflow.

“The API gives you access to the models Higgsfield makes available to your account. My workflow helps you create photos with ChatGPT, use those photos for API videos, and review the quoted video cost before you generate.

“Today, we’re only getting everything connected. We’ll create our first video in the next lesson.”

## 2. The three things you need

**Show:**

1. ChatGPT/Codex with local tool access.
2. Your own Higgsfield API account, key and balance.
3. Chris Filmmaking Studio, installed with one setup prompt.

**Say:**

“First, you need a supported local Codex environment to run this workflow. For photos, use ChatGPT’s built-in image tool where available. If your local environment doesn’t have image generation, you can create a photo in ChatGPT separately and attach it later.

“Second, you need your own Higgsfield API account and key. Any paid generation uses your API balance.

“Third, you’ll install my Studio skill. That gives the assistant the instructions and client it needs to connect the steps. You don’t need to learn coding for this setup—we’ll use one installation prompt.

“You don’t download the API itself. It’s an online service. You download the Studio toolkit that connects to it.”

**Small on-screen note:** API billing is separate from a Higgsfield website subscription. Available models and account access vary. ChatGPT plan and usage limits still apply.

## 3. Get your Higgsfield API key

**Show:** https://console.higgsfield.ai — sign in, then open the API keys section. The address may redirect to the current API console.

**Say:**

“Open the Higgsfield API console using the link below. Sign in or create your own account, then find the API keys section.

“Create your API credential. It contains a key ID and a secret. Keep that information private—we’ll enter it in a private setup form in a moment.

“You can also review the Billing section to see your API balance. You’ll need sufficient balance and model access when you’re ready to generate. Creating the connection does not mean a paid video has been submitted.”

**Recording direction:** Stop recording before revealing or copying a real credential. Do not show the key, clipboard contents, account payment details or credential file. Resume on a safe screen.

## 4. Install Chris Filmmaking Studio

**Show:** https://github.com/chrisslack171-coder/chris-filmmaking-studio

**Say:**

“Next, open my GitHub page and copy the installation prompt from the README. Paste it into a local Codex task.

“The assistant will check the requirements, inspect the toolkit and help install it. If your computer needs a dependency or permission, it will guide you. Wait for the actual installation confirmation.”

**Copy/paste prompt:**

```text
Install Chris Filmmaking Studio from:
https://github.com/chrisslack171-coder/chris-filmmaking-studio

Read the README, download and extract the repository ZIP, and inspect
scripts/install.py before running it. Check the local requirements,
including Python 3.10 or newer, and guide me if anything is missing.
Do not overwrite an existing customized skill.

Install the skill, then use $chris-filmmaking-studio.
Reuse my existing Higgsfield API credentials if already configured.
Otherwise open the private local setup form so I can enter my own
API key there, not in this chat.

Use ChatGPT's built-in image tool for photos when available and the
direct Higgsfield API for videos. Show a live quote before paid
generation and a cost receipt afterward.

Do not submit any paid generation during setup. If installation or
download fails, explain the blocker rather than claiming success.
```

**Say:**

“The skill uses Python behind the scenes, but you don’t have to write Python code. The setup prompt asks the assistant to check that for you.

“If the installed skill doesn’t appear, restart Codex and select Chris Filmmaking Studio, or type its name with the dollar sign.”

**On-screen:** `$chris-filmmaking-studio`

## 5. Connect your key privately

**Show:** The private localhost setup form with an empty password field. Do not record real credential entry.

**Say:**

“When the assistant opens the private setup form, enter your own full API credential there. Save it, then return to the conversation and tell the assistant you’re done.

“Don’t paste your secret into chat, GitHub or a public comment. Every student connects their own account—not mine.”

**Recording direction:** Pause before entering the credential. Resume after the form confirms it was saved.

**Say:**

“This client stores the credential locally on your computer. It is not encrypted at rest, so keep your computer account protected.

“If you already connected this API account, the workflow can reuse that setup without asking you to enter the key again.”

## 6. Confirm setup and close

**Paste:**

```text
Use $chris-filmmaking-studio.
Confirm that the skill and local API client are installed and that
my credentials are configured, without displaying the key.
Tell me if anything is missing.
Do not upload media or submit paid generation.
```

**Show:** The actual local setup result.

**Say:**

“That’s the setup. We have the Studio workflow installed and our credentials saved.

“This local check does not prove every model is available to us. When we make our first video, we’ll check a supported model, request a live quote, and approve the cost before generating.

“In the next lesson, we’ll create a photo, turn it into a video, and review the result and cost receipt.”

**End card:**  
Connected and ready for the next lesson  
Photos → video quote → your approval → generation

---

## Video description

Set up Higgsfield API access and Chris Filmmaking Studio for a guided photo-to-video workflow.

You’ll learn how to:
- Find the Higgsfield API console and create your own API key.
- Install the Studio skill using a copy/paste prompt in a supported local Codex environment.
- Save your key through a private local form.
- Confirm the local setup without generating paid content.

Links:
- Higgsfield API console: https://console.higgsfield.ai
- Chris Filmmaking Studio: https://github.com/chrisslack171-coder/chris-filmmaking-studio
- Official credential guidance: https://docs.higgsfield.ai/docs/authentication

The API is an online service; the downloadable item is the Studio toolkit. This setup accesses models supported by Higgsfield’s API and available to your account. It does not guarantee access to every model or replace every platform.

API generation is billed separately from ChatGPT and Higgsfield website subscriptions. Native ChatGPT images have no Higgsfield API charge, but ChatGPT plan limits still apply. The Studio reports live generation estimates; final billed amounts require separate verification.

Chris Filmmaking Studio is an independent adaptation of Samin Yasar’s MIT-licensed Higgsfield API Studio: https://github.com/Samin12/higgsfield-api-studio

## Instructor-only troubleshooting

- GitHub package missing: finish publication before sharing the lesson.
- Python missing: let the assistant guide installation of Python 3.10+; manual commands are in the toolkit README.
- Skill missing: verify installation and restart Codex.
- Private form expired: ask the assistant to reopen it on the same computer.
- Saved key: means locally configured, not proven generation access.
- Missing native image tool: use a separately created photo or an existing reference in the next lesson.
- Permissions blocked: report the actual missing permission rather than saying setup succeeded.
- Do not promise free videos, universal model access, a fixed discount, or unlimited generation.

