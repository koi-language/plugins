---
name: locations
description: "MANDATORY before creating or editing a reusable LOCATION / set (a place a scene happens in: a dining room, a warehouse, a beach). It is the contract for the location JSON (every field + its meaning) and the establishing-PLATE flow. A scene = its characters + its location; both are first-class reusable identity anchors (a character has a turnaround sheet, a location has an establishing plate). If you are about to create/modify a location and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): create/new location, crear/nueva localización, define a set/plató, save_location, generate_location_plate, or associating a set with a storyboard scene."
---

# Locations

A **location** is a persisted, reusable set/place stored as ONE JSON file at
`<project>/locations/<id>.json`, indexed as a first-class creation. Author and edit
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
| `views` | `[{ id, label, path }]` | the establishing views: a free list. `label` is free text owned by the user (no fixed front/rear/left/right); `path` is null on an empty slot waiting to be filled. Set by `generate_location_plate`. **As many as it takes to cover every part of the place the story shoots, and no more** (see "Coverage"). |
| `plate` | string | READ-ONLY: derived from the first view with an image, the location's anchor. Change `views`, never this. |
| `details` | string[] | OPTIONAL ABSOLUTE paths to close-up / DETAIL shots of the place (a sign, a scale, a corner). Uploaded or assigned by the user, POINTERS only. Distinct from `photos` (the input references that DEFINE the place). |

`createdAt` / `updatedAt` are managed by the tool — on an UPDATE, read the
existing doc and pass its fields back (including `id`) so you update in place.

## Creation flow

1. **Create** the location: `save_location` with `name` + a strong visual
   `description`. 🔴 **FILL EVERY structured attribute you can infer from the
   story** — `locationType` (interior|exterior|mixed), `timeOfDay`, `palette`,
   `lighting`. Do NOT leave them empty when the scene description states them (an
   empty attribute next to a full description is a bug). Add any reference `photos`.
2. **Cover the place** with `generate_location_plate`: first the wide master
   view, then one view per part of the place the story shoots that the master
   does not show well (procedure below, "Coverage").
3. **Link it**: on the storyboard, set the scene's `locationId` to this location
   (and/or add it to the storyboard `locations` roster).

## Plate views — the SET analog of the character turnaround

A **character** → a turnaround **sheet** (`generate_character_sheet`) that locks a
person's identity. A **location** → establishing **views** of the EMPTY set that
lock the world's look, palette and light across every clip shot there. No face on
a set, so no likeness-laundering is needed.

🔴 **Cover the place the story uses, consistently.** A plate that frames ONE
spot of a big place (a corner of the overpass) leaves the rest to be invented
clip by clip, and it drifts: a reported bug ("a script with lots of landscape,
and the location only had one tight picture that does not cover the scene").
The opposite failure is a pile of views nobody shoots. So:

### Coverage: plan the views from the story
Before rendering, read the scenes set in this location (their action and their
shots' framing, and the 3D cameras when the previz exists) and list the PARTS
of the place they show: which features (the overpass, the rails, the service
road, the horizon), seen from where, looking which way (toward the sun or with
it behind). Then:
1. **The master view first: WIDE and ELEVATED, the whole place at once.** Not
   centred on one element: a high, wide vantage (a crane or a drone height,
   short lens, deep focus) that shows every feature the story uses in its real
   layout and distances, with room around it. Interiors: a corner-to-corner
   wide that shows the whole room, every wall the scenes use.
2. **Then one view per uncovered part.** Every part on your list that the
   master shows too small, hidden or from the wrong side gets its own view, at
   the height and direction the story's cameras look at it from (ground level
   along the rails toward the horizon; the reverse angle, toward the overpass
   with the sun behind). Each one attaches the master as reference (below), so
   it is the SAME place; each `label` says what it shows ("rails toward the
   horizon, ground level", "reverse: the overpass from the road").
3. **Stop when the list is covered.** A small place one wide covers completely
   (a room, a single doorway) has one view. Never views "just in case", never
   left/right/rear as a ritual.

**YOU (the agent) author the descriptions: `generate_location_plate` NEVER
writes the prompt.** It only renders the image from the prompt YOU give it.

### Writing a view
Write a **precise, faithful, element-by-element** description of the empty
location, grounded in its `description`. Name EVERY concrete element the place has:
every piece of furniture, the TV, the wall clock, the china cabinet, the
azulejo tiling, the ceiling beams, the dining table (shape/wood), the exact
number of chairs, the sideboard, the doors, the windows/balcony, the lamps, the
plants, the paintings, the floor, the palette, and the light and how it falls.
For the master, also the vantage (height, which way it looks) and the layout
(what is where, how far apart). **Never a thin one-liner** like "a traditional
dining room at night": that is the main failure to avoid. Then call:

```
generate_location_plate({ prompt: "<your precise description>", label: "<what it shows>", locationId })
```

It adds the view and returns its `path`. **You must SEE it** (read the
returned path) and check it against your coverage list before the next one.

### Views later, on demand
After the coverage pass, generate one more ONLY when:
- the **user asks** for it (in chat, or via that view's button in the GUI), or
- a **scene genuinely needs that side** — you are about to shoot the set from an
  angle the existing views don't show, and the render would otherwise invent it.

Never "just in case", never as a completion ritual. Every view after the
master (coverage or on demand) **MUST attach the `plate` as reference**: that is what keeps it the SAME place instead of a
re-invented one:

```
generate_location_plate({ prompt: "<your description of this view>", label: "<short label>",
  referenceImages: [ "<the current plate path>" ], locationId })
```

Pass `viewId` to fill or replace an existing view; omit it to add a new one. When
the user gave a view a label, that label says which view it is: follow it, and
never rename it. `label` only applies to a view that has none.

The user can also **ASSIGN** an image to a view, **REMOVE** one, or add empty ones
from the location tab. Respect what is there: never regenerate a view the user
assigned unless they ask.

### Detail shots (`details`)
Close-ups of the place the user uploads or assigns (a hand-written sign, a scale,
a corner). You do not generate these — they are the user's. Attach them as extra
reference anchors when a shot features that detail.

## Regenerating / editing a view
- To redo ONE view, call `generate_location_plate` again with its `viewId` (keep
  attaching the current `plate` as reference unless it IS the first view).
- To tweak a view (e.g. "open the window"), `generate_image` in EDIT mode with that
  view's image as the reference + the change + the set's description, then
  `save_location` writing the new path into that entry of `views`.

## Gotchas

- **NEVER hand-write the JSON** — always `save_location`.
- **Update in place**: read the doc, mutate, `save_location` with the SAME `id`
  (and its `createdAt`) so you don't duplicate.
- **`views`** come from `generate_location_plate`, not by hand, and the tool never
  writes the prompt — YOU author a precise, faithful description.
- Every view after the first MUST attach the `plate` as `referenceImages` — that
  reference is what keeps it the SAME room instead of a plausible but different one.
- Reference `photos` are the raw inputs the location was built FROM; `views` are
  the generated establishing views the video pipeline attaches.
