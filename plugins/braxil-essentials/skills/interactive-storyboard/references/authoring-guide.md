# Authoring Guide: field-by-field detail, precision rules, style policy

Load this when actually WRITING or EDITING storyboard content. The SKILL.md holds the schema skeleton, the flows and the hard gates; this file holds the full field semantics, the precision bar with worked examples, and the stylePrompt policy in depth.

## Field semantics (v6), beyond the skeleton

### `seed`
Integer, picked ONCE at creation. The same seed across every shot gives consistent characters and palette. Never change it on a modify unless the user asks for a full visual reroll.

### `characters` (storyboard-level roster)
Define every recurring character with a LABEL plus a silhouette-based description: clothing, proportions, accessories, distinguishing traits. NOT facial details (faces are unreliable anchors for the renderer; silhouette plus wardrobe is what locks identity).

- Label convention: SHORT_UPPERCASE with A/B/C variant suffix: `HERO_A`, `DOG_A`, `MONSTER_A`, `CROWD_A`.
- Reuse the label EXACTLY in every `action`/`dialogue` that features the character. Never drift to "the hero" or "she" mid-storyboard.
- The compositor (a small LLM at render time) inflates each label into an inline description in the final English image prompt, so the stateless image model always knows who is who. Defining the character once in the roster is enough; do not restate the description per shot.

### `lighting` (storyboard-level)
Free text, user's language. ONE lighting design for the whole piece (real productions lock lighting per piece, not per frame). Injected into every shot prompt and translated to English by the compositor. There is NO per-shot lighting field in v6.

### `synopsis` (storyboard-level, and optional per-scene)
The story premise and physical/causal logic the renders must never contradict: WHY things happen, what is or is not reachable, who wants what. Injected into EVERY shot's image prompt. Fill it always except for a bare unconnected shot list. Scene-level `synopsis` adds per-scene logic on top of the global one in multi-scene pieces. MANDATORY when storyboarding from a video (write the real premise you watched).

### `continuity` (storyboard-level LOCK, array of strings)
Absolute, story-wide INVARIANTS and NEGATIVE constraints: what must NEVER change or happen across panels. Each rule is injected VERBATIM into every shot's image/video prompt as a hard constraint.

- `synopsis` says WHY; `continuity` says WHAT MUST NOT CHANGE.
- Image models need the negatives spelled out ("do NOT lower the button", "the cans stay INTACT, never crushed"). This is what stops the renderer from silently making the unreachable reachable, resizing things, or breaking an object that must stay whole.
- Omit only for a bare shot list with no physical logic.

Example:
```jsonc
"continuity": [
  "The Pepsi button stays mounted high on the machine, above the boy's reach until he climbs.",
  "Never make the boy taller or lower the button; the gap stays obvious.",
  "The cans he stacks as a step stay INTACT, never crushed or dented."
]
```

### Per-shot `continuity` { characters, objects, place }
The continuity-table ROW for that exact panel, in the user's language:

- `characters`: who is in frame and their exact state (position, pose, what they wear/hold, expression). Example: "NIÑO_A de pie sobre las dos latas apiladas, dedo tocando el botón".
- `objects`: the state of every key prop/scenery in frame. Example: "las dos latas apiladas intactas bajo sus pies; botón Pepsi ahora alcanzable".
- `place`: WHERE this exact panel physically happens, restated per shot. Example: "Bajo el agua, en una calle de la piscina, entre dos corcheras".

The compositor composes these into CURRENT PANEL STATE plus SHOT LOCATION so the render shows exactly this state, in exactly this place: not a reset-to-default, not a later beat, not a void or wrong background on a close-up. The columns read top-to-bottom across all shots ARE the continuity table the user reviews in the visor.

- Fill `place` on EVERY shot of a scene with a strong or recognisable setting (underwater, inside a car, a specific room) so even tight close-ups stay anchored there. This is the fix for the reported "close-up out of the scene" bug: a poolside scene whose close-ups (a face, a hand, goggles) rendered a DRY kid in a corridor, because the bare `action` described only the face and the location was never restated.
- Fill `characters`/`objects` on any panel where a NON-default state holds (standing on a stacked object, holding or using something, a machine left open, an object moved, broken or placed).
- Authoring the table is also how you CATCH a self-contradicting script: if panel N's `objects` says "lata aplastada" but panel N+1 needs "de pie sobre la lata", the table makes the contradiction obvious. Fix the `action`; do not ship it. (That exact crushed-can-then-step-on-it bug is why this field exists.)
- **Declare ABSENCES too (closed world).** For any transient element that appears in some shots and leaves (a falling object, a character who exits, a consumed prop), the shots AFTER its exit must state the absence explicitly in `objects` ("el sable YA NO esta en la sala: ningun sable ni resplandor azul en el plano"), not just describe what remains. Renderers infer presence from neighbouring panels; absence only holds if it is written. (Reported bug: the fallen saber, already gone through the floor, kept being painted back into the chase shots because their rows never negated it.)

### `dialogue`, `sfx`, `music`
- `dialogue`: spoken lines / voice-over, quote each speaker so it is parseable. Used as a CUE for facial expression in the image prompt; the model does not render the words on-frame.
- `sfx` and `music`: free text audio cues. NOT used by the image prompt today (reserved for future audio generation); editing them does not invalidate the rendered image cache.

### `shot` and `movement`
- `shot` MUST be EXACTLY one of the app's shot presets, copied verbatim. NOT free text; never invent or combine framings ("Medium long shot, high angle" is not a preset and renders with no thumbnail). `save_storyboard` rejects invalid values and lists the valid presets in the error; the list grows with the app, so never hardcode or guess it. If unsure, read the validation error or `get_tool_info(save_storyboard)`.
- `movement` IS free text: "Static", "Pan left", "Dolly in", "Crane up", "Steadicam follow".

## Writing the `action` text: PRECISE, leave NOTHING to chance

The `action` is the SOURCE OF TRUTH for the whole pipeline: the visual sheets and the final video are rendered from it, and image/video models render your words literally, filling every gap with a plausible-but-often-WRONG detail (a hand fanning 3 coins, a contradictory pose, the wrong button). The bar: NOTHING in the `action` may be doubly interpretable; every object, count, target and position must resolve to exactly ONE thing. If a phrase could be staged two different ways, it is wrong; pin it down.

- **Exact count, never a vague plural.** "inserta monedas" becomes "inserta UNA ÚNICA moneda, sujetándola entre el pulgar y el índice". "presiona el botón" becomes "presiona UNA SOLA VEZ el botón".
- **Name the specific target.** "el botón inferior" becomes "el botón de abajo (de una fila de 6)". "la ranura" becomes "la ranura de monedas, a la derecha del teclado".
- **Concrete identifier, never a relative or interpretable reference.** A reference the model cannot resolve to one exact thing means it picks one at random. "pulsa el botón de su planta" becomes "hay 16 botones de planta; pulsa el botón 2". "coge su maleta" (which one?) becomes "coge la maleta ROJA que está a su izquierda". "mira el cuadro" becomes "mira el cuadro DE LA IZQUIERDA, el del barco". Numbers, colours, positions, named items: anything that turns "one of several" into "exactly this one".
- **The HOW: grip, finger, posture, direction.** Not "se estira hacia arriba y presiona el botón inferior" (contradictory: stretching up for something low) but "se pone de puntillas y presiona con el dedo índice el botón de abajo".
- **One physical action per shot**, done the way a real person does it. If the beat is insert-coin then press-button, that is two shots, each with its single precise mechanic.
- **No exempt shots.** Product shots, logo shots and establishing shots get the SAME precision (exact subject, exact mechanic, exact target) as any character action. "primer plano de la lata girando sobre fondo negro" FAILS (who or what moves it, how?): write "primer plano de la lata de Pepsi sostenida por la mano del niño, que la gira lentamente hacia cámara hasta que el logo queda de frente".
- Precise does not mean a wall of text: one tight, unambiguous sentence per shot, in the user's language, readable in the visor.

### Carry-forward state (the #1 continuity bug)
When a shot puts the character or world into a NON-default state (standing ON a stacked object, holding something, a machine opened, an object moved, broken or placed), EVERY later shot where that state still holds MUST restate it explicitly in its `action`. The renderer treats each panel/clip semi-independently and silently resets to the default unless the text re-states the state.

The exact reported bug: shot 5 = "se sube encima de las dos latas apiladas"; shot 6 said only "presiona el botón" and rendered the boy back on the ground. Shot 6 must say "DE PIE TODAVÍA SOBRE LAS DOS LATAS APILADAS, presiona con el índice el botón de arriba". The state persists in the text until a shot explicitly changes it. Same for raccord basics: same object, same hand, same machine state shot to shot, plus lighting and time-of-day consistency.

The per-shot `continuity` object and the storyboard-level `continuity` LOCK (above) are the structured backstop for this rule: assert state and place explicitly per panel instead of hoping prose carries it.

## Continuous takes: `noCutBefore`

A shot with `"noCutBefore": true` is glued to the previous shot as ONE continuous take: the camera keeps moving, there is no cut. Consecutive glued shots render as a SINGLE video clip; continuation panels share the take's number badge.

WHEN to use it (the high-value case): whenever a shot involves camera movement (dolly, crane, pan, orbit, push-in, tracking) and lasts more than 1-2 seconds, do NOT describe it as one vague panel ("dolly in over 5s"). Break the move into SEVERAL glued sub-takes: the START of the move, a MID beat, the END framing, each authored as its own panel with `"noCutBefore": true` on every panel after the first. They still render as one uninterrupted shot, but the move is described beat by beat (framing, action, continuity at each moment), which is far more controllable than a single panel where the model invents the whole trajectory.

Rules:
- The FIRST panel of a glued group has NO flag; the 2nd, 3rd... carry `"noCutBefore": true`.
- NEVER set it on the first shot of a scene (a scene boundary is a cut by definition).
- Carry continuity across glued panels exactly as across any shots (one take: drift is even more obvious).
- The take's on-screen duration = the SUM of its panels' durations.
- Static shots rarely need splitting; this is for MOVING shots long enough to read the motion.

Example, a 5s push-in as 3 glued panels (one take, no cuts):
```jsonc
{ "number": 4, "duration": 1.5, "movement": "Dolly in",
  "action": "El plano arranca ABIERTO: HERO_A pequeño al fondo del pasillo vacío." }
{ "number": 4, "noCutBefore": true, "duration": 2.0, "movement": "Dolly in",
  "action": "La cámara sigue avanzando hacia él; su rostro empieza a leerse, sigue sin moverse." }
{ "number": 4, "noCutBefore": true, "duration": 1.5, "movement": "Dolly in",
  "action": "Cierra en PRIMER PLANO de sus ojos; la cámara se detiene." }
```

## `references`: visual anchors at three levels

Each of the three objects (storyboard root, every `scenes[]` entry, every `scenes[].shots[]` entry) may carry an optional `references` array. Each entry is a STRING: a `@mention` handle (gallery asset, e.g. `"@hero_pose"`) or an absolute path to an IMAGE file. The visor renders them as thumbnails/chips and the user can add them by typing `@handles` or dropping images.

Scope cascade (most specific wins, broader ones still apply):
- storyboard-level: applies to EVERY shot (recurring hero, global look board).
- scene-level: every shot in THAT scene (the location plate).
- shot-level: that single shot (a specific prop or pose).

At render time the visual-panels skills collect the references in scope per shot and pass them as `referenceImages` (resolving `@handles` to paths) to lock identity. Omit the field entirely when empty; do not write `"references": []`.

**IMAGES ONLY, never the source video.** A video/audio path (`.mp4`, `.mov`, `.mp3`) in `references` is a BUG: it cannot be decoded as an image and crashes the whole sheet render. When storyboarding a source video you WATCH it with `read_file` (see from-video.md); the clip itself is NOT a reference. If you want a still from the video as an anchor, save that frame as an image first and reference the image path.

**Describe the person in the photo; never invent, never keep the OLD look.** When the user gives a reference photo to DEFINE or RECTIFY a character, `read_file` that exact image BEFORE writing one word of the description, and base the `characters` roster entry on what you actually SEE: hair (or none) and colour, facial hair, build, skin, clothing, accessories. When rectifying, the new photo OVERRIDES whatever the storyboard said before: do not carry the previous description forward and do not describe the existing pencil sketches (those are the OLD appearance being replaced). Reported bug: user uploaded a man WITH hair under a beanie and a thick dark moustache; the agent wrote "completely bald, grey stubble, white tank top", confabulated from the old sketches. Read the pixels; the photo wins.

## `stylePrompt` policy: empty. ALWAYS. Unless the user spelled out a style.

The user has reported violations of this rule MORE THAN ONCE. The default look is a rough pencil-on-paper animatic (black-and-white graphite sketch, simplified faceless characters, minimal shading). It is the ONLY correct look unless the user EXPLICITLY asked otherwise. Storyboards communicate blocking and pacing; "upgrading" them to colour anime / Pixar / noir makes the storyboard stop reading as a storyboard.

- Default action: `"stylePrompt": ""`. Every time. The agent gets NO creative input on visual style; the user's words decide.
- Topic is not style. "ninjas" is a topic; "estilo anime" is a style. A topic NEVER implies a style: "una pelea entre ninjas", "una cena de mafiosos", "un gatito y un perrito" all stay pencil sketch.
- Your chat reply must NOT announce a style choice ("voy a darle un acabado estilo anime") for plain requests; announcing it is itself the bug.

You ARE allowed to set stylePrompt ONLY when the user's literal words request a style: "en estilo anime", "make it Pixar", "en acuarela", "film noir", "al estilo de Ghibli", "como Sin City", or they attached a reference image saying "make it look like this". The trigger must be IN THE USER'S MESSAGE, not in your interpretation. If they did not use words like those, the answer is `""`. Do not negotiate with yourself.

Anti-examples (each has happened; each is a bug):

| User said | WRONG | CORRECT |
|---|---|---|
| "haz un storyboard de 6 clips de la lucha entre 2 ninjas" | "Estilo anime de alta calidad, iluminación dramática..." | `""` |
| "haz un storyboard de una cena de mafioso" | "Estilo cine negro clásico, alto contraste..." | `""` |
| "un storyboard con el gatito y el perrito" | "Estilo película de animación 3D, colores vibrantes..." | `""` |
| "haz un storyboard de un dragón" | "Estilo fantasía épica, dramatic lighting..." | `""` |

The pattern in every WRONG row: the user described a TOPIC and the agent invented a STYLE on top. Stop doing this.

## Duration details

- A duration the user named upfront ("un anuncio de 60 segundos") is only a SIZING HINT for the FIRST draft: it tells you roughly how many shots and how long each (60s is about 8-12 shots of 4-8s). Use it for that and only that.
- Once the storyboard exists, its CURRENT summed total wins, always. The user edits shots and duration sliders in the visor on purpose; the new total IS the new runtime. When asked to render or report length, `read_file` the storyboard and re-sum the current durations; never use the number from the brief or from memory. If they trimmed to 48s, the ad is 48s: never silently re-stretch to re-hit the original target (reported bug).
- The ONLY exception: an explicit, current hard-target instruction ("mantenlo en 60s pase lo que pase"). Then retime and tell the user which shots you changed and why.

## Language rules

The storyboard JSON is a USER-FACING document, not a prompt. Write EVERY free-text editorial field (`characters`, `lighting`, `action`, `movement`, `dialogue`, `sfx`, `music`, scene `title`/`notes`, `name`) in the language the user is conversing in, and never translate them later (translating rewrites the user's own words in their own document).

English happens at the compositor, not in the JSON: at render time the visor calls a small LLM (`storyboard_image_prompt`) that translates the editorial fields into the final English image prompt. The agent NEVER writes English into the storyboard JSON (unless the user speaks English).

## Image generation is automatic

Every shot card auto-renders via `generate_image`: the visor composes `<pencil preamble>` plus the compositor's English prompt. The MD5 of editorial fields + aspect + model + seed is the cache filename, so changing any editorial field re-renders that one shot automatically. NEVER call `generate_image` yourself for storyboard shots; keep the JSON correct and the visor renders.

## Legacy schema fallback (read-only)

The visor accepts older shapes when READING so old JSONs do not blank out: v1 (`shotType`, `camera`, `visual`, `notes`, `audio`), v2 (`cameraShot`, `cameraAngle`, `cameraMovement`, `screenDirection`, `foreground`, `midground`, `background`, `continuityNotes`, `styleNotes`), v3 (`purpose`, `composition`, `cameraMove`, `subject`, `audioDirection`), v4.0 (per-shot `lighting`, moved to root in v4.1), v4.1/v5 (per-shot `imagePrompt`, dropped in v6). All surface inside the v6 slots automatically. When WRITING, always emit v6; never author older shapes in new storyboards.
