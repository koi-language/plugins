# Video Type — Ad

Per-type spec for the **ad** video type. Single source of truth for pacing, captions, audio cue and mix when `type == "ad"`.

**User might say:** anuncio / ad / commercial / campaign / spot / brand video / product ad / promo / promotional / paid ad.

## Per-clip pacing

Each **CLIP** is ≤ 15 s; total clips ≈ duration / 15. (This pacing is per CLIP. Clips then pack onto sheets of ≤ 12 panels — Chunking Step B — so the number of IMAGES can be fewer than the number of clips. Ads run dense at ~10 panels/clip, so an ad clip usually fills its own sheet.)

- Panels per clip: **8–10** (HARD floor at 8 for ads — do not go below)
- Per-panel duration: **1.5–2 s**

So a 15 s ad = 1 clip × ~10 panels; a 30 s ad = 2 clips × ~10 panels; 45 s = 3 clips; 60 s = 4 clips.

> ⚠ **DO NOT propose 4 panels × 3.75 s for an ad.** That's explainer pacing — a wholly different type. Ads are punchy quick-cut sequences; the rhythm is the format. Concrete worked layouts you MUST stay close to:
>
> - **15 s ad** → 1 clip, **10 panels × 1.5 s** (or 8 × 1.875 s, or 9 × 1.66 s — anything in the 8–10 panels × 1.5–2 s envelope).
> - **30 s ad** → 2 clips, **10 panels × 1.5 s each** (20 panels total → 2 sheets, since 20 > the 12-panel sheet cap).
> - **45 s ad** → 3 clips × ~10 panels.
> - **60 s ad** → 4 clips × ~10 panels.
>
> If your draft has fewer than 8 panels in any clip of an ad, the count is wrong — re-do it before showing the user.

## Caption tone

Punchy imperative (`"Open."` / `"Pour."` / `"Done."`). Verbs only, no fluff. Short.

## Dialogue

Rare — at most one voiceover line at the end ("Brand X. Made for mornings.").

## Brief context (internal — informs the panels; NOT rendered on the sheet)

> Context for YOU, not a footer column. The sheet has NO footer (see STORYBOARD_ANATOMY's chrome). Fold the relevant intent into the panel content / emphasis / composition; never draw it as a box, strip, or column on the image.

Keep in mind internally (for YOUR planning only, NEVER drawn on the sheet): what the brand wants the viewer to feel and remember (premium, accessible, fun, trusted) and the single product moment that has to land. Fold this into the panels' content and emphasis; do NOT render any notes box, strip or column.

## Audio cue (for `generate_video` and the timeline render)

- Default `withAudio: true` only if the ad has a voiceover hook (most don't).
- Add a **music track** at the timeline stage, NOT per-clip — music continuity across cuts requires a single track, not 10 clips each with their own music attempt.
- Optional foley emphasis on the hero shot ("the pour", "the unbox").
- Audio cue line in the per-frame `generate_video` prompt only when that frame has a spoken line:
  > *"Audio: ambient kitchen / room tone, no music (music added in post)."*

## Mix

- ~70% character action + ~30% product / detail close-ups.
- The hero product moment is non-negotiable — at least one frame must be a tight product hero shot.
