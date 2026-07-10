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
- `resolution` — output size. **Per-model** — some use labels (`1K/2K/4K`), others size buckets (`low/medium/high/ultra`). A few cap the render unless you pass a high value — the table lists the default and the ceiling.
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

Once the category is fixed, several models usually qualify. Decide from the data — neutrally, with no default favourite:

- Compare the candidates' cards in `references/models.md` on the traits your task needs: max reference images, aspect ratios, resolution ceiling, output formats, and whether they take `cameraAngles` or `quality`.
- **What the labels mean — use them to pick the best-suited model.** A model's labels (the Catalog table's **Labels** column) mark the content, subject or style that model is the BEST-SUITED for. If the user's request matches a label, **strongly prefer that model** over an unlabelled one in the same category — that is exactly what the label is telling you. Examples: a model labelled `cities` is the best pick for a city / urban photo; `manga` → the best for manga-style drawing; `portrait` → portraits; `logo` → logos; `anime`, `watercolor`, `product`, etc. → their named style/subject. Read every candidate's labels against what the user asked for and route to the model whose label fits. When no label matches your task, ignore labels and choose on quality / price.
- Some capabilities live on a single model (camera-rotation, masked inpaint, outpaint, transparent cut-out). Find that model by the param / label it supports in the table + `references/models.md` — never by memory.

## Gotchas

- **Never pick a slug from the wrong category** — a text-to-image (`image_generation`) slug given `referenceImages`, or an editing slug asked to upscale, fails at the adapter. Match the operation to its category first, then choose within it.
- **Some models cap resolution unless you ask** — for a few, omitting `resolution` returns a low render even for a "4K" request. Always set `resolution` (`high`/`ultra`) for high-res work; check the model's card.
- **Seed only works on the models whose card lists it** — check the card before promising reproducibility.
- **`referenceImages` for edits, not `startFrame`** — startFrame is a video concept.
- Read the model's card in `references/models.md` before setting `quality` or `cameraAngles` — only specific models consume them.
