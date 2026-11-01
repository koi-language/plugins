---
name: physics-of-motion
description: "MANDATORY whenever a script, 3D previz or video prompt contains a body, vehicle or object in real motion: running, jumping, falling, being hit, tumbling, fighting, chases, crashes, throwing, carrying, riding, water, moving vehicles. The rule book for how things really move and how motion reads as weighty and alive: per-situation rules with the numbers to compute (speed, distance, stopping time) and the beats each action must play (anticipation, action, reaction, settling). Use it when WRITING the action, when PLANNING it in 3D and when wording the video prompt. Triggers (any language): física, físicamente imposible, inercia, parece un videojuego, antinatural, caída, salto, rueda, voltereta, choque, pelea, persecución, physics, inertia, looks fake, video-game feel, floaty, weightless, tumble, stunt, crash."
---

# Physics of motion

Viewers feel fake physics instantly, even when they cannot say why. Most of it
comes from one mistake: the action is written as its result ("he lands on the
train and slides a little") instead of as what forces do to a body.

Treat this as the default for every story. If the user or the script explicitly
asks for the unreal (a superhero, a cartoon, a dream, slapstick), do exactly
that, never correct it. Keep it internally consistent: decide what is bent and
keep everything else real.

## The method: run it for every physical action

1. **Situation.** Which sheets below apply? Often several (a jump onto a train:
   Jumping, Falls and impacts, Moving surfaces).
2. **Numbers.** Before and at contact: speed, direction, height, mass. Compute
   distance and time from them with the formulas here. Never guess.
3. **Beats.** Write the whole arc: anticipation, action, contact, reaction,
   settling. A result without its reaction is the video-game look.
4. **Fit.** Add up the beats' real durations. When they do not fit the shot,
   lengthen the shot, cut away on purpose, or change the action. Never compress
   physics to fit a duration.
5. **Causes.** Every change of speed or direction names its visible cause. No
   cause, no change.

Worked example: a man leaps from a bridge onto a train at 54 km/h (15 m/s). He
has almost no forward speed, so the roof passes under him at 15 m/s. At about
5 m/s² of friction: 15/5 = **3 s** and 15²/(2×5) = **22 m**, a whole wagon,
thrown toward the TAIL, turning over about eight times, losing speed with every
hit. A hand can only catch something once he has slowed down. "He lands and
slides a little" is impossible, and so is any plan that needs under 3 s.

## Formulas

| What | Formula | Examples |
|---|---|---|
| Stopping time | `t = v / a` | 15 m/s at 5 m/s²: 3 s |
| Stopping distance | `d = v² / (2a)` | 15 m/s at 5 m/s²: 22 m |
| Fall time | `t = √(2h / 9.81)` | 1 m 0.45 s, 2 m 0.64 s, 5 m 1 s, 10 m 1.4 s, 20 m 2 s |
| Impact speed | `v = √(2 × 9.81 × h)` | 1 m 4.4 m/s, 3 m 7.7 m/s (28 km/h), 10 m 14 m/s (50 km/h) |
| Thrown range | `d ≈ v² / 9.81` at best angle | 15 m/s: ~23 m |
| Tightest curve | `r = v² / (μ × 9.81)` | runner 6 m/s: ~5 m; car 20 m/s: ~50 m |
| Two bodies that stay together | `v = m1 × v1 / (m1 + m2)` | 80 kg at 6 m/s tackles 80 kg: 3 m/s together |
| Relative speed | `v_rel = v_body - v_surface` | what the body feels on landing |

Friction deceleration (`a ≈ μ × 9.81`) of a body on: rough concrete, asphalt or
a steel roof 4-7 m/s²; grass or wet metal 3-4; packed snow 1.5-3; ice about 1.
Tires: see Vehicles.

## Situation sheets

### Walking and running
- Walk 1.2-1.8 m/s, ~2 steps/s. Jog 2.5-4 m/s. Hard run 4-6 m/s, ~3 strides/s.
  All-out sprint 7-9 m/s and only for seconds. Counted steps must match the time.
- **Starts and stops have steps.** Reaching a sprint takes 2-3 s (10-15 m).
  Stopping from a run takes 2-3 strides (0.5-1 s, 1.5-3 m), body leaning back.
- **Turns cost speed.** A sharp turn at a run: slow down, plant the outside foot,
  lean in, push off. A 90° turn at full speed with no loss is a video game.
- Fatigue shows: a long run gets slower and rougher. Backwards is about half the
  speed. Stairs up 0.5-0.8 m/s per floor's slope length; uneven ground shortens
  the stride.
- *Video-game errors:* full speed from the first frame, instant stops, gliding,
  turning on a point.

### Jumping
- Beats: run-up or crouch, push-off, flight with the body shaping itself,
  landing that bends knees and hips.
- Rise 0.5-0.9 m. Air time 0.5-0.7 s. Standing jump 1.5-2.5 m, running jump
  2-4 m. A gap above 5 m needs an athlete and a long run-up.
- The flight is a parabola and cannot be steered: no change of direction in the
  air, only the limbs move.
- Landing absorbs speed: under ~2 m with bent legs and a step or two; ~2.5-4 m
  needs a roll; forward speed carries on into running steps or a tumble.
- *Video-game errors:* floating, steering in the air, landing stiff and walking
  off, no crouch before and no bend after.

### Falls and impacts
- **Decide three things: what touches first, where the energy goes, how long
  until the body is still.** Energy goes into a tumble, a bounce, a slide, a
  crumple, or breaking something.
- Toppling over from standing takes 0.8-1 s; hands and arms react on the way.
- A body thrown along a surface does not slide like a puck. It hits, turns over,
  hits again, losing speed each time, limbs loose and flung outward. Use the
  stopping formula; its direction stays one line.
- **🔴 Inertia.** With no footing a body keeps its direction and only slows down
  until something acts on it. Any change needs a named, visible event in that
  beat: a blow, an obstacle, a hand gripping. Never "swinging left and right" or
  weaving.
- Injury is real: a hard hit leaves a limp, winded breathing or stillness for
  seconds. Nobody springs up right after. Getting up from the floor takes
  1.5-2.5 s, more when hurt.
- A grip cannot stop a fast body: above about 4-6 m/s it tears loose or wrecks
  the arm. Slow down first, then the hand catches, and the arm takes the load.
- *Video-game errors:* landing and sliding a little, stopping dead, getting up
  at once, a rigid body, hits with no reaction.

### Moving surfaces (trains, trucks, boats, platforms)
- Always think in relative speed. Landing on something moving: the body keeps
  its old speed, so it is thrown toward the REAR of the vehicle. Stepping off at
  speed: thrown FORWARD along the ground at the vehicle's speed.
- Standing on it: braking throws you forward, accelerating backward, a curve
  outward, a sway or a bump needs a wide stance or a handhold.
- Open air at speed: at 15+ m/s wind pushes hard, clothes and hair stream back,
  people crouch and hold on. A boat heaves, a truck bed jolts.
- The background must keep moving at the vehicle's speed during the whole action.
- Walking along a vehicle: judge only the person's own effort, at normal
  walking and running speeds.

### Fights and blows
- A blow starts at the feet and hips: weight shifts, then the shoulder, then the
  arm. A real swing is 0.1-0.3 s of action after a visible wind-up, which is
  what lets the other person react.
- Whoever gets hit reacts in the direction of the blow: the head snaps, the body
  staggers 1-2 steps, the hands come up. A punch does not throw anyone metres.
- Heavier bodies move less; a light fighter bounces off a heavy one.
- A body that hits a wall stops there and rebounds slightly, and the wall or
  furniture reacts. Falls follow the falls sheet.
- Fights tire people quickly. Distance, grabs and clinches are common; a clean
  exchange of many blows is not. Pain and damage carry over shot to shot.
- A gunshot does not throw a body back: it drops or stumbles. A blast can throw
  someone a few metres, and they land by the falls sheet.

### Vehicles
- Acceleration: car 3-5 m/s², sports car up to 8, motorbike 5-9, bus or truck
  1-2, train 0.3-1.5. Braking on dry road: car or motorbike 7-9 m/s², truck 4-6,
  wet road about half, train 0.5-1.5 (from 90 km/h: ~25 s and ~300 m).
- From 100 km/h a car needs ~3.5 s and ~45 m after ~1 s of driver reaction.
- Heavy things change speed slowly: a train cannot jump from 20 to 50 km/h and
  cannot stop for a person. Speed changes must build over time.
- Cornering: the body rolls outward and passengers lean out; at the limit the
  tires slide wide. A motorbike leans in. Nothing turns at speed without a radius.
- Braking pitches the nose down, acceleration lifts it; suspension settles after
  bumps. Jumps land nose-heavy and hard.
- **Crash:** ~0.1 s, the front crumples 0.5-1 m, both vehicles keep moving
  together by the two-body formula, spinning if hit off-centre. Unbelted people
  continue at the old speed into whatever is in front of them. Objects inside fly
  forward. Debris and glass carry on along the same direction.
- A rider separated from a motorbike keeps its speed and follows the falls sheet;
  the bike slides on its side separately, throwing sparks.

### Objects
- **Weight is shown through the body.** Under ~5 kg: one hand, no change. 10-20 kg:
  both hands or leaning the other way, slower. 30+ kg: from the legs, back
  braced, short steps, breath. Anything light must not be lifted with strain, and
  anything heavy must not be swung around easily.
- Throw: preparation, step, hips, arm. A stone 15-20 m/s, a 5 kg object 3-6 m.
  In the air it follows a parabola and spins steadily.
- A released object keeps the speed of whoever released it; a dropped thing falls
  by the fall formula. Things never hover, or drift down, unless they are light
  (paper, cloth, feathers).
- What it does on landing depends on the material: rubber bounces, wood clatters
  and tumbles, metal rings and rolls, glass breaks and spreads forward, cloth
  folds, liquid splashes along the direction of travel.
- Cause and effect in contact: a push moves the object only while the hand is
  there, then friction stops it. Doors swing on hinges and rebound. Nothing moves
  before it is touched.

### Several bodies
- Every contact has two sides. If one hits, both react, and the lighter takes
  more of it (two-body formula). A collision between runners stops or tangles
  both; a tackle travels on together and falls.
- Holding or pulling someone: both lose speed, and the puller leans and braces.
  Carrying an adult (70 kg): ~1 m/s, a run only for moments. Dragging: short
  jerks and backward lean.
- A hand-off or a catch takes up the object's speed: the catcher's arms give way
  and they may step back.
- In crowds, a push travels as a wave, and bodies part or fall around an obstacle.
- Timing between bodies needs a shared clock: the reaction starts at contact,
  never before.

### Water, snow, mud, wind
- Water brakes hard: a jump in stops within 1-3 m, with a splash scaled to speed.
  From 10+ m it hurts. Swimming 1-2 m/s. Wading to the waist 0.5-1 m/s, high knees
  and arms out. Wet clothes drag and hang heavy coming out.
- Snow or mud: 1-2 m/s at most in deep going, the foot sinks and pulls out, falls
  are soft and short. Ice: small steps, arms out, and a slide lasts until friction
  or an obstacle ends it.
- Strong wind: lean into it, shorter steps, hair and cloth streaming with it.

### Time and editing
- **Slow motion slows EVERYTHING in the shot by the same factor:** bodies,
  vehicles, dust, water, background. Never one element alone.
- Speed and direction carry across a cut. A body that leaves a shot at 15 m/s
  enters the next at 15 m/s, going the same way.
- A cut can skip time only when it reads as a jump in time. It may not hide
  impossible physics in continuous action.
- After the action, the state persists: bruises, dust, torn clothes, broken
  props, breathing hard.

## Motion craft: how real motion also reads as alive

The physics says what is possible; this says how it reads. It applies to bodies,
vehicles, props, and the camera.

### Name the problem first
Diagnose in one line before changing anything. "Janky" is almost always one of:
- **Robotic:** constant speed, dead stops. Fix the speed curve.
- **Floaty:** too slow for its weight or size, soft start where it should snap.
  Fix the timing and the curve.
- **Janky:** everything moves together, on one flat timeline, with no offset. Fix
  the spacing and stage it.
- **Dead:** correct but lifeless, no wind-up, no overshoot, no reaction. Add the
  arc and the secondary motion.

### The speed curve matches the force
- **Fast start, slow settle** (ease-out): what was thrown or struck, and anything
  stopping by friction. A tumble starts at its fastest.
- **Slow start, fast end** (ease-in): what gravity or an engine accelerates; what
  is leaving at speed; a fall.
- **Slow, fast, slow** (ease-in-out): what is self-powered from A to B: a person
  crossing a room, a car between stops, a deliberate camera move.
- **Overshoot and settle** (spring): anything with give: suspension, a body
  catching itself, a door on its hinge, a camera operator landing a frame. Less
  damping is bouncy, playful; more is tight, heavy. Use it only for physical
  things; a value that must land exactly (light level, a fade, exposure, a rack
  of focus) changes on a precise timed ramp, with no overshoot.
- **Constant speed** only for what truly holds one: a cruising train, a conveyor,
  a drifting cloud. Never for a body starting or stopping.

### Timing and spacing
- Duration scales with **distance, size and mass**. Same move, longer distance:
  longer. Bigger or heavier: slower to start and to stop. Few frames read as
  light and sharp; many as heavy and deliberate.
- Spacing is how distance spreads over the frames. Frames bunched at the end is a
  settle; bunched at the start is an acceleration.
- Starting and stopping are not symmetric: a run builds up over seconds and stops
  in a stride; a thrown body has no build-up at all.

### Anticipation, action, follow-through
1. **Anticipation:** the small opposite move before the main one (the knee bends
   before the jump, the arm draws back, the car's nose dips before it launches).
   It primes the eye. Keep it brief; a struck body has none, because it did not
   know. That absence is what makes an ambush read as an ambush.
2. **Action:** the main move with its speed curve.
3. **Follow-through:** what continues after the main move stops. The arm carries
   on after the punch, the knees absorb the landing, hair, coat and bag arrive
   late. Without it the move reads as dead.

### The twelve principles, applied to live-action bodies
1. **Squash and stretch:** bodies compress through joints: knees and spine on
   landing, cheeks and shoulders on impact. Vehicles do it through suspension.
   Limbs never deform.
2. **Anticipation:** as above.
3. **Staging:** one main action at a time, placed where the eye is. Six things
   moving equally means no story.
4. **Straight-ahead and pose-to-pose:** plan key poses and contact moments first,
   then what links them. Chaotic things (a tumble, debris) run forward from their
   cause.
5. **Follow-through and overlap:** parts stop at different times. Hips, then
   torso, then head and arms, then clothing.
6. **Slow in, slow out:** the speed curves above.
7. **Arcs:** limbs swing on arcs from their joints, thrown things on parabolas,
   turning people and vehicles on curves. Straight-line motion looks mechanical.
8. **Secondary action:** breath, a hand reaching for balance, dust rising, a bag
   swinging. It supports the main action and never competes.
9. **Timing:** frames give weight and mood.
10. **Exaggeration:** hold it to choosing the most telling instant and pose, in
    framing and in lens. In a realistic story never beyond the numbers here. Bolder
    only when the story's style asks for it.
11. **Solid drawing:** weight, balance and volume. A person's centre of mass stays
    over their feet unless they are falling or moving; a leaning body is doing
    something about it.
12. **Appeal:** clarity of silhouette and intent. The action reads at a glance.

### Hold the plan as a spec
For every significant physical action, keep these lines in your working notes:

```
ACTION    what happens, sheets used
NUMBERS   speed, relative speed, height, mass; distance and time computed
BEATS     anticipation / action / contact / reaction / settle, each with seconds
CURVE     per moving thing: settle, accelerate, A to B, spring or constant
CAUSES    each change of speed or direction and what visibly causes it
OVERLAP   what lags: hair, coat, bag, dust, debris
AFTER     what state carries on into the next shots
```

## Where it applies

### Writing the script
Write the full arc, with its distances and durations in plain words, and make
the shot as long as it needs. A viewer's "he lands" becomes: *"He hits the roof
shoulder first and the train tears him backward: he turns over and over along
22 metres of steel, arms flung loose, slowing with every hit, for three seconds,
until he stops flat on his stomach near the wagon's end."* Name causes. Avoid
wording that the video model renders as a zigzag ("swinging", "tumbling back and
forth").

### Planning the 3D
Translate the computed numbers into positions and times:
- A body thrown along a surface: `{ character, type: "tumble", to, startMs, endMs,
  aboard?, roll?, turns?, pose? }`. It bakes the constant-friction stop and really
  turns over; never fake it with a walk in several legs or a slide in a held pose.
- A vehicle keeps a speed consistent across legs, changing it gradually over
  several legs.
- If the script asks for what cannot be, re-time or rewrite it and keep them
  matching, as `scene-3d` requires. A change the user decided is theirs to change.
- `physics.warnings` catches part of this: impossible speeds, stops too hard for
  friction, a hard landing with no reaction, a vehicle's sudden speed change, a
  zigzag. Passing it does not make an action real: run the method anyway.

### Wording the video prompt
The previz gives camera, place, path and timing. The body's mannequin is never
copied, so the prompt must carry the physical performance: what touches first,
the turning over, loose limbs, the speed dying off, the state at the end. A
tumble in the reference gives direction, rhythm and duration; a real actor's
body performs it.
