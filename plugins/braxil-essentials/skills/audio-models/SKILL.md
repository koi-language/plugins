---
name: audio-models
description: MANDATORY before ANY audio generation — activate this skill the moment a request involves speech/TTS, transcription, sound effects / Foley, music, or voice cloning, i.e. before EVERY `generate_audio` (or `create_voice`) call. It is the required model+parameter contract: `model` is a mandatory parameter (there is NO auto-router) and this skill tells you which model to pick by category (matching the mode) and exactly which parameters each supported model accepts or rejects. If you are about to generate audio and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): "text to speech/TTS", "narración/voz en off", "read this aloud", "lee esto en voz alta", "transcribe this audio", "transcribe/subtítulos", "sound effect/Foley", "efecto de sonido", "generate music/score", "genera música/banda sonora", "clone a voice", "clona una voz", or any mention of an audio model (MiniMax, Wizper/Whisper, ElevenLabs).
---

# Audio models

Runbook for producing audio through BRAXIL's `generate_audio` tool (+ `create_voice` for cloning). **Do not reimplement audio API code.** **You choose the model** (the `model` param is required — there is no auto-router): pick the mode → pick a slug from the matching category → send only what that model accepts.

**Where to find what — it's already in your context, don't go searching:**
- **Categories & Labels of every model → the `generate_audio` tool's OWN description (the "Catalog" table).** Already in your context — read it RIGHT THERE to pick a model. **Never grep files, `references/`, or the backend for models / categories / labels.**
- **Per-model PARAMETERS → `references/models.md`** (what each model accepts). Read a model's card before setting a non-obvious field.

## Categories — match your mode, ALWAYS

Every audio model carries a Koi category (in the tool's Catalog table). Pick a slug **whose category matches your mode, and NEVER one that lacks it.**

| Category | Mode | Use it for |
|---|---|---|
| `audio_tts` | `speech` | text → spoken audio |
| `audio_sfx` | `sfx` | sound effects / ambient beds (text-only; no video-conditioned model is currently enabled) |
| `audio_music` | `music` | music tracks / scores |
| `audio_transcribe` | `transcribe` | audio → text |
| `audio_voice_clone` | (via `create_voice`) | cloning a voice from a sample |

## The tool: `generate_audio`

One tool, four **modes**. YOU pick the model each time — pass `model` (required) with a slug from the mode's category.

**The exact accepted values for every parameter DEPEND ON THE MODEL you pick** — read your chosen model's table in `references/models.md` (its output formats, duration range, voice ids, and which knobs it honours) and pass ONLY what it lists. The bullets below only say what each param MEANS:

- `mode` — `speech` (alias `tts`, default) · `transcribe` · `sfx` · `music`.
- `model` — **REQUIRED for speech / sfx / music** — YOU pick the slug whose category matches the mode. **Transcribe needs no model.** Omitting it for a generation mode errors out.
- `saveTo` — optional COPY path. Original always in `~/.koi/audio/` (returned `savedTo`); copy is `exportedTo`.

**Speech mode** (text → audio) — enabled model: `fal-ai/minimax/speech-2.8-hd`:
- `text` (required) — the actual words to speak. **Keep in the user's language** — the voice reproduces it verbatim; do NOT translate to English.
- `voice` — a MiniMax preset `voice_id` (e.g. `Wise_Woman`, `Deep_Voice_Man`, `Calm_Woman`, `Casual_Guy`, …) OR a cloned-voice id from `create_voice`.
- `outputFormat` / `speed` / `emotion` / `pitch` / `volume` / `language` — **values are per the model's table** (MiniMax: speed 0.5–2.0, pitch −12..12, emotion 7-value enum, format `mp3/pcm/flac`, `language` as a human name like "Spanish").

**Transcribe mode** (audio → text) — enabled model: `fal-ai/wizper`:
- `audioFile` (required, path). Optional `language` ISO hint (auto-detects when omitted) and `task` (`transcribe`/`translate`). No model pick needed. Returns `{ success, text }`.

**SFX mode** (prompt → sound effect) — enabled model: `fal-ai/elevenlabs/sound-effects/v2` (text-only):
- `prompt` (required, **English**) — describe the sound. `durationSeconds` (0.5–22s) · `promptInfluence` (0..1) · `loop` · `outputFormat` — see the table.
- ⚠ No **video-conditioned** SFX/Foley model is currently enabled, so `videoFile` has no effect.

**Music mode** (prompt → music track) — enabled model: `fal-ai/elevenlabs/music`:
- `prompt` (required, **English** — mood/genre/instrumentation/structure). `durationSeconds` (3–600s) · `outputFormat` · `instrumental` (no vocals). `seed` is ignored. See the table.

## `create_voice` (voice cloning)

Clone a voice from an audio sample (MiniMax Voice Clone), then use the returned voice name as `voice` in later speech calls. Knobs: `noiseReduction` (phone/handheld samples), `volumeNormalization`, `accuracy` 0..1, `previewText`, `modelVariant` (`speech-02-hd` default / `speech-02-turbo` / `speech-01-hd` / `speech-01-turbo`). `language` is NOT supported (dropped).

## Routing

| I want… | Category → mode + fields |
|---|---|
| Spoken narration / dialogue | `audio_tts` → `speech`, `text` (+voice/emotion/speed) |
| A transcript / subtitles | `audio_transcribe` → `transcribe`, `audioFile` (`chunkLevel: word` for caption timing) |
| A sound effect / ambient bed | `audio_sfx` → `sfx`, `prompt` (+loop/duration) |
| A music track / score | `audio_music` → `music`, `prompt` (+duration/instrumental) |
| Clone a voice | `audio_voice_clone` → `create_voice`, sample |

## Choosing within a category

When a mode's category holds more than one model, decide from the data — neutrally, no default favourite:

- Compare the candidates' cards in `references/models.md` on the traits your task needs: output formats, duration range, and the knobs you rely on (`loop` for seamless beds, `instrumental` for no-vocals music, `videoFile` for synced Foley, `chunkLevel: word` for caption timing, `language` for pronunciation, `seed` where it's honoured).
- **What the labels mean — use them to pick the best-suited model.** A model's labels (the Catalog table's **Labels** column) mark the content or style that model is the BEST-SUITED for. If the user's request matches a label, **strongly prefer that model** over an unlabelled one in the same category — the label is telling you it is the best fit. Examples: `narration` → the best for a voice-over read; `cinematic` / `orchestral` → the best for that kind of score; `foley`, `ambient`, etc. → their named sound type. Read every candidate's labels against what the user asked for and route accordingly. When no label matches, ignore labels and choose on quality / price.
- Some knobs live on a single model (seamless `loop` on SFX, `instrumental` on music). Find that model by the field it supports in the table + `references/models.md`, not by memory.

## Gotchas

- **Speech `text` stays in the user's language; SFX/music `prompt` must be English.** They are different fields with different rules — don't translate spoken lines.
- **Format support is per-model** — some TTS models accept only mp3/pcm/flac; others use codec_samplerate_bitrate combos. Unsupported values clamp or drop to the provider default. Check the card.
- **Seed is unreliable in audio** — several models ignore it. Check the card before promising reproducibility.
- **All enabled audio models are text-only** — none conditions on a video, so audio can't be auto-synced to on-screen action right now (describe the sound in the prompt instead).
- **Duration is per-model** and each mode differs — speech has no duration knob (length follows the text). Read the card before promising a length.
