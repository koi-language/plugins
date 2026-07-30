# Video models — per-model parameters (in `video` tool terms)

Only models **enabled in the BRAXIL backend** are listed, and each table uses the **actual MCP tool parameters the agent can set** — NOT raw fal fields.

`video` parameters: **`operation` ('new'|'edit'|'extend'), `model`, `prompt`, `startFrame`, `endFrame`, `referenceImages`, `referenceVideos` (new only — continuation/prev-clip), `sourceVideo` (edit/extend), `aspectRatio`, `cameraMovement`, `resolution`, `duration`, `quality`, `withAudio`, `seed`, `extra_params`** (`seed`, `referenceVideos` and `extra_params` are `operation:"new"` only; `seed` honoured by Seedance / Veo / WAN, ignored by Kling; `extra_params` = model-specific escape hatch, see Notes). There is NO `characterOrientation`, `keepOriginalSound` or `audioUrl` on this tool.

`cameraMovement` (optional): `static`, `pan_left`, `pan_right`, `zoom_in`, `dolly_in`, `orbit_right`, … — a motion hint honoured by some models, ignored by others.

Talking-head **avatar** rides the SAME tool: `operation:"new"` + `audioFile` + a REQUIRED `model` from the `video_avatar` cards (see the Avatar section).

> Each model's **categories** and **labels** are NOT repeated here — they are backend-managed and shown per model in the live **Catalog table** in the tool's own description. This file is the parameter contract only.

---

## Models you pick with `model` (operation `"new"`)

### Seedance 2.0 — Text-to-Video — `bytedance/seedance-2.0/text-to-video`
- text-only (no frames).

| `video` param | Req? | Accepted values (this model) | Notes |
|---|---|---|---|
| prompt | required | string | English. |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | clamped to nearest. |
| resolution | optional | `480p·720p·1080p·4k` | omit → 1080p. Reaches 4k (per fal schema). |
| duration | optional | 4–15 s | omit → auto. |
| withAudio | optional | true/false | default true. |
| seed | optional | integer | reproducibility — same seed + prompt ⇒ same clip. |

- **Rejects**: startFrame, endFrame, referenceImages. ▶ activate `braxil-essentials:seedance-2-0`.

### Seedance 2.0 — Image-to-Video — `bytedance/seedance-2.0/image-to-video`
- needs `startFrame` (optional `endFrame`).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image | literal first frame. |
| endFrame | optional | image | first+last interpolation. |
| prompt | optional | string | motion description. |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `480p·720p·1080p·4k` | omit → 1080p. Reaches 4k (per fal schema). |
| duration | optional | 4–15 s | omit → auto. |
| withAudio | optional | true/false | default true. |
| seed | optional | integer | reproducibility — same seed + prompt ⇒ same clip. |

- **Rejects**: referenceImages. ▶ activate `braxil-essentials:seedance-2-0`.

### Seedance 2.0 — Reference-to-Video — `bytedance/seedance-2.0/reference-to-video`
- composes from `referenceImages`.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string; `@refN` binds to the images by position | |
| referenceImages | required | up to 9 images | via the tool, only IMAGE refs are settable. |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `480p·720p·1080p·4k` | omit → 720p. Reaches 4k (per fal schema). |
| duration | optional | `auto·4–15` s | omit → auto. |
| withAudio | optional | true/false | default true. |
| seed | optional | integer | reproducibility — same seed + prompt ⇒ same clip. |

- **Rejects**: startFrame, endFrame. *Not settable via the tool:* reference AUDIO (the model supports it, but `video` exposes no `audioUrl`). `referenceVideos` IS available on `operation:"new"` (continuation / prev-clip). **Extra params** (via `extra_params` — see the Notes): `bitrate_mode` (encoder bitrate mode). ▶ activate `braxil-essentials:seedance-2-0`.

### Veo 3.1 — Image-to-Video — `fal-ai/veo3.1/image-to-video`
- needs `startFrame` + `prompt`.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤20000 chars | |
| startFrame | required | image (≥720p, 16:9 or 9:16) | |
| aspectRatio | optional | `auto·16:9·9:16` | only these. |
| resolution | optional | `720p·1080p·4k` (low→720p, medium/high→1080p, ultra→4k) | omit → 1080p. |
| duration | optional | snapped to `4s·6s·8s` | omit → 8s. |
| withAudio | optional | true/false | default true. |
| seed | optional | integer | reproducibility — same seed + prompt ⇒ same clip. |

- **Rejects**: endFrame (no last frame on this slug), referenceImages.

### Kling v3 Pro — Image-to-Video — `fal-ai/kling-video/v3/pro/image-to-video`
- needs `startFrame` (optional `endFrame`).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image (≤10MB, aspect 0.40–2.50) | |
| endFrame | optional | image | |
| prompt | optional | string ≤2500 chars | |
| duration | optional | 3–15 s | omit → 5s. |
| withAudio | optional | true/false | Chinese/English voice. |

- **Rejects**: aspectRatio (inherited from start image), resolution, referenceImages.

### WAN 2.7 — Image-to-Video — `fal-ai/wan/v2.7/image-to-video`
- needs `startFrame` (optional `endFrame`).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image (JPEG/PNG/BMP/WEBP, ≤20MB) | |
| endFrame | optional | image | first-and-last-frame mode. |
| prompt | optional | string ≤5000 chars | |
| resolution | optional | `720p·1080p` (low/medium→720p, high/ultra→1080p) | omit → 1080p. |
| duration | optional | 2–15 s | omit → 5s. |
| seed | optional | integer 0–2147483647 | reproducibility — same seed + prompt ⇒ same clip. |

- **Rejects**: aspectRatio (follows input image), withAudio. *Not settable via the tool:* audio-driven lip-sync (`audioUrl`).

### Pixverse v6 — Image-to-Video — `fal-ai/pixverse/v6/image-to-video`
- needs `startFrame`. First frame ONLY — it does not interpolate to a tail frame.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image | the literal first frame. |
| prompt | required | string ≤2048 bytes | the ONLY i2v model here that requires a prompt. |
| resolution | optional | `360p·540p·720p·1080p` (low→540p, medium→720p, high/ultra→1080p) | omit → 720p. |
| duration | optional | 1–15 s (any integer, not an enum) | omit → 5s. |
| withAudio | optional | true/false | BGM + SFX + dialogue. **Upstream default is OFF**, so pass it explicitly for a scored clip. |
| seed | optional | integer | reproducibility — same seed + prompt ⇒ same clip. |

- **Rejects**: aspectRatio (inherited from the start image), endFrame, referenceImages. *Not settable via the tool:* `style` (anime / 3d_animation / clay / comic / cyberpunk), `thinking_type` (prompt auto-optimisation), `generate_multi_clip_switch` (dynamic camera cuts), `negative_prompt`.

### Luma Ray 3.2 — Text-to-Video — `luma/agent/ray/v3.2/text-to-video`
- text-only (no frames). Elegant, clean-motion cinematic / b-roll.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤6000 chars | English. |
| aspectRatio | optional | `3:4·4:3·1:1·9:16·16:9·21:9` | clamped to nearest; omit → 16:9. |
| resolution | optional | `540p·720p·1080p` (low→540p, medium→720p, high/ultra→1080p) | omit → 1080p. |
| duration | optional | snapped to `5s`/`10s` (≤7→5s, else 10s) | omit → 5s. |

- **Rejects**: startFrame, endFrame, referenceImages. **No native audio** (no `withAudio`), no `seed`.

### Luma Ray 3.2 — Image-to-Video — `luma/agent/ray/v3.2/image-to-video`
- needs `startFrame` (optional `endFrame`).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤6000 chars | motion description. |
| startFrame | required | image | literal first frame → `image_url`. |
| endFrame | optional | image | last frame → interpolation. |
| aspectRatio | optional | `3:4·4:3·1:1·9:16·16:9·21:9` | omit → 16:9. |
| resolution | optional | `540p·720p·1080p` | omit → 1080p. |
| duration | optional | `5s`/`10s` | omit → 5s. |

- **Rejects**: referenceImages. **No native audio**, no `seed`.

### Gemini Omni Flash — Image-to-Video — `google/gemini-omni-flash/image-to-video`
- needs `startFrame` + `prompt`. Fast & cheap.
- 📖 **Usage guide → `references/usage/gemini-omni.md`** — READ before composing the prompt (prompting technique, image-role tags, audio).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤20000 chars | |
| startFrame | required | image | literal first frame → `image_url`. |
| aspectRatio | optional | `16:9·9:16` only | clamped to nearest orientation; omit → 16:9. |
| duration | optional | 3–10 s (clamped) | omit → 8s. |

- **Rejects**: endFrame, referenceImages, resolution, seed, withAudio.

### Gemini Omni Flash — Reference-to-Video — `google/gemini-omni-flash/reference-to-video`
- composes from `referenceImages` (up to 10). Fast & cheap.
- 📖 **Usage guide → `references/usage/gemini-omni.md`** — READ before composing the prompt (how to bind refs with `<IMAGE_REF_N>` tags, prompting technique, audio).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤20000 chars; bind refs positionally via `<IMAGE_REF_0>`-style tags yourself | |
| referenceImages | required | up to 10 images | |
| aspectRatio | optional | `16:9·9:16` only | omit → 16:9. |
| duration | optional | 3–10 s (clamped) | omit → 8s. |

- **Rejects**: startFrame, endFrame, resolution, seed, withAudio.

### Kling v3 Standard — Motion-Control — `fal-ai/kling-video/v3/standard/motion-control`
- motion transfer. ⚠ **Requires a reference motion video + `characterOrientation`, which the `video` tool does NOT expose (no `referenceVideos`/`characterOrientation` params).** Effectively not usable through the standard MCP `video` tool right now — do not pick it unless a dedicated path provides those inputs.

---

## Server-routed — operation `"edit"` / `"extend"` (leave `model` UNSET)

The server picks the editor; you pass `sourceVideo` + `prompt`.

### Gemini Omni Flash — Video Edit — `google/gemini-omni-flash/edit`  *(operation `"edit"`)*
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"edit"` | |
| sourceVideo | required | path/@mention to the clip | |
| prompt | required | edit instruction ≤20000 chars | tip: append "Keep everything else the same." |
- Output dims/length follow the source. Unavailable in EEA/CH/UK.
- 📖 **Usage guide → `references/usage/gemini-omni.md`** — READ before composing the prompt (edit prompting technique, audio keep-vs-regenerate, gotchas).

### Luma Ray 3.2 — Video-to-Video — `luma/agent/ray/v3.2/video-to-video`  *(operation `"edit"`)*
Restyle / transform an existing clip.
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"edit"` | |
| sourceVideo | required | path/@mention to the clip | → `video_url`. |
| prompt | required | string ≤6000 chars | how to edit the video. |
| resolution | optional | `540p·720p·1080p` | omit → 1080p. |
| duration | optional | `5s`/`10s` | omit → 5s. |
| startFrame | optional | image | first frame of the edited output. |

### Luma Ray 3.2 — Reframe — `luma/agent/ray/v3.2/reframe`  *(operation `"edit"`)*
Change a clip's **aspect ratio**, outpainting the newly exposed areas.
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"edit"` | |
| sourceVideo | required | source clip ≤30s | → `video_url`. |
| aspectRatio | **required** | `3:4·4:3·1:1·9:16·16:9·21:9` | the NEW aspect ratio (the point of reframe). |
| prompt | required | string ≤6000 chars | what to paint into the new areas. |
| resolution | optional | `540p·720p·1080p` | omit → 1080p. |

### Veo 3.1 — Extend Video — `fal-ai/veo3.1/extend-video`  *(operation `"extend"`)*
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"extend"` | |
| sourceVideo | required | 720p/1080p, 16:9 or 9:16 (no transcode) | |
| prompt | required | describes the extension | |
| duration | — | ignored — extension is a FIXED 7 s | |

---

## Avatar (`video_avatar`) — talking video from a face PHOTO, via the SAME video tool

**ONLY for making a still face photo SPEAK a driving audio — never for anything else.** Same `video` tool, `operation:"new"`; the avatar mode switches on when you pass `audioFile`:

- **`model` is REQUIRED, you pick it** from the cards below (all carry the `video_avatar` category) — exactly like every other generation, no auto-pick.
- **`startFrame`** = the face photo (front-facing portraits work best). Output dimensions FOLLOW THE PHOTO — crop/frame it to the shape you want BEFORE calling (`aspectRatio` is ignored by these models).
- **`audioFile`** = the audio the avatar speaks. The clip's length follows the audio.
- **`prompt`** is OPTIONAL here (English scene/style hint; some models ignore it). No duration, no withAudio (the audio IS the track), no referenceImages/Videos.

### Creatify Aurora — `fal-ai/creatify/aurora`  *(avatar — DEFAULT pick)*

| param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | face photo | output dims follow it |
| audioFile | required | ~≤60 s | |
| resolution | optional | `480p·720p` (default 720p) | maps low→480p, medium+→720p |
| prompt | optional | English scene hint | |

- **The preferred avatar model — reach for it first** unless the user names another or needs 1080p output.
- Same source-photo size behaviour as the others (worker download cap — see OmniHuman's note; the engine auto-shrinks, and on a "Failed to download" error you run `optimize_image`).

### OmniHuman v1.5 — `fal-ai/bytedance/omnihuman/v1.5`  *(avatar — 1080p alternative)*

| param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | face photo | output dims follow it |
| audioFile | required | **≤30 s** (1080p) / ≤60 s (720p) | fal-documented; the strict 30 s cap applies at the default 1080p |
| resolution | optional | `720p·1080p` (default 1080p) | fal's own docs: 720p is faster AND allows 60 s audio |
| prompt | optional | English scene hint | |

- Pick it over Aurora when the user asks for 1080p or a full-body performance.
- **Source-photo size — NOT in fal's schema, learned in production:** the avatar worker fails to DOWNLOAD multi-MB source images (`body.image_url: Failed to download the file` — a 5 MB 2560px PNG fails, a 234 KB 1280px JPEG works). The engine now auto-shrinks the photo to ≤2 MB / ≤2048px before upload, so do NOT pre-process it yourself (no sips/ffmpeg resizing). If you still see that error, retrying the identical call is pointless — run **`optimize_image({ image })`** (LOSSLESS PNG shrink to ≤2 MB / ≤2048px) and retry with its `savedTo`. **NEVER convert the photo to JPEG with sips/ffmpeg — that destroys quality.**

### Kling AI Avatar v2 Pro — `fal-ai/kling-video/ai-avatar/v2/pro`  *(avatar)*

| param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | face photo | output dims follow it |
| audioFile | required | ~≤60 s | |
| prompt | optional | English scene hint | |

- Takes ONLY photo + audio + prompt — every other param is ignored.
- Same source-photo size behaviour as OmniHuman (worker download cap, engine auto-shrinks to ≤2 MB / ≤2048px).

- **Practical caps whatever the model**: driving audio ≤30 s per call keeps you safe on every card; longer speeches → several avatar calls stitched on a timeline. Source photos are auto-shrunk by the engine to the worker's real download cap (≤2 MB / ≤2048px) — never pre-resize them yourself. Dubbing an EXISTING video is `lipsync_video`, never an avatar model.

---

## Lip-sync — dedicated tool (no `model` pick)

Re-voicing / dubbing an EXISTING video goes through its own tool, **`lipsync_video`** (not the avatar tool, and not `video`):

- **`lipsync_video({ video, audioFile })`** → serves `fal-ai/veed/lipsync/v2`. `video` = the source clip whose on-screen mouth is re-articulated; `audioFile` = the new audio track to sync to. Everything else in the source (framing, motion, background, dimensions, length) is preserved — only the lips change. Produces a NEW video.

| `lipsync_video` param | Req? | Notes |
|---|---|---|
| video | required | the existing clip to re-lipsync (fal field `video_url`). |
| audioFile | required | the new audio the video should speak (fal field `audio_url`). |

- Takes ONLY those two inputs — no prompt, aspectRatio, duration or seed (veed/lipsync/v2 exposes none). Output follows the source video's own dimensions and length.
- **Avatar vs lip-sync:** a face PHOTO → the `video` tool in avatar mode (`startFrame` + `audioFile` + a `video_avatar` model); an existing VIDEO → `lipsync_video`. Different shapes, different inputs.

---

## Notes
- **startFrame ≠ referenceImages**: startFrame = literal frame 0; storyboards/style refs are `referenceImages` (only reference-to-video accepts them).
- **Duration & resolution are per-model** — Veo `4s/6s/8s`, extend fixed 7s, Seedance/Kling up to 15s. **4k is reached by Veo AND ALL THREE Seedance 2.0 endpoints (text-to-video, image-to-video, reference-to-video)** — per their fal schemas; check each model's row. Most models emit 1080p when you omit resolution (Seedance t2v/i2v → 1080p, ref-to-video → 720p).
- **`seed` IS a `video` parameter** (on `operation:"new"`) — honoured by Seedance / Veo / WAN, ignored by Kling. **`referenceVideos` IS a `video` parameter on `operation:"new"`** (continuation / prev-clip carry-over; honoured by reference-to-video models like Seedance). **`characterOrientation`, `keepOriginalSound`, `audioUrl` are NOT `video` parameters** — the agent cannot set them, even where a model supports them.
- **`extra_params` — the model-specific escape hatch.** For a per-model knob this tool does NOT expose as a first-class field (e.g. Seedance `bitrate_mode`), pass it inside `extra_params` as an object whose KEY is the EXACT provider field name (snake_case, as in the model's API) and value as the API expects — e.g. `extra_params: { "bitrate_mode": "..." }`. Only send params listed in the model's own row above; the keys travel verbatim to the provider (unknown ones are ignored). `extra_params` NEVER overrides a first-class param (duration/resolution/aspectRatio/…) — set those directly. Same mechanism exists on `generate_image` and `generate_audio`.
