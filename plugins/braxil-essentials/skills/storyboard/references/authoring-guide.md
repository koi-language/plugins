# Authoring Guide: fields, precision, style policy

Load when WRITING/EDITING. SKILL.md = schema skeleton, flows, hard gates; here = field semantics, precision bar, stylePrompt policy.

## Field semantics (v7)

- **`seed`**: int, picked ONCE; same seed all shots = consistent chars/palette. Never change on modify unless user asks a full visual reroll.
- **`characters`** (roster): an ARRAY of `{ name, description?, sex?, age?, characterId? }`, one entry per recurring character. **MANDATORY & COMPLETE**: you MUST list EVERY recurring character that appears in the story — read the whole story and enumerate who intervenes; the visor's cast list is EXACTLY this array (it does NOT and MUST NOT guess characters from the shot text, so anything you omit simply won't be there). If you open/edit a storyboard whose `characters` is empty or incomplete, REPAIR it: read the scenes and author the full roster. `name` = the LABEL `SHORT_UPPERCASE`+A/B/C (`HERO_A`), reused EXACTLY in every `action`/`dialogue`, never "she". `description` = silhouette desc (clothing, proportions, accessories, traits), NOT faces. **`sex`** = canonical `female`|`male`|`nonbinary`|`other`, **`age`** = number (years): FILL both whenever the story tells you them — they are STRUCTURED fields that SEED the same fields on a character card created from this member (a description saying "hombre de 55" is NOT enough; set `sex:"male"`, `age:55`). `characterId` (optional) = the id of a saved character card `~/.koi/characters/<id>.json` when this cast member is backed by one, so the visor can open its card from the cast list (the USER assigns cards in the visor; you just author the roster). Compositor (render-time LLM) inflates label→inline English desc; define once, don't restate per shot. The visor renders each entry as a row. A legacy free-text roster STRING is still accepted (old boards, never parsed), but EMIT THE ARRAY on new/edited storyboards.
- **`lighting`** (root): free text, user's language; the DEFAULT design for the whole piece, injected+translated into every shot. v7 also allows a **per-shot `lighting`** that refines/overrides this for one shot (see below) — leave it empty and every shot inherits the root design.
- **`synopsis`** (root, optional per-scene): premise + physical/causal logic renders must never contradict (WHY, what's reachable, who wants what). Injected into EVERY shot. Fill always except a bare shot list. Scene-level adds per-scene logic. MANDATORY from a video (write real premise watched).
- **`continuity`** (root LOCK, string[]): absolute story-wide INVARIANTS + NEGATIVE constraints, injected VERBATIM into every image/video prompt. `synopsis`=WHY; `continuity`=WHAT MUST NOT CHANGE. Spell out negatives ("do NOT lower the button", "cans stay INTACT") to stop renderer making unreachable reachable, resizing, breaking objects. Omit only for a bare shot list.

### Per-shot `continuity` { characters, objects, place }
Continuity-table ROW for that panel, user's language:
- `characters`: who's in frame + exact state (position, pose, wear/hold, expression).
- `objects`: state of every key prop/scenery in frame.
- `place`: WHERE panel physically happens, restated per shot.

Compositor → CURRENT PANEL STATE + SHOT LOCATION → render shows exactly this state in this place (no default-reset, later beat, void, or wrong close-up bg). Columns top-to-bottom = the continuity table user reviews in visor.
- Fill `place` on EVERY shot of a scene with a strong setting (underwater, car, room) so close-ups stay anchored (fixes "close-up out of scene").
- Fill `characters`/`objects` on any NON-default state (on stacked object, holding/using, machine open, object moved/broken/placed).
- Table CATCHES self-contradiction (N "can crushed" vs N+1 "standing on can" → fix `action`).
- **Declare ABSENCES (closed world):** a transient element that leaves (falling object, exiting char, consumed prop) → shots AFTER exit must state absence in `objects`, not just remaining elements. Renderers infer presence from neighbours; absence holds only if written.

### `dialogue`, `sfx`, `music`
- `dialogue`: lines/VO, quote each speaker to parse; a CUE for facial expression, words NOT rendered on-frame.
- `sfx`/`music`: free-text audio cues, NOT used by image prompt (reserved for future audio); editing them doesn't invalidate rendered image cache.

### Cinematography fields: `shot`, `camera`, `composition`, `lighting` (all FREE TEXT)
The cinematography is designed by `cinematic-video-prompt-engineer`; this skill only writes its decisions into these fields. None is a preset menu.
- `shot`: framing = shot-size + angle, FREE TEXT ("Close-up, low angle", "Extreme wide shot, eye level"). No preset whitelist.
- `camera` (was `movement`): camera work — movement + lens/focal + speed + focus ("Static", "Dolly in, 50mm", "Handheld, slow-motion", "Rack focus to foreground"). A legacy `movement` value is still read as `camera`.
- `composition` (optional): in-frame layout — lead room, thirds, depth/foreground, subject screen-position, screen-direction / 180-axis / eyeline.
- `lighting` (optional, per-shot): the light for THIS shot, refining/overriding the root `lighting`. Empty = inherit the root design.

## Writing `action`: PRECISE

`action` = SOURCE OF TRUTH (sheets + final video render from it). Models render words literally, filling gaps WRONG. Bar: NOTHING doubly interpretable; every object/count/target/position → exactly ONE thing.
- **Exact count, never vague plural** ("insert coins" → "ONE coin, held thumb+index").
- **Name specific target** ("lower button" → "bottom button of a row of 6").
- **Concrete identifier, never relative/interpretable** (else random pick): numbers/colours/positions/named items.
- **The HOW: grip, finger, posture, direction** (avoid contradictions like "stretches up, presses lower button").
- **One physical action per shot**; insert-coin then press-button = two shots.
- **No exempt shots**: product/logo/establishing get SAME precision (state who/what moves the subject + how).
- One tight sentence per shot, user's language, readable in visor.

### Carry-forward state (#1 continuity bug)
A shot setting a NON-default state (on stacked object, holding, machine open, object moved/broken/placed) → EVERY later shot where it still holds MUST restate it in `action`; renderer treats panels semi-independently, silently resets to default. State persists in text until a shot explicitly changes it. Same raccord: same object/hand/machine + lighting + time-of-day, shot-to-shot. Per-shot + root `continuity` = structured backstop.

## Continuous takes: `noCutBefore`

`"noCutBefore": true` glues a shot to previous as ONE take (camera keeps moving, no cut). Consecutive glued shots render as a SINGLE clip; continuation panels share the take's number badge.

WHEN: camera movement (dolly/crane/pan/orbit/push-in/tracking) lasting >1-2s → don't do one vague panel; break into glued sub-takes (START/MID/END framing), each its own panel, flag on all after the first. Renders as one uninterrupted shot but described beat by beat (more controllable than model inventing trajectory).

Rules:
- FIRST panel of glued group: NO flag; 2nd+ carry `"noCutBefore": true`.
- NEVER on a scene's first shot (scene boundary = cut).
- Carry continuity across glued panels as across any shots.
- Take duration = SUM of its panels' durations.
- Static shots rarely split; this is for MOVING shots long enough to read motion.
- Glued panels share one `number`; author START→MID→END framing across them.

## `references`: visual anchors, 3 levels

Optional `references` array on root, each `scenes[]`, each `scenes[].shots[]`. Each entry a STRING: `@mention` handle (gallery asset, `"@hero_pose"`) or absolute path to an IMAGE. Visor → thumbnails/chips; user adds via `@handles` or dropping images.

Scope cascade (specific wins, broader still applies): root → EVERY shot; scene → every shot in scene; shot → that shot. At render, the `storyboard-to-video` skill collects in-scope refs per clip, passes them as `referenceImages` (`@handles`→paths) to lock identity. Omit when empty; never `"references": []`.
- **IMAGES ONLY, never source video.** Video/audio path (`.mp4`/`.mov`/`.mp3`) = BUG, can't decode, crashes sheet render. From a source video, WATCH it with `read_file` (from-video.md); clip is NOT a ref. For a still, save frame as image first, ref that path.
- **Describe the person in the photo; never invent, never keep OLD look.** User gives a photo to DEFINE/RECTIFY a char → `read_file` that exact image BEFORE writing; base `characters` entry on what you SEE (hair or none + colour, facial hair, build, skin, clothing, accessories). Rectifying: new photo OVERRIDES storyboard; don't carry old desc forward, don't describe existing pencil sketches (OLD look being replaced). Read pixels; photo wins.

## `stylePrompt`: empty ALWAYS unless user spelled out a style

Reported violated MORE THAN ONCE. Default = rough pencil animatic (B&W graphite, simplified faceless chars, minimal shading); ONLY correct look unless user EXPLICITLY asked otherwise.
- Default `"stylePrompt": ""`, every time; agent gets NO creative input, user's words decide.
- Topic ≠ style: a topic (ninjas, mafiosos, gatito y perrito, dragón) NEVER implies style; all stay pencil.
- Chat reply must NOT announce a style for plain requests; announcing = the bug.
- Set stylePrompt ONLY on user's LITERAL words ("en estilo anime", "make it Pixar", "en acuarela", "film noir", "al estilo de Ghibli", "como Sin City", or attached image "make it look like this"). Trigger IN THE USER'S MESSAGE, not interpretation; else `""`.

## Duration

- A duration named upfront ("60s ad") = SIZING HINT for FIRST draft only (60s ≈ 8-12 shots of 4-8s).
- Once it exists, CURRENT summed total wins always. User edits shots/sliders on purpose; new total IS runtime. To render/report length, `read_file` + re-sum current durations; never use brief's number or memory. Trimmed to 48s = 48s; never silently re-stretch to target.
- ONLY exception: explicit current hard-target ("keep at 60s no matter what") → retime, tell user which shots changed + why.

## Language rules

JSON is a USER-FACING document, not a prompt. Write EVERY free-text editorial field (`characters`, `lighting`, `action`, `camera`, `composition`, `dialogue`, `sfx`, `music`, scene `title`/`notes`, `name`) in user's language; never translate later (rewrites their words). English at compositor only: render-time visor calls `storyboard_image_prompt` (small LLM) → final English image prompt. Agent NEVER writes English into JSON (unless user speaks English).

## Image generation is automatic

Every shot card auto-renders via `generate_image`: visor composes `<pencil preamble>` + compositor's English prompt. Cache filename = MD5(editorial fields + aspect + model + seed) → changing any editorial field re-renders that one shot. NEVER call `generate_image` yourself for storyboard shots; keep JSON correct, visor renders.

## Legacy schema fallback (read-only)

Visor reads older shapes so old JSONs don't blank: v1 (`shotType`, `camera`, `visual`, `notes`, `audio`); v2 (`cameraShot`, `cameraAngle`, `cameraMovement`, `screenDirection`, `foreground`, `midground`, `background`, `continuityNotes`, `styleNotes`); v3 (`purpose`, `composition`, `cameraMove`, `subject`, `audioDirection`); v4.0 (per-shot `lighting`, →root in v4.1, back per-shot in v7); v4.1/v5 (per-shot `imagePrompt`, dropped v6); v6 (`movement`, → renamed `camera` in v7 — old `movement` still read). All surface in v7 slots. When WRITING always emit v7 (`shot`, `camera`, `composition`, `lighting`, …); never author older shapes.
