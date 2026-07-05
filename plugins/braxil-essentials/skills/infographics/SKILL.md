---
name: infographic
description: Generates professional infographics with 20 layout types and 17 visual styles. Analyzes content, recommends layout×style combinations, and generates publication-ready infographics. Use when user asks to create "infographic", "visual summary" or similar.
---

# Infographic Generator

Two dimensions: **layout** (information structure) × **style** (visual aesthetics). Freely combine any layout with any style.

## Layout Gallery

| Layout | Best For |
|--------|----------|
| `linear-progression` | Timelines, processes, tutorials |
| `binary-comparison` | A vs B, before-after, pros-cons |
| `comparison-matrix` | Multi-factor comparisons |
| `hierarchical-layers` | Pyramids, priority levels |
| `tree-branching` | Categories, taxonomies |
| `hub-spoke` | Central concept with related items |
| `structural-breakdown` | Exploded views, cross-sections |
| `bento-grid` | Multiple topics, overview (default) |
| `iceberg` | Surface vs hidden aspects |
| `bridge` | Problem-solution |
| `funnel` | Conversion, filtering |
| `isometric-map` | Spatial relationships |
| `dashboard` | Metrics, KPIs |
| `periodic-table` | Categorized collections |
| `comic-strip` | Narratives, sequences |
| `story-mountain` | Plot structure, tension arcs |
| `jigsaw` | Interconnected parts |
| `venn-diagram` | Overlapping concepts |
| `winding-roadmap` | Journey, milestones |
| `circular-flow` | Cycles, recurring processes |

Full definitions: `references/layouts/<layout>.md`

## Style Gallery

| Style | Description |
|-------|-------------|
| `craft-handmade` | Hand-drawn, paper craft (default) |
| `claymation` | 3D clay figures, stop-motion |
| `kawaii` | Japanese cute, pastels |
| `storybook-watercolor` | Soft painted, whimsical |
| `chalkboard` | Chalk on black board |
| `cyberpunk-neon` | Neon glow, futuristic |
| `bold-graphic` | Comic style, halftone |
| `aged-academia` | Vintage science, sepia |
| `corporate-memphis` | Flat vector, vibrant |
| `technical-schematic` | Blueprint, engineering |
| `origami` | Folded paper, geometric |
| `pixel-art` | Retro 8-bit |
| `ui-wireframe` | Grayscale interface mockup |
| `subway-map` | Transit diagram |
| `ikea-manual` | Minimal line art |
| `knolling` | Organized flat-lay |
| `lego-brick` | Toy brick construction |

Full definitions: `references/styles/<style>.md`

## Recommended Combinations

| Content Type | Layout + Style |
|--------------|----------------|
| Timeline/History | `linear-progression` + `craft-handmade` |
| Step-by-step | `linear-progression` + `ikea-manual` |
| A vs B | `binary-comparison` + `corporate-memphis` |
| Hierarchy | `hierarchical-layers` + `craft-handmade` |
| Overlap | `venn-diagram` + `craft-handmade` |
| Conversion | `funnel` + `corporate-memphis` |
| Cycles | `circular-flow` + `craft-handmade` |
| Technical | `structural-breakdown` + `technical-schematic` |
| Metrics | `dashboard` + `corporate-memphis` |
| Educational | `bento-grid` + `chalkboard` |
| Journey | `winding-roadmap` + `storybook-watercolor` |
| Categories | `periodic-table` + `bold-graphic` |

Default: `bento-grid` + `craft-handmade`

## Output Structure

```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```

Slug: 2-4 words kebab-case from topic. Conflict: append `-YYYYMMDD-HHMMSS`.

## Core Principles

- Preserve all source data **verbatim**—no summarization or rephrasing
- Define learning objectives before structuring content
- Structure for visual communication (headlines, labels, visual elements)
- **⛔ ALWAYS generate at maximum resolution (`4k`).** An infographic is dense small text — at the backend's default (low) resolution the labels come out blurry/illegible and the whole deliverable is unusable. The `generate_image` call MUST carry `resolution: "4k"` and `quality: "high"`. This is NON-NEGOTIABLE and is the #1 cause of bad infographics when forgotten. See Step 6 for the exact gate.

## Workflow

### Step 1: Source the content — RESEARCH or USER-PROVIDED

This skill never invents facts. So FIRST establish where the data comes from.

- **If the user already gave content** (pasted text, an attached doc, a URL to turn into an infographic) → use it; skip the question, go straight to 1.1.
- **If it's only a bare topic** (e.g. *"un infographic sobre la guerra civil"*) with no data → ASK via `prompt_user` (in the user's language), one question, two options:
  - *"Investiga tú los datos (busco en internet con fuentes)"* → **1A**
  - *"Yo te aporto el contenido"* → **1B**

**1A — Research (web search).** Run `web_search` to gather the key facts, figures, dates and quotes for the topic. **Use only what you actually find, and keep each important data point tied to its source** (note the source URL/name next to it). Build `source.md` from these VERIFIED findings — that becomes the verbatim source for the rest of the flow (the "no new information / verbatim" rules below now apply to the researched data). If results are thin or conflicting, tell the user and ask how to proceed — never pad with invented numbers.

**1B — User-provided.** The user writes / pastes the content (or attaches a doc). **Also invite them to attach any PHOTOS or material they want featured** — logos, portraits, maps, charts, reference images. Save the text → `source.md`; keep the list of attached image paths for Step 6.

**Photos / material (either path).** Any real image the user attached — or, in 1A, an image you saved locally from a source — is `read_file`'d (read-before-use) and then passed to `generate_image` as `referenceImages` in Step 6, so it's woven into the infographic instead of the model drawing a generic stand-in. (No real photos are fetched otherwise — everything else is rendered by the model.)

**1.1 Analyze Content → `analysis.md`**

1. Save source content (from 1A research or 1B user input → `source.md`)
2. Analyze: topic, data type, complexity, tone, audience
3. Detect source language and user language
4. Extract design instructions from user input
5. Save analysis (in 1A, also record the sources used)

See `references/analysis-framework.md` for detailed format.

### Step 2: Generate Structured Content → `structured-content.md`

Transform content into infographic structure:
1. Title and learning objectives
2. Sections with: key concept, content (verbatim), visual element, text labels
3. Data points (all statistics/quotes copied exactly)
4. Design instructions from user

**Rules**: Markdown only. No new information. All data verbatim.

See `references/structured-content-template.md` for detailed format.

### Step 3: Recommend Combinations

Recommend 3-5 layout×style combinations based on:
- Data structure → matching layout
- Content tone → matching style
- Audience expectations
- User design instructions

### Step 4: Confirm Options

Present all options in single confirmation:
1. **Combination** (always): 3+ options with rationale
2. **Aspect** (always): landscape/portrait/square
3. **Language** (only if source ≠ user language): which language for text

**⛔ Send ALL 17 styles as options in ONE call — never just the 3-5 recommended (users complain when they only see 3).** Put the best-fit styles FIRST and mark them recommended; then list every remaining style from the Style Gallery above, each as a human-readable label + its one-line look in the user's language (e.g. *"Cómic audaz — alto contraste, halftone"*, *"Pizarra de tiza"*, *"Acuarela de cuento"*…). The whole list ships in a single prompt, so the client can show the top picks and collapse the rest behind a "ver todos" toggle **without another round-trip** — do NOT "ask 3 then re-prompt with the rest". One call, all 17 styles. (Pair the chosen style with the recommended/selected layout; offer the full 20-layout Gallery the same way if the user wants to browse layouts.)

**⛔ Each combination option MUST be a HUMAN-READABLE label in the USER'S language — NEVER the raw kebab-case slug.** The internal ids (`linear-progression`, `aged-academia`, `bento-grid`, `chalkboard`, …) are file names, not UI copy: showing `linear-progression-aged-academia` as a choice is unreadable (the reported bug). Write each option as a natural phrase describing the layout × style, e.g.:
- *"Progresión lineal · estética académica envejecida"*
- *"Cuadrícula bento · pizarra de tiza"*
- *"Comparación enfrentada · gráfico audaz"*

Add a one-line rationale per option (why it fits this content). Keep the slug ONLY in your own internal notes so Step 5 can resolve `references/layouts/<layout>.md` + `references/styles/<style>.md` — the user never sees it. The same applies to aspect/language options: present them in the user's language ("Horizontal / Vertical / Cuadrado"), not enum tokens.

### Step 5: Generate Prompt → `prompts/infographic.md`

**⛔ MANDATORY FIRST ACTION of this step — AFTER the user confirms the combination in Step 4, `read_file` BOTH definition files for the CHOSEN combination:**
- `references/layouts/<layout>.md`
- `references/styles/<style>.md`

The one-line descriptions in the Layout/Style galleries above are NOT enough to write the prompt — the definition files carry the actual spec (exact color palette with hex codes, typography treatment, visual elements, text placement, variants). Reading other references earlier in the flow does NOT count: you cannot know which two files matter until the user picks, so the read happens HERE, every time. Never write the prompt from memory or from the gallery one-liners.

Then build the prompt by filling `references/base-prompt.md` (keep its section structure):
1. `{{LAYOUT_GUIDELINES}}` ← the layout definition just read (structure, visual elements, text placement)
2. `{{STYLE_GUIDELINES}}` ← the style definition just read — copy the palette hex codes, typography and visual-element specs into the prompt verbatim
3. `{{CONTENT}}` / `{{TEXT_LABELS}}` ← structured content from Step 2
4. All text in confirmed language

### Step 6: Generate Image

> **⛔⛔ READ THIS BEFORE CALLING `generate_image` ⛔⛔**
> The single most common failure of this skill is generating at the backend's
> default (low) resolution → blurry, unreadable infographic. **The very first
> thing you set on the `generate_image` call is the resolution.** A call to
> `generate_image` WITHOUT an explicit `resolution: "4k"` is a BUG — do not make it.

**6.1 — Set resolution + quality (MANDATORY, non-negotiable).**
On the `generate_image` call you MUST set:
- `resolution: "4k"` — the maximum. NEVER omit it and NEVER let it default. (If the
  active catalog genuinely does not list `4k`, pass the largest bucket it DOES list —
  e.g. `2k` — but `4k` is the target.)
- `quality: "high"`.

If you call `get_tool_info` for `generate_image` first, confirm the exact enum value
for the max resolution from the live catalog and use that — but you still ALWAYS pass it.

**6.2 — Pass the prompt.** Use the EXACT contents of `prompts/infographic.md` as the
`prompt` — read the file back if needed. Do NOT improvise a new/shorter inline prompt at
call time; the file you assembled in Step 5 IS the prompt.

**6.3 — Reference images (only if any).** If the user attached photos / material
(Step 1B) or you saved sourced images (1A) → `read_file` each, then pass them as
`referenceImages` so they're incorporated, and anchor them in the prompt (e.g. "place the
provided portrait of X in the top-left cell"). Otherwise omit `referenceImages` and the
model draws everything.

**6.4 — VERIFY THE OUTPUT IS HIGH-RES (hard gate — do NOT skip to Step 7).**
After the image returns, check its real dimensions (`image_info` / `inspect_creation`).
If the longest edge is **below 3000px**, run `upscale_image` (`upscaleFactor` chosen to
bring the longest edge to **≥4000px**, max 4) and use the upscaled file as the final
deliverable. You may only declare the infographic done once its longest edge is ≥3000px.

**6.5 — On failure, auto-retry once** (re-issuing the call WITH the `resolution`/`quality`
settings from 6.1).

### Step 7: Output Summary

Report: topic, layout, style, aspect, language, **final image resolution (longest edge in px)**, output path, files created. The resolution line is a self-check — if it reads below 3000px you skipped the Step 6.4 gate; go back and upscale before declaring done.

## References

- `references/analysis-framework.md` - Analysis methodology
- `references/structured-content-template.md` - Content format
- `references/base-prompt.md` - Prompt template
- `references/layouts/<layout>.md` - 20 layout definitions
- `references/styles/<style>.md` - 17 style definitions


