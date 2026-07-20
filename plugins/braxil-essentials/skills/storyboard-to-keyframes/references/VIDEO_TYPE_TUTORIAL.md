# Video Type — Tutorial

Per-type spec for the **tutorial** video type. Single source of truth for pacing, captions, audio cue and mix when `type == "tutorial"`.

**User might say:** tutorial / how to / step-by-step / como hacer / instructional / guide / walkthrough / lesson / training video / paso a paso.

## Per-clip pacing

Each **CLIP** is ≤ 15 s; total clips ≈ duration / 15. (This pacing is per CLIP. Clips then pack onto sheets of ≤ 12 panels — Chunking Step B — so the number of IMAGES is often FEWER than the number of clips. Tutorial clips are small (3–4 panels), so 2–3 usually fit on ONE sheet.)

- Panels per clip: **3–4**
- Per-panel duration: **4–5 s**

So a 15 s tutorial = 1 clip × 3–4 panels; a 30 s = 2 clips × 3–4 panels; 45 s = 3 clips; 60 s = 4 clips.

## Caption tone

Instructive, numbered-step-like. (`"Step 1 — Mix the dry ingredients."` / `"Step 4 — Let it rest for 10 minutes."`) The number prefix `Step N — ` is recommended even though the card already has its own number — viewers reading the caption shouldn't have to look up.

## Dialogue

Voiceover throughout, more verbose than explainer — actually narrates the step. Use the dialogue slot with `[VO]` prefix.

## Brief context (internal — informs the panels; NOT rendered on the sheet)

> Context for YOU, not a footer column. The sheet has NO footer (see STORYBOARD_ANATOMY's chrome). Fold the relevant intent into the panel content / emphasis / composition; never draw it as a box, strip, or column on the image.

Keep in mind internally (for YOUR planning only, NEVER drawn on the sheet): the assumed skill level (beginner / intermediate / advanced), the one common mistake to call out, and any safety / quality tip the audience needs. Fold this into the panels' content and emphasis; do NOT render any notes box, strip or column.

## Audio cue

- `withAudio: true` per-frame.
- Add a quiet music bed at the timeline stage — sparser than explainer (silence between steps is fine).
- Foley / SFX on each step (whisking, clicking, sawing, mixing) at the timeline stage.

## Mix

- ~30% character action (showing the person doing it) and ~70% detail close-ups (showing exactly how the hands move, what the result looks like).
- Top-down "demo angle" for at least half the detail frames.
