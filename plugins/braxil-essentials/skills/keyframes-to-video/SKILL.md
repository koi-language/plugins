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
- **`references`**: OPTIONAL manifest of recurring subjects, each `{ alias: path-or-@handle }`, e.g. `{ hero_character: "/…/leo.png", product_pack: "@acme_bottle" }`. ✅ On the **Seedance reference-to-video + storyboard** path (the default) these are the IDENTITY SOURCE used to build each character's **model-sheet TURNAROUND**: resolve the in-scope character refs (`@handle` → path) and pass them as Image 1 when generating the turnaround, then launder it through Seedream and attach it alongside this clip's DEPTH-MAP SHEET (STEP B). No entry for a character → generate its turnaround from the storyboard's `characters` description (see PRE-STEP §2).
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

**Several panels can be ONE shot (one take, no internal cut): animate THROUGH.** This happens when consecutive shots are flagged `noCutBefore` (or share `number`) = a glued plano secuencia authored in the JSON → ONE SHOT line that cites the whole panel range, moving smoothly, NO internal cut. A real cut (a new SHOT line) falls ONLY where the JSON is NOT glued. (Note: panels are now **one per shot** — there are no automatic start/mid/end camera-move keyframe panels anymore; the only many-panels-one-take case is `noCutBefore`.) So **the number of shots in a clip = number of takes**, and each shot carries exactly one panel.

**Render SEQUENTIALLY, not parallel**: each clip continues from the one before it, so the seam inherits camera energy, world-state and momentum, and you can sanity-check before committing. Clip 1: no previous clip. Clip K ≥ 2: wait for K-1 to finish, verify its `savedTo` exists, then chain it (see "Attach references" + prompt part 2).

### ⚠️ SCOPE: the compact shape + minimal attachments below are the SEEDANCE reference-to-video + storyboard path
Everything from here to the end of STEP B — the "attach only the clip's own individual panels + the previous clip" rule AND the compact per-clip prompt shape — is written for **the chosen model being a Seedance-class model doing REFERENCE-TO-VIDEO, driven by a storyboard** — the default here because it's the only multi-shot-capable path today (you still choose it on merit from the model cards, not from a label). If you end up on a **different model** (no Seedance-class model available, a non-reference-to-video model, or no storyboard to anchor to), this is NOT how you compose: follow that model's own craft skill + the `video-generator` skill, whose techniques for references and prompt shape differ (e.g. other models often need explicit character/product identity refs and a fuller brief). Don't force this compact/minimal-attachment shape onto a model it wasn't written for.

### 🧩 PRE-STEP (before attaching): the clip's SHEET → ONE depth map + the CHARACTER SHEET → Seedream

> 🧭 **THE FORMULA — what you attach per clip:**
> 1. **This clip's OWN sheet, WHOLE and UNCROPPED, with ONLY the CHARACTERS converted to DEPTH-MAP figures** (one image) — sets, backgrounds, props, objects and lighting stay EXACTLY as rendered, photoreal and untouched; every person becomes a grayscale depth-gradient silhouette in their exact pose and position. It carries the SCENE STRUCTURE **and the world's real look** of every panel at once — only the characters are structure-only. 🚫 The depth treatment NEVER touches objects or décor: characters only.
> 2. **The CHARACTER SHEET(s) — a model-sheet TURNAROUND per character appearing in the clip (2×4: 4 full-body views + 4 head close-ups) — PLUS the EXTRAS GROUP SHEET(s) for any recurring unnamed group in the clip (crowd, caravan, soldiers, crew…; one-row lineup built upstream in `storyboard-to-keyframes` Step 2b §1b)**. 🚨 **These, and ONLY these, are MANDATORY through Seedream** — they carry every face you attach, and a raw photoreal face gets the whole render rejected. A clip with extras but no group sheet re-invents the group's faces/wardrobe on every clip: if the group recurs and no sheet exists, build it (Seedream) and persist it before rendering.
> 3. **The OBJECT / LOCATION references the clip actually needs** — the set plate ("el plató"), a key prop, a product pack, etc., as already generated upstream. Attach them as they are: **no Seedream pass needed** (no faces → the filter never fires on them). Only what this clip genuinely needs, not the whole library.
>
> 🚫 **DO NOT `extract_panel`.** No per-panel crops, no per-panel depth maps. The sheet goes in WHOLE — exactly as it is, untouched except for the depth conversion — and the characters go in as Seedream'd turnaround sheets. Decomposing into individual panels is the OLD method and is now FORBIDDEN on this path.
>
> **Why it works — TWO reasons, and the first is the important one:**
> - **🔗 CONTINUITY of the performance + FIDELITY of the world.** Depth-mapping the CHARACTERS leaves their performance unpinned — no literal still to snap to, so motion flows shot to shot — while the photoreal sets/props/lighting anchor the world's exact look, which a full-sheet depth map used to throw away (wrong décor, wrong palette, wrong props). Characters: structure guides. World: the render must match what you see.
> - **🛡️ The face filter.** The characters on the sheet are depth silhouettes — **no face at all** — so the likeness filter cannot fire on it. Identity comes from the character turnarounds instead — those are Seedream images, which is what clears the filter.

Per clip:

1. **Characters-only depth pass on the SHEET** — `generate_image` in EDIT mode with **this clip's whole sheet** as the reference image. **🔥 NO CROPPING, NO WARPING, NO RE-FRAMING: the sheet must come back EXACTLY as it is** — same grid, same panels in the same cells, same composition inside each panel, same photoreal sets/props/lighting. **ONLY the people change.** Pass the sheet's own `width`/`height`/`aspectRatio` so it returns at the same shape and size. **Use this prompt (verbatim):**
   > `Repaint ONLY the PEOPLE in this image as grayscale DEPTH-MAP figures: each person becomes a smooth gray depth gradient (nearer parts lighter, farther parts darker) with NO facial features, NO skin or clothing texture and NO colour — a clean depth-shaded silhouette in their exact pose, position and framing. EVERYTHING ELSE — sets, backgrounds, props, objects, vehicles, animals' surroundings, lighting, colours, the grid of panels and every panel's composition — stays EXACTLY as it is, photoreal and untouched, 1:1. Do not move, add, remove, re-frame, merge or restyle anything.`

   (The character depth figures are APPROXIMATED by an image model, not a metric depth pass — accepted and intended; they only have to convey pose, blocking and camera distance. Objects and décor are NEVER depth-mapped.)

2. **The CHARACTER SHEET(s) through Seedream** — the actors' fichas: face, hair, wardrobe, proportions.

   **♻️ FIRST look for the turnaround upstream — normally it ALREADY EXISTS.** `storyboard-to-keyframes` (Step 2b) builds one per character **with Seedream** before rendering the sheet and persists it in the storyboard's `references` / the `characters` Library. Resolve it (`@handle` → `resolve_handle`) and **reuse it as-is: it was BORN from Seedream, so it already clears the face filter — no second laundering pass, and never regenerate it (that drifts identity).** Only build one here if it genuinely does not exist:

   **📐 A character sheet is a MODEL-SHEET TURNAROUND, generated per character — you REPRODUCE the character into it.** One sheet per character, `generate_image`, with that character's reference image (from the storyboard's `references` / `scene.references`, `@handle` → `resolve_handle`, or the character Library) as **Image 1** so the identity matches. **Exact layout — 2 rows × 4 columns, wide (16:9):**
   - **Top row** = four FULL-BODY standing views: front, right-side profile, left-side profile, back.
   - **Bottom row** = four HEAD-AND-SHOULDERS close-ups: front, three-quarter, side profile, back of the head.

   **Prompt template (fill the `<…>` from the storyboard's `characters` roster — build, age, hair, wardrobe, accessories):**
   > `A photorealistic character model-sheet turnaround of ONE <male/female> character on a plain neutral seamless grey studio backdrop, even flat studio lighting. Match the face and identity to the character in Image 1. Layout: two rows by four columns. Top row = four full-body standing views: front, right-side profile, left-side profile, and back. Bottom row = four head-and-shoulders close-ups: front, three-quarter, side profile, and back of the head. <CHARACTER DESCRIPTION: build, age, hair, facial hair, wardrobe, accessories, footwear>. Keep the face and build IDENTICAL across all eight views. Clean production character-reference sheet aesthetic, photorealistic, no text, no numbers, no logos, no watermark.`

   - **No reference image for that character?** Compose the description from the storyboard's `characters` roster + how they read in the panels, and generate the turnaround from that (drop the "Match the face and identity to the character in Image 1" line).
   - **Build each character's turnaround ONCE and reuse it for every clip** — regenerating per clip drifts identity. Attach only the characters that appear in the clip being rendered.
   - **🚨 SUPER MANDATORY — every character sheet must BE a Seedream image before it is attached.** Built upstream with Seedream (Step 2b) → it already is one: attach directly, no second pass. Came from anywhere else (user upload, another model) → launder it: `generate_image` EDIT with the **Seedream edit model — pick its CURRENT slug from the `image-generator` skill's catalog, never hardcode a slug here** (Seedream specifically is what clears the downstream face filter; the exact version can change) — the sheet as reference, 1:1. A Seedream image CLEARS Seedance's face filter; a raw photoreal face does NOT — and these sheets hold the ONLY faces you attach, so skipping it on even one gets the whole render rejected with *"image_urls: may contain likenesses of real people"*. **Prompt (verbatim):**
     > `Reproduce this reference image exactly, as a faithful 1:1 copy: identical subject, face, identity, expression, pose, framing, composition, lighting, colours and background. Do not restyle, beautify, age or alter the face in any way; do not add, remove or move anything. Output the same image.`
   - Whichever route, the turnaround is built ONCE per character and reused across every clip (same identity everywhere, fewer calls).

3. **Gather the OBJECT / LOCATION references this clip needs** — the set/location plate ("el plató"), key props, product packs. These were already generated upstream (storyboard `references` / `scene.references` / Library; resolve `@handle` → path). **No extra pass on them: attach as-is.** They carry no face, so Seedream is NOT required (and not useful) here. Pick only what is actually in frame for this clip.

4. **The depth + Seedream passes run IN PARALLEL** (independent). Set **`metadata: { "visible": false }`** on both intermediates — technical prep, not user output. (Prep only; it does NOT relax the SEQUENTIAL `generate_video` rule, which chains clips.)

The attach list is then: **the depth-map SHEET (characters-as-depth, world photoreal)** + **the Seedream'd TURNAROUND of each character in this clip** + **the Seedream'd EXTRAS GROUP SHEET(s) for any recurring group in this clip** + **the object/location refs the clip needs** (as-is, no Seedream). The RAW sheet (with photoreal faces) is NEVER attached, and panels are NEVER extracted.

### Attach references (Seedance reference-to-video + storyboard) — the DEPTH SHEET + the CHARACTER SHEET, NOTHING ELSE
> 🛑 On EVERY clip attach exactly these, and nothing more:
> 1. **This clip's DEPTH-MAP SHEET** (from the pre-step) — ONE image, whole and uncropped, alias e.g. `depth_sheet`. Sets, props and lighting on it are the REAL look (match them); the characters on it are depth silhouettes = STRUCTURE only (pose, blocking, camera distance — their look comes from the turnarounds). **Never attach the RAW sheet (it carries photoreal faces), never extract panels**, and **never attach another clip's sheet**. The prompt names the panel range ("panels A to B") and the model maps shots→panels itself.
> 2. **The Seedream'd TURNAROUND SHEET of each character appearing in THIS clip** — one per character, aliased by character label (e.g. `HERO_A`) — **and the Seedream'd EXTRAS GROUP SHEET of each recurring unnamed group in THIS clip**, aliased by group label (e.g. `EXTRAS_CARAVANA`). They are IDENTITY: the depth sheet deliberately carries no look, so faces, hair, wardrobe and proportions all come from here — for the extras too, or the group re-rolls its look clip to clip. Attach only the characters/groups actually in this clip.
> ⚠️ **These references must be the CURRENT ones.** If the user changed the set/décor or a character's look at any point, the plate / turnaround should have been regenerated and persisted upstream (`storyboard-to-keyframes` § Fixing panels). If what you resolve here still shows the OLD décor or the OLD identity while the panels show the new one, STOP and say so — attaching the stale reference is exactly what makes the video come back with the change missing. Never paper over it by editing the prompt.
>
> 3. **The OBJECT / LOCATION references this clip needs** — the set/location plate, key props, product packs (already generated upstream; resolve `@handle` → path). Alias them meaningfully (e.g. `SET_suite`, `prop_bottle`). Attached AS THEY ARE — **no Seedream pass** (they carry no face). Attach only what the clip needs; skip anything not in frame.
> 4. **The immediately-previous clip as a video (K ≥ 2 ONLY)**: `[{ alias: "prev_clip", path: <K-1's savedTo> }]` in `referenceVideos`. IMMEDIATE predecessor only — never earlier clips. ⚠️ **If (and ONLY if) the previous clip shows PHOTOREALISTIC human faces** — photoreal/live-action style with characters on screen; the case that trips Seedance's likeness filter — attach a **BLURRED copy** instead of the raw clip. Make it locally with ffmpeg via `shell` (no model call, seconds): `ffmpeg -y -i <prev.mp4> -vf "gblur=sigma=25" -c:a copy <prev>_blur.mp4`. The blur defeats the likeness detector while PRESERVING everything the chain needs: motion, pacing, camera energy, palette, world-state AND the audio track. Stylized looks (3D animation, anime, claymation…) or clips with no people on screen don't trip the filter: attach the raw clip. If a raw-clip render still comes back rejected for likeness, that's the signal you misjudged — re-send with the blurred copy.
>
> That's the attachment list: the depth sheet + this clip's character turnarounds + the object/location refs it needs (+ previous clip for K ≥ 2). ⚠️ Seedance caps at **12 files per generation** — if you'd exceed it, drop the least-load-bearing object refs first, never a character turnaround or the depth sheet. The tool REJECTS (`success:false`) if the prompt cites a reference not attached, so cite only these. Clip 1 has no previous clip.
>
> **In the prompt, say what each reference IS** so the model uses them correctly — e.g. *"`depth_sheet` shows this clip's panels (panels 4–7): the sets, props and lighting on it are the real look — match them; the PEOPLE on it are grayscale depth figures — use them only for pose, blocking and camera distance, never for look. `HERO_A` is her character turnaround sheet: take her face, hair and wardrobe from it. `SET_suite` is the location plate: the room must match it."*

Per CLIP (global `clipIndex` order) call `generate_video` with:
- **`prompt`**: per "Per-clip prompt (COMPACT)" below; addresses ONLY the shots/panels in THIS clip.
- **`referenceImages`**: this clip's DEPTH-MAP SHEET + the Seedream'd TURNAROUND of each character in the clip + the object/location refs it needs (as-is). No photoreal panel sheet, no extracted panels, no other clips' sheets.
- **`referenceVideos`** (K ≥ 2 ONLY): `[{ alias: "prev_clip", path: <K-1's savedTo> }]`. Omit for K=1. Immediate predecessor only.
- **`duration`**: the CLIP's resolved value (`clip.durationSec`), whole second in `[D_min,D_max]`. NOT hardcoded, NOT the sheet total.
- **`aspectRatio`**: 🚨 **ASK THE USER — do NOT infer it from the storyboard.** Aspect ratio is a VIDEO decision, not a storyboard property: the SAME storyboard can be turned into 16:9, 9:16, 1:1, 4:5… Before generating ANY clip of this piece, ask the user which format(s) they want (16:9 YouTube/web, 9:16 Reels/TikTok/Shorts, 1:1 / 4:5 Instagram, …) — via `prompt_user` / `prompt_form`, never a `print`. Use their answer as `aspectRatio` on EVERY clip (MANDATORY; the sheet is only a neutral reading surface, the model reframes). A 16:9 clip in a 9:16 timeline = black bars. If they want several formats, that's several passes at different `aspectRatio` — ask once, up front.
- **`quality: "high"`**.
- **`withAudio: true`**: ALWAYS (default `false` → omitting = silent = hard failure). Controls DIEGETIC sound (SFX/dialogue/voiceover/ambient), NOT music. Exclude music ONLY via the closing Audio line, NEVER via `withAudio: false` (kills SFX/voices). Only `false` for a deliberately fully-silent clip (essentially never).
- **`saveTo: <directory>`**.

### Model choice (NOT hardcoded) + activate the craft skill
> **Step 0a — ASK THE USER THE VIDEO FORMAT/RESOLUTION FIRST (MANDATORY, gating).** Aspect ratio and resolution are VIDEO decisions, NOT storyboard properties — the same storyboard yields videos in many formats. Before generating ANY clip, ask the user (via `prompt_user`/`prompt_form`, never a `print`) which aspect ratio they want (16:9 web/YouTube, 9:16 Reels/TikTok/Shorts, 1:1 or 4:5 Instagram, …) and, if the model exposes it, the resolution. Do this ONLY here (at video generation), NEVER at storyboard time. Use their answer as `aspectRatio` on every clip. Several formats requested → several passes; ask once, up front. Do not proceed to generate without this answer.
> **Step 0b — activate `video-generator` FIRST.** Before choosing or wording any clip, activate the `video-generator` skill. MANDATORY for ALL video generation: it explains how to call `generate_video` and the exact params each model accepts. Do this even here — the model-specific craft skill does NOT replace it (`video-generator` = how the TOOL works; the craft skill = how to WORD a clip). Never commit to a model's craft skill before `video-generator` is active.
> **Then choose the video model — the BEST one for THIS situation. Never hardcoded, and NOT decided by any fixed label — YOU judge it from the model cards.** Read the `video-generator` model cards and pick what fits this piece: it MUST be **multi-shot-capable** when a clip renders several hard-cut shots (per the cards, that's the Seedance 2.0 family today), and it should match the style, the input shape you're feeding it (reference-to-video vs image-to-video), the aspect/resolution, and audio needs. Weigh the cards per clip and pick the strongest fit — if a better-suited model exists for these shots, use it. When no single model is multi-shot AND fits, prefer multi-shot capability (the storyboard's shot structure is the priority) and lean on its craft skill for the rest.
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

> **Faithful transcription, never invent a shot.** Shot lines come ONLY from THIS clip's JSON shots, in JSON order — no add / drop / reorder / split / merge. `noCutBefore`-glued runs collapse into ONE shot line (cite their panel range, "no cut"); otherwise each shot = one panel = one shot line. Before writing, state *"this clip has N shots"* and match. **Carry established state forward — from the continuity matrix (see the callout above):** for each shot, check its `continuity` row `{ characters, objects, place }` and restate any non-default state that still holds, even where the shot's `action` text dropped it, or Seedance resets it. The row is authoritative; transcribe it, don't re-derive. **Causal order only:** never show aftermath before its cause.

**4. Closing scene note (1 line).** The environment / atmosphere / lighting that holds across the whole clip, plus the audio note. Example: *"Ochre dusty sky, long hard shadows, soft constant Mars wind. Audio: diegetic sound only, natural ambience; music on a separate timeline track."* When the storyboard has story-wide invariants (`continuity` LOCK / negatives the model won't infer), fold the few hard ones in here as a short *"Hard rules: …"* clause (e.g. *"the button stays mounted high and out of reach until he climbs; bottles stay intact"*). Audio phrasing: single-sheet or music baked in → *"diegetic sound only, natural ambience"*; multi-sheet with a separate music track → *"…music is on a separate timeline track, not part of this clip."* `withAudio: true` is a tool param, NEVER prompt text; never `withAudio: false` to keep music out.

**⚙️ DESCRIBE THE PHYSICS of any action — a vague verb makes Seedance invent wrong mechanics.** The compact shape strips STYLE, never the mechanics of a physical action. Seedance renders the words literally, so a loose verb becomes a literal (wrong) instruction. Two archetypes, both reported bugs:
- **Floating instead of a real trajectory.** *"spins in mid-air then snaps into his fist"* → the model reads "in mid-air" as "float". Fix: write the ARC with gravity — *"the coin rises, peaks, then falls back accelerating under gravity and lands firmly in his closed fist"*. State up/peak/down + acceleration + the contact/endpoint.
- **A detail materialising all at once instead of being progressively created.** *"drags a single fresh red arrow"* → the model draws the line AND pops the arrowhead into existence. Fix: describe the MECHANISM stroke by stroke — *"the pen tip moves and red ink appears ONLY directly under the moving tip, tracing the shaft first, then the two head strokes; nothing exists ahead of the tip"*. Name what creates what, and that nothing appears before its cause reaches it.

General rule: for any action, name the **actor + force/mass + trajectory + acceleration + contact + visible endpoint**, and forbid the wrong reading (*"no floating; no part appears before the tip reaches it"*). One physical cause with its visible consequences beats a single vague verb. **ALWAYS keep scene continuity:** the mechanics you describe must be consistent with the shot's `continuity` row and the surrounding shots — the object's state, position and momentum at this shot's start come from where the previous shot left them (matrix authority); never describe a motion that contradicts the established state, and carry the end state forward. If a shot has no real-world mechanics (a static look, a held pose) this doesn't apply — don't over-specify.

**Panels are ACTION references, not start frames — say it once.** A panel is a representative moment WITHIN its shot (often mid-action), not the first frame. Add one global line: *"the panels are reference stills of a moment WITHIN each shot, not starting frames: begin each shot naturally before its reference moment and flow the motion through it."* Never pass a panel/sheet as `startFrame` (only a previous clip's real final frame qualifies, and only if you use frame-anchoring).

**Faces need NO strip line.** The sheet goes in with its characters as depth figures (no face at all) and the character turnarounds are Seedream copies (clean ordinary faces) — there is no mesh, grid or overlay to negate. Do not add any "bare skin / strip the mesh" line; that method is gone.

**Length:** keep the whole prompt tight — roughly the size of the reference example (one scene line, one count line, one line per shot, one closing line). Don't pad; do give each shot enough motion to differentiate it.

### Part 2 — CLIP CHAINING (clips 2…N): attach the previous clip and say it's a continuation
For every clip after the first, you already attached the immediately-previous clip as `prev_clip` (`Video 1`) in `referenceVideos`. In the prompt, add a short continuation line right after the scene line, stating explicitly that this clip continues the attached previous clip:

> *"`Video 1` is the immediately preceding clip of this same film. This clip continues DIRECTLY from its last frame: same lighting, character positions, momentum and world-state at its end — do not reset. Match its pacing and camera energy. Do NOT repeat or re-enact its shots; render only the NEW shots below."*

**When you attached the BLURRED copy** (previous clip had photoreal faces — see "Attach references" §4), say so explicitly, and re-point identity at the turnarounds:

> *"`Video 1` is a BLURRED version of the immediately preceding clip of this same film (blurred for delivery only — treat it as that clip). Continue DIRECTLY from its final moment: same character positions, momentum, lighting and world-state at its end — do not reset. Match its pacing and camera energy; take the blur as delivery artifact, NOT as the look: render this clip SHARP, with faces and identity from the character turnaround sheets. Do NOT repeat or re-enact its shots; render only the NEW shots below."*

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
2. **Same reference discipline on every clip** — each clip attaches its own DEPTH-MAP SHEET + the Seedream'd turnaround of each character in it, plus the previous clip video from K ≥ 2. The turnarounds carry identity across the piece (reuse the SAME sheet per character everywhere); the depth sheet carries structure.
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
- `extract_panel` / decompose the sheet into panels — FORBIDDEN on this path. The clip's sheet goes in WHOLE as a single DEPTH MAP. Name the panel range in the prompt; the model maps shots→panels.
- Distort the sheet on the way to its depth map — the depth sheet keeps the sheet's EXACT grid, framing, aspect and size. No cropping, re-framing, merging cells or warping.
- Attach the PHOTOREAL panel sheet, extracted panels, or another clip's sheet. (Object/location refs the clip needs ARE welcome — just keep it to what's in frame and respect the 12-file cap.)
- Add per-shot panel citations — the count line ("panels A to B") maps them; the model counts.
- Force the compact shape / minimal attachments onto a non-Seedance or non-reference-to-video model — that path uses its own craft skill's techniques (SCOPE note in STEP B).
- Hardcode `duration: 15` (STEP A owns timing).
- Search disk for the storyboard JSON (STEP 0 / INPUTS: metadata is the only auto-recovery; missing → sheet pixels, never an unrelated JSON).
- Compress a >15 s CLIP by dropping shots (STEP A fail-fast; a SHEET may exceed 15 s, a CLIP never).
- Render one clip per panel or per sheet — one per **CLIP** (STEP B).
- Invent, add, drop, reorder, split or merge shots (STEP B: shots come ONLY from THIS clip's JSON, in order; glued runs = one shot line).
- Describe an action with a vague verb — spell out its PHYSICS (trajectory, gravity, acceleration, contact, what-creates-what) and forbid the wrong reading, so Seedance doesn't float it or materialise details out of order; keep the mechanics consistent with the continuity matrix (STEP B "⚙️ DESCRIBE THE PHYSICS").
- Burn ANY text into the video, or copy sheet chrome (spoken lines are AUDIO).
- Attach a raw photoreal human face to Seedance (it rejects the WHOLE render → *"may contain likenesses of real people"*). With this method the sheet is a depth map (faceless), so the ONLY faces you attach are on the **CHARACTER TURNAROUND SHEETS** — and **SUPER MANDATORY: each must BE a Seedream image** (born from Seedream upstream in Step 2b, or laundered here with an EXACT 1:1 copy); the Seedream image is what clears the filter. Skip one and the render fails. The chained previous-clip VIDEO also carries her face: when it shows photoreal faces, chain the ffmpeg-BLURRED copy instead (Attach references §4) — audio and motion survive, the likeness filter doesn't fire — and label it as blurred in the continuation line (STEP B Part 2).
- `replace_panel` / modify the APPROVED sheet in place — `extract_panel` only READS crops; never write back to the original. Face fixes live in the separate Seedream copies, not in the sheet.
- Flip the viewpoint, or break causal order (force the viewpoint + negate the opposite; state only advances).
- For clips 2…N: forget to attach the previous clip and state it's a continuation (STEP B Part 2) — without it the model re-enacts the previous clip.
- Ignore the continuity matrix — read the per-shot `continuity` rows + LOCK when you read the storyboard, and restate carried-forward state in each Seedance shot line (STEP B "🎬 READ THE CONTINUITY MATRIX FIRST"); it's the raccord authority, not optional colour.
- Reset world state between clips (each clip opens in the previous clip's end state).
- Bake music into per-clip renders for ≥ 2 sheets (STEP C), or duck music reflexively (STEP D: only under voice).
- Ship a silent clip / use `withAudio: false` to drop music (STEP B).
- Render 16:9 for a vertical target (pass the platform `aspectRatio` every call).
- Concatenate outside the timeline, reuse/append a timeline, or finish without `show_timeline`-ing the TIMELINE (STEP D).
