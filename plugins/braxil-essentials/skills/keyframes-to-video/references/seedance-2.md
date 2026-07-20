# Seedance 2.0 prompt spec (model-specific layer)

Apply this file when the chosen video model is a Seedance-class multi-shot model doing **reference-to-video from a storyboard**. It refines, never replaces, the skill's compact shape (scene line → count line → one line per shot → closing note) and its attachment rule (this clip's own WHOLE sheet + the previous clip video, nothing else).

## Attachments (Seedance reference-to-video)

- **This clip's OWN whole panel sheet** (uncropped) — the ONLY image. Never `extract_panel` / crop; never attach other sheets; never attach separate character/prop refs (the sheet already carries the character design). Name the panel range in the prompt ("panels A to B").
- **The immediately-previous clip as a video** (`prev_clip` → `Video 1`), K ≥ 2 only. Immediate predecessor only.
- Max 12 files total per generation; reference VIDEOS max 3, each < 50 MB, combined ≤ 15 s. When the previous clip exceeds the budget, trim to its final 5–8 seconds (timeline tools), never skip the continuation line.

## Compact prompt skeleton (per clip)

Keep it SHORT — the size of the reference example, no timecodes, no CUT blocks, no per-shot style.

1. **Scene line** (1–2 sentences): medium/look + who is in frame. Copy VERBATIM across every clip of the piece (paraphrasing drifts the look).
2. **Continuation line** (K ≥ 2 only): "`Video 1` is the immediately preceding clip; continue directly from its last frame — same lighting, positions, momentum, world-state; don't reset; don't re-enact its shots."
3. **Count line**: "`<N>` shots, hard cuts, perfect continuity. Each shot matches the framing of its reference panel (panels A to B)." The model counts and maps shots→panels; no per-shot panel citation.
4. **One line per SHOT**, JSON order: `SHOT n — <shot size>, <angle if non-default>, <one camera move>: <one physical beat>.` Dialogue inline in its spoken language; SFX inline at the end. One camera instruction per shot.
5. **Closing note** (1 line): environment / atmosphere / lighting held across the clip + the audio line ("diegetic sound only…"; music on a separate track). Fold any story-wide hard rules in as a short "Hard rules: …" clause.

Panels are reference stills of a moment WITHIN each shot, not start frames: say it once globally.

## Hard limits (Seedance 2.0)

- Output: 4–15 seconds per generation. A clip over 15 s MUST be split upstream (`keyframes` chunking) BEFORE composing — never here.
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
- DO decompose into individual panels — ALWAYS `extract_panel` this clip's panels and attach them one per panel, in order (never the whole sheet). The count line still names the panel range; the model maps shots→panels.
- DON'T attach anything beyond this clip's own sheet + the previous clip video.
- DON'T describe multi-beat physics inside one shot: one physical beat per shot, motion flows through the panel's reference moment.
- DON'T mention platform names, watermarks, text overlays or captions: no on-screen text ever.
- DO launder photoreal human faces through Seedream before attaching: Seedance rejects a raw photoreal face as a reference, but ACCEPTS a Seedream-generated image. Pre-step (main skill): `extract_panel` each face panel → `generate_image` EDIT with `bytedance/seedream/v5/pro/edit` for an EXACT 1:1 copy → attach that Seedream copy. The face panel's LAST model MUST be Seedream (at 4K use Seedream's max size, do NOT upscale a face panel). No mesh, no strip line — the Seedream copy is already a clean ordinary face.
