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

1. **Create** the character: `save_character` with at least `name` + a strong
   visual `description`, plus the structured attributes you know (`sex`, `age`,
   `height`, `weight`, `build`) and any reference `photos`.
2. **Turnaround**: `generate_character_sheet` (see below) — it builds the sheet
   and auto-attaches `sheet` + `sheetCells` to the character (pass `characterId`).
3. **Voice**: assign one (see below) and `save_character` with `voiceId` + `ttsModel`.
   A character with no voice cannot speak in a video.

## Turnaround sheet — the `characters`-labelled model (default GPT Image 2)

`generate_character_sheet({ description?, photos?, characterId?, model?, aspectRatio? })`
renders a 4-columns × 2-rows sheet (top row = 4 full-body views; bottom row = 4
face portraits) with thick pure-black gutter bars, detects the 8 cells, and
attaches them to the character.

- **Model**: the tool uses the catalog model tagged with the **`characters`
  label**; if none is tagged it defaults to **GPT Image 2** (`openai/gpt-image-2/edit`
  when reference photos are given, else `openai/gpt-image-2`). Don't override
  `model` unless the user asks — pick the best identity/character model here.
- **Seedance**: you do NOT need a Seedream sheet here. When the character is
  later driven by **Seedance** video, the `seedance-2-0` skill handles making a
  Seedream-compatible copy of the sheet itself before use.
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

- **NEVER hand-write the JSON** — always `save_character`.
- **Update in place**: to edit a character, read it, mutate, and `save_character`
  with the SAME `id` (and its `createdAt`) so you don't create a duplicate.
- **`sheet` / `sheetCells`** come from `generate_character_sheet`, not by hand.
- Reference `photos` are the raw inputs the character was built FROM; the
  `sheet` is the generated, Seedance-ready representation.
