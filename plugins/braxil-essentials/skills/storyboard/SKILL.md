---
name: storyboard
description: >
  Author and edit the storyboard: the native in-app artefact saved as JSON (~/.koi/storyboards/<id>.json) that the GUI visor renders as editable pencil-sketch shot cards. This is the DEFAULT meaning of "a storyboard": the editable SOURCE artefact for video pre-production. SCOPE: this skill (and being the first step of a video) applies ONLY to a video that has MULTIPLE shots / an actual story or script. Do NOT author a storyboard for animating a single image, or for a single short one-shot clip, those skip the storyboard entirely and go straight to video generation (image-to-video / `generate_video`). If it is unclear whether the user wants a multi-shot story/video or just a single short shot / to animate one image, ASK before authoring, do not assume the storyboard pipeline. Covers the file convention, the v6 schema, character-continuity mechanics, the pencil-sketch style default, and the creation + modification flows. It does NOT decide cinematography: framing / shot type / angle / movement, pacing, durations and shot counts are delegated to its references and the `screenwriting` skill, never set by this skill itself. ALWAYS author it through this skill, NEVER substitute a markdown table, a text shot list, or a hand-written JSON; a table is NOT a storyboard. The bare word "storyboard" (in ANY language) defaults to THIS skill, and so do "interactive storyboard" / "storyboard interactivo" if the user happens to say them. Trigger on any of these (and their synonyms / translations): "storyboard", "storyboard interactivo", "hazme/créame un storyboard", "guion gráfico" / "guión gráfico", "escaleta", "desglose de planos", "storyboard editable", "shot list", "scene plan", "animatic", "beat sheet", "video pre-production / pre-producción", as long as the user does NOT explicitly ask for a rendered IMAGE or sheet. A bare "guión" / "script" with no clear multi-shot-video intent is AMBIGUOUS (it may mean a plain text screenplay, a podcast script, etc.): ASK rather than assume this skill. Do NOT use this skill to GENERATE images or video: once the JSON exists, its sibling `storyboard-to-keyframes` renders it into 4K sheet images, and `keyframes-to-video` turns those into the film.
---

## The artefact

App-owned JSON the GUI visor watches and renders as editable pencil-sketch shot cards.

- **Path (MANDATORY):** `~/.koi/storyboards/<id>.json`. `<id>` = stable kebab slug (`sb-<unix-ms>` or human like `mafiosos-restaurante`); the `id` INSIDE the JSON == filename. NEVER write anywhere else (cwd/Desktop/project = invisible; visor only watches that folder).
- Always write via the storyboard tools, NEVER `write_file`/`edit_file`: **`update_storyboard`** for content edits (diff-style: only the changed fields, only the affected panels re-render), **`save_storyboard`** for create/restructure (derives `version`/`createdAt`/`updatedAt`/path, validates, escapes JSON).

## Schema (v6) skeleton

Full semantics/examples/gotchas: [references/authoring-guide.md](references/authoring-guide.md): load before authoring or editing content.

```jsonc
{
  "id": "sb-… | kebab-slug",        // == filename
  "name": "Human-readable title",
  // ⛔ NO "aspect" / format field. Aspect ratio is NOT a storyboard property —
  // it belongs to the VIDEO, and ONE storyboard can be turned into videos in
  // MANY formats (16:9, 9:16, 1:1…). Never author it here, never ask the user
  // about format at storyboard time. The panels render on a neutral reading
  // surface; the final video format/resolution is chosen ONLY when the video
  // is generated (see keyframes-to-video / video-generator).
  "seed": 7382913,                  // int, pick ONCE: same seed = consistent look
  "characters": [                   // recurring-cast roster: ARRAY of { name, description?, characterId? }
    { "name": "HERO_A", "description": "tall slim faceless woman, long dark coat (no face)" },
    { "name": "SIDEKICK", "description": "short stocky man, red cap", "characterId": "sidekick-bob" } // characterId links a saved ~/.koi/characters/<id>.json card
  ], // name = SHORT_UPPERCASE label reused verbatim in action/dialogue; visor renders each as a clickable row. (Legacy free-text string still accepted, but EMIT THE ARRAY.)
  "lighting": "Luz dura de mediodía, sombras profundas.",  // ONE design for whole piece
  "stylePrompt": "",                // EMPTY unless user literally asked for a style
  "synopsis": "Premise + physical logic the renders must respect.",
  "continuity": [ "The button stays high, out of reach until he climbs." ], // LOCK: story-wide invariants+negatives, injected verbatim into every shot prompt
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
      "continuity": { "characters": "…", "objects": "…", "place": "…" }, // this panel's continuity-table row
      "dialogue": "HERO_A: \"…\"",
      "sfx": "…", "music": "…",     // audio metadata (not in image prompt)
      "references": []              // shot-scope anchors (omit if empty)
    }]
  }]
}
```

## Hard rules (each = a reported bug)

1. **ALWAYS invoke `screenwriting` FIRST**, every time the user writes/modifies guion/story/storyboard content (Skill tool `braxil-essentials:screenwriting`, or `activate_skill screenwriting`). A storyboard IS the script made visible: story, `action`, `dialogue`, timing/rhythm, add/remove/reorder shots, "mejora el guion", "arregla los tiempos", "hazlo profesional" = screenwriting work. Apply its craft, then express in JSON. Its ref .md files mirrored below (reading complements, does NOT substitute invoking). ONLY exception: purely mechanical edits, zero story content (`references` paths, renaming, fixing a rejected field, re-numbering).
2. **`action` = zero ambiguity.** Models render literally and invent whatever is open. Every object/count/target/position → exactly ONE thing: exact count ("una única moneda"), specific target ("el botón de abajo, de una fila de 6"), concrete identifiers ("la maleta ROJA a su izquierda", never "su maleta"), the HOW (grip/finger/posture), ONE physical action per shot. No exempt shots (product/logo/establishing need the same precision).
3. **Carry-forward state (#1 continuity rule).** Once a shot establishes a NON-default state (standing on stacked cans, holding something, machine open, prop moved/broken), EVERY later shot where it still holds must restate it in `action`; the renderer silently resets otherwise. Splitting into micro-cuts is FREE; resetting state across a cut is broken. Back with per-shot `continuity` {characters, objects, place} (fill `place` on EVERY shot of a strong-setting scene so close-ups stay anchored; fill characters/objects wherever non-default state holds) + storyboard-level `continuity` LOCK (invariants + negatives).
4. **`stylePrompt` = `""`** unless the user's literal words request a style ("en estilo anime", "make it Pixar", "como Sin City", a ref image + "make it look like this"). Topic NEVER implies style (ninjas/mafiosos/dragones stay pencil sketch). Don't announce a style choice for plain requests.
5. **Carry the user's reference photos into `references`, MANDATORY.** Any character/subject/product photo the user gave (path in `## ATTACHED MEDIA` / `**Attached files:**`, image in `# WORKING AREA`, a named `@handle`) goes into `references` NOW (recurring/global look → storyboard level; some-shots-only → those shots' level); describing it in `characters` is NOT enough. IMAGES/`@handles` only. When a photo DEFINES/RECTIFIES a character, `read_file` it and describe what you SEE. Full detail (3-level cascade, video-crashes-render, describe-what-you-see, photo-overrides-sketch): see authoring-guide.md.
6. **User's language everywhere.** All editorial fields (`action`, `dialogue`, `characters`, `lighting`, names, notes...) in the conversing language; never translate. English happens at the compositor at render time, never in the JSON.
7. **Duration: the storyboard is the single timing authority (mechanic only).** Summed `duration`s ARE the runtime: re-read and re-sum before reporting/rendering; never silently retime to re-hit an old target. Only an explicit current hard-target ("que dure exactamente 30s") authorises retiming, and say what you retimed. This skill sets NO durations, shot counts or per-shot pacing itself — how to size a first draft and how long each beat runs is SCREENWRITING craft: get it from `screenwriting` + authoring-guide.md, never decide it here.
8. **Character labels.** Define each recurring character ONCE in roster as `SHORT_UPPERCASE_A` (`HERO_A`, `DOG_A`) with silhouette-based desc, then reuse the label EXACTLY in every `action`/`dialogue`; never drift to "the hero"/"she". Compositor inflates labels at render time.
9. **`noCutBefore` glues panels into ONE take/clip** (`true` on every panel after the first; NEVER on a scene's first shot — scene boundary = cut). That is the field mechanic; WHEN to break a camera move into beat-by-beat panels is cinematography craft — see authoring-guide.md (`noCutBefore`) and `../screenwriting/references/visual-grammar.md`.
10. **Storyboard → sheets consistency is ABSOLUTE: PROPAGATE BY DEFAULT.** If rendered keyframe sheets exist (creations with `metadata.sourceStoryboard` → this), any modification makes affected cuadros STALE and you MUST update the visual side IN THE SAME TURN, unasked: content-level shot changes → `storyboard-to-keyframes` fixing flow on affected cuadros; shots added/removed/reordered or scene-level → re-render affected sheet(s) with a NEW `sheetSetId`. Skip only if the user EXPLICITLY defers ("luego lo regeneramos"), then state which cuadros/sheets are out of date. Reverse direction (in `storyboard-to-keyframes`): story-affecting changes against sheets land HERE first, then propagate back.
11. **Image generation is automatic.** The visor renders every card (pencil preamble + compositor prompt; edits re-render via cache hash). NEVER call `generate_image` for storyboard shots.

## Shot / angle / movement vocabulary → NOT here

This skill does not carry framing/angle/movement craft. The valid `shot` presets are validated by `save_storyboard` (invalid → the error lists the current set; never hardcode or guess them). `movement` is free text. Choosing WHICH framing, angle or camera move — the shot-size ladder, what each angle conveys, the 180-degree rule, eyeline/screen-direction matching, coverage — is cinematography and lives in the craft references, not here:

- `references/authoring-guide.md` — `shot`/`movement` field semantics (how to fill them validly).
- `../screenwriting/references/visual-grammar.md` — full shot ladder, angles, movements, composition, 180-degree diagrams, coverage.

## Reference files (load on demand)

This skill's guides:

| File | When |
|---|---|
| [references/authoring-guide.md](references/authoring-guide.md) | Writing/editing ANY content: full field semantics, `action` precision bar + examples, continuity fields, `noCutBefore`, references cascade, stylePrompt anti-examples, duration detail, language rules, legacy schemas. |
| [references/from-video.md](references/from-video.md) | Storyboarding an EXISTING video (1:1 transcription). |

`screenwriting` craft library (siblings of this folder), read through a storyboard lens:

| File | Load while storyboarding when |
|---|---|
| `.../story-structure.md` | Inventing/restructuring: give even a 20s spot five-act shape (want+obstacle, inciting incident, MIDPOINT at center, worst point, climax mirroring opening). Shot progression IS the act structure; check vs its checklist. |
| `.../scene-craft.md` | What each scene/shot SHOWS: every shot a unit of change (changes nothing → cut it), enter late/leave early, end on the turning point (cut = cliffhanger), show don't tell (juxtapose, don't explain). |
| `.../character-dialogue-subtext.md` | Writing `dialogue` + character-driven `action`: subtext over statement, distinct voices per label, exposition hidden in conflict, facade vs flaw readable in behaviour. |
| `.../visual-grammar.md` | `shot`/`movement` beyond the tables: shot-size ladder, composition (lead room, thirds), eyeline/POV grammar, motivated moves, 180-degree diagrams, pan-speed/judder limits, coverage so panels cut together. |
| `.../production-craft.md` | Planning like a shoot: coverage (establishing + cutaways + reactions, not only the talker), one page = one minute, blocking as choreography, shots that assemble multiple ways. |
| `.../structure-worked-examples.md` | Calibrating a longer/trickier piece vs real act maps (Raiders, Hamlet, The Godfather...) or a user talking Save the Cat / Field / Vogler. |
| `.../tv-and-series-structure.md` | Episodic (series of spots, webserie, chaptered): story engines, serial midpoints, cliffhanger placement across episodes. |

(paths above = `../screenwriting/references/`)

## Create vs MODIFY: decide FIRST, every time

**DEFAULT = MODIFY the storyboard you're already working on. Create NEW only when the user EXPLICITLY asks for a new/separate/another storyboard.** (Wrong = duplicate tab + lost work, reported bug.)

The working storyboard is set by the CONVERSATION, not by focused tab: whichever you most recently created/saved/`read_file`'d in THIS conversation; track its `id`. Every follow-up ("rectifica", "añade un plano", a new reference photo, "itera") targets THAT storyboard even if the user focused another doc. Fallback ONLY when no storyboard is established in the conversation: the active document in `# WORKING AREA`. When in doubt and a storyboard is open → MODIFY. Never default to create.

## Flow: creating a NEW storyboard

1. **Invoke `screenwriting` first** (rule 1); develop the story (concrete want+obstacle, turning point at center, last shots answer the first, every shot a unit of change). Even a 20s ad reads better as a tiny five-act story.
2. **Pick a UNIQUE id** (descriptive kebab; suffix `-v2`/date if collision-prone). Reusing an id = "new storyboard shows old shots" bug; on collision `save_storyboard` auto-renames and returns the new id, use it after.
3. **Build as a STRUCTURED OBJECT** (a tool argument, never hand-serialized JSON): id, name (NO aspect/format — it is NOT a storyboard property; see the schema note), `synopsis` (almost always), `continuity` LOCK (any story with physical logic), characters roster, lighting, stylePrompt `""`, scenes/shots with all editorial fields in user's language, per-shot `continuity` rows, durations. Carry reference photos into `references` (rule 5). Do NOT set `version`/`createdAt`/`updatedAt` or compute path.
4. **`save_storyboard`** with the object. On `success: false`, read `error`, fix that field, retry.
5. **Verify**: success true, AND if a reference photo was given, at least one `references` entry carries it; if missing, add and save again BEFORE moving on.
6. **`show_result`** with `resourceType: 'file'`, the returned absolute path, and the name (opens the visor tab). Tell the user it's ready (name + shot count) and ask for tweaks.

**From an EXISTING video** (not creative: 1:1 transcription): `read_file` the video FIRST (watch natively; never ffprobe/extract_frame/transcribe_audio), one shot per cut with real timecodes, verbatim dialogue; verify durations sum EXACTLY to `durationSec` and shot count == cut count before saving. Full flow: [references/from-video.md](references/from-video.md).

## Flow: modifying an EXISTING storyboard

0. **Invoke `screenwriting` first for ANY content change** (rule 1); skip only for purely mechanical edits.
1. **`read_file` the working storyboard first** (conversation-established; active tab only as fallback). It may have been edited inline in the visor, always re-read. Parse it; **keep its `id` EXACTLY** (same id = in-place, new id = duplicate).
2. **CONTENT edits (changing field values) → `update_storyboard`, ALWAYS.** Send ONLY the deltas, addressed by scene/shot id: `{ id, set?: {…root…}, scenes?: [{id, set}], shots?: [{id, set}] }`. Never re-send unchanged fields "for safety" — every field that differs from disk counts as an edit and re-renders that panel's sketch (a root field re-renders ALL panels). The result's `affectedPanels` lists exactly which sketches will redraw: tell the user.
3. **STRUCTURAL edits (add/remove/reorder scenes or shots, renumber, change ids) → `save_storyboard`** with the full mutated object (preserves `createdAt`, bumps `updatedAt`). Copy every field you are not changing VERBATIM from the read — re-wording an untouched `shot`/`action` re-renders that panel for nothing. Verify the result's `editorialChanges` matches your intent; if it lists fields you didn't mean to touch, re-save restoring them verbatim.
4. Keep `number` sequential across ALL scenes after reorder/insert/delete (tool rejects otherwise).
5. Verify `success: true`; on false, fix and retry. Don't tell the user it's done until it is. Visor picks up disk changes; no `show_result` for updates.
6. **Propagate to visual sheets (rule 10):** if rendered sheets exist, update affected cuadros (or re-render affected sheets) this same turn; never leave the panel grafico contradicting the saved storyboard.

## Self-check before EVERY save (hard gate)

Read your payload back; if any check fails, fix BEFORE saving:

1. `synopsis` filled (except a bare unconnected shot list).
2. `continuity` LOCK filled for any story with physical/spatial logic (invariants that, if broken, ruin the story).
3. Continuity table reads clean top-to-bottom: every panel's `continuity` row filled (`place` on EVERY shot of a scene; characters/objects wherever non-default state holds) and consecutive rows physically consistent (nothing broken in one row yet whole in the next; nobody on the floor then on the object without a climbing panel; no panel in a place the script never moved to). Contradiction = the script is wrong: fix `action`/`continuity`, don't ship.
4. EVERY `action` passes the zero-ambiguity bar: could a stranger stage this exactly ONE way? Vague/atmospheric lines ("plano del producto", "el chico reacciona", "X girando sobre fondo negro") FAIL, rewrite. No exempt shots.
5. Carry-forward state restated in every shot where a non-default state still holds (rule 3).
6. `stylePrompt` is `""` unless the user's message literally requested a style (rule 4).

## Don't

- Call `generate_image` for shots (rule 11).
- Write storyboard JSONs outside `~/.koi/storyboards/` (and only via `update_storyboard`/`save_storyboard`).
- Fabricate fields not in the schema (`mediaRef`, `cacheKey`...).
- Write English into editorial fields; translate the user's text.
- Put `@handles` in `action`/`characters` text unless the user confirmed they exist in the gallery (visor strips them at compose time).
- Invent a `stylePrompt`; empty string is the default.
- Substitute a markdown table, text shot list, or hand-written JSON for the artefact: a table is NOT a storyboard.
