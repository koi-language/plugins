---
name: video-generator
description: MANDATORY before ANY video generation — activate this skill the moment a request involves creating, generating, animating, or editing a video, i.e. before EVERY `generate_video` call: text-to-video, image-to-video, reference-to-video, motion transfer, talking-head avatar, video-to-video edit, or extend. It is the required model+parameter contract: `model` is a mandatory parameter (there is NO auto-router) and this skill tells you which model to pick by category and matching input shape, and exactly which parameters each supported model accepts or rejects (and any per-model reference PREP, e.g. Seedance's face-filter workaround in `references/usage/seedance.md`). If you are about to generate/animate/edit a video and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): "generate/create/make a video", "genera/crea/haz un vídeo", "animate this image/photo", "anima esta imagen/foto", "image to video", "talking head/avatar", "extend/make this clip longer", "restyle this video", "remove the background of this video", or any mention of a video model (Veo, Kling, Seedance, WAN, Gemini Omni Flash, OmniHuman).
---

# Video models

Runbook for producing video through BRAXIL's `generate_video` tool. **Do not reimplement video API code.** **You choose the model** (the `model` param is required — there is no auto-router): identify the operation → pick a slug from the matching category whose input shape fits → send only what that model accepts.

**Where to find what — it's already in your context, don't go searching:**
- **Categories & Labels of every model → the `video` tool's OWN description (the "Catalog" table).** Already in your context — read it RIGHT THERE to pick a model. **Never grep files, `references/`, or the backend for models / categories / labels.**
- **Per-model PARAMETERS → `references/models.md`** (what each model accepts + input shape). Read a model's card before choosing a slug or setting a non-obvious field (startFrame vs referenceImages, duration enums, audio). A model's card also links its **USAGE guide** (`references/usage/<model>.md`) when one exists — READ it before composing the prompt.

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
- `referenceVideos` — (operation `"new"` only) video REFERENCES for CONTINUITY / style / motion carry-over, e.g. the immediately-preceding clip of a multi-shot film so this new clip continues from it. NOT a v2v edit of them (that is `operation:"edit"`): the model renders the NEW scene in `prompt` and treats the videos as continuity anchors. Only reference-to-video / continuation-aware models honour them (e.g. `bytedance/seedance-2.0/reference-to-video`); others ignore them. Combine freely with `referenceImages` (e.g. the character turnarounds + the previous clip). The tool auto-routes this as a continuation (keeps your pinned model, not a v2v editor).
- `withAudio` — generate an audio track (SFX/dialogue/VO/ambient). **Default true.** Set false only for a deliberately silent clip. Does NOT control background music (exclude music via prompt text).
- `cameraMovement` — optional motion hint (`static`, `pan_left`, `zoom_in`, `dolly_in`, `orbit_right`, …); some models honour it, others ignore it.
- `seed` — reproducibility seed (operation `"new"` only): same seed + prompt ⇒ the same clip **on models that honour it** (Seedance, Veo, WAN; Kling ignores it). Omit for a fresh result.

> The `video` tool has NO `characterOrientation`, `keepOriginalSound` or `audioUrl` — even where a model supports them, the agent can't set them here. (`referenceVideos` IS available on `operation:"new"` — see above.)
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
| `video_lipsync` | re-voice a clip | re-articulating the lips of an EXISTING video to a new audio track (`videoUrl` + `audioUrl`) |

**Hard rule:** editing a clip ⇒ **`operation:"edit"` with `model` UNSET** (server-routed to the `video_editing` pool — the best/default editor is **Gemini Omni Flash**); extending ⇒ `video_extend`; an avatar (face photo → talking video) ⇒ `video` `operation:"new"` with `startFrame` (the face photo) + `audioFile` (the driving audio) + a **REQUIRED** `model` from `video_avatar`; dubbing/re-voicing an existing clip (video → same clip, new lips) ⇒ `lipsync_video`; removing the background from an existing clip ⇒ `video` `operation:"bg-remove"` with `sourceVideo` + a `video_background_removal` model (see the Background removal card in `references/models.md`). And never pin an image-to-video slug for a text-only prompt (or a text-to-video slug when you pass a `startFrame`) — the shapes must line up. (No synced-Foley model is currently enabled.)

> ⚠ **"Edit / modify / change / add / remove X in THIS clip" is NEVER a generation model.** Do NOT reach for a `reference-to-video` or `image-to-video` slug (Seedance, Gemini Omni image-to-video, etc.) to change an existing video — that generates a NEW clip from a still/refs, it does not edit the source. Any request that starts from an existing clip and wants it modified in place is `operation:"edit"`, model UNSET. (`referenceVideos` on a Seedance `reference-to-video` generation is for *chaining a new shot* off a prior clip, not for editing that clip.)

**Avatar vs lip-sync — different shapes, don't confuse them:** you have a face PHOTO and want it to speak → the SAME `video` tool, `operation:"new"`, with `startFrame` = the photo, `audioFile` = the audio, and `model` = a `video_avatar` slug (REQUIRED, you pick it — cards in `references/models.md`). You already have a VIDEO and want its speech replaced/dubbed → `lipsync_video` (veed/lipsync/v2).

> ⚠ **If the user ATTACHED a spoken-audio file, THAT file is the `audioFile` — pass it straight in. Do NOT synthesise a new one.** The two shapes, by what else is attached:
> - **Attached AUDIO + PHOTO** → talking-head avatar **driven by the attached audio**: one `video` call, `operation:"new"`, `startFrame` = photo, `audioFile` = the attached clip, `model` from `video_avatar`.
> - **Attached AUDIO + VIDEO** ("haz que el personaje del vídeo hable este audio") → **lip-sync**: `lipsync_video` with `video` = the attached clip + `audioFile` = the attached audio (**that same audio and that same video** — no model, nothing regenerated).
>
> In BOTH cases the attached audio already IS the voice and the words: do NOT call `generate_audio` (TTS) to re-create it. TTS / `create_voice` only enter when there is **no audio and you have the TEXT** to speak (or you must reuse a cloned voice for NEW words). Never invent a voice for audio you were handed.

## Routing: pick the slug yourself

| I want to… | Tool / how | Send |
|---|---|---|
| Generate from text | `video` `operation:"new"`, `model` from `video_generation` | `prompt` (+aspectRatio/resolution/duration/withAudio) |
| Animate one photo | `video` `"new"`, `model` from `image_to_video` | `prompt` + `startFrame` |
| Frame A → frame B | `video` `"new"`, `model` that accepts a last frame | `prompt` + `startFrame` + `endFrame` |
| Compose from image refs | `video` `"new"`, `model` = `bytedance/seedance-2.0/reference-to-video` | `prompt` + `referenceImages` |
| Continue from the previous clip (multi-shot chaining) | `video` `"new"`, `model` = `bytedance/seedance-2.0/reference-to-video` | `prompt` + `referenceImages` (e.g. the character turnarounds) + `referenceVideos` (the previous clip) |
| Edit an existing clip | `video` `operation:"edit"` — **no model** (server-routed) | `sourceVideo` + `prompt` |
| Extend a clip (+7s) | `video` `operation:"extend"` — **no model** | `sourceVideo` + `prompt` |
| Talking-head avatar (face photo speaks) | `video` `"new"`, `model` from `video_avatar` | `startFrame` (face photo) + `audioFile` (**the ATTACHED audio if given — never re-synthesise it**; +`prompt` hint, optional) |
| Lip-sync / dub an existing clip | `lipsync_video` — **no model** | `video` + `audioFile` |

⚠ **Motion transfer (Kling Motion-Control)** needs a reference motion video + `characterOrientation`, which the `video` tool doesn't expose — it isn't usable through the standard tool right now.

## Choosing within a category — pick on merit

Once the category and input shape are fixed, several models may qualify. **Choose deliberately from each model's strengths — do not just grab whatever's first, and do not fall back to WAN merely because a better model errored.** These are the generative (`operation:"new"`) models BRAXIL has enabled:

| Model | Best at | Watch out for |
|---|---|---|
| **Seedance 2.0** `bytedance/seedance-2.0/*` | **Default first choice — best quality-per-cost.** Only one with `reference-to-video` (compose from up to 9 refs) and true text-to-video. Native audio, up to 15s, honours `seed`, most aspect ratios, **reaches 4k** (all three endpoints; pass `resolution: "4k"`). **Richest COLOR SCIENCE of the family — the one for cinematic/graded looks.** | Photoreal faces need reference PREP → `references/usage/seedance.md`. |
| **Seedance 2.5** `bytedance/seedance-2.5/*` | Longer clips (**up to 30 s**) and much bigger reference caps (≤30 images + reference audio ≤10). Pick it when a clip must exceed 15 s or carry more refs than 2.0 allows. | **720p max** (no 1080p/4k), no `seed`, and a **cleaner, more NEUTRAL color science: the same warm-35mm cinematic prompt comes out visibly flatter than on 2.0** (field-observed). Grade-critical cinematic pieces stay on 2.0. Same likeness filter/PREP as 2.0. |
| **Kling v3 Pro** `fal-ai/kling-video/v3/pro/image-to-video` | Strong image-to-video for **product & controlled cinematic** shots; clean motion, start+end frame, up to 15s. Best pick when Seedance can't do it. | Image-to-video only. Inherits aspect from the start image (no `aspectRatio`/`resolution`), ignores `seed`. |
| **Veo 3.1** `fal-ai/veo3.1/image-to-video` | Top-tier realism; reaches 4k. Reach for it when you need maximum photoreal polish (Seedance also does 4k, so pick Veo for the realism, not just the resolution). | Image-to-video only, no `endFrame`, durations locked to `4s/6s/8s`, 16:9 or 9:16 only. Priciest — use when the max-quality is the point. |
| **Luma Ray v3.2** `luma/agent/ray/v3.2/text-to-video` · `…/image-to-video` | **Elegant, clean-motion b-roll / cinematic** clips; polished all-rounder. Does text-to-video AND image-to-video (start+end frame), most aspect ratios, up to 1080p. Also does **reframe** (change a clip's aspect ratio) and **video-to-video** — see below. | Only `5s`/`10s` durations. **No native audio.** Caps at 1080p. |
| **Gemini Omni Flash** `google/gemini-omni-flash/image-to-video` · `…/reference-to-video` | **Fast & cheap** image-to-video and reference-to-video (compose from up to 10 refs). Good for quick iteration / social hooks. | Minimal controls: `16:9`/`9:16` only, `3–10s`, no `seed`/`resolution`. Lower fidelity than the cinematic models. |
| **WAN 2.7** `fal-ai/wan/v2.7/image-to-video` | A fallback image-to-video when the others can't serve the shape. | **Last resort — pricey and weaker.** No audio. Don't pick it over Seedance/Kling/Veo/Luma just because one of them errored; retry the better ones first. |

**Decision in one line (this table is GENERATION only — new clips):** refs or text-only → **Seedance** (or **Gemini Omni Flash** for a fast/cheap take); animating a photo → **Seedance**, then **Kling** (product/controlled), **Veo** (max photoreal realism) or **Luma** (elegant b-roll); only if none fit → **WAN**. (Need 4k? Both Seedance and Veo deliver it.) **Editing an EXISTING clip is not here → `operation:"edit"`, model UNSET, best editor Gemini Omni Flash (next section).**

### Editing an existing clip — the editor is auto-picked, but here's who's best

Edits are **`operation:"edit"` (leave `model` UNSET)** — the server/router picks the editor from the `video_editing` pool for you. You don't choose the slug, but knowing the merits tells you what to expect (and which `default` label to set in the backoffice):

| Editor | Best at | Notes |
|---|---|---|
| **Gemini Omni Flash** `google/gemini-omni-flash/edit` | **The best, default editor.** Follows a plain-language instruction and **keeps everything else in the frame the same** — the go-to for "change/add/remove X in this clip". Output dims/length follow the source. | Unavailable in EEA/CH/UK. Make it the pool's `default`-labelled row so the router picks it first. |
| **Luma Ray v3.2 v2v** `luma/agent/ray/v3.2/video-to-video` | Whole-clip **restyle / colour-grade / repaint / motion swap** — a stylistic transform of the source, not a surgical edit. | 5s/10s, up to 1080p. |
| **Luma Ray v3.2 reframe** `luma/agent/ray/v3.2/reframe` | **Re-aspect a clip** (e.g. 16:9 → 9:16), outpainting the newly exposed areas. The pick when the ask is "change the aspect ratio / reframe for Reels". | Needs the target `aspectRatio`. |
| **Kling o3 v2v** `fal-ai/kling-video/o3/*/video-to-video/*` | Reference-guided v2v when you need extra style/character image refs bound to the edit. | Niche; the router only reaches for it over Gemini when its shape/label fits. |

Rule of thumb: a **targeted instruction edit** ("remove the logo", "make it night") → **Gemini Omni Flash**; a **full restyle** → Luma v2v; an **aspect-ratio change** → Luma reframe. Since the agent leaves `model` unset, enforce this by putting the `default` label on Gemini Omni Flash's `video_editing` row in the backoffice. See `references/models.md`.

### Two overrides that beat the table

- **A matching label wins.** A model's labels (Catalog table's **Labels** column) mark what it's BEST-SUITED for (`avatar`/`talking-head`, `anime`, `product`, `cinematic`, `nature`…). If the user's request matches a label, prefer that labelled model even over the default. When no label matches, choose on the strengths above.
- **Input shape is absolute.** Only choose among models that actually accept your shape (a text-only prompt can't go to an image-to-video slug; an `endFrame` needs a model that takes one). If the preferred model's variant can't take your input, step to the next that fits — don't force it.

Some behaviours live on a single model (motion transfer, fixed-length extend, server-routed edit); find them by input shape in `references/models.md`, not by memory.

## Editing a clip longer than 10 seconds — ASK FOR THE SEGMENT FIRST

An AI video edit covers **10 SECONDS AT MOST**. So before editing an existing clip, look at its duration:

- **≤ 10 s** → edit it as usual (`operation:"edit"`, `sourceVideo` = the clip).
- **> 10 s** → **do NOT start generating.** The user has to tell you WHICH part they want changed:
  1. Show the clip with the **segment-selection tool armed**: `show_video` with `selectSegment: true` (MCP), or `show_result` `resourceType:"video"` + `selectSegment: true` (native tools). It works whether the clip is already open in the work area or not — if it is visible, the tool is simply armed on it; if not, it opens with the tool armed.
  2. **Ask them in the chat**, in their language, to drag the segment they want modified, and say plainly that an edit can cover at most 10 seconds. Then **WAIT for their answer**.
  3. Their pick reaches you in the **`# WORKING AREA`** block of the next turn (the selected segment, start/end in ms). **Edit exactly that segment** — cut it out of the source and edit the cut, never the whole clip.

The same rule holds when the clip arrives as an attachment rather than open in the work area: show it with `selectSegment` and ask.

## 🔴 When a generation FAILS (likeness filter, content policy, provider error)

**NEVER strip information from the request to force it through.** The goal is ALWAYS to generate the clip as well as possible — not to generate it at any cost. Dropping a reference image (a turnaround, a plate, a continuity frame), thinning the prompt's identity/continuity detail, or downgrading to a weaker model just to dodge an error produces a clip that "succeeds" while betraying the piece — a drifted face, reset positions, a broken set. **If the flow says a reference must be attached, it STAYS attached on every attempt, no exceptions.** A failed render with the right inputs is a better outcome than a finished render with the wrong ones.

1. **First response: RETRY THE IDENTICAL REQUEST — unchanged — two or three times.** These failures are highly RANDOM: the same request that just got rejected (filter false-positive, transient provider error) very often goes through on the second or third try. Touch nothing between attempts.
2. **Still failing? Fix the CAUSE with its sanctioned mechanism — never by removing information:**
   - Likeness/face filter → launder the offending reference through Seedream (turnaround-style 1:1 re-description, per the model's card) and attach the laundered copy. The reference still goes in.
   - Content-policy on the prompt's wording → reword the flagged phrasing WITHOUT losing any of the scene's content or constraints.
   - Input shape the model can't take → a different model that accepts the SAME references — never the same model with the references dropped.
3. **Nothing works? STOP and tell the user** what fails and the options. Never silently deliver a degraded clip — the user can't see what you quietly removed.

## Gotchas

- **startFrame ≠ referenceImages.** startFrame is a strict commitment to identical pixels at t=0. Storyboards, sheets, mood boards, character/style refs are `referenceImages`. When unsure, use `referenceImages` — the wrong choice fails or produces a different take.
- **Editing/extending a video?** Use `operation:"edit"`/`"extend"` with `sourceVideo` = the clip (no `model`). Never re-attach the images that video was generated from — that rebuilds a *different* take.
- **Audio defaults ON** for generative models (`withAudio`).
- **Duration is per-model** — some cap at 8s, others reach 15s, and extend is a fixed length. Check the card before promising a duration.
- **Only some models reach 4k** — others ignore `resolution` or inherit it from the input. Check the card.
- Read the model's card in `references/models.md` before setting `endFrame`, `resolution`, `duration` or `cameraMovement` — support and accepted values are per-model.
