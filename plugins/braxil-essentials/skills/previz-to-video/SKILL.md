---
name: previz-to-video
description: >
  🔴 ACTIVATE whenever a 3D PREVIZ (a storyboard's montage, or 3D clips on any timeline) must become REAL VIDEO. Triggers (any language): "genera/haz el vídeo", "pásalo a vídeo", "monta el vídeo del storyboard", "haz la película", "pasa el storyboard a vídeo", "renderiza los clips", "genera vídeo a partir de los clips", "turn this into video", "generate the video", or a request on 3D clips from the timeline's clip menu. The 3D scene is the SOURCE of every take: its cameras, blocking, cuts and timing are FIXED facts the video reproduces; the storyboard only adds the script (action, lines, sound) and the cast/set references. Also activate `video-generator` (the model + parameter contract) and `cinematic-video-prompt-engineer` (writes each take's prompt in its direct mode, from the facts this skill hands it) before any `generate_video` call.
---

# Previz to video

The 3D previz is the film's blueprint. Every storyboard shot already has a 3D
shot (see `scene-3d`), and the storyboard's montage timeline holds one 3D clip
per shot, in script order. Turning it into video means re-rendering those 3D
clips photographically: each take is generated FROM the 3D (it is the take's
`referenceVideo`) and lands back on the same clips, with the 3D one switch
away ("Ver 3D (fuente)" / "Ver vídeo real" in the clip menu).

What is FIXED by the 3D, and never re-decided by anyone (you, cinematic, the
model): the shots and their order, where each cut falls, each shot's length,
the camera (framing, angle, lens, moves), who is in frame, screen positions,
blocking and timing. BLOCKING here means only WHERE each body is, WHERE it
travels and which way it faces, never how it moves.

🔴 The 3D figures' BODY MOTION is a placeholder, NOT a reference. Their limbs,
poses, gait and gestures are deliberately crude and abstract so the model does
NOT copy them. The model must never reproduce the mannequin's pose or limb
movement (a raised arm, a stiff jump, a robotic walk): it takes from the
figure its position, path, facing, timing and its body pose (standing,
seated, riding, lying, kneeling...) only, and invents the body performance itself,
natural and believable, from the script. Copying the
grey figure's movement literally is the worst failure of this pipeline.

What the words still carry: who and what things look like (cast, wardrobe,
vehicles, place), the ACTING (body language, posture, gestures, expressions,
how someone walks, sits or reacts: written from the script, never from the
3D figure), the spoken lines, light, sound, and what happens out of frame.

Delegations, non-negotiable:
1. **Model behaviour and reference prep: `video-generator`** (its
   `references/models.md` cards). Read them before naming or reasoning about a
   model.
2. **Prompt wording: `cinematic-video-prompt-engineer`, in its DIRECT mode**
   (`精简模式`: final prompt only, no diagnosis or strategy). You hand it the
   take's facts as FIXED input (see "The prompt"); it writes the prose. It does
   not choose shots, durations or cuts here: the 3D already did.
3. **Timeline work: the engine and `timeline-assembler`.** Takes land on their
   clips by themselves; you never trim, stretch or move a 3D clip.

## 🔴 Step 0: resolution, asked once

Unless the user already named it for this video, ask the resolution
(AskUserQuestion, the values the take model accepts per its card) BEFORE
anything is generated, and pass it as `resolution` on every `generate_video`
of the pass. Never pick it yourself (user rule; the `video` tool refuses
without it). The aspect ratio comes from the 3D scene (`take.aspectRatio`);
ask about it only if the user wants a different format than the previz.

## Step 1: the previz must be current

The video can only be as right as its 3D. Before preparing takes:
- From a storyboard: `get_scene3d { storyboardId, storyTimeline: true }` →
  `storyTimelineId` (the montage). If the storyboard tools report a
  `previz3d` block (shots `missing`, `stale`, `orphans`), bring the previz in
  sync first (`scene-3d`), never render from a stale 3D.
- From any other timeline: the 3D clips the user picked (or every clip still
  in 3D).

## Step 2: prepare the takes

`prepare_scene3d_video { timelineId, clipIds }` (omit `clipIds` = every clip
still in 3D). **One take over several small ones:** consecutive clips of the
same 3D set (same track, end to end, ≤ 30 s) come back JOINED as one `take`,
their exact 3D windows (trim and slip included) baked end to end into one
`referenceVideo` that carries the camera, the blocking and the cuts. Separate
takes per clip only when the user asks (`oneTake: false`). Never render a cut
by hand, never pass a `scene3d:` path to a media tool.

Each take returns:
- `referenceVideo`, `durationSec`, `aspectRatio`, `model`;
- `shots`: per shot, where it falls in the take, its storyboard `script`
  (action, dialogue, sound, lighting), `onScreen` (who the 3D shows left /
  centre / right, how near) and `inFrameTimeline` (second by second: who is in
  frame and their view, what is near but out of frame);
- `castKey` (which grey figure is which character), `characters`, `place`;
- `objects`: the story's objects the take shows (a train, a motorbike), each
  with its previz look and reference images (its sheet, then its details), and
  `details` (`[{ label, path }]`): its story-critical close-ups and
  `Interior:` views;
- `referenceImages`: the character sheets, the place plates, the objects'
  images, the storyboard refs;
- `previousClip` when a finished clip precedes it on the track.

### References

Attach ALL the take's `referenceImages`, prepared per the model card, never
drop one to get a render through. If a character in the take has no sheet,
the place has no plate, or a story object it shows (a train, a motorbike) has
no object card with a sheet, build it first (`generate_character_sheet` per `characters`,
`generate_location_plate` per `locations`, the object's card and sheet via
the `objects` skill: `save_object` + `generate_object_sheet`, per the `story`
skill's rule 14), and likewise a critical DETAIL the take's shots rely on (a
close-up of a part, or an `Interior:` view for a shot inside the object) that
the card lacks: build it via the `objects` skill (`generate_object_detail`)
before rendering, with `metadata: { "visible": false }`,
persist it on the storyboard (`update_storyboard`) and prepare again. If a reference
still shows an OLD look the story has changed, stop and say so: a stale
reference brings the old look back.

## Step 3: the prompt (cinematic, direct mode)

Activate `cinematic-video-prompt-engineer` and ask for its DIRECT output in
ENGLISH (spoken lines stay in their original language, in quotes). Hand it,
per take:

**Fixed facts (it must not change them):**
- the take's shots in order, with their count; the take lasts `durationSec`;
  the cuts are exactly the 3D's;
- per shot, from `onScreen` and `inFrameTimeline`: who is in frame, their
  screen side, their VIEW (front / three-quarter front / side /
  three-quarter from behind / behind, and which side), what is near but OUT of
  frame and on which side. When the storyboard's words disagree with the 3D,
  the 3D wins;
- `castKey`: which grey figure is which character ("the boy, the small blue
  figure in the reference"), and `objects` the same way ("the steam train,
  the long grey shape in the reference, matches its reference image");
- each object's `details`, NAMED by their label in the prompt of the shots
  that show them ("the number 4417 painted on the boxcar door, as in its
  detail reference"). An insert / close-up shot of that part uses that detail
  as its reference; a shot INSIDE the object uses its `Interior:` views as
  references, the way a location plate anchors a set.

**Story material (what it writes about):** per shot, the `script`'s action,
dialogue VERBATIM, sound and light; the story's style line, identical on
every take; the continuity lock and the state that still holds (a prop
broken, someone already seated); the PHYSICS of any real action (force, arc,
contact, visible endpoint) and INERTIA: a falling, sliding or rolling body
keeps one direction and only slows down, changing it only at a named, visible
event; never words like "swinging left and right" or "tumbling" without that
event, which the video model renders as an impossible zigzag.

**Required shape of the prompt (feed it as constraints):**
- open by saying the attached video is the MASTER for CAMERA AND PLACEMENT
  ONLY: a grey 3D previz to be re-rendered photographically; its camera,
  framing, what is in and out of frame, positions, paths, sides and timing
  override anything in the text;
- right after, say plainly that the grey figures are crude placeholders: take
  only where each one stands, moves to and faces; do NOT copy their poses,
  limb movement or gestures; every person moves and acts naturally, as a real
  actor would, following the text;
- and that the reference's SURFACES carry no information: its flat grey
  materials, colours, shapes on the ground or walls and any pattern are NOT
  to be rendered; the look of every surface (ground, road, walls, vehicles)
  comes from the attached reference images and the text only. The take's
  reference is baked with every surface but the figures one matte grey
  (`flatSurfaces`), so nothing should be there to copy, but say it anyway;
- one block per shot ("Shot 1 (0–3.2 s): …"), the words "HARD CUT" between
  blocks, and once, plainly: "Cut ONLY at HARD CUT; never anywhere else";
- inside a block NO times at all (time marks read as extra shots): one
  paragraph saying the shot follows the reference video's camera EXACTLY as
  ONE continuous move, then in order what happens, chained with "then", "as",
  "while". Every change of framing inside a shot is the camera MOVING there,
  never a new shot;
- something that happens out of frame is said AS out of frame ("his car
  overtakes on the right, entirely out of frame: only its roar and her eyes
  following it"), never as seen. If the user wants it on screen, the 3D camera
  has to frame it first: tell them;
- never ask for a view the reference's camera does not have (the model cuts
  to get it);
- words go on WHO and WHAT things look like, light and sound, and above all
  on the ACTING: per shot, the body language, gestures, expression and the
  manner of each movement (how she walks, how he turns), invented from the
  script and the emotion of the beat, never read off the grey figure. Do not
  re-describe the camera or the paths the video already carries;
- light, wardrobe, props and the sound bed continuous across the cuts;
- the sharpest picture: crisp focus, fine detail in skin, hair and fabric, the
  reference's exact framing and headroom; no softness or degradation (soft
  focus, haze, heavy grain, low-res) unless the user asked for that look;
- each attached reference named with what it is (character sheet = identity,
  plate = the place's look); identity anchors, not start frames;
- no burned-in text: lines are audio, never captions;
- the closing audio note: NO MUSIC IN THE CLIP, even in the background or
  from a source in the scene (no score, song, humming or instrument). A band,
  a radio or a TV shown in the scene makes no sound of its own. Only sound
  effects, natural ambience and the characters' voices. Only if the user asks
  for music inside the clip may it have it.

Use cinematic's prompt VERBATIM. Before rendering, check it against the
facts: same shot count and order, every line present, sides as the 3D shows
them. If something is off, send it back with the fact restated; never patch
the prompt yourself.

### Continuity from the previous take

When a take has `previousClip` and its scene continues from it:
- **Selective continuity frames:** extract (`extract_frame`, full-res,
  `metadata: { "visible": false }`) only the frames carrying state this take
  must match (usually the previous clip's last frame), each attached under a
  role alias (`prev_end`, …) with one legend line saying exactly what it binds.
  Nothing binds (new place, time jump, nobody carries over) → attach nothing.
  Never compose frames into a grid.
- **Sound:** extract the previous clip's audio tail
  (`ffmpeg -sseof -15 -i <prev.mp4> -vn -q:a 2 <tail>.mp3`) and pass it as
  `referenceAudio` when the card supports it; ALWAYS also describe the bed in
  words (listen with `ask_video`: the ambience layers, their level, what is
  still sounding at the cut) so cinematic writes that the bed CONTINUES, with
  the layers named.
- Spell the opening state out in words (screen sides, momentum), even with
  no frames attached.

## Step 4: generate

Per take, `generate_video` with:
- `model`: the take's `model` (Seedance 2.5 reference-to-video), read its
  card first;
- `referenceVideos: [referenceVideo]`, ALL `referenceImages` (+ continuity
  frames), `referenceAudio` when used;
- `duration: durationSec` (never shorter: clip lengths are protected),
  `aspectRatio`, `resolution`: the user's choice;
- `withAudio: true` (music is excluded in the prompt, never with
  `withAudio: false`);
- `storyboardId`, `sceneId`, `shotIds` as TOP-LEVEL params when it comes from
  a storyboard;
- the prompt from Step 3.

Several takes: start them ALL with `wait: false`, then await. Exception: a
take that chains continuity frames from a previous take being generated in
this same pass waits for that one.

## Step 5: review and land

🔴 **The user's change is the truth.** A change the user asks for (a pose, a
speed, a camera, a duration, an action) is carried into EVERY place that
describes that moment: the 3D scene AND the story script (`update_storyboard`:
`action`, `shot`, `camera`, `composition`, `continuity`, `duration`). The new
wording is never improvised: it is written with the
`cinematic-video-prompt-engineer` skill (poses, faces, acting, movement,
camera, lenses, staging), exactly like the rest of the story, and the 3D and
the take prompts follow that wording. The old script wording is what is out of
date: never warn that "the script says otherwise", never revert the change to
match it. Ask only when two of the user's own requests contradict each other. When `prepare_scene3d_video` or your own review finds the
previz and the script disagree because of such a change, update the script
(and the take prompt) to the previz before generating; do not stop to flag it.
The same before every take: `prepare_scene3d_video` returns `physics.motion`
(distance, time, speed, natural step count of each movement; each pose change
and how long it takes). The take prompt and the script must say exactly what
those numbers allow ("two steps back" needs ~1 s; 0.45 s is one step); fix
the wording with cinematic or re-time the 3D yourself, before generating.

1. **Watch each take** (`read_file` the mp4, or `extract_frame` around each
   shot) against the previz and the scripts: shot count and cuts, composition
   and camera move, who is where, state, light, sound.
2. **Repair surgically.** More than half the shots wrong → regenerate the
   take (same references, corrected prompt, never thinner). Otherwise fix only
   the bad shots: locate the real cut times on the render (ffmpeg scene
   detection), have cinematic rewrite that ONE shot's prompt with the defect
   stated as a correction, generate it as a single shot with the same
   references (continuity frames chosen by need, never as `startFrame` across
   a hard cut), and `replace_take` (in place; `take_history` /
   `restore_take` bring back an earlier version).
3. **Landing:** a take generated from `referenceVideo` lands on its clips by
   itself (the result says `scene3dTake`): each clip starts at the take's real
   cut nearest the planned one and keeps its length. Call
   `assign_scene3d_take { timelineId, clipIds, mediaPath }` only to put a
   DIFFERENT file on the clips. When the 3D changes later the clips are
   flagged out of date (`scene3d.renderStale`): offer to regenerate them.
4. A failed generation (filter, policy, provider): retry the identical
   request first, then fix the cause by its sanctioned mechanism (see
   `video-generator`); never drop a reference or thin the prompt to force it.

## Step 6: music and hand-off

- **Music** only when the story calls for it AND there are ≥ 2 takes: ONE
  `generate_audio` (`type: "music"`, `duration` = the whole montage), laid on
  its own audio track of that timeline from 0, never on V1. Duck it only under
  dialogue (≈ −28 dB), per `timeline-assembler`'s mixing levels. One take
  alone may carry music in the clip only if the user asks.
- **Voice drift** across takes: if a character's voice audibly changes, offer
  one TTS pass of the lines with a fixed voice on an audio track.
- End with the timeline shown (`show_timeline { id }`). Export only when the
  user asks (`render_timeline` → `show_video`).

## Don't
- Re-decide shots, cuts, durations, framing or screen sides: the 3D owns them.
- Render from a stale or missing previz.
- Hand-write or edit the take's prompt: cinematic writes it from the facts.
- Pick the resolution yourself.
- Drop a reference, or attach a storyboard panel image as a reference.
- Trim, stretch or move a 3D clip to fit a take, or generate shorter than
  `durationSec`.
- Put times inside a shot block, or describe as seen what the 3D keeps out of
  frame.
- Burn text into the video, or let music into the clips.
- Search the disk for a storyboard or scene: ids come from the conversation,
  the working area or the tools.
