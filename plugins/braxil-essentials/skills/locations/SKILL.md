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
| `plate` | string | path to the generated VIEWS SHEET (set by `generate_location_plate`). |
| `plateCells` | array of `{x,y,w,h}` | the 4 row rects the visor slices the sheet by (set by the tool; never by hand). |
| `layout` | object | the top-down FLOOR PLAN the plate was rendered from `{ room, objects:[{name,xPct,yPct,wPct,dPct,count,note}] }` (set by the tool; the spatial source of truth so views stay consistent). |

`createdAt` / `updatedAt` are managed by the tool — on an UPDATE, read the
existing doc and pass its fields back (including `id`) so you update in place.

## Creation flow

1. **Create** the location: `save_location` with `name` + a strong visual
   `description`. 🔴 **FILL EVERY structured attribute you can infer from the
   story** — `locationType` (interior|exterior|mixed), `timeOfDay`, `palette`,
   `lighting`. Do NOT leave them empty when the scene description states them (an
   empty attribute next to a full description is a bug). Add any reference `photos`.
2. **Views sheet**: `generate_location_plate` (pass `locationId`) — it builds the
   sheet of the EMPTY set and auto-attaches `plate` + `plateCells`. It is the
   world anchor reused across every clip set there. No face on a set, so no
   likeness-laundering is needed.
3. **Link it**: on the storyboard, set the scene's `locationId` to this location
   (and/or add it to the storyboard `locations` roster).

## Views sheet (the SET analog of the character turnaround)

- A **character** → a turnaround **sheet** (`generate_character_sheet`), a 4×2
  8-cell grid at 4K, that locks a person's identity.
- A **location** → a **views sheet** (`generate_location_plate`), **1 column × 4
  ROWS (4 cells stacked)**: **4 WIDE PANORAMIC camera views** of the EMPTY set —
  **FRONT, REAR, LEFT, RIGHT**, each labelled (`FRONT VIEW`, `REAR VIEW`, `LEFT
  SIDE VIEW`, `RIGHT SIDE VIEW`).
- **How the tool keeps the 4 views CONSISTENT (3D-lite):** four independent views
  drift (chair counts change, the lamp moves). So the tool FIRST authors ONE
  top-down **floor plan** (`layout`: labelled boxes with positions + counts) from
  the description, draws it as a reference image, then renders EACH view FROM that
  shared plan (attaching it) so every view shows the SAME objects in the SAME
  places with the SAME counts, and composites the 4 into the sheet (exact cells).
  The `layout` is saved on the card. You normally just call the tool — it does all
  this. Pass your own `layout` only to re-render with an edited floor plan.

### Change ONE view without touching the rest
To edit a single view (e.g. "make the REAR view show the window open"), do **NOT
regenerate the whole sheet**. Edit that one row in place, exactly like fixing a
storyboard panel:
1. `extract_panel({ sheet: <plate path>, panel: N, cols: 1, rows: 4 })` — N is the
   1-based, top-to-bottom index: **1 FRONT, 2 REAR, 3 LEFT, 4 RIGHT**. Read the
   returned path (you must SEE it).
2. `generate_image` in EDIT mode with that row + the change + the set's
   description (to keep the location's identity), at the aspect `extract_panel`
   returned.
3. `replace_panel({ sheet: <plate path>, panel: N, image: <new view>, cols: 1,
   rows: 4 })` — it composites the new view back into the sheet in place (same
   path); the visor picks it up automatically.

## Gotchas

- **NEVER hand-write the JSON** — always `save_location`.
- **Update in place**: read the doc, mutate, `save_location` with the SAME `id`
  (and its `createdAt`) so you don't duplicate.
- **`plate`** comes from `generate_location_plate`, not by hand.
- Reference `photos` are the raw inputs the location was built FROM; the `plate`
  is the generated establishing representation the video pipeline attaches.
