# Video Type — Social Post

Per-type spec for the **social-post** video type. Single source of truth for pacing, captions, audio cue and mix when `type == "social-post"`.

**User might say:** social / social post / reel / TikTok / Instagram / shorts / story / vertical short / IG video / IG reel / for social / para social / corto.

## Per-clip pacing

Each **CLIP** is ≤ 15 s; total clips ≈ duration / 15. (This pacing is per CLIP. Clips then pack onto sheets of ≤ 12 panels — Chunking Step B. Social clips run dense (~10 panels), so a social clip usually fills its own sheet.)

- Panels per clip: **8–10** (the 10-panel cap is hard — readability)
- Per-panel duration: **1.5–2 s**

So a 15 s social post = 1 clip × ~10 panels; a 30 s = 2 clips × ~10 panels; 45 s = 3 clips; 60 s = 4 clips.

## Caption tone

Rhythmic, on-screen-text style. Often the caption IS the on-screen text the model should render in the clip. (`"POV: you finally made it."` / `"Wait for it…"` / `"This. Changed. Everything."`)

## Dialogue

Usually none — music-driven. When present, it's a single hook line at the start ("POV: …") or a punchline at the end.

## Brief context (internal — informs the panels; NOT rendered on the sheet)

> Context for YOU, not a footer column. The sheet has NO footer (see STORYBOARD_ANATOMY's chrome). Fold the relevant intent into the panel content / emphasis / composition; never draw it as a box, strip, or column on the image.

Keep in mind internally (for YOUR planning only, NEVER drawn on the sheet): the platform (TikTok / Reels / Shorts), the hook in the first 2 seconds, and whether the format is landscape 16:9 or will be reframed to 9:16 at the per-frame generate_video step. Fold this into the panels' content and emphasis; do NOT render any notes box, strip or column.

## Audio cue

- `withAudio: false` per-frame — music-driven, music goes on the timeline.
- Add a single music track at the timeline stage; cuts must sync to beats.
- Optional whoosh / pop SFX on transitions at the timeline stage.

## Mix

- Pacing-first: every frame is short and visually loud.
- ~50/50 person and detail, with the hook frame (frame 1) usually being a person reaction shot.
- For dance / lifestyle content, the mix swings heavily to person (~80%).
