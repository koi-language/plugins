# Audio models — per-model parameters (in `generate_audio` / `create_voice` tool terms)

Only models **enabled in the BRAXIL backend** are listed, and each table uses the **actual MCP tool parameters the agent can set** — NOT raw fal fields.

`generate_audio` parameters: **`mode`, `model`, `text`, `prompt`, `voice`, `durationSeconds`, `outputFormat`, `speed`, `emotion`, `pitch`, `volume`, `language`, `videoFile`, `audioFile`, `seed`, `loop`, `promptInfluence`** (+ `saveTo`). Voice cloning is a separate tool `create_voice`.

> Each model's **categories** and **labels** are NOT repeated here — they are backend-managed and shown per model in the live **Catalog table** in the tool's own description. This file is the parameter contract only.

---

## Speech — pick `model` with `mode: 'speech'`

### MiniMax Speech 2.8 HD — `fal-ai/minimax/speech-2.8-hd`
- text → speech.

| `generate_audio` param | Req? | Accepted values (this model) | Notes |
|---|---|---|---|
| text | required | 1–10000 chars | kept in the user's language (reproduced verbatim). |
| voice | optional | MiniMax preset `voice_id` (`Wise_Woman`, `Deep_Voice_Man`, `Calm_Woman`, `Casual_Guy`, `Lively_Girl`, `Patient_Man`, …) or a cloned voice id | |
| speed | optional | 0.5 – 2.0 | |
| pitch | optional | integer −12 – 12 | |
| volume | optional | 0.01 – 10 | |
| emotion | optional | `happy·sad·angry·fearful·disgusted·surprised·neutral` | only these 7. |
| outputFormat | optional | `mp3·pcm·flac` | others (wav/aac/opus) clamp to mp3. |
| language | optional | human NAME (`English`, `Spanish`, `French`, …, `auto`) — ISO codes are mapped for you | improves pronunciation. |

- **Ignored here**: `durationSeconds` (length follows the text), `seed`, `promptInfluence`, `loop`.

---

## Sound effects — pick `model` with `mode: 'sfx'`

### ElevenLabs Sound Effects V2 — `fal-ai/elevenlabs/sound-effects/v2`
- prompt → sound effect (text-only).

| `generate_audio` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | text ≤450 chars | English. |
| durationSeconds | optional | 0.5 – 22 s | omit → auto. |
| promptInfluence | optional | 0 – 1 | default 0.3. |
| loop | optional | true/false | seamless ambient bed. |
| outputFormat | optional | `mp3_44100_128` (default) and the codec_samplerate_bitrate combos: `mp3_22050_32`, `mp3_44100_32/64/96/192`, `pcm_8000…48000`, `ulaw_8000`, `alaw_8000`, `opus_48000_32/64/96/128/192`; bare `mp3`/`pcm`/`opus` also accepted | anything else → default. |

- **Ignored here**: `seed` (dropped). *Not settable via the tool:* `videoFile` — no video-conditioned SFX model is enabled, so it has no effect.

---

## Music — pick `model` with `mode: 'music'`

### ElevenLabs Music — `fal-ai/elevenlabs/music`
- prompt → music track (text-only).

| `generate_audio` param | Req? | Accepted values | Notes |
|---|---|---|---|
| prompt | required | text ≤4100 chars | English; describe mood/instrumentation/tempo. |
| durationSeconds | optional | 3 – 600 s | a <3s request is raised to 3s. |
| outputFormat | optional | same combos as SFX V2 (`mp3_*`, `pcm_*`, `ulaw_8000`, `alaw_8000`, `opus_48000_*`); bare `mp3`/`pcm`/`opus` too | default `mp3_44100_128`. |

- **Ignored / not settable via the tool**: `seed` (ignored), and "instrumental / no-vocals" (the model supports it, but `generate_audio` has no `instrumental` param) — steer vocals via the prompt instead.

---

## Transcribe — `mode: 'transcribe'` (no `model` pick)

### Wizper (Whisper large-v3) — `fal-ai/wizper`
- audio file → text.

| `generate_audio` param | Req? | Accepted values | Notes |
|---|---|---|---|
| mode | required | `'transcribe'` | routes here automatically. |
| audioFile | required | path to the audio (mp3/mp4/m4a/wav/webm) | |
| language | optional | ISO-639-1 hint | omit → auto-detect. |

- *Not settable via the tool:* translate-to-English (`task`), word-level timestamps (`chunkLevel`) — no tool params for them.

---

## Voice cloning — dedicated tool `create_voice` (no `model` pick)

### MiniMax Voice Clone — `fal-ai/minimax/voice-clone`
Clone a voice, then use its name as `voice` in later `mode: 'speech'` calls.

| `create_voice` param | Req? | Accepted values | Notes |
|---|---|---|---|
| audioFile | required | path to a 10–60 s clean voice sample | the user can **record it live with BRAXIL's mic (~60 s of natural speech)** or supply an existing file — offer both. |
| name | required | unique display name | used later as `voice`. |
| description | optional | accent/age/timbre hint | |
| language | optional | ISO-639-1 code | |

- *Not settable via the tool:* noise reduction, volume normalization, accuracy, preview text, model variant (the adapter supports them, but `create_voice` exposes only the four params above).

---

## Notes
- **Speech `text` stays in the user's language**; **SFX/music `prompt` must be English**.
- **Format support is per-model**: MiniMax speech = `mp3/pcm/flac`; ElevenLabs = the codec_samplerate_bitrate combos. Unsupported values clamp/drop to the default.
- **`seed` is honoured by no enabled audio model** — don't promise reproducibility.
- **All enabled audio is text-only** — nothing syncs to a video (`videoFile` has no effect).
