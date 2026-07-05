---
name: slide-deck
description: Generates professional slide deck images from content. Creates outlines with style instructions, then generates individual slide images. Use when user asks to "create slides", "make a presentation", "generate deck", "slide deck", or "PPT".
---

# Slide Deck Generator

Transform content into professional slide deck images. The deck is designed for **reading and sharing** (self-explanatory slides, logical scroll flow, social-media-friendly) rather than live presentation — that assumption drives every layout and density decision below.

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** exposed by the current agent runtime — e.g., `AskUserQuestion`, `request_user_input`, `clarify`, `ask_user`, or any equivalent.
2. **Fallback**: if no such tool exists, emit a numbered plain-text message and ask the user to reply with the chosen number/answer for each question.
3. **Batching**: if the tool supports multiple questions per call, combine all applicable questions into a single call; if only single-question, ask them one at a time in priority order.

Concrete `AskUserQuestion` references below are examples — substitute the local equivalent in other runtimes.

## Image Generation Tools

When this skill needs to render an image, use generate_image tool

**Prompt file requirement (hard)**: write each image's full, final prompt to a standalone file under `prompts/` (naming: `NN-slide-[slug].md`) BEFORE invoking any backend. The file is the reproducibility record and lets you switch backends without regenerating prompts.

Concrete tool names (`imagegen`, `image_generate`, `baoyu-image-gen`) above are examples — use the right generate_image tool.

## Batch Generation Policy

After every prompt file for the current generation group has been saved and verified, generate slide images in batches by default.

Priority order:

1. Use the chosen backend's native batch / multi-task interface if it exists. Each task must keep its own prompt file, output path, aspect ratio, session ID, and direct reference images.
2. If no native batch interface exists but the runtime can issue parallel tool calls, dispatch up to `generation_batch_size` slide images at a time. Default: `4`. An explicit user request in the current message, such as `--batch-size 4` or "并行4张一起生成", overrides EXTEND.md.
3. If neither native batch nor parallel tool calls are available, generate sequentially.

Rules:

- Never start the first batch until all selected slide prompt files exist on disk.
- Retry failed items once without regenerating successful items.
- Do not use subagents merely to parallelize image rendering. Use subagents only for separate prompt iteration or creative exploration.
- Merge PPTX/PDF only after all selected slide images are generated.

## Confirmation Policy

Default behavior: **confirm before generation**.

- Treat explicit skill invocation, a file path, matched signals/presets, and `EXTEND.md` defaults as **recommendation inputs only**. None of them authorizes skipping confirmation.
- Do **not** start Step 3 or later until the user completes Step 2.
- Skip confirmation only when the current request explicitly says to do so, for example: "直接生成", "不用确认", "跳过确认", "按默认出幻灯片", or equivalent wording.
- If confirmation is skipped explicitly, state the assumed style / audience / slide-count / language / backend in the next user-facing update before generating.

## Language

Respond in the user's language across questions, progress reports, error messages, and the completion summary. Keep technical tokens (style names, file paths, code) in English.

## Script Directory

`{baseDir}` = this SKILL.md's directory. Resolve `${BUN_X}`: prefer `bun`; else `npx -y bun`; else suggest `brew install oven-sh/bun/bun`.

| Script | Purpose |
|--------|---------|
| `scripts/merge-to-pptx.ts` | Merge slides into PowerPoint |
| `scripts/merge-to-pdf.ts` | Merge slides into PDF |

## Style System

17 presets covering technical / educational / lifestyle / editorial use cases. Every preset is a combination of four dimensions (texture / mood / typography / density). If the user picks "Custom dimensions" in Round 1, Round 2 of the confirmation asks one question per dimension — options and verbatim copy live in `references/confirmation.md`.

### Presets (17)

| Preset | Dimensions | Best For |
|--------|------------|----------|
| `blueprint` (Default) | grid + cool + technical + balanced | Architecture, system design |
| `chalkboard` | organic + warm + handwritten + balanced | Education, tutorials |
| `corporate` | clean + professional + geometric + balanced | Investor decks, proposals |
| `minimal` | clean + neutral + geometric + minimal | Executive briefings |
| `sketch-notes` | organic + warm + handwritten + balanced | Educational, tutorials |
| `hand-drawn-edu` | organic + macaron + handwritten + balanced | Educational diagrams, process explainers |
| `watercolor` | organic + warm + humanist + minimal | Lifestyle, wellness |
| `dark-atmospheric` | clean + dark + editorial + balanced | Entertainment, gaming |
| `notion` | clean + neutral + geometric + dense | Product demos, SaaS |
| `bold-editorial` | clean + vibrant + editorial + balanced | Product launches, keynotes |
| `editorial-infographic` | clean + cool + editorial + dense | Tech explainers, research |
| `fantasy-animation` | organic + vibrant + handwritten + minimal | Educational storytelling |
| `intuition-machine` | clean + cool + technical + dense | Technical docs, academic |
| `pixel-art` | pixel + vibrant + technical + balanced | Gaming, developer talks |
| `scientific` | clean + cool + technical + dense | Biology, chemistry, medical |
| `vector-illustration` | clean + vibrant + humanist + balanced | Creative, children's content |
| `vintage` | paper + warm + editorial + balanced | Historical, heritage |

Per-preset specs: `references/styles/<preset>.md`. Preset → dimension mapping: `references/dimensions/presets.md`.

### Dimensions (when "Custom dimensions" picked)

| Dimension | Options | Purpose |
|-----------|---------|---------|
| **Texture** | clean, grid, organic, pixel, paper | Background treatment |
| **Mood** | professional, warm, cool, vibrant, dark, neutral, macaron | Color temperature |
| **Typography** | geometric, humanist, handwritten, editorial, technical | Headline/body styling |
| **Density** | minimal, balanced, dense | Information per slide |

Full per-dimension specs: `references/dimensions/*.md`.

### Auto-Selection

Match content signals to a preset. Pick the first row whose signal keywords appear in the source; fall back to `blueprint` if nothing matches.

| Signals in source | Preset |
|-------------------|--------|
| tutorial, learn, education, guide, beginner | `sketch-notes` |
| hand-drawn, infographic, diagram, process, onboarding | `hand-drawn-edu` |
| classroom, teaching, school, chalkboard | `chalkboard` |
| architecture, system, data, analysis, technical | `blueprint` |
| creative, children, kids, cute | `vector-illustration` |
| briefing, academic, research, bilingual | `intuition-machine` |
| executive, minimal, clean, simple | `minimal` |
| saas, product, dashboard, metrics | `notion` |
| investor, quarterly, business, corporate | `corporate` |
| launch, marketing, keynote, magazine | `bold-editorial` |
| entertainment, music, gaming, atmospheric | `dark-atmospheric` |
| explainer, journalism, science communication | `editorial-infographic` |
| story, fantasy, animation, magical | `fantasy-animation` |
| gaming, retro, pixel, developer | `pixel-art` |
| biology, chemistry, medical, scientific | `scientific` |
| history, heritage, vintage, expedition | `vintage` |
| lifestyle, wellness, travel, artistic | `watercolor` |

### Slide Count Heuristic

| Source length | Recommended slides |
|---------------|--------------------|
| < 1000 words | 5-10 |
| 1000-3000 words | 10-18 |
| 3000-5000 words | 15-25 |
| > 5000 words | 20-30 (consider splitting) |

## Reference Images

Users may supply reference images to guide style, palette, layout, or subject.

- File path → copy to `{slide-deck-dir}/refs/NN-ref-{slug}.{ext}`
- Pasted image with no path → ask for the path, or extract style traits verbally as a text fallback

**Usage modes** (per reference):

| Usage | Effect |
|-------|--------|
| `direct` | Pass the file to the backend as a reference image for each slide |
| `style` | Extract style traits (line treatment, texture, mood) and append to every slide's prompt body |
| `palette` | Extract hex colors and append to every slide's prompt body |

Record refs in each slide's prompt frontmatter:

```yaml
references:
  - ref_id: 01
    filename: 01-ref-brand.png
    usage: direct
```

At generation time, verify files exist. If `usage: direct` and the backend accepts refs (e.g., `baoyu-image-gen --ref`), pass the file on every slide. Otherwise embed extracted `style`/`palette` traits in the prompt text.

## File Layout

```
slide-deck/{topic-slug}/
├── source-{slug}.{ext}
├── outline.md
├── prompts/NN-slide-{slug}.md
├── NN-slide-{slug}.png
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

**Slug**: 2-4 words, kebab-case, extracted from topic. "Introduction to Machine Learning" → `intro-machine-learning`.

**Backup rule** (applies across steps): if a file about to be written already exists, rename it to `<name>-backup-YYYYMMDD-HHMMSS.<ext>` before writing the new one. This protects user edits and enables rollback.

## Workflow

Copy this checklist and check off items as you complete them:

```
- [ ] Step 0: Resume check ⚠️ DO FIRST (before any research/analysis)
- [ ] Step 1: Setup & analyze
- [ ] Step 2: Confirmation ⚠️ REQUIRED (Round 1; Round 2 only if "Custom dimensions")
- [ ] Step 3: Generate outline
- [ ] Step 4: Review outline (conditional)
- [ ] Step 5: Generate prompts
- [ ] Step 6: Review prompts (conditional)
- [ ] Step 7: Generate images
- [ ] Step 8: Merge to PPTX/PDF
- [ ] Step 9: Output summary
```

### Step 0: Resume Check ⚠️ DO FIRST

**This runs BEFORE any web research, source gathering, or content analysis.** Its only job is to avoid throwing away work that already exists on disk — the #1 failure mode is the skill being re-triggered mid-project (e.g. the user says "continue with the presentation" after an unrelated detour) and cold-restarting from scratch, silently discarding an outline/analysis the user already approved.

**0.1 Derive the topic-slug** from the requested topic (same rule as the File Layout slug), WITHOUT doing any research first.

**0.2 Check for an in-progress deck**: does `slide-deck/{topic-slug}/` (or a near-match dir for the same topic) already contain any of `source-*.md`, `analysis.md`, `outline.md`, `prompts/`, or slide PNGs?

- **No** → this is a fresh project. Proceed to Step 1 normally.
- **Yes** → DO NOT re-research, re-analyze, or regenerate anything yet. Determine the furthest completed stage from what's on disk (source → analysis → outline → prompts → images → merged deck) and ask the user how to proceed using the **Existing Content** question in `references/confirmation.md`. The **recommended** option is **Continue** — resume from the first INCOMPLETE stage:

  | Furthest artifact present | Resume at |
  |---------------------------|-----------|
  | `outline.md` (no `prompts/`) | Step 5 (Generate prompts) |
  | `prompts/` (no PNGs) | Step 7 (Generate images) |
  | some PNGs (incomplete) | Step 7 for the missing slides only |
  | all PNGs (no pptx/pdf) | Step 8 (Merge) |

  Only re-run earlier stages if the user explicitly picks a "Regenerate …" or "Backup and regenerate" option. "Continue"/"sigue"/"retomamos" and equivalent wording mean RESUME, never restart.

**Treat a re-invocation of this skill as a likely resume, not a new project, until 0.2 proves otherwise.**

### Step 1: Setup & Analyze

**1.1 Analyze content** — follow `references/analysis-framework.md`: classify content, detect language, note signals for style selection, estimate slide count from length (see the **Slide Count Heuristic** in Style System above), generate topic slug. Save source as `source.md` (honor backup rule if one exists).

**1.2 Check existing output** ⚠️ REQUIRED before Step 2. This is the same gate as **Step 0** — if you already ran Step 0 for this topic and the user chose to start fresh / backup-and-regenerate, don't ask again. Only reached here when Step 0 determined this is a new project (or the user opted to regenerate). If `slide-deck/{topic-slug}/` exists, use the **Existing Content** question in `references/confirmation.md` (Continue / regenerate outline / regenerate images / backup and regenerate / exit).

Save findings to `analysis.md`: topic, audience, signals, recommended style and slide count, language detection.

### Step 2: Confirmation ⚠️ REQUIRED

**Hard gate**: this step is mandatory per the [Confirmation Policy](#confirmation-policy) — Steps 3+ cannot start until the user confirms here (or explicitly opts out with "直接生成" / equivalent wording in the current request).

**Round 1 (always)** — batch five questions in one `AskUserQuestion` call: style, audience, slide count, review-outline?, review-prompts?. Verbatim options in `references/confirmation.md`.

Summary displayed before the questions:
- Content type + topic
- Detected language
- Recommended style (based on signals)
- Recommended slide count (based on length)

**Round 2 (only if "Custom dimensions" in Round 1)** — batch four questions: texture, mood, typography, density. Verbatim options in `references/confirmation.md`. The four answers replace the preset.

**After confirmation**: update `analysis.md` with final choices and store `skip_outline_review` / `skip_prompt_review` flags from Q4/Q5.

### Step 3: Generate Outline

Read `references/design-guidelines.md` and apply it while building the outline: let the confirmed **audience** drive density/typography/color choices, and resolve the palette and headline/body treatment from its guidance (don't leave these to chance).

Resolve style: preset → `references/styles/{preset}.md`; custom dimensions → combine files in `references/dimensions/`. Build `STYLE_INSTRUCTIONS` from the resolved style, apply confirmed audience + language + slide count, follow `references/outline-template.md`, and save as `outline.md`.

Stop here if `--outline-only`. Skip Step 4 if `skip_outline_review`.

### Step 4: Review Outline (Conditional)

Display a slide-by-slide table (`# | Title | Type | Layout`) along with total count and resolved style. Ask: proceed / edit outline first / regenerate — verbatim in `references/confirmation.md`.

On "Edit outline first", tell the user to edit `outline.md` and ask again when ready. On "Regenerate outline", return to Step 3.

### Step 5: Generate Prompts

**Before the loop**: read `references/content-rules.md` once and keep its rules in context for every slide. They are MANDATORY at prompt-write time, not optional polish — they govern what each prompt MUST contain:
- **Data Traceability** — copy the literal numbers, labels, axis values, and caption text from the outline into the prompt. Never collapse concrete data into vague descriptors (write the real figures and the real caption text, NOT "a data grid of results" or "editorial captions explaining robustness").
- **No Placeholders** — every chart, label, and caption must carry its real content. A prompt that describes a chart's *shape* but not its *data/text* is a placeholder and must be fixed before saving.
- **Narrative Headlines** — apply the Bad/Good table.

For each slide in outline:
1. Read `references/base-prompt.md`
2. Extract `STYLE_INSTRUCTIONS` from the outline (don't re-read the style file). The render aesthetic (hand-drawn vs clean/vector vs photographic) is dictated by `STYLE_INSTRUCTIONS` — do NOT default to hand-drawn; honor the resolved texture/typography.
3. Add the slide's content, embedding the literal data/text per `content-rules.md` above
4. If a `Layout:` is specified, include guidance from `references/layouts.md`
5. Self-check against `content-rules.md`: does the prompt contain every concrete number/label/caption from the outline, with no placeholder descriptors? If not, fix it before saving.
6. Save to `prompts/NN-slide-{slug}.md` (backup rule applies)

Stop here if `--prompts-only`. Skip Step 6 if `skip_prompt_review`.

### Step 6: Review Prompts (Conditional)

Display the prompts index (`# | Filename | Slide Title`) and ask: proceed / edit prompts first / regenerate — verbatim in `references/confirmation.md`. Branches mirror Step 4.

### Step 7: Generate Images

1. Resolve the image backend via the Image Generation Tools rule at the top — ask once if multiple are installed.
   - **`codex-imagegen` invocation**: when the rule resolves to `codex-imagegen`, see [references/codex-imagegen.md](references/codex-imagegen.md) for the invocation contract (preferred `baoyu-image-gen --provider codex-cli` path, runtime wrapper discovery, parameter notes, stdout schema, batch semantics — n=1 per call so slide batches must dispatch one wrapper call per slide).
2. Confirm every `prompts/NN-slide-{slug}.md` exists (hard requirement; prompt files are the reproducibility record regardless of backend).
3. Session ID: `slides-{topic-slug}-{timestamp}` — pass to the backend only if it supports sessions.
4. Build a task list for selected slides with each slide's prompt file, output PNG path, aspect ratio, session ID, and verified direct references.
5. Dispatch slide images in batches per the `## Batch Generation Policy`: backend native batch first, runtime parallel tool calls second, sequential only as fallback. Backup rule applies to PNG files before dispatch. Report progress as `Generated X/N`. Retry only failed items once before reporting an error.

`--regenerate N` jumps to this step for the named slides only. `--images-only` starts here with existing prompts.

### Step 8: Merge

```bash
${BUN_X} {baseDir}/scripts/merge-to-pptx.ts <slide-deck-dir>
${BUN_X} {baseDir}/scripts/merge-to-pdf.ts <slide-deck-dir>
```

### Step 9: Summary

```
Slide Deck Complete!
Topic: [topic]
Style: [preset or "custom: texture+mood+typography+density"]
Location: [directory]
Slides: N

- 01-slide-cover.png
- ...
- NN-slide-back-cover.png

Outline: outline.md
PPTX: {topic-slug}.pptx
PDF: {topic-slug}.pdf
```

## Slide Modification

| Action | How |
|--------|-----|
| Edit | Update `prompts/NN-slide-{slug}.md` **first**, then `--regenerate N` |
| Add | Create new prompt at position, generate image, renumber subsequent `NN` (slugs unchanged), update `outline.md`, re-merge |
| Delete | Remove PNG + prompt, renumber subsequent, update `outline.md`, re-merge |

Always update the prompt file before regenerating the image — this keeps the prompts directory as the source of truth and makes changes reproducible. Only `NN` changes on renumber; slugs stay stable so references remain valid.

Text correction policy:

- If a slide's title, bullets, or any other rendered text is misspelled, garbled, hard to read, or visually weak, do not patch the bitmap with code.
- For text-correction regenerations, write a new prompt file and a new output path so the flawed candidate is preserved for comparison.
- Post-processing is limited to crop, resize, compression, or format conversion that does not alter text or the main composition.

See `references/modification-guide.md` for full details.

## References

| File | Content |
|------|---------|
| `references/confirmation.md` | Verbatim AskUserQuestion option copy for every confirmation |
| `references/analysis-framework.md` | Content analysis framework |
| `references/outline-template.md` | Outline structure |
| `references/base-prompt.md` | Base prompt body for image generation |
| `references/layouts.md` | Layout options |
| `references/design-guidelines.md` | Audience, typography, color selection |
| `references/content-rules.md` | Content guidelines |
| `references/modification-guide.md` | Edit/add/delete workflows |
| `references/styles/<preset>.md` | Per-preset specifications |
| `references/dimensions/*.md` | Per-dimension specifications |
| `references/config/preferences-schema.md` | EXTEND.md schema |

## Notes

- Image generation takes ~10-30s per slide; report progress between them.
- For sensitive public figures, prefer stylized alternatives to avoid likeness issues.
- Maintain visual consistency via the session ID when the backend supports it.

## Changing Preferences

EXTEND.md lives at the first matching path listed in Step 1.1. Two ways to change it:

- **Edit directly** — open EXTEND.md and change fields. Full schema: `references/config/preferences-schema.md`.
- **Common one-line edits**:
  - `preferred_image_backend: auto` — default; runtime-native tool wins, falls back to the only installed backend, asks only if multiple non-native are present.
  - `preferred_image_backend: codex-imagegen` — pin to Codex's built-in.
  - `preferred_image_backend: baoyu-image-gen` — pin to the baoyu-image-gen skill.
  - `preferred_image_backend: ask` — confirm backend every run.
  - `generation_batch_size: 4` — default number of slide images to render concurrently when the backend/runtime supports batch or parallel generation.
  - `preferred_style: blueprint`, `preferred_audience: experts`, `language: zh`.

## Script dependencies (first use)

The export scripts (`scripts/merge-to-pdf.ts`, `scripts/merge-to-pptx.ts`) need their npm dependencies. They are NOT shipped in the repo: on first use, run `npm install` in this skill's directory (a `package.json` is provided). If the scripts fail with a missing-module error, that install is the fix.
