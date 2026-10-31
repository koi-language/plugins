---
name: objects
description: "MANDATORY before creating or editing a reusable story OBJECT / prop / vehicle card (a motorbike, a freight train, a laptop, a weapon, a suitcase). It is the contract for the object JSON (every field + its meaning) and the SHEET flow (ONE image: a three-quarter hero view on the left half, a front elevation and a side profile on the right quarters, cropped into the card's views). A scene = its characters + its location + its objects; each is a first-class reusable identity anchor (a character has a turnaround sheet, a location an establishing plate, an object its sheet). If you are about to create/modify an object and this skill is not active, ACTIVATE IT FIRST. Triggers (any language): create/new object, prop or vehicle card, crear/nuevo objeto, ficha de objeto/vehículo/atrezzo, save_object, generate_object_sheet, generate_object_view, generate_object_detail, object details / close-ups / interior, or associating an object with a story (the storyboard `objects` roster)."
---

# Objects

An **object** is a persisted, reusable story prop stored as ONE JSON file at
`<project>/objects/<id>.json`, indexed as a first-class creation. Author and edit
it ONLY through the `save_object` tool (never hand-write the JSON). Give it its
**sheet** with ONE `generate_object_sheet` call; extra **views** only on demand
with `generate_object_view`. The story-critical **details** (close-ups of a
part, and the INTERIOR when a shot happens inside it) with one
`generate_object_detail` call each. A story links one via the storyboard
`objects` roster: `{ name, description?, objectId }`.

## The object JSON: every field

`save_object` takes `{ object: { … }, summary? }`. Fields:

| field | type | meaning |
|---|---|---|
| `id` | kebab-case string | filename id. OPTIONAL on create (derived from name). To UPDATE, pass the SAME id. |
| `name` | string (required) | display name / label (e.g. "MOTO ROJA"). |
| `handle` | string | BARE @mention (no leading `@`), e.g. `"moto"` → resolves as `@moto`. |
| `description` | string | a strong visual description: shape, proportions, size, materials, colours, markings, logos, wear and condition. User's language. |
| `category` | string | free text, e.g. "vehicle", "prop", "device", "weapon". |
| `tags` | string[] | free tags. |
| `photos` | string[] | ABSOLUTE paths to the INPUT reference photos that DEFINE the object. `photos[0]` is the hero. POINTERS only. |
| `sheet` | string | ABSOLUTE path of the object SHEET (the three-panel image below). Set by `generate_object_sheet`, never by hand. |
| `sheetCells` | `[{ x, y, w, h }]` | the sheet's detected cells, normalized 0..1, in the order threeQuarter, front, side. Set by `generate_object_sheet`, never by hand. |
| `views` | `[{ id, label, path }]` | the views of the object: a free list. `label` is free text owned by the user; `path` is null on an empty slot waiting to be filled. The first three are the sheet crops, ids `threeQuarter`, `front`, `side`, set by `generate_object_sheet`; any other view is an extra from `generate_object_view`. |
| `details` | `[{ id, label, path }]` | the story-critical DETAILS: close-ups of a specific part (`label` = what it shows, e.g. "number 4417 painted on the boxcar door", "dented fuel tank, left side") and INTERIOR views (label starting with `Interior:`, e.g. "Interior: cabin toward the windshield"). `id` a unique kebab/camel string; `path` null = an empty slot waiting to be generated (the user can add one in the GUI). Filled by `generate_object_detail`, never by hand. |
| `image` | string | READ-ONLY, derived: the first view with a path (the three-quarter crop once there is a sheet), else `photos[0]`, else null. The roster image of every story that links this card. Change `views` / `photos`, never this. |
| `model` | string | OPTIONAL `build_model3d` model id: the object's 3D model, reused by every previz of it. |

`createdAt` / `updatedAt` are managed by the tool. On an UPDATE, read the
existing doc and pass its fields back (including `id`, without `image`) so you
update in place.

## Creation flow

1. **Create** the object: `save_object` with `name` + a strong visual
   `description`. 🔴 **FILL EVERY attribute you can infer from the story**
   (`category`, `tags`, the description's shape, colours, materials,
   markings). Add any reference `photos` the user gave.
2. **Build its sheet** with ONE `generate_object_sheet` call (pass
   `objectId`), then READ the sheet and check it (procedure below).
3. **Generate its details** (MANDATORY when the story depends on them): one
   `generate_object_detail` per detail, procedure below.
4. **Link it**: write the returned id into the storyboard `objects` roster
   entry's `objectId` (`update_storyboard`).

## The sheet: the PROP analog of the character turnaround

A **character** → a turnaround **sheet** that locks a person's identity. A
**location** → establishing **plates** of the empty set. An **object** → its
**sheet**: ONE image that shows the object ALONE from three sides, so the video
model and the 3D modeler see more than one face of it (a train seen head-on
tells nothing about its side).

### What you get

`generate_object_sheet` renders ONE landscape image (3:2, high resolution) with
THREE panels separated by thick pure-black bands, the same neutral light-grey
seamless background and the same studio light in all three, no text or labels:

| panel | place on the sheet | view id | framing |
|---|---|---|---|
| hero | LEFT HALF, full height | `threeQuarter` | three-quarter view from slightly above. |
| front | RIGHT HALF, top quarter | `front` | front elevation: straight-on, orthographic look (long lens, no perspective distortion). |
| side | RIGHT HALF, bottom quarter | `side` | side profile: the exact side, orthographic look. |

The tool detects the three panels, crops each into its own image and, with an
`objectId`, saves everything onto the card: `sheet`, `sheetCells`, and the
views `threeQuarter`, `front`, `side` (the crops) placed FIRST in `views`, so
the card's `image` is the three-quarter crop. A view label the user wrote is
kept; every other view of the card is left untouched. With no
`referenceImages`, the card's `photos` (and its previous sheet when you
regenerate) are attached as references automatically.

**YOU (the agent) author the description: the tool NEVER writes it.** It only
wraps your description with the fixed layout above.

### Writing the prompt

Write a **precise, element-by-element** description of the OBJECT itself,
grounded in its `description`: the overall shape and proportions, every part (a
motorbike: tank, seat, fairing, headlight, mirrors, exhaust, wheels, spokes,
forks; a train: the locomotive's nose, cab windows, livery stripes, bogies,
couplers, the number of carriages), the materials and finishes, the exact
colours, markings, numbers and logos, the wear. **No layout, panel, camera or
background words**: the tool adds them. **Never a thin one-liner** like "a red
motorbike": that is the main failure to avoid. Then call:

```
generate_object_sheet({ prompt: "<your precise description of the object>", objectId })
```

It returns `{ sheet, sheetCells, views, … }`. **You must SEE it**: read the
`sheet` path and check the three panels: the SAME object in all three, the hero
a three-quarter view on the left half, the front elevation top right, the side
profile bottom right, the whole object inside each panel, no text. If anything
is wrong, call it again (it attaches the previous sheet and the photos as
references) with a corrected description.

### Extra views, on demand

`generate_object_view` adds ONE extra view, ONLY when the user asks for it (in
chat, or via that view's button in the GUI), or when a scene genuinely needs a
side the sheet does not show (the rear of a car chased from behind, a top plan).
Never "just in case". With an `objectId` it attaches the sheet (first), the
views and the photos as references so it stays the SAME object. Its prompt is
your precise description of the object plus the framing of that view, the same
neutral seamless background and light as the sheet.

Pass `viewId` to fill or replace an existing view (e.g. an empty slot the GUI
created); omit it to add a new one with a `label`. When the user gave a view a
label, that label says which view it is: follow it, and never rename it.

The user can also **ASSIGN** an image to a view, **REMOVE** one, or add empty ones
from the object tab. Respect what is there: never regenerate a view the user
assigned unless they ask.

## Details (MANDATORY when the story depends on them)

The sheet locks the object's overall look; it does NOT lock the small things a
story points at. Those are generated and ATTACHED to the card as `details`, so
every take that shows them gets them right.

1. **After the sheet, read the story**: every shot where the object appears
   (its action, framing, dialogue and continuity notes).
2. **List the details the story relies on**:
   - anything a shot frames in CLOSE-UP or INSERT (the hand on the gear lever,
     the key in the lock);
   - anything the plot or dialogue points at (a number, a logo, a crack, a
     lock, a gauge, a name painted on the hull);
   - marks of STATE that must stay consistent from shot to shot (damage, dirt,
     rust, cargo, a broken window);
   - parts that distinguish THIS object from a generic one of its kind.
   **Do not invent details the story does not need.**
3. **The INTERIOR**: if any shot of the story happens INSIDE the object, or
   looks into it (a car cabin, a train cab, the inside of a boxcar, the back of
   a van), its interior is a MANDATORY detail set: ONE interior view per
   distinct viewpoint the story shoots from, with `framing: "interior"` and a
   label starting with `Interior:` (e.g. "Interior: cabin toward the
   windshield", "Interior: driver's side, dashboard").
4. **Generate them ONE AT A TIME**, one `generate_object_detail` call per item,
   each with a precise `label`:

   ```
   generate_object_detail({ objectId, label: "number 4417 painted on the boxcar door",
     prompt: "<your precise description of that part>" })
   generate_object_detail({ objectId, framing: "interior",
     label: "Interior: cabin toward the windshield",
     prompt: "<your precise description of the viewpoint and everything in view>" })
   ```

   YOU author `prompt`: which part, where on the object, its shape, material,
   colour, wear, and the EXACT text when the detail is text on the object (for
   an interior: the viewpoint and everything in view, seats, dashboard, trim).
   The tool adds the framing (a macro / insert on the sheet's neutral light-grey
   background and light, 1:1; or a wide 16:9 interior view in natural interior
   light, empty of people unless told) and ALWAYS attaches the sheet as
   reference so it is the SAME object.
5. **READ each result** and compare it with the sheet: same materials,
   colours, markings and wear; the right part; the exact text. If wrong, call
   it again with its `detailId` and a corrected description (the previous image
   is attached too).

If the user adds an EMPTY detail slot (in the GUI), fill it by passing its
`detailId`; its label says what it shows: follow it, never rename it. Without
`detailId` the tool appends a new detail.

## Regenerating / editing

- To redo the three standard views, call `generate_object_sheet` again: they
  come from the sheet, never from three `generate_object_view` calls.
- To redo ONE extra view, call `generate_object_view` again with its `viewId`.
- To redo ONE detail, call `generate_object_detail` again with its `detailId`.
- To tweak an image (e.g. "add a dent on the door"), `generate_image` in EDIT
  mode with that image as the reference + the change + the object's
  description, then `save_object` writing the new path into that entry of
  `views`. A change to the object itself (a new colour) means the sheet and
  every extra view and detail must follow: regenerate the sheet first, then the
  extras and the details.

## The video and the 3D model

- On the real-video takes, the object's references are its `sheet` (ONE
  reference image carrying its three views), then its details, then its extra
  views, then its photos; the take's `objects[]` entry also lists its
  `details` (`[{ label, path }]`) so the prompt names them.
- When the previz models the object (`build_model3d`, via `3d-modeler`), the
  sheet's three crops (the `threeQuarter`, `front` and `side` views) plus any
  extra views and the photos are the references, and the built model's id is
  saved on the card as `model` (`save_object`) so every later previz reuses it
  instead of modeling it again. Details are NOT 3D modeling references.

## Gotchas

- **NEVER hand-write the JSON**: always `save_object`.
- **Update in place**: read the doc, mutate, `save_object` with the SAME `id`
  (and its `createdAt`), without `image` (it is derived).
- **The standard views come from ONE sheet**: never build them as separate
  `generate_object_view` calls; separate renders drift into different objects.
- **`sheet`, `sheetCells`** and the `threeQuarter` / `front` / `side` views are
  set by `generate_object_sheet`, never by hand, and the tool never writes the
  prompt: YOU author a precise description.
- **Details are part of the card**: an object whose story-critical details (or,
  when a shot happens inside it, its interior views) are missing is not ready
  for video.
- Reference `photos` are the raw inputs the object was built FROM; the sheet
  and the views are the generated images the pipeline attaches.
