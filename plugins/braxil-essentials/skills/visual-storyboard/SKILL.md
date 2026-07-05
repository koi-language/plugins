---
name: visual-panels
description: >
  Render a 4K VISUAL PANEL SHEET (a single composite IMAGE: a clean full-bleed grid of panels, each cell is the panel image edge-to-edge, with NO rendered numbers: the app's viewer overlays numbering) by composing the image-generation prompt (a single multi-section block tuned for Nano Banana Pro / GPT Image 2) and calling `generate_image`. The deliverable is the rendered image, never a raw prompt for the user to copy. This skill does NOT author or plan a story: the editable SOURCE storyboard is the `interactive-storyboard` JSON, and this skill renders that finished JSON into a visual sheet. THE CYCLE is always: interactive storyboard → visual panels → video — do NOT skip the interactive storyboard. If the user wants panels (or a video) for a multi-shot story but there is NO storyboard yet, author the `interactive-storyboard` FIRST; render straight from a bare idea (no storyboard) ONLY when the user EXPLICITLY asks for just the image/sheet and not a storyboard. Use ONLY when the user explicitly wants the VISUAL / IMAGE output — a "panel sheet", "visual panels", "panel layout", "render the storyboard as an image", "break this story into panels", panels they can SEE — or when they pair "storyboard" with an image / video generation tool (Nano Banana Pro, GPT Image, Midjourney, DALL-E, Seedance, Kling, Sora, Veo, Runway, Luma, Hailuo, Wan, Higgsfield, Flux), or upload character references for a visual. Do NOT use this skill for a bare "make me a storyboard" / "shot list" / "scene plan" with no mention of images — that is the interactive JSON (`interactive-storyboard`), not this skill. Works for any visual style — 3D animation, live-action, anime, 2D animation, stop-motion, editorial, comic book, or any other aesthetic. To animate the approved sheet into the final video (per-clip prompt + rendering + timeline assembly), see `visual-panels-to-video`.
---

# Visual Panels

Turn a story idea + character references into a **4K visual panel sheet**: a single composite image, a clean full-bleed grid of panels (each cell is the panel image edge-to-edge; NO numbers are rendered: the app's viewer overlays its own numbering).

This skill is end-to-end — it composes the image prompt AND calls `generate_image` to render the sheet. **The deliverable is the rendered image, NOT a prompt string for the user to copy elsewhere.**

## ⛔ Style: USE what the user already gave you — ask ONLY when it's genuinely missing

The visual style is a USER decision — NEVER infer it from the brand, topic, or vibe (a Chanel storyboard is **not** automatically "live-action luxury"; a Pokémon one **not** "anime"; a kids' product **not** "3D family-film"). But "don't infer" does NOT mean "always ask". **First GATHER the style the user already provided; ask ONLY if none exists.** Re-asking for a style the user already gave is its own reported bug (*"¿por qué me vuelve a preguntar el estilo si ya se lo dije / si ya está en el storyboard?"*).

GATHER the style from ALL of these before deciding — use the first that is explicit:
1. **Anything the user said in THIS conversation** — not just their first/latest message. "en estilo anime", "fotorrealista", "como una peli", "el mismo estilo de antes" all count, wherever they said it.
2. **The source interactive storyboard's `stylePrompt`** — when NON-EMPTY it IS an explicit choice the user made upstream (the visor's style field). USE it; do NOT re-ask. (An EMPTY `stylePrompt` is the only "no choice" case → then style is genuinely missing.)
3. **The brief / `# WORKING AREA`** context the user pointed you at.

If an explicit style exists in ANY of the above → proceed with it, NO form. Raise the `prompt_form` style picker (Step 1 of `STORYBOARD_ANATOMY.md`: the 3 presets + custom + optional character-ref pickers + notes) ONLY when NONE of the sources carry an explicit style.

**Same rule for character references** — pull them from the storyboard's `references` / the user's attachments; do NOT re-ask for a photo you already have (see INPUTS). General principle: **STOP asking for anything you can already read from the conversation, the storyboard JSON, or the working area — ask only the genuine unknowns.**

## This skill's reference files (read them, don't paraphrase from memory)

The authoritative specs live in this skill's own `references/` directory. When the skill is activated, the runtime returns the skill's absolute `directory` plus a `resources` list — read each file from `<that directory>/references/<file>` (or `list_skills` → this skill's `directory`). NEVER hardcode `~/.koi/skills/...`; in a dev checkout the skill resolves to the plugin repo path, so always use the activation-returned directory.

- **`references/STORYBOARD_ANATOMY.md`** — the authoritative Phase 1 spec. The 6 steps (gather inputs → analyse references → break the story into beats → compose the prompt with sections A–H → call `generate_image` at 4K → companion note), the grid chooser, the per-section prompt template, the length targets, and the handling-variations table. **Read this first** before writing any prompt; the SKILL.md you're reading right now is just the entrypoint.
- **`references/STYLE_PRESETS.md`** — the 3 official visual style presets (Premium 3D / Claymation / Realistic UGC) with ready-to-paste phrasing blocks for section B of the prompt, plus the custom-style flow for anything else (anime, live-action, watercolor, cyberpunk, …). POV is **not** a style here — it's a per-shot camera angle that combines with any of the styles.
- **`references/VIDEO_TYPE_<TYPE>.md`** — five per-type spec files (ad / explainer / tutorial / demo / social-post). Read ONLY the one matching the user-named `type` for its brief-context note (internal — informs the panels, NOT rendered), the caption style, the shot mix and the audio cue. Never read all five. Skip entirely when the user didn't name a video type.
- **Sheet FORMAT lives in the prose of section E.** The deliverable is a clean **full-bleed grid**: each panel's image fills its cell edge-to-edge, panels separated ONLY by thin black gutter lines, NO rendered numbers or labels, and the grid runs to all four margins. NOTHING else: no title banner, no cards, no drop shadows, no caption bars, no timecodes, no number badges, no footer/legend. See STORYBOARD_ANATOMY.md → section E for the exact wording. (`references/LAYOUT_TEMPLATE.png` is dead: the format used to be copied from that attached skeleton, do NOT attach it or any other format reference.)

## ⚠ STAMP THE SOURCE-STORYBOARD METADATA — non-negotiable

Every `generate_image` call this skill makes MUST carry `metadata` that declares where the sheet came from. This is what lets the downstream `visual-panels-to-video` skill recover per-shot durations / dialogue / SFX exactly as the user set them in the visor — without this link the next step has to guess from pixels and may confabulate (the reported bug *"de repente cambia de tema, era un viejo con un reloj y dijo que era SOC 2"*).

Two cases, ONE field. Pick the right one and ALWAYS pass it:

- **Source = interactive storyboard JSON** (most common — the user has a storyboard open in the visor and asked to render it visually):
  ```
  metadata: {
    sourceStoryboard: "/Users/.../.koi/storyboards/<id>.json",  // ← absolute path
    sheetSetId: "<storyboard-id>-<unix-ms>",  // VERSION LINK: pick ONE id at the START of the
                                 // render run (e.g. the storyboard id + a timestamp you fix once)
                                 // and stamp the SAME value on EVERY part of this run. A new
                                 // full render = a NEW sheetSetId. The panels viewer groups by
                                 // this field so part 1 of a new version is NEVER mixed with
                                 // part 2 of an old one. NEVER reuse a previous run's id.
    storyboardPart: K,           // 1-based SHEET index (1 if single-sheet)
    storyboardParts: K_total,    // total SHEETS (1 if single-sheet)
    storyboardShotIds: ["sh1","sh2", …],  // ALL shot ids on THIS sheet (union across its clips)
    grid: { cols: 3, rows: 4 },  // the grid YOU chose for this sheet (free choice; keeping
                                 // cells near the video aspect is just the recommended default).
                                 // A hint for the panels viewer; the panel tools auto-detect the
                                 // real grid from the pixels regardless
    // panel→clip map — a sheet can hold several clips; this is what lets
    // visual-panels-to-video render one generate_video per clip from the
    // right panels. clipIndex is GLOBAL (1-based, timeline order across sheets).
    // See references/STORYBOARD_ANATOMY.md → Chunking → Step B.
    clips: [
      { clipIndex: 1, shotIds: ["sh1","sh2"], panels: [1,2,3], durationSec: 12 },
      { clipIndex: 2, shotIds: ["sh3"],        panels: [4,5],   durationSec: 8  }
    ]
  }
  ```
  You already `read_file`d the JSON to compose the prompt — its absolute path is what you pass.

- **Source = idea + refs only** (no JSON, the user's first message was *"hazme un storyboard de X"* with refs / notes, never an interactive JSON):
  ```
  metadata: {
    storyboardOrigin: "idea"
  }
  ```
  Explicit declaration that there is no JSON to link to — keeps audit trail clean.

**Never call `generate_image` from this skill without one of those two `metadata` shapes.** Both downstream tools and `image-lineage` notes depend on this. The runtime now logs a loud warning when this skill's call signature (`label: "visual_storyboard"`) is missing both — don't ignore the warning, fix the call.

## High-level flow

1. **Activate this skill.** The runtime returns the absolute directory; remember it for the reads below.
2. **`read_file` `references/STORYBOARD_ANATOMY.md`.** That's the spec — every step you need is there.
3. **`read_file` `references/STYLE_PRESETS.md`** to grab the phrasing block for the chosen style (or follow the custom-style flow there for anything outside the 3 presets).
4. **`read_file` `references/VIDEO_TYPE_<TYPE>.md`** IF the user named a video type. Skip otherwise.
5. **Follow STORYBOARD_ANATOMY's 6 steps verbatim:** gather inputs → analyse references → break the story into beats → compose the prompt → call `generate_image` (with `resolution: "4k"` AND the `metadata` block above — both mandatory) → show_result + companion note.

That's it. The detail lives in `STORYBOARD_ANATOMY.md`. Don't re-derive it here.

## 🛑 Multi-sheet = STRICTLY SEQUENTIAL, NEVER parallel

When a storyboard needs more than ONE 4K sheet (chunked into PARTs), render the sheets **one at a time, in order, awaiting each before the next** — NEVER fire several `generate_image` calls in parallel or back-to-back. Each sheet K ≥ 2 MUST carry the prior approved sheets (PARTs 1…K-1) in `referenceImages` to lock identity; a sheet that renders before its predecessor exists has nothing to match, so the SAME actor comes out with a DIFFERENT FACE on each sheet (the reported bug). Render PART 1 → wait → `show_result` → PART 2 (with PART 1 attached) → wait → … Exactly ONE sheet in flight at any moment. Do NOT announce or do "parallel generation of the N pages"; do "one sheet at a time, each using the previous as reference". Full rule in `STORYBOARD_ANATOMY.md` → "Cross-sheet referencing".

## 🔧 Fixing panels: virtual panels, direct replace, version history

The sheet is ONE image; its panels are VIRTUAL cells (the tools AUTO-DETECT the real grid from the gutter lines: omit cols/rows). The user can ask for anything against specific cuadros, including CROSS-PANEL references ("pon el fondo de los cuadros 8 y 9 como el del cuadro 1"). Flow:

00. **🚦 STORY GATE FIRST: does this change affect the STORY, or only the pixels?** The interactive storyboard JSON is the SINGLE SOURCE OF TRUTH; sheets are derived renders and must NEVER contradict it. Classify the request before touching anything:
   - **VISUAL-ONLY fix** (a render error: wrong orientation, drifted background/set, proportions, a character looking wrong, style glitch: the storyboard's `action`/`dialogue`/`continuity` remain TRUE as written) -> proceed with the panel flow below; the storyboard stays untouched.
   - **STORY-AFFECTING change** (WHAT happens, who appears, what is said, changing a scene or setting, adding/removing/reordering shots or clips, retiming): **FIRST update the interactive storyboard** (invoke `interactive-storyboard`, which chains `screenwriting` per its own rule 1) so the JSON reflects the new truth, **THEN** update the visual side: fix the affected cuadros via the panel flow, or re-render the affected sheet(s) with a NEW `sheetSetId` when the structure changed (shots added/removed/reordered change the panel->clip mapping and single-panel fixes cannot express that). Consistency between the interactive storyboard and the visual panels is ABSOLUTE: never leave a sheet telling a story its storyboard no longer tells.
0. **RESOLVE THE NUMBERS FIRST: the user's "cuadro/diapositiva N" is the GLOBAL slide number of the panels viewer, sequential across ALL PART sheets.** It is NOT the per-sheet panel number (historic sheets carried baked-in per-sheet numerals restarting at 1 per PART; new sheets carry none) and NEVER a storyboard scene or shot number: do not map "diapositiva 8" to sh8/escena 3. Compute the mapping mechanically: order the storyboard's sheets by `storyboardPart` (latest `sheetSetId` batch only), count each sheet's panels from its `metadata.clips` (union of `panels`), and walk cumulatively: global 8 with an 11-panel PART 1 = sheet 1, panel 8; global 15 = sheet 2, panel 4. When the GUI's working-area context already provides the cuadro->sheet/panel mapping, use it verbatim. If the request is ambiguous after this (e.g. numbers beyond the total), ask; never guess a different scene.
1. `extract_panel { sheet, panel: N }` for EVERY panel involved: the ones to fix AND the ones used as reference (e.g. panel 1 for its background). Each returns a temp working copy plus its `width/height/aspectRatio`.
2. `read_file` each working copy (see them; unlocks them as generation references). If the GUI opened an annotated copy in the work area, re-read the ANNOTATED file right before generating: marks are instructions, never content.
3. `generate_image` in EDIT mode per panel to fix: the panel's working copy FIRST, then the reference panels/character/set refs, with a forensic super-description and the instruction to change ONLY what was asked, preserving style, palette and framing, and rendering NO numbers or labels (legacy panels may carry a baked-in numeral: remove it if the edit touches that corner, keep the panel otherwise clean). **🔥 DIMENSIONS ARE SACRED: the candidate MUST come back at the SAME dimensions/aspect as the extracted working copy (pass the `aspectRatio` that extract_panel returned; the engine also auto-detects it from the first reference when omitted). `replace_panel` REJECTS aspect mismatches. And match the SIZE, not just the shape: a cell is ~1MP (e.g. 1100x760), so pass the LOWEST resolution tier that covers it and normal quality: NEVER `resolution: "4k"` or `quality: high` for a single panel (it burns credits and time and gets downscaled on composite anyway; 4k is for full SHEETS only).** This rule is generic: ANY image edit keeps the original's dimensions unless the user explicitly asks otherwise.
3b. **SCHEDULING: parallel, sequential, or a mix, decided by the DEPENDENCY GRAPH.** Before generating, classify each panel edit by its inputs:
   - **Independent edits** (each panel's inputs are only EXISTING images: its own working copy, already-extracted reference panels, character/set refs) -> generate them IN PARALLEL. Extract everything first, then fire the generate_image calls together.
   - **Dependent edits** (a panel's input includes the RESULT of another edit) -> SEQUENTIAL: generate the prerequisite, read it, then generate the dependent one with it as reference.
   - **Shared-change edits** (several panels must receive the SAME new element, e.g. "el fondo de 8 y 9 como el del 1"): even though they look independent, generating them in parallel lets each one reinterpret the change and they DRIFT from each other. Chain them: fix the FIRST panel, then pass the CORRECTED first panel as an extra reference when fixing the rest, so all changed panels match each other (same rule as the strictly-sequential multi-sheet renders). Mixes are normal: two independent groups can run in parallel while each group chains internally.
3c. **Metadata for panel-fix generations (NOT the sheet stamp).** These generate_image calls must NOT carry the sheet metadata shape (no `clips`, no `grid`, no `storyboardPart/Parts`): stamp instead `metadata: { panelFix: true, sheet: <abs sheet path>, panel: N, sourceStoryboard: <abs json path> }`. A panel-fix image stamped like a sheet gets opened by the panels viewer as a 12-cell hoja and sliced into nonsense (reported bug). And do NOT `show_result` the intermediate panel image: the viewer refreshes the fixed slide alone after replace_panel; report in one line instead.
4. `read_file` each result and verify it (content AND dimensions).
5. **Replace DIRECTLY: `replace_panel { sheet, panel: N, image }`. Do NOT ask for confirmation.** Every replacement automatically records the panel's VERSION HISTORY (the original cell is version 1; the new one becomes current). The user sees versions in the panels viewer and can restore or delete them there, or ask you to (`panel_versions` op list/restore/delete). History is the safety net; asking first is the anti-pattern now.
6. `read_file` the sheet to confirm the composite. The viewer refreshes alone. Report which cuadros changed, one line.

**DELETING a cuadro ("elimina el 18"):** this is always STORY-AFFECTING (gate 00): (1) update the interactive storyboard first (remove the shot); (2) propagate with `delete_panel { sheet, panel }`: it SHIFTS every later panel one cell back mechanically (free, no regeneration), blackens the last cell and re-indexes the sheet's clips metadata. NEVER paint the deleted cuadro black in place and NEVER regenerate the sheet just for a deletion. Panels never flow between sheets: each sheet simply ends with one more bare black cell.

Regenerating the WHOLE sheet to fix panels is the anti-pattern: it re-rolls every panel that was right. Only re-render the full sheet for a global change (style, story, layout), stamping a NEW `sheetSetId`.

## Pairs with

- **`visual-panels-to-video`** (downstream) — once the user approves the sheet, this skill composes the cinematic per-clip video prompt, renders each clip, and assembles them on a timeline.
