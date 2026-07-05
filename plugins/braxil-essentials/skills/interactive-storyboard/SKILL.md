---
name: interactive-storyboard
description: >
  Author and edit the INTERACTIVE storyboard — the native in-app artefact saved as JSON (~/.koi/storyboards/<id>.json) that the GUI visor renders as editable pencil-sketch shot cards. This is the DEFAULT meaning of "a storyboard": the editable SOURCE artefact for video pre-production. SCOPE — this skill (and being the first step of a video) applies ONLY to a video that has MULTIPLE shots / an actual story or script. Do NOT author a storyboard for animating a single image, or for a single short one-shot clip — those skip the storyboard entirely and go straight to video generation (image-to-video / `generate_video`). If it is unclear whether the user wants a multi-shot story/video or just a single short shot / to animate one image, ASK before authoring — do not assume the storyboard pipeline. Covers the file convention, the v6 schema, character continuity, lighting design, shot vocabulary (shot type / angle / movement), the pencil-sketch style enforcement, and the creation + modification flows. ALWAYS author it through this skill — NEVER substitute a markdown table, a text shot list, or a hand-written JSON; a table is NOT a storyboard. The user will RARELY say the literal words "interactive storyboard" — the bare word "storyboard" (in ANY language) defaults to THIS skill. Trigger on any of these (and their synonyms / translations): "storyboard", "storyboard interactivo", "hazme/créame un storyboard", "guion gráfico" / "guión gráfico", "escaleta", "desglose de planos", "storyboard editable", "shot list", "scene plan", "animatic", "beat sheet", "video pre-production / pre-producción" — as long as the user does NOT explicitly ask for a rendered IMAGE or sheet. A bare "guión" / "script" with no clear multi-shot-video intent is AMBIGUOUS (it may mean a plain text screenplay, a podcast script, etc.) — ASK rather than assume this skill. Do NOT use this skill to GENERATE images or video: once the JSON exists, its sibling `visual-panels` renders it into 4K sheet images, and `visual-panels-to-video` turns those into the film.
---

## The artefact

Storyboards are a first-class, app-owned artefact: JSON documents the GUI visor watches and renders as editable pencil-sketch shot cards.

**Canonical path (MANDATORY):** `~/.koi/storyboards/<id>.json`, where `<id>` is a stable kebab-case slug (`sb-<unix-ms>` or human-readable like `mafiosos-restaurante`) and the `id` INSIDE the JSON equals the filename. NEVER create the file anywhere else (not cwd, not Desktop, not a project dir): the visor only watches that folder; anything outside it is invisible to the user.

Always write/update through **`save_storyboard`** (it derives `version`, `createdAt`, `updatedAt` and the path, validates fields, and handles JSON escaping). NEVER `write_file`/`edit_file` a storyboard.

## Schema (v6) skeleton

Full field semantics, examples and gotchas: [references/authoring-guide.md](references/authoring-guide.md). Load it whenever you are about to author or edit content.

```jsonc
{
  "id": "sb-… | kebab-slug",        // matches the filename
  "name": "Human-readable title",
  "aspect": "16:9",                 // "1:1" "16:9" "9:16" "4:3" "3:4" "3:2" "2:3" "21:9"
  "seed": 7382913,                  // int, pick ONCE: same seed = consistent look
  "characters": "- HERO_A: tall slim faceless woman, long dark coat...",
                                    // roster: LABEL + silhouette description (no faces)
  "lighting": "Luz dura de mediodía, sombras profundas.",
                                    // ONE lighting design for the whole piece
  "stylePrompt": "",                // EMPTY unless the user literally asked for a style
  "synopsis": "Premise + physical logic the renders must respect.",
  "continuity": [                   // LOCK: story-wide invariants + negatives,
    "The button stays high, out of reach until he climbs."
  ],                                //   injected verbatim into every shot prompt
  "references": ["@hero", "/abs/path/img.png"],   // IMAGES/@handles only, never video
  "scenes": [{
    "id": "sc1", "title": "…", "location": "", "notes": "",
    "synopsis": "",                 // optional per-scene premise
    "references": [],               // scene-scope anchors (omit if empty)
    "shots": [{
      "id": "sh1",
      "number": 1,                  // 1-based, sequential across ALL scenes
      "noCutBefore": false,         // true = continuation of previous shot (one take)
      "duration": 3.0,              // seconds, number > 0
      "shot": "Close-up, low angle",// EXACTLY one app preset, verbatim (validated)
      "movement": "Dolly in",       // free text
      "action": "…",                // user's language, ZERO ambiguity (see below)
      "continuity": { "characters": "…", "objects": "…", "place": "…" },
                                    // this panel's continuity-table row
      "dialogue": "HERO_A: \"…\"",
      "sfx": "…", "music": "…",     // audio metadata (not in image prompt)
      "references": []              // shot-scope anchors (omit if empty)
    }]
  }]
}
```

## The hard rules (each one exists because a user reported the bug)

1. **ALWAYS invoke the `screenwriting` skill alongside this one.** Not sometimes: EVERY time the user asks to write or modify a guion, a story, or a storyboard's content, the `screenwriting` skill gets invoked FIRST (Skill tool with `braxil-essentials:screenwriting`, or `activate_skill screenwriting`). A storyboard IS the script made visible, so story, `action` lines, `dialogue`, timing/rhythm, adding/removing/reordering shots, "mejora el guion", "arregla los tiempos", "hazlo profesional" are all screenwriting work: apply ITS craft, then come back here to express the result in the JSON. Its full craft library (all its reference .md files) is also mirrored in the table below with storyboard-focused guidance; reading those files complements but does NOT substitute invoking the skill. ONLY exception: purely mechanical edits with zero story content (`aspect`, `references` paths, renaming, fixing a rejected field, re-numbering).

2. **`action` = zero ambiguity.** Image/video models render your words literally and invent whatever you leave open. Every object, count, target and position must resolve to exactly ONE thing: exact count ("una única moneda"), the specific target ("el botón de abajo, de una fila de 6"), concrete identifiers ("la maleta ROJA a su izquierda", never "su maleta"), the HOW (grip, finger, posture), ONE physical action per shot. No exempt shots: product/logo/establishing shots need the same precision. Full bar + worked examples in the authoring guide.

3. **Carry-forward state, the #1 continuity rule.** Once a shot establishes a NON-default state (standing on the stacked cans, holding something, a machine open, a prop moved/broken), EVERY later shot where it still holds must restate it explicitly in its `action`; the renderer silently resets to default otherwise. Splitting into many micro-cuts is FREE; resetting state across a cut is broken. Back it with the two structured fields: per-shot `continuity` { characters, objects, place } (fill `place` on EVERY shot of a scene with a strong setting so close-ups stay anchored; fill characters/objects wherever a non-default state holds) and the storyboard-level `continuity` LOCK (invariants + negatives the renderer must never violate).

4. **`stylePrompt` stays `""` unless the user's literal words request a style** ("en estilo anime", "make it Pixar", "como Sin City", a reference image with "make it look like this"). Topic NEVER implies style: ninjas, mafiosos, dragones all stay pencil sketch. Do not announce a style choice in chat for plain requests. Reported multiple times; the anti-example table is in the authoring guide.

5. **Carry the user's reference photos into `references`, MANDATORY.** Any character/subject/product photo the user gave (path in `## ATTACHED MEDIA` / `**Attached files:**`, image in `# WORKING AREA`, a named `@handle`) goes into `references` NOW: recurring character or global look at storyboard level; subject in only some shots at those shots' level. Describing the photo in `characters` is NOT enough: without the path the renderer never sees the face (reported: "le di las fotos y no ha adjuntado ninguna"). IMAGES and `@handles` only: a video/audio path in `references` crashes the sheet render. And when a photo DEFINES or RECTIFIES a character: `read_file` it and describe what you SEE; the new photo overrides any previous description or old sketches.

6. **User's language everywhere.** All editorial fields (`action`, `dialogue`, `characters`, `lighting`, names, notes...) in the language the user is conversing in; never translate them. English happens at the compositor at render time, never in the JSON.

7. **Duration: the storyboard is the single timing authority.** The summed `duration`s ARE the runtime. A duration the user named upfront only sizes the FIRST draft (60s = 8-12 shots of 4-8s). After that, the storyboard's current total wins: re-read and re-sum before reporting or rendering; never silently retime to re-hit an old target. Only an explicit, current hard-target instruction ("que dure exactamente 30s") authorises retiming, and say what you retimed.

8. **Character labels.** Define every recurring character ONCE in the roster as `SHORT_UPPERCASE_A` (`HERO_A`, `DOG_A`) with a silhouette-based description, then reuse the label EXACTLY in every `action`/`dialogue`; never drift to "the hero"/"she". The compositor inflates labels at render time.

9. **Camera-movement shots: split into a glued take.** A moving shot longer than 1-2s should be authored as 2-4 panels describing the move beat by beat, with `"noCutBefore": true` on every panel after the first (they render as ONE clip). Never on the first shot of a scene. Details + example in the authoring guide.

10. **Storyboard -> sheets consistency is ABSOLUTE: PROPAGATE BY DEFAULT.** If this storyboard already has rendered visual panel sheets (creations with `metadata.sourceStoryboard` pointing at it), any modification here makes the affected cuadros STALE, and you MUST update the visual side IN THE SAME TURN, without being asked: content-level changes to specific shots -> the `visual-panels` fixing flow on the affected cuadros; shots added/removed/reordered or scene-level changes -> re-render the affected sheet(s) with a NEW `sheetSetId`. Only skip propagation when the user EXPLICITLY defers it ("luego lo regeneramos"), and then state exactly which cuadros/sheets are out of date. The reverse direction also holds and lives in the `visual-panels` skill: story-affecting changes requested against the sheets must land HERE first, then propagate back to the sheets.

11. **Image generation is automatic.** The visor renders every card itself (pencil preamble + compositor prompt; edits re-render via cache hash). NEVER call `generate_image` for storyboard shots.

## Cinematic vocabulary

Preferred values for `shot` (combine with an angle, e.g. "CU low angle") and `movement`. Deeper craft (composition, eyelines, 180-degree rule, coverage): `../screenwriting/references/visual-grammar.md`.

| Shot | Framing | Use for |
|------|---------|---------|
| ECU | Eyes / a detail | Intense emotion, reveals |
| CU | Face fills frame | Emotion, reaction, dialogue |
| MCU | Head and shoulders | Conversations |
| MS | Waist up | Dialogue, action |
| MLS | Knees up | Walking, casual interaction |
| LS | Full body | Character in environment |
| WS | Environment dominant | Establishing, scale |
| EWS | Vast landscape | Epic scope, isolation |

| Angle | Effect |
|-------|--------|
| Eye Level | Neutral default |
| High Angle | Subject small, vulnerable |
| Low Angle | Subject powerful, threatening |
| Bird's Eye | God-like overview, geography |
| Worm's Eye | Extreme power, awe |
| Dutch Angle | Unease, tension, madness |
| Over-the-Shoulder | Dialogue framing |
| POV / First-Person | Through the subject's eyes (hands visible, subject never shown); combines with any visual style |

| Movement | Emotion |
|----------|---------|
| Static | Stability, observation, tension |
| Pan / Tilt | Scanning, revealing (horizontal / vertical) |
| Dolly | Intimacy (in), distance (out) |
| Truck | Following alongside |
| Crane/Jib | Grand reveals, transitions |
| Zoom | Focus shift, emphasis (lens only) |
| Steadicam | Immersive following |
| Handheld | Urgency, chaos, documentary |

Classic continuity craft while choosing shots: keep all cameras on one side of the action axis (180-degree rule; cross only via a neutral shot or a visible move), match on action across cuts, eyeline matches (look, then what they see), consistent screen direction. Full treatment with diagrams in `../screenwriting/references/visual-grammar.md`.

## Reference files (load on demand)

This skill's own guides:

| File | When |
|---|---|
| [references/authoring-guide.md](references/authoring-guide.md) | Writing/editing ANY content: full field semantics, `action` precision bar + examples, continuity fields, `noCutBefore`, references cascade, stylePrompt anti-examples, duration detail, language rules, legacy schemas. |
| [references/from-video.md](references/from-video.md) | Storyboarding an EXISTING video (1:1 transcription flow). |

The `screenwriting` craft library (same files that skill uses; siblings of this skill's folder), read through a storyboard lens:

| File | Load while storyboarding when |
|---|---|
| `../screenwriting/references/story-structure.md` | Inventing or restructuring the piece's story: give even a 20-second spot the five-act shape (want + obstacle, inciting incident, MIDPOINT at the center, worst point, climax mirroring the opening). The shot progression IS the act structure; check the board against its authoring checklist. |
| `../screenwriting/references/scene-craft.md` | Deciding what each scene/shot must SHOW: every shot is a unit of change (if a panel changes nothing, cut it), enter late / leave early when picking each panel's moment, end scenes on the turning point so the cut itself is the cliffhanger, show don't tell (two plus two: let panels juxtapose instead of explain). |
| `../screenwriting/references/character-dialogue-subtext.md` | Writing `dialogue` lines and character-driven `action`: subtext over statement, distinct voices per label, exposition hidden in conflict, facade vs flaw readable in behaviour (what the character DOES in frame). |
| `../screenwriting/references/visual-grammar.md` | Choosing `shot`/`movement` beyond the tables above: shot-size ladder, composition (lead room, thirds), eyeline and POV grammar, motivated camera moves, 180-degree rule with diagrams, pan-speed/judder limits for fast action, coverage logic so consecutive panels cut together. |
| `../screenwriting/references/production-craft.md` | Planning the board like a shoot: coverage thinking (establishing + cutaways + reactions, not only the talker), one page equals one minute when sizing durations, blocking as choreography, shots that can assemble more than one way. |
| `../screenwriting/references/structure-worked-examples.md` | Calibrating a longer or trickier piece against real act maps (Raiders, Hamlet, The Godfather...) or translating a user who talks in Save the Cat / Field / Vogler vocabulary. |
| `../screenwriting/references/tv-and-series-structure.md` | Episodic content: a series of spots, a webserie, chaptered storyboards: story engines, serial midpoints, cliffhanger placement across episodes. |

## Create vs MODIFY: decide FIRST, every time

**DEFAULT = MODIFY the storyboard you are already working on. Create a NEW one ONLY when the user EXPLICITLY asks for a new/separate/another storyboard.** Getting this wrong spawns a duplicate tab and throws away the user's work (reported bug).

The working storyboard is set by the CONVERSATION, not by which tab is focused: it is whichever you most recently created, saved or `read_file`'d in THIS conversation; track its `id`. Every follow-up ("rectifica", "añade un plano", a new reference photo, "itera") targets THAT storyboard even if the user focused another document. Fallback ONLY when the conversation has no established storyboard: the active document in `# WORKING AREA`. When in doubt and a storyboard is open, it is a MODIFY. Never default to create.

## Flow: creating a NEW storyboard

1. **Invoke `screenwriting` first** (rule 1) and develop the story with its workflow: concrete want + obstacle, a turning point at the center, last shots answering the first, every shot a unit of change. Even a 20-second ad reads better as a tiny five-act story than as a list of pretty shots.
2. **Pick a UNIQUE id** (descriptive kebab-case; suffix `-v2`/date if the slug may collide). Reusing an existing id is what causes the "new storyboard shows old shots" bug; on collision `save_storyboard` auto-renames and returns the new id, use it afterwards.
3. **Build the storyboard as a STRUCTURED OBJECT** (a tool argument, never hand-serialized JSON): id, name, aspect (default "16:9"), `synopsis` (almost always), `continuity` LOCK (any story with physical logic), characters roster, lighting, stylePrompt `""`, scenes/shots with all editorial fields in the user's language, per-shot `continuity` rows, durations. Carry the user's reference photos into `references` (rule 5). Do NOT set `version`/`createdAt`/`updatedAt` or compute the path.
4. **Call `save_storyboard`** with the object. On `success: false`, read `error`, fix the exact field, retry.
5. **Verify**: success true, AND if the user gave any reference photo, at least one `references` entry carries it; if missing, add it and save again BEFORE moving on.
6. **`show_result`** with `resourceType: 'file'`, the returned absolute path, and the storyboard name (opens the visor tab). Tell the user it is ready (name + shot count) and ask for tweaks.

**From an EXISTING video**: not creative work, a 1:1 transcription. `read_file` the video FIRST (watch it natively; never ffprobe/extract_frame/transcribe_audio), one shot per cut with real timecodes, verbatim dialogue, and verify before saving that the durations sum EXACTLY to the video's `durationSec` and the shot count equals the cut count. Full flow: [references/from-video.md](references/from-video.md).

## Flow: modifying an EXISTING storyboard

0. **Invoke `screenwriting` first for ANY content change** (rule 1); skip only for purely mechanical edits.
1. **`read_file` the working storyboard first** (the conversation-established one; active tab only as fallback). It may have been edited inline in the visor, so always re-read. Parse it; **keep its `id` EXACTLY as-is**: same id = in-place edit, new id = duplicate.
2. Mutate the object (there is no partial-edit API: `save_storyboard` takes the whole updated object).
3. **`save_storyboard`** with the full object (preserves `createdAt`, bumps `updatedAt`).
4. Keep `number` sequential across ALL scenes after any reorder/insert/delete (the tool rejects otherwise).
5. Verify `success: true`; on false, fix and retry. Do NOT tell the user it is done until it is. The visor picks up changes from disk; no `show_result` needed for updates.
6. **Propagate to the visual sheets (rule 10):** if rendered panel sheets exist for this storyboard, update the affected cuadros (or re-render the affected sheets) in this same turn: never leave the panel grafico contradicting the storyboard you just saved.

## Self-check before EVERY save (hard gate)

Read your own payload back; if any check fails, fix it BEFORE saving:

1. `synopsis` filled (except a bare unconnected shot list).
2. `continuity` LOCK filled for any story with physical/spatial logic (the invariants that, if broken, ruin the story).
3. The continuity table reads clean top-to-bottom: every panel's `continuity` row filled (`place` on EVERY shot of a scene; characters/objects wherever non-default state holds) and consecutive rows physically consistent: nothing broken in one row yet whole in the next, nobody on the floor in one row yet on the object in the next without a climbing panel, no panel in a place the script never moved to. If two rows contradict, the script is wrong: fix `action`/`continuity`, do not ship.
4. EVERY `action` passes the zero-ambiguity bar: could a stranger stage this exactly ONE way? Vague or atmospheric lines ("plano del producto", "el chico reacciona", "X girando sobre fondo negro") FAIL and must be rewritten. No exempt shots.
5. Carry-forward state restated in every shot where a non-default state still holds.
6. `stylePrompt` is `""` unless the user's actual message contains a style request. No exceptions, no "it would look cooler".

## Don't

- Don't call `generate_image` for shots: the visor renders automatically.
- Don't write storyboard JSONs anywhere outside `~/.koi/storyboards/` (and only via `save_storyboard`).
- Don't fabricate fields not in the schema (`mediaRef`, `cacheKey`...).
- Don't write English into editorial fields; don't translate the user's text.
- Don't put `@handles` in `action`/`characters` text unless the user confirmed they exist in the gallery (the visor strips them at compose time).
- Don't invent a `stylePrompt`; empty string is the default.
- Don't substitute a markdown table, text shot list, or hand-written JSON for the artefact: a table is NOT a storyboard.
