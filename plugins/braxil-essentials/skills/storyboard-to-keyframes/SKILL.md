---
name: storyboard-to-keyframes
description: >
  Render a 4K KEYFRAME SHEET (a single composite IMAGE: a clean full-bleed grid of panels, each cell is the panel image edge-to-edge, with NO rendered numbers: the app's viewer overlays numbering) by composing the image-generation prompt (a single multi-section block tuned for a high-fidelity text-to-image model) and calling `generate_image`. The deliverable is the rendered image, never a raw prompt for the user to copy. This skill does NOT author or plan a story: the editable SOURCE storyboard is the `storyboard` JSON, and this skill renders that finished JSON into a visual sheet. THE CYCLE is always: storyboard → keyframes → video, do NOT skip the storyboard. If the user wants panels (or a video) for a multi-shot story but there is NO storyboard yet, author the `storyboard` FIRST; render straight from a bare idea (no storyboard) ONLY when the user EXPLICITLY asks for just the image/sheet and not a storyboard. Use ONLY when the user explicitly wants the VISUAL / IMAGE output: a "panel sheet", "keyframes", "panel layout", "render the storyboard as an image", "break this story into panels", panels they can SEE, or when they pair "storyboard" with any image / video generation tool or model, or upload character references for a visual. Do NOT use this skill for a bare "make me a storyboard" / "shot list" / "scene plan" with no mention of images: that is the storyboard JSON (`storyboard`), not this skill. Works for any visual style: 3D animation, live-action, anime, 2D animation, stop-motion, editorial, comic book, or any other aesthetic. To animate the approved sheet into the final video (per-clip prompt + rendering + timeline assembly), see `keyframes-to-video`.
---

# Storyboard → Keyframes

Story idea + character refs → **4K panel sheet**: one composite image, full-bleed grid (each cell = panel edge-to-edge; NO rendered numbers, viewer overlays its own). End-to-end: compose the image prompt AND call `generate_image`. Deliverable = rendered image, NOT a prompt to copy.

## ⛔ Style: use what the user gave, ask ONLY if genuinely missing

Style is a USER decision: NEVER infer from brand/topic/vibe (Chanel ≠ live-action luxury; Pokémon ≠ anime). "Don't infer" ≠ "always ask" (re-asking a given style is a bug). Use first explicit source: (1) anything the user said THIS conversation, any message; (2) storyboard `stylePrompt` NON-EMPTY = explicit upstream choice, USE it (EMPTY = missing); (3) brief / `# WORKING AREA`. Explicit anywhere → proceed, NO form. Raise `prompt_form` style picker (ANATOMY Step 1: 3 presets + custom + optional character-ref pickers + notes) ONLY when none is explicit. Same for character refs: pull from storyboard `references` / attachments; don't re-ask for a photo you have. Ask only genuine unknowns not readable from conversation / storyboard JSON / working area.

## Reference files (read, don't paraphrase)

On activation the runtime returns the skill's absolute `directory` + `resources`; read each as `<directory>/references/<file>` (or `list_skills` → `directory`). NEVER hardcode `~/.koi/skills/...` (dev checkout resolves to plugin repo path).
- **`references/STORYBOARD_ANATOMY.md`**: authoritative Phase 1 spec, **read FIRST**: 6 steps (gather inputs → analyse references → break story into beats → compose prompt sections A–H → `generate_image` 4K → companion note), grid chooser, per-section template, length targets, handling-variations table.
- **`references/STYLE_PRESETS.md`**: 3 presets (Premium 3D / Claymation / Realistic UGC), ready-to-paste section-B phrasing, + custom-style flow (anime, live-action, watercolor, cyberpunk…). POV is NOT a style: per-shot camera angle, combinable with any style.
- **`references/VIDEO_TYPE_<TYPE>.md`**: five (ad / explainer / tutorial / demo / social-post). Read ONLY the user-named `type` (brief-context note = internal, informs panels, NOT rendered; caption style; shot mix; audio cue). Never all five; skip if no type named.
- **Sheet FORMAT = section-E prose.** Full-bleed grid, panels edge-to-edge, thin black gutter lines only, NO numbers/labels, grid to all four margins. NOTHING else: no title banner, cards, drop shadows, caption bars, timecodes, number badges, footer/legend. (`references/LAYOUT_TEMPLATE.png` is DEAD, never attach it or any format reference.)
- **Render realistic human faces normally here** — as ordinary bare skin. (The Seedance face-filter workaround happens LATER in `keyframes-to-video`, right before the video render: each face panel is laundered through an exact Seedream copy, which clears the filter — not at panel-generation time.)

## ⚠ STAMP SOURCE-STORYBOARD METADATA: non-negotiable

GATE: every `generate_image` for a source storyboard MUST stamp `metadata.clips` (the panel→clip map) plus `sourceStoryboard` (abs JSON path), `sheetSetId` (VERSION LINK: pick ONE at run START, SAME on every part; new full render = NEW id, NEVER reuse; viewer groups by it), `storyboardPart`/`storyboardParts` (1-based SHEET index / total), `storyboardShotIds` (ALL shot ids on THIS sheet, union across clips), and `grid`. This lets downstream `keyframes-to-video` recover per-shot durations/dialogue/SFX exactly as set in the visor (else it guesses from pixels: bug). **Field semantics + the full `clips`/`metadata` shape live in ANATOMY → Chunking → Step B; read there, don't re-derive.** **Source = idea + refs only** (no JSON: first msg *"hazme un storyboard de X"* with refs/notes): instead pass `metadata: { storyboardOrigin: "idea" }`.

Never `generate_image` here without one shape. Downstream tools + `image-lineage` depend on it. Runtime logs a loud warning when a sheet call lacks both.

## Model

**Pass `label: "visual_storyboard"` in the `generate_image` call.** The router ranks any model carrying that catalog label first and picks it (e.g. GPT Image 2), which is the model curated for dense multi-panel sheets. If no model carries the label the router falls back on its own to a good 4K-capable text-to-image model, so the label is always safe to pass. Full sheets render at `resolution: "4k"`.

## High-level flow

Activate (remember the returned absolute directory) → `read_file` `STORYBOARD_ANATOMY.md` → `read_file` `STYLE_PRESETS.md` (chosen style's phrasing / custom flow) → `read_file` `VIDEO_TYPE_<TYPE>.md` IF a type is named else skip → follow ANATOMY's 6 steps verbatim → `generate_image` (`label: "visual_storyboard"`, `resolution: "4k"`, plus the `metadata` block) → show_result + companion note.

## 🛑 Multi-sheet = STRICTLY SEQUENTIAL, never parallel

>1 sheet (PARTs): render one at a time, in order, awaiting each: NEVER several `generate_image` in parallel/back-to-back. Each sheet K≥2 MUST carry prior approved sheets (PARTs 1…K-1) in `referenceImages` to lock identity; rendering before its predecessor exists → nothing to match → SAME actor, DIFFERENT FACE (bug). PART 1 → wait → `show_result` → PART 2 (PART 1 attached) → wait → … Exactly ONE in flight. Full rule: ANATOMY → "Cross-sheet referencing".

## 🔧 Fixing panels: virtual cells, direct replace, version history

Sheet = ONE image; panels = VIRTUAL cells (tools auto-detect grid from gutter lines, omit cols/rows). User can target any cuadros, incl. CROSS-PANEL refs ("fondo de 8 y 9 como el del 1").

> 🚫🔒 **A change is applied PANEL BY PANEL — the ONE exception is a change that affects EVERY panel.** Decide by how many panels the edit actually touches:
> - **Affects ALL panels of the sheet** (nothing on it is left unchanged) → this is the ONLY case you may re-render the whole sheet in a single `generate_image` EDIT pass (previous sheet as reference). There are no untouched panels to protect from drift, so one sheet-wide edit is acceptable.
> - **Affects a SUBSET — ONE panel or SEVERAL, but not all** (however "transversal" it feels: "vestido azul en los planos donde sale", "cambia el frasco en 3, 7 y 9", "luz más cálida en las tomas de interior") → **go PANEL BY PANEL**: `extract_panel` → `generate_image` EDIT → `replace_panel` for EACH affected panel, and leave every **unaffected panel BYTE-FOR-BYTE untouched** — do NOT extract, edit or replace them at all.
>
> **Why re-rendering the whole sheet for a SUBSET is FORBIDDEN:** `generate_image` EDIT over the full grid does NOT reproduce the untouched panels 1:1 — it silently re-draws EVERY cell, so panels you never wanted to change drift a little, and **each successive modification compounds that drift** (this is exactly the reported "cada modificación altera un poco la imagen" — unaffected panels keep degrading edit after edit). A subset change spanning N panels = **N independent per-panel edits** (fire the independent ones in parallel per §3b; chain a shared new element via §3b "Shared-change"), NEVER one sheet re-render.
>
> **Per-panel resolution (subset path) — size EACH panel INDEPENDENTLY; panels can have DIFFERENT resolutions.** For every affected panel, generate its edit at the LOWEST resolution tier that still covers THAT panel's own pixel size — the nearest tier **above** it — using the `width/height`/`aspectRatio` `extract_panel` returned for that specific panel. Compute it per panel (cell A might be 1100×760, cell B 900×900 → different tiers); never pick one blanket size for all, and NEVER `resolution:"4k"` / `quality:"high"` for a single panel (4k = full SHEETS only; a panel is downscaled into its cell anyway). See §3.
>
> (Separate case: a **STRUCTURAL** story change — shots/clips added, removed or reordered so the panel→clip mapping itself changed, gate 00 — is a **fresh render from the storyboard with a NEW `sheetSetId`**, not an "edit the old sheet" pass at all.)

> 🚨🔴 **A CHANGE TO THE SET / DÉCOR / BACKGROUND MUST REGENERATE THE SET PLATE — not just the panels. THIS IS THE HALF THAT GETS FORGOTTEN AND IT BREAKS THE VIDEO.**
>
> The set plate is a **PERSISTED reference** (`scene.references` / the `locations` Library asset), and `keyframes-to-video` **re-attaches it to Seedance on every clip**. So if you repaint the affected panels but leave the OLD plate in place, **the stale décor is what actually reaches the video**: the sheet looks correct, the user approves it, and then the render silently comes back with the set they just asked you to change. The panels are right and the video is wrong — and it looks like the video model ignored the brief when in fact you fed it the old room.
>
> **Order, always, no exceptions:**
> 1. **Regenerate the SET PLATE first**, with the change applied — same canonical wide view of the location, same `lighting` design as the rest of the piece.
> 2. **PERSIST it OVER the old one** (`save_storyboard` → `scene.references`, and/or update the `locations` Library asset). The superseded plate must no longer be reachable by any later run — a leftover old plate re-enters on the next regeneration/agenda run.
> 3. **THEN regenerate the affected panels**, anchored to the **NEW** plate (positional `Image N`), per the panel-by-panel rule above.
>
> **Same failure mode for the CAST — treat it identically.** A change to a character's look, wardrobe, hair or age must **regenerate that character's TURNAROUND (with Seedream) and persist it over the old one BEFORE fixing the panels**. Otherwise `keyframes-to-video` attaches the old turnaround and the video keeps the old identity, no matter how the panels look. **And for the EXTRAS too:** a recurring unnamed group (crowd, caravan, soldiers, crew…) has its own Seedream GROUP SHEET (Step 2b §1b) — a change to the group's look regenerates and persists THAT sheet first, same rule.
>
> Rule of thumb: **if a change outlives one panel, it lives in a reference — so fix the REFERENCE first, then the panels.**

**00. 🚦 STORY GATE FIRST: story or only pixels?** Storyboard JSON = SINGLE SOURCE OF TRUTH; sheets are derived, must NEVER contradict it.
- **VISUAL-ONLY** (render error: orientation, drifted background/set, proportions, character wrong, style glitch, `action`/`dialogue`/`continuity` stay TRUE) → panel flow; storyboard untouched.
- **STORY-AFFECTING** (WHAT happens, who appears, what's said, changing scene/setting, add/remove/reorder shots or clips, retiming) → FIRST update the storyboard (invoke `storyboard`, which chains `screenwriting` per its rule 1), THEN visuals: fix cuadros, or re-render affected sheet(s) with a NEW `sheetSetId` when structure changed (shot add/remove/reorder changes panel→clip mapping; single-panel fixes can't express that). Storyboard↔visual consistency ABSOLUTE.

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

- **`keyframes-to-video`** (downstream): after approval, composes the cinematic per-clip video prompt, renders each clip, assembles on a timeline.
