---
name: timeline-assembler
description: "Canonical rules for assembling a Braxil timeline — cutting a source with TRIMMED clips (never new files), track conventions, fps / aspect-ratio inheritance, audio mixing / ducking, transitions, subtitles, and finishing by SHOWING the timeline (never auto-rendering). Use whenever a workflow stitches clips or trims a source into a video via create_timeline + add_clip_to_timeline. Triggers: timeline, assemble video, montar video, montar timeline, build timeline, compose video, stitch clips, cut video, quitar tomas falsas, recortar video, edit timeline."
---

This skill is the source of truth for HOW to build a Braxil timeline well. It's intentionally workflow-agnostic — `create-video`, future `create-social-clip`, `slideshow-to-video`, `podcast-to-video`, anything that assembles clips should follow these rules. Workflows just supply the inputs (which clips, which audio, which subtitles); the assembly logic lives here.

## 🛑 SUPER-MUST #1 — Cut a source with TRIMMED clips, NEVER new .mp4 files

To build a video out of a source that has bad takes / dead air / parts to drop, you do **NOT** create new video files. The timeline plays **TRIMMED segments of the SAME source**: place several clips that ALL point at that ONE source `path`, each spanning a different `[X → Y]` range of the source. That is exactly what a timeline is for.

A clip is trimmed with `sourceInMs` + `durationMs` in `add_clip_to_timeline`:
- `path`: the **SAME source video** — reuse the exact same file for every segment.
- `sourceInMs`: where IN THE SOURCE the segment starts, ms (second X × 1000).
- `durationMs`: how long the segment plays, ms ((Y − X) × 1000).
- `startMs`: where the segment sits on the timeline (append after the previous one).

Example — "keep 0–4 s and 9–15 s of `take.mp4`, drop the fluffed bit in between" = **TWO clips of the same file**: `{ path: "take.mp4", startMs: 0, sourceInMs: 0, durationMs: 4000 }` then `{ path: "take.mp4", startMs: 4000, sourceInMs: 9000, durationMs: 6000 }`. Add as many segments as you need until it's perfect; nudge each edge with `trim_clip`.

**FORBIDDEN, full stop:** creating ANY new `.mp4` (via `generate_video`, `ffmpeg`, a re-encode, a "cut clips" step) to stitch a video out of an existing source. Never duplicate a source into new files to assemble it — the source is placed as-is with trimmed clips (same file, different in/out). This is a MUST.

## 🛑 SUPER-MUST #2 — Assembling a video = SHOW the timeline, NEVER render it

When you assemble a video, the deliverable is the **TIMELINE shown in the work area** — NOT a rendered mp4. Do **NOT** call `render_timeline`, do **NOT** "generate the video". Finish with:

`show_result({ resourceType: "timeline", timelineId })`

The timeline plays fully in the work area (preview, scrub, inline editing). Flattening it to an mp4 with `render_timeline` is done **ONLY** when the user EXPLICITLY asks to export / render / download the final file. Default assembly ends at "show the timeline" — never at a render. This is a MUST.

## Editing a talking-head video → `references/TALKING_HEAD.md`

Editing a raw **talking-head / selfie / piece-to-camera** source (a person talking
straight at the camera — UGC ad, founder explainer, etc.) has its own playbook:
**cut the silences / dead air, alternate normal↔zoom framings so no shot runs past
~10 s (keeping the face in frame), pop a brand logo on V2 when a brand is named,
and drop topic-matching B-roll cutaways**. Read **`references/TALKING_HEAD.md`**
for the full rules whenever the source is someone talking to camera.

## 🛑 The timeline is addressed by `id`, never by a disk path you hunt for

`create_timeline` returns `{ success, id, timeline }` — that `id` **is** the timeline. Every subsequent tool (`add_clip_to_timeline`, `set_clip_volume`, `get_timeline`, `render_timeline`, `show_result`) takes that `id`. You already hold everything you need from the tool responses; the on-disk JSON is internal renderer plumbing, not something you address.

Therefore, **forbidden, full stop**:

- ❌ "Let me search the created timeline on disk to confirm its exact path" — i.e. *"Buscaremos la línea de tiempo creada en el disco para confirmar su ruta exacta."* There is nothing to confirm: the `id` came back in the `create_timeline` response. This step must never exist.
- ❌ Any `shell` / `find` / `ls` / `read_dir` / `read_file` against `.koi/timelines/` (or any `.koi/**` dir) to locate, verify, or "make sure it saved". Those dirs hold EVERY project — you'd grab another session's file.
- ❌ Re-deriving a path from the `id` to read the JSON yourself. Need the current state? Call `get_timeline(id)` — it returns the full object from the DB-backed store.

Lost the `id` (you shouldn't — it's in the response)? The ONLY recovery is `recall_creations({ kind: 'timeline' })` → `inspect_creation(id)`. The database is the single lookup path. Disk is never a fallback.

## Reading & editing an existing timeline — dedicated tools, NEVER file tools

A timeline is a LIVE app artefact: the GUI visor watches it and reflows the instant it changes, and the user can also edit it inline. So your in-memory copy from a previous turn may be stale — **re-read the CURRENT state immediately before every edit**, never trust a snapshot.

**⚡ The fast, default way to edit a timeline is to WORK ON THE JSON: `get_timeline` → transform the whole object in memory → `update_timeline` (which saves the modified .json).** One read + one write covers ANY edit, however big — building all the clips, splitting a source into many trimmed segments, retiming, reordering, adding overlays, setting every `scale`. Do NOT drive an edit as a long chain of unitary calls (`add_clip_to_timeline` × N, `move_clip`, `set_clip_volume`, `trim_clip`, `update_clip`…): that's slow, chatty, and each call re-validates. Compose the final state once and write it once.

- **READ:** `get_timeline` — no args needed for the timeline the user has open (defaults to the active document); returns the full live JSON (clips with `startMs`, `track`, `scale`, `offsetX/Y`, …). Do NOT `read_file` a timeline to inspect it — `read_file` RENDERS it to a video so you can WATCH it; it does not give you the structure.
- **WRITE (default, use this almost always):** transform that JSON yourself and send the WHOLE result back in a SINGLE `update_timeline` call (atomic full-state replacement). `update_timeline` IS "edit the .json" — minus the risk of a malformed hand-write breaking the visor.
- **WRITE (shortcut — ONLY for a tiny, isolated change):** for a single trivial tweak to ONE clip ("mute this", "move that 2s") a unitary `update_clip` / `move_clip` / `trim_clip` / `set_clip_volume` is fine and cheaper. The moment the edit touches MORE than one clip, or adds/removes/retimes several, go back to the read-JSON → `update_timeline` path. NEVER use the unitary tools to assemble or to do a multi-clip edit.

## The timeline JSON shape — what to build / transform for `update_timeline`

`update_timeline` call: `{ id: "<timelineId>", state: { settings, clips } }` — `state` MUST contain `settings` and `clips`; the `id` comes from the param, NOT from `state`. `get_timeline` returns `{ id, name, version, settings, clips }` → transform `settings` + `clips` and send them back as `state`. When editing, START from what `get_timeline` returned and change only what you need; **only include fields you actually set** — omitted optional fields default sensibly, don't invent values.

### `settings`
`{ projectFps, projectWidth, projectHeight, videoTracks, audioTracks, activeVideoTrack, activeAudioTrack, pixelsPerSecond, playheadMs, trackHeight, … }`. `projectFps` / `projectWidth` / `projectHeight` are inherited from the first video clip (see "FPS and dimensions") — do NOT change them unless the user wants a different render shape. Leave the view fields (`pixelsPerSecond`, `previewSplit`, `playheadMs`, `trackHeight`…) exactly as `get_timeline` returned them.

### `clips[]` — each clip object
**Required (every clip):**
- `id` — `"clip-<hex8>"`. KEEP existing ids when editing; for a NEW clip mint a fresh unique one.
- `track` — `"V1"`/`"V2"`/`"A1"`/`"A2"`… (STRING). V-tracks stack (higher = on top); A-tracks all mix.
- `path` — absolute source file (or sentinel `"title:<id>"` / `"timeline:<id>"`).
- `startMs` — position ON THE TIMELINE, integer ms.
- `durationMs` — visible length, integer ms ≥ 50.

**Trim (place a SEGMENT of a source — this is how you cut / drop silences, SUPER-MUST #1):**
- `sourceInMs` — where IN THE SOURCE this clip starts (ms; 0 = from the top).
- `sourceTotalMs` — the source's true length (ms); keep it accurate so a trim never runs past the end.

**Visual transform (per clip):**
- `scale` — zoom (1.0 = fit, 1.15–1.3 = punch-in). `offsetX` / `offsetY` — re-frame after a zoom so the subject stays centred (never crop the face out).
- `sourceWidthPx` / `sourceHeightPx` — source native pixel size (probed on add). `rotation`, `hue`, `saturation`, `brightness`, `contrast`, `cornerRadiusPx`… — optional colour/geometry.

**Audio & linking:**
- `linkId` — shared id pinning a V clip to its auto-paired A peer (they move/trim/remove together) — keep it consistent.
- `hasAudio` — whether the clip feeds the mix. `volumePoints` — `[{ t, v }]` gain automation (`t` = ms, `v` = linear gain 0–2).

**Transitions:**
- `transitionIn` / `transitionOut` — `{ type, durationMs, alignment, params? }` (e.g. a cross-dissolve out on a logo/overlay; see "Transitions").

**Other:**
- `shotCuts` — detected shot-cut points inside the source, in source-ms (the clip's "tomas"; see `extract_take`). `titleProps` — typography for `title:` clips. `aiState` — AI-generation provenance on AI clips; leave it as-is.

Both paths validate and the GUI reflects the change instantly. **Do NOT hand-edit the timeline JSON with `edit_file`/`write_file`** — `update_timeline` IS the "edit the JSON" path, minus the risk of a malformed write breaking the visor. If your edit reports success the user sees it on the next paint; if it failed, the visor won't change — surface the failure, don't claim success.

## Tracks — z-order and mixing

Tracks are named `V1`, `V2`, … (video) and `A1`, `A2`, … (audio). Their semantics differ:

- **V-tracks stack visually.** Higher number = higher in the z-order. V2 paints OVER V1 (covers whatever V1 was showing for the same time range); V3 paints over V1+V2; etc. Use V2+ for cutaways, overlays, lower-thirds, title cards, picture-in-picture.
- **A-tracks mix audibly.** All A-tracks play SIMULTANEOUSLY and their levels are summed (`amix`). A higher A-track number does NOT mute the lower ones — they all sound together at their respective volumes. Use one track per audio role so each can be levelled independently.

### Canonical track layout

| Track | Use |
|---|---|
| **V1** | Main video — per-scene / per-sheet renders, in sequence on the time axis |
| **V2** | Visual overlays — logos, lower-thirds, image cutaways, title cards, B-roll inserts (paints over V1 for the duration of the overlay clip) |
| **V3+** | Additional overlay layers when V2 isn't enough (rare) |
| **A1** | Voiceover / dialogue — auto-paired by `add_clip_to_timeline` when a V-track clip carries audio (a sibling A1 clip is created with the same path / start / duration / linked via `linkId`). Or a dedicated TTS pass when the workflow chose silent video + external voice. |
| **A2** | Background music — ONE continuous clip sized to the full video duration |
| **A3+** | SFX / foley accents (whooshes, taps, stings) — one per type if needed |

### 🛑 Every video clip with sound MUST have a paired A-track audio clip — ALWAYS

A V-track video clip that carries audio does NOT sound on its own in the mix — its sound comes from a **paired clip on an A-track**. So **every** talking/video clip that has audio MUST have an audio peer on an A-lane. No exceptions (unless the clip is genuinely silent and you want it silent).

- **Via `add_clip_to_timeline`:** this is automatic — when you add a V-track video with an audio stream (ffprobe-detected), the tool drops a sibling clip on the first free A lane (same `path`, `startMs`, `durationMs`, `sourceInMs`, sharing a `linkId`), and flips the V clip's `hasAudio` to false to avoid double-mixing. The A peer is the canonical source for the renderer and for volume edits (`set_clip_volume`, `volumePoints`, mute). To opt out for a genuinely silent layer, pass `hasAudio: false`.
- **⚠️ Via `update_timeline` (building the JSON yourself): the auto-pair does NOT run — you MUST add the A-track peers by hand.** For EVERY V-track video clip that has audio, emit a matching A-track clip in the `clips` array: same `path`, `startMs`, `durationMs`, `sourceInMs`, a shared `linkId`, on an A lane — and set the V clip's `hasAudio: false`. Forgetting this = a video with NO SOUND (the reported bug: a talking-head timeline that had zero A-track clips → silent). This is a MUST.

**Example — one talking segment (trimmed 22–34.5 s of the source), with its audio peer:**

```json
{ "id": "clip-seg1v", "track": "V1", "path": "/…/IMG_1659.MOV",
  "startMs": 0, "durationMs": 12500, "sourceInMs": 22000, "sourceTotalMs": 91120,
  "linkId": "seg1", "hasAudio": false },
{ "id": "clip-seg1a", "track": "A1", "path": "/…/IMG_1659.MOV",
  "startMs": 0, "durationMs": 12500, "sourceInMs": 22000, "sourceTotalMs": 91120,
  "linkId": "seg1" }
```

The V clip shows the picture (`hasAudio:false`), the A1 peer carries its voice — same `startMs`/`durationMs`/`sourceInMs`, same `linkId`. Do this for every talking segment.

## FPS and dimensions inherit from the first video clip

The timeline does NOT have a hardcoded frame rate or output size. When the FIRST video clip is dropped via `add_clip_to_timeline`, it ffprobes the source for `avg_frame_rate`, `width`, `height` and stamps them onto `timeline.settings.{fps,width,height}`. The renderer reads those before falling back to its 30 fps × 1920×1080 default.

**Why this matters:** a 24 fps source playing inside a 30 fps timeline (or 1080×1920 vertical clips in a 1920×1080 horizontal timeline) produces visible black flickers at every clip seam and black bands around the frame. Inheritance keeps source and output aligned by default.

**Rules:**
- DO NOT pass `fps`, `width`, or `height` to `create_timeline` unless the user explicitly asked for a specific render shape.
- DO NOT pass them to `render_timeline` either — let the inherited values drive the render.
- The inheritance only fires for the FIRST video clip on an empty timeline. Later clips on a populated timeline don't silently change the project's framerate.
- If the clips are heterogeneous (mixed 24 / 30 fps sources), the FIRST clip wins. Either re-encode the rest to match in pre-production, OR explicitly call `setTimelineSettings` with the target fps before dropping any clip.

## Audio mixing levels (linear gain → dB cheat sheet)

`set_clip_volume({ clipId, change: { gain: <value> } })` takes a linear gain in `[0, 2]`. Conversion: `dB = 20 × log10(gain)`. Reference values:

| Source role | Linear gain | dB | When to use |
|---|---:|---:|---|
| Voiceover / dialogue (V-track embedded) | 1.0 | 0 dB | Default for spoken content — the reference level |
| Music UNDER voiceover (ducked) | **0.04** | **-28 dB** | The standard mix while a narrator / character is speaking |
| Music in intro / outro / silent montage (not ducked) | 0.25 | -12 dB | When there's no voice over the music — let it breathe a bit louder |
| SFX accent (whoosh, click, sting) | 0.5–0.7 | -6 to -3 dB | One-off transients; should be audible but not steal focus |
| Background ambient bed (continuous room tone) | 0.1–0.2 | -20 to -14 dB | Texture under voice; never compete with the voiceover |
| Mute a clip without removing it | 0.0 | -∞ dB | Same as setting `volumePoints: null` and a 0-curve |

**Duck music ONLY when it competes with VOICE — decide from the actual audio, don't duck reflexively.** The duck exists so a narrator / character can be heard over the music. So:
- **There IS voiceover / dialogue playing over the music** (the V-track clips carry spoken lines, or there's a separate VO track) → duck the music to ≈ -28 dB (0.04) **for the stretches where the voice is speaking** so the words sit on top. At unity gain the music drowns the voice (the "música demasiado alta" complaint).
- **There is NO voice** — the music is the main audio, an ambient bed scoring an action sequence, an intro/outro, a montage, an SFX-only beat — **do NOT duck it.** Ducking a wordless action scene to -28 dB makes it sound broken/empty. Keep the music at a normal, present level (roughly unity / -3 to -6 dB, or whatever the piece needs).
- **Mixed** (voice in some sections, none in others) → use `volumePoints` keyframes: full level where there's no voice, ducked where the voice speaks (see "Two-level music" below). Don't flat-duck the whole track.

The agent makes this call per video by looking at whether voice is actually present at each point — there is NO fixed "always duck" rule. When in doubt: voice present → duck under it; no voice → leave it up.

**Two-level music (intro loud, body ducked):** if the video opens with 2-3 seconds of music alone before the voice kicks in, use `volumePoints` keyframes instead of a single gain:
- `{ t: 0, v: 0.25 }` → -12 dB during the intro
- `{ t: 2500, v: 0.04 }` → ramp to -28 dB by 2.5 s (a tiny dip works better than a hard cut)
- `{ t: <voice_end_ms>, v: 0.25 }` → back up for the outro

## Music is ONE single track — never per-clip

When multi-clip workflows generate the video as N independent clips (e.g. 2× 15 s sheets stitched into a 30 s video), DO NOT ask the per-clip generator for music. Independent renders cannot preserve melody continuity across the seam — the music cuts / restarts every clip boundary and the audible result is broken. Generate ONE music file sized to the full video duration via `generate_audio` and lay it on A2 as a single clip.

For single-clip videos (one render covers the whole duration with no seams) music inside the clip is fine; this constraint only fires for multi-clip assembly.

## Per-clip audio (V-track) is sacred

When the workflow's clips are generated via `generate_video` and the timeline will mix their audio:
- `withAudio: true` is **MANDATORY** on every clip. Setting it false because a scene has no spoken lines is the silent-clip bug — even a wordless scene needs room tone / footsteps / SFX baked in.
- The clip's prompt MUST describe the audio explicitly: voiceover lines in panel order, ambient / SFX appropriate to the scene, AND when ≥ 2 sheets are stitched, a "no music or background score in this clip; music will be added on the timeline" line. The model fills in voiceover-or-SFX based on what the prompt asks for; if the prompt is silent on audio, the result is often silent video.

## Aspect ratio comes from the platform, applied to every clip

Pass `aspectRatio` to EVERY `generate_video` call upstream. The timeline does NOT reframe clips on its own — if the clips are 16:9 and the timeline ends up 9:16, the renderer letterboxes (black bars top + bottom). The reframe must happen at clip generation time, not at render time.

| Platform | Aspect ratio | Frame size (typical) |
|---|---|---|
| Reels / TikTok / Shorts | 9:16 | 1080 × 1920 |
| YouTube / Vimeo / Web | 16:9 | 1920 × 1080 |
| Instagram feed (square) | 1:1 | 1080 × 1080 |
| Instagram feed (portrait) | 4:5 | 1080 × 1350 |

## Transitions (default = hard cut)

The renderer cuts hard between clips unless a transition is set explicitly via `set_clip_transition`. Hard cuts are the right default — soft transitions easily look amateur if applied uniformly.

| Workflow / context | Default | When to add a soft transition |
|---|---|---|
| ad | Hard cut | Rarely — only on a rhetorical "before / after" reveal |
| explainer | Hard cut | Cross-fade (300 ms) between major narrative sections |
| tutorial | Hard cut | None — each step starts crisply |
| demo | Hard cut | Soft fade (200 ms) on the hero product reveal frame |
| social-post / Reels / TikTok | Hard cut + whoosh SFX | Never crossfade — kills the platform's punchy feel |
| Narrative / dialogue scene | Hard cut | Cross-fade on scene-change beats; never within a scene |

When in doubt, leave hard. Soft transitions are an editorial choice, not a polish step.

## Subtitles

`add_subtitles_to_timeline` lays a synthetic subtitle track. Add it when:
- **Tutorial** → always. Step-by-step viewers read along.
- **Explainer** → optional, recommended for social-feed distribution where viewers may scroll with sound off.
- **Ad / Demo** → captions are usually baked into the storyboard already (CAPTION row of each panel), so a separate subtitle track duplicates them. Skip unless the user explicitly asked.
- **Social-post** → captions are part of the visual language — usually rendered as big animated text in the V-track clips themselves, not as a subtitle track.

When you do add subtitles, derive the segments from the panel `caption` / `dialogue` fields the workflow already produced; never re-write them at the timeline stage.

## The render hand-off

The canonical end-of-workflow sequence:

1. `create_timeline({ name: "<video-title>" })` — NO fps / width / height overrides.
2. `add_clip_to_timeline` × N for V1 video clips, in time order — trimmed segments of the SAME source(s) per SUPER-MUST #1 (never new files). The first call seeds fps + dimensions automatically.
3. If music: ONE `generate_audio({ duration: total_seconds })` then `add_clip_to_timeline` for the music file on A2. Duck it ONLY if voice/dialogue plays over it — `set_clip_volume(clipId, { change: { gain: 0.04 } })` (-28 dB) where the voice speaks (or `volumePoints` for mixed sections). If there's NO voice (ambient music scoring an action, intro/outro, montage), leave it at a normal present level — do NOT duck. See "Audio mixing levels".
4. (Optional) `set_clip_transition` on the few clips that warrant a soft edge.
5. (Optional) `add_subtitles_to_timeline` for tutorial / social explainer.
6. **`show_result({ resourceType: "timeline", timelineId })` — THIS IS THE END.** Show the assembled timeline in the work area. STOP here. Do NOT render (SUPER-MUST #2).

**Rendering to a flat mp4 is NOT part of assembly.** Only when the user EXPLICITLY asks to export / render / download the final file do you then:
7. `render_timeline({ id })` — NO fps / width / height overrides; let the inherited settings drive.
8. `show_result({ resourceType: "video", path: <rendered file> })` — surface the final mp4.

Default UX: assemble → **show the timeline** → done. The user previews, scrubs and edits it live; they render it themselves (or ask you to) if and when they want a flat file. Never auto-render.

## Common mistakes to avoid

- ❌ Creating NEW `.mp4` files to cut a source (bad takes, dead air). WRONG — place TRIMMED clips of the SAME source (`sourceInMs` + `durationMs` on the same `path`). Never `generate_video` / `ffmpeg` / re-encode a source into new files to assemble it. See SUPER-MUST #1.
- ❌ Rendering the timeline (or "generating the video") as the finish. WRONG — assembly ENDS at `show_result({ resourceType: "timeline", timelineId })`. Only render when the user explicitly asks to export. See SUPER-MUST #2.
- ❌ `ffmpeg concat` to glue clips instead of using `create_timeline`. The timeline is the abstraction; concat strips you of multi-track, mix, reframe, transitions, subtitles, and crash recovery.
- ❌ Passing `fps` / `width` / `height` to `create_timeline` or `render_timeline` as defensive defaults. Inheritance is doing the right thing; overriding it re-introduces the black-flicker / black-band bugs.
- ❌ Music drowning the voice. WHEN there's voiceover/dialogue, duck the music to -28 dB under it (or volumePoints for mixed sections). ❌ But also: don't duck music that has NO voice over it (ambient/action/intro/outro) — that makes a wordless scene sound empty. Decide from the actual audio.
- ❌ Mixing audio across V-tracks expecting only one to play. ALL audio mixes — set unwanted clips' gain to 0 instead of relying on track order.
- ❌ Generating clips in 16:9 and hoping the timeline will reframe to 9:16. It won't — it letterboxes. Pass `aspectRatio` to `generate_video` upstream.
- ❌ Per-clip music in multi-clip assemblies. Audible seam every 15 s. Always one continuous music track on A2.

## Related tools

- `create_timeline` — instantiate
- `add_clip_to_timeline` — drop a clip (auto-probes fps/dims for the first video clip)
- `set_clip_volume` — duck / boost a clip
- `set_clip_transition` — soft edges
- `add_subtitles_to_timeline` — synthetic subtitle track
- `move_clip` / `trim_clip` / `update_clip` / `remove_clip` — post-add edits
- `add_track` / `remove_track` — adjust the track count
- `render_timeline` — final render (mp4 by default)
- `show_result({ resourceType: "timeline", timelineId })` — open editor preview
- `show_result({ resourceType: "video", path })` — open rendered file
