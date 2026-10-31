# Video models — per-model parameters (in `video` tool terms)

Only models **enabled in the BRAXIL backend** are listed, and each table uses the **actual MCP tool parameters the agent can set** — NOT raw fal fields.

`video` parameters: **`operation` ('new'|'edit'|'extend'), `model`, `prompt`, `startFrame`, `endFrame`, `referenceImages`, `referenceVideos` (new only — continuation/prev-clip), `referenceAudio` (new only — a single mp3/wav the model composes the soundscape from, e.g. the previous clip's extracted audio for a seamless diegetic bed; only models whose card lists reference audio honour it), `sourceVideo` (edit/extend), `aspectRatio`, `cameraMovement`, `resolution`, `duration`, `quality`, `withAudio`, `seed`, `extra_params`** (`seed`, `referenceVideos`, `referenceAudio` and `extra_params` are `operation:"new"` only; `seed` honoured by Seedance / Veo / WAN, ignored by Kling; `extra_params` = model-specific escape hatch, see Notes). There is NO `characterOrientation` or `keepOriginalSound` on this tool.

`cameraMovement` (optional): `static`, `pan_left`, `pan_right`, `zoom_in`, `dolly_in`, `orbit_right`, … — a motion hint honoured by some models, ignored by others.

Talking-head **avatar** rides the SAME tool: `operation:"new"` + `audioFile` + a REQUIRED `model` from the `video_avatar` cards (see the Avatar section).

**Multi-shot** (one generation renders several hard-cut shots mapped to reference panels — the storyboard→video path): the **Seedance family (use 2.5 — always)** AND the **MiniMax H3 family** (`minimax/h3/*`; the H3 Max Multi-Angle camera-move slug is NOT multi-shot). **Every other video model produces ONE continuous shot per call.** Each card states it explicitly. When a clip needs several hard-cut shots you MUST pick a multi-shot model; choose it on this capability + fit (read the cards), not from any fixed label. **Multi-shot is a model BEHAVIOUR, not a schema field** — it isn't in the fal openapi, so it's curated per card from testing/docs, not auto-derived.
- **Real human faces do NOT force the model choice — BOTH Seedance and MiniMax H3 handle photoreal faces perfectly.** ⚠️ Do NOT steer a live-action / real-face storyboard to MiniMax just because it has real faces — that is NOT a reason to avoid Seedance. **Seedance does real faces perfectly via its documented workaround: reproduce each character's turnaround through Seedream with a detailed re-description** (a Seedream reproduction clears Seedance's likeness filter; see the Seedance reference-to-video card's reference-PREP section / `references/usage/seedance.md`). MiniMax H3 accepts photoreal references directly — its ONLY edge here is skipping that one Seedream generation step, not any capability Seedance lacks. So pick the model on **craft, look, limits and fit** (Seedance's craft skill + look, its 4k reach, its reference caps, etc.), never on the mere presence of real faces.

Every card lists that model's **hard limits (from the fal schema)** — prompt char cap, max references, duration range, enums. Respect them: exceeding a limit (e.g. a prompt over the model's max) fails the call. If your prompt is over the cap, compress it, don't truncate blindly.

> Each model's **categories** and **labels** are NOT repeated here — they are backend-managed and shown per model in the live **Catalog table** in the tool's own description. This file is the parameter contract only.

---

## Models you pick with `model` (operation `"new"`)

> ⛔ **Seedance 2.0 cards below are kept for reference only — NEVER pick a 2.0 slug.** User decision: Seedance is always **2.5** (cards further down). The engine upgrades any 2.0 slug to the same 2.5 endpoint anyway (always the `/us/` slugs).

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
| referenceImages | required | up to 9 images | plus `referenceVideos` and `referenceAudio` (see Limits). |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `480p·720p·1080p·4k` | omit → 720p. Reaches 4k (per fal schema). |
| duration | optional | `auto·4–15` s | omit → auto. |
| withAudio | optional | true/false | default true. |
| seed | optional | integer | reproducibility — same seed + prompt ⇒ same clip. |

- **Limits (fal schema):** `prompt` no char cap; `referenceImages` **≤9**, `referenceVideos` **≤3**, reference audio **≤3, combined ≤15 s** — **combined ≤12 files total** (hard cap). **Multi-shot: YES** — native (hard-cut shots → panels; THE storyboard→video model).
- **Rejects**: startFrame, endFrame. **Reference AUDIO: settable via `referenceAudio`** (one mp3/wav ≤15 s — trim longer sources to the LAST ≤15 s, that's what a seam continues from; the model composes the soundscape from it — the sound-continuity anchor for clip chaining; name its role in the prompt). `referenceVideos` IS available on `operation:"new"` (continuation / prev-clip). **Extra params** (via `extra_params` — see the Notes): `bitrate_mode` (`standard`/`high`).
- **References go in DIRECTLY.** Attach character sheets, photos, plates and continuity frames AS-IS — never re-synthesise them through Seedream first (user decision). If the likeness filter rejects a render: retry the identical request 2-3×, then stop and tell the user. 📖 `references/usage/seedance.md`.
- **🔗 CHAINING clip K ≥ 2:** selective continuity frames of clip K-1 (see `previz-to-video`'s "Continuity from the previous take"), attached AS-IS like on every model. Prefer them over the previous clip as a video reference: they carry each character's exact screen position.
-

### Seedance 2.5 — Text-to-Video — `bytedance/seedance-2.5/us/text-to-video`
- **Use the US endpoint slug above** (user decision; the global `bytedance/seedance-2.5/text-to-video` is deactivated and the engine rewrites it to US). Same schema.
- text-only (no frames). Newer Seedance generation: **longer clips (up to 30 s) and now up to 1080p** (fal added 1080p to the 2.5 family; 4k remains 2.0-only).

| `video` param | Req? | Accepted values (this model) | Notes |
|---|---|---|---|
| prompt | required | string | English. |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | clamped to nearest. |
| resolution | optional | `480p·720p·1080p` | omit → 720p. **Max is 1080p** (4k is 2.0-only). |
| duration | optional | 4–30 s | omit → auto. |
| withAudio | optional | true/false | default true. |

- **Limits (fal schema):** `prompt` no char cap. **Multi-shot: YES** — native (several hard-cut shots in one clip). **No `seed`** (not in the 2.5 schema).
- **Rejects**: startFrame, endFrame, referenceImages.

### Seedance 2.5 — Image-to-Video — `bytedance/seedance-2.5/us/image-to-video`
- **Use the US endpoint slug above** (user decision; the global `bytedance/seedance-2.5/image-to-video` is deactivated and the engine rewrites it to US). Same schema.
- needs `startFrame` (optional `endFrame`). **`prompt` is REQUIRED** (the tool refuses an empty one — always describe the motion).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image | literal first frame. |
| prompt | required | string | motion description. |
| endFrame | optional | image | first+last interpolation. |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `480p·720p·1080p` | omit → 720p. **Max is 1080p** (4k is 2.0-only). |
| duration | optional | 4–30 s | omit → auto. |
| withAudio | optional | true/false | default true. |

- **Limits (fal schema):** `prompt` no char cap. **Multi-shot: YES** (native, hard-cut shots). **No `seed`** (not in the 2.5 schema).
- **Rejects**: referenceImages.

### Seedance 2.5 — Reference-to-Video — `bytedance/seedance-2.5/us/reference-to-video`
- **Use the US endpoint slug above** (user decision; the global `bytedance/seedance-2.5/reference-to-video` is deactivated and the engine rewrites it to US). Same schema.
- composes from `referenceImages`. **Much larger reference caps than 2.0.**
- **⚠️ COLOR SCIENCE: noticeably cleaner and more NEUTRAL than 2.0** — the same warm-35mm / earthy-palette cinematic prompt renders visibly FLATTER here (field-observed on identical prompts + refs). This is the model's aesthetic prior, not a prompt bug: heavier grade wording recovers only part of it. Push the grade in the prompt (palette, contrast, film stock) — 2.5 is still the model to use (user decision: always 2.5, never 2.0).
- **📦 Payload note ("payload too large" / HTTP 413):** NOT a fal schema limit — reference images travel inline (base64) in the gateway body, and this model's big caps invite stacking many multi-MB PNG references past the body limit. The runtime now auto-offloads any reference over ~600 KB to fal storage (travels as a URL — look for "heavy reference offloaded" in the log), so this should no longer occur. If it DOES occur (older engine build), the recovery is to shrink the reference files (`optimize_image`, lossless) — NEVER to drop references.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string; `@refN` binds to the images by position | |
| referenceImages | required | up to 30 images | plus `referenceVideos` and `referenceAudio` (see Limits). |
| aspectRatio | optional | `auto·21:9·16:9·4:3·1:1·3:4·9:16` | |
| resolution | optional | `480p·720p·1080p` | omit → 720p. **Max is 1080p** (4k is 2.0-only). |
| duration | optional | `auto·4–30` s | omit → auto. |
| withAudio | optional | true/false | default true. |
| seed | optional | integer | reproducibility (results may still vary slightly). |

- **Limits (fal schema):** `prompt` no char cap; `referenceImages` **≤30**, `referenceVideos` **≤10** (each 1.8–30.2 s, combined ≤30.2 s), reference audio **≤10** — **combined ≤50 files total** (hard cap). **Multi-shot: YES** — native (hard-cut shots → panels; THE storyboard→video model). `seed` honoured.
- **Rejects**: startFrame, endFrame. **Reference AUDIO: settable via `referenceAudio`** (one mp3/wav — the previous clip's extracted audio as the sound-continuity anchor for clip chaining; trim to the tail that matters, ~last 15 s; name its role in the prompt). `referenceVideos` IS available on `operation:"new"`.
- **🛡️ Reference PREP — MANDATORY for photoreal human faces** — same likeness filter as 2.0. 📖 Full guide → `references/usage/seedance.md`.

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
- **✅ Accepts REAL human faces in references directly — NO tricks.** MiniMax takes photoreal character references AS-IS: attach the raw turnarounds, no blur. Seedance also takes references as-is (no pre-processing); choose between them on craft/look/limits/fit. Real faces alone must NEVER decide the model; choose on craft/look/limits/fit.
- **Audio: NATIVE and always ON** — the model generates synced sound/dialogue itself (no `withAudio` toggle in the schema; you can't turn it off or steer it, but it DOES come out with audio — don't warn the user it's missing/uncontrollable).
- The model also accepts up to 3 reference AUDIO clips (each needs at least one image or video ref) but that is **not settable via the tool** (`video` exposes no `audioUrl`). **Rejects**: startFrame, endFrame. *Not settable:* `seed`.

### MiniMax H3 Max Multi-Angle (Image-to-Video): `minimax/h3-max/multi-angle/image-to-video`
- needs `startFrame`. **Camera-only move around ONE still image**: the scene stays frozen while the camera orbits, rises/drops and pushes in/out along explicit 3D keyframes. For turntables, orbit reveals and multi-angle views of a product, character or set from a single frame; NOT for subject/character motion.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image | the frame the camera moves around; output canvas follows it. |
| prompt | optional | string, ≤50000 chars | omit → the model's built-in "scene frozen, only the camera moves" prompt. |
| resolution | optional | `480p·768p·1080p` (`low`→480p, `medium`/`720p`→768p, `high`/`ultra`→1080p) | omit → 768p. 1080p = latent refinement of a native 768p render. |
| duration | optional | 5–15 s (integer) | omit → 5 s. |
| seed | optional | integer | reproducibility. |

- **Camera path → `extra_params.camera_trajectory`** (this model's core control): an ordered array of **2–12 keyframes**, each an object with ALL four keys:
  - `time`: 0–1, normalized position in the clip (0 = start, 1 = end).
  - `azimuth`: horizontal angle around the subject, in degrees. Signed; full turns are preserved (e.g. 720 = two orbits), max **32 turns** of total azimuth travel.
  - `elevation`: vertical angle around the subject, **−90…90** degrees.
  - `distance`: camera distance from the subject in normalized scene units, **> 0** (smaller = closer).
  - The first pose is held until its `time`; the last pose is held for the rest of the clip.
  - fal's own example (starts at `azimuth 0 · elevation 0 · distance 1`): `extra_params: { "camera_trajectory": [ {"time": 0, "azimuth": 0, "elevation": 0, "distance": 1}, {"time": 0.3, "azimuth": 45, "elevation": 15, "distance": 0.2}, {"time": 0.8, "azimuth": 90, "elevation": -90, "distance": 1} ] }`.
- **Other extra params:** `prompt_expansion_mode` (`balanced` default, ~1 s prompt rewrite; `quality` spends up to ~30 s on a richer prompt).
- **Limits (fal schema):** `prompt` **≤50000 chars**; `camera_trajectory` **2–12** keyframes (`time` 0–1, `elevation` −90…90, `distance` >0, ≤32 azimuth turns total); `duration` 5–15 s integer. **Multi-shot: NO** (one continuous camera move).
- **Rejects**: endFrame, referenceImages, referenceVideos, aspectRatio (canvas follows the image). *Not settable:* `withAudio` (not in the schema).

### MiniMax H3-Max Turbo — Text-to-Video — `minimax/h3-max-turbo/text-to-video`
- text-only (no frames). fal's **post-trained** H3 variant: stronger prompt adherence and better aesthetics than plain H3, and the **Turbo** tier is the cheap/fast one.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string | English. **≤50000 chars** — 25× H3's 2000-char ceiling, so no compressing needed here. |
| aspectRatio | optional | `21:9·16:9·4:3·1:1·3:4·9:16` | clamped to nearest; NO `auto` — omit → 16:9. |
| resolution | optional | `480p` · `768p` | native tiers. `720p`/`1080p`/`2k`/`4k` all fold to **768P** (the ceiling); only an explicit `low`/`480p` gets the cheap tier. Omit → 768P. |
| duration | optional | 5–15 s (integer) | omit → 5s. |
| seed | optional | integer | ✅ **supported** — unlike plain H3, which has no seed at all. |

- **NOT 2K.** The H3-Max family renders natively at 480P/768P; H3's fixed `2K` does not exist here. If the user needs 2K, that's plain `minimax/h3/*`.
- The engine always sends `prompt_expansion_mode: "balanced"` (the schema requires the field). The `quality` mode spends ~30 s rewriting your prompt — **wrong for us**: our prompts are already authored shot-by-shot, so a model rewrite can only drift off the storyboard.
- **Audio:** no `withAudio` toggle in the schema (same as the H3 base) — expect the family's native synced audio; you can't steer it here.
- **Rejects**: startFrame, endFrame, referenceImages, referenceVideos.

### MiniMax H3-Max Turbo — Image-to-Video — `minimax/h3-max-turbo/image-to-video`
- needs `startFrame` (optional `endFrame`).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| startFrame | required | image | literal first frame; output dims follow it. |
| endFrame | optional | image | first→last keyframe interpolation. |
| prompt | required | string ≤50000 chars | motion description — REQUIRED on this slug. |
| resolution | optional | `480p` · `768p` | as above; omit → 768P. |
| duration | optional | 5–15 s (integer) | omit → 5s. |
| seed | optional | integer | ✅ supported. |

- No `aspectRatio` (output follows the image — frame the photo first). **Rejects**: referenceImages, referenceVideos.

### MiniMax H3-Max — Reference-to-Video — `minimax/h3-max/reference-to-video`
- composes from `referenceImages` (+ `referenceVideos`). The **non-Turbo** H3-Max tier: better aesthetics, pricier per second.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤50000 chars; refs cited as `Image N` / `Video N` / `Audio N` (the engine rewrites your `@refN` for you) | |
| referenceImages | optional | up to 9 images | |
| referenceVideos | optional | up to 3 clips (2–15 s each, combined ≤ 15 s) | continuation / composition refs. |
| aspectRatio | optional | `adaptive·21:9·16:9·4:3·1:1·3:4·9:16` | omit → adaptive. |
| resolution | optional | `480p` · `768p` | omit → 768P. |
| duration | optional | 5–15 s (integer) | omit → 5s. |
| seed | optional | integer | ✅ supported. |

- **Cross-modal cap: 12 FILES TOTAL** (images + videos + audio), on top of the per-modality 9 / 3 / 3. Over that, the engine trims audio first, then videos, then images — so keep the set under 12 or you lose refs silently.
- **Reference billing is separate**: the first ~4096 reference tokens are free (≈4 images at 1024×1024, or ONE at 2048×2048), then each extra 1K tokens is charged. Downscale refs you don't need at full size.
- **Rejects**: startFrame, endFrame.

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

### Gemini Omni Flash 1.1 — Text-to-Video — `google/gemini-omni-flash/v1.1/text-to-video`
- text-only. The v1.1 revision: same minimal, prose-driven model, **plus a real `resolution` knob that reaches 4k**.
- 📖 **Usage guide → `references/usage/gemini-omni.md`** — READ before composing the prompt (prompting technique, audio).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤20000 chars | all cinematography/pacing/audio direction lives in the prose. |
| aspectRatio | optional | `16:9·9:16` only | clamped to nearest orientation; omit → 16:9. |
| duration | optional | 3–10 s (clamped) | omit → 8s. **Note the window: 3–10, not the MiniMax 5–15.** |
| resolution | optional | `360p·720p·1080p·4k` | NEW in v1.1. Omit → fal's 720p default (we don't send the field at all, so you're never billed for an upgrade you didn't ask for). `2k` folds DOWN to 1080p. |

- **Rejects**: startFrame, endFrame, referenceImages, referenceVideos, seed, withAudio.

### Gemini Omni Flash 1.1 — Image-to-Video — `google/gemini-omni-flash/v1.1/image-to-video`
- needs `startFrame` + `prompt`. Two things v1 didn't have: an **`endFrame`** and **`resolution`**.
- 📖 **Usage guide → `references/usage/gemini-omni.md`**.

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤20000 chars | how the first image animates (or interpolates into the end image). |
| startFrame | required | image | literal first frame. |
| endFrame | optional | image | ✅ **NEW in v1.1** — with both frames set the model INTERPOLATES between them in order. v1 had no end frame at all. |
| aspectRatio | optional | `16:9·9:16` only | omit → 16:9. |
| duration | optional | 3–10 s (clamped) | omit → 8s. |
| resolution | optional | `360p·720p·1080p·4k` | NEW in v1.1; omit → 720p default. |

- **Rejects**: referenceImages, referenceVideos, seed, withAudio.

### Gemini Omni Flash 1.1 — Reference-to-Video — `google/gemini-omni-flash/v1.1/reference-to-video`
- composes from `referenceImages` (≤10) and — **new in v1.1** — `referenceVideos` (≤3).
- 📖 **Usage guide → `references/usage/gemini-omni.md`** — READ before composing the prompt (how refs bind, prompting technique, audio).

| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | string ≤20000 chars; write `@refN` and the engine rewrites it | see the ref-binding note below. |
| referenceImages | optional | up to 10 images | |
| referenceVideos | optional | up to 3 clips, **each ≤3 s** | ⚠ hard 3-second cap PER CLIP — trim before attaching or fal rejects it. |
| aspectRatio | optional | `16:9·9:16` only | omit → 16:9. |
| duration | optional | 3–10 s (clamped) | omit → 8s. |
| resolution | optional | `360p·720p·1080p·4k` | NEW in v1.1; omit → 720p default. |

- **Ref binding — write `@ref1`, `@ref2`, … as usual.** This model's native dialect is `<IMAGE_REF_n>` / `<VIDEO_REF_n>`, which is **ZERO-indexed with a separate counter per modality** (2 images + 1 video ⇒ `@ref1 @ref2 @ref3` becomes `<IMAGE_REF_0> <IMAGE_REF_1> <VIDEO_REF_0>`). The engine does that translation for you AFTER applying the caps, so the indices always match what actually ships. Do NOT hand-write the tags — unlike v1, where you had to.
- **Rejects**: startFrame, endFrame, seed, withAudio.

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

### Gemini Omni Flash 1.1 — Video Edit — `google/gemini-omni-flash/v1.1/edit`  *(operation `"edit"`)*
The v1.1 editor: identical to the v1 one plus a `resolution` knob.
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"edit"` | |
| sourceVideo | required | path/@mention to the clip | |
| prompt | required | edit instruction ≤20000 chars | tip: append "Keep everything else the same." |
| resolution | optional | `360p·720p·1080p·4k` | NEW in v1.1. Omit → 720p; `2k` folds down to 1080p. |
- Length still follows the source; only the resolution is now yours to set. Unavailable in EEA/CH/UK.
- 📖 **Usage guide → `references/usage/gemini-omni.md`**.

### Kling o3 4K — Video-to-Video Reference / Edit — `fal-ai/kling-video/o3/4k/video-to-video/reference` · `…/edit`  *(operation `"edit"`)*
The 4K tier of the Kling o3 v2v pair. Same fields as the standard/pro tiers — what the tier buys you is a **bigger input envelope**: source clip up to **3840 px** and **15 s** (standard caps at 2160 px / 10 s), ≤200 MB, 24–60 fps, .mp4/.mov only.
| `video` param | Req? | Accepted values | Notes |
|---|---|---|---|
| operation | required | `"edit"` | |
| sourceVideo | required | .mp4/.mov, 3–15 s, 720–3840 px, ≤200 MB | |
| prompt | required | edit instruction ≤2500 chars | **much tighter than Gemini's 20000** — keep it short. |
| referenceImages | optional | up to 4 images, ≤10 MB and ≥300 px each | style / character refs. |
| aspectRatio | optional | `16:9·9:16·1:1` — **`/reference` ONLY** | anything else → auto (matches the source). |
| duration | optional | 3–15 s — **`/reference` ONLY** | |
- ⚠ **The two routes are NOT symmetric**: `/edit` rejects `aspectRatio` and `duration` (framing and length follow the source); `/reference` accepts both.
- On `/edit`, `@refN` binds POSITIONALLY to `@ImageN` in the prompt (the engine rewrites it). On `/reference`, the images are GLOBAL style guidance and are not bound positionally.
- Audio from the source is **opt-in** (dropped by default, like every model here).

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
- **Duration & resolution are per-model** — Veo `4s/6s/8s`, extend fixed 7s, Kling up to 15s, Seedance 2.5 up to 30s. **4k is reached by Veo** (Seedance 2.5 tops at 1080p; 2.0 is not used) — check each model's row. Most models emit 1080p when you omit resolution (Seedance t2v/i2v → 1080p, ref-to-video → 720p).
- **`seed` IS a `video` parameter** (on `operation:"new"`) — honoured by Seedance / Veo / WAN, ignored by Kling. **`referenceVideos` IS a `video` parameter on `operation:"new"`** (continuation / prev-clip carry-over; honoured by reference-to-video models like Seedance). **`characterOrientation`, `keepOriginalSound`, `audioUrl` are NOT `video` parameters** — the agent cannot set them, even where a model supports them.
- **`extra_params` — the model-specific escape hatch.** For a per-model knob this tool does NOT expose as a first-class field (e.g. Seedance `bitrate_mode`), pass it inside `extra_params` as an object whose KEY is the EXACT provider field name (snake_case, as in the model's API) and value as the API expects — e.g. `extra_params: { "bitrate_mode": "..." }`. Only send params listed in the model's own row above; the keys travel verbatim to the provider (unknown ones are ignored). `extra_params` NEVER overrides a first-class param (duration/resolution/aspectRatio/…) — set those directly. Same mechanism exists on `generate_image` and `generate_audio`.
