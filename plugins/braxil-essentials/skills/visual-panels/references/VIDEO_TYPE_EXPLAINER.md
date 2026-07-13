# Video Type — Explainer

Per-type spec for the **explainer** video type. Single source of truth for pacing, captions, audio cue and mix when `type == "explainer"`.

**User might say:** explainer / explicativo / explainer video / how it works / como funciona / overview / introduction / intro video / concept video / pitch video / what is X.

## Per-clip pacing

Each **CLIP** is ≤ 15 s; total clips ≈ duration / 15. (This pacing is per CLIP. Clips then pack onto sheets of ≤ 12 panels — Chunking Step B — so the number of IMAGES is often FEWER than the number of clips. Explainer clips are small (3–5 panels), so 2–3 usually fit on ONE sheet.)

- Panels per clip: **3–5**
- Per-panel duration: **3–5 s**

So a 15 s explainer = 1 clip × 3–5 panels; a 30 s = 2 clips × 3–5 panels; 45 s = 3 clips; 60 s = 4 clips.

## Caption tone

Didactic, descriptive — the caption SAYS what's happening so the viewer follows even with the sound off. (`"Tap the new button."` / `"The app finds the nearest store."` / `"Your order arrives in minutes."`)

## Dialogue

Voiceover throughout, often one VO line per frame. Use the dialogue slot with `[VO]` prefix.

## Brief context (internal — informs the panels; NOT rendered on the sheet)

> Context for YOU, not a footer column. The sheet has NO footer (see STORYBOARD_ANATOMY's chrome). Fold the relevant intent into the panel content / emphasis / composition; never draw it as a box, strip, or column on the image.

Keep in mind internally (for YOUR planning only, NEVER drawn on the sheet): the audience's prior knowledge (assume zero), the single insight the viewer must walk away with, and the tone of the voiceover (warm, professional or playful, pick one). Fold this into the panels' content and emphasis; do NOT render any notes box, strip or column.

## Audio cue

- `withAudio: true` per-frame so the VO line is generated with the clip.
- Add a soft music bed at the timeline stage — low energy, not melodic enough to compete with the voice.
- Subtle UI sounds (taps, swooshes) on action frames at the timeline stage.

## Mix

- ~50/50 character action and detail / UI close-ups.
- For SaaS explainers, lean heavier on UI close-ups (~70%).
- For physical-product explainers, lean heavier on hands + product (~60%).
