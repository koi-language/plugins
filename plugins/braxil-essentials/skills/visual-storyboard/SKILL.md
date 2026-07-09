---
name: visual-panels
description: >
  Render a 4K VISUAL PANEL SHEET (a single composite IMAGE: a clean full-bleed grid of panels, each cell is the panel image edge-to-edge, with NO rendered numbers: the app's viewer overlays numbering) by composing the image-generation prompt (a single multi-section block tuned for Nano Banana Pro / GPT Image 2) and calling `generate_image`. The deliverable is the rendered image, never a raw prompt for the user to copy. This skill does NOT author or plan a story: the editable SOURCE storyboard is the `interactive-storyboard` JSON, and this skill renders that finished JSON into a visual sheet. THE CYCLE is always: interactive storyboard → visual panels → video, do NOT skip the interactive storyboard. If the user wants panels (or a video) for a multi-shot story but there is NO storyboard yet, author the `interactive-storyboard` FIRST; render straight from a bare idea (no storyboard) ONLY when the user EXPLICITLY asks for just the image/sheet and not a storyboard. Use ONLY when the user explicitly wants the VISUAL / IMAGE output: a "panel sheet", "visual panels", "panel layout", "render the storyboard as an image", "break this story into panels", panels they can SEE, or when they pair "storyboard" with an image / video generation tool (Nano Banana Pro, GPT Image, Midjourney, DALL-E, Seedance, Kling, Sora, Veo, Runway, Luma, Hailuo, Wan, Higgsfield, Flux), or upload character references for a visual. Do NOT use this skill for a bare "make me a storyboard" / "shot list" / "scene plan" with no mention of images: that is the interactive JSON (`interactive-storyboard`), not this skill. Works for any visual style: 3D animation, live-action, anime, 2D animation, stop-motion, editorial, comic book, or any other aesthetic. To animate the approved sheet into the final video (per-clip prompt + rendering + timeline assembly), see `visual-panels-to-video`.
---

# Visual Panels

Story idea + character refs → **4K panel sheet**: one composite image, full-bleed grid (each cell = panel edge-to-edge; NO rendered numbers, viewer overlays its own). End-to-end: compose the image prompt AND call `generate_image`. Deliverable = rendered image, NOT a prompt to copy.

## ⛔ Style: use what the user gave, ask ONLY if genuinely missing

Style is a USER decision: NEVER infer from brand/topic/vibe (Chanel ≠ live-action luxury; Pokémon ≠ anime). "Don't infer" ≠ "always ask" (re-asking a given style is a bug). Use first explicit source: (1) anything the user said THIS conversation, any message; (2) storyboard `stylePrompt` NON-EMPTY = explicit upstream choice, USE it (EMPTY = missing); (3) brief / `# WORKING AREA`. Explicit anywhere → proceed, NO form. Raise `prompt_form` style picker (ANATOMY Step 1: 3 presets + custom + optional character-ref pickers + notes) ONLY when none is explicit. Same for character refs: pull from storyboard `references` / attachments; don't re-ask for a photo you have. Ask only genuine unknowns not readable from conversation / storyboard JSON / working area.

## Reference files (read, don't paraphrase)

On activation the runtime returns the skill's absolute `directory` + `resources`; read each as `<directory>/references/<file>` (or `list_skills` → `directory`). NEVER hardcode `~/.koi/skills/...` (dev checkout resolves to plugin repo path).
- **`references/STORYBOARD_ANATOMY.md`**: authoritative Phase 1 spec, **read FIRST**: 6 steps (gather inputs → analyse references → break story into beats → compose prompt sections A–H → `generate_image` 4K → companion note), grid chooser, per-section template, length targets, handling-variations table.
- **`references/STYLE_PRESETS.md`**: 3 presets (Premium 3D / Claymation / Realistic UGC), ready-to-paste section-B phrasing, + custom-style flow (anime, live-action, watercolor, cyberpunk…). POV is NOT a style: per-shot camera angle, combinable with any style.
- **`references/VIDEO_TYPE_<TYPE>.md`**: five (ad / explainer / tutorial / demo / social-post). Read ONLY the user-named `type` (brief-context note = internal, informs panels, NOT rendered; caption style; shot mix; audio cue). Never all five; skip if no type named.
- **Sheet FORMAT = section-E prose.** Full-bleed grid, panels edge-to-edge, thin black gutter lines only, NO numbers/labels, grid to all four margins. NOTHING else: no title banner, cards, drop shadows, caption bars, timecodes, number badges, footer/legend. (`references/LAYOUT_TEMPLATE.png` is DEAD, never attach it or any format reference.)

## ⚠ STAMP SOURCE-STORYBOARD METADATA: non-negotiable

GATE: every `generate_image` for a source storyboard MUST stamp `metadata.clips` (the panel→clip map) plus `sourceStoryboard` (abs JSON path), `sheetSetId` (VERSION LINK: pick ONE at run START, SAME on every part; new full render = NEW id, NEVER reuse; viewer groups by it), `storyboardPart`/`storyboardParts` (1-based SHEET index / total), `storyboardShotIds` (ALL shot ids on THIS sheet, union across clips), and `grid`. This lets downstream `visual-panels-to-video` recover per-shot durations/dialogue/SFX exactly as set in the visor (else it guesses from pixels: bug). **Field semantics + the full `clips`/`metadata` shape live in ANATOMY → Chunking → Step B; read there, don't re-derive.** **Source = idea + refs only** (no JSON: first msg *"hazme un storyboard de X"* with refs/notes): instead pass `metadata: { storyboardOrigin: "idea" }`.

Never `generate_image` here without one shape. Downstream tools + `image-lineage` depend on it. Runtime logs a loud warning when this skill's call (`label: "visual_storyboard"`) lacks both.

## High-level flow

Activate (remember the returned absolute directory) → `read_file` `STORYBOARD_ANATOMY.md` → `read_file` `STYLE_PRESETS.md` (chosen style's phrasing / custom flow) → `read_file` `VIDEO_TYPE_<TYPE>.md` IF a type is named else skip → follow ANATOMY's 6 steps verbatim → `generate_image` (`resolution: "4k"` AND the `metadata` block, both mandatory) → show_result + companion note.

## 🛑 Multi-sheet = STRICTLY SEQUENTIAL, never parallel

>1 sheet (PARTs): render one at a time, in order, awaiting each: NEVER several `generate_image` in parallel/back-to-back. Each sheet K≥2 MUST carry prior approved sheets (PARTs 1…K-1) in `referenceImages` to lock identity; rendering before its predecessor exists → nothing to match → SAME actor, DIFFERENT FACE (bug). PART 1 → wait → `show_result` → PART 2 (PART 1 attached) → wait → … Exactly ONE in flight. Full rule: ANATOMY → "Cross-sheet referencing".

## 🔧 Fixing panels: virtual cells, direct replace, version history

Sheet = ONE image; panels = VIRTUAL cells (tools auto-detect grid from gutter lines, omit cols/rows). User can target any cuadros, incl. CROSS-PANEL refs ("fondo de 8 y 9 como el del 1").

**00. 🚦 STORY GATE FIRST: story or only pixels?** Storyboard JSON = SINGLE SOURCE OF TRUTH; sheets are derived, must NEVER contradict it.
- **VISUAL-ONLY** (render error: orientation, drifted background/set, proportions, character wrong, style glitch, `action`/`dialogue`/`continuity` stay TRUE) → panel flow; storyboard untouched.
- **STORY-AFFECTING** (WHAT happens, who appears, what's said, changing scene/setting, add/remove/reorder shots or clips, retiming) → FIRST update the storyboard (invoke `interactive-storyboard`, which chains `screenwriting` per its rule 1), THEN visuals: fix cuadros, or re-render affected sheet(s) with a NEW `sheetSetId` when structure changed (shot add/remove/reorder changes panel→clip mapping; single-panel fixes can't express that). Interactive↔visual consistency ABSOLUTE.

**0. RESOLVE NUMBERS FIRST.** "cuadro/diapositiva N" = GLOBAL viewer slide number, sequential across ALL PART sheets. NOT the per-sheet panel number (historic sheets baked numerals restarting at 1 per PART; new ones none) and NEVER a scene/shot number. Compute mechanically: order sheets by `storyboardPart` (latest `sheetSetId` batch only), count each sheet's panels from `metadata.clips` (union of `panels`), walk cumulatively (global 8, 11-panel PART 1 = sheet 1 panel 8). If GUI working-area gives the mapping, use verbatim. Ambiguous → ask, never guess.

**1.** `extract_panel { sheet, panel: N }` for EVERY panel involved: to fix AND used as reference. Returns temp working copy + `width/height/aspectRatio`.

**2.** `read_file` each copy (unlocks as gen refs). If GUI opened an annotated copy, re-read the ANNOTATED file right before generating: marks are instructions, not content.

**3.** `generate_image` EDIT mode per panel: working copy FIRST, then reference panels/character/set refs, forensic super-description + instruction to change ONLY what was asked, preserving style/palette/framing, NO numbers/labels (legacy baked numeral: remove if the edit touches that corner, else keep). **🔥 DIMENSIONS SACRED: candidate MUST return SAME dimensions/aspect as the extracted copy**: pass the `aspectRatio` extract_panel returned (engine auto-detects from first ref if omitted); `replace_panel` REJECTS aspect mismatches. Match SIZE: cell ~1MP (e.g. 1100x760) → LOWEST resolution tier covering it + normal quality; NEVER `resolution: "4k"` / `quality: high` for one panel (downscaled anyway; 4k = full SHEETS only). Generic: any edit keeps original dimensions unless user asks otherwise.

**3b. SCHEDULING by DEPENDENCY GRAPH.**
- **Independent** (inputs only EXISTING images: own copy, extracted refs, character/set refs) → PARALLEL: extract all first, fire together.
- **Dependent** (input includes another edit's RESULT) → SEQUENTIAL: generate prerequisite, read it, then the dependent with it as ref.
- **Shared-change** (several panels get the SAME new element) → parallel drifts; chain: fix FIRST, pass the CORRECTED first as extra ref for the rest. Mixes normal: independent groups parallel, each chaining internally.

**3c. Panel-fix metadata (NOT the sheet stamp).** No `clips`/`grid`/`storyboardPart/Parts`; stamp `metadata: { panelFix: true, sheet: <abs sheet path>, panel: N, sourceStoryboard: <abs json path> }` (a panel-fix stamped as a sheet gets sliced into a 12-cell hoja: bug). Do NOT `show_result` the intermediate image (viewer refreshes the fixed slide alone after replace_panel), report one line.

**4.** `read_file` each result; verify content AND dimensions.

**5. Replace DIRECTLY: `replace_panel { sheet, panel: N, image }`: NO confirmation.** Auto-records VERSION HISTORY (original = version 1; new = current). User restores/deletes in viewer, or asks you (`panel_versions` op list/restore/delete). Asking first is the anti-pattern.

**6.** `read_file` the sheet to confirm the composite (viewer refreshes alone). Report changed cuadros, one line.

**DELETING a cuadro**: always STORY-AFFECTING (gate 00): (1) update storyboard first (remove shot); (2) `delete_panel { sheet, panel }`: SHIFTS every later panel one cell back (free, no regen), blackens the last cell, re-indexes clips metadata. NEVER paint black in place; NEVER regenerate the sheet for a deletion. Panels never flow between sheets: each ends with one more bare black cell.

Regenerating the WHOLE sheet to fix panels = anti-pattern (re-rolls correct panels). Full-render only for a global change (style/story/layout), stamping a NEW `sheetSetId`.

## Pairs with

- **`visual-panels-to-video`** (downstream): after approval, composes the cinematic per-clip video prompt, renders each clip, assembles on a timeline.
