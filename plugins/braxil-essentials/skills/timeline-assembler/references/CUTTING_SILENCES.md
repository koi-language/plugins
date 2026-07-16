# Cutting a source: trim clips, drop silences & bad takes

The core move of any edit that starts from a recorded source (a screen capture, a
talking-head take, an interview, any raw clip with dead air / fluffed lines / parts
to drop). This is the detail behind **SUPER-MUST #1** in the main skill.

## The rule: TRIMMED clips of the SAME source, never new .mp4 files

To build a video out of a source that has bad takes / dead air / parts to drop, you
do **NOT** create new video files. The timeline plays **TRIMMED segments of the SAME
source**: place several clips that ALL point at that ONE source `path`, each spanning
a different `[X → Y]` range of the source. That is exactly what a timeline is for.

A clip is trimmed with `sourceInMs` + `durationMs`:
- `path` — the **SAME source video**; reuse the exact same file for every segment.
- `sourceInMs` — where IN THE SOURCE the segment starts, ms (second X × 1000).
- `durationMs` — how long the segment plays, ms ((Y − X) × 1000).
- `startMs` — where the segment sits ON THE TIMELINE (append after the previous one).
- `sourceTotalMs` — the source's true length (ms); keep it accurate so a trim never
  runs past the end.

**Example — "keep 0–4 s and 9–15 s of `take.mp4`, drop the fluffed bit in between"**
= **TWO clips of the same file**:

```json
{ "path": "take.mp4", "startMs": 0,    "sourceInMs": 0,    "durationMs": 4000 },
{ "path": "take.mp4", "startMs": 4000, "sourceInMs": 9000, "durationMs": 6000 }
```

The first plays source 0→4 s at timeline 0→4 s; the second plays source 9→15 s right
after it at timeline 4→10 s. The 4–9 s fluff is simply never placed. Add as many
segments as you need until it's perfect; nudge each edge with `trim_clip`.

## FORBIDDEN, full stop

Creating ANY new `.mp4` (via `generate_video`, `ffmpeg`, a re-encode, a "cut clips"
step) to stitch a video out of an existing source. Never duplicate a source into new
files to assemble it — the source is placed as-is with trimmed clips (same file,
different in/out). `ffmpeg concat` to glue clips is likewise wrong: the timeline is
the abstraction, and concat strips you of multi-track, mix, reframe, transitions,
subtitles and crash recovery.

## Find the cut points precisely — NEVER cut mid-word

A cut that lands inside a word ("…agen—/—tes"), or joins two halves of a sentence that
don't connect, is the #1 way an edit reads as broken. The trim boundaries (`sourceInMs`
and `sourceInMs + durationMs`) are DECISIONS about the audio, not guesses off the
filmstrip. So:

> 🛑 **NEVER take cut timing from `ask_video`.** The video analyzer's timestamps are
> unreliable and can be badly INFLATED — a real case reported timestamps up to ~128 s on a
> **91 s** file (≈1.4× off). Cutting from those numbers destroys the montage (segments land
> past the end, words are halved). `ask_video` is for CONTENT ("what happens / what is
> said"), NOT for WHEN. The only sources of truth for cut timing are the ASR transcript and
> ffmpeg silence detection, below — always cross-check them against the source's true
> duration (a timestamp beyond the clip length means the tool is wrong; discard it).

1. **Transcribe the source with TIMESTAMPS via the ASR.** Call `generate_audio` in
   `transcribe` mode on the SOURCE (pass the video path directly as `audioFile` — its audio
   is extracted for you). It returns `segments`: a timestamped list `[{ start, end, text }]`
   (seconds) per phrase — the real phrase timing. Every cut comes from these `start`/`end`
   values, never from `ask_video`.
2. **Confirm the exact pause edge with ffmpeg silence detection.** The ASR gives the phrase
   boundaries; ffmpeg's `silencedetect` gives the precise silence windows to land the cut
   IN. Run (via shell) `ffmpeg -i <source> -af silencedetect=noise=-30dB:d=0.3 -f null -`
   and read the `silence_start` / `silence_end` pairs from stderr. Place each cut inside a
   detected silence that lines up with a phrase boundary from step 1 — that combination
   (transcript for WHAT, silencedetect for the exact WHERE) is what makes a clean edit.
   Sanity-check every value against the source duration.
3. **Every cut edge falls IN A SILENCE, between phrases — never inside a word.** Map a
   kept phrase to a clip: `sourceInMs` ≈ its segment `start` (snapped into the preceding
   detected silence), and `sourceInMs + durationMs` ≈ its `end` (snapped into the following
   silence), seconds → ×1000 for ms. E.g. a phrase at `start: 23.35, end: 32.10` with
   silences at 23.1–23.4 and 32.0–32.5 → cut at ~23.2 s and ~32.3 s, never at 31.6 s
   (mid-word).
4. **Leave a few frames of air at each edge** (~0.1–0.2 s lead-in and tail) so the
   boundary word isn't clipped and the consonants aren't chopped. A hard butt-cut flush
   against the first/last phoneme sounds truncated.
5. **The JOIN must stay coherent.** A clip should end on a completed clause / thought and
   the next should open the next one, so the speech reads continuously across the cut
   (the "…que se llama loop." → "Y que básicamente…" kind of join). Don't end a clip
   mid-clause and resume somewhere unrelated — read the two segments back-to-back in the
   transcript and check they actually connect as spoken language. If they don't, pick
   different boundaries.
6. **Verify after building**: re-read the transcript segments across each seam to confirm
   no word is halved and every join flows. Nudge any bad edge with `trim_clip`. (Don't use
   `ask_video` timestamps to verify timing — its clock is unreliable; trust the transcript
   and the source duration.)

## Keep the audio peer in sync when you cut

Every V-track clip that carries sound has a paired A-track clip. When you trim / split
a segment, the A peer must get the **same** `startMs` / `durationMs` / `sourceInMs`, or
the voice desyncs from the picture. See `TRACKS_AND_AUDIO.md` — this is the single most
common way a hand-built cut goes silent or out of sync.

## How aggressively to cut silences

The threshold depends on the source. For a **talking-head / piece-to-camera** source
the full playbook (silence threshold, breathing room, pacing, zoom alternation, B-roll)
lives in `TALKING_HEAD.md` — read that when the source is a person talking to camera.
For other sources (screencasts, montages) cut only the genuinely dead stretches and
leave natural pacing intact; do not machine-gun every pause.
