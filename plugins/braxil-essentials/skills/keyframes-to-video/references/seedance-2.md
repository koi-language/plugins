# Seedance 2.0 prompt spec (model-specific layer of `keyframes-to-video`)

> ⚠️ **SCOPE — this file is NOT generic Seedance guidance.** It describes how **`keyframes-to-video`** drives Seedance on its own pipeline (storyboard → approved keyframe sheets → clips): the depth-map sheet, the character turnarounds, the object/location refs, the clip chaining. **None of it applies to using Seedance outside this pipeline** — a plain "hazme un vídeo con Seedance" has no sheets, no depth maps and no turnarounds. For Seedance craft in general (prompt shape, camera, motion, characters, continuation, IP-safety) the authority is the standalone **`seedance-2-0`** skill, which this file neither extends nor overrides.

Apply this file when the chosen video model is a Seedance-class multi-shot model doing **reference-to-video from a storyboard**. It refines, never replaces, the skill's compact shape (scene line → count line → one line per shot → closing note) and its attachment rule (this clip's DEPTH-MAP SHEET + the Seedream'd character TURNAROUNDS + the Seedream'd EXTRAS GROUP SHEETS + the object/location refs it needs + the previous clip video).

## Attachments (Seedance reference-to-video)

- **This clip's OWN sheet, WHOLE and uncropped, with ONLY the CHARACTERS as DEPTH-MAP figures** — one image. Repaint ONLY the people as grayscale depth silhouettes (exact pose/position, no faces); sets, props, lighting and colours stay photoreal and untouched, grid and every panel's composition 1:1 (same size/aspect). 🚫 The depth treatment NEVER touches objects or décor. NEVER `extract_panel` / crop; never the RAW sheet (photoreal faces); never another clip's sheet. Name the panel range in the prompt ("panels A to B").
- **A character model-sheet TURNAROUND per character in the clip** (2 rows × 4 cols: 4 full-body views + 4 head close-ups, grey studio backdrop), each an EXACT Seedream copy — this is where identity/look comes from (the depth sheet carries none). Build each once and reuse across clips.
- **An EXTRAS GROUP SHEET per recurring unnamed group in the clip** (crowd, caravan, soldiers, crew…: one-row lineup of 4–6 representative extras, grey studio backdrop), also Seedream-born — it locks the group's wardrobe/types/era (the prompt states the real headcount). Without it the group re-rolls its look on every clip. Build once upstream, reuse.
- **The object / location refs the clip needs** (set plate, props, product) — attached AS-IS, no Seedream (no faces on them).
- **The immediately-previous clip as a video** (`prev_clip` → `Video 1`), K ≥ 2 only. Immediate predecessor only.
- Max 12 files total per generation; reference VIDEOS max 3, each < 50 MB, combined ≤ 15 s. When the previous clip exceeds the budget, trim to its final 5–8 seconds (timeline tools), never skip the continuation line.

## Compact prompt skeleton (per clip)

Keep it SHORT — the size of the reference example, no timecodes, no CUT blocks, no per-shot style.

1. **Scene line** (1–2 sentences): medium/look + who is in frame. Copy VERBATIM across every clip of the piece (paraphrasing drifts the look).
2. **Continuation line** (K ≥ 2 only): "`Video 1` is the immediately preceding clip; continue directly from its last frame — same lighting, positions, momentum, world-state; don't reset; don't re-enact its shots." When the attached copy is the BLURRED one (photoreal faces in the previous clip), say instead that `Video 1` is a blurred version of the preceding clip (blurred for delivery only), and add: take the blur as delivery artifact, not as the look — render sharp, identity from the turnarounds.
3. **Count line**: "`<N>` shots, hard cuts, perfect continuity. Each shot matches the framing of its reference panel (panels A to B)." The model counts and maps shots→panels; no per-shot panel citation.
4. **One line per SHOT**, JSON order: `SHOT n — <shot size>, <angle if non-default>, <one camera move>: <one physical beat>.` Dialogue inline in its spoken language; SFX inline at the end. One camera instruction per shot.
5. **Closing note** (1 line): environment / atmosphere / lighting held across the clip + the audio line ("diegetic sound only…"; music on a separate track). Fold any story-wide hard rules in as a short "Hard rules: …" clause.

Panels are reference stills of a moment WITHIN each shot, not start frames: say it once globally.

## Hard limits (Seedance 2.0)

- Output: 4–15 seconds per generation. A clip over 15 s MUST be split upstream (`storyboard-to-keyframes` chunking) BEFORE composing — never here.
- Camera setups: reliable up to ~5 per generation; more = the clip was mis-chunked.
- Keep the SAME scene line and lighting phrasing on every clip of the piece.

## Camera vocabulary (use these exact terms)

static locked-off, slow dolly in / dolly out, push-in, snap zoom, whip pan, slow pan left/right, tilt up/down, crane up/down, orbit clockwise/counterclockwise, tracking shot alongside, handheld (subtle sway), shoulder-level follow, low-angle looking up, high-angle looking down, POV, insert ECU. One camera instruction per shot; combining two moves in one shot invites drift.

## The 2-second hook (conditional)

For social-first pieces (ads, shorts, reels) the FIRST shot of the FILM should open on a strong hook: motion already in progress, a striking composition, or the punchline object in frame. NEVER override the user's approved storyboard to force a hook: if the storyboard's opening is a slow establish, render the slow establish (user requirements are sacred). Apply the hook only when composing beats the storyboard leaves open.

## Do / Don't

- DO name counts, sides and targets exactly (Seedance renders literally; ambiguity invents).
- DO keep every character's noun phrase identical across all shots and clips.
- DO state explicit ABSENCES for aftermath shots (what must NOT appear).
- DO attach the clip's sheet WHOLE, with ONLY its CHARACTERS repainted as depth-map figures (`generate_image` EDIT, same size/aspect, no crop or warp; sets/props/lighting stay photoreal) — never decompose into panels, never the raw sheet. **Two reasons:** depth-mapped characters carry pose/blocking WITHOUT pinning a literal frame (the performance flows shot-to-shot) and WITHOUT a face (the likeness filter can't fire); the photoreal environment anchors the world's exact look, which a full-sheet depth map used to lose. The count line still names the panel range; the model maps shots→panels. Say in the prompt that the sheet's ENVIRONMENT is the real look to match, while its PEOPLE are depth figures = structure/blocking only, identity from the turnarounds.
- DON'T attach the RAW panel sheet (photoreal faces), extracted panels, or another clip's sheet. (Object/location refs the clip needs are fine — respect the 12-file cap.)
- DON'T describe multi-beat physics inside one shot: one physical beat per shot, motion flows through the panel's reference moment.
- DON'T mention platform names, watermarks, text overlays or captions: no on-screen text ever.
- **Identity comes from the CHARACTER TURNAROUND SHEETS — and they are the ONLY attachment that is MANDATORY through Seedream** (object/location refs go as-is; the depth sheet's characters are faceless depth figures).** The panel sheet you attach carries no photoreal face, so the turnarounds hold the ONLY faces: `generate_image` EDIT with `bytedance/seedream/v5/pro/edit` for an EXACT 1:1 copy, then attach. Seedance rejects a raw photoreal face (*"image_urls: may contain likenesses of real people"*) but ACCEPTS a Seedream image — skip the pass and the whole render fails. Do it once and reuse across clips so identity never drifts. **Also: the chained previous-clip reference VIDEO carries the face too — when it shows PHOTOREAL faces, attach the ffmpeg-BLURRED copy instead (`gblur=sigma=25`, `-c:a copy`: motion + audio survive, likeness filter doesn't fire) and say in the prompt that `Video 1` is a blurred version of the preceding clip. A likeness rejection on a raw-clip chain is the signal to switch to the blurred copy.**
