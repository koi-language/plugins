# Tracks, audio pairing & mixing

Everything about laying clips on tracks and getting the sound right: z-order, the
mandatory V↔A audio pairing, mixing / ducking levels, and the one-music-track rule.

## Tracks — z-order and mixing

Tracks are named `V1`, `V2`, … (video) and `A1`, `A2`, … (audio). Their semantics differ:

- **V-tracks stack visually.** Higher number = higher in the z-order. V2 paints OVER V1
  (covers whatever V1 was showing for the same time range); V3 paints over V1+V2; etc.
  Use V2+ for cutaways, overlays, lower-thirds, title cards, picture-in-picture.
- **A-tracks mix audibly.** All A-tracks play SIMULTANEOUSLY and their levels are summed
  (`amix`). A higher A-track number does NOT mute the lower ones — they all sound together
  at their respective volumes. Use one track per audio role so each can be levelled
  independently.

### Canonical track layout

| Track | Use |
|---|---|
| **V1** | Main video — per-scene / per-sheet renders, in sequence on the time axis |
| **V2** | Visual overlays — logos, lower-thirds, image cutaways, title cards, B-roll inserts (paints over V1 for the duration of the overlay clip) |
| **V3+** | Additional overlay layers when V2 isn't enough (rare) |
| **A1** | Voiceover / dialogue — auto-paired by `add_clip_to_timeline` when a V-track clip carries audio. Or a dedicated TTS pass when the workflow chose silent video + external voice. |
| **A2** | Background music — ONE continuous clip sized to the full video duration |
| **A3+** | SFX / foley accents (whooshes, taps, stings) — one per type if needed |

## 🛑 Every video clip with sound MUST have a paired A-track audio clip — ALWAYS

A V-track video clip that carries audio does NOT sound on its own in the mix — its sound
comes from a **paired clip on an A-track**. So **every** talking / video clip that has
audio MUST have an audio peer on an A-lane. No exceptions (unless the clip is genuinely
silent and you want it silent).

- **Via `add_clip_to_timeline`:** automatic — when you add a V-track video with an audio
  stream (ffprobe-detected), the tool drops a sibling clip on the first free A lane (same
  `path`, `startMs`, `durationMs`, `sourceInMs`, sharing a `linkId`), and flips the V
  clip's `hasAudio` to false to avoid double-mixing. The A peer is the canonical source
  for the renderer and for volume edits. To opt out for a genuinely silent layer, pass
  `hasAudio: false`.
- **⚠️ Via `update_timeline` (building the JSON yourself): the auto-pair does NOT run —
  you MUST add the A-track peers by hand.** For EVERY V-track video clip that has audio,
  emit a matching A-track clip: same `path`, `startMs`, `durationMs`, `sourceInMs`, a
  shared `linkId`, on an A lane — and set the V clip's `hasAudio: false`. Forgetting this
  = a video with NO SOUND (the reported bug: a talking-head timeline that had zero A-track
  clips → silent). This is a MUST.

**Example — one talking segment (trimmed 22–34.5 s of the source), with its audio peer:**

```json
{ "id": "clip-seg1v", "track": "V1", "path": "/…/IMG_1659.MOV",
  "startMs": 0, "durationMs": 12500, "sourceInMs": 22000, "sourceTotalMs": 91120,
  "linkId": "seg1", "hasAudio": false },
{ "id": "clip-seg1a", "track": "A1", "path": "/…/IMG_1659.MOV",
  "startMs": 0, "durationMs": 12500, "sourceInMs": 22000, "sourceTotalMs": 91120,
  "linkId": "seg1" }
```

The V clip shows the picture (`hasAudio:false`), the A1 peer carries its voice — same
`startMs` / `durationMs` / `sourceInMs`, same `linkId`. Do this for every talking segment.

## Audio mixing levels (linear gain → dB cheat sheet)

`set_clip_volume({ clipId, change: { gain: <value> } })` takes a linear gain in `[0, 2]`.
Conversion: `dB = 20 × log10(gain)`. Reference values:

| Source role | Linear gain | dB | When to use |
|---|---:|---:|---|
| Voiceover / dialogue (V-track embedded) | 1.0 | 0 dB | Default for spoken content — the reference level |
| Music UNDER voiceover (ducked) | **0.04** | **-28 dB** | The standard mix while a narrator / character is speaking |
| Music in intro / outro / silent montage (not ducked) | 0.25 | -12 dB | When there's no voice over the music — let it breathe a bit louder |
| SFX accent (whoosh, click, sting) | 0.5–0.7 | -6 to -3 dB | One-off transients; audible but not stealing focus |
| Background ambient bed (continuous room tone) | 0.1–0.2 | -20 to -14 dB | Texture under voice; never compete with the voiceover |
| Mute a clip without removing it | 0.0 | -∞ dB | Same as setting `volumePoints: null` and a 0-curve |

## Duck music ONLY when it competes with VOICE

The duck exists so a narrator / character can be heard over the music — decide from the
actual audio, don't duck reflexively.

- **There IS voiceover / dialogue over the music** → duck the music to ≈ -28 dB (0.04)
  **for the stretches where the voice speaks** so the words sit on top. At unity gain the
  music drowns the voice (the "música demasiado alta" complaint).
- **There is NO voice** — the music is the main audio, an ambient bed scoring an action
  sequence, an intro/outro, a montage, an SFX-only beat — **do NOT duck it.** Ducking a
  wordless action scene to -28 dB makes it sound broken/empty. Keep it present (roughly
  unity / -3 to -6 dB, or whatever the piece needs).
- **Mixed** (voice in some sections, none in others) → use `volumePoints` keyframes: full
  level where there's no voice, ducked where the voice speaks. Don't flat-duck the whole
  track.

There is NO fixed "always duck" rule. When in doubt: voice present → duck under it; no
voice → leave it up.

**Two-level music (intro loud, body ducked):** if the video opens with 2–3 s of music
alone before the voice kicks in, use `volumePoints` instead of a single gain:
- `{ "t": 0, "v": 0.25 }` → -12 dB during the intro
- `{ "t": 2500, "v": 0.04 }` → ramp to -28 dB by 2.5 s (a tiny dip beats a hard cut)
- `{ "t": <voice_end_ms>, "v": 0.25 }` → back up for the outro

## Music is ONE single track — never per-clip

When multi-clip workflows generate the video as N independent clips (e.g. 2× 15 s sheets
stitched into a 30 s video), DO NOT ask the per-clip generator for music. Independent
renders cannot preserve melody continuity across the seam — the music cuts / restarts
every clip boundary and the result is broken. Generate ONE music file sized to the full
video duration via `generate_audio` and lay it on A2 as a single clip.

For single-clip videos (one render covers the whole duration with no seams) music inside
the clip is fine; this constraint only fires for multi-clip assembly.

## Per-clip audio (V-track) is sacred

When the workflow's clips are generated via `generate_video` and the timeline will mix
their audio:
- `withAudio: true` is **MANDATORY** on every clip. Setting it false because a scene has
  no spoken lines is the silent-clip bug — even a wordless scene needs room tone /
  footsteps / SFX baked in.
- The clip's prompt MUST describe the audio explicitly: voiceover lines in panel order,
  ambient / SFX appropriate to the scene, AND when ≥ 2 sheets are stitched, a "no music
  or background score in this clip; music will be added on the timeline" line. If the
  prompt is silent on audio, the result is often silent video.
