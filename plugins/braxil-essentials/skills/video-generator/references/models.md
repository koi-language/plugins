# Video models — per-model parameters (in `video` tool terms)

Only models **enabled in the BRAXIL backend** are listed, and each table uses the **actual MCP tool parameters the agent can set** — NOT raw fal fields.

`video` parameters: **`operation` ('new'|'edit'|'extend'), `model`, `prompt`, `startFrame`, `endFrame`, `referenceImages`, `referenceVideos` (new only — continuation/prev-clip), `sourceVideo` (edit/extend), `aspectRatio`, `cameraMovement`, `resolution`, `duration`, `quality`, `withAudio`, `seed`, `extra_params`** (`seed`, `referenceVideos` and `extra_params` are `operation:"new"` only; `seed` honoured by Seedance / Veo / WAN, ignored by Kling; `extra_params` = model-specific escape hatch, see Notes). There is NO `characterOrientation`, `keepOriginalSound` or `audioUrl` on this tool.

`cameraMovement` (optional): `static`, `pan_left`, `pan_right`, `zoom_in`, `dolly_in`, `orbit_right`, … — a motion hint honoured by some models, ignored by others.

Talking-head **avatar** rides the SAME tool: `operation:"new"` + `audioFile` + a REQUIRED `model` from the `video_avatar` cards (see the Avatar section).

**Multi-shot** (one generation renders several hard-cut shots mapped to reference panels — the storyboard→video path): the **Seedance 2.0 family** AND the **MiniMax H3 family**. **Every other video model produces ONE continuous shot per call.** Each card states it explicitly. When a clip needs several hard-cut shots you MUST pick a multi-shot model; choose it on this capability + fit (read the cards), not from any fixed label. **Multi-shot is a model BEHAVIOUR, not a schema field** — it isn't in the fal openapi, so it's curated per card from testing/docs, not auto-derived.
- **Real human faces do NOT force the model choice — BOTH Seedance and MiniMax H3 handle photoreal faces perfectly.** ⚠️ Do NOT steer a live-action / real-face storyboard to MiniMax just because it has real faces — that is NOT a reason to avoid Seedance. **Seedance does real faces perfectly via its documented workaround: reproduce each character's turnaround through Seedream with a detailed re-description** (a Seedream reproduction clears Seedance's likeness filter; see the Seedance reference-to-video card's reference-PREP section / `references/usage/seedance.md`). MiniMax H3 accepts photoreal references directly — its ONLY edge here is skipping that one Seedream generation step, not any capability Seedance lacks. So pick the model on **craft, look, limits and fit** (Seedance's craft skill + look, its 4k reach, its reference caps, etc.), never on the mere presence of real faces.

Every card lists that model's **hard limits (from the fal schema)** — prompt char cap, max references, duration range, enums. Respect them: exceeding a limit (e.g. a prompt over the model's max) fails the call. If your prompt is over the cap, compress it, don't truncate blindly.

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

- **Limits (fal schema):** `prompt` no char cap. **Multi-shot: YES** — native (several hard-cut shots in one clip, shots mapped to reference panels; the storyboard→video model).
- **Rejects**: startFrame, endFrame, referenceImages.
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

- **Limits (fal schema):** `prompt` no char cap. **Multi-shot: YES** (native, hard-cut shots → panels).
- **Rejects**: referenceImages.
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

- **Limits (fal schema):** `prompt` no char cap; `referenceImages` **≤9**, `referenceVideos` **≤3**, reference audio ≤3 — **combined ≤12 files total** (hard cap). **Multi-shot: YES** — native (hard-cut shots → panels; THE storyboard→video model).
- **Rejects**: startFrame, endFrame. *Not settable via the tool:* reference AUDIO (the model supports it, but `video` exposes no `audioUrl`). `referenceVideos` IS available on `operation:"new"` (continuation / prev-clip). **Extra params** (via `extra_params` — see the Notes): `bitrate_mode` (`standard`/`high`).
- **🛡️ Reference PREP — MANDATORY for photoreal human faces. 📖 Full guide → `references/usage/seedance.md`.** Seedance's likeness filter REJECTS the whole render (`"image_urls: may contain likenesses of real people"`) for a real-looking face. In short: **reproduce each character's turnaround 1:1 through Seedream with a FULL re-description** of the subject (Image 1 = the turnaround itself; the detailed re-description is what makes Seedream re-synthesise it and clear the filter — a bare "reproduce exactly" fails). The chained previous clip gets a **blurred copy** when it shows real faces. Stylized faces / set plates / props need nothing. Read the guide before rendering with a real-face storyboard.
-
### MiniMax H3 — Text-to-Video — `minimax/h3/text-to-video`
- text-only (no frames). MiniMax Hailuo-03; fixed 2K output.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string | English. |
| aspectRatio | optional | `21:9·16:9·4:3·1:1·3:4·9:16` | clamped to nearest; NO `auto` — omit → 16:9. |
| resolution | optional | `2K` only | fixed by the model; any other value is ignored (always 2K). |
| duration | optional | 5–15 s (integer) | omit → 5s. |

- **Limits (fal schema):** `prompt` **1–2000 chars** (HARD max 2000 — over that the call is rejected; compress, keep the key beats). **Multi-shot: YES** — several hard-cut shots in one generation.
- **Audio: NATIVE and always ON** — the model generates synced sound/dialogue itself (usually very good). There's no `withAudio` toggle in the schema, so you can't turn it off or steer it here — but it DOES come out with sound; do NOT warn the user that audio is "uncontrollable" or might be missing. (For a project that needs music on a separate track, add that track later; the clip's own diegetic audio is fine.)
- **Rejects**: startFrame, endFrame, referenceImages, referenceVideos. *Not settable:* `seed` (not in the schema).

### MiniMax H3 — Image-to-Video — `minimax/h3/image-to-video`
- needs `startFrame` (optional `endFrame`). Fixed 2K output.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image | literal first frame; output dims follow it. |
| endFrame | optional | image | first→last keyframe interpolation. |
| prompt | required | string | motion description — REQUIRED on this slug. |
| resolution | optional | `2K` only | fixed (always 2K). |
| duration | optional | 5–15 s (integer) | omit → 5s. |

- **Limits (fal schema):** `prompt` **1–2000 chars** (HARD max 2000 — compress if over). **Multi-shot: YES** — several hard-cut shots in one generation.
- **Audio: NATIVE and always ON** — the model produces synced sound itself (no `withAudio` toggle in the schema; you can't turn it off or steer it, but it DOES come out with audio — don't warn the user it's missing/uncontrollable).
- No `aspectRatio` (output follows the image). **Rejects**: referenceImages, referenceVideos. *Not settable:* `seed`.

### MiniMax H3 — Reference-to-Video — `minimax/h3/reference-to-video`
- composes from `referenceImages` (+ `referenceVideos`). Fixed 2K output.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string; refs cited as `Image N` / `Video N` / `Audio N` (the engine rewrites the runtime's `@refN` for you) | |
| referenceImages | optional | up to 9 images | |
| referenceVideos | optional | up to 3 clips (2–15 s each, combined ≤ 15 s) | continuation / composition refs. |
| aspectRatio | optional | `adaptive·21:9·16:9·4:3·1:1·3:4·9:16` | omit → adaptive. |
| resolution | optional | `2K` only | fixed (always 2K). |
| duration | optional | 5–15 s (integer) | omit → 5s. |

- **Limits (fal schema):** `prompt` **1–2000 chars** (HARD max 2000 — compress if over); `referenceImages` **≤9**, `referenceVideos` **≤3** (2–15 s each, combined ≤15 s), reference audio ≤3. **Multi-shot: YES** — several hard-cut shots in one generation, shots mapped to the reference panels (a storyboard→video path, like Seedance).
- **✅ Accepts REAL human faces in references directly — NO tricks.** MiniMax takes photoreal character references AS-IS: attach the raw turnarounds, no Seedream laundering, no blur. ⚠️ This is a **convenience (fewer steps), NOT a reason to prefer it over Seedance for real faces** — Seedance handles real faces perfectly too, via its documented Seedream turnaround-(re)generation workaround (see its card's reference-PREP section). Real faces alone must NEVER decide the model; choose on craft/look/limits/fit.
- **Audio: NATIVE and always ON** — the model generates synced sound/dialogue itself (no `withAudio` toggle in the schema; you can't turn it off or steer it, but it DOES come out with audio — don't warn the user it's missing/uncontrollable).
- The model also accepts up to 3 reference AUDIO clips (each needs at least one image or video ref) but that is **not settable via the tool** (`video` exposes no `audioUrl`). **Rejects**: startFrame, endFrame. *Not settable:* `seed`.

### Flux 3 — Text-to-Video — `blackforestlabs/flux-3/text-to-video`
- text-only (no frames). Black Forest Labs Flux 3; caps at 1080p.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string, no char cap | |
| aspectRatio | optional | `auto·21:9·2:1·16:9·4:3·1:1·3:4·9:16` | clamped to nearest. |
| resolution | optional | `720p·1080p` (low→720p, medium/high/ultra→1080p) | omit → 1080p. NO 4k. |
| duration | optional | `auto·5–20` s (whole seconds) | omit → auto. |
| withAudio | optional | true/false | default true. Native audio at no extra cost. |

- **Limits (fal schema):** `prompt` no char cap. **NO `seed` input** (the output reports a seed but it can't be pinned — true for EVERY Flux 3 video endpoint). `safety_tolerance` 0–4 (we send 4 = loosest). **Multi-shot: NO** — one continuous shot per call (for hard-cut storyboard shots use Seedance/MiniMax H3).
- **Rejects**: startFrame, endFrame, referenceImages, referenceVideos.
- **Pricing (fal):** $0.17/s @720p, $0.29/s @1080p.

### Flux 3 — Image-to-Video — `blackforestlabs/flux-3/image-to-video`
- needs `startFrame` + `prompt`.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string | motion description. |
| startFrame | required | image (PNG/JPEG/WebP) → first frame | |
| aspectRatio | optional | `auto·21:9·2:1·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `720p·1080p` | omit → 1080p. |
| duration | optional | `auto·5–20` s | omit → auto. |
| withAudio | optional | true/false | default true. |

- **Limits (fal schema):** no `seed`; no `end_image_url` on this slug (use the first-last sibling for two anchors). **Multi-shot: NO**.
- **Rejects**: endFrame, referenceImages, referenceVideos.
- **Pricing (fal):** $0.17/s @720p, $0.29/s @1080p.

### Flux 3 — First-Last-Frame-to-Video — `blackforestlabs/flux-3/first-last-frame-to-video`
- needs `startFrame` + `endFrame` + `prompt`.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string | |
| startFrame | required | first frame image | |
| endFrame | required | last frame image | |
| aspectRatio | optional | `auto·21:9·2:1·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `720p·1080p` | omit → 1080p. |
| duration | optional | `5–20` s (INTEGER, EXPLICIT) | omit → 5s. NO `auto` — an explicit duration is required to place the end frame. |
| withAudio | optional | true/false | default true. |

- **Limits (fal schema):** no `seed`. **Multi-shot: NO**.
- **Rejects**: referenceImages, referenceVideos.
- **Pricing (fal):** $0.17/s @720p, $0.29/s @1080p.

### Flux 3 — Keyframes-to-Video — `blackforestlabs/flux-3/keyframes-to-video`
- needs `referenceImages` (1–10 stills) + `prompt`. Interpolates ONE continuous clip THROUGH the pinned images.
- ⚠️ **Name collision, NOT the storyboard pipeline.** This is a fal MODEL that just tweens through a few pinned stills. It is NOT the `keyframes-to-video` SKILL (the storyboard→video orchestrator). Don't confuse them.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string | |
| referenceImages | required | 1–10 images → pinned keyframes | pinned in ORDER, evenly spaced from frame 0 to `duration×24` (video is 24 fps). |
| aspectRatio | optional | `auto·21:9·2:1·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `720p·1080p` | omit → 1080p. |
| duration | optional | `5–20` s (INTEGER, EXPLICIT) | omit → 5s. NO `auto` — needed to validate keyframe positions. |
| withAudio | optional | true/false | default true. |

- **Limits (fal schema):** `referenceImages` **≤10** (each becomes a keyframe pinned to a unique `frame_index` = frame position in the 24 fps clip, ≤ `duration×24`). no `seed`. **Multi-shot: NO** (one continuous interpolated shot).
- **Rejects**: startFrame, endFrame, referenceVideos.
- **Pricing (fal):** $0.17/s @720p, $0.29/s @1080p.

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

### Flux 3 — Extend Video — `blackforestlabs/flux-3/extend-video`  *(operation `"extend"`)*
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"extend"` | |
| sourceVideo | required | MP4 **<50 MB and <15 s** (rides in `referenceVideos[0]`) | source constraints are the caller's to meet; no transcode here. |
| prompt | required | how the clip continues from its final frames | |
| aspectRatio | optional | `auto·21:9·2:1·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `720p·1080p` | omit → 1080p. |
| duration | optional | `auto·5–20` s | REAL extension length (unlike Veo's fixed 7 s). omit → auto. |
| withAudio | optional | true/false | default true. |

- **Limits (fal schema):** source MP4 <50 MB & <15 s. no `seed`. **Rejects**: startFrame, endFrame, referenceImages.
- **Pricing (fal):** $0.41/s @720p, $0.53/s @1080p (pricier than the other Flux 3 endpoints).

---

## Avatar (`video_avatar`) — talking video from a face PHOTO, via the SAME video tool

**ONLY for making a still face photo SPEAK a driving audio — never for anything else.** Same `video` tool, `operation:"new"`; the avatar mode switches on when you pass `audioFile`:

- **`model` is REQUIRED, you pick it** from the cards below (all carry the `video_avatar` category) — exactly like every other generation, no auto-pick.
- **`startFrame`** = the face photo (front-facing portraits work best). Output dimensions FOLLOW THE PHOTO — crop/frame it to the shape you want BEFORE calling (`aspectRatio` is ignored by these models).
- **`audioFile`** = the audio the avatar speaks. The clip's length follows the audio.
- **`prompt`** is OPTIONAL but **SUPPORTED by every current avatar model** — Aurora, OmniHuman v1.5 AND Kling AI Avatar v2 Pro all expose a `prompt` field on fal, and it's plumbed end-to-end (the `video` tool → gateway → adapter → fal). Use it to STEER the performance: expression, emotion, gesture, camera framing, background/scene. Write it in English. Do NOT leave it blank just because it's optional — a short scene/style hint measurably shapes the result; skipping it is the common mistake. No duration, no withAudio (the audio IS the track), no referenceImages/Videos.

- **Picking WHICH person speaks in a multi-person photo — pass the FULL image + a `mask_url` (OmniHuman only). NEVER crop.** Always keep the whole frame as `startFrame`. Avatar models animate the single face they detect and the `prompt` does NOT choose the speaker, BUT **OmniHuman v1.5** exposes a native `mask_url` — *"only the person in the white area of the mask will speak"*. Pass it via `extraParams` as a LOCAL mask image path: `extraParams: { "mask_url": "/path/to/mask.png" }` — the engine uploads it to fal and swaps in the URL for you. Build the mask by segmenting the target subject (SAM smart-select / the mask tools) so their area is WHITE and everyone else BLACK, over the full-frame dimensions. Aurora and Kling AI Avatar have NO mask param, so subject selection there isn't possible — use OmniHuman when the user points at one of several people.

### Creatify Aurora — `fal-ai/creatify/aurora`  *(avatar — DEFAULT pick)*

| param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | face photo | output dims follow it |
| audioFile | required | ~≤60 s | |
| resolution | optional | `480p·720p` (default 720p) | maps low→480p, medium+→720p |
| prompt | optional | English scene/style hint | accepted & used — steers expression, gesture, framing & background; pass it, don't leave it blank |

- **The preferred avatar model — reach for it first** unless the user names another or needs 1080p output.
- Same source-photo size behaviour as the others (worker download cap — see OmniHuman's note; the engine auto-shrinks, and on a "Failed to download" error you run `optimize_image`).

### OmniHuman v1.5 — `fal-ai/bytedance/omnihuman/v1.5`  *(avatar — 1080p alternative)*

| param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | face photo | output dims follow it |
| audioFile | required | **≤30 s** (1080p) / ≤60 s (720p) | fal-documented; the strict 30 s cap applies at the default 1080p |
| resolution | optional | `720p·1080p` (default 1080p) | fal's own docs: 720p is faster AND allows 60 s audio |
| prompt | optional | English scene/style hint | accepted & used — steers expression, gesture, framing & background; pass it, don't leave it blank |
| extraParams.mask_url | optional | LOCAL mask image path | **subject selector** — only the person in the WHITE area speaks; everyone else BLACK. Full-frame dims. Pass a local path in `extraParams`; the engine uploads it to fal. OmniHuman ONLY (Aurora/Kling ignore it). Use it to make one of several people talk WITHOUT cropping. |

- Pick it over Aurora when the user asks for 1080p or a full-body performance.
- **Source-photo size — NOT in fal's schema, learned in production:** the avatar worker fails to DOWNLOAD multi-MB source images (`body.image_url: Failed to download the file` — a 5 MB 2560px PNG fails, a 234 KB 1280px JPEG works). The engine now auto-shrinks the photo to ≤2 MB / ≤2048px before upload, so do NOT pre-process it yourself (no sips/ffmpeg resizing). If you still see that error, retrying the identical call is pointless — run **`optimize_image({ image })`** (LOSSLESS PNG shrink to ≤2 MB / ≤2048px) and retry with its `savedTo`. **NEVER convert the photo to JPEG with sips/ffmpeg — that destroys quality.**

### Kling AI Avatar v2 Pro — `fal-ai/kling-video/ai-avatar/v2/pro`  *(avatar)*

| param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | face photo | output dims follow it |
| audioFile | required | ~≤60 s | |
| prompt | optional | English scene/style hint | accepted & used — steers expression, gesture, framing & background; pass it, don't leave it blank |

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

## Background removal (`video_background_removal`) — via the SAME `video` tool

Strip the backdrop from an EXISTING video → a transparent-background clip. Rides the `video` tool with **`operation:"bg-remove"`** (NOT the image `background_removal` tool, which is image-only):

- **`operation:"bg-remove"`** + **`sourceVideo`** (the clip) + **`model`** = a `video_background_removal`-category slug. No prompt, no audio.

### Bria Video Background Removal — `bria/video/background-removal`

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"bg-remove"` | |
| sourceVideo | required | path/@mention to the existing clip | fal field `video_url`. |
| model | required | `bria/video/background-removal` | agent-picked (the `video_background_removal` slug). |

- **Output is TRANSPARENT by default** in an alpha-capable codec (`webm_vp9`) — that's what makes "remove the background" actually transparent. `mp4_h264`/`mp4_h265` CANNOT carry alpha (a transparent request bakes to BLACK).
- **`extraParams` (this model's knobs):**
  - `background_color` — default `Transparent`. Enum: `Transparent·Black·White·Gray·Red·Green·Blue·Yellow·Cyan·Magenta·Orange` (a solid colour instead of alpha).
  - `output_container_and_codec` — default `webm_vp9` (alpha). Enum: `mp4_h265·mp4_h264·webm_vp9·mov_h265·mov_proresks·mkv_h265·mkv_h264·mkv_vp9·gif`. **Alpha-capable ones: `webm_vp9`, `mov_proresks`, `mkv_vp9`.** Use `mp4_h264` only with a SOLID `background_color` (opaque delivery).
  - e.g. opaque white-background mp4: `extraParams: { "output_container_and_codec": "mp4_h264", "background_color": "White" }`.
- Audio: kept by default; drop it with `withAudio: false` (maps to `preserve_audio: false`).

---

## Notes
- **startFrame ≠ referenceImages**: startFrame = literal frame 0; storyboards/style refs are `referenceImages` (only reference-to-video accepts them).
- **Duration & resolution are per-model** — Veo `4s/6s/8s`, extend fixed 7s, Seedance/Kling up to 15s. **4k is reached by Veo AND ALL THREE Seedance 2.0 endpoints (text-to-video, image-to-video, reference-to-video)** — per their fal schemas; check each model's row. Most models emit 1080p when you omit resolution (Seedance t2v/i2v → 1080p, ref-to-video → 720p).
- **`seed` IS a `video` parameter** (on `operation:"new"`) — honoured by Seedance / Veo / WAN, ignored by Kling. **`referenceVideos` IS a `video` parameter on `operation:"new"`** (continuation / prev-clip carry-over; honoured by reference-to-video models like Seedance). **`characterOrientation`, `keepOriginalSound`, `audioUrl` are NOT `video` parameters** — the agent cannot set them, even where a model supports them.
- **`extra_params` — the model-specific escape hatch.** For a per-model knob this tool does NOT expose as a first-class field (e.g. Seedance `bitrate_mode`), pass it inside `extra_params` as an object whose KEY is the EXACT provider field name (snake_case, as in the model's API) and value as the API expects — e.g. `extra_params: { "bitrate_mode": "..." }`. Only send params listed in the model's own row above; the keys travel verbatim to the provider (unknown ones are ignored). `extra_params` NEVER overrides a first-class param (duration/resolution/aspectRatio/…) — set those directly. Same mechanism exists on `generate_image` and `generate_audio`.
