---
name: storyboard
description: >
  Author and edit the storyboard: the native in-app artefact saved as JSON (~/.koi/storyboards/<id>.json) that the GUI visor renders as editable pencil-sketch shot cards. This is the DEFAULT meaning of "a storyboard": the editable SOURCE artefact for video pre-production. SCOPE: this skill (and being the first step of a video) applies ONLY to a video that has MULTIPLE shots / an actual story or script. Do NOT author a storyboard for animating a single image, or for a single short one-shot clip, those skip the storyboard entirely and go straight to video generation (image-to-video / `generate_video`). If it is unclear whether the user wants a multi-shot story/video or just a single short shot / to animate one image, ASK before authoring, do not assume the storyboard pipeline. Covers the file convention, the v7 schema, character-continuity mechanics, the pencil-sketch style default, and the creation + modification flows. It does NOT write the story or the scenes: the HIGH-LEVEL story — premise, five-act structure, sequences, the scene map and the characters — is delegated to `screenwriting`; each SCENE is then written ENTIRELY by `cinematic-video-prompt-engineer` (the physical action, the naturalistic dialogue, the planos of framing / camera / composition / light, and where cuts fall). This skill only EXPRESSES their decisions as JSON, never invents them. ALWAYS author it through this skill, NEVER substitute a markdown table, a text shot list, or a hand-written JSON; a table is NOT a storyboard. The bare word "storyboard" (in ANY language) defaults to THIS skill, and so do "interactive storyboard" / "storyboard interactivo" if the user happens to say them. Trigger on any of these (and their synonyms / translations): "storyboard", "storyboard interactivo", "hazme/créame un storyboard", "guion gráfico" / "guión gráfico", "escaleta", "desglose de planos", "storyboard editable", "shot list", "scene plan", "animatic", "beat sheet", "video pre-production / pre-producción", as long as the user does NOT explicitly ask for a rendered IMAGE or sheet. A bare "guión" / "script" with no clear multi-shot-video intent is AMBIGUOUS (it may mean a plain text screenplay, a podcast script, etc.): ASK rather than assume this skill. Do NOT use this skill to GENERATE images or video: once the JSON exists, `storyboard-to-video` groups its shots into clips and generates the videos DIRECTLY (there is NO keyframe/panel-sheet step — the storyboard's shots go straight to video).
---

## The artefact

App-owned JSON the GUI visor watches and renders as editable pencil-sketch shot cards.

- **Path (MANDATORY):** `~/.koi/storyboards/<id>.json`. `<id>` = stable kebab slug (`sb-<unix-ms>` or human like `mafiosos-restaurante`); the `id` INSIDE the JSON == filename. NEVER write anywhere else (cwd/Desktop/project = invisible; visor only watches that folder).
- Always write via the storyboard tools, NEVER `write_file`/`edit_file`: **`update_storyboard`** for content edits (diff-style: only the changed fields, only the affected panels re-render), **`save_storyboard`** for create/restructure (derives `version`/`createdAt`/`updatedAt`/path, validates, escapes JSON).

## Schema (v7) skeleton

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
  // is generated (see storyboard-to-video / video-generator).
  "seed": 7382913,                  // int, pick ONCE: same seed = consistent look
  "characters": [                   // recurring-cast roster: ARRAY of { name, description?, sex?, age?, characterId? }
    { "name": "HERO_A", "description": "tall slim woman, long dark coat", "sex": "female", "age": 30 },
    { "name": "SIDEKICK", "description": "short stocky man, red cap", "sex": "male", "age": 45, "characterId": "sidekick-bob" } // characterId links a saved ~/.koi/characters/<id>.json card
  ], // name = SHORT_UPPERCASE label reused verbatim in action/dialogue; sex = female|male|nonbinary|other, age = number — FILL both when the story tells you (they seed a character card made from this member); visor renders each as a clickable row. (Legacy free-text string still accepted, but EMIT THE ARRAY.)
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
      "shot": "Close-up, low angle",// framing: shot-size + angle. FREE TEXT (no preset)
      "camera": "Dolly in, 50mm, slow push", // camera work: movement + lens/focal + speed + focus (was "movement")
      "composition": "…",           // OPTIONAL: in-frame layout — lead room, thirds, depth, screen position, screen-direction / 180 / eyeline
      "lighting": "…",              // OPTIONAL: light for THIS shot (refines the storyboard-level "lighting")
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

1. **Invoke the two craft skills FIRST — story ARCHITECTURE, then SCENE realization.** A storyboard IS the film pre-visualised, so BEFORE authoring content:
   - **(a) `screenwriting` — the HIGH-LEVEL story** (Skill tool `braxil-essentials:screenwriting`): the premise/theme, the five-act STRUCTURE, the SEQUENCES and the SCENE MAP (which scenes exist, their order, each scene's dramatic FUNCTION / goal / turning point, its location and which characters are in it), the CHARACTERS (bible, arcs, voice) and the story-wide continuity LOCK. It does NOT write the shot-level content.
   - **(b) `cinematic-video-prompt-engineer` — get its NATIVE scene output, THEN transliterate it. TWO steps, never merged:**
     - **(i) DELEGATE the scene to the isolated `scene-writer` agent — ACTUALLY CALL THE TOOL.** 🔴 You MUST really INVOKE the Agent/Task tool with `subagent_type: "braxil-essentials:scene-writer"`. Do NOT describe delegating in prose, do NOT paraphrase a hand-off, do NOT write the scene yourself and claim the agent did it — that is a bug. If you did not emit a real Agent/Task tool call, the scene was NOT written by the isolated agent. The agent runs the `cinematic-video-prompt-engineer` skill in a CLEAN, isolated context and returns the scene's FULL native output (its `镜头` shot-breakdown: framing, camera, composition, light, performance, dialogue, sound, timing). **🔴 HOW you pass the scene: as a NATURAL, user-style prompt — exactly as a user would type it to the cinematic engine, NOT a pre-chewed brief.** Cinematic's input is a plot / scene idea (see its skill: "plot summary, novel excerpt, or scene idea"). So write it in PROSE: what happens in this scene, who is in it and who they are (from the roster), where it takes place, the emotional turn, and any continuity from the prior scene / the story premise + invariants to respect. **Do NOT hand it a shot list, framing, camera moves, a duration, a structure or a rigid field-brief** — those are cinematic's to decide; pre-digesting them is a bug. It decides EVERYTHING by its own skill — duration, shot count, structure, cutting, dialogue. Then take its answer **VERBATIM**, as if we had asked the agent directly as a user. **Fallback (only if the Agent/Task tool genuinely does not exist in this backend):** invoke `cinematic-video-prompt-engineer` INLINE the SAME way — a natural prose scene prompt, its answer used as-is; never re-decide the scene yourself.
     - **(ii) SHOW the user what the agent returned, THEN transliterate.** First **`print` the scene the agent wrote** — its shot breakdown (per shot: framing, action, and the dialogue lines) — so the user sees the actual cinematic output, NOT a one-line summary like "the agent returned the scene". Then **TRANSLITERATE that output into the JSON**: each `镜头`/shot cinematic wrote → one storyboard shot; map its parts to the fields: shot-size+angle → `shot`, camera-move+lens/speed/focus → `camera`, composition → `composition`, light → `lighting`, performance/action → `action`, the spoken line → `dialogue`, sound → `sfx`/`music`, timing → `duration`, continuous-take → `noCutBefore`. This is a FAITHFUL transliteration: do NOT re-decide, drop, add, reorder, merge, pad or "improve" anything — you EXPRESS cinematic's scene verbatim in intent, in the user's language.

   So: **screenwriting decides WHAT story and WHICH scenes; cinematic writes HOW each scene plays.** Apply both, then express the result in JSON; this skill invents neither. ONLY exception: purely mechanical edits, zero story/scene content (`references` paths, renaming, fixing a rejected field, re-numbering).
2. **`action` = zero ambiguity.** Models render literally and invent whatever is open. Every object/count/target/position → exactly ONE thing: exact count ("una única moneda"), specific target ("el botón de abajo, de una fila de 6"), concrete identifiers ("la maleta ROJA a su izquierda", never "su maleta"), the HOW (grip/finger/posture), ONE physical action per shot. No exempt shots (product/logo/establishing need the same precision).
3. **Carry-forward state (#1 continuity rule).** Once a shot establishes a NON-default state (standing on stacked cans, holding something, machine open, prop moved/broken), EVERY later shot where it still holds must restate it in `action`; the renderer silently resets otherwise. Splitting into micro-cuts is FREE; resetting state across a cut is broken. Back with per-shot `continuity` {characters, objects, place} (fill `place` on EVERY shot of a strong-setting scene so close-ups stay anchored; fill characters/objects wherever non-default state holds) + storyboard-level `continuity` LOCK (invariants + negatives).
4. **`stylePrompt` = `""`** unless the user's literal words request a style ("en estilo anime", "make it Pixar", "como Sin City", a ref image + "make it look like this"). Topic NEVER implies style (ninjas/mafiosos/dragones stay pencil sketch). Don't announce a style choice for plain requests.
5. **Carry the user's reference photos into `references`, MANDATORY.** Any character/subject/product photo the user gave (path in `## ATTACHED MEDIA` / `**Attached files:**`, image in `# WORKING AREA`, a named `@handle`) goes into `references` NOW (recurring/global look → storyboard level; some-shots-only → those shots' level); describing it in `characters` is NOT enough. IMAGES/`@handles` only. When a photo DEFINES/RECTIFIES a character, `read_file` it and describe what you SEE. Full detail (3-level cascade, video-crashes-render, describe-what-you-see, photo-overrides-sketch): see authoring-guide.md.
6. **User's language everywhere.** All editorial fields (`action`, `dialogue`, `characters`, `lighting`, names, notes...) in the conversing language; never translate. English happens at the compositor at render time, never in the JSON.
7. **Duration: the storyboard is the single timing authority (mechanic only).** Summed `duration`s ARE the runtime: re-read and re-sum before reporting/rendering; never silently retime to re-hit an old target. Only an explicit current hard-target ("que dure exactamente 30s") authorises retiming, and say what you retimed. This skill sets NO durations, shot counts or per-shot pacing itself — shot count, per-shot durations and where cuts fall are part of SCENE realization (`cinematic-video-prompt-engineer` writes them with each scene); the overall runtime target / how many scenes is `screenwriting`'s high-level call. Never decide either here.
8. **Character labels.** Define each recurring character ONCE in roster as `SHORT_UPPERCASE_A` (`HERO_A`, `DOG_A`) with silhouette-based desc, then reuse the label EXACTLY in every `action`/`dialogue`; never drift to "the hero"/"she". Compositor inflates labels at render time.
9. **`noCutBefore` glues panels into ONE take/clip** (`true` on every panel after the first; NEVER on a scene's first shot — scene boundary = cut). That is the field mechanic; WHEN to break a camera move into beat-by-beat panels is cinematography — `cinematic-video-prompt-engineer` decides it (see authoring-guide.md for the `noCutBefore` field semantics).
10. **The storyboard is the single source; the video is generated DIRECTLY from it — there is NO keyframe/panel-sheet step.** Edits to the JSON simply take effect on the next `storyboard-to-video` render (its shots are grouped into clips and rendered straight to video). If a rendered video already exists and the user changed the story, say which clips are now out of date and offer to re-render; never leave a stale render presented as current.
11. **Image generation is automatic.** The visor renders every card (pencil preamble + compositor prompt; edits re-render via cache hash). NEVER call `generate_image` for storyboard shots.
12. **Every roster character MUST be associated with a character card — MANDATORY.** Each `characters` entry needs a `characterId` linking a saved `~/.koi/characters/<id>.json` card (with a generated turnaround), because the card + its sheet are what lock that character's identity in the video (a text description does not carry a face). When you author or finish a storyboard whose roster has UNLINKED members (no `characterId`), you MUST resolve it — ASK the user via `prompt_user`/`prompt_form` (NEVER a `print`): *"do you want to ASSOCIATE existing character(s), or shall I INVENT and create new ones?"*
   - **Associate** → let the user pick the existing card(s); write each returned id into that roster entry's `characterId`.
   - **Invent** → for EACH unlinked member, via the `characters` skill: (1) `save_character` with the roster entry's `name` + `description` + `sex` + `age` (fill every attribute); (2) `generate_character_sheet` to build and attach its TURNAROUND IMAGE (pass `characterId`); (3) write the returned `characterId` back into the roster entry. Do all three — a character invented but with no card or no sheet is incomplete.
   Never silently skip the association; a storyboard headed for video with unlinked characters is a reported bug.

## The SCENE CONTENT — action, dialogue, planos → written by `cinematic-video-prompt-engineer`, not here

This skill does not write the scene: not the `action`, not the `dialogue`, not the shots. Cinematic realises each scene from screenwriting's brief and hands back every per-shot field — `action` (physical beats), `dialogue` (naturalistic lines + delivery), and the cinematography, all FREE TEXT (no preset menus): `shot` (framing = shot-size + angle), `camera` (movement + lens/focal + speed + focus), `composition` (in-frame layout + screen-direction / 180 / eyeline), `lighting` (per-shot light), plus `noCutBefore` (where cuts fall), `sfx`/`music` and durations. This skill only WRITES cinematic's decisions into those fields; it invents none of them.

- `references/authoring-guide.md` — field semantics + contracts (the `action` zero-ambiguity bar, continuity fields): how the fields must be filled ONCE cinematic has authored them. (Not a source for WHAT to write.)

## Reference files (load on demand)

This skill's guides:

| File | When |
|---|---|
| [references/authoring-guide.md](references/authoring-guide.md) | Writing/editing ANY content: full field semantics, `action` precision bar + examples, continuity fields, `noCutBefore`, references cascade, stylePrompt anti-examples, duration detail, language rules, legacy schemas. |
| [references/from-video.md](references/from-video.md) | Storyboarding an EXISTING video (1:1 transcription). |

**The SCENE CONTENT — action, dialogue, planos — is `cinematic-video-prompt-engineer`'s, NOT the files below.** The `screenwriting` library is the HIGH-LEVEL story ARCHITECTURE only (premise, structure, sequences, the scene map, characters), read through a storyboard lens:

| File | Load while storyboarding when |
|---|---|
| `.../story-structure.md` | Inventing/restructuring: give even a 20s spot five-act shape (want+obstacle, inciting incident, MIDPOINT at center, worst point, climax mirroring opening). The scene progression IS the act structure; check vs its checklist. |
| `.../scene-craft.md` | Defining each scene's FUNCTION at the map level: does it change something (else cut it), where its turning point sits. (Writing the scene's actual beats/dialogue is cinematic's, not here.) |
| `.../character-dialogue-subtext.md` | The CHARACTER bible: who each character is, their arc, their distinct voice/register. (Writing the actual `dialogue` lines is cinematic's, not here.) |
| `.../production-craft.md` | Producibility of the STORY: one page = one minute, what survives the edit. |
| `.../structure-worked-examples.md` | Calibrating a longer/trickier piece vs real act maps (Raiders, Hamlet, The Godfather...) or a user talking Save the Cat / Field / Vogler. |
| `.../tv-and-series-structure.md` | Episodic (series of spots, webserie, chaptered): story engines, serial midpoints, cliffhanger placement across episodes. |

(paths above = `../screenwriting/references/`)

## Create vs MODIFY: decide FIRST, every time

**DEFAULT = MODIFY the storyboard you're already working on. Create NEW only when the user EXPLICITLY asks for a new/separate/another storyboard.** (Wrong = duplicate tab + lost work, reported bug.)

The working storyboard is set by the CONVERSATION, not by focused tab: whichever you most recently created/saved/`read_file`'d in THIS conversation; track its `id`. Every follow-up ("rectifica", "añade un plano", a new reference photo, "itera") targets THAT storyboard even if the user focused another doc. Fallback ONLY when no storyboard is established in the conversation: the active document in `# WORKING AREA`. When in doubt and a storyboard is open → MODIFY. Never default to create.

## Flow: creating a NEW storyboard

1. **Invoke `screenwriting` first for the HIGH-LEVEL story** (rule 1a): develop the premise, the five-act shape (concrete want+obstacle, turning point at center, last scene answers the first), the SCENE MAP (the ordered list of scenes with each one's function/goal/location/characters) and the characters. Even a 20s ad reads better as a tiny five-act story. **Then, per scene, DELEGATE it to the isolated `scene-writer` agent** (rule 1b): it writes the whole scene natively (`action`, naturalistic `dialogue`, the planos, `noCutBefore`, `sfx`/`music`, durations) in a clean context; you TRANSLITERATE its output into the shots (fallback: run cinematic inline if the agent is unavailable).
2. **Pick a UNIQUE id** (descriptive kebab; suffix `-v2`/date if collision-prone). Reusing an id = "new storyboard shows old shots" bug; on collision `save_storyboard` auto-renames and returns the new id, use it after.
3. **Build as a STRUCTURED OBJECT** (a tool argument, never hand-serialized JSON): id, name (NO aspect/format — it is NOT a storyboard property; see the schema note), `synopsis` (almost always), `continuity` LOCK (any story with physical logic), characters roster, lighting, stylePrompt `""`, scenes/shots with all editorial fields in user's language, per-shot `continuity` rows, durations. Carry reference photos into `references` (rule 5). Do NOT set `version`/`createdAt`/`updatedAt` or compute path.
4. **`save_storyboard`** with the object. On `success: false`, read `error`, fix that field, retry.
5. **Verify**: success true, AND if a reference photo was given, at least one `references` entry carries it; if missing, add and save again BEFORE moving on.
6. **`show_result`** with `resourceType: 'file'`, the returned absolute path, and the name (opens the visor tab). Tell the user it's ready (name + shot count) and ask for tweaks.

**From an EXISTING video** (not creative: 1:1 transcription): `read_file` the video FIRST (watch natively; never ffprobe/extract_frame/transcribe_audio), one shot per cut with real timecodes, verbatim dialogue; verify durations sum EXACTLY to `durationSec` and shot count == cut count before saving. Full flow: [references/from-video.md](references/from-video.md).

## Flow: modifying an EXISTING storyboard

0. **Invoke the craft skills first for ANY content change** (rule 1): `screenwriting` for high-level story/structure/scene-map/character edits, `cinematic-video-prompt-engineer` for anything INSIDE a scene (action, dialogue, planos, cuts, light); skip only for purely mechanical edits.
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
