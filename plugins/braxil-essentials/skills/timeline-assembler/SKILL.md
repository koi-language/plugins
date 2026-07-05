---
name: timeline-assembler
description: "Canonical rules for assembling a Braxil timeline — track conventions, fps / aspect-ratio inheritance from source clips, audio mixing levels, music ducking, transitions, subtitles, and the preview-before-render handoff. Use whenever a workflow stitches multiple media clips into a single output via create_timeline + add_clip_to_timeline + render_timeline. Triggers: timeline, assemble video, montar video, montar timeline, build timeline, compose video, stitch clips, render timeline, edit timeline."
---

This skill is the source of truth for HOW to build a Braxil timeline well. It's intentionally workflow-agnostic — `create-video`, future `create-social-clip`, `slideshow-to-video`, `podcast-to-video`, anything that ends in a `render_timeline` call should follow these rules. Workflows just supply the inputs (which clips, which audio, which subtitles); the assembly logic lives here.

## 🛑 The timeline is addressed by `id`, never by a disk path you hunt for

`create_timeline` returns `{ success, id, timeline }` — that `id` **is** the timeline. Every subsequent tool (`add_clip_to_timeline`, `set_clip_volume`, `get_timeline`, `render_timeline`, `show_result`) takes that `id`. You already hold everything you need from the tool responses; the on-disk JSON is internal renderer plumbing, not something you address.

Therefore, **forbidden, full stop**:

- ❌ "Let me search the created timeline on disk to confirm its exact path" — i.e. *"Buscaremos la línea de tiempo creada en el disco para confirmar su ruta exacta."* There is nothing to confirm: the `id` came back in the `create_timeline` response. This step must never exist.
- ❌ Any `shell` / `find` / `ls` / `read_dir` / `read_file` against `.koi/timelines/` (or any `.koi/**` dir) to locate, verify, or "make sure it saved". Those dirs hold EVERY project — you'd grab another session's file.
- ❌ Re-deriving a path from the `id` to read the JSON yourself. Need the current state? Call `get_timeline(id)` — it returns the full object from the DB-backed store.

Lost the `id` (you shouldn't — it's in the response)? The ONLY recovery is `recall_creations({ kind: 'timeline' })` → `inspect_creation(id)`. The database is the single lookup path. Disk is never a fallback.

## Reading & editing an existing timeline — dedicated tools, NEVER file tools

A timeline is a LIVE app artefact: the GUI visor watches it and reflows the instant it changes, and the user can also edit it inline. So your in-memory copy from a previous turn may be stale — **re-read the CURRENT state immediately before every edit**, never trust a snapshot.

- **READ:** `get_timeline` — no args needed for the timeline the user has open (defaults to the active document); returns the full live JSON (clips with `startMs`, `track`, `scale`, `offsetX/Y`, …). Do NOT `read_file` a timeline to inspect it — `read_file` RENDERS it to a video so you can WATCH it; it does not give you the structure.
- **WRITE (default):** transform that JSON yourself and send the WHOLE result back in a SINGLE `update_timeline` call (atomic full-state replacement). One read + one write covers any edit — bulk changes, reordering, retiming, structural surgery — with no per-tool contract to learn and no partial application.
- **WRITE (shortcut):** for a trivial tweak to ONE clip ("mute this", "move that 2s"), a single `update_clip` / `move_clip` / `trim_clip` call is cheaper than re-emitting the full JSON. Use them only in that case.

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

**Auto-pair audio for V clips:** when you call `add_clip_to_timeline` with a V-track video that has an audio stream (ffprobe-detected at add time), the tool automatically drops a sibling clip on the first free A lane — same path, same `startMs`, same `durationMs`, sharing a `linkId` so move/trim/remove stays in sync. The V clip's own `hasAudio` is flipped to false to prevent double-mixing; the A peer becomes the canonical source for the renderer and for any per-clip volume edits (`set_clip_volume`, `volumePoints`, mute). You get the dedicated audio lane "for free" — same UX as dropping a clip into Final Cut / DaVinci. To opt out (e.g. you want a silent video layer), pass `hasAudio: false` to `add_clip_to_timeline`.

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
2. `add_clip_to_timeline` × N for V1 video clips, in time order. The first call seeds fps + dimensions automatically.
3. If music: ONE `generate_audio({ duration: total_seconds })` then `add_clip_to_timeline` for the music file on A2. Duck it ONLY if voice/dialogue plays over it — `set_clip_volume(clipId, { change: { gain: 0.04 } })` (-28 dB) where the voice speaks (or `volumePoints` for mixed sections). If there's NO voice (ambient music scoring an action, intro/outro, montage), leave it at a normal present level — do NOT duck. See "Audio mixing levels".
4. (Optional) `set_clip_transition` on the few clips that warrant a soft edge.
5. (Optional) `add_subtitles_to_timeline` for tutorial / social explainer.
6. **`show_result({ resourceType: "timeline", timelineId })`** — open the timeline editor so the user can preview / scrub / approve before the render burns cycles.
7. `render_timeline({ id })` — NO fps / width / height overrides; let the inherited settings drive.
8. `show_result({ resourceType: "video", path: <rendered file> })` — surface the final mp4.

Skipping step 6 (the preview) is allowed only when the user explicitly said "render directly". The default UX is: assemble → show timeline → render → show video. The user gets two chances to review (timeline + final) instead of just discovering issues on the rendered file.

## Common mistakes to avoid

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
