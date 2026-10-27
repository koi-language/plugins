---
name: scene-3d
description: "MANDATORY before ANY 3D previz work — blocking a scene in 3D, building an animated storyboard / animatic from 3D, framing or re-framing a camera in a 3D scene, or generating a real video FROM a 3D previz. It is the contract for the scene3d JSON (set, characters, blocking, shots) and the craft for turning storyboard shots into cameras. Activate together with `storyboard` when the previz comes from a storyboard. Triggers (any language): \"previz\", \"previsualización\", \"3D\", \"anima el storyboard\", \"animatic\", \"monta la escena en 3D\", \"bloquea la escena\", \"blocking\", \"cámara más baja/alta\", \"más cerrado/abierto\", \"plano 3D\", save_scene3d, update_scene3d, render_scene3d, add_scene3d_to_timeline, or a request arriving with a `[3D previz shot — …]` preamble from the timeline."
---

# 3D previz (scene3d)

Braxil blocks scenes in 3D and **Blender** renders them headless into animated
previews. The previews become:

- **the storyboard's Timeline view** — every storyboard scene as a live 3D
  set (free camera, every shot camera drawn in place) beside the picture, over
  the story's **montage**: one clip per 3D shot, in script order (see
  "Montage" below);
- **timeline clips** — `add_scene3d_to_timeline` lays shots down as ordinary
  video clips on any OTHER timeline (trim / slip / split / move work as on any
  clip; every re-render updates them automatically);
- **structure for real generation** — the shot's previz drives `generate_video`
  video-to-video so the real take keeps your blocking and camera.

Never hand-write scene files: use `save_scene3d` (create / replace),
`update_scene3d` (patch), `get_scene3d` (read / list), `render_scene3d`
(styles + passes). The first render on a machine may download Blender
(~400 MB) — say so if it takes a while.

## The model: ONE set, ONE clock, N cameras

A **scene** = one place + its characters + their **blocking on a single
clock** (ms). A **shot** = one camera over a window `[startMs, startMs+durationMs]`
of that clock.

- Sequential shots → consecutive windows (shot 2 starts where shot 1 ends).
- **Coverage** (shot / reverse-shot of the same dialogue, a cutaway during the
  same action) → **overlapping** windows. The action happens once; the cameras
  watch it from different places. This is what keeps continuity right for free.
- A shot is played LIVE: Blender interprets its camera over the scene clock in
  the timeline (nothing is pre-rendered), so the window only decides where it
  cuts — trim / slip just move it. Outside its window the camera holds still.

## Coordinates

Metres. **x → right, y → into the set (towards the back wall), z → up**, floor
at z = 0, set centred on the origin. A room `size: [w, d, h]` spans
x ∈ [−w/2, w/2], y ∈ [−d/2, d/2]. "Front" of the set is −y (where a default
audience/camera sits), the back wall is +y.

Facing (`facing`, `turn` target) in degrees: **0 = looking towards +y (the back
wall), 90 = towards −x (left), 180 = towards −y (front), −90 / 270 = towards +x (right)**.
Prefer a TARGET over degrees: `facing: "luis"` (a character id), a prop id, or `[x, y]`.

## Scene shape

```yaml
scene:
  name: "Cocina — la discusión"
  aspect: "16:9"          # storyboard aspect
  style: clay             # clay (fast grey, default) | sketch (pencil lines, matches panels) | lit (EEVEE light)
  storyboard:             # link → animated cards
    id: <storyboardId>
    sceneId: <storyboard scene id>
  set:
    type: room            # room | exterior | empty
    size: [6, 5, 2.8]
    wallColor: "#c9c3b8"
    floorColor: "#7a7468"
    backdropImage: <abs path to the location plate>   # optional, shown on the back wall
    props:
      - id: table
        shape: table      # box cylinder sphere cone plane table chair sofa bed desk counter shelf cabinet door window lamp plant tree car building
        position: [0, 0.5]
        size: [1.6, 0.9, 0.75]
      - id: door
        shape: door
        position: [-2.95, 1.5]
        rotation: 90
  lighting: interior_warm # day overcast golden_hour sunset night interior_warm interior_cool rembrandt noir studio
  characters:
    - id: marta
      name: Marta
      characterId: <saved Braxil character id, if any>
      position: [-2.6, 1.5]
      facing: table
      color: "#c0694a"    # tints the wooden mannequin (keeps the cast apart)
      height: 1.68
    - id: luis
      name: Luis
      position: [1, 0.6]
      facing: marta
      pose: sitting
  actions:
    - character: marta
      type: walk          # walk run turn look_at sit stand wave point raise_arm
      to: [-0.6, 0.9]
      startMs: 0
      endMs: 2400
      face: luis
    - character: luis
      type: stand
      startMs: 2600
      endMs: 3400
  shots:
    - id: sh1
      storyboardShotId: <storyboard shot id>
      startMs: 0
      durationMs: 3000
      camera:
        subject: [marta, luis]
        shotSize: wide
        lens: 24
        height: eye
      move: dolly_in
    - id: sh2
      storyboardShotId: <storyboard shot id>
      startMs: 2400
      durationMs: 2500
      camera:
        subject: luis
        shotSize: medium_close
        lens: 50
        ots: marta        # over Marta's shoulder
```

### Camera: describe, don't compute

Give **intent** and let the builder solve the position:

| field | values |
|---|---|
| `subject` | a character id, or a list for a two-shot |
| `shotSize` | `extreme_wide` `wide` `full` `medium_full` (american) `medium` `medium_close` `close_up` `extreme_close_up` |
| `angle` | degrees around the subject from ITS facing: 0 frontal, 30–45 three-quarter, 90 profile, 180 from behind |
| `height` | `eye` · `low` (contrapicado) · `high` (picado) · `overhead` (cenital) · `ground` · or metres |
| `ots` | character whose shoulder we shoot over (reverse shots) |
| `lens` | mm. 18–24 wide/space, 35 natural, 50 dialogue, 85–135 intimate/compressed |
| `dof` | true → shallow focus (the preview and the renders both blur by the real lens + `fstop`, default 2) |
| `focusOn` | what is sharp for the whole shot: a character id or a prop id |
| `focus` | a FOCUS CHANGE inside the shot (rack focus): `[{t, target}]`, `t` = ms from the shot start, `target` = character / prop id; the focus travels between the keys |

Only for a very specific composition give `position: [x, y, z]` + `target`
(a point or a character id). Camera moves: `move` = `static` `dolly_in`
`dolly_out` `truck_left/right` `pan_left/right` `tilt_up/down` `crane_up/down`
`orbit_left/right` `zoom_in/out` `follow` (re-frames on the subject every few
frames) `handheld`, always as `{ type, speed }`:

| `speed` | travel | turn (pan/tilt/orbit) |
|---|---|---|
| `very_slow` | 7 cm/s | 2.5°/s |
| `slow` (default) | 18 cm/s | 6°/s |
| `medium` | 40 cm/s | 14°/s |
| `fast` | 90 cm/s | 30°/s |

Moves run at CONSTANT speed (a dolly on rails); add `ease: true` only when the
shot asks for a soft start/stop. `amount` (metres / degrees / zoom factor)
overrides the speed when the shot gives an explicit distance.
`keyframes: [{ t, position, target, lens }]` (t = ms from the shot start) is the
fully explicit fallback.

**Cameras edited by hand on the stage are keyframes.** The user can drag a
camera, its aim and its path points on the timeline's 3D stage, change its
focal length and add cameras; Braxil saves that as the shot's `keyframes`
(and drops `move`). Those keyframes ARE the user's camera: keep them on any
other edit, and re-frame such a shot by editing its keyframes, never by
replacing them with a `move`. `camera.focusKeys` `[{t, d}]` (ms from the shot
start, metres) is focus pulled by hand — it replaces `focus` / `focusOn` for
that shot; keep it. Likewise `camera.lensKeys` `[{t, mm}]` is the zoom keyed
by hand (it overrides the `lens` of the keyframes). And `camera.lensKit` `{name, min, max}` is the lens on
the camera for the whole shot (a prime has min = max; zoom stays inside it).
A shot with `inMontage: false` was taken out of the story's montage by the
user: leave it out, do not put it back.

**Every object must read as what it is.** The video model recognises things
from the grey previz: a car built as a flat box comes back as anything. Use the
library shape (`car`, `racecar` for open-wheel / Formula 1, `van`, `truck`,
`bus`, `motorbike`, `bicycle`, furniture…) and, for what the library lacks, a
`group` whose parts give its telling silhouette (wings, wheels, cabin, mast…),
at real size. Never a bare `box` for an object with a shape of its own.

**Vehicles drive, people ride.** Move a vehicle with `drive` actions (`prop`,
`to`, times — chain legs for curves, about one waypoint per second; it turns
nose-first along the path) and seat its driver / passengers with `ride`
(`character`, `prop`; no times = the whole scene). Never fake it with a
character running while "holding" the vehicle.

**One action clock per scene.** Actions run on the scene clock once; the
shots are only windows on it (who sees the action, from where). Never
re-time the action to fit a camera, and never repeat a moment in two shots
that follow each other — shot windows of a scene follow on from each other.

### Translate EVERY storyboard field — this is what makes the previz match

The script of each shot has `shot`, `camera`, `composition`, `lighting`,
`action`. Map ALL of them, field by field — a vague "dolly_in, 35mm" is not a
translation of a paragraph:

| storyboard field | scene3d |
|---|---|
| `shot` ("MCU frontal, ligero contrapicado", "WS altura de pecho") | `camera.subject` + `shotSize` + `angle` + `height` |
| `camera` ("Dolly In muy lento, 35mm", "Rack Focus de A a B", "Estática") | `move` + `speed`, `lens`, `focus` / `focusOn` + `dof` |
| `composition` ("descentrado al tercio izquierdo con aire a la derecha", "en primer término, de espaldas y desenfocadas, tres personas enmarcan…") | `frame.at` for the subject, `ots` / foreground characters placed between camera and subject, `dof` |
| `lighting` ("luz de ventana desde la izquierda del cuadro", "contraluz que dibuja un filo") | `light` on the FIRST shot that describes it: `key` (`screen_left`, `back`…), `quality`; later shots only `rim` |
| `action` | ONLY positions, facing, sit/stand, and object interactions (`hold`/`grab`/`give`/`put`/`kick`) |

The light belongs to the SCENE, fixed in the world: the key (direction,
quality, colour, intensity) is read from the first shot with a `light`,
against THAT shot's camera, and every other shot keeps it — cutting to
another camera never moves the sun or the window. A later shot's `key` /
`quality` is ignored; its `rim: true` (a camera-side accent) is honoured.
So write the key on the shot that best establishes the place (usually the
first wide), in that shot's screen terms.

ALWAYS frame declaratively (`subject` + `shotSize` + `angle` + `height` +
`frame.at`), never by guessing `position`/`target` coordinates — the solver
keeps the camera inside the room and clear of furniture; guessed coordinates
don't. Explicit `position` only for a frame the vocabulary can't express.

### Be faithful to the shot description — every word

The previz is only useful if it shows THE shot that was written. Translate
every descriptor, not just the move type:

- speed words → `speed`: "muy lento / imperceptible / muy suave" → `very_slow`,
  "lento / suave / continuo" → `slow`, "normal" → `medium`, "rápido / brusco" → `fast`;
- "dolly / travelling / push in" (the camera MOVES) ≠ "zoom" (the lens changes):
  never use `zoom_*` for a dolly or vice versa;
- the lens written in the shot (35mm, 85mm…) → `lens`, exactly;
- "profundidad de campo corta / bokeh / foco en X" → `dof: true` + `focusOn: X`;
- "rack focus / cambio de foco / el foco pasa a… y vuelve" → `dof: true` +
  `focus` as a LIST of keys, never a single target: e.g. "rack focus al fondo
  y vuelta a la manzana" in a 2.5 s shot = `[{t:0,target:apple},
  {t:600,target:apple}, {t:1050,target:frutera}, {t:1550,target:frutera},
  {t:2050,target:apple}]` (hold, travel ~450 ms, hold, travel back);
- framing ("altura de pecho", "ligero contrapicado", "perfil tres cuartos",
  "descentrado") → `height` / `angle` / an explicit `position`.

If a descriptor has no field, choose the closest and say so in one line.

## The previz is PART of the storyboard (mandatory)

Every storyboard shot must have a 3D shot built from its CURRENT content. The
storyboard tools (`save_storyboard`, `update_storyboard`) and the scene3d tools
return a `previz3d` block whenever that is not true — shots `missing`, `stale`
(the storyboard shot changed since its 3D shot was built) or `orphans` (3D
shots whose storyboard shot was deleted). When you see it, bring the previz back
in sync BEFORE telling the user you're done:

- missing → add the shots (`update_scene3d addShots`, or `save_scene3d` for a new scene);
- stale → re-block ONLY those shots from the new description; if the change
  doesn't touch the blocking (e.g. reworded action, same staging) use
  `update_scene3d { confirmShots: [...] }`;
- orphans → `removeShots`.

**Speed:** storyboard scenes are independent sets. Delegate each one that needs
work to a `previz-blocker` subagent — ALL IN PARALLEL, in ONE message with one
Agent call per scene (brief: storyboard id, storyboard scene id, scene3d id if
any, what to do: build / re-block shots X / rebuild the set from new photos).
Never block scenes one after another yourself. Each scene renders all its
cameras in one Blender pass and the cards appear as they land.

## Characters = position markers (they do NOT act)

Everyone is an abstract BLOCK FIGURE (faceted ball head, slab torso, block
legs — grey clay). They exist to say WHERE each person is, which way they
face / look, standing or sitting. **They never act**: no walk cycles (a walk
glides), no nods, waves, shrugs or gestures — the video model performs all of
that from the script. Use a limb ONLY when the picture must read an
interaction with an OBJECT or a body:

- `hold` (the coach holds the ball at chest / chin / waist — the prop rides the hands),
- `grab` (reach a prop and keep it), `give` (hand it to another character),
  `put` (leave it somewhere), `kick` (a leg strikes, optionally sending the prop `to` a point).

Everything else in an `action` line ("asiente tres veces", "sonríe",
"manos en los bolsillos") is performance: leave it to the video model.
`color` only tints the clay so the cast stays apart; `height` sets the build.
(`characterStyle: "mannequin"` switches to wooden artist's mannequins.)

## Places and objects: match the reference images, at real scale

The set must be the place the story happens in — spatially. **When the scene
has reference images of the place** (storyboard scene/shot `references`, the
plate / photos of its saved location — `previz3d.layout` lists them), READ
every image before blocking and reproduce its layout:

- the room's size and shape, where the walls, doors and windows are;
- EVERY object that gives the space its geography (table, sofa, bar, columns,
  a car, a stall…) at its REAL dimensions, position and orientation;
- a recognizable silhouette — it doesn't have to be exact, but a car must read
  as a car (use the library shape, real size) and an object the library lacks
  is a `group` of simple parts with its real proportions;
- then set `set.layoutFrom` to all the reference images you matched.

Pick a shot's camera from the photo's own viewpoint when the storyboard shot
frames the place the same way. When NEW reference images arrive later (the
user attaches a photo of the real location — "it's an imperial salon, not a
room"), the scene's `previz3d.layout` flags it: rebuild / adjust the set from
them, never keep the generic one. Without images, still furnish the place with
the objects the action needs plus a few that orient the viewer (doors,
windows, the big furniture), all at real size.

## From a storyboard (the main flow)

1. `get_storyboard` → its scenes, shots, aspect, characters, locations.
   If `get_scene3d { storyboardId }` already lists scenes, UPDATE them; never duplicate.
2. **One `save_scene3d` per storyboard scene** (a scene = one set).
3. Set: if the scene has reference images of the place, lay it out FROM them
   (section above). Otherwise size the room to the action (a kitchen ~5×4 m, a
   bar ~10×8 m) with the props the action touches plus the ones that orient the
   viewer, at real size.
4. Characters: one per cast member present. `characterId` from the storyboard
   roster; `color` (wood tint) / `height` from their descriptions.
5. Blocking: read the shots IN ORDER and write the action once on the clock —
   entrances, crosses, sits, turns, looks. Durations come from the shots
   (`duration` seconds × 1000).
6. Shots: one per storyboard shot, `storyboardShotId` set, window on the clock
   (consecutive, or overlapping for coverage). Translate the shot field:
   "PG / plano general" → `wide`, "PE / plano entero" → `full`, "PA / americano" → `medium_full`,
   "PM / plano medio" → `medium`, "PMC / plano medio corto" → `medium_close`,
   "PP / primer plano" → `close_up`, "PPP / detalle" → `extreme_close_up`;
   "contrapicado" → `height: low`, "picado" → `high`, "cenital" → `overhead`,
   "escorzo / sobre el hombro" → `ots`; movement → `move`.
7. **Review** (see "Review loop"): every returned sheet against its script;
   fix with `update_scene3d` until they match, then tell the user the cards
   now play on hover.

Keep the 180° rule: for a two-person exchange keep every camera on the same
side of the line between them (same sign of `angle` relative to each subject).

## Edits (incl. the timeline's floating bar)

A request with a `[3D previz shot — scene3d id …, shot id …]` preamble targets
that shot. `get_scene3d` first, then the SMALLEST `update_scene3d` patch:

- framing / lens / camera height → `shots: [{ id, set: { camera: { … } } }]` (camera merges one level deep);
- move → `shots: [{ id, set: { move: … } }]`;
- "que entre por la derecha" / blocking → `characters` / `addActions` / `removeActions`;
- "más largo" → the shot's `durationMs` (and the actions it contains).

Unchanged shots are never re-rendered; the timeline clips and storyboard cards
update by themselves. Don't call add_scene3d_to_timeline again for an edit.

## Montage: the storyboard's own timeline (automatic, both ways)

Each storyboard has ONE montage timeline (`role: "storyboard"`), created and
kept by the engine — never build it yourself and never `add_scene3d_to_timeline`
a storyboard's shots onto it. V1 holds one clip per linked 3D shot, in script
order, a live window on the shot's scene clock. It follows every save (new
shots join, windows and order track the script), and the user's edits on it
flow back: a trim / slip changes the storyboard shot's `duration` and the 3D
shot's window, a reorder reorders the storyboard's shots and scenes. Its id:
`get_scene3d { storyboardId, storyTimeline: true }` → `storyTimelineId`.

When the user is on that view, the WORKING AREA names the 3D shot they picked —
"este plano", "la cámara", "que entre antes" mean that shot: the smallest
`update_scene3d` patch, then the review loop.

## What each camera sees (internal continuity)

Every rendered shot carries `preview.inFrame` (mirrored on the storyboard shot
as `_preview3d.inFrame`): the characters (id, name, `characterId`, `share` =
fraction of the frame height they fill, `x` = horizontal screen position 0–1)
and props the camera actually sees over its window, computed from the 3D. It
is the per-shot traceability the old continuity matrix kept by hand — use it
internally (which references a generation needs, who is where on screen); the
user never sees it as a table.

## Look and passes

One look: **lit** (clean real-time EEVEE — real light, shadows, focus; day
scenes under Blender's physical sky). `passes: ["depth", "mask"]` adds
structure videos: depth (white =
near) and mask (each character a flat colour in `characters[]` order:
red, green, blue, yellow, magenta, cyan).

## Review loop (mandatory, every time)

`save_scene3d` / `update_scene3d` / `render_scene3d` return `review`: for each
rendered shot its storyboard `script` and a 3-frame sheet (start | middle |
end) attached as an image. LOOK at every sheet and check it against its
script before moving on — framing, angle, lens, the camera move between the
three frames, composition (screen positions, lead room, foreground), staging
and props, light direction. A shot is done only when its sheet matches; fix
with update_scene3d and look again (max 3 rounds per shot). Report anything
the vocabulary can't express.

## Generating the real shot from the previz

The 3D is the SOURCE of the real video: the take is rendered FROM it, lands
on the same clip(s), and the 3D stays one switch away ("Ver 3D (fuente)" /
"Ver vídeo real" in the clip menu). "Pásalo a vídeo" on one 3D clip, on
several, or on the whole montage is always this flow:

1. Activate `video-generator` + `cinematic-video-prompt-engineer`.
2. `prepare_scene3d_video { timelineId, clipIds }` (omit `clipIds` = every
   clip still in 3D). **ONE TAKE over several small ones:** consecutive clips
   of the same 3D set (same track, end to end, ≤ 30 s) come back JOINED as
   one `take` — their exact 3D windows (trim / slip included) baked end to
   end into one `referenceVideo` that carries the camera, the blocking AND
   the cuts. Each take lists `shots` (which clip, where it falls in the take,
   its storyboard script), `referenceImages` (character sheets / photos of
   who is in it, the place's plates, storyboard refs), `durationSec`,
   `model` and `previousClip` for continuity. Separate takes per clip only
   when the user asks for them (`oneTake: false`). Never render a `cut` by
   hand for this, and never pass a `scene3d:` path to a media tool.
3. Per take — several takes: start them ALL with `wait: false`, then await —
   `generate_video` with `model` = **`bytedance/seedance-2.5/us/reference-to-video`
   (always 2.5)**, `referenceVideos: [referenceVideo]`, ALL its
   `referenceImages` (never drop them), `duration: durationSec`, and ONE
   prompt written SHOT BY SHOT — the shots of the 3D are the only cuts:
   - one block per entry of `shots` ("Shot 1 (0–3.2 s): …"), the words
     "HARD CUT" between two blocks, and once, plainly: "Cut ONLY at HARD CUT;
     never anywhere else";
   - inside a block NO times at all (no "0–6 s", no "around 6 s": time
     marks read as more shots and the model cuts there): one paragraph
     saying the shot follows the reference video's camera EXACTLY as ONE
     continuous move, then in order what happens — what the camera does
     (moves, zoom, focus pulls, framing), who is who and how they look,
     acting, gestures, lines, what happens out of shot, light, sound —
     chained with "then", "as", "while", never with times;
   - light, wardrobe, props and sound continuous across the cuts. Say that the
   reference video is a grey 3D previz to be fully re-rendered
   photographically, keeping its composition, motion and cut points.
   **The reference video is the MASTER.** Open the prompt by saying so: the
   attached video's camera, framing, what is in and out of frame, positions,
   sides and timing override anything in the text. Then CHECK the prompt
   against that shot's `inFrameTimeline` (second by second: `inFrame` = who /
   which vehicle the shot shows, side, distance; `offFrame` = what is near but
   out of shot, and on which side) and correct it lightly: an action that
   happens out of shot stays in the prompt, said as out of shot ("A's car
   overtakes on the right, entirely out of frame — only its roar and B's eyes
   following it"). Never write it as seen while the reference doesn't show it
   (the model invents it to obey the text). If the user wants it ON screen,
   tell them the 3D camera must frame it first.
   Give each figure the VIEW the timeline gives (front / three-quarter front /
   side / three-quarter from behind / behind, and which of its sides) — a view
   the reference's camera does not have ("his face, sun full on it" while it
   shows his side) makes the model CUT to get it. Every change of framing
   inside a shot is the camera MOVING there, never a new shot.
   Spend the words on who / what things look like (cast, vehicles, place,
   light, sound), not on re-staging motion the video already carries.
   **Screen positions come from the 3D, not the script:** each shot's
   `onScreen` says who the reference shows on the left / centre / right and
   how near; write THOSE sides (the storyboard's "screen right" may be out of
   date — a prompt that contradicts the reference makes the model mirror the
   shot). Tie every character to its grey figure with `castKey` ("the boy —
   the small blue figure in the reference — …") so the model knows which
   figure is which sheet.
4. REVIEW THE TAKE: `extract_frame` around each planned shot (or `ask_video`)
   and compare with the previz and the scripts — composition, camera move,
   who is where. If it drifts, regenerate with a corrected prompt (same
   references, never thinner); say what you fixed.
5. `assign_scene3d_take { timelineId, clipIds, mediaPath }` — splits the
   take over its clips: each clip starts at the take's REAL cut nearest to
   the planned one (ffmpeg scene detection) and keeps its own length.
   **Clip lengths are protected**: the tool refuses a take shorter than its
   clips (regenerate longer), and you never trim, stretch or move a clip to
   fit a take. It records which state of the 3D the take came from; when the
   3D changes afterwards the clips are flagged out of date
   (`scene3d.renderStale`) — offer to regenerate.

## Limits (say them when relevant)

Characters are mannequins (no faces, hands or cloth); props are simple
volumes. Previz is for space, timing, camera and staging — not for look.
