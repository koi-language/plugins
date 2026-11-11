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
- `seed` — reproducibility seed: same seed + same prompt ⇒ the same image **on models that honour it** (Krea 2 Turbo and the Nano-Banana 2 / Pro models; GPT Image 2.x and Seedream Lite ignore it). Omit for a fresh random result.
- `referenceImages` — file paths / attachment IDs (`att-N`) / `@mention` handles, OR objects `{ alias, path }`. **Prefer aliased objects** and refer to them by alias in the prompt ("paint the `logo` onto the `mug`"). **Only edit / outpaint / bg-remove models accept refs, and the max count is per-model** — text-to-image models reject them.
- `outputFormat` — **per-model** (most do `png/jpeg/webp`; some only `png/jpeg` — the table lists it). Default png.
- `cameraAngles` — `{ horizontal?, vertical?, zoom? }` — ONLY for a different camera angle of an existing image; consumed only by a camera-rotation model (its card lists `cameraAngles` support). At least one axis; omitted axes stay at the model default.
- `saveTo` — optional COPY destination (dir or full `.png/.jpg/.webp` path). The original always stays in `<project>/images` and comes back as `images[].savedTo` — **use that for downstream chaining, never fabricate a path**; your copy is `images[].exportedTo`.
- `summary` — one-line "what was this for" for the creations ledger.
- `model` — **REQUIRED. YOU pick the exact slug.** There is no auto-router — omitting it (or passing `"auto"`) makes the tool error out. Read the **Catalog table** in the tool's own description (or `references/models.md`) and pick a slug whose **Categories** column contains the bucket for your operation (see "Categories" below). The gateway hard-errors on an unknown slug, so don't invent one.

Returns `{ success, provider, model, images: [{ url?, b64?, savedTo?, exportedTo? }] }`.

## Exact pixel size requested but the model has NO `width`/`height` — MANDATORY rule

When the user asks for a **concrete pixel size** (e.g. "1024×1024", "512px", "a 1080p", "4K", "un icono de 1024"):

1. **If the chosen model accepts `width`+`height`** (ONLY the Seedream family and Qwen-Image-Edit) → set them to the exact size. Done.
2. **If it does NOT** (GPT Image 2.x, Nano-Banana, Krea, Bria… — every other model) → you **CANNOT** pass an exact canvas, so you MUST APPROXIMATE it from the two labels the model *does* accept — **do NOT just render at the default size and shrink it**:
   - **`resolution`** → pick the label whose pixel size (in that model's card — e.g. GPT Image 2.x: `low`=1280, `medium`=1920, `high`=2560, `ultra`=3840 long edge) is **CLOSEST to the requested size**. For 1024 that is `low` (1280), NOT the default `high` (2560).
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

**Outpaint, upscale and background-removal are NOT `generate_image`** — they are **dedicated tools**, and you ALWAYS pass their `model` too (top of the QUALITY RANKING), so the user sees which model runs. Masked inpaint is not exposed by the MCP tools at all.

## Routing: which tool + (for generate_image) which model

| Operation | Tool | Send |
|---|---|---|
| Text-to-image | `generate_image` (`model` from `image_generation`) | `prompt` (+aspectRatio/resolution/n) |
| Edit / image-to-image | `generate_image` (`model` from `image_editing`) | `prompt` + `referenceImages` |
| Camera angle of an image | `generate_image` (`model` = `fal-ai/qwen-image-edit-2511-multiple-angles`) | `referenceImages` (1) + `cameraAngles` |
| Outpaint / extend the canvas | `outpaint_image`, `model` = `fal-ai/flux-2-pro/outpaint` | `image` + `padTop/padBottom/padLeft/padRight` (+`prompt`) |
| Upscale | `upscale_image`, `model` = `fal-ai/topaz/upscale/image` | `image` (+`upscaleFactor`/`prompt`/`creativity`/`faceEnhancement`) |
| Remove background | `background_removal`, `model` = `fal-ai/bria/background/remove` | `image` |
| Remove an object (masked) | `generate_image` (`model` = `fal-ai/ideogram/object-removal`) | `referenceImages` = `[source, B/W mask]` (white = remove; build the mask with an edit model first — see its card) |
| Inpaint a masked region (fill with new content) | — | not available via the MCP tools |

## Choosing within a category

**🔴 HIGHEST QUALITY WINS, across ALL models (user rule).** The DEFAULT for every operation is ALWAYS the highest-quality model that can do it, per the **QUALITY RANKING** below. Go down the ranking ONLY when: the higher model cannot do the operation / input shape (check its card), the user names another model, or the user explicitly asks for speed, low cost or a throwaway draft. When a model is added to the catalog, PLACE IT IN THE RANKING in the same change (and say its rank on its card in `references/models.md`).

**QUALITY RANKING (best first):**
- Text-to-image and edit / image-to-image: **1. GPT Image 2.6 Sunburst** (`openai/gpt-image-2.6/sunburst/text-to-image`, `…/sunburst/edit`), the best image model (user decision). Every other image model ranks below it and is used only under the exceptions listed further down.
- **More pixels / 4K (user rule):** the image is final and only needs more pixels → `upscale_image` with **Topaz** (faithful: it does not redraw the picture). The image is being changed anyway → ONE edit with **GPT Image 2.6 Sunburst edit at `resolution: "ultra"`** (4K). NEVER use Nano Banana or any other edit model to "upscale": an edit model redraws the whole image.
- Upscale: **1. Topaz** (`fal-ai/topaz/upscale/image`, faithful) · 2. Recraft Creative Upscale (`fal-ai/recraft/upscale/creative`) only when the user wants the upscaler to invent new detail.
- Background removal: **1. Bria** (`fal-ai/bria/background/remove`) · 2. Pixelcut (`pixelcut/background-removal`).
- Outpaint: **1. Flux 2 Pro outpaint** (`fal-ai/flux-2-pro/outpaint`) · 2. Bria Expand (`fal-ai/bria/expand`).
- Camera rotation, masked removal: one model each.
- 🔴 **Pass `model` on EVERY media tool call** (generate_image, upscale_image, background_removal, outpaint_image…), never leave it to auto-routing: the chat banner shows the model.

**🔴 NEWEST VERSION WINS (user rule).** When a model family has several versions in the catalog (GPT Image 2 / 2.5 / 2.6, Seedream 4.5 / 5, Nano-Banana 2 / Pro, …), ALWAYS use the NEWEST version. An older version is only picked when the user names it explicitly, or when the operation is impossible on the newest one (check its card). This applies to every default named below: if a newer version of the default exists, use the newer one.

**🔴 BEST QUALITY WINS within the same version (user rule).** When the newest version comes in several variants (quality vs speed / cost: Sunburst vs Flare, Pro vs Lite / Standard / Turbo / Fast / Mini, Max vs base…), the DEFAULT is ALWAYS the highest-quality variant. Pick a faster or cheaper variant ONLY when the user explicitly asks for speed or low cost, or for a throwaway draft.

**DEFAULT MODEL — always GPT Image 2.6 unless a concrete reason below forces another.** It has two variants: **Sunburst = best quality**, **Flare = speed**. 🔴 **QUALITY FIRST by default: use Sunburst.** Use Flare ONLY when the user explicitly asks for speed ("rápido", "quick draft", "a quick test") or for a throwaway preview.
- **Text-to-image** → `openai/gpt-image-2.6/sunburst/text-to-image` (fast: `openai/gpt-image-2.6/flare/text-to-image`).
- **Edit / image-to-image** → `openai/gpt-image-2.6/sunburst/edit` (fast: `openai/gpt-image-2.6/flare/edit`).
- GPT Image 2 and 2.5 are OLDER versions: never pick them unless the user names them.

Reach for GPT Image 2.6 first, every time. Do NOT switch to Nano-Banana, Seedream, Krea, Qwen, Bria or any other model just because it "might look better" or "is newer" — that is exactly the wrong reason. Only deviate when ONE of these is true:

1. **The operation is impossible on GPT Image 2.6.** Camera-rotation (`fal-ai/qwen-image-edit-2511-multiple-angles`), an exact-pixel canvas (Seedream family / Qwen-Image-Edit accept explicit `width`+`height`), or the separate no-model tools (outpaint, upscale, background-removal). If GPT Image 2.6 cannot physically do it, use the one model that can.
2. **The user explicitly names another model** ("use Nano-Banana", "hazla con Seedream"). Honour the request.
3. **A catalog Label matches a genuinely specialized style the user asked for** AND GPT Image 2.6 is not itself labelled for it — e.g. the user asks for `manga`/`anime`/`watercolor`/`logo` and another model carries that exact label. A generic "realistic photo / recreate this / make an image" request is NOT a specialized style — keep GPT Image 2.6.

If none of the three applies, use GPT Image 2.6. When in doubt, GPT Image 2.6.

- Compare the candidates' cards in `references/models.md` only for the parameters GPT Image 2.6 accepts/rejects (aspect ratios, resolution ceiling, output formats, `quality`). Only the GPT Image 2 / 2.5 / 2.6 families read `quality` (`xhigh`/`max` only on 2.5 / 2.6).
- **What the labels mean.** A model's labels (the Catalog table's **Labels** column) mark the content/subject/style it is best-suited for. They only override the GPT Image 2.6 default under exception 3 above — a specialized style the user explicitly asked for that GPT Image 2 isn't labelled for. Never let a label pull you off GPT Image 2.6 for a generic request.
- Some capabilities live on a single model (camera-rotation, masked inpaint, outpaint, transparent cut-out). Find that model by the param / label it supports in the table + `references/models.md` — never by memory (this is exception 1).

## 🔴 NEVER build image content by hand (user rule, top priority)

EVERY visual change to an image is drawn by an IMAGE MODEL. The result you deliver is ALWAYS either (a) the model's output, whole, or (b) the master with ONE kind of local operation applied:

**The ONLY local pixel operation allowed:** cut a region from the MODEL'S EDIT of the master and paste it onto THAT master, at the SAME resolution, at the same coordinates, 1:1 (see "Edit mode: master"). Source = the model's edit of this master. Destination = this master. Nothing else.

**FORBIDDEN, always, whatever the reason** (each one has already been tried and the user rejected it: it looks fake, pasted, without real shadows or light):
- Pasting / placing / inserting into an image any element taken from ANOTHER image: a reference photo, a "restored" badge or logo, a cut-out, an element from an earlier version or another generation, a texture. ("I placed the badge myself" = forbidden.)
- Removing or covering something by hand (clone, patch, paint, blur, fill).
- Mixing versions: detail / texture / frequency transfer from one version to another, blending a high-res copy into an upscaled image, "adding the fine texture only where both versions match", masks that combine two generations. ("I took only the fine texture from the high-res copy" = forbidden.)
- Upscaling with an edit model or by resizing and then repairing it by hand.
- Any colour / tone matching that is not explicitly asked by the user.

**The flows:**
- **The RESOLUTION changes** (e.g. the user wants it in 4K and the master is smaller) → ONE edit with the model AT the new resolution (4K: `resolution: "ultra"` + `aspectRatio`, master + references in `referenceImages`, ALL the requested changes in that one prompt). That whole image IS the result AND becomes the NEW MASTER. No compositing of any kind afterwards. If it is not good enough, run the edit again with a better prompt: never fix it by hand.
- **Same resolution** → the edit with the model, then (edit mode "master") `composite_partial_edit` pastes ONLY the areas the MODEL changed onto the master, as described below.
- **Only more pixels, nothing else changes** → `upscale_image` (Topaz). Its output is the result. Nothing pasted on it.

To make an element match a reference (an exact badge, a logo), put the reference in `referenceImages` and describe it in the prompt: the model draws it into the scene with its light and shadows. If the model's version is not identical enough, edit again (better prompt, a close-up reference): never paste the reference.

## Edit mode: master or normal (user setting, per turn)

Each turn carries an `# IMAGE EDIT MODE` line set by the user in the chat options. Default: **master**.

**normal** → keep the edit model's whole output as the result, as usual.

**master** → the user wants ONLY the changed areas. Edit models re-render the WHOLE picture even when told "change only X" (faces, cloth texture, ground, sky all drift), so in master mode **the model's whole output is NEVER the result**. Procedure:
1. **The MASTER is the clean image.** It is the original the user gave, the last version the user approved, or the last edit that CHANGED THE RESOLUTION (that one replaces the master, see the rule above). EVERY new edit starts from the master as `referenceImages`, NEVER from the previous edit. Remember which file is the master of each image (say it to the user the first time).
2. **Edit with the model as usual** (same model choice and params), at the master's size so the elements stay in place.
3. 🔴 **Build the partial edit with `composite_partial_edit` { masterImage: the master, editImage: the model's edit }.** NEVER composite by hand (Python / PIL / ImageMagick). The tool:
   - finds what the model REALLY changed, ignoring the re-render drift, and keeps each change whole (its shadows, folds, reflections);
   - follows every change to its END, on BOTH sides: where the new content appears AND where the old content disappears (a strap or rifle that moved = new strap + old strap gone, all along its length). A cut that stops half-way leaves the old object next to the new one (two straps);
   - cuts every area generously and fades it OUTSIDE the change, so no old colour shows at the edge;
   - pastes the pixels 1:1 at the same place (never scaled, moved or altered);
   - saves it as a new PNG and registers it as a creation (partial edit, with its master and edit in Info);
   - returns the `regions` it found and a `checkImage` with the pasted area tinted magenta.
   It refuses images of different size: that is a resolution change, the edit is the new master.
4. **Check it.** LOOK at `checkImage` and at the composite, zoomed on every change:
   - a tinted area the user did NOT ask for (drift on the ground, a face) → call again with `regions`: normalised boxes {x,y,w,h} around where the change was asked. `regions` only CHOOSES which changes go in: a chosen change is still taken whole, also outside the box, so a box on the hand is enough for a rifle that moved from hand to shoulder;
   - an object that moved or was removed must show NO trace of its old place: if you see the old one next to the new one, the change was cut short → raise `margin` / `sensitivity`;
   - a change missing or cut short (old colour at an edge, a shadow that stops) → call again with a higher `margin` (wider cut) or `sensitivity` (subtler changes).
5. 🔴 **NEVER fall back to the whole edit.** If after adjusting it still is not right, show the user the composite and the edit and ASK. Delivering the whole edit in master mode is exactly what the user turned this mode on to avoid.
6. **Global changes are the only exception** (a new style, new light / time of day, a reframe or new camera, a change over most of the image): there is no "area" to cut. Say so and ask before delivering the whole edit.
7. Once the user approves the result, it becomes the new master.

`save_composite_image` only registers a composite made another way; `composite_partial_edit` already registers its own.

## Gotchas

- **Provider chokes on a HEAVY source image** ("Failed to download the file", size/timeout errors on `referenceImages`) → run **`optimize_image({ image })`** (LOSSLESS PNG shrink, default ≤2 MB / ≤2048px) and retry with its `savedTo`. **NEVER convert to JPEG via shell (sips/ffmpeg)** — lossy re-encoding is forbidden; this tool is the sanctioned path.

- **Never pick a slug from the wrong category** — a text-to-image (`image_generation`) slug given `referenceImages`, or an editing slug asked to upscale, fails at the adapter. Match the operation to its category first, then choose within it.
- **Some models cap resolution unless you ask** — for a few, omitting `resolution` returns a low render even for a "4K" request. Always set `resolution` (`high`/`ultra`) for high-res work; check the model's card.
- **Editing a SMALL reference → the output inherits the ref's tiny canvas unless you set `resolution`.** Edit models (e.g. GPT Image 2.6 edit, Seedream edit) match the output size to the base `referenceImages` when you DON'T pass an explicit size — so a 500×500 web thumbnail in, a ~500×500 render out, and your `aspectRatio` is IGNORED. `quality` does NOT change pixels (it's sampling effort only). When the reference is small and you want a proper-size result, **pass `resolution: high`/`ultra` (and `aspectRatio`) explicitly** so the model renders a fresh large canvas instead of copying the ref's dimensions.
- **Low-res result → REGENERATE, do NOT upscale — ESPECIALLY with references.** If a render came out small/low-res (matched a small ref, or you forgot `resolution`), the fix is to **redo the generation at the right `resolution`**, NOT to run `upscale_image` on the bad output. Upscaling FABRICATES detail and looks worse than a clean high-res render — and it's never justified when a reference exists, because you can just generate again from that same reference at full size. Reserve `upscale_image` for when the source is already the best available pixels (a real photo, a final render you can't reproduce) — never as a patch for a generation you undersized.
- **Exact pixel size on a model without `width`/`height`** — approximate with the CLOSEST `resolution` label + CLOSEST `aspectRatio`, then downscale locally if it must be exact. Never render at the default size and shrink, and never say the model "always renders at a fixed internal resolution". See the "Exact pixel size requested" section.
- **Seed only works on the models whose card lists it** — check the card before promising reproducibility.
- **`referenceImages` for edits, not `startFrame`** — startFrame is a video concept.
- Read the model's card in `references/models.md` before setting `quality` or `cameraAngles` — only specific models consume them.
