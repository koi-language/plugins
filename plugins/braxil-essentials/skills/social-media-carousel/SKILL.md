---
name: social-media-carousel
description: Create social-media carousels (Instagram, LinkedIn, TikTok, Facebook, X) as a set of generated IMAGES. Structures content as hook → value → CTA, respects platform sizes and safe zones, and renders each slide with generate_image using a clean professional style by default (or a slide-deck style preset on request). Use for "create a carousel", "Instagram/LinkedIn carousel", "swipe post", "turn this into slides", "social media slides".
---

# Social Media Carousel

Turn a topic, newsletter, or notes into a carousel where **every slide is a generated image** (no HTML, no templates).

## ⚠️ Act now — do NOT hunt the filesystem

Everything you need to make a great carousel is **in this document**. Do **NOT** run `find`, `shell`, `read_file`, `search`, or `get_tool_info` to locate this skill, its `SKILL.md`, or any `references/` file. Don't go looking for old projects. The `references/` files listed at the bottom are **optional deep-dives** — you only ever open one if the user explicitly asks for a specific slide-deck style you don't already know. For a normal request, read nothing else: go straight from the user's ask to writing the outline and calling `generate_image`.

## The whole job in 5 steps

### 1. Understand the ask (and research if needed)

- Identify the **topic**, **platform** (default: Instagram; if the user says LinkedIn, use LinkedIn), and **slide count** (default 6; range 4–10).
- If the user asks you to look something up ("búscalo por internet"), do the web research FIRST: `web_search` → wait → optionally `web_fetch` 1–2 good sources → then continue. Keep facts accurate (real numbers, names, sources).
- **Autonomous / YOLO mode**: do NOT ask questions. Pick sensible defaults (platform from the ask, 4:5 ratio, 6 slides, the Default Style below) and proceed straight to generating. Only ask a question if the user is NOT in autonomous mode AND something essential is genuinely missing.

### 2. Pick size + resolution + style

`generate_image` does NOT take pixel width/height. It takes `aspectRatio` and `resolution` enums. Set both explicitly on every call:

**`aspectRatio`** — by platform (default `4:5`):

| Platform | aspectRatio | Renders ~ |
|----------|-------------|-----------|
| Instagram / LinkedIn / Facebook | `4:5` | 1024×1280 at 1K |
| TikTok / Stories | `9:16` | 1024×1820 at 1K |
| Square / X | `1:1` | 1024×1024 at 1K |

**Target the networks' own resolution — never bigger.** Social feeds display at ≈1080 px wide and downscale anything larger, so generating bigger only burns credits for zero visible gain.

**`resolution: "1k"` + `quality: "medium"` — MANDATORY. Do NOT omit `resolution`.**
- The `resolution` enum is a ceiling on the LONGEST edge: `1k`≈1024, `2k`≈2048, `4k`≈4096. `1k` (1024) is the closest step to the networks' native ≈1080 px **without going over** — exactly what you want.
- **If you omit `resolution`, the backend defaults to 2K (2048) — ~4× the pixels, ~4× the credits, and thrown away when the network downscales. Always set it.**
- If the live catalog doesn't offer `1k` for the chosen model, pick the **smallest** resolution it does offer that is ≥1024 (i.e. closest to 1080). NEVER jump to `2k`/`4k` by default.
- Use `quality: "medium"` for finals; `quality: "low"` for quick drafts. (Social slides are big text + few words — they do NOT need the 4K/high treatment dense infographics require.)
- Only go `resolution: "2k"`+ if the user explicitly asks for print-grade.
- **Sanity check after the first slide**: if its long edge comes out much bigger than ~1350 px (e.g. 2560), the auto-picked model's smallest tier is oversized — run `get_tool_info(generate_image)`, pick a model/resolution whose ceiling is ~1K, and regenerate. Don't keep paying 2K+ for images the network shrinks to 1080.

Target dimensions per network are in `references/platform-specs.md` (Instagram 1080×1350 or 1080×1080, TikTok 1080×1920, etc.). Nothing social needs more than that. Generate every slide at the SAME `aspectRatio` and `resolution`. Slide caps: IG/LinkedIn 20, TikTok 35, Facebook 10, X 4.

**Style**: use the **Default Style** block below unless the user names a different look. (17 slide-deck presets exist in `references/styles/` — only open one if the user asks for a specific named style you don't already know.) **When you DO ask the user which style** (non-autonomous), send ALL 17 presets as options in ONE call (the 2-3 best matches first, marked recommended; then the rest; then Custom) — never just 2-3 and never "ask 3 then re-prompt". Use the Full Style Catalog in `references/confirmation.md` for the option titles + descriptions.

### 3. Write the outline + per-slide prompts

Structure every carousel as **Hook → Value → CTA**:

- **Slide 1 — Hook**: a bold claim / surprising stat / question that stops the scroll. One emphasized highlight word. Add a visible "Swipe →" cue. ~10–20 words.
- **Slides 2…N-1 — Value**: ONE idea each. Narrative heading (tells the story, not a label), a couple of short supporting lines, one emphasized key phrase. ~15–40 words per slide. Keep exact numbers/names/sources.
- **Slide N — CTA**: one-line takeaway + a clear ask (Follow / Save / Comment / link) + the author handle if given. Not just "Thanks".

Save the plan to `social-carousel/{topic-slug}/outline.md` (slug = 2–4 kebab-case words). Then write one prompt file per slide at `social-carousel/{topic-slug}/prompts/NN-slide-{slug}.md` containing: the Default Style block (or chosen style), this slide's literal text/data (no placeholders), the aspect ratio, and a one-line layout note. The prompt file is the reproducibility record — write it before generating.

**Rules that keep slides good (apply inline, don't go read a file):**
- These are IMAGES read on a phone: large type, high contrast, ≤ ~40 words/slide.
- **Safe zone**: keep ALL text away from the edges (top ≥8%, bottom ≥12%, sides ≥6%; on 9:16 keep text in the centre) — feeds overlay UI on the borders.
- Same palette, type, margins, accent and numbering on EVERY slide (a carousel must look like one set).
- No watermarks, fake platform UI, page numbers, or logos.
- Voice: direct, confident. Avoid AI clichés ("dive into", "explore", "journey", "revolutionary").
- Match the slide text language to the user's language.

### 4. Generate the images

Once every prompt file exists, call `generate_image` for each slide with the SAME params: `aspectRatio` (e.g. `"4:5"`), `resolution: "1k"`, `quality: "medium"`. Generate in batches (parallel where supported, ~4 at a time); report `Generated X/N`; retry a failed slide once. Save as `NN-slide-{slug}.png` in order.

### 5. Package for the platform, then show

The upload format differs by platform — match it:

| Platform | Carousel format | Deliverable |
|----------|-----------------|-------------|
| **LinkedIn** | **A PDF document post** — LinkedIn carousels are NOT a set of images; you upload ONE PDF and LinkedIn renders the swipeable carousel | bundle all slides into `{topic-slug}.pdf` (one slide per page, in order) **and** keep the PNGs |
| Instagram / Facebook / TikTok / X | Native multi-image post | the PNGs themselves, uploaded in order |

**For LinkedIn, merge the PNGs into a single PDF** with the bundled `scripts/merge-to-pdf.ts` (the same assembler the slide-deck skill uses — it embeds each `NN-slide-*.png` as one page at its native pixel size, in order, and writes `{topic-slug}.pdf`):

```bash
${BUN_X} {baseDir}/scripts/merge-to-pdf.ts social-carousel/{topic-slug}
```

If it errors on a missing `pdf-lib`, install once and retry: `cd {baseDir} && ${BUN_X} install`. (LinkedIn document carousels: PDF, 1:1 or 4:5 pages, up to 300 pages, ≤100 MB — our defaults fit.)

Then present the result: for LinkedIn, hand over `{topic-slug}.pdf` (the thing they upload) and mention the PNGs are there too; for the other platforms, present the numbered PNGs in swipe order.

## Default Style (use this unless told otherwise)

Drop this verbatim into each prompt as the style. It's a clean, professional editorial look that works for LinkedIn and most topics:

```
STYLE: Clean professional editorial. Flat solid background, generous whitespace, strong grid.
Background: off-white #F7F5F1 (or deep navy #0F172A for a bold/dark variant — keep one choice across all slides).
Typography: large bold geometric sans-serif headlines; clean medium-weight sans body. Clear size contrast (headline 3–4× body).
Color: one accent used consistently — confident blue #2E86C1 (or warm red #D94A4A for energy). Primary text #1A1A1A on light, #FFFFFF on dark.
Accent elements: a thin underline or small kicker number per slide; simple flat icons only where they add meaning. No clutter, no gradients-as-decoration, no stock-photo collage.
Mood: credible, modern, editorial — like a premium publication's social post.
```

For a different feel, the user can name a slide-deck preset (e.g. `bold-editorial`, `corporate`, `minimal`, `notion`, `dark-atmospheric`, `vector-illustration`, `scientific`, `editorial-infographic`). Only then open that one file in `references/styles/`.

## File Layout

```
social-carousel/{topic-slug}/
├── source.md                      # fetched/pasted research (only if you did any)
├── outline.md                     # hook → value → CTA plan
├── prompts/NN-slide-{slug}.md     # one prompt per slide
├── NN-slide-{slug}.png            # the generated slides (swipe order)
└── {topic-slug}.pdf               # LinkedIn only: slides bundled as a PDF document post
```

If a `social-carousel/{topic-slug}/` for THIS exact topic already exists with slides, ask whether to continue or regenerate. Otherwise just create it — do NOT scan the disk for unrelated old projects.

## Optional deep-dive references

Open one ONLY if you specifically need it (you usually don't):

| File | When |
|------|------|
| `references/platform-specs.md` | exact specs/safe-zones for an unusual platform |
| `references/carousel-structure.md` | more hook types, frameworks, swipe psychology |
| `references/content-transformation.md` | turning a long newsletter/article into slides |
| `references/styles/<preset>.md` | a specific named slide-deck style the user requested |
| `references/dimensions/*.md` | building a fully custom texture/mood/typography/density style |
| `references/content-rules.md`, `references/outline-template.md`, `references/base-prompt.md` | extra checklists/templates |

## Scripts

`{baseDir}` = this SKILL.md's directory. Resolve `${BUN_X}`: prefer `bun`; else `npx -y bun`; else suggest `brew install oven-sh/bun/bun`.

| Script | Purpose |
|--------|---------|
| `scripts/merge-to-pdf.ts` | Bundle the slide PNGs into one PDF (LinkedIn document carousel). One page per slide, native size, swipe order. |

## Notes
- 6–8 slides is the engagement sweet spot.
- Image generation takes ~10–30s/slide; report progress.
- For sensitive public figures, use stylized alternatives instead of refusing.
