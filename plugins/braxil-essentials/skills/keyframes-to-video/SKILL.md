---
name: keyframes-to-video
description: Turning one or more approved KEYFRAME sheets (the 4K panel-grid images built by the `storyboard-to-keyframes` skill) into the FINAL video. Takes the sheet images, an optional references manifest (characters / products / settings to lock identity), and (when available) the storyboard JSON (the authority for per-clip timing, per-shot action, dialogue, SFX and music). Composes a COMPACT per-clip video prompt for each clip, renders one video per CLIP: a clip is a group of consecutive panels (e.g. panels 4–7), and a single sheet can hold several clips (see each sheet's `metadata.clips`), with each clip's duration driven by the storyboard when present, generates a single music track when needed, and assembles every clip back-to-back on a timeline into one continuous video. Use whenever you have approved panel sheets and need the rendered video (e.g. Step 4 of the create-video workflow). Pairs with `storyboard-to-keyframes` (its upstream) and `timeline-assembler` (which it delegates assembly to).
---

OUTPUT stage: `storyboard-to-keyframes` produced the approved 4K sheet(s); this skill **composes the video prompt AND renders** each clip, then stitches all into the final film. Assembly mechanics (track layout, fps/aspect inheritance, music ducking, transitions, subtitles, preview handoff) are delegated to **`timeline-assembler`**: read its SKILL.md before assembling, don't re-derive.

## 🛑 STEP 0: RECOVER + READ THE STORYBOARD JSON FIRST (MANDATORY, before any `generate_video`)
The sheet is NOT the script, the storyboard JSON is. Never infer the scene from sheet pixels when a `sourceStoryboard` exists (reported bug: hallucinated "vending machine" for a man-on-a-sofa storyboard).
1. Recover via `inspect_creation({ filePath: "<sheet path>" })` → `creation.metadata.sourceStoryboard` → `read_file` THAT JSON (AUTHORITY for premise, per-shot action, timing, continuity, dialogue, audio). **When you read it, read the CONTINUITY MATRIX too** — the per-shot `continuity` rows `{ characters, objects, place }` + the story-wide `continuity` LOCK. Hold it in mind for every clip: it drives what state you must restate in each Seedance shot line (see "🎬 READ THE CONTINUITY MATRIX FIRST" in STEP B). It is not optional colour, it is the raccord authority.
2. NEVER pass the SHEET as `startFrame`, it's `referenceImages` (look/identity) only.
3. NEVER skip to a raw `generate_video` off pixels + invented prompt; compose FROM the JSON, shot by shot.
4. Fall back to sheet pixels ONLY when `inspect_creation` returns no `sourceStoryboard`. Never ask the user to name the project.

## INPUTS
From the task description, or `step5_output.json` (create-video workflow):
- **`sheets`**: ORDERED list of approved sheet images (PART 1…N), absolute paths. Required. **Resolving when not given an explicit list** (ad-hoc "genera el vídeo"): a session holds SEVERAL videos; most-recent-on-disk is often the WRONG project (bug: rendered horse project instead of Star Wars). Resolve scoped, never by recency: target = ACTIVE doc in `# WORKING AREA`, take its `id`; `recall_creations({ kind: 'image', storyboard: '<id>' })` → only sheets whose `metadata.sourceStoryboard` ties to it, ordered by `storyboardPart`. 🚫 NEVER "most recent", `ls`/`shell` the images dir, or mix storyboards. No active storyboard / spans >1 / empty → STOP and ask which to render (offer candidates by name).
- **`references`**: OPTIONAL manifest of recurring subjects, each `{ alias: path-or-@handle }`, e.g. `{ hero_character: "/…/leo.png", product_pack: "@acme_bottle" }`. ⚠️ On the **Seedance reference-to-video + storyboard** path (the default) you do NOT attach these — the panels already carry identity, and each clip attaches only its own INDIVIDUAL panels + the previous clip (STEP B). This manifest is for OTHER-model paths whose technique needs explicit identity refs; there, pass the in-scope refs (shot+scene+storyboard, resolving `@handle` → path) into `referenceImages`.
- **`storyboard_path`**: path to `~/.koi/storyboards/<id>.json`. When present = AUTHORITY for: per-shot `duration`, `action`, `continuity` = { characters, objects } (legacy: single `state` string), `dialogue`, `sfx`/`music`/`audio`, plus storyboard-level `synopsis` (premise), `continuity` (LOCK = story-wide invariants/negatives), `characters`, `lighting`, `aspect`. Prefer over sheet pixels; transcribe `synopsis` + LOCK + per-shot `continuity`, don't drop. **Recovery (NEVER ask the user which storyboard, asking is the bug):** (1) `inspect_creation({ filePath: "<sheet abs path>" })`: MANDATORY; `metadata.sourceStoryboard` = ABSOLUTE PATH (+ `storyboardPart`/`storyboardParts`); ⚠️ `read_file` returns PIXELS not this. Hit → `read_file` THAT JSON. (2) Only if no `sourceStoryboard` → fall back to sheet pixels (`read_file` PNG; vision returns panels/captions/banner/timecodes → derive durations/beats). ⛔ DO NOT filesystem-search for a "matching" JSON (no `shell ls .koi/storyboards/`, `recall_creations` to "find" it, reading every JSON and guessing): confabulation bug matched `soc2_compliance_explainer.json` to a pocket-watch story. Metadata is the ONLY sheet→JSON link; no metadata = no JSON → use pixels. Neither metadata nor legible pixels → surface via a single `print` (not blocking), proceed best-effort; never invent the link.
- **`audio_plan` / `type` / `aspect_ratio` (platform)**: OPTIONAL (music need+brief, video type, destination aspect). Pre-resolved in `step5_output.json`.
- **`targetGenerator`**: OPTIONAL (Seedance/Kling/Sora/Veo/Runway/Luma/Hailuo/Wan/Higgsfield); tailor camera + pacing. Absent → model-agnostic.

`sheets` missing/empty → surface the error.

## STEP A: Enumerate the CLIPS and resolve each clip's duration
**A sheet is NOT a clip.** `storyboard-to-keyframes` packs multiple clips per sheet in **`metadata.clips`**: `[{ clipIndex, shotIds, panels, durationSec }, …]`. Read every sheet's `metadata.clips` (via `inspect_creation`), concatenate, sort by global `clipIndex` → render plan. **One `generate_video` per CLIP**, in `clipIndex` order across ALL sheets, NOT per sheet. Fallback (old sheets, no `metadata.clips`): whole sheet = one clip.

**Duration range: read from the tool, never hardcode:** `get_tool_info("generate_video")` → `duration` schema (typical whole seconds [4,15] + `"auto"`; trust the tool). Use `D_min`/`D_max`. Resolve per clip, priority: (1) **`clip.durationSec`** (PREFERRED): clamp to `[D_min,D_max]`; with the JSON cross-check == sum of its `shotIds`' `shot.duration`; (2) no JSON → sheet pixels: sum per-panel timecodes for total `S`, or use banner total (`PART K: … (<n> frames · <S> s total)`), clamp `S` to a whole second in `[D_min,D_max]`; (3) neither → `D_max` AND surface uncertainty via `print`.

NEVER hardcode `duration: 15` when the storyboard says otherwise. State per-clip durations before rendering (*"3 clips: PART 1 → 14 s, PART 2 → 10 s, PART 3 → 10 s"*). ⚠ **The storyboard total overrides any duration in the task/brief** (task "60 s" but storyboard sums 48 s → video is 48 s; don't pad/stretch/add filler). Sole exception: explicit hard-target ("must stay exactly 60 s") → refit.

### ⛔ Fail-fast: a single CLIP > 15 s is malformed (a sheet may exceed 15 s, fine)
Sanity-check EACH clip (`durationSec` or summed `shot.duration`). Any clip > 15 s (or no `metadata.clips` AND whole sheet's shots sum > 15 s) → upstream chunking bug; don't silently drop shots (*"hizo los 15 s pero solo de una parte"* bug). STOP: *"Clip `<clipIndex>` sums to `<X>` s but a rendered clip caps at 15 s. Please re-build the sheets with `storyboard-to-keyframes`: its Chunking step splits shots into ≤15 s clips I'll then render and concatenate."* Never auto-compress/truncate.

## STEP B: Render one `generate_video` per CLIP (a group of consecutive panels, e.g. 4–7 → ONE video), SEQUENTIALLY with clip-chaining
> 🛑 BEFORE the first `generate_video`, in this order: (1) activate the `video-generator` skill (MANDATORY for any video generation — how the tool + each model's params work); (2) choose the video MODEL (see "Model choice"); (3) if that model has a dedicated craft skill, activate it. Don't skip to a self-written brief, and don't commit to a model's craft skill before `video-generator` is active.

Unit = **clip** = a GROUP of consecutive panels (`metadata.clips[].panels`). `[4,5,6,7]` → ONE video for panels 4–7. NOT per panel; NOT per sheet (a 12-panel sheet may be 3 clips → 3 videos, e.g. 1–4/5–9/10–12).

**Several panels can be ONE shot (one take, no internal cut): animate THROUGH.** Two cases, same handling: (a) a camera-move shot's 2-3 keyframe panels (share `shotId`) = start/middle/end of one move; (b) consecutive shots flagged `noCutBefore` (or sharing `number`) = glued plano secuencia. Both → ONE SHOT line that cites the whole panel range, moving smoothly, NO internal cut. A real cut (a new SHOT line) falls ONLY where the JSON is NOT glued. So **the number of shots in a clip = number of takes, not number of panels.**

**Render SEQUENTIALLY, not parallel**: each clip continues from the one before it, so the seam inherits camera energy, world-state and momentum, and you can sanity-check before committing. Clip 1: no previous clip. Clip K ≥ 2: wait for K-1 to finish, verify its `savedTo` exists, then chain it (see "Attach references" + prompt part 2).

### ⚠️ SCOPE: the compact shape + minimal attachments below are the SEEDANCE reference-to-video + storyboard path
Everything from here to the end of STEP B — the "attach only the clip's own individual panels + the previous clip" rule AND the compact per-clip prompt shape — is written for **the chosen model being a Seedance-class model doing REFERENCE-TO-VIDEO, driven by a storyboard**. That is the default `storyboard-to-video`-labelled path. If you end up on a **different model** (no Seedance-class model available, a non-reference-to-video model, or no storyboard to anchor to), this is NOT how you compose: follow that model's own craft skill + the `video-generator` skill, whose techniques for references and prompt shape differ (e.g. other models often need explicit character/product identity refs and a fuller brief). Don't force this compact/minimal-attachment shape onto a model it wasn't written for.

### 🧩 PRE-STEP (before attaching): DECOMPOSE the clip into individual panels; launder any FACE panel through Seedream

> 🚨🚨 **SUPER MANDATORY — NON-NEGOTIABLE, THE #1 CAUSE OF REJECTED RENDERS:** EVERY panel in which a human face — **or ANY part of one** — is visible, in ANY form, MUST be laundered through an EXACT Seedream copy before it is attached. NO exceptions. Skip even ONE face panel and Seedance's face filter rejects the whole render with *"image_urls: may contain likenesses of real people"*, and you waste render after render hunting the trigger. Do the Seedream pass on ALL of them UP FRONT, in the same parallel batch — never wait to be rejected first.
>
> **"a face (or part of one)" is DELIBERATELY BROAD — when in doubt, launder (it is cheap, 1:1, and NEVER hurts):**
> - a full frontal portrait **AND** a ¾ / profile / side face
> - a face seen **from BEHIND or at the back of the head** if ANY sliver of feature (cheek, brow, ear-line, jaw, nose tip) is visible
> - a **partial / cropped / edge-of-frame** face, a **small or background** face, a face **out of focus / blurred / in shadow / backlit**
> - eyes **open OR closed**, face turned away, tilted, or half-hidden by hair/hand/object
> - a face **reflected in a mirror / glass / water**
> - **more than one** face in the panel (launder the panel — the whole crop goes through Seedream once)
>
> The ONLY panels that skip Seedream are ones with **ZERO human face and zero face-part anywhere** (pure hands/objects/scenery/backs-of-heads-with-no-visible-features), or a **stylised** face (anime / 2D / clay / cartoon — those don't trip the filter). If a real photoreal human's face or any fragment of it is in the frame at all → Seedream. Full stop.
>
> ⚠️ **The previous-clip REFERENCE VIDEO carries faces too.** When you chain `referenceVideos` (K ≥ 2) and that prior clip contains her face, Seedance's filter can fire on the VIDEO (the error still says `image_urls`). If a chained render is rejected for likeness even though every panel was laundered, the reference VIDEO is the culprit — swap it for a **faceless continuity frame** (`extract_frame` a hands/object/scenery frame from the prior clip) instead of the whole video. Never assume it's a panel when the video is in play.

**ALWAYS attach this clip's panels as INDIVIDUAL images, one reference per panel — never the whole sheet.** (This is the technique the 4K path always used; it is now the DEFAULT for EVERY render — a clean single-panel reference reads better than one dense grid, and it lets you fix faces per-panel.) Two things can require an extra pass on a panel before it's attached: it holds a **photoreal human face** (Seedance reference-to-video REJECTS a raw photoreal face as a reference → the render fails), or you're rendering **4K** (a bare sheet-crop is too soft at 4k). Handle both here, per clip:

1. **`extract_panel(sheet=<this clip's sheet>, panel=<n>)`** for every panel in the clip's range, in order. NEVER `replace_panel` / never modify the approved sheet — the crops are throwaway; set **`metadata: { "visible": false }`** on every intermediate below too (they're technical prep, not user output; the media library hides `visible === false`, same as annotation snapshots).

2. **Per panel, decide the LAST model it passes through:**
   - **Panel shows a realistic / photoreal / live-action HUMAN face OR ANY part of one** (per the SUPER-MANDATORY broad definition above — frontal, profile, from behind with any feature visible, partial, small, blurred, reflected, eyes open or closed) → its LAST step is an **EXACT Seedream copy**. `generate_image` in EDIT mode, **`model: "bytedance/seedream/v5/pro/edit"`** (check the `image-generator` skill for the current slug + params), the panel crop as the reference image, reproducing it 1:1. A **Seedream-generated image CLEARS Seedance's face filter**; a raw photoreal crop does not. **Use this EXACT prompt (verbatim):**
     > `Reproduce this reference image exactly, as a faithful 1:1 copy: identical subject, face, identity, expression, pose, framing, composition, lighting, colours and background. Do not restyle, beautify, age or alter the face in any way; do not add, remove or move anything. Output the same image.`
     Resolution of the Seedream copy:
     - **Not 4K** → close to the panel crop's own pixel size (pass its `width`+`height`, or an `aspectRatio`+`resolution` near it). Seedance then renders at the max resolution closest to it — no upscale needed.
     - **4K** → at Seedream's **MAXIMUM supported size**: pass `width`+`height` filling the panel's aspect within Seedream's area cap (Seedream v5 Pro edit tops at ~4.2 MP = 2048² total — e.g. a 16:9 panel → ~2731×1536; a portrait panel → the same area in its own aspect). **Do NOT `upscale_image` a face panel** — that would make the upscaler its last model and re-introduce a raw face Seedance rejects.
   - **Panel has ZERO human face and zero face-part anywhere** (pure hands / objects / scenery / a back-of-head with no visible features), or a stylised anime / 2D / clay / cartoon face — those don't trip the filter. If you are not CERTAIN a panel is faceless, treat it as a face panel and Seedream it:
     - **Not 4K** → attach the plain `extract_panel` crop as-is (no extra pass).
     - **4K** → `upscale_image` the crop to the max the video model accepts (Seedance → 4k), `upscaleFactor` to get it crisp. (No face → the upscaler being its last model is fine.)

3. **🔒 INVARIANT — the LAST model any FACE panel passes through is ALWAYS Seedream**, never an upscaler or anything else after it. That is the whole mechanism: Seedance only accepts the face once it is a Seedream image. So at 4K you upscale the non-face panels but you do NOT upscale the face panels — those get a Seedream copy at max size instead.

4. **Run the per-panel passes IN PARALLEL** — panels are independent, so fire all the Seedream copies / upscales at once and await them together, never one-at-a-time. (This is prep; it does NOT relax the SEQUENTIAL `generate_video` rule, which chains clips because each continues from the last.)

The attach list is then this clip's **individual processed panels, in order**: the Seedream exact copy for every face panel, the plain (Not-4K) or upscaled (4K) crop for the rest. The whole sheet is NEVER attached.

### Attach references (Seedance reference-to-video + storyboard) — this clip's OWN individual panels + the previous clip, NOTHING ELSE
> 🛑 On EVERY clip attach exactly these, and nothing more:
> 1. **This clip's INDIVIDUAL panels** (the processed crops from the pre-step), one reference image per panel of THIS clip's range, in order: the **Seedream exact copy** for any face panel, the plain crop (Not-4K) or upscaled crop (4K) for the rest. Alias them per panel (e.g. `panel_4`…`panel_7`). **Never attach the whole sheet**, and **do NOT attach any OTHER clip's panels** (not prior parts, not later parts). The prompt names the panel range ("panels A to B") and the model maps shots→panels itself. The panels already carry the characters' design, so you do NOT attach separate character / product / location identity refs on this path.
> 2. **The immediately-previous clip as a video (K ≥ 2 ONLY)**: `[{ alias: "prev_clip", path: <K-1's savedTo> }]` in `referenceVideos`. IMMEDIATE predecessor only — never earlier clips.
>
> That's the whole attachment list: this clip's own panels (+ previous clip for K ≥ 2). The tool REJECTS (`success:false`) if the prompt cites a reference not attached, so cite only these. Clip 1 has no previous clip → panels only.

Per CLIP (global `clipIndex` order) call `generate_video` with:
- **`prompt`**: per "Per-clip prompt (COMPACT)" below; addresses ONLY the shots/panels in THIS clip.
- **`referenceImages`**: ONLY this clip's own individual processed panels, in order — the Seedream exact copy for face panels, the plain (Not-4K) or upscaled (4K) crop for the rest. No whole sheet, no other clips' panels, no identity refs.
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

**2. Shot-count + continuity line.** *"`<N>` shots, hard cuts, perfect continuity. Each shot matches the framing of its reference panel (panels `<A>` to `<B>`)."* — `N` = number of shots (takes) in THIS clip; `A`–`B` = this clip's panel range, attached as individual reference panels in order. **The model counts and maps shots→panels itself — do NOT add per-shot panel citations.** (If a shot spans several keyframe/glued panels, that is still one shot; the range still covers them.)

**3. One line per SHOT, in JSON order.** Format:
```
SHOT n — <shot size / framing>, <angle if non-default>, <camera movement>: <super-brief action>.
```
- **Header** = shot number + framing (extreme wide / wide / medium / medium group / close-up / ECU / insert…) + angle only when non-default (low-angle / high-angle / rear / POV / over-shoulder — and negate the opposite: *"rear only, no front"*) + movement (static / slow push-in / dolly-in / pan left / whip pan / orbit…). One camera move per shot.
- **Action** = the shot's `action` from the JSON, compressed to its ONE essential physical beat. Name grip / side / count exactly when it matters ("a single amber bottle", "button 2 of 16"), one mechanical step per shot. **Compress the STYLE, never the PHYSICS** (see the hard rule below): the beat stays one action, but if that action has real-world mechanics — a trajectory, gravity, contact, something being drawn/created — spell those out. Don't re-describe style or appearance.
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

**⚙️ DESCRIBE THE PHYSICS of any action — a vague verb makes Seedance invent wrong mechanics.** The compact shape strips STYLE, never the mechanics of a physical action. Seedance renders the words literally, so a loose verb becomes a literal (wrong) instruction. Two archetypes, both reported bugs:
- **Floating instead of a real trajectory.** *"spins in mid-air then snaps into his fist"* → the model reads "in mid-air" as "float". Fix: write the ARC with gravity — *"the coin rises, peaks, then falls back accelerating under gravity and lands firmly in his closed fist"*. State up/peak/down + acceleration + the contact/endpoint.
- **A detail materialising all at once instead of being progressively created.** *"drags a single fresh red arrow"* → the model draws the line AND pops the arrowhead into existence. Fix: describe the MECHANISM stroke by stroke — *"the pen tip moves and red ink appears ONLY directly under the moving tip, tracing the shaft first, then the two head strokes; nothing exists ahead of the tip"*. Name what creates what, and that nothing appears before its cause reaches it.

General rule: for any action, name the **actor + force/mass + trajectory + acceleration + contact + visible endpoint**, and forbid the wrong reading (*"no floating; no part appears before the tip reaches it"*). One physical cause with its visible consequences beats a single vague verb. **ALWAYS keep scene continuity:** the mechanics you describe must be consistent with the shot's `continuity` row and the surrounding shots — the object's state, position and momentum at this shot's start come from where the previous shot left them (matrix authority); never describe a motion that contradicts the established state, and carry the end state forward. If a shot has no real-world mechanics (a static look, a held pose) this doesn't apply — don't over-specify.

**Panels are ACTION references, not start frames — say it once.** A panel is a representative moment WITHIN its shot (often mid-action), not the first frame. Add one global line: *"the panels are reference stills of a moment WITHIN each shot, not starting frames: begin each shot naturally before its reference moment and flow the motion through it."* Never pass a panel/sheet as `startFrame` (only a previous clip's real final frame qualifies, and only if you use frame-anchoring).

**Faces need NO strip line.** Face panels are laundered through an EXACT Seedream copy (pre-step), which is a clean ordinary face — there is no mesh, grid or overlay to negate. Do not add any "bare skin / strip the mesh" line; that method is gone.

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
2. **Same reference discipline on every clip** — each clip attaches its own INDIVIDUAL panels (Seedream exact copy for face panels; plain or 4K-upscaled crop otherwise), in order, plus the previous clip video from K ≥ 2. The panels carry identity across the piece.
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
- Attach the WHOLE sheet — ALWAYS decompose into this clip's INDIVIDUAL panels (`extract_panel`) and attach them one per panel, in order (Seedream exact copy for face panels; plain or 4K-upscaled crop otherwise). Name the panel range in the prompt; the model maps shots→panels.
- Upscale a FACE panel — a face panel's LAST model MUST be Seedream (an exact copy; at 4K, at Seedream's max size). Never run an upscaler after Seedream. Non-face panels: upscale at 4K (a raw sheet-panel is too soft), attach the plain crop otherwise.
- Attach anything beyond this clip's own individual panels + the previous clip video — no whole sheet, no other clips' panels, no separate identity refs (the panels carry identity).
- Add per-shot panel citations — the count line ("panels A to B") maps them; the model counts.
- Force the compact shape / minimal attachments onto a non-Seedance or non-reference-to-video model — that path uses its own craft skill's techniques (SCOPE note in STEP B).
- Hardcode `duration: 15` (STEP A owns timing).
- Search disk for the storyboard JSON (STEP 0 / INPUTS: metadata is the only auto-recovery; missing → sheet pixels, never an unrelated JSON).
- Compress a >15 s CLIP by dropping shots (STEP A fail-fast; a SHEET may exceed 15 s, a CLIP never).
- Render one clip per panel or per sheet — one per **CLIP** (STEP B).
- Invent, add, drop, reorder, split or merge shots (STEP B: shots come ONLY from THIS clip's JSON, in order; glued runs = one shot line).
- Describe an action with a vague verb — spell out its PHYSICS (trajectory, gravity, acceleration, contact, what-creates-what) and forbid the wrong reading, so Seedance doesn't float it or materialise details out of order; keep the mechanics consistent with the continuity matrix (STEP B "⚙️ DESCRIBE THE PHYSICS").
- Burn ANY text into the video, or copy sheet chrome (spoken lines are AUDIO).
- Attach a raw photoreal human face — or ANY panel with a face-part (partial, profile, from behind, small, blurred, reflected, eyes closed) — to Seedance (it rejects the WHOLE render → *"may contain likenesses of real people"*). **SUPER MANDATORY:** route EVERY such panel through an EXACT Seedream copy FIRST (pre-step), all of them up front — the Seedream image is what clears the filter. Missing even one panel fails the render. And remember the chained previous-clip VIDEO carries her face too: if a laundered render still rejects for likeness, swap the reference video for a faceless `extract_frame` anchor.
- `replace_panel` / modify the APPROVED sheet in place — `extract_panel` only READS crops; never write back to the original. Face fixes live in the separate Seedream copies, not in the sheet.
- Flip the viewpoint, or break causal order (force the viewpoint + negate the opposite; state only advances).
- For clips 2…N: forget to attach the previous clip and state it's a continuation (STEP B Part 2) — without it the model re-enacts the previous clip.
- Ignore the continuity matrix — read the per-shot `continuity` rows + LOCK when you read the storyboard, and restate carried-forward state in each Seedance shot line (STEP B "🎬 READ THE CONTINUITY MATRIX FIRST"); it's the raccord authority, not optional colour.
- Reset world state between clips (each clip opens in the previous clip's end state).
- Bake music into per-clip renders for ≥ 2 sheets (STEP C), or duck music reflexively (STEP D: only under voice).
- Ship a silent clip / use `withAudio: false` to drop music (STEP B).
- Render 16:9 for a vertical target (pass the platform `aspectRatio` every call).
- Concatenate outside the timeline, reuse/append a timeline, or finish without `show_timeline`-ing the TIMELINE (STEP D).
