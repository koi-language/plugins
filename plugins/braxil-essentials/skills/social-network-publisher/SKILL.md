---
name: social-network-publisher
description: Publish posts to X (Twitter), LinkedIn, Facebook, Instagram, TikTok, YouTube, Threads and Pinterest on the user's behalf, through their connected accounts. One-click OAuth via the BRAXIL Auth Broker (tokens held encrypted server-side, no API keys on the client); supports text and media (images, video, and — on LinkedIn — PDF/document carousels). Use when the user wants to publish, post or share content to a social network, connect/disconnect a social account, or list which accounts are connected.
---

# Social Network Publisher

Publish to **X (Twitter), LinkedIn, Facebook, Instagram, TikTok, YouTube,
Threads and Pinterest** using each
platform's official API. Authentication is one-click OAuth through the BRAXIL
**Auth Broker** (the backend): tokens are stored securely server-side
(encrypted) and refreshed automatically. No Client Secrets, cookies, or browser
automation live on this machine.

## ⚠️ YOU run every script — NEVER the user

Run every Python script in this skill **yourself**, with the shell tool. **NEVER**
tell the user to open a terminal, run `python …`, or paste a command for them to
run — not for connecting accounts, not for posting, not for anything. The scripts
are designed to run autonomously from inside BRAXIL (the engine injects the user's
auth via `KOI_AUTH_TOKEN`, so they just work). Even account linking is autonomous:
`connect.py` opens the OAuth page in the browser by itself. The user's ONLY possible
involvement is clicking **"Authorize"** in that browser window the script already
opened — they never run, type, or copy any command. If something needs executing,
you execute it.

## How it works
1. **Connect (one-time per platform).** You run `connect.py`, which opens
   the official authorization page in the user's browser automatically. After the
   user grants access there, the BRAXIL backend exchanges the code and stores the
   tokens. (You run the script; the user only clicks "Authorize".)
2. **Publish.** The poster scripts ask the backend for a fresh short-lived
   access token (`broker_client.get_token`) and post directly to the platform.

Identity is automatic: the engine provides the logged-in user's BRAXIL token via
the `KOI_AUTH_TOKEN` environment variable, so the scripts just work when run
from inside BRAXIL. (The user must be signed in to BRAXIL.)

## Connect an account
Run this yourself (never hand it to the user):
```bash
python scripts/connect.py --platform x          # x | linkedin | meta | tiktok | youtube | threads | pinterest
```
- `meta` covers **both** Facebook Pages and Instagram Business (one Meta login).
- The browser opens automatically; once the user authorizes there, the script
  prints `✅ Connected`. Your job is to run the script and wait for that result —
  do NOT ask the user to run anything.

Check what's connected:
```bash
python scripts/connect.py --list
```

## Disconnect an account
Removes the stored connection and revokes the saved tokens server-side. Run it yourself.
```bash
python scripts/connect.py --disconnect --platform x --account @brand_account   # one specific account
python scripts/connect.py --disconnect --platform tiktok                       # ALL accounts of that platform
```
- `--account` is a `@handle`, display name, or id (use `--list` to see them). If
  the user has several accounts on that platform and doesn't say which, ask — or
  show `--list` first — before removing one.
- Omitting `--account` disconnects **every** account of that platform; confirm
  with the user before doing that.

### Multiple accounts per network
A user can connect **several accounts of the same network** (e.g. two X
profiles). To add another, you run `connect.py --platform x` again **while the
user is signed into that other account in the browser** — it adds a second
connection instead of replacing the first.

When publishing, pick which one with `--account` (a `@handle`, display name, or
id). If only one account is connected, `--account` is optional; if several are
connected and you omit it, the script errors and lists them.
```bash
python scripts/x_poster.py --text "…" --account @brand_account
```
For Meta, one login already exposes several Facebook pages / Instagram accounts —
pick the page with `--page <id>` (and `--account` only if you connected more than
one Meta login).

## ⚠️ Image sizing — generate at social dimensions, NEVER 4K

Social networks downscale or REJECT oversized images. **X returns `413 Payload
Too Large` when an image file exceeds ~5 MB** — the usual cause is feeding it a
4K / 2048px "max quality" render. There is no point generating huge images for a
post: the platform throws the extra pixels away.

**Before you publish — and ideally when you GENERATE the image in the first
place — size it for the target network:**

- **Generate at the target dimensions, not at 4K.** Long edge **≤ 1440 px**,
  default **1080 px**, file **≤ 5 MB**. For a multi-network post (X + Facebook +
  Instagram together), one **1080 × 1080** (square) or **1080 × 1350** (portrait)
  JPEG satisfies every network and never 413s.
- Per-network recommended sizes and file limits are in
  **`references/image-specs.md`** — read it and pick the right size for the
  format (feed / portrait / story / link).
- If an image you already have is too big, **resize it with Braxil's own image
  tools** to fit the spec before publishing — never run a Python/PIL/ImageMagick
  script to resize.

Rule of thumb: if you're about to post an image wider than ~1440 px or heavier
than 5 MB, resize it FIRST. Don't wait for the 413.

## Publish
```bash
# X — text, and/or media (local files). Up to 4 images OR 1 video (not both).
python scripts/x_poster.py --text "Hello from BRAXIL"
python scripts/x_poster.py --text "Look!" --image /path/a.png --image /path/b.png
python scripts/x_poster.py --video /path/clip.mp4 --text "Optional caption"

# LinkedIn — personal profile OR a Company Page you administer.
# Media: up to 9 images, OR 1 video, OR 1 document (PDF/DOC/PPT carousel). Not mixed.
python scripts/linkedin_poster.py --list-orgs                       # see your admin Pages
python scripts/linkedin_poster.py --text "Hello"                    # post as yourself
python scripts/linkedin_poster.py --text "Hello" --org "BRAXIL"     # post as the Page (id or name)
python scripts/linkedin_poster.py --text "Pics" --image a.png --org BRAXIL
python scripts/linkedin_poster.py --text "Demo" --video clip.mp4
python scripts/linkedin_poster.py --text "Our deck" --document slides.pdf

# Facebook page — text, and/or a photo or a video (local files hosted automatically).
python scripts/meta_poster.py --target facebook --text "Hello from BRAXIL"
python scripts/meta_poster.py --target facebook --text "Look" --image ./photo.png
python scripts/meta_poster.py --target facebook --text "Watch" --video ./clip.mp4

# Instagram — image OR video (Reel). A LOCAL file is hosted automatically, or pass a public URL.
python scripts/meta_poster.py --target instagram --image ./infographic.png --text "Caption"
python scripts/meta_poster.py --target instagram --image-url "https://…/img.jpg" --text "Caption"
python scripts/meta_poster.py --target instagram --video ./reel.mp4 --text "Caption"   # → Reel

# TikTok — uploads the video file directly (local file OR a URL it downloads).
# ⚠️ TikTok has a MANDATORY pre-publish flow — see the section below. Do NOT post
# without first fetching creator info and asking the user for title + privacy.
python scripts/tiktok_poster.py --creator-info                 # ALWAYS run this FIRST
python scripts/tiktok_poster.py --video /path/clip.mp4 --title "My video" --privacy PUBLIC_TO_EVERYONE \
    --allow-comment --your-brand                               # flags reflect the user's form answers

# YouTube — VIDEO ONLY (no text post). Vertical ≤60s with #Shorts → a Short.
python scripts/youtube_poster.py --video /path/clip.mp4 --title "My video" --description "…" --privacy public
python scripts/youtube_poster.py --video short.mp4 --title "Demo #Shorts" --tags shorts,demo --privacy unlisted

# Threads — text, OR an image, OR a video. Local media hosted automatically.
python scripts/threads_poster.py --text "Hello Threads"
python scripts/threads_poster.py --text "Look" --image ./photo.png
python scripts/threads_poster.py --text "Watch" --video ./clip.mp4

# Pinterest — a Pin = a board + an IMAGE (local hosted automatically) + title/description.
python scripts/pinterest_poster.py --list-boards                              # see board ids/names first
python scripts/pinterest_poster.py --image ./pin.png --title "My pin" --description "…" --board "Inspiration"
python scripts/pinterest_poster.py --image-url "https://…/img.jpg" --title "My pin" --board 12345 --link https://site.com
```

If a poster reports the account isn't connected (or a reconnect is required),
run the matching `connect.py --platform <p>` again **yourself** — don't ask the
user to run it; just execute it and let the browser handle the consent.

## TikTok — MANDATORY pre-publish flow (compliance)

**This section applies ONLY to TikTok.** For every other network, post normally.
For TikTok you MUST follow these steps — TikTok requires it and the app fails
audit otherwise. NEVER post a TikTok video by guessing the title or privacy.

**Step 1 — Fetch creator info FIRST (every time, right before the form).**
```bash
python scripts/tiktok_poster.py --creator-info --account <handle?>
```
Use the returned JSON to drive the form and enforce the rules:
- `creator_nickname` — show it, so the user knows **which TikTok account** the
  video posts to.
- `privacy_level_options` — the ONLY privacy choices you may offer.
- `comment_disabled` / `duet_disabled` / `stitch_disabled` — if `true`, that
  interaction is OFF in the user's TikTok settings: present it **disabled/greyed
  out** and never pass its `--allow-*` flag.
- `max_video_post_duration_sec` — if the video is longer, STOP and tell the user;
  do not post.
- If the response says the creator **cannot post right now** (rate/limit), STOP
  and tell the user to try again later — do not attempt the upload.

**Step 2 — Preview + ask the user with a `prompt_form`.** First show a **preview**
of the exact video (e.g. `show_result` the file). Then build ONE form.

**Only ask for what the user hasn't already specified.** If they already gave a
value ("title 'X'", "make it public", "allow comments"), use it and DROP that
field — don't make them repeat it. Ask only what's missing. Exception: Privacy,
Interactions and the Commercial disclosure are TikTok audit choices that must be
explicit with no pre-set default — surface them (pre-selecting nothing) unless the
user already stated them unambiguously.

Build the form with these field shapes (the form renderer supports `select`,
`multiSelect` checkbox lists, and clickable markdown links in any `label`/
`description`):

```yaml
- intent: prompt_form
  title: "Publish to TikTok (@<creator_nickname>)"
  fields:
    - type: "text"            # OMIT if the user already gave the title
      name: "title"
      label: "Caption / Description"
      description: "Editable — no watermarks or auto promo text unless you ask."
      required: true
    - type: "select"          # single-select; build from privacy_level_options
      name: "privacy"
      label: "Who can view this video"
      description: "Pick one."
      required: true
      options: [ { value: "PUBLIC_TO_EVERYONE", label: "Public" }, … ]
    - type: "select"          # ← multi-check: three independent checkboxes
      name: "interactions"
      label: "Allow users to"
      multiSelect: true
      required: false
      options:
        - { value: "comment", label: "Comment" }
        - { value: "duet",    label: "Duet" }
        # disabled:true ONLY if *_disabled in creator_info — and ALWAYS pair it
        # with disabledReason so the form shows WHY (rendered dim in parentheses).
        - { value: "stitch",  label: "Stitch", disabled: true, disabledReason: "disabled in your TikTok settings" }
    - type: "select"          # single-select, 3 options — THIS IS THE LAST STEP
      name: "disclosure"
      label: "Disclose video content"
      description: "Disclose if your video promotes goods or services in exchange for something of value (can't be changed after posting). By posting, you agree to TikTok's [Music Usage Confirmation](https://www.tiktok.com/legal/page/global/music-usage-confirmation/en)."
      required: true
      options:
        - { value: "none",            label: "My video does not promote any brand, product or service" }
        - { value: "your_brand",      label: "Your brand",      description: "You are promoting yourself or your own business. Labeled 'Promotional content'." }
        - { value: "branded_content", label: "Branded content", description: "You are promoting another brand or a third party. Labeled 'Paid partnership'. Not allowed with Private (Only Me). By posting branded content you also agree to TikTok's [Branded Content Policy](https://www.tiktok.com/legal/page/global/bc-policy/en)." }
```

There is **no separate consent step** — publishing IS the agreement (just like
TikTok's own composer), and the agreement line lives in the disclosure step's
text above.

Rules to enforce as you build / read the form:
- **Interactions** default unchecked; mark `disabled: true` on any interaction the
  creator turned off (`*_disabled` from creator_info), and ALWAYS pair it with a
  `disabledReason` (e.g. `"disabled in your TikTok settings"`) — the form shows it
  dim in parentheses next to the label. Duet/Stitch don't apply to photo posts —
  for photos show only Comment.
- **Private-only posts — say so in the form.** If the only value in
  `privacy_level_options` is `SELF_ONLY` (e.g. the app isn't audited yet, or the
  account is private), the video can ONLY be posted **private (only you)**. Make
  that explicit in the privacy field's description, e.g.: *"This video can only be
  posted as Private (only you) right now because the app isn't approved for public
  posting yet."* And since branded content can't be private, drop the
  `branded_content` option from the disclosure step and note why.
- **Branded content can't be private**: if the post is/ends up private, do NOT
  offer `branded_content` (and the script refuses it). If the user picks
  `branded_content` and a non-private privacy is available, remove `SELF_ONLY` from
  the privacy options.

**Step 3 — If the user cancels, post NOTHING.** Publishing IS the agreement (the
Music Usage Confirmation line is shown in the disclosure step). If the form comes
back cancelled (`answers: null, cancelled: true` — the user closed it without
submitting), **do not upload or generate anything**; just tell them nothing was
posted.

**Step 4 — Publish, then report status.** Map the answers to flags:
`--allow-comment/--allow-duet/--allow-stitch` only for the interactions they
checked; `--your-brand` for `your_brand`, `--branded-content` for `branded_content`
(neither for `none`). After it runs, tell the user it **may take a few minutes** to
process and appear on their profile; the script polls status and reports
`published` vs `still processing`.

## Notes for the agent
- **Never delegate script execution to the user.** Every `python scripts/*.py`
  command in this skill is something YOU run via the shell tool. The user never
  opens a terminal. Their only possible action is clicking "Authorize" in the
  OAuth browser window that `connect.py` opens by itself.
- One Meta connection exposes the user's Facebook pages + linked Instagram
  Business accounts. When the user has several pages, pass `--page <pageId>`.
- Instagram requires the image/video hosted at a public URL (handled
  automatically; IG video is always published as a Reel).
  TikTok uploads the video file directly to TikTok (no public URL / domain
  verification needed); pass `--video` (local) or `--video-url` (downloaded first).
- Dependencies: standard library only (no `requests`/Playwright needed).
