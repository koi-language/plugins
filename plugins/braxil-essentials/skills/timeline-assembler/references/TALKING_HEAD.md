# Editing a talking-head video (persona hablando a cámara)

Rules for turning a raw talking-head / selfie / piece-to-camera source (someone
talking straight at the camera, e.g. a UGC ad, a founder explaining something)
into a finished edit **on the timeline**. This is pure assembly — obey the
timeline-assembler SUPER-MUSTs: **cut with TRIMMED clips of the SAME source
(never new .mp4 files)**, and **finish by SHOWING the timeline, never rendering**.

The goal of every rule below is the same: **kill dead air and never let the same
static shot run long enough to bore the viewer.** On social/YouTube, viewers
decide whether to keep watching in the first few seconds and every flat stretch
is a reason to leave.

## 1. Cut the silences — no dead air

Raw talking-head footage is full of pauses, "ehhh"s, restarts and dead air. Cut
them so the delivery is tight, but **don't strip ALL silence** (zero-pause speech
sounds robotic and breathless).

- **Threshold:** any silence / pause longer than **~0.7 s** gets cut. Leave a
  short natural breath of **~0.3–0.5 s** in its place (a tiny pad, not a hard
  butt-cut) so speech still sounds human. (Fast-paced explainer → tighten toward
  0.3 s; calm/podcast delivery → up to ~1 s.)
- **How:** this is exactly SUPER-MUST #1 — you keep the talking parts as several
  TRIMMED clips of the SAME source and simply DON'T place the silent ranges.
  E.g. speech at `0–4.2 s` and `5.5–11 s`, 1.3 s of dead air between →
  two clips of the same file: `{ sourceInMs: 0, durationMs: 4200 }` then
  `{ sourceInMs: 5500, durationMs: 5500 }`, laid back-to-back on V1. Never
  generate new files to remove silence.
- Also cut fluffed takes / obvious mistakes / long "umm"s the same way.

## 2. Alternate framings — never hold one shot too long

A single unbroken shot of the same face gets boring fast. Change the framing
**every ~5–10 seconds** (never let one framing run past ~10 s). The cheapest,
best-looking pattern interrupt for a single source is alternating **normal ↔
slight zoom**.

- **Zoom is a per-clip parameter** — set the clip's `scale` (`scale: 1.0`
  normal). A punch-in must be a REAL zoom, not a timid one: use **`scale: 1.5`
  or more** (≈ 1.5–1.8) so the change is clearly visible. A 1.1–1.2 nudge reads
  as nothing. Because each talking segment is already its own trimmed clip
  (rule 1), just alternate `scale` clip to clip: normal → zoomed (≥1.5) →
  normal → zoomed…, flipping roughly every 5–10 s.
- **The face MUST stay in frame when you zoom.** A ≥1.5 zoom crops a lot, so a
  centred `scale` will chop off the head or push the face off-centre. You MUST
  set `offsetX` / `offsetY` on the zoomed clip so the crop re-centres on the
  face — never zoom and let the face get cut off. If you can't keep the face
  framed at the chosen zoom, re-frame with the offsets (or check the frame
  first) — but don't drop below ~1.5 just to avoid re-framing.
- Don't zoom on EVERY clip and don't zoom hard — subtle, alternating punches read
  as intentional editing; constant heavy zoom reads as nervous.

## 3. Brand logo pop-in when a brand is named → `references/BRAND_LOGO_OVERLAY.md`

Whenever the speaker **names a brand**, drop that brand's transparent logo on
screen at the exact moment it's spoken — on a track ABOVE the talking head (V2+),
zooming in, holding ≤ 5 s with a subtle shadow, then dissolving out. Finding /
verifying the logo, making it transparent, and picking a well-contrasting corner
has its own full playbook: **read `references/BRAND_LOGO_OVERLAY.md`** whenever a
brand logo must appear.

## 4. B-roll cutaways — show what's being talked about

Don't leave the same person talking on screen the whole video. Every so often,
cover the talking head with **B-roll that illustrates the current topic** so the
visuals move with the words.

- Talking about a shoe factory → cut to footage of a shoe factory. Talking about
  running → running footage. The B-roll should MATCH what's being said at that
  moment.
- **How:** place the B-roll clip on **V2** over the talking head for its
  duration (V2 covers V1), OR cut it inline on V1 between talking segments. Keep
  the speaker's AUDIO running underneath (the B-roll is a visual cover, the voice
  continues) — put the B-roll clip on a V-track with its own audio muted
  (`set_clip_volume` gain 0, or `hasAudio: false`) so it doesn't fight the voice.
- **Cadence:** combine with rule 2 — between the zoom alternations, drop a B-roll
  cutaway every 15–30 s (or when a concept clearly deserves a visual). Channels
  that refresh the visual at least every ~30 s measurably hold viewers better.
- If you don't have suitable B-roll, `generate_video` a short clip of it (this is
  NEW footage that ILLUSTRATES a point — allowed; it is NOT "cutting the source
  into new files", which is what SUPER-MUST #1 forbids).

## Putting it together — as ONE `update_timeline`, not dozens of calls

A talking-head edit touches MANY clips (a dozen+ trimmed speech segments, a
different `scale` on each, logo overlays, B-roll). Do NOT build it with a long
chain of unitary `add_clip_to_timeline` / `set_clip_volume` / `update_clip` calls
— that's slow and chatty. **Compose the WHOLE `clips` array in memory and write
it in a SINGLE `update_timeline`** (read the current JSON with `get_timeline`
first if the timeline already exists). See "Reading & editing an existing
timeline" in the main skill.

For a raw talking-head source: (1) split into trimmed speech clips on V1, dropping
the silences/fluffs; (2) alternate `scale` normal↔zoom every ~5–10 s, keeping the
face framed; (3) add logo PNGs on V2 at brand mentions (pop-in zoom, ≤5 s,
dissolve out); (4) drop topic-matching B-roll on V2 every ~15–30 s. Build all of
that as one full timeline state and `update_timeline` it in one shot, then
`show_result({ resourceType: "timeline", timelineId })` — never render.
