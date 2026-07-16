---
name: visual-panels-to-video
description: Turning one or more approved VISUAL panels sheets (the 4K panel-grid images built by the `visual-panels` skill) into the FINAL video. Takes the sheet images, an optional references manifest (characters / products / settings to lock identity), and (when available) the storyboard JSON (the authority for per-clip timing, per-shot action, dialogue, SFX and music). Composes a COMPACT per-clip video prompt for each clip, renders one video per CLIP: a clip is a group of consecutive panels (e.g. panels 4–7), and a single sheet can hold several clips (see each sheet's `metadata.clips`), with each clip's duration driven by the storyboard when present, generates a single music track when needed, and assembles every clip back-to-back on a timeline into one continuous video. Use whenever you have approved panel sheets and need the rendered video (e.g. Step 4 of the create-video workflow). Pairs with `visual-panels` (its upstream) and `timeline-assembler` (which it delegates assembly to).
---

OUTPUT stage: `visual-panels` produced the approved 4K sheet(s); this skill **composes the video prompt AND renders** each clip, then stitches all into the final film. Assembly mechanics (track layout, fps/aspect inheritance, music ducking, transitions, subtitles, preview handoff) are delegated to **`timeline-assembler`**: read its SKILL.md before assembling, don't re-derive.

## 🛑 STEP 0: RECOVER + READ THE STORYBOARD JSON FIRST (MANDATORY, before any `generate_video`)
The sheet is NOT the script, the storyboard JSON is. Never infer the scene from sheet pixels when a `sourceStoryboard` exists (reported bug: hallucinated "vending machine" for a man-on-a-sofa storyboard).
1. Recover via `inspect_creation({ filePath: "<sheet path>" })` → `creation.metadata.sourceStoryboard` → `read_file` THAT JSON (AUTHORITY for premise, per-shot action, timing, continuity, dialogue, audio). **When you read it, read the CONTINUITY MATRIX too** — the per-shot `continuity` rows `{ characters, objects, place }` + the story-wide `continuity` LOCK. Hold it in mind for every clip: it drives what state you must restate in each Seedance shot line (see "🎬 READ THE CONTINUITY MATRIX FIRST" in STEP B). It is not optional colour, it is the raccord authority.
2. NEVER pass the SHEET as `startFrame`, it's `referenceImages` (look/identity) only.
3. NEVER skip to a raw `generate_video` off pixels + invented prompt; compose FROM the JSON, shot by shot.
4. Fall back to sheet pixels ONLY when `inspect_creation` returns no `sourceStoryboard`. Never ask the user to name the project.

## INPUTS
From the task description, or `step5_output.json` (create-video workflow):
- **`sheets`**: ORDERED list of approved sheet images (PART 1…N), absolute paths. Required. **Resolving when not given an explicit list** (ad-hoc "genera el vídeo"): a session holds SEVERAL videos; most-recent-on-disk is often the WRONG project (bug: rendered horse project instead of Star Wars). Resolve scoped, never by recency: target = ACTIVE doc in `# WORKING AREA`, take its `id`; `recall_creations({ kind: 'image', storyboard: '<id>' })` → only sheets whose `metadata.sourceStoryboard` ties to it, ordered by `storyboardPart`. 🚫 NEVER "most recent", `ls`/`shell` the images dir, or mix storyboards. No active storyboard / spans >1 / empty → STOP and ask which to render (offer candidates by name).
- **`references`**: OPTIONAL manifest of recurring subjects, each `{ alias: path-or-@handle }`, e.g. `{ hero_character: "/…/leo.png", product_pack: "@acme_bottle" }`. ⚠️ On the **Seedance reference-to-video + storyboard** path (the default) you do NOT attach these — the panel sheet already carries identity, and each clip attaches only its own sheet + the previous clip (STEP B). This manifest is for OTHER-model paths whose technique needs explicit identity refs; there, pass the in-scope refs (shot+scene+storyboard, resolving `@handle` → path) into `referenceImages`.
- **`storyboard_path`**: path to `~/.koi/storyboards/<id>.json`. When present = AUTHORITY for: per-shot `duration`, `action`, `continuity` = { characters, objects } (legacy: single `state` string), `dialogue`, `sfx`/`music`/`audio`, plus storyboard-level `synopsis` (premise), `continuity` (LOCK = story-wide invariants/negatives), `characters`, `lighting`, `aspect`. Prefer over sheet pixels; transcribe `synopsis` + LOCK + per-shot `continuity`, don't drop. **Recovery (NEVER ask the user which storyboard, asking is the bug):** (1) `inspect_creation({ filePath: "<sheet abs path>" })`: MANDATORY; `metadata.sourceStoryboard` = ABSOLUTE PATH (+ `storyboardPart`/`storyboardParts`); ⚠️ `read_file` returns PIXELS not this. Hit → `read_file` THAT JSON. (2) Only if no `sourceStoryboard` → fall back to sheet pixels (`read_file` PNG; vision returns panels/captions/banner/timecodes → derive durations/beats). ⛔ DO NOT filesystem-search for a "matching" JSON (no `shell ls .koi/storyboards/`, `recall_creations` to "find" it, reading every JSON and guessing): confabulation bug matched `soc2_compliance_explainer.json` to a pocket-watch story. Metadata is the ONLY sheet→JSON link; no metadata = no JSON → use pixels. Neither metadata nor legible pixels → surface via a single `print` (not blocking), proceed best-effort; never invent the link.
- **`audio_plan` / `type` / `aspect_ratio` (platform)**: OPTIONAL (music need+brief, video type, destination aspect). Pre-resolved in `step5_output.json`.
- **`targetGenerator`**: OPTIONAL (Seedance/Kling/Sora/Veo/Runway/Luma/Hailuo/Wan/Higgsfield); tailor camera + pacing. Absent → model-agnostic.

`sheets` missing/empty → surface the error.

## STEP A: Enumerate the CLIPS and resolve each clip's duration
**A sheet is NOT a clip.** `visual-panels` packs multiple clips per sheet in **`metadata.clips`**: `[{ clipIndex, shotIds, panels, durationSec }, …]`. Read every sheet's `metadata.clips` (via `inspect_creation`), concatenate, sort by global `clipIndex` → render plan. **One `generate_video` per CLIP**, in `clipIndex` order across ALL sheets, NOT per sheet. Fallback (old sheets, no `metadata.clips`): whole sheet = one clip.

**Duration range: read from the tool, never hardcode:** `get_tool_info("generate_video")` → `duration` schema (typical whole seconds [4,15] + `"auto"`; trust the tool). Use `D_min`/`D_max`. Resolve per clip, priority: (1) **`clip.durationSec`** (PREFERRED): clamp to `[D_min,D_max]`; with the JSON cross-check == sum of its `shotIds`' `shot.duration`; (2) no JSON → sheet pixels: sum per-panel timecodes for total `S`, or use banner total (`PART K: … (<n> frames · <S> s total)`), clamp `S` to a whole second in `[D_min,D_max]`; (3) neither → `D_max` AND surface uncertainty via `print`.

NEVER hardcode `duration: 15` when the storyboard says otherwise. State per-clip durations before rendering (*"3 clips: PART 1 → 14 s, PART 2 → 10 s, PART 3 → 10 s"*). ⚠ **The storyboard total overrides any duration in the task/brief** (task "60 s" but storyboard sums 48 s → video is 48 s; don't pad/stretch/add filler). Sole exception: explicit hard-target ("must stay exactly 60 s") → refit.

### ⛔ Fail-fast: a single CLIP > 15 s is malformed (a sheet may exceed 15 s, fine)
Sanity-check EACH clip (`durationSec` or summed `shot.duration`). Any clip > 15 s (or no `metadata.clips` AND whole sheet's shots sum > 15 s) → upstream chunking bug; don't silently drop shots (*"hizo los 15 s pero solo de una parte"* bug). STOP: *"Clip `<clipIndex>` sums to `<X>` s but a rendered clip caps at 15 s. Please re-build the sheets with `visual-panels`: its Chunking step splits shots into ≤15 s clips I'll then render and concatenate."* Never auto-compress/truncate.

## STEP B: Render one `generate_video` per CLIP (a group of consecutive panels, e.g. 4–7 → ONE video), SEQUENTIALLY with clip-chaining
> 🛑 BEFORE the first `generate_video`, in this order: (1) activate the `video-generator` skill (MANDATORY for any video generation — how the tool + each model's params work); (2) choose the video MODEL (see "Model choice"); (3) if that model has a dedicated craft skill, activate it. Don't skip to a self-written brief, and don't commit to a model's craft skill before `video-generator` is active.

Unit = **clip** = a GROUP of consecutive panels (`metadata.clips[].panels`). `[4,5,6,7]` → ONE video for panels 4–7. NOT per panel; NOT per sheet (a 12-panel sheet may be 3 clips → 3 videos, e.g. 1–4/5–9/10–12).

**Several panels can be ONE shot (one take, no internal cut): animate THROUGH.** Two cases, same handling: (a) a camera-move shot's 2-3 keyframe panels (share `shotId`) = start/middle/end of one move; (b) consecutive shots flagged `noCutBefore` (or sharing `number`) = glued plano secuencia. Both → ONE SHOT line that cites the whole panel range, moving smoothly, NO internal cut. A real cut (a new SHOT line) falls ONLY where the JSON is NOT glued. So **the number of shots in a clip = number of takes, not number of panels.**

**Render SEQUENTIALLY, not parallel**: each clip continues from the one before it, so the seam inherits camera energy, world-state and momentum, and you can sanity-check before committing. Clip 1: no previous clip. Clip K ≥ 2: wait for K-1 to finish, verify its `savedTo` exists, then chain it (see "Attach references" + prompt part 2).

### ⚠️ SCOPE: the compact shape + minimal attachments below are the SEEDANCE reference-to-video + storyboard path
Everything from here to the end of STEP B — the "attach only the clip's own sheet + the previous clip" rule AND the compact per-clip prompt shape — is written for **the chosen model being a Seedance-class model doing REFERENCE-TO-VIDEO, driven by a storyboard**. That is the default `storyboard-to-video`-labelled path. If you end up on a **different model** (no Seedance-class model available, a non-reference-to-video model, or no storyboard to anchor to), this is NOT how you compose: follow that model's own craft skill + the `video-generator` skill, whose techniques for references and prompt shape differ (e.g. other models often need explicit character/product identity refs and a fuller brief). Don't force this compact/minimal-attachment shape onto a model it wasn't written for.

### 🕸️ PRE-STEP (before attaching): mesh realistic human faces onto a NEW sheet copy
Seedance reference-to-video REJECTS a photoreal human face used as a reference image — the render fails. The panels come from `visual-panels` with **ordinary bare faces**; you fix it HERE, right before rendering, by making a meshed COPY of the sheet and attaching that instead of the original. Do this per clip, only when needed:

1. **Does this clip's panel range contain a realistic / photoreal / live-action HUMAN face?** No → skip this pre-step entirely, attach the original sheet. Stylised faces (anime / 2D / clay / cartoon 3D) and non-face subjects don't trip the filter — skip them too. If unsure, mesh it (a stripped mesh costs nothing; a rejected render costs the whole clip).
2. **Copy the sheet first — NEVER modify the approved original in place.** `replace_panel` edits the sheet file in place, so work on a fresh copy (duplicate the sheet PNG to a temp path). The approved sheet the user sees must stay bare-faced.
3. **For each panel with a face, crop → mesh → paste back into the copy:**
   - `extract_panel(sheet=<copy>, panel=<n>)` → the panel crop (note its aspect).
   - `generate_image` in EDIT mode with that crop as the reference image, at the SAME aspect. **Prefer a Nano-Banana edit model for the meshing** (e.g. `model: "fal-ai/nano-banana-2/edit"`) — it holds identity/pose while overlaying the mesh cleanly; check the `image-generator` skill for the current slug + params. **Pass `metadata: { "visible": false }`** so these throwaway meshed crops stay HIDDEN from the creations drawer / gallery (they're a technical intermediate, not a user output — the media library filters `visible !== false`, same as annotation snapshots). **Use this EXACT prompt (verbatim) when the panel has ONE face:**
     > `A high-fidelity digital human asset. Overlay a faint, translucent blue geometric wireframe mesh onto the face. The mesh lines should follow the contours of the cheeks and forehead. The eyes and mouth must remain clear. Rendered in a technical software interface style. No UI just the mesh filter on top of the face`
     - **When the panel has SEVERAL faces**, keep the wording but make it plural — apply the mesh to EVERY face:
       > `A high-fidelity digital human asset. Overlay a faint, translucent blue geometric wireframe mesh onto every human face in the image. The mesh lines should follow the contours of each face's cheeks and forehead. Every face's eyes and mouth must remain clear. Rendered in a technical software interface style. No UI just the mesh filter on top of the faces`
     - Do not add anything else to the prompt (no "keep identical" walls — the affirmative "mesh on top of the face" already preserves the shot; over-negating freezes the edit).
   - `replace_panel(sheet=<copy>, panel=<n>, image=<meshed crop>)` → composites it back into the copy.
4. The result is a NEW whole-sheet image identical to the approved one EXCEPT the face panels now carry the mesh. **This meshed copy is what you attach** (still one whole sheet — the "no individual panels" rule holds). The prompt then tells the model to strip the mesh and render bare skin (see the mesh line in "Per-clip prompt").

### 🔎 4K OUTPUT ONLY: upscale each panel and attach them INDIVIDUALLY
This applies **only when the user asks for the video in 4K** (you'll pass `resolution: "4k"` to `generate_video`). In that case a whole reference sheet is too low-res per-panel to hold up at 4k, so switch this clip to **individual, upscaled panels**:

1. **Order is fixed: MESH FIRST, THEN UPSCALE — never the other way round.** If a panel has a realistic human face, run the mesh pre-step on it FIRST (crop → mesh → the meshed crop). Only AFTER meshing do you upscale. (Upscaling a bare face then meshing would re-introduce a raw face; and meshing an already-upscaled panel wastes the upscale.)
2. **Upscale each of this clip's panels** (the meshed crop for face panels, the plain `extract_panel` crop for the rest) with `upscale_image` to the **maximum resolution the video model accepts** (Seedance → 4k). Use the `upscaleFactor` needed to get each panel crisp at that size. Set `metadata: { "visible": false }` on these intermediate upscaled crops too (throwaway, keep them out of the creations drawer).
3. **Attach the individual upscaled panels as separate reference images** (one per panel of this clip, in order). **This is the ONLY case where you attach individual panels instead of the whole sheet** — everywhere else the whole-sheet rule stands.
4. Everything else is unchanged: still `resolution: "4k"` on the `generate_video` call, still the compact prompt, still the mesh-strip negation for any meshed panel, still `prev_clip` for K ≥ 2.

Not 4K → ignore this section; attach the whole sheet (meshed copy if faces) as normal.

### Attach references (Seedance reference-to-video + storyboard) — the clip's OWN whole sheet + the previous clip, NOTHING ELSE
> 🛑 On EVERY clip attach exactly these, and nothing more:
> 1. **The clip's OWN panel sheet — the WHOLE sheet image, uncropped.** Alias `sheet_part_K` (or `storyboard` for a single-sheet storyboard). **When the clip has human faces, this is the MESHED COPY from the pre-step above** (whole sheet, face panels meshed); otherwise the original sheet. Either way it is the WHOLE grid PNG: **never `extract_panel` / crop / pass individual panels** as the attachment, and **do NOT attach any OTHER sheet** (not prior parts, not later parts). (The pre-step's `extract_panel` is an internal step to BUILD the meshed sheet, not what you attach.) The prompt names WHICH panels of it this clip uses ("panels A to B"); the model reads only those. The sheet already carries the characters' design, so you do NOT attach separate character / product / location identity refs on this path. **(EXCEPTION — 4K output: attach individual upscaled panels instead of the whole sheet; see the "4K OUTPUT ONLY" section above.)**
> 2. **The immediately-previous clip as a video (K ≥ 2 ONLY)**: `[{ alias: "prev_clip", path: <K-1's savedTo> }]` in `referenceVideos`. IMMEDIATE predecessor only — never earlier clips.
>
> That's the whole attachment list: own sheet (+ previous clip for K ≥ 2). The tool REJECTS (`success:false`) if the prompt cites a reference not attached, so cite only these two. Clip 1 has no previous clip → sheet only.

Per CLIP (global `clipIndex` order) call `generate_video` with:
- **`prompt`**: per "Per-clip prompt (COMPACT)" below; addresses ONLY the shots/panels in THIS clip.
- **`referenceImages`**: ONLY this clip's own whole sheet — the MESHED COPY when the clip has human faces (pre-step), else the original. No other sheets, no individual-panel crops, no identity refs. **(4K output = the exception: individual upscaled panels, meshed-first; see "4K OUTPUT ONLY".)**
- **`referenceVideos`** (K ≥ 2 ONLY): `[{ alias: "prev_clip", path: <K-1's savedTo> }]`. Omit for K=1. Immediate predecessor only.
- **`duration`**: the CLIP's resolved value (`clip.durationSec`), whole second in `[D_min,D_max]`. NOT hardcoded, NOT the sheet total.
- **`aspectRatio`**: the target platform (9:16 Reels/TikTok/Shorts, 16:9 YouTube/web, 1:1 or 4:5 Instagram). MANDATORY; the sheet stays 16:9 (reading surface), the model reframes. A 16:9 clip in a 9:16 timeline = black bars.
- **`quality: "high"`**.
- **`withAudio: true`**: ALWAYS (default `false` → omitting = silent = hard failure). Controls DIEGETIC sound (SFX/dialogue/voiceover/ambient), NOT music. Exclude music ONLY via the closing Audio line, NEVER via `withAudio: false` (kills SFX/voices). Only `false` for a deliberately fully-silent clip (essentially never).
- **`saveTo: <directory>`**.

### Model choice (NOT hardcoded) + activate the craft skill
> **Step 0 — activate `video-generator` FIRST.** Before choosing or wording any clip, activate the `video-generator` skill. MANDATORY for ALL video generation: it explains how to call `generate_video` and the exact params each model accepts. Do this even here — the model-specific craft skill does NOT replace it (`video-generator` = how the TOOL works; the craft skill = how to WORD a clip). Never commit to a model's craft skill before `video-generator` is active.
> **Then choose the video model — never hardcoded here.** Pick from the `generate_video` catalog (in the tool's own description): **if a model is tagged with the `storyboard-to-video` label, use that one**; otherwise pick a multi-shot-capable model appropriate for the shots. Backend-managed (a label) — if backoffice moves it, you follow automatically.
> **If the chosen model has a dedicated craft skill, activate it** and use it for wording.
> > 🔴 Currently a **Seedance-class** model has one: activate `seedance-2-0` (bundled; Claude backend: `Skill` tool `braxil-essentials:seedance-2-0`; koi backend: `activate_skill({ name: "seedance-2-0" })`). ACTIVATING THE ROOT ISN'T ENOUGH — then `Read` (NOT `Skill`) its craft sub-skills BEFORE any clip prompt: `skills/seedance-prompt-short/SKILL.md` (compact shape — this is the DEFAULT here, ALWAYS); `skills/seedance-camera/SKILL.md` + `skills/seedance-motion/SKILL.md` (ALWAYS); `skills/seedance-antislop/SKILL.md` (kill "cinematic/beautiful", ALWAYS); `skills/seedance-copyright/SKILL.md` (IP-safe rewrite when brands/real people/franchise props); `skills/seedance-continuation/SKILL.md` (clips 2…N of a chained sequence); `skills/seedance-characters/SKILL.md` (locking recurring characters). Activating but never `Read`ing a craft file = did NOT use it.
> **No craft skill for the chosen model →** use the compact shape below (self-sufficient). It's an enhancement, not a dependency; don't tell the user to install anything.
> **Division of labour:** the craft skill shapes WORDING + cinematography; THIS skill owns the compact STRUCTURE + the tool call (which references, panel-range naming, aspect/duration, clip-chaining). Feed the craft skill THIS clip's material (its shots' `action`, framing, camera, `dialogue`, `continuity` rows, resolved `duration`, target `aspect`, reference plan). It never invents beats or drops continuity/dialogue.

### Per-clip prompt (COMPACT — this is the required shape for Seedance reference-to-video)
> Applies on the Seedance-class reference-to-video + storyboard path (see the SCOPE note above). Other models → their craft skill decides the prompt shape.

The prompt is SHORT and structured, never a verbose director's brief. It describes ONLY the shots that appear in THIS clip, in JSON order. No banners, no ALL-CAPS shouting, no timecodes, no per-shot style or appearance re-description (the sheet + refs carry the look). Model renders words literally, so keep each shot to its essential physical beat.

> ### 🎬 READ THE CONTINUITY MATRIX FIRST — before writing a single SHOT line
> The storyboard's **continuity matrix** is the per-shot `continuity` rows `{ characters, objects, place }` (one row per shot / panel) PLUS the storyboard-level `continuity` LOCK (story-wide invariants + negatives). It is the authority on WHAT STATE holds in each shot, and Seedance silently RESETS any state it isn't told about at the shot where it applies (character back on the ground, prop un-broken, room clean again). So, for THIS clip, walk the matrix rows for its shots BEFORE composing, and carry what they say INTO the prompt:
> - **Per-shot row → the matching SHOT line.** When a row records a NON-DEFAULT state that still holds in that shot (someone standing ON the cans, a bottle already half-empty, a melted hole, a specific `place`), restate it inside that shot's line — even if the shot's `action` text dropped it. The matrix is authoritative; transcribe it, don't re-derive. Fill `place` when a close-up would otherwise lose the setting.
> - **LOCK → the closing "Hard rules" clause** (part 4). The story-wide invariants/negatives go in verbatim once.
> - **Never invent or "fix" state.** Only re-inject state the matrix established; never add a new event. If two consecutive rows contradict (broken here, whole next), that is a source bug — render the physically coherent reading the synopsis/LOCK imply and surface the conflict; never animate the impossible state.
>
> The matrix is the single best guard against raccord drift ("unreachable became reachable", "step-object destroyed", "he's back on the floor"). Keep it in view for every clip, not just clip 1.

Four parts, in this order:

**1. Scene line (1–2 sentences).** The look / medium + who or what is in frame, from the storyboard `style` / `synopsis`. **Copy this line VERBATIM across every clip of the piece** — paraphrasing between clips drifts the look. Example: *"Photorealistic NASA-documentary footage on Mars. Three rock-skinned gray-ochre aliens, each holding an amber glass bottle."*

**2. Shot-count + continuity line.** *"`<N>` shots, hard cuts, perfect continuity. Each shot matches the framing of its reference panel (panels `<A>` to `<B>`)."* — `N` = number of shots (takes) in THIS clip; `A`–`B` = this clip's panel range on the attached whole sheet. **The model counts and maps shots→panels itself — do NOT add per-shot panel citations.** (If a shot spans several keyframe/glued panels, that is still one shot; the range still covers them.)

**3. One line per SHOT, in JSON order.** Format:
```
SHOT n — <shot size / framing>, <angle if non-default>, <camera movement>: <super-brief action>.
```
- **Header** = shot number + framing (extreme wide / wide / medium / medium group / close-up / ECU / insert…) + angle only when non-default (low-angle / high-angle / rear / POV / over-shoulder — and negate the opposite: *"rear only, no front"*) + movement (static / slow push-in / dolly-in / pan left / whip pan / orbit…). One camera move per shot.
- **Action** = the shot's `action` from the JSON, compressed to its ONE essential physical beat. Name grip / side / count exactly when it matters ("a single amber bottle", "button 2 of 16"), one mechanical step per shot. Don't re-describe style or appearance.
- **Dialogue** inline, in the language it is spoken, in quotes: *"…says: «…y le digo: que en la Tierra hay vida. Pero inteligente, va a ser que no.»"*.
- **SFX** for that shot, inline at the end when notable.

Example shot lines (from the reference prompt):
```
SHOT 1 — extreme wide establishing shot, slow push-in: red Martian plain under an ochre sky; the three aliens sit small and distant at center on flat rocks, each with an amber bottle. Nothing else moves.
SHOT 2 — medium group shot, static: the three clink their bottles in a toast and laugh; one gestures and says: «...y le digo: que sí, que en la Tierra hay vida. Pero inteligente, va a ser que no.»
SHOT 3 — close-up, static: one alien raises his amber bottle and takes a long sip, eyes half-closed.
SHOT 4 — medium shot, static: all three snap their heads left, eyes wide; the drinker spits the beer in a thin stream. They freeze, staring off-frame.
```

> **Faithful transcription, never invent a shot.** Shot lines come ONLY from THIS clip's JSON shots, in JSON order — no add / drop / reorder / split / merge. Camera-move keyframe panels and `noCutBefore`-glued runs collapse into ONE shot line (cite their panel range, "no cut"). Before writing, state *"this clip has N shots"* and match. **Carry established state forward — from the continuity matrix (see the callout above):** for each shot, check its `continuity` row `{ characters, objects, place }` and restate any non-default state that still holds, even where the shot's `action` text dropped it, or Seedance resets it. The row is authoritative; transcribe it, don't re-derive. **Causal order only:** never show aftermath before its cause.

**4. Closing scene note (1 line).** The environment / atmosphere / lighting that holds across the whole clip, plus the audio note. Example: *"Ochre dusty sky, long hard shadows, soft constant Mars wind. Audio: diegetic sound only, natural ambience; music on a separate timeline track."* When the storyboard has story-wide invariants (`continuity` LOCK / negatives the model won't infer), fold the few hard ones in here as a short *"Hard rules: …"* clause (e.g. *"the button stays mounted high and out of reach until he climbs; bottles stay intact"*). Audio phrasing: single-sheet or music baked in → *"diegetic sound only, natural ambience"*; multi-sheet with a separate music track → *"…music is on a separate timeline track, not part of this clip."* `withAudio: true` is a tool param, NEVER prompt text; never `withAudio: false` to keep music out.

**Panels are ACTION references, not start frames — say it once.** A panel is a representative moment WITHIN its shot (often mid-action), not the first frame. Add one global line: *"the panels are reference stills of a moment WITHIN each shot, not starting frames: begin each shot naturally before its reference moment and flow the motion through it."* Never pass a panel/sheet as `startFrame` (only a previous clip's real final frame qualifies, and only if you use frame-anchoring).

**🕸️ Wireframe mesh on faces = annotation, STRIP it — say it whenever you meshed a panel.** When you built a meshed sheet in the pre-step (faces carry the faint pale-blue wireframe so the sheet survives Seedance's face filter), that mesh is a technical mark on the SHEET, never part of the scene — the video must render ordinary bare skin, no mesh. Add a global line NAMING the exact panels you meshed, e.g.: *"the pale-blue wireframe grid drawn over the woman's face in reference panels 3 and 5 is a technical annotation on the sheet, NOT part of the scene — her face is ordinary bare skin in every shot and no grid, mesh, lines or overlay of any kind ever appears on it."* Name the actual meshed panels of THIS clip; if you meshed none, omit the line. Without the negation the model paints the grid onto the face.

**Length:** keep the whole prompt tight — roughly the size of the reference example (one scene line, one count line, one line per shot, one closing line). Don't pad; do give each shot enough motion to differentiate it.

### Part 2 — CLIP CHAINING (clips 2…N): attach the previous clip and say it's a continuation
For every clip after the first, you already attached the immediately-previous clip as `prev_clip` (`Video 1`) in `referenceVideos`. In the prompt, add a short continuation line right after the scene line, stating explicitly that this clip continues the attached previous clip:

> *"`Video 1` is the immediately preceding clip of this same film. This clip continues DIRECTLY from its last frame: same lighting, character positions, momentum and world-state at its end — do not reset. Match its pacing and camera energy. Do NOT repeat or re-enact its shots; render only the NEW shots below."*

Attach and cite ONLY the immediately-previous clip (K-1), not earlier ones. Without this line the model tends to re-enact the previous clip instead of continuing it. Omit the whole part for clip 1.

## STEP C: Music track (single, full-length, only when needed)
Audio plan calls for music AND **≥ 2 sheets** → ONE separate track (per-clip music thumps every boundary; independent renders can't keep a continuous melody across seams): ONE `generate_audio`, `type: "music"`, `duration: <total = sum of all clip durations>`, `prompt` from the type's music brief + tone. Single-sheet (one clip, no seams) → music inside the clip render is fine, skip. Voiceover-only / SFX-only → no music, skip.

## STEP D: Assemble the timeline (concatenate every clip into one video)
Follow `timeline-assembler`.
1. **Always `create_timeline` a NEW timeline**: one fresh per video; NEVER reuse/append/overwrite. Descriptive `name` + target `aspectRatio`; do NOT pass fps/width/height (inheritance). Keep the returned `timelineId`.
2. **V1: concatenate clips in order, back-to-back, each clip's OWN duration** (cumulative cursor, no uniform 15 s slots):
   ```
   cursorMs = 0
   for clip in clips (in sheet order):
       add_clip_to_timeline(track="V1", path=clip.path, startMs=cursorMs, durationMs=clip.durationSec * 1000)
       cursorMs += clip.durationSec * 1000
   ```
   `add_clip_to_timeline` auto-detects each clip's audio stream, do NOT pass `hasAudio`.
3. **A2: music** (if STEP C): one clip at `startMs: 0`, `durationMs: totalMs`. **Duck ONLY where it competes with voice, from actual audio, not reflexively:** voiceover/dialogue → duck to ≈ −28 dB (`set_clip_volume(<musicClipId>, { change: { gain: 0.04 } })`, or `volumePoints` for speaking stretches); NO-voice sections (action beat, intro/outro, wordless montage, SFX-only) → do NOT duck. See assembler's "Audio mixing levels".
4. (Optional) subtitles for tutorial/explainer per the assembler's "Subtitles" matrix.
5. **Hand-off: ALWAYS end by showing the TIMELINE.** `show_timeline({ id })` — pass the id from `create_timeline`, nothing else (NOT a path; don't hunt the .json on disk). That's the finish. Only if the user explicitly asks to export: `render_timeline({ id })` → `show_video` the rendered mp4. (koi/CLI surface: `show_result({ resourceType: "timeline", timelineId })`.)

Final length = sum of per-clip durations (= storyboard total when present). Concatenation is timeline-only: NEVER `ffmpeg concat` or any glue tool.

## MODEL DISPATCH (read before composing any prompt)
Composition is MODEL-AWARE: identify the family of the model you chose (see "Model choice") and load its spec from `references/` if one exists. **If the chosen model is Seedance-class, read [references/seedance-2.md](references/seedance-2.md)** and compose per its skeleton/limits/camera vocabulary. Other families: apply the compact shape above until a dedicated reference exists.

## Continuity across clips (multi-shot lock)
The compact shape keeps continuity with a few hard rules — keep them verbatim across clips:
1. **Identical subject nouns in every shot and every clip** — the SAME short noun phrase ("the three rock-skinned aliens"); re-describing re-casts them.
2. **Same reference discipline on every clip** — each clip attaches its own whole sheet (never crops, EXCEPT 4K output = individual upscaled panels), plus the previous clip video from K ≥ 2. The sheet carries identity across the piece.
3. **Lock the scene line + lighting phrasing verbatim** across all clips (copy, don't paraphrase).
4. **Max ~5 camera setups per clip** (Seedance-class). Exceed → the upstream chunking already split it; if not, split into two chained calls.
5. **Clip chaining (the plano-secuencia formula):** attach the immediately-previous clip as `prev_clip` video and add the continuation line (STEP B Part 2). The previous VIDEO carries the DYNAMICS (pacing, movement, camera cadence, lighting in motion); its final frame is the join point. If the model can't take a video ref, fall back to frame-anchoring: pass the previous clip's extracted final frame as the start/anchor of the next.
6. **One master audio bed:** music OFF the clips (separate track), only diegetic SFX per shot.

## Voice consistency across clips (read once)
With `withAudio: true` voiceover is per clip; reference-to-video models match voice to the visible character, so the same character ref across sheets gives high-but-not-guaranteed consistency. If voice audibly drifts, fallback: `withAudio: false` on every clip (silent), generate ONE TTS pass of the whole script via `generate_audio` with a fixed `voice`, lay as a second audio track. Trades lip-sync precision for identical voice; use only when drift shows.

## Iteration
- **Clip re-roll:** `generate_video` again for that clip, same references, revise ONLY the affected SHOT lines; keep the scene line, continuation line, closing note identical. K ≥ 2 `prev_clip` still points at K-1; if K-1 was re-rolled, propagate its NEW path.
- **Total duration change:** re-resolve per-CLIP durations (STEP A); relative weighting usually scales, don't uniformly scale unless the user said so.
- **Target generator change:** swap the per-tool tailoring and re-render; shot grammar stays, only camera language shifts.

## Don't (terse checklist; each detailed in full above)
- (Seedance r2v path) Write a long verbose director's brief — the prompt is COMPACT (scene line + count line + one line per shot + closing note).
- ATTACH individual-panel crops — attach the WHOLE sheet (the meshed copy when the clip has faces), and name the panel range in the prompt. (`extract_panel` IS used internally to BUILD the meshed sheet in the face pre-step; just never attach a bare crop as the reference.) THE ONE EXCEPTION is 4K output, where you attach individual UPSCALED panels (meshed-first) — see "4K OUTPUT ONLY".
- (4K) Upscale BEFORE meshing — always mesh first, then upscale. And don't forget to upscale at all: at 4K a raw sheet-panel is too soft.
- Attach anything beyond this clip's own sheet + the previous clip video — no other sheets, no separate identity refs (the sheet carries identity).
- Add per-shot panel citations — the count line ("panels A to B") maps them; the model counts.
- Force the compact shape / minimal attachments onto a non-Seedance or non-reference-to-video model — that path uses its own craft skill's techniques (SCOPE note in STEP B).
- Hardcode `duration: 15` (STEP A owns timing).
- Search disk for the storyboard JSON (STEP 0 / INPUTS: metadata is the only auto-recovery; missing → sheet pixels, never an unrelated JSON).
- Compress a >15 s CLIP by dropping shots (STEP A fail-fast; a SHEET may exceed 15 s, a CLIP never).
- Render one clip per panel or per sheet — one per **CLIP** (STEP B).
- Invent, add, drop, reorder, split or merge shots (STEP B: shots come ONLY from THIS clip's JSON, in order; glued runs = one shot line).
- Burn ANY text into the video, or copy sheet chrome (spoken lines are AUDIO).
- Attach a photoreal human face UNMESHED to Seedance (it rejects it → failed render) — mesh the face panels onto a sheet copy first (pre-step). And don't let the mesh render in the output: add the "bare skin, no mesh" negation naming the meshed panels.
- Mesh the APPROVED sheet in place — always work on a copy; the original stays bare-faced.
- Flip the viewpoint, or break causal order (force the viewpoint + negate the opposite; state only advances).
- For clips 2…N: forget to attach the previous clip and state it's a continuation (STEP B Part 2) — without it the model re-enacts the previous clip.
- Ignore the continuity matrix — read the per-shot `continuity` rows + LOCK when you read the storyboard, and restate carried-forward state in each Seedance shot line (STEP B "🎬 READ THE CONTINUITY MATRIX FIRST"); it's the raccord authority, not optional colour.
- Reset world state between clips (each clip opens in the previous clip's end state).
- Bake music into per-clip renders for ≥ 2 sheets (STEP C), or duck music reflexively (STEP D: only under voice).
- Ship a silent clip / use `withAudio: false` to drop music (STEP B).
- Render 16:9 for a vertical target (pass the platform `aspectRatio` every call).
- Concatenate outside the timeline, reuse/append a timeline, or finish without `show_timeline`-ing the TIMELINE (STEP D).
