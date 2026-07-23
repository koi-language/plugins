---
name: image-generator
description: MANDATORY before ANY image generation or editing — activate this skill the moment a request involves creating, generating, drawing, rendering, editing, inpainting, outpainting/reframing, upscaling, removing the background of, or camera-rotating an image, i.e. before EVERY `generate_image` call. It is the required model+parameter contract: `model` is a mandatory parameter (there is NO auto-router) and this skill tells you which model to pick by category and exactly which parameters each supported model accepts or rejects. If you are about to generate/edit an image and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): "generate/create/make/draw/render an image", "genera/crea/haz/dibuja una imagen o foto", "edit/retouch this photo", "edita/retoca la foto", "inpaint", "outpaint", "reframe", "upscale", "remove/quita el fondo", "logo", "poster", "banner", "mockup", or any mention of an image model (Nano-Banana, GPT Image, Seedream, Krea, Qwen, Bria).
---

# Image models

Runbook for producing images through BRAXIL's `generate_image` tool. **Do not reimplement image API code** — no `generate.py`, no SDK wrapper, no direct fal calls. **You choose the model** (the `model` param is required — there is no auto-router): identify the operation → pick a slug from the matching category → send only the parameters that model accepts.

**Where to find what — it's already in your context, don't go searching:**
- **Categories & Labels of every model → the `generate_image` tool's OWN description (the "Catalog" table).** It is already in your context. Read it RIGHT THERE to pick a model. **Never grep files, `references/`, or the backend for models / categories / labels** — they live in the tool description, immediately available.
- **Per-model PARAMETERS → `references/models.md`** (what each model accepts). Read a model's card before setting a non-obvious param (`cameraAngles`, `quality`).

The gateway hard-errors on an unknown slug and silently drops fields a model doesn't understand.

## The tool: `generate_image`

**The exact accepted values for every parameter DEPEND ON THE MODEL you pick.** Before calling, read your chosen model's parameter table in `references/models.md` and pass ONLY what it lists — its exact aspect-ratio enum (or "any `W:H`"), resolution labels, `n` max, output formats, and whether it supports `cameraAngles`. The bullets below only say what each param MEANS:

- `prompt` (required) — **always English** (models degrade on non-English captions). The ONLY exception is literal on-image text (a sign, a label, UI copy, speech-bubble dialogue): keep that verbatim in the user's language, wrapped in quotes inside the otherwise-English prompt.
- `aspectRatio` — the frame ratio. **Accepted values are per-model** — some have a fixed enum (e.g. `auto·16:9·1:1·9:16·…`), others accept any `W:H`. See the model's table; omit to let it default.
- `resolution` — output size as a **semantic label**. **Per-model** — some use labels (`1K/2K/4K`), others size buckets (`low/medium/high/ultra`). A few cap the render unless you pass a high value — the table lists the default and the ceiling.
- `width` + `height` — an **exact pixel canvas** (both required together), used instead of the `resolution` label when you need a precise size. **Only the Seedream family and Qwen-Image-Edit honour them**; every other model ignores them and uses `aspectRatio`/`resolution`. Each model caps the **total AREA** (not per-side): Seedream edit tops at ~4.2 MP (= 2048²), so one side may exceed 2048 if the other shrinks (`4096×1024` ✓), but true 4K (~8.3 MP) does not fit — edit then upscale, or use a 4K-capable text-to-image model. Nothing is clamped client-side; the provider enforces its own area/aspect limits. Video has no width/height (its models size by `resolution` tier + `aspectRatio`). **If the user asks for an exact pixel size on a model WITHOUT `width`/`height`, do NOT render at the default and shrink — approximate it with the closest `resolution` label + closest `aspectRatio`; see the "Exact pixel size requested" section below.**
- `quality` — sampling effort (`low | medium | high | auto`), decoupled from pixel count. **Only some models consume it** (their table lists it); most ignore it. `low` for thumbnails, `high` for finals.
- `n` — number of images. **Max is per-model** (see the table — commonly 4, some 6).
- `seed` — reproducibility seed: same seed + same prompt ⇒ the same image **on models that honour it** (Krea 2 Turbo and the Nano-Banana 2 / Pro models; GPT Image 2 and Seedream Lite ignore it). Omit for a fresh random result.
- `referenceImages` — file paths / attachment IDs (`att-N`) / `@mention` handles, OR objects `{ alias, path }`. **Prefer aliased objects** and refer to them by alias in the prompt ("paint the `logo` onto the `mug`"). **Only edit / outpaint / bg-remove models accept refs, and the max count is per-model** — text-to-image models reject them.
- `outputFormat` — **per-model** (most do `png/jpeg/webp`; some only `png/jpeg` — the table lists it). Default png.
- `cameraAngles` — `{ horizontal?, vertical?, zoom? }` — ONLY for a different camera angle of an existing image; consumed only by a camera-rotation model (its card lists `cameraAngles` support). At least one axis; omitted axes stay at the model default.
- `saveTo` — optional COPY destination (dir or full `.png/.jpg/.webp` path). The original always stays in `~/.koi/images` and comes back as `images[].savedTo` — **use that for downstream chaining, never fabricate a path**; your copy is `images[].exportedTo`.
- `summary` — one-line "what was this for" for the creations ledger.
- `model` — **REQUIRED. YOU pick the exact slug.** There is no auto-router — omitting it (or passing `"auto"`) makes the tool error out. Read the **Catalog table** in the tool's own description (or `references/models.md`) and pick a slug whose **Categories** column contains the bucket for your operation (see "Categories" below). The gateway hard-errors on an unknown slug, so don't invent one.

Returns `{ success, provider, model, images: [{ url?, b64?, savedTo?, exportedTo? }] }`.

## Exact pixel size requested but the model has NO `width`/`height` — MANDATORY rule

When the user asks for a **concrete pixel size** (e.g. "1024×1024", "512px", "a 1080p", "4K", "un icono de 1024"):

1. **If the chosen model accepts `width`+`height`** (ONLY the Seedream family and Qwen-Image-Edit) → set them to the exact size. Done.
2. **If it does NOT** (GPT Image 2, Nano-Banana, Krea, Bria… — every other model) → you **CANNOT** pass an exact canvas, so you MUST APPROXIMATE it from the two labels the model *does* accept — **do NOT just render at the default size and shrink it**:
   - **`resolution`** → pick the label whose pixel size (in that model's card — e.g. GPT Image 2: `low`=1280, `medium`=1920, `high`=2560, `ultra`=3840 long edge) is **CLOSEST to the requested size**. For 1024 that is `low` (1280), NOT the default `high` (2560).
   - **`aspectRatio`** → pick the ratio **CLOSEST to the requested one** (1024×1024 → `1:1`; 1920×1080 → `16:9`; etc.). If the model takes any `W:H`, pass the exact ratio.
   - **Only then**, if the user needs the pixels to be *exact*, resize the returned file DOWN to that size locally (a lossless downscale of the closest render) — never upscale past what the model produced, and never claim the model "renders at a fixed internal resolution": it doesn't, you chose the closest label.

Same token cost whichever label you pick (the price is per call, independent of size), so **always choose the closest label rather than the default** — a 1024 target rendered from `low` (1280) is far better than from `high` (2560).

## Multiple images at once — use `batch`, never many separate calls

When you need SEVERAL images in one go (regenerating a set of storyboard panels, a variation grid, a few edits), pass them in the **`batch` array of a SINGLE `generate_image` call** — do **NOT** emit one `generate_image` tool call per image. Tool calls run **serially**, so N separate calls take N× as long; one batched call runs them **in parallel** and returns together.

- Each `batch` entry is an object with the same fields as a single call (`prompt`, `model`, `referenceImages`, `aspectRatio`, `resolution`, `quality`, `outputFormat`, `seed`, `metadata`, `summary`, `n`).
- Any field you set at the **top level** is the shared default for entries that omit it — set a common `model` / `aspectRatio` once and give each entry just its own `prompt`.
- Returns `{ results: [ …one result per entry, in order… ] }`; each entry carries the saved path(s) in its `artifacts[]` (and the raw result under `result`). A per-entry `ok:false` means only that image failed — the others still ran.

Use a single call for a single image (the top-level fields). Reach for `batch` the moment there is more than one.

## Categories — you pick a `generate_image` model for two of them

The `generate_image` `model` param covers **generation** and **editing** only. Pick a slug **whose category matches what you are doing, and NEVER one that lacks it**:

| Category | Use it for |
|---|---|
| `image_generation` | text-to-image — a fresh image from a prompt (no `referenceImages`) |
| `image_editing` | image-to-image / instruction edit / camera re-angle — changing an existing image (`referenceImages` present) |

**Outpaint, upscale and background-removal are NOT `generate_image`** — they are **dedicated tools with no model pick** (auto-routed). Masked inpaint is not exposed by the MCP tools at all.

## Routing: which tool + (for generate_image) which model

| Operation | Tool | Send |
|---|---|---|
| Text-to-image | `generate_image` (`model` from `image_generation`) | `prompt` (+aspectRatio/resolution/n) |
| Edit / image-to-image | `generate_image` (`model` from `image_editing`) | `prompt` + `referenceImages` |
| Camera angle of an image | `generate_image` (`model` = `fal-ai/qwen-image-edit-2511-multiple-angles`) | `referenceImages` (1) + `cameraAngles` |
| Outpaint / extend the canvas | `outpaint_image` — **no model** | `image` + `padTop/padBottom/padLeft/padRight` (+`prompt`) |
| Upscale | `upscale_image` — **no model** | `image` (+`upscaleFactor`/`prompt`/`creativity`/`faceEnhancement`) |
| Remove background | `background_removal` — **no model** | `image` |
| Inpaint a masked region | — | not available via the MCP tools |

## Choosing within a category

**DEFAULT MODEL — always GPT Image 2 unless a concrete reason below forces another.** It is the standard pick for both categories:
- **Text-to-image** → `openai/gpt-image-2`.
- **Edit / image-to-image** → `openai/gpt-image-2/edit`.

Reach for GPT Image 2 first, every time. Do NOT switch to Nano-Banana, Seedream, Krea, Qwen, Bria or any other model just because it "might look better" or "is newer" — that is exactly the wrong reason. Only deviate when ONE of these is true:

1. **The operation is impossible on GPT Image 2.** Camera-rotation (`fal-ai/qwen-image-edit-2511-multiple-angles`), an exact-pixel canvas (Seedream family / Qwen-Image-Edit accept explicit `width`+`height`), or the separate no-model tools (outpaint, upscale, background-removal). If GPT Image 2 cannot physically do it, use the one model that can.
2. **The user explicitly names another model** ("use Nano-Banana", "hazla con Seedream"). Honour the request.
3. **A catalog Label matches a genuinely specialized style the user asked for** AND GPT Image 2 is not itself labelled for it — e.g. the user asks for `manga`/`anime`/`watercolor`/`logo` and another model carries that exact label. A generic "realistic photo / recreate this / make an image" request is NOT a specialized style — keep GPT Image 2.

If none of the three applies, use GPT Image 2. When in doubt, GPT Image 2.

- Compare the candidates' cards in `references/models.md` only for the parameters GPT Image 2 accepts/rejects (aspect ratios, resolution ceiling, output formats, `quality`) — GPT Image 2 is the only model that reads `quality`.
- **What the labels mean.** A model's labels (the Catalog table's **Labels** column) mark the content/subject/style it is best-suited for. They only override the GPT Image 2 default under exception 3 above — a specialized style the user explicitly asked for that GPT Image 2 isn't labelled for. Never let a label pull you off GPT Image 2 for a generic request.
- Some capabilities live on a single model (camera-rotation, masked inpaint, outpaint, transparent cut-out). Find that model by the param / label it supports in the table + `references/models.md` — never by memory (this is exception 1).

## Gotchas

- **Never pick a slug from the wrong category** — a text-to-image (`image_generation`) slug given `referenceImages`, or an editing slug asked to upscale, fails at the adapter. Match the operation to its category first, then choose within it.
- **Some models cap resolution unless you ask** — for a few, omitting `resolution` returns a low render even for a "4K" request. Always set `resolution` (`high`/`ultra`) for high-res work; check the model's card.
- **Exact pixel size on a model without `width`/`height`** — approximate with the CLOSEST `resolution` label + CLOSEST `aspectRatio`, then downscale locally if it must be exact. Never render at the default size and shrink, and never say the model "always renders at a fixed internal resolution". See the "Exact pixel size requested" section.
- **Seed only works on the models whose card lists it** — check the card before promising reproducibility.
- **`referenceImages` for edits, not `startFrame`** — startFrame is a video concept.
- Read the model's card in `references/models.md` before setting `quality` or `cameraAngles` — only specific models consume them.
