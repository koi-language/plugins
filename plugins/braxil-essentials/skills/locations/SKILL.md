---
name: locations
description: "MANDATORY before creating or editing a reusable LOCATION / set (a place a scene happens in: a dining room, a warehouse, a beach). It is the contract for the location JSON (every field + its meaning) and the establishing-PLATE flow. A scene = its characters + its location; both are first-class reusable identity anchors (a character has a turnaround sheet, a location has an establishing plate). If you are about to create/modify a location and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): create/new location, crear/nueva localización, define a set/plató, save_location, generate_location_plate, or associating a set with a storyboard scene."
---

# Locations

A **location** is a persisted, reusable set/place stored as ONE JSON file at
`~/.koi/locations/<id>.json`, indexed as a first-class creation. Author and edit
it ONLY through the `save_location` tool (never hand-write the JSON). Give it its
establishing **plate views** with `generate_location_plate`. A scene links one
via `scene.locationId` on the storyboard.

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
| `plate` | string | path to the **FRONT** establishing view (set by `generate_location_plate`). |
| `plateRear` | string | path to the **REAR** (reverse 180°) establishing view (set by `generate_location_plate`). |

`createdAt` / `updatedAt` are managed by the tool — on an UPDATE, read the
existing doc and pass its fields back (including `id`) so you update in place.

## Creation flow

1. **Create** the location: `save_location` with `name` + a strong visual
   `description`. 🔴 **FILL EVERY structured attribute you can infer from the
   story** — `locationType` (interior|exterior|mixed), `timeOfDay`, `palette`,
   `lighting`. Do NOT leave them empty when the scene description states them (an
   empty attribute next to a full description is a bug). Add any reference `photos`.
2. **Plate views** (the 2-step procedure below) with `generate_location_plate`.
3. **Link it**: on the storyboard, set the scene's `locationId` to this location
   (and/or add it to the storyboard `locations` roster).

## Plate views — the SET analog of the character turnaround

A **character** → a turnaround **sheet** (`generate_character_sheet`) that locks a
person's identity. A **location** → a small set of establishing **views** of the
EMPTY set that lock the world's look, palette and light across every clip shot
there. No face on a set, so no likeness-laundering is needed.

**YOU (the agent) author the descriptions — `generate_location_plate` NEVER
writes the prompt.** It only renders the image from the prompt YOU give it. This
is a real authoring job; do it in TWO steps, one image per call:

### Step 1 — FRONT view
Write a **precise, faithful, element-by-element** description of the empty
location, grounded in its `description`. Name EVERY concrete element the place has
— every piece of furniture, the TV, the wall clock, the china cabinet, the
azulejo tiling, the ceiling beams, the dining table (shape/wood), the exact
number of chairs, the sideboard, the doors, the windows/balcony, the lamps, the
plants, the paintings, the floor, the palette, and the light and how it falls.
**Never a thin one-liner** like "a traditional dining room at night" — that is the
main failure to avoid. Then call:

```
generate_location_plate({ view: "front", prompt: "<your precise FRONT description>", locationId })
```

It saves the image to `plate` and returns its path. **You must SEE it** before the
next step (read the returned path).

### Step 2 — REAR view (reverse shot FROM the front)
Write a description of the SAME room seen from the **opposite side (camera rotated
180°)**: the wall the FRONT camera stood at is now in front; the FRONT view's back
wall / window / balcony is now **BEHIND the camera and NOT visible**. Then call it
**attaching the FRONT image as reference** so the reverse view is the SAME room,
not a re-invented one:

```
generate_location_plate({ view: "rear", prompt: "<your reverse-shot description>",
  referenceImages: [ "<front plate path from step 1>" ], locationId })
```

It saves the image to `plateRear`.

### Exteriors
For an EXTERIOR that FRONT + REAR cannot capture (a building / house seen from
outside where the sides matter), also author `view:"left"` and `view:"right"` the
same way (attach the FRONT as reference). Interiors normally need only FRONT +
REAR.

## Regenerating / editing a view
- To redo ONE view, just call `generate_location_plate` again for that `view`
  (for `rear`/`left`/`right`, keep attaching the current `plate` as reference so
  it stays the same room).
- To tweak a view (e.g. "open the window in the REAR"), `generate_image` in EDIT
  mode with that view's image as the reference + the change + the set's
  description, then `save_location` writing the new path back to `plate`/`plateRear`.

## Gotchas

- **NEVER hand-write the JSON** — always `save_location`.
- **Update in place**: read the doc, mutate, `save_location` with the SAME `id`
  (and its `createdAt`) so you don't duplicate.
- **`plate` / `plateRear`** come from `generate_location_plate`, not by hand, and
  the tool never writes the prompt — YOU author a precise, faithful description.
- The REAR MUST attach the FRONT as `referenceImages` — that reference is what
  keeps it the SAME room instead of a plausible but different one.
- Reference `photos` are the raw inputs the location was built FROM; `plate` /
  `plateRear` are the generated establishing views the video pipeline attaches.
