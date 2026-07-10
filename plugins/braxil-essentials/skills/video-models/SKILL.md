---
name: video-models
description: MANDATORY before ANY video generation — activate this skill the moment a request involves creating, generating, animating, or editing a video, i.e. before EVERY `generate_video` call: text-to-video, image-to-video, reference-to-video, motion transfer, talking-head avatar, video-to-video edit, or extend. It is the required model+parameter contract: `model` is a mandatory parameter (there is NO auto-router) and this skill tells you which model to pick by category and matching input shape, and exactly which parameters each supported model accepts or rejects (and which specific models have their own optimization skill, e.g. Seedance). If you are about to generate/animate/edit a video and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): "generate/create/make a video", "genera/crea/haz un vídeo", "animate this image/photo", "anima esta imagen/foto", "image to video", "talking head/avatar", "extend/make this clip longer", "restyle this video", "remove the background of this video", or any mention of a video model (Veo, Kling, Seedance, WAN, Gemini Omni Flash, OmniHuman).
---

# Video models

Runbook for producing video through BRAXIL's `generate_video` tool. **Do not reimplement video API code.** **You choose the model** (the `model` param is required — there is no auto-router): identify the operation → pick a slug from the matching category whose input shape fits → send only what that model accepts.

**Where to find what — it's already in your context, don't go searching:**
- **Categories & Labels of every model → the `video` tool's OWN description (the "Catalog" table).** Already in your context — read it RIGHT THERE to pick a model. **Never grep files, `references/`, or the backend for models / categories / labels.**
- **Per-model PARAMETERS → `references/models.md`** (what each model accepts + input shape). Read a model's card before choosing a slug or setting a non-obvious field (startFrame vs referenceImages, duration enums, audio).

Choosing a slug whose adapter rejects your request shape (e.g. an image-to-video slug for a text-only prompt) fails loudly.

## The tool: `generate_video`

**The exact accepted values for every parameter DEPEND ON THE MODEL you pick** — read your chosen model's table in `references/models.md` (its duration set, aspect ratios, resolution labels, which frames/refs it takes, audio behaviour) and pass ONLY what it lists. The bullets below only say what each param MEANS:

- `prompt` (required) — **always English** (models lose motion fidelity / scene coherence otherwise). The ONLY exception is dialogue, lyrics, voice-over, or on-screen text the model must reproduce verbatim: keep that in the user's language, quoted, inside the otherwise-English prompt.
- `duration` — seconds. **Per-model legal set** — some are fixed (Veo `4s/6s/8s`, extend `7s`), others clamp up to 15s, avatars follow the audio. See the model's table.
- `aspectRatio` — **per-model** — some accept `auto/16:9/9:16/…`; frame-driven and avatar models inherit dims from the input image. See the table.
- `resolution` — **per-model** labels — only some reach 4k, and most emit `1080p` when you omit it. See the table for the default and ceiling.
- `startFrame` — the **LITERAL first frame** — frame 0 of the output looks identical to this image. Use ONLY when the user wants the video to begin from this exact picture. **Never** pass a storyboard/sheet/mood-board/style ref here — those go in `referenceImages`. Accepts a path / `att-N` / `@mention`.
- `endFrame` — the LITERAL last frame. Pair with `startFrame` for "animate FROM image A TO image B" — the model interpolates. Don't collapse a FROM→TO request into a frameless prompt.
- `referenceImages` — visual REFERENCES (style sheets, storyboards, character designs, subject photos) guiding look/composition/identity, NOT the literal first frame. Only reference-to-video models accept them.
- `sourceVideo` — the existing clip, for `operation:"edit"`/`"extend"` (the ONLY reference for those — never re-attach the images the video was generated from).
- `withAudio` — generate an audio track (SFX/dialogue/VO/ambient). **Default true.** Set false only for a deliberately silent clip. Does NOT control background music (exclude music via prompt text).
- `cameraMovement` — optional motion hint (`static`, `pan_left`, `zoom_in`, `dolly_in`, `orbit_right`, …); some models honour it, others ignore it.
- `seed` — reproducibility seed (operation `"new"` only): same seed + prompt ⇒ the same clip **on models that honour it** (Seedance, Veo, WAN; Kling ignores it). Omit for a fresh result.

> The `video` tool has NO `characterOrientation`, `keepOriginalSound`, `referenceVideos` or `audioUrl` — even where a model supports them, the agent can't set them here.
- `saveTo` — optional COPY (dir or `.mp4/.mov/.webm`). Original stays in `~/.koi/videos/` (returned `savedTo` — use THAT for the timeline/library); copy is `exportedTo`.
- `model` — **REQUIRED. YOU pick the exact slug.** No auto-router — omitting it (or `"auto"`) makes the tool error out. Read the tool's **Catalog table** (or `references/models.md`) and pick a slug whose **Categories** match your operation AND whose input shape matches your request. Don't invent a slug.

## Categories — match your operation, ALWAYS

Every model carries one or more Koi categories (in the tool's Catalog table). Pick a slug **whose category matches the operation, and NEVER one that lacks it.** Video adds a second constraint: **the input shape must match too** (a text-to-video slug can't take a `startFrame`; an image-to-video slug needs one).

| Category | Use it for | You are doing |
|---|---|---|
| `video_generation` | text/image/reference → video (create) | making a new clip from a prompt, a still, or reference images |
| `image_to_video` | animate a still | driving motion from one `startFrame` (often also tagged `video_generation`) |
| `video_editing` | v2v transform | restyling / repainting an existing clip (`referenceVideos` present) |
| `video_extend` | make longer | continuing an existing clip |
| `video_avatar` | talking head | lip-syncing a face image to an audio track (`imageUrl` + `audioUrl`) |

**Hard rule:** editing a clip ⇒ pick a `video_editing` slug; extending ⇒ `video_extend`; an avatar ⇒ `video_avatar`. And never pin an image-to-video slug for a text-only prompt (or a text-to-video slug when you pass a `startFrame`) — the shapes must line up. (No video background-removal or synced-Foley model is currently enabled.)

## Routing: pick the slug yourself

| I want to… | Tool / how | Send |
|---|---|---|
| Generate from text | `video` `operation:"new"`, `model` from `video_generation` | `prompt` (+aspectRatio/resolution/duration/withAudio) |
| Animate one photo | `video` `"new"`, `model` from `image_to_video` | `prompt` + `startFrame` |
| Frame A → frame B | `video` `"new"`, `model` that accepts a last frame | `prompt` + `startFrame` + `endFrame` |
| Compose from image refs | `video` `"new"`, `model` = `bytedance/seedance-2.0/reference-to-video` | `prompt` + `referenceImages` |
| Edit an existing clip | `video` `operation:"edit"` — **no model** (server-routed) | `sourceVideo` + `prompt` |
| Extend a clip (+7s) | `video` `operation:"extend"` — **no model** | `sourceVideo` + `prompt` |
| Talking-head avatar | `generate_avatar_video` — **no model** | `image` + `audioFile` (+`aspectRatio`) |

⚠ **Motion transfer (Kling Motion-Control)** needs a reference motion video + `characterOrientation`, which the `video` tool doesn't expose — it isn't usable through the standard tool right now.

## Choosing within a category

Once the category and input shape are fixed, several models may qualify. Decide from the data — neutrally, no default favourite:

- Compare the candidates' cards in `references/models.md` on the traits your task needs: max resolution (only some reach 4k), duration range (differs a lot — some cap at 8s, others reach 15s, extend is fixed), native-audio support, and the exact input shape (start/end frame, refs, audio-driven lip-sync).
- **What the labels mean — use them to pick the best-suited model.** A model's labels (the Catalog table's **Labels** column) mark the content, subject, motion or style that model is the BEST-SUITED for. If the user's request matches a label, **strongly prefer that model** over an unlabelled one in the same category — the label is telling you it is the best fit. Examples: `avatar` / `talking-head` → the best for a lip-synced presenter; `anime` → the best for anime-style motion; `product` → product/e-commerce clips; `cinematic`, `nature`, etc. → their named subject/style. Read every candidate's labels against what the user asked for and route accordingly. When no label matches, ignore labels and choose on quality / price.
- Some behaviours live on a single model (motion transfer, fixed-length extend). Find that model by the input shape / label it supports in the table + `references/models.md`, not by memory.

## Per-model optimization skills

Some models have a **dedicated skill** with the optimal way to prompt and drive them. This does NOT bias which model you choose — but the moment you DO choose one that has a skill, **activate that skill first** so you use the model optimally. A model's card in `references/models.md` names its skill when one exists.

- **Seedance 2** (`bytedance/seedance-2.0/*`) → activate the `braxil-essentials:seedance-2-0` skill before building the prompt.

## Gotchas

- **startFrame ≠ referenceImages.** startFrame is a strict commitment to identical pixels at t=0. Storyboards, sheets, mood boards, character/style refs are `referenceImages`. When unsure, use `referenceImages` — the wrong choice fails or produces a different take.
- **Editing/extending a video?** Use `operation:"edit"`/`"extend"` with `sourceVideo` = the clip (no `model`). Never re-attach the images that video was generated from — that rebuilds a *different* take.
- **Audio defaults ON** for generative models (`withAudio`).
- **Duration is per-model** — some cap at 8s, others reach 15s, and extend is a fixed length. Check the card before promising a duration.
- **Only some models reach 4k** — others ignore `resolution` or inherit it from the input. Check the card.
- Read the model's card in `references/models.md` before setting `endFrame`, `resolution`, `duration` or `cameraMovement` — support and accepted values are per-model.
