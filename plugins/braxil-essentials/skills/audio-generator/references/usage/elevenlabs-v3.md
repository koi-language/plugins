# ElevenLabs Eleven v3 — usage guide (TTS)

> Per-model USAGE guide: how to prompt this model well (technique, not
> parameters). Parameter table lives in `references/models.md` — don't
> duplicate it. Model slug: `fal-ai/elevenlabs/tts/eleven-v3`.

Eleven v3 is ElevenLabs' most **expressive** TTS. You direct the performance
with **audio tags** written INLINE in the `text` — bracketed cues the model
reads as stage direction, NOT as words to speak (`[laughs]`, `[whispers]`,
`[tired]`…). This is the model's whole point; use it for emotional / character
/ reactive voice-over, not for a flat neutral read (MiniMax is fine for that).

## Voices — pass a NAME in `voice`

`voice` takes an ElevenLabs voice **name** (default `Rachel` if omitted). Pick
one whose range fits the read; for **tag-heavy / emotional** scripts choose an
expressive or characterful voice (a flat voice may read the tag out loud or
under-perform). These are ElevenLabs' current **default** voices — any valid
ElevenLabs voice name also works, and the default set rotates over time, so
treat this as a guide, not a fixed enum.

**Female**
- `Rachel` — American, calm & soothing (default). Narration, audiobooks.
- `Aria` — American, husky & expressive. Social, characterful.
- `Sarah` — American, soft, warm & professional. Gentle news / narration.
- `Laura` — American, young, sunny & quirky. Upbeat social.
- `River` — American, non-binary, calm & confident, neutral. Social / narration.
- `Charlotte` — Swedish-English, sultry & seductive. Characters, sensual.
- `Alice` — British, confident & clear. News.
- `Matilda` — American, young, warm & friendly. Audiobooks.
- `Jessica` — American, young, playful & expressive. Conversational.
- `Lily` — British, warm, slightly raspy. Narration.

**Male**
- `Roger` — American, confident & easy-going. Social, conversational.
- `Charlie` — Australian, casual & natural, hyped. Conversational.
- `George` — British, warm, raspy narrator. Distinctive narration.
- `Callum` — transatlantic, intense, hoarse & gravelly. Games, characters.
- `Liam` — American, young, articulate & energetic. Narration, social.
- `Will` — American, chill & friendly. Social, conversational.
- `Eric` — American, middle-aged, smooth & friendly. Conversational.
- `Chris` — American, casual & natural, everyday. Conversational.
- `Brian` — American, deep & resonant. Narration, documentary.
- `Daniel` — British, authoritative. News, broadcast.
- `Bill` — American, older, friendly & trustworthy. Narration, documentary.

## Audio tags — write them inside `text`

Put the tag right where the beat happens: `[tired] It's been a long day… [upset] how many more can I take?`

**Emotions:** `[sad]` `[angry]` `[happily]` `[sorrowful]` `[awe]` `[curious]` `[crying]` `[mischievously]` `[excited]` `[worried]` `[sarcastic]` `[tired]` `[upset]` `[annoyed]` `[surprised]`

**Human / non-verbal reactions:** `[laughs]` `[laughs harder]` `[starts laughing]` `[big laugh]` `[wheezing]` `[sighs]` `[clears throat]` `[coughing]` `[gasps]`

**Delivery, pacing & volume:** `[whispers]` `[shouts]` `[softly]` `[booming]` `[pause]` `[rushed]` `[drawn out]` `[beginning to speak]` `[interrupting]` `[overlapping]`

**Sound effects:** `[gunshot]` `[explosion]` `[clapping]` `[applause]`

**Accents / character voices:** `[French accent]` `[British accent]` `[pirate voice]`

The list is not exhaustive — descriptive states/actions in brackets often work
even if not listed. Experiment.

## Getting good results

- **Combine tags** for layered delivery: `[whispers] [nervous] I don't think we're alone…`
- **The VOICE must support the tag.** Pick a voice with a wide emotional range for tag-heavy scripts. If the voice wasn't trained for a cue, it may **read the tag out loud** instead of performing it — if that happens, switch voice or drop the tag.
- **Punctuation is part of the direction:** commas = breathing beats, `…` = a natural pause, CAPS = emphasis (`I want it right NOW`).
- **Give it enough text.** v3 needs context to act — a 3-word line performs worse than a full sentence. For very short lines, prefer a plain read.
- **Keep the spoken words in the user's language**; the TAGS stay in English (they're control tokens, not spoken).

## `stability` (via `extra_params`) — how hard it obeys the tags

`stability` is 0–1 (default 0.5). It trades expressiveness for consistency:

- **~0.0 "Creative"** — most expressive, responds strongly to tags; can wander/hallucinate. Best for emotional, characterful reads.
- **~0.5 "Natural"** (default) — balanced.
- **~1.0 "Robust"** — most consistent take-to-take, but **ignores tags more**. Use for a steady, neutral read.

Rule of thumb: **tag-heavy / emotional → lower stability** (`extra_params: { "stability": 0.3 }`); **steady narration → higher**.

## Example call (conceptually)

```
generate_audio(
  mode: "speech",
  model: "fal-ai/elevenlabs/tts/eleven-v3",
  voice: "Rachel",                      // an ElevenLabs voice NAME
  text: "[whispers] Did you hear that? [gasps] [nervous] We need to go. NOW.",
  language: "en",
  extra_params: { "stability": 0.3 }    // lower = more expressive
)
```

## Not on this model
No `speed` / `emotion` / `pitch` / `volume` / `outputFormat` knobs — expression
comes from the tags + `stability`. Those canonical fields are ignored here.
