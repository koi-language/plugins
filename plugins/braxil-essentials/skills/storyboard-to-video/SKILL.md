---
name: storyboard-to-video
description: Turning an approved STORYBOARD DIRECTLY into the FINAL video — there is NO keyframe/panel-sheet step; the storyboard's shots are grouped into clips and rendered straight to video. Model-AGNOSTIC (works with any model in the `video-generator` catalog) and prompt authoring is DELEGATED to `cinematic-video-prompt-engineer` (the house's best prompt engine). The storyboard JSON is the AUTHORITY (per-clip timing, per-shot action, dialogue, SFX, music, continuity). The identity/look ANCHORS — the character turnaround sheets + the set/location plates — are ALWAYS attached to lock consistency across clips (built here once if missing, then reused). Composition ALWAYS comes from the cinematic prompt. For each CLIP it assembles that clip's story brief (scene, shots-in-order, dialogue, continuity, duration, reference legend) from the storyboard + anchors, hands it to `cinematic-video-prompt-engineer` to author the cinematic prompt, then renders one video per CLIP with that prompt and stitches every clip back-to-back on a timeline. A clip is a group of consecutive shots (≤ the model's max clip length). Use whenever you have an approved storyboard and need the rendered video, or the user says "genera el vídeo" / "monta el vídeo del storyboard" / "haz la película", or otherwise asks to turn an existing storyboard into video. Pairs with `cinematic-video-prompt-engineer` (which authors each clip's prompt), `video-generator` (the authority on each model's params + per-model reference PREP) and `timeline-assembler` (which it delegates assembly to).
---

OUTPUT stage: an approved storyboard exists (JSON + the cast/set anchors); this skill **renders** each clip DIRECTLY (there is NO keyframe/panel-sheet step) and stitches all into the final film. It is **model-agnostic** — nothing here is tied to a specific video model. THREE delegations, non-negotiable:
1. **THE PROMPT → `cinematic-video-prompt-engineer` is the SOLE author.** 🔴 It, and ONLY it, decides and writes the prompt that goes to the video model. This skill (and the storyboard, anchors, sheet, continuity matrix, model card…) exist ONLY to give it the INPUT INFO it needs — this skill ASSEMBLES that input (the story brief) and hands it over. It NEVER decides, writes, edits, rephrases or "improves" prompt content itself; the final prompt is whatever cinematic returns. If something must appear in the prompt (a constraint, the reference legend, the continuity LOCK), you FEED it to cinematic as input — you never author it yourself.
2. **Per-model behaviour + reference PREP → `video-generator`** (its `references/models.md` cards). The card is the ONLY authority on what a model does, the params it accepts, and HOW its references must be prepared (raw as-is, a depth pass, a face-laundering pass, a blurred/processed previous clip, a file cap, etc.). This skill never bakes in a specific model's prep.
3. **Assembly → `timeline-assembler`** (track layout, fps/aspect inheritance, music ducking, transitions, subtitles, preview handoff).

Read each skill's SKILL.md / card before using it; don't re-derive. What THIS skill owns: reading the storyboard JSON, resolving the anchors (building them if missing), grouping shots into clips + durations, deciding WHAT references to attach, the `generate_video` tool call, music, and the timeline.

## 🎞️ THE MODEL REFERENCES ARE THE ANCHORS (there is NO keyframe sheet)
- **The identity/look ANCHORS = the character TURNAROUND sheets + the set/location PLATES.** These lock face, hair, wardrobe, and the world's look/palette across every clip. **They are MANDATORY on every render** — a text prompt, however good, does not carry a face; without them a multi-shot piece drifts ("same character, different face each clip"). Built here once if missing (see "Build missing anchors"), then reused across every clip.
- **Composition ALWAYS comes from the cinematic prompt** authored by `cinematic-video-prompt-engineer`. There is no composed panel sheet in this pipeline — nothing but the **ANCHORS** (turnarounds + plates, prepared per the model card) + the **cinematic prompt** ever reaches the model. Never put a panel image in `referenceImages`.

## 🛑 STEP 0: READ THE STORYBOARD JSON FIRST (MANDATORY, before any `generate_video`)
The storyboard JSON is the script. **When you read it, read the CONTINUITY MATRIX too** — the per-shot `continuity` rows `{ characters, objects, place }` + the story-wide `continuity` LOCK. Hold it in mind for every clip; it drives what state you restate in each clip's brief ("🎬 READ THE CONTINUITY MATRIX FIRST", STEP B). It is the raccord authority, not optional colour.
- The storyboard JSON path is given directly (task / `# WORKING AREA` active doc, or the storyboard established in the conversation). `read_file` it.
- ⛔ NEVER filesystem-search for a "matching" JSON (`shell ls .koi/storyboards/`, `recall_creations` to "find" it, reading every JSON and guessing): confabulation bug matched `soc2_compliance_explainer.json` to a pocket-watch story. The directly-given / conversation-established path is the ONLY link; never invent one.
- NEVER skip to a raw `generate_video` off an invented prompt.

## INPUTS
From the task description, or `step5_output.json` (create-video workflow):
- **`storyboard_path`** (the spine, effectively required): path to `~/.koi/storyboards/<id>.json`. AUTHORITY for per-shot `duration`, `action`, `continuity` = { characters, objects } (legacy: single `state` string), `dialogue`, `sfx`/`music`/`audio`, plus storyboard-level `synopsis` (premise), `continuity` (LOCK = story-wide invariants/negatives), `characters`, `lighting`. Transcribe `synopsis` + LOCK + per-shot `continuity`, don't drop.
- **`references` (the ANCHORS — always used):** the recurring subjects, each `{ alias: path-or-@handle }`, resolving to each character's **model-sheet TURNAROUND** and each **set/location PLATE**. Normally already persisted in the storyboard's `references` / the character/locations Library; resolve them (`@handle` → path). **If a needed anchor does NOT exist, build it here before rendering** (see "Build missing anchors").
- **`audio_plan` / `type`**: OPTIONAL (music need+brief, video type).
- **`aspect_ratio` (platform)**: the destination format. NOT a storyboard property — ALWAYS ask the user (STEP B, Step 0a).

No storyboard JSON → surface the error; never invent the source.

## STEP A: Group the shots into CLIPS and resolve each clip's duration
A **clip** = a group of consecutive shots rendered as ONE `generate_video`, ≤ the model's max clip length. **Chunk the storyboard JSON's shots yourself:** walk the shots in JSON order accumulating duration; cut a clip when adding the next shot would exceed the model's `D_max` OR cross a hard scene boundary. `noCutBefore`-glued shots (or shots sharing `number`) stay in the SAME clip (a continuous take). Number clips 1…N in order. Each clip = `{ clipIndex, shotIds, durationSec = sum of its shots' duration }`.

**Duration range: read from the tool, never hardcode:** `get_tool_info("generate_video")` → `duration` schema (whole seconds + `"auto"`; trust the tool for THIS model). Use `D_min`/`D_max`. Per clip: `clip.durationSec` clamped to `[D_min,D_max]`; cross-check == sum of its `shotIds`' `shot.duration`. No JSON durations → `D_max` AND surface uncertainty via `print`.

State per-clip durations before rendering (*"3 clips: 14 s, 10 s, 10 s"*). ⚠ **The storyboard total overrides any duration in the task/brief** (task "60 s" but storyboard sums 48 s → 48 s; no padding). Sole exception: an explicit hard-target → refit.

### ⛔ Fail-fast: a single CLIP longer than the model's max clip length is malformed
Sanity-check EACH clip against the model's `D_max`. Any clip > `D_max` → chunking bug; don't silently drop shots (*"hizo los 15 s pero solo de una parte"* bug). STOP and re-chunk so no clip exceeds `D_max`. Never auto-compress/truncate.

## STEP B: Render one `generate_video` per CLIP, SEQUENTIALLY with clip-chaining
> 🛑 BEFORE the first `generate_video`, in this ORDER: (1) activate **`video-generator`** and read its `references/models.md` (MANDATORY — how the tool + each model works); (2) choose the video MODEL and read its card in full (see "Model choice"); (3) ask the user (aspect + whatever the card implies — Step 0a); (4) resolve/build the anchors; (5) for each clip, activate **`cinematic-video-prompt-engineer`** to author the prompt.

Render SEQUENTIALLY, not parallel: each clip continues from the one before it (the seam inherits camera energy, world-state and momentum) and you can sanity-check before committing. Clip 1: no previous clip. Clip K ≥ 2: wait for K-1 to finish, verify its `savedTo`, then chain it (see "Clip chaining").

### 🚨 UNIVERSAL reference rules — EVERY clip, ANY model (non-negotiable)
Every `generate_video` clip MUST attach:
1. **The character TURNAROUND sheet of each character that PARTICIPATES in THIS clip — MANDATORY. Only the ones actually in this clip, NOT the whole cast.** Identity (face, hair, wardrobe, proportions) comes from these; WITHOUT them the characters drift. One per participating character. Plus the **EXTRAS GROUP SHEET** of any recurring unnamed group in the clip (crowd, caravan…) — without it the group re-rolls its look every clip.
2. **The set/location PLATE + any objects/props that appear in THIS clip** — only what's in frame for this clip. These carry the world's look/palette.
3. **🚫 NOT the composed panel sheet, and NOT extracted panels.** The composed sheet is NEVER put in `referenceImages` — composition comes from the cinematic prompt (the `cinematic-video-prompt-engineer` output), not from a panel image. And NEVER extract or attach panels one-by-one. *(The ONE grid that is allowed is the CONTINUITY SHEET built from the previous clip's real frames — see "Clip chaining". It records where the last clip ENDED; it prescribes nothing about this clip's composition.)*

**HOW each reference is PREPARED is dictated by the CHOSEN model's card** in `video-generator/references/models.md` — raw as-is, a transform (depth pass, face-laundering copy, blurred/processed previous clip), a file cap, etc. **This skill prescribes no specific prep — read the card and do what it says; if silent, attach as-is.** The WHAT above (anchors always; the composed sheet is NEVER a model reference; never one-by-one panels; never drop a character sheet) is non-negotiable on every model.

### Build missing anchors (fast path, or a character/set never sheeted)
If a needed anchor is not already persisted:
- **🙈 `metadata: { "visible": false }` on EVERY image you build here** (turnarounds, plates, and any per-model prep like a Seedream copy or depth pass). These are technical anchors/intermediates for the render, not user deliverables — keep them OUT of the creations drawer. They're still persisted as `references` and fully reusable. The only visible output is the final video.
- **Character turnaround** — resolve it from the character CARD first: each roster member's `characterId` → `~/.koi/characters/<id>.json` → its `sheet` (turnaround). If a needed character has no card/sheet, build one with **`generate_character_sheet`** (see the `characters` skill). **Prepare it per the chosen video model's card** (some models need it laundered/processed). Build once, reuse across every clip.
- **Set/location plate(s)** — resolve from the LOCATION CARDS: the scene's `locationIds` (an ARRAY — a scene can span several sets) → each `~/.koi/locations/<id>.json` → its `plate` (the establishing plate). On each clip, attach the plate(s) of the location(s) actually in frame for that clip so the set stays consistent. If a needed location has no card or the card has no `plate`, build one with **`generate_location_plate`** (see the `locations` skill) and persist it. A plate carries no face → no laundering.
- Persist what you build (via `update_storyboard`, patching just `references` — never `save_storyboard`) so future runs re-use it.

### Attach references
> On EVERY clip attach exactly what the UNIVERSAL rules list, prepared per the model card, and nothing more:
> 1. **The TURNAROUND of each character in THIS clip** (aliased by label e.g. `HERO_A`) **+ the EXTRAS GROUP SHEET of each recurring group** (e.g. `EXTRAS_CARAVANA`). IDENTITY.
> 2. **The set/location PLATE + props in frame** (e.g. `SET_suite`, `prop_bottle`). The world's look.
> 3. **The immediately-previous clip's CONTINUITY SHEET (K ≥ 2 ONLY, every model)** — built with `build_continuity_sheet`, prepared per the card (Seedance: laundered through Seedream; every other model: as-is). See "Clip chaining".
> 🚫 **NOT the composed PANEL sheet** (composition = the cinematic prompt) and **NOT extracted panels**. (The continuity sheet of item 3 is not this — it is the previous clip's end state, not a composition source.)
> ⚠️ **These references must be the CURRENT ones.** If the user changed a set or a character's look, the plate/turnaround should have been regenerated upstream. If what you resolve still shows the OLD look while the story wants the new one, STOP and say so — attaching a stale reference is what makes the change come back missing. Never paper over it in the prompt.
> ⚠️ **Respect the model card's file / reference caps.** Over the cap → drop the least-load-bearing object refs first, never a character turnaround. The tool REJECTS (`success:false`) if the prompt cites a reference not attached, so cite only what you attach.
>
> **In the prompt, say what each reference IS** (part of the binding lines below): e.g. *"`HERO_A` is her character turnaround: take her face, hair and wardrobe from it. `SET_suite` is the location plate: match the room's look, palette and lighting."*

Per CLIP (global `clipIndex` order) call `generate_video` with:
- **`prompt`**: authored SOLELY by `cinematic-video-prompt-engineer` (this skill feeds it the story brief + the mandatory constraints as input); used VERBATIM, never edited here. See "Per-clip prompt".
- **`referenceImages`**: the turnaround of each character/group in the clip + the set/prop refs it needs (each prepared per the card) + on K ≥ 2 the CONTINUITY SHEET of clip K-1 (alias `prev_state`, prepared per the card). 🚫 NOT the composed PANEL sheet, no extracted panels, no other clips' panel sheets.
- **`referenceVideos`** (K ≥ 2, OPTIONAL, only if the card supports a video reference AND the model has no likeness filter): `[{ alias: "prev_clip", path: <K-1's savedTo> }]` — extra pacing/camera-energy signal on top of the sheet, never a replacement for it (see "Clip chaining").
- **`duration`**: the CLIP's resolved value, whole second in `[D_min,D_max]`. NOT hardcoded.
- **`aspectRatio`**: 🚨 the user's answer from Step 0a — NOT inferred from the storyboard. Same on every clip of a pass.
- **`quality`**: the model card's highest sensible tier (e.g. `"high"`).
- **`withAudio: true`**: ALWAYS unless the card names a different audio control (omitting = silent = hard failure). Controls DIEGETIC sound, NOT music. Exclude music ONLY via the closing Audio line, never `withAudio: false`.
- **`saveTo: <directory>`**.

### Model choice (NOT hardcoded)
> **🔴 Step 0 — ACTIVATE `video-generator` BEFORE ANYTHING ELSE (MANDATORY, ABSOLUTE FIRST).** Before you make ANY decision, pick or even NAME a model, reason about what it can do, OR ask the user anything, **activate `video-generator` and READ its `references/models.md`.** Its cards are the ONLY authority on what each model does, its params, and how its references must be prepared. **NEVER state, assume, or reason about a model's behaviour without having READ its card.** Model not in the cards → don't propose it. This gate comes BEFORE Step 0a.
> **Step 0b — PICK the best model for THIS clip from the cards, then READ its card in full.** Never from memory, a model name, or a fixed label. Several hard-cut shots in a clip → the card must mark the model able to render them in one generation. Let the card define capabilities, limits, params and reference PREP.
> **Step 0a — ASK THE USER (MANDATORY, gating).** Always ask **aspect ratio** (a VIDEO decision, NOT a storyboard property — the same storyboard → many formats): which format(s) via `prompt_user`/`prompt_form`, never a `print`. Beyond that, ask ONLY what the card shows the model exposes. Do this ONLY here (at video generation), NEVER at storyboard time. Several formats → several passes; ask once, up front. Don't generate without this answer.
> **Prompt WORDING is authored by `cinematic-video-prompt-engineer` for EVERY model.** If the card lists model-specific phrasing constraints (a param the prompt must name, a camera limit, a token cap), pass them to `cinematic-video-prompt-engineer` as extra brief input — do NOT let the card re-author the prompt, do NOT restate its specs here.
> **Division of labour:** `cinematic-video-prompt-engineer` is the SOLE author of the prompt (wording + cinematography + the constraints it's fed); THIS skill owns the STORY BRIEF + mandatory constraints it FEEDS that skill, the anchors + prep (per card), and the tool call. It does NOT author, edit or "improve" the prompt — cinematic does, exclusively.

### Per-clip prompt — the WORDING is authored by `cinematic-video-prompt-engineer` (not here)
> This skill owns the PIPELINE and the REFERENCES; the CINEMATIC WORDING of every clip's prompt is produced by **`cinematic-video-prompt-engineer`** (the house's best prompt engine). You do NOT hand-write the shot prose. Per clip, in order:

**1. Activate `cinematic-video-prompt-engineer`** (after `video-generator` + the model pick).

**2. Hand it THIS clip's STORY BRIEF — assembled from the storyboard JSON, in English, never from sheet pixels.** The brief is raw material, not a finished prompt. For THIS clip only:
- **Scene / medium + premise** from `style` / `synopsis` — the one-line look + who/what is in frame. IDENTICAL across every clip of the piece (paraphrasing drifts the look).
- **The clip's shots IN JSON ORDER**, one entry each: intended framing / angle / camera move (when the JSON carries it), the shot's `action` compressed to its ONE essential physical beat, its `dialogue` VERBATIM in the language spoken, its notable `sfx`. `noCutBefore`-glued shots (or shared `number`) = ONE entry (a continuous take, no internal cut).
- **⚠️ Framing/composition lives ONLY in this brief / the cinematic prompt — ALWAYS.** Be explicit about each shot's shot-size, angle and camera move so cinematic (and the model) have the composition from words alone.
- **🔴 STAGING / AXIS LOCK — a fixed-location multi-character scene (dinner table, car, sofa…) MUST carry an explicit screen-geometry lock, or the model flips who is where on every hard cut (silent 180-degree cross — the reported "she was beside the father, two shots later across from him" bug).** Feed cinematic, from the storyboard's `continuity` LOCK, the scene-wide staging line (camera stays on ONE side; each character's fixed SCREEN position — screen-LEFT / screen-RIGHT / far-end) and require it VERBATIM as a hard rule in EVERY clip. AND per shot in the brief, restate the visible character's screen side + facing (e.g. *"MS of MADRE — still the screen-LEFT person; HIJA stays screen-RIGHT"*). An unstated close-up is exactly where the model crosses the axis. If the storyboard LOCK has no staging line for such a scene, DERIVE it from shot 1's blocking before briefing cinematic.
- **The continuity matrix for these shots** — the per-shot `continuity` rows `{ characters, objects, place }` (non-default state that still holds) + the story-wide `continuity` LOCK. Tell cinematic to KEEP this state in the matching shot and never reset or invent it.
- **The PHYSICS of each action** — where an action has real mechanics (trajectory, gravity, contact, something drawn/created), spell them out (actor + force/mass + arc + acceleration + contact + visible endpoint) and forbid the wrong reading (no floating; nothing appears before its cause reaches it). A loose verb makes the model invent wrong mechanics.
- **Fixed constraints cinematic must NOT re-decide:** duration is `<D>` s (STEP A — do NOT re-derive from content); the shot list is EXACTLY these `<N>` shots (do NOT re-select, add, drop, reorder, split or merge — render THESE, cinematically); target format is `<aspectRatio>`.
- **The reference legend** — what images are attached and what each IS: each character turnaround (e.g. `HERO_A`) = identity; each set/location plate (`SET_x`) = the world's look/palette/lighting; each prop/product = match exactly. (No composed sheet is attached — do not reference one.) The references are identity/look anchors, NOT start frames.

**3. Ask it for the COMPACT/DIRECT output, in ENGLISH.** Invoke cinematic in its direct final-prompt mode (its `精简模式`: "final prompt only, no diagnosis/strategy") and require the final prompt in **English** — keep its standardized shot-size / camera-move abbreviations (ECU, CU, MCU, WS, MS, Dolly In/Out, Pan, Tilt, Track, Zoom…); spoken dialogue lines stay in their ORIGINAL language, in quotes. You want the copy-ready prompt, not the workshop sections.

**4. Take cinematic's final prompt and use it as the `generate_video` `prompt` VERBATIM.** You already fed it every mandatory constraint (below) as INPUT, so its returned prompt carries them — do NOT append to, edit, rephrase or "wrap" it. If a required constraint is missing from what it returned, feed it to cinematic again and re-ask — never patch the prompt yourself. cinematic is the sole author.

**Faithful, no invention (verify cinematic's output, don't rewrite it).** Before rendering, state *"this clip has N shots"* and confirm cinematic's prompt renders exactly those N, in JSON order, with every dialogue line and every carried-forward continuity state present. If it dropped a shot, changed the count, re-timed the clip, or invented a beat, send it back to cinematic with the constraint restated — never fix it by editing the prompt yourself.

> ### 🎬 READ THE CONTINUITY MATRIX FIRST — before assembling the brief
> The **continuity matrix** is the per-shot `continuity` rows `{ characters, objects, place }` PLUS the storyboard-level `continuity` LOCK. It is the authority on WHAT STATE holds in each shot, and many models silently RESET any state they aren't told about (character back on the ground, prop un-broken, room clean again). For THIS clip, walk the matrix rows and carry what they say INTO the brief:
> - **Per-shot row → the matching shot entry.** A NON-DEFAULT state that still holds (someone standing ON the cans, a bottle already half-empty, a melted hole, a specific `place`) goes in that shot's brief entry even if its `action` text dropped it. The matrix is authoritative; transcribe it. Fill `place` when a close-up would lose the setting.
> - **LOCK → the closing "Hard rules" binding line**, verbatim, once.
> - **Never invent or "fix" state.** Only re-inject state the matrix established. Contradictory consecutive rows = a source bug: brief the physically coherent reading the synopsis/LOCK imply and surface the conflict; never render the impossible state.

### Mandatory constraints you FEED CINEMATIC (part of the brief — cinematic writes them into the final prompt; this skill never appends them itself)
These are INPUT requirements handed to cinematic, NOT text this skill adds to the prompt. Require cinematic to include, verbatim where noted, on EVERY clip (then verify per "Faithful, no invention" and send its output as-is):
- **Reference legend** naming each attached reference as above, plus the shot-count line: *"`<N>` shots, hard cuts, perfect continuity, in this exact order."* (Framing is already in the per-shot cinematic text — the composed sheet is not attached, so there is no panel map.)
- **Anchors-are-action-refs line** (once): *"the attached character/set references are identity/look anchors, not starting frames: begin each shot naturally and flow the motion through it."*
- **Closing audio note**: diegetic sound only / natural ambience; for ≥ 2 clips-with-separate-music add "music is on a separate timeline track, not part of this clip." (`withAudio: true` is a tool param, never prompt text.)
- **Hard rules** from the LOCK (the few story-wide invariants/negatives the model won't infer), verbatim, once.
- **No burned-in text**: spoken lines are AUDIO, never captions; never copy sheet chrome.
- For clips K ≥ 2: the **continuation line** (see "Clip chaining").

### Clip chaining (clips 2…N): continue from the previous clip
Each clip after the first continues the one before it. **The CONTINUITY SHEET is the chaining mechanism on EVERY model** — a still grid of the previous clip's real frames carries the character SCREEN POSITIONS precisely, which is the thing that drifts between clips (the reported "the boy was on her right, next clip on her left" bug):

1. **`build_continuity_sheet`** on clip K-1, passing `cuts` = its INTERIOR shot boundaries in seconds (the cumulative shot durations you already have from the storyboard — shots of 3.5/3/3/3/2.5 s → `cuts: [3.5, 6.5, 9.5, 12.5]`; omit `cuts` for a single-take clip). It returns a 2-column × N-row grid (row = take, left cell = its first frame, right cell = its last) plus a `promptHint`.
2. **PREP per the model card.** Only models with a **likeness filter (Seedance)** need one: **launder the sheet through Seedream** exactly like a character turnaround — a 1:1 reproduction with a FULL re-description of what the grid shows (per `video-generator/references/usage/seedance.md`). The raw sheet carries the same real faces the filter rejects. **Every other model takes the sheet AS-IS** — no clone, no blur, no processing.
3. **Attach it as ONE reference image** (alias `prev_state`) and paste the tool's `promptHint` VERBATIM into the prompt — it describes the exact layout that was built, so the description can never drift from the image. The hint already tells the model these are frames of the immediately-preceding clip, which cell it continues from, and never to render the grid itself.

- 🙈 `metadata: { "visible": false }` on the sheet (and on its laundered copy when there is one) — technical anchors, not deliverables.
- This sheet is the ONE composed grid that IS a legitimate reference: it records the previous clip's END STATE, it does not prescribe this clip's composition (which still comes only from the cinematic prompt). The storyboard's composed PANEL sheet remains banned.
- ⚠️ **Not the same thing as the storyboard's CONTINUITY MATRIX** (the per-shot `continuity` rows `{characters, objects, place}`, STEP 0). That matrix is TEXT inside the JSON and drives what state each brief restates; this sheet is an IMAGE of the previous clip's actual frames. Both are used, they never substitute for each other.
- **Video reference of the previous clip: OPTIONAL, and never on a likeness-filter model.** When the card supports `referenceVideos` and the model has no filter, you MAY add the clip itself as `prev_clip` (`Video 1`) on top of the sheet for pacing/camera energy — the sheet still carries the positions. Never attach a blurred copy as the positional anchor: the blur preserves only motion, pacing, palette and audio, which is what made this fail before.

**ALWAYS also SPELL OUT the opening state in words.** A reference SHOWS; the prompt is what the model OBEYS. "Do not reset the positions" is useless without saying what they are — and you authored the storyboard, so you know them. Take the last shot of clip K-1 and state its screen sides literally, e.g. *"abre exactamente donde terminó el clip anterior: HERMANA en screen-LEFT, HERMANITO en screen-RIGHT, manos de dentro cogidas, caminando hacia cámara, tramo central del pasillo"*. Screen sides, never a character's own left/right (see the axis/screen rules in `storyboard/references/authoring-guide.md`).

Then add a short continuation line right after the scene line:
> *"`prev_state` is a grid of frames from the immediately preceding clip of this same film (see its description above). This clip continues DIRECTLY from that clip's end: same lighting, character screen positions, momentum and world-state — do not reset. Match its pacing and camera energy. Do NOT repeat or re-enact its shots; render only the NEW shots below."*

If you ALSO attached the clip as a video reference, name it too (*"`Video 1` is that same preceding clip"*). Cite ONLY the immediately-previous clip (K-1). Omit the whole part for clip 1.

## STEP C: Music track (single, full-length, only when needed)
Audio plan calls for music AND **≥ 2 clips** → ONE separate track (per-clip music thumps every boundary; independent renders can't keep a continuous melody across seams): ONE `generate_audio`, `type: "music"`, `duration: <total = sum of all clip durations>`, `prompt` from the type's music brief + tone. Single clip (no seams) → music inside the clip render is fine, skip. Voiceover-only / SFX-only → no music, skip.

## STEP D: Assemble the timeline (concatenate every clip into one video)
Follow `timeline-assembler`.
1. **Always `create_timeline` a NEW timeline**: one fresh per video; NEVER reuse/append/overwrite. Descriptive `name` + target `aspectRatio`; do NOT pass fps/width/height (inheritance). Keep the returned `timelineId`.
2. **V1: concatenate clips in order, back-to-back, each clip's OWN duration** (cumulative cursor):
   ```
   cursorMs = 0
   for clip in clips (in clipIndex order):
       add_clip_to_timeline(track="V1", path=clip.path, startMs=cursorMs, durationMs=clip.durationSec * 1000)
       cursorMs += clip.durationSec * 1000
   ```
   `add_clip_to_timeline` auto-detects each clip's audio stream, do NOT pass `hasAudio`.
3. **A2: music** (if STEP C): one clip at `startMs: 0`, `durationMs: totalMs`. **Duck ONLY where it competes with voice, from actual audio, not reflexively:** voiceover/dialogue → duck to ≈ −28 dB (`set_clip_volume(<musicClipId>, { change: { gain: 0.04 } })`, or `volumePoints` for speaking stretches); NO-voice sections → do NOT duck. See assembler's "Audio mixing levels".
4. (Optional) subtitles for tutorial/explainer per the assembler's "Subtitles" matrix.
5. **Hand-off: ALWAYS end by showing the TIMELINE.** `show_timeline({ id })` — pass the id from `create_timeline`, nothing else. Only if the user explicitly asks to export: `render_timeline({ id })` → `show_video` the rendered mp4. (koi/CLI surface: `show_result({ resourceType: "timeline", timelineId })`.)

Final length = sum of per-clip durations (= storyboard total when present). Concatenation is timeline-only: NEVER `ffmpeg concat`.

## Continuity across clips (multi-shot lock)
Keep these verbatim across clips:
1. **Identical subject nouns in every shot and every clip** — the SAME short noun phrase ("the three rock-skinned aliens"); re-describing re-casts them. (Part of the scene line cinematic copies verbatim.)
2. **Same anchor discipline on every clip** — each clip attaches the turnaround of each character/group in it + the plates in frame (prepared per the card), plus the previous clip's CONTINUITY SHEET from K ≥ 2. (Never the composed PANEL sheet.) The turnarounds carry identity across the piece (reuse the SAME sheet per character everywhere).
3. **Lock the scene line + lighting phrasing verbatim** across all clips (cinematic copies, never paraphrases).
4. **Respect the model's per-clip setup/complexity limits** (from its card). Exceed → re-chunk / split into two chained calls.
5. **Clip chaining:** the previous clip's CONTINUITY SHEET on every model (`build_continuity_sheet`, prepped per the card) + the continuation line + the opening state SPELLED OUT in screen sides.
6. **One master audio bed:** music OFF the clips (separate track), only diegetic SFX per shot.

## Voice consistency across clips (read once)
With `withAudio: true` voiceover is per clip; models that match voice to the visible character give high-but-not-guaranteed consistency with the same character ref across clips. If voice audibly drifts, fallback: `withAudio: false` on every clip (silent), generate ONE TTS pass of the whole script via `generate_audio` with a fixed `voice`, lay as a second audio track. Trades lip-sync precision for identical voice; use only when drift shows.

## Iteration
- **Clip re-roll:** `generate_video` again for that clip, same references, feed cinematic the SAME brief with only the affected shot(s) revised; keep the scene line, continuation line, closing note identical. K ≥ 2 `prev_state` still comes from K-1; **if K-1 was re-rolled, REBUILD its continuity sheet from the new render** (and re-launder it on Seedance) — a sheet from the discarded take anchors the wrong positions.
- **Total duration change:** re-resolve per-CLIP durations (STEP A); relative weighting usually scales, don't uniformly scale unless the user said so.
- **Model change:** re-read the new model's card (params + reference prep can differ) and re-render; the story brief you feed cinematic is unchanged, only the reference prep + tool params shift.

## Don't (terse checklist; each detailed in full above)
- Hand-write the clip prompt — the WORDING is authored by `cinematic-video-prompt-engineer` from the brief you feed it (STEP B).
- Bake in any specific model's behaviour, params, or reference PREP — the `video-generator` card is the single source of truth; this skill is model-agnostic.
- Skip the identity/look ANCHORS (turnarounds + plates) — they are MANDATORY on every render (🎞️ + STEP B).
- Put any panel/keyframe image in `referenceImages` — there is no keyframe sheet in this pipeline; the only references are the anchors, and composition comes from the cinematic prompt.
- Hardcode a `duration` (STEP A) or a model's max clip length (read `D_max` from the tool).
- Search disk for the storyboard JSON (STEP 0: given path or sheet metadata only; never an unrelated JSON).
- Compress a clip longer than the model's max by dropping shots (STEP A fail-fast).
- Render one clip per shot — one per **CLIP** (a group of consecutive shots).
- Let cinematic invent, add, drop, reorder, split or merge shots, or re-time the clip (STEP B).
- Feed cinematic a vague verb for a physical action — spell out its PHYSICS, consistent with the continuity matrix (STEP B).
- Burn ANY text into the video (spoken lines are AUDIO).
- Attach a stale (old-look/identity) reference (STEP B "Attach references").
- Flip the viewpoint, or break causal order.
- For clips 2…N: forget the previous clip + the continuation line (Clip chaining).
- Ignore the continuity matrix (STEP B "🎬 READ THE CONTINUITY MATRIX FIRST").
- Reset world state between clips (each clip opens in the previous clip's end state).
- Bake music into per-clip renders for ≥ 2 clips (STEP C), or duck music reflexively (STEP D).
- Ship a silent clip / use `withAudio: false` to drop music (STEP B).
- Render a format other than the user's answer (pass the Step 0a `aspectRatio` every call).
- Concatenate outside the timeline, reuse/append a timeline, or finish without `show_timeline`-ing the TIMELINE (STEP D).
