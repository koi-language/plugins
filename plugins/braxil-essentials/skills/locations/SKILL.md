---
name: locations
description: "MANDATORY before creating or editing a reusable LOCATION / set (a place a scene happens in: a dining room, a warehouse, a beach). It is the contract for the location JSON (every field + its meaning) and the establishing-PLATE flow. A scene = its characters + its location; both are first-class reusable identity anchors (a character has a turnaround sheet, a location has an establishing plate). If you are about to create/modify a location and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): create/new location, crear/nueva localización, define a set/plató, save_location, generate_location_plate, or associating a set with a storyboard scene."
---

# Locations

A **location** is a persisted, reusable set/place stored as ONE JSON file at
`~/.koi/locations/<id>.json`, indexed as a first-class creation. Author and edit
it ONLY through the `save_location` tool (never hand-write the JSON). Give it an
establishing **plate** with `generate_location_plate`. A scene links one via
`scene.locationId` on the storyboard.

## The location JSON — every field

`save_location` takes `{ location: { … } }`. Fields:

| field | type | meaning |
|---|---|---|
| `id` | kebab-case string | filename id. OPTIONAL on create (derived from name). To UPDATE, pass the SAME id. |
| `name` | string (required) | display name / label (e.g. "COMEDOR"). |
| `handle` | string | BARE @mention (no leading `@`), e.g. `"comedor"` → resolves as `@comedor`. |
| `description` | string | what the place looks like — architecture, layout, furniture, materials, mood. User's language. |
| `locationType` | canonical string | `interior` \| `exterior` \| `mixed`. |
| `timeOfDay` | string | e.g. "night", "golden hour". |
| `palette` | string | color / mood note. |
| `lighting` | string | the set's default light. |
| `tags` | string[] | free tags. |
| `photos` | string[] | ABSOLUTE paths to reference photos. `photos[0]` is the hero. POINTERS only. |
| `plate` | string | path to the generated establishing plate (set by `generate_location_plate`). |

`createdAt` / `updatedAt` are managed by the tool — on an UPDATE, read the
existing doc and pass its fields back (including `id`) so you update in place.

## Creation flow

1. **Create** the location: `save_location` with `name` + a strong visual
   `description`, plus the structured attributes you can infer (`locationType`,
   `timeOfDay`, `palette`, `lighting`) and any reference `photos`.
2. **Plate**: `generate_location_plate` (pass `locationId`) — it builds a clean
   establishing shot of the EMPTY set and auto-attaches `plate` to the location.
   The plate is the world anchor reused across every clip set there. No face on
   a plate, so no likeness-laundering is needed.
3. **Link it**: on the storyboard, set the scene's `locationId` to this location
   (and/or add it to the storyboard `locations` roster).

## Turnaround vs plate

- A **character** → a turnaround **sheet** (`generate_character_sheet`), an 8-cell
  grid, rendered at 2K, that locks a person's identity.
- A **location** → an establishing **plate** (`generate_location_plate`), ONE
  clean wide of the empty set, rendered at 2K, that locks the world's look /
  palette / lighting.

## Gotchas

- **NEVER hand-write the JSON** — always `save_location`.
- **Update in place**: read the doc, mutate, `save_location` with the SAME `id`
  (and its `createdAt`) so you don't duplicate.
- **`plate`** comes from `generate_location_plate`, not by hand.
- Reference `photos` are the raw inputs the location was built FROM; the `plate`
  is the generated establishing representation the video pipeline attaches.
