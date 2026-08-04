---
name: characters
description: MANDATORY before creating or editing a reusable CHARACTER (a cast member — person, mascot, spokesperson) via `save_character` / `generate_character_sheet`. It is the contract for the character JSON (every field + its meaning), the the turnaround-sheet model (the `characters`-labelled catalog model, default GPT Image 2), and the voice-assignment flow (list_voices → ElevenLabs, match the voice's gender to the character's sex). If you are about to create/modify a character and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): "create/new character", "crear/nuevo personaje", "define a character", "define un personaje", "character card/ficha de personaje", "cast member", "generate the character turnaround/sheet", "genera la hoja/turnaround del personaje", "assign a voice to the character", "asigna una voz al personaje", or any mention of save_character / generate_character_sheet.
---

# Characters

A **character** is a persisted, reusable cast member stored as ONE JSON file at
`~/.koi/characters/<id>.json`, indexed as a first-class creation. Author and edit
it ONLY through the `save_character` tool (never hand-write the JSON). Give it a
turnaround with `generate_character_sheet`, and a voice with `list_voices` +
`save_character`.

## The character JSON — every field

`save_character` takes `{ character: { … } }`. Fields:

| field | type | meaning |
|---|---|---|
| `id` | kebab-case string | filename id. OPTIONAL on create (derived from name). To UPDATE, pass the SAME id. |
| `name` | string (required) | display name. |
| `handle` | string | BARE @mention (no leading `@`), e.g. `"jason"` → resolves as `@jason` in prompts. |
| `description` | string | physical traits / wardrobe / age / attitude — what defines them VISUALLY. Write it in the user's language. |
| `backstory` | string | background, motivations, relationships. |
| `sex` | canonical string | `female` \| `male` \| `nonbinary` \| `other`. Drives voice gender filtering. |
| `age` | number | years. |
| `height` | number | centimetres. |
| `weight` | number | kilograms. |
| `build` | canonical string | complexion: `slim` \| `average` \| `athletic` \| `muscular` \| `curvy` \| `heavy`. |
| `photos` | string[] | ABSOLUTE paths to reference photos. `photos[0]` is the hero. POINTERS only (bytes never copied). |
| `sheet` | string | path to the generated turnaround sheet (set by `generate_character_sheet`). |
| `sheetCells` | array | detected crop geometry of `sheet` (set by `generate_character_sheet`). Don't author by hand. |
| `voiceId` | string | the voice this character speaks with: a preset voice name (e.g. `"Rachel"`) or a cloned-voice id/name. |
| `ttsModel` | string | the TTS model slug that speaks the voice (provider-scoped). |

`createdAt` / `updatedAt` are managed by the tool — but on an UPDATE, read the
existing doc and pass its fields back (including `id`) so you update in place.

## Creation flow (do all three)

1. **Create** the character: `save_character` with `name` + a strong visual
   `description`, and **FILL EVERY structured attribute you can infer** —
   `sex`, `age`, `height`, `weight`, `build` — plus `backstory` and any
   reference `photos`. 🔴 **Do NOT leave attributes at their defaults when the
   description or story tells you the value.** "Older man, around 60, heavy
   build" → `sex: "male"`, `age: 60`, `build: "heavy"` (estimate `height`/
   `weight` from the build when not stated); a woman in her 20s →
   `sex: "female"`, `age: ~25`. The description text is NOT a substitute for the
   structured fields: the GUI, voice-gender filtering and downstream tools read
   the STRUCTURED attributes, so an empty `sex`/`age` with a full description is
   a bug. Only leave an attribute unset when it is genuinely unknowable.
2. **Turnaround**: `generate_character_sheet` (see below) — it builds the sheet
   and auto-attaches `sheet` + `sheetCells` to the character (pass `characterId`).
3. **Voice**: assign one (see below) and `save_character` with `voiceId` + `ttsModel`.
   A character with no voice cannot speak in a video.

## Turnaround sheet — real photos → GPT Image 2, invented → Seedream

`generate_character_sheet({ description?, photos?, characterId?, model?, aspectRatio? })`
renders a 4-columns × 2-rows sheet (top row = 4 full-body views; bottom row = 4
face portraits) with thick pure-black gutter bars, detects the 8 cells, and
attaches them to the character.

- **Model — AUTO by whether the character has reference photos** (don't override
  `model` unless the user asks):
  - **WITH reference photos** (a real person) → the **`characters`**-label
    identity model (default **GPT Image 2** edit), which best matches the source.
  - **NO reference photos** (a **100% invented** character) → the
    **`characters-synthetic`**-label model (**Seedream** text-to-image). A
    synthesised face is **Seedance-native**: it clears the reference-to-video
    likeness filter with NO later laundering pass, so an invented character is
    ready to drive Seedance video straight from its turnaround.
- **Real-photo characters + Seedance**: their GPT Image 2 sheet is NOT
  Seedance-native; when later driven by Seedance the video pipeline regenerates a
  Seedream turnaround from the source first (see `video-generator` →
  `references/usage/seedance.md`). Invented characters skip that — they are
  already Seedream.
- **Resolution**: the sheet renders at **2K** (`generate_character_sheet` requests `resolution: '2k'` = 2048).
- Pass `characterId` so the sheet lands on the character automatically.

## Voice — list_voices + ElevenLabs, match the sex

- Call **`list_voices`** (default provider **ElevenLabs**) to get the provider's
  built-in preset voices (`presets: [{ id, label, gender }]`) plus the user's
  clones for that provider.
- Pick a preset whose **`gender` matches the character's `sex`** (male → a male
  voice, female → a female voice). Set `character.voiceId` to that preset name
  and `character.ttsModel` to the TTS model slug.
- To PREVIEW a voice, call `generate_audio` (speech mode) with that `voice` +
  `model`; there is no stored sample for a preset.

## Gotchas

- **Fill the structured attributes, always** — `sex`, `age`, `height`, `weight`,
  `build` must reflect what the description/story says; leaving them at defaults
  while the description reads "a robust man of 60" is a reported bug.
- **NEVER hand-write the JSON** — always `save_character`.
- **Update in place**: to edit a character, read it, mutate, and `save_character`
  with the SAME `id` (and its `createdAt`) so you don't create a duplicate.
- **`sheet` / `sheetCells`** come from `generate_character_sheet`, not by hand.
- Reference `photos` are the raw inputs the character was built FROM; the
  `sheet` is the generated, Seedance-ready representation.
