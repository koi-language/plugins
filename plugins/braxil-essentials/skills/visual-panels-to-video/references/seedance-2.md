# Seedance 2.0 prompt spec (model-specific layer)

Apply this file whenever the chosen video model is a Seedance-class multi-shot model. It refines, never replaces, the skill's general rules (continuity formula, panels-are-action-references, dimensions, music-off-clips).

## Prompt skeleton (per clip)

1. **Reference roles block** (first lines): one line per attached file stating its authority, in attachment order: "Image 1 = shot blueprint panels (follow ONLY panels A-B, in order)", "Image 2/3 = character identity locks (match face, build, hair, wardrobe exactly)", "Image 4 = prop design lock", "Video 1 = the immediately preceding clip of this same film" (rule 5b). Seedance natively understands positional references; keep roles explicit and never re-describe a locked identity differently later.
2. **Global style + set line**: one sentence, copied VERBATIM across every clip of the piece (film stock, set, palette, lighting direction). Paraphrasing between clips is what causes look drift.
3. **Continuity lock**: the hard rules true in every shot (from the storyboard's continuity LOCK + per-shot rows).
4. **Timeline: CUT blocks with timestamps** ("CUT 3 (0:05.5 - 0:07.5)"), beat-by-beat. Each block: shot type + camera move (exact vocabulary below), ONE physical action, dialogue with speaker label, SFX. Panels are reference stills of a moment WITHIN the cut, never start frames: say it once globally.
5. **Audio design line**: diegetic SFX + dialogue + ambience only; name silence explicitly when wanted ("near-silence, faint idle hum"). Music NEVER in the clip (separate timeline track).

## Hard limits (Seedance 2.0)

- Output: 4-15 seconds per generation. Our storyboard clips must respect this: a clip over 15s MUST be split (frame-chained, rule 5) BEFORE composing.
- Camera setups: reliable up to ~5 per generation; more setups = split the clip.
- Attachments: max 12 files total per generation. Reference VIDEOS: max 3, each < 50MB, combined <= 15s. When passing the previous clip (rule 5b) and it exceeds the budget, trim to its final 5-8 seconds (extract with the timeline tools), never skip the role sentence.
- Keep the SAME reference set (same files, same order) on every clip of the piece.

## Camera vocabulary (use these exact terms)

static locked-off, slow dolly in / dolly out, push-in, snap zoom, whip pan, slow pan left/right, tilt up/down, crane up/down, orbit clockwise/counterclockwise, tracking shot alongside, handheld (subtle sway), shoulder-level follow, low-angle looking up, high-angle looking down, POV, insert ECU. One camera instruction per CUT; combining two moves in one cut invites drift.

## The 2-second hook (conditional)

For social-first pieces (ads, shorts, reels) the FIRST cut of the FILM should open on a strong hook: motion already in progress, a striking composition, or the punchline object in frame. NEVER override the user's approved storyboard to force a hook: if the storyboard's opening is a slow establish, render the slow establish (user requirements are sacred). Apply the hook only when composing beats the storyboard leaves open or when the user asks for social-optimized pacing.

## Do / Don't

- DO name counts, sides and targets exactly (Seedance renders literally; ambiguity invents).
- DO keep every character's noun phrase identical across all cuts and clips.
- DO state explicit ABSENCES for aftermath shots (what must NOT appear).
- DON'T pass the raw panel sheet when per-panel crops fit in the attachment budget (gutter lines bleed into textures as banding).
- DON'T describe multi-beat physics inside one cut: one frozen intent per cut, motion flows through the panel's reference moment.
- DON'T mention platform names, watermarks, text overlays or captions: no on-screen text ever.
