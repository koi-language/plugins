# Image models — per-model parameters (in `generate_image` tool terms)

Only models **enabled in the BRAXIL backend** are listed, and each table uses the **actual MCP tool parameters the agent can set** — NOT raw fal fields. If a param isn't a tool parameter, the agent can't set it, so it's not in the table (see "Not settable via the tool" per model).

`generate_image` parameters: `model` **(required),** `prompt`**,** `referenceImages`**,** `aspectRatio`**,** `resolution`**,** `width`**,** `height`**,** `quality`**,** `outputFormat`**,** `cameraAngles`**,** `n`**,** `seed` (+ `saveTo`, `summary`, `metadata`). `seed` is honoured only by models whose card lists it; the rest accept and ignore it. `width`+`height` (both together) request an **exact pixel canvas** instead of the semantic `resolution` label — honoured ONLY by models that accept explicit dimensions (the **Seedream family** and **Qwen-Image-Edit**); every other model ignores them and falls back to `aspectRatio`/`resolution`. Mind each model's **area cap** (a per-model total-pixel ceiling — e.g. Seedream v5 Pro/Lite edit top out at 2048×2048 ≈ 4.2 MP, so an exact canvas must stay within it; true 4K is not reachable on those edit endpoints). There is NO `maskImage`, `safetyTolerance`, `loras` on this tool.

Background-removal, outpaint and upscale are **separate tools** with **no** `model` **pick** (auto-routed) — see the last section.

---

## Models you pick with the `model` param of `generate_image`

### GPT Image 2 — `openai/gpt-image-2`  *(text-to-image)*

- create from a prompt · no references.


| `generate_image` param | Req?     | Accepted values (this model)                                  | Notes                                                                             |
| ---------------------- | -------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| prompt                 | required | 2–32000 chars                                                 | English.                                                                          |
| aspectRatio            | optional | any `W:H` (converted to pixels)                               | edges multiple of 16, max edge 3840, ratio ≤3:1. Omit → `auto`.                   |
| resolution             | optional | `low·medium·high·ultra` → long edge 1280 / 1920 / 2560 / 3840 | default high. `ultra` = 4K long edge.                                             |
| quality                | optional | `low·medium·high·auto`                                        | sampling effort (auto→high). **This is the only model that reads** `quality`**.** |
| outputFormat           | optional | `png·jpeg·webp`                                               | default png.                                                                      |
| n                      | optional | 1–4                                                           | default 1.                                                                        |


- **Rejects**: referenceImages, cameraAngles.

### Nano Banana 2 — `fal-ai/nano-banana-2`  *(text-to-image)*

- Google Nano-Banana 2 · no references.


| `generate_image` param | Req?     | Accepted values                                                   | Notes                                   |
| ---------------------- | -------- | ----------------------------------------------------------------- | --------------------------------------- |
| prompt                 | required | string                                                            | English.                                |
| aspectRatio            | optional | `auto·21:9·16:9·3:2·4:3·5:4·1:1·4:5·3:4·2:3·9:16·4:1·1:4·8:1·1:8` | clamped to closest.                     |
| resolution             | optional | `low/medium`→1K · `high`→2K · `ultra`→4K                          | default 1K. Set `high`/`ultra` for ≥2K. |
| outputFormat           | optional | `png·jpeg·webp`                                                   | default png.                            |
| n                      | optional | 1–4                                                               |                                         |


- **Rejects**: referenceImages, cameraAngles, quality. `safetyTolerance` is not a tool param. `**seed` — honoured** (reproducibility: same seed + prompt ⇒ same image).

### Nano Banana Pro — `fal-ai/nano-banana-pro`  *(text-to-image)*

- higher-fidelity Nano-Banana · no references.


| `generate_image` param | Req?     | Accepted values                                   | Notes                                             |
| ---------------------- | -------- | ------------------------------------------------- | ------------------------------------------------- |
| prompt                 | required | string                                            | English.                                          |
| aspectRatio            | optional | `auto·21:9·16:9·3:2·4:3·5:4·1:1·4:5·3:4·2:3·9:16` | narrower than nano-banana-2 (no 4:1/1:4/8:1/1:8). |
| resolution             | optional | `low/medium`→1K · `high`→2K · `ultra`→4K          | default 1K.                                       |
| outputFormat           | optional | `png·jpeg·webp`                                   | default png.                                      |
| n                      | optional | 1–4                                               |                                                   |


- **Rejects**: referenceImages, cameraAngles, quality. `**seed` — honoured** (reproducibility).

### Seedream 5 Lite — `fal-ai/bytedance/seedream/v5/lite/text-to-image`  *(text-to-image)*

- cheap/fast Seedream 5 Lite · no references.


| `generate_image` param | Req?     | Accepted values                                                      | Notes         |
| ---------------------- | -------- | -------------------------------------------------------------------- | ------------- |
| prompt                 | required | string                                                               | English.      |
| aspectRatio            | optional | any `W:H` (→ pixel size)                                             | default 1:1.  |
| resolution             | optional | `low`→768 · `medium`→1024 · `high`→1536 · `ultra`→2048 (max side px) | default high. |
| n                      | optional | 1–6                                                                  | up to 6.      |


- **Rejects**: referenceImages, cameraAngles, quality, outputFormat (provider returns PNG). `seed` accepted but IGNORED by this model.

### Seedream 5 Pro — `bytedance/seedream/v5/pro/text-to-image`  *(text-to-image)*

- higher-fidelity Seedream 5 Pro · no references (slug has NO `fal-ai/` prefix).


| `generate_image` param | Req?     | Accepted values                                                      | Notes            |
| ---------------------- | -------- | -------------------------------------------------------------------- | ---------------- |
| prompt                 | required | string                                                               | English.         |
| aspectRatio            | optional | any `W:H` (→ pixel size, per-side ≤14142)                           | omit → model ~2K. |
| resolution             | optional | `low`→768 · `medium`→1024 · `high`→1536 · `ultra`→2048 (max side px) | default high.    |
| n                      | optional | 1–6                                                                  | up to 6.         |


- **Rejects**: referenceImages, cameraAngles, quality, outputFormat (forced png). `seed` is NOT a field on this model.

### Krea 2 Turbo — `fal-ai/krea-2/turbo`  *(text-to-image)*

- Krea 2 Turbo · no references.


| `generate_image` param | Req?     | Accepted values                                                      | Notes                                                                                      |
| ---------------------- | -------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| prompt                 | required | 1–5000 chars                                                         | English.                                                                                   |
| aspectRatio            | optional | any `W:H` (→ pixel size)                                             | default 1:1.                                                                               |
| resolution             | optional | `low`→768 · `medium`→1024 · `high`→1536 · `ultra`→2048 (max side px) | default high, ≤2048/side.                                                                  |
| outputFormat           | optional | `png·jpeg` (no webp; webp→png)                                       | default png.                                                                               |
| n                      | optional | 1–4                                                                  |                                                                                            |
| seed                   | optional | integer                                                              | reproducibility — same seed + prompt ⇒ same image (honoured, like the Nano-Banana models). |


- **Rejects**: referenceImages, cameraAngles, quality.

### MAI Image 2.5 Pro — `microsoft/mai-image-2.5-pro`  *(text-to-image)*

- Microsoft MAI · create from a prompt · no references.


| `generate_image` param | Req?     | Accepted values                              | Notes                                              |
| ---------------------- | -------- | -------------------------------------------- | -------------------------------------------------- |
| prompt                 | required | string                                       | English.                                           |
| aspectRatio            | optional | `auto·1:1·4:3·3:4·16:9·9:16·3:2·2:3`         | fixed enum, clamped to closest. Omit → `auto` (the model decides from the prompt). |
| outputFormat           | optional | `jpeg·png·webp`                              | default png.                                       |
| n                      | optional | default 1                                    | the schema publishes no max.                       |


- **Rejects / ignored**: referenceImages (use the /edit slug), `seed` (accepted, ignored — no reproducibility), `resolution` / `width`+`height` / `quality` (NO size knobs at all: the model sizes output from the aspect ratio alone — for an exact pixel size follow the "Exact pixel size requested" rule with aspectRatio only, then downscale locally), cameraAngles.

### GPT Image 2 — Edit — `openai/gpt-image-2/edit`  *(image-to-image)*

- edit reference images · **needs** `referenceImages`.


| `generate_image` param | Req?     | Accepted values                                         | Notes                          |
| ---------------------- | -------- | ------------------------------------------------------- | ------------------------------ |
| prompt                 | required | 2–32000 chars                                           | edit instructions.             |
| referenceImages        | required | 1–16 images (each ≤25 MB)                               |                                |
| aspectRatio            | optional | any `W:H` (→ pixels); omit → inferred from ref[0]       | same pixel limits as generate. |
| resolution             | optional | `low/medium/high/ultra` → 1280/1920/2560/3840 long edge |                                |
| quality                | optional | `low·medium·high·auto`                                  | only this family reads it.     |
| outputFormat           | optional | `png·jpeg·webp`                                         |                                |
| n                      | optional | 1–4                                                     |                                |


- *Not settable via the tool:* `maskImage` (masked inpaint is NOT exposed by `generate_image`). `seed` accepted but IGNORED.

### Nano Banana 2 — Edit — `fal-ai/nano-banana-2/edit`  *(image-to-image)*

- edit · **needs** `referenceImages`.


| `generate_image` param | Req?     | Accepted values                                                   | Notes              |
| ---------------------- | -------- | ----------------------------------------------------------------- | ------------------ |
| prompt                 | required | string                                                            | edit instructions. |
| referenceImages        | required | 1–14 images                                                       |                    |
| aspectRatio            | optional | `auto·21:9·16:9·3:2·4:3·5:4·1:1·4:5·3:4·2:3·9:16·4:1·1:4·8:1·1:8` |                    |
| resolution             | optional | `low/medium`→1K · `high`→2K · `ultra`→4K                          |                    |
| outputFormat           | optional | `png·jpeg·webp`                                                   |                    |
| n                      | optional | 1–4                                                               |                    |


- **Rejects**: cameraAngles, quality. `safetyTolerance` is not a tool param. `**seed` — honoured** (reproducibility).

### ~~Nan~~o Banana Pro — Edit — `fal-ai/nano-banana-pro/edit`  *(image-to-image / upscaling-capable)*

- edit · **needs** `referenceImages`.


| `generate_image` param | Req?     | Accepted values                                   | Notes              |
| ---------------------- | -------- | ------------------------------------------------- | ------------------ |
| prompt                 | required | string                                            | edit instructions. |
| referenceImages        | required | 1–14 images                                       |                    |
| aspectRatio            | optional | `auto·21:9·16:9·3:2·4:3·5:4·1:1·4:5·3:4·2:3·9:16` |                    |
| resolution             | optional | `low/medium`→1K · `high`→2K · `ultra`→4K          |                    |
| outputFormat           | optional | `png·jpeg·webp`                                   |                    |
| n                      | optional | 1–4                                               |                    |


- **Rejects**: cameraAngles, quality. `**seed` — honoured** (reproducibility).

### Seedream 5 Lite — Edit — `fal-ai/bytedance/seedream/v5/lite/edit`  *(image-to-image)*

- edit · **needs** `referenceImages`.


| `generate_image` param | Req?     | Accepted values                                        | Notes              |
| ---------------------- | -------- | ------------------------------------------------------ | ------------------ |
| prompt                 | required | string                                                 | edit instructions. |
| referenceImages        | required | 1–10 images                                            |                    |
| aspectRatio            | optional | any `W:H` (→ pixel size)                               |                    |
| resolution             | optional | `low`→768 · `medium`→1024 · `high`→1536 · `ultra`→2048 |                    |
| n                      | optional | 1–6                                                    |                    |


- **Rejects**: cameraAngles, quality, outputFormat. `seed` accepted but IGNORED by this model.

### Seedream 5 Pro — Edit — `bytedance/seedream/v5/pro/edit`  *(image-to-image)*

- edit · **needs** `referenceImages`. The higher-fidelity Pro sibling of the Lite edit above (slug has NO `fal-ai/` prefix).


| `generate_image` param | Req?     | Accepted values                                        | Notes              |
| ---------------------- | -------- | ------------------------------------------------------ | ------------------ |
| prompt                 | required | string                                                 | edit instructions. |
| referenceImages        | required | 1–10 images (if >10, only the LAST 10 are used)        |                    |
| aspectRatio            | optional | any `W:H` (→ pixel size, per-side ≤14142)             | omit → model keeps ~2K. |
| resolution             | optional | `low`→768 · `medium`→1024 · `high`→1536 · `ultra`→2048 |                    |
| width + height         | optional | exact px canvas; cap is **total AREA ≤ 4.2 MP** (= 2048²), aspect 1:16–16:1 | both together. The limit is area, NOT per-side: one side MAY exceed 2048 if the other shrinks (`4096×1024` ✓, `2896×1448` ✓, even `8192×512` ✓). **True 4K does NOT fit** (`3840×2160`≈8.3 MP doubles the cap) — for 4K, edit here then upscale, or use a 4K text-to-image model. min area 1024². |
| n                      | optional | 1–6                                                    |                    |


- **Rejects**: cameraAngles, quality, outputFormat (forced png). `seed` is NOT a field on this model.

### MAI Image 2.5 Pro — Edit — `microsoft/mai-image-2.5-pro/edit`  *(image-to-image)*

- Microsoft MAI · instruction edit of ONE image · **needs** `referenceImages` **(exactly 1)**.


| `generate_image` param | Req?     | Accepted values                              | Notes                                              |
| ---------------------- | -------- | -------------------------------------------- | -------------------------------------------------- |
| prompt                 | required | string                                       | the edit instruction, English.                     |
| referenceImages        | required | exactly 1 image                              | SINGLE-reference model — it cannot compose from several refs (logo+mug etc. → use a multi-ref editor like Seedream/Nano-Banana edit). |
| aspectRatio            | optional | `auto·1:1·4:3·3:4·16:9·9:16·3:2·2:3`         | default `auto` = match the input. Setting another value REFRAMES the output. |
| outputFormat           | optional | `jpeg·png·webp`                              | default png.                                       |
| n                      | optional | default 1                                    | the schema publishes no max.                       |


- **Rejects / ignored**: `seed` (no reproducibility), `resolution` / `width`+`height` / `quality` (no size knobs — output size follows the input/aspect), cameraAngles, maskImage.

### Qwen Image Edit 2511 — Multiple Angles — `fal-ai/qwen-image-edit-2511-multiple-angles`  *(camera re-angle)*

- re-render a subject from a new camera angle · **needs** `referenceImages` **(exactly 1) +** `cameraAngles`.


| `generate_image` param | Req?     | Accepted values                                              | Notes                                                                                                                        |
| ---------------------- | -------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| prompt                 | required | string                                                       | **contextual only** — the sliders drive it, not the prose.                                                                   |
| referenceImages        | required | exactly 1 image                                              |                                                                                                                              |
| cameraAngles           | required | `{ horizontal 0–360, vertical −30–90, zoom 0–10 }` (≥1 axis) | 0=front/90=right/180=back/270=left; −30=low-angle/90=bird's-eye; 0=wide/10=close-up. **Only this model reads cameraAngles.** |
| n                      | optional | 1–4                                                          |                                                                                                                              |


- **Rejects / forced**: aspectRatio, resolution, outputFormat (hardcoded png), quality. Throws if no camera axis is set.

### Ideogram Object Removal — `fal-ai/ideogram/object-removal`  *(masked object removal)*

- erase an object from a photo and re-synthesise the hole from context · **needs** `referenceImages` **(exactly 2: [source, mask])**.


| `generate_image` param | Req?     | Accepted values                        | Notes                                                                                                                                     |
| ---------------------- | -------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| referenceImages        | required | exactly 2: `[source, mask]`            | **refs[0] = the photo** (≤10 MB). **refs[1] = a black-and-white MASK at the SAME dimensions: WHITE = remove, BLACK = keep.** Use aliases (`source`, `mask`). |


- **Rejects / ignored**: prompt (the model takes none — removal is mask-driven), aspectRatio, resolution, n (always 1 output), seed, outputFormat, width/height, quality.
- **Where does the mask come from?** The agent BUILDS it with any edit model first — e.g. GPT Image 2 Edit with the source as reference and a prompt like *"Output a black-and-white mask of this image at the exact same dimensions: the `<object>` as a solid WHITE silhouette, everything else solid BLACK. No gray, no anti-aliasing halo, no other content."* — then passes `[source, that mask]` here. Make the white region slightly GENEROUS (cover shadows/reflections of the object) for clean removal.
- Prefer this over a prompted edit ("remove the X") when the edit model keeps regenerating the whole image or drifting the scene: this endpoint touches ONLY the white region and leaves every other pixel byte-identical.

---

## Image operations handled by DEDICATED tools (no `model` pick — auto-routed)

These do NOT go through `generate_image`; you don't choose a model.

- **Remove background** → `background_removal({ image })` → serves `fal-ai/bria/background/remove`. Returns a transparent PNG. No other params.
- **Outpaint / extend the canvas** → `outpaint_image({ image, padTop?, padBottom?, padLeft?, padRight?, prompt? })` → serves `fal-ai/flux-2-pro/outpaint`. `prompt` describes only the NEW margins; per-side pad in pixels.
- **Upscale** → `upscale_image({ image, upscaleFactor 1–4 (default 2), prompt?, creativity 0–1?, faceEnhancement?, outputFormat png/webp/jpeg })`. `prompt`/`creativity` only affect generative upscalers.

---

## Notes

- `quality` is consumed ONLY by GPT Image 2 (/edit); every other model ignores it.
- `cameraAngles` is consumed ONLY by Qwen Multiple-Angles.
- `seed` **IS a parameter of** `generate_image`, honoured by **Krea 2 Turbo and the Nano-Banana 2 / Pro models (base + edit)**; **GPT Image 2, Seedream 5 Lite and the MAI Image 2.5 Pro family** accept and ignore it. `maskImage`**,** `safetyTolerance`**,** `loras` **are NOT parameters** — the agent cannot set them here.
- `width` + `height` (an exact px canvas, both together) are consumed ONLY by the **Seedream family** and **Qwen-Image-Edit**; every other model ignores them and uses `aspectRatio`/`resolution`. Always stay under the model's area cap (Seedream edit = 2048² ≈ 4.2 MP).
- **Resolution matters**: Nano-Banana caps low unless you send `high`/`ultra`.

