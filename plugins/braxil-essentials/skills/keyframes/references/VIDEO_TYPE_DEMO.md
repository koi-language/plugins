# Video Type — Demo

Per-type spec for the **demo** video type. Single source of truth for pacing, captions, audio cue and mix when `type == "demo"`.

**User might say:** demo / product demo / demostración / showcase / unboxing / hands-on / first-look / review / product video.

## Per-clip pacing

Each **CLIP** is ≤ 15 s; total clips ≈ duration / 15. (This pacing is per CLIP. Clips then pack onto sheets of ≤ 12 panels — Chunking Step B — so the number of IMAGES can be FEWER than the number of clips. Two small demo clips (~5 panels) may share one sheet (≤12).)

- Panels per clip: **5–7**
- Per-panel duration: **2–3 s**

So a 15 s demo = 1 clip × 5–7 panels; a 30 s = 2 clips × 5–7 panels; 45 s = 3 clips; 60 s = 4 clips.

## Caption tone

Declarative, feature-focused. (`"360-degree view."` / `"All-day battery."` / `"One-tap pairing."`) Lists what the product CAN DO frame-by-frame.

## Dialogue

Often a voiceover, but optional — many demos are music + on-screen captions only. When voiced, the line is short and feature-focused, not chatty.

## Brief context (internal — informs the panels; NOT rendered on the sheet)

> Context for YOU, not a footer column. The sheet has NO footer (see STORYBOARD_ANATOMY's chrome). Fold the relevant intent into the panel content / emphasis / composition; never draw it as a box, strip, or column on the image.

Keep in mind internally (for YOUR planning only, NEVER drawn on the sheet): the 1–2 features that absolutely have to be shown, the product moment that's the "wow", and whether the demo should feel premium / friendly / technical. Fold this into the panels' content and emphasis; do NOT render any notes box, strip or column.

## Audio cue

- `withAudio: true` only when the frame has a voiceover line.
- Music at the timeline stage — slightly more present than explainer, syncs with the feature reveals.
- Product SFX (clicks, unfolds, fan whir, screen tap) at the timeline stage on every detail frame.

## Mix

- ~30% person-with-product (lifestyle context) and ~70% product close-ups.
- At least one full-product hero shot (front-on, clean background).
- At least one "in use" hands shot.
