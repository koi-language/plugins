---
name: timeline-assembler
description: "Canonical rules for assembling a Braxil timeline — cutting a source with TRIMMED clips (never new files), track conventions, fps / aspect-ratio inheritance, audio mixing / ducking, transitions, subtitles, and finishing by SHOWING the timeline (never auto-rendering). Use whenever a workflow stitches clips or trims a source into a video via create_timeline + add_clip_to_timeline. Triggers: timeline, assemble video, montar video, montar timeline, build timeline, compose video, stitch clips, cut video, quitar tomas falsas, recortar video, edit timeline."
---

Assembling a timeline is **task-dependent**: how you build a video depends on WHAT KIND of video it is and WHAT SOURCES you have. There is no single universal recipe — trimming one raw talking-head take, stitching several generated storyboard clips, a slideshow, a podcast-to-video are all assembled differently. **A priori you do NOT know how to build it.** So don't assume a sequence up front:

1. **Identify the video and its sources** — what is being made (talking-head / UGC, interview, travel, event, product / demo, storyboard film or ad, slideshow, podcast-to-video, highlights / recap, vertical reel / TikTok…), and what you're actually given: one raw take to trim? several finished clips to concatenate? images? a separate audio / music track? dialogue with dead air? The type matters less than the shape of the sources — many types assemble the same way (talking-head ≈ interview ≈ screencast = trim one source; travel ≈ event ≈ slideshow = montage of media + music).
2. **See what the job needs** — which of the tasks below actually apply to THIS video.
3. **Read the reference for each task before doing it.** Each `references/` file is the source of truth for its task; paths are relative to THIS skill's directory (`list_skills` to find it).

## Tasks — identify yours, then read its reference

| If the job involves… | Read |
|---|---|
| **Cutting a source** — trimming a take, dropping silences / dead air / bad takes | `references/CUTTING_SILENCES.md` |
| **Building / editing the timeline JSON** — the shape of `settings` + every `clip` field, with examples | `references/TIMELINE_JSON.md` |
| **Tracks & audio** — z-order, the mandatory V↔A audio pairing, mixing / ducking levels, one continuous music track | `references/TRACKS_AND_AUDIO.md` |
| **Frame rate / size** — fps & dimension inheritance, and matching the platform aspect ratio | `references/FPS_AND_ASPECT.md` |
| **Transitions** — when a soft edge is warranted vs the hard-cut default | `references/TRANSITIONS.md` |
| **Subtitles** — when to add them and where the segments come from | `references/SUBTITLES.md` |
| **A talking-head / piece-to-camera source** — the full cut-and-punch-in playbook | `references/TALKING_HEAD.md` |
| **A brand / logo overlay** — putting a logo on screen when a brand is named | `references/BRAND_LOGO_OVERLAY.md` |

Most videos need several rows at once (e.g. a talking-head cut = cutting + tracks/audio + logo overlay). Read each that applies.

## Common patterns — the sources tell you which one

Most videos fall into one of these four shapes. Identify the pattern from the SOURCES you hold, then it tells you which task rows to combine. These are starting recipes, NOT a fixed sequence — adapt to the actual job.

**A · Trim one source** — you hold ONE long recording to clean up.
- *Types:* talking-head / UGC, interview, screencast, podcast-to-video.
- *Do:* cut the silences / dead air with trimmed clips of that one source; keep each clip's A-track audio peer in sync; optionally punch-in (`scale`) to break monotony; add subtitles; drop a logo when a brand is named.
- *Read:* `CUTTING_SILENCES` · `TRACKS_AND_AUDIO` · `TALKING_HEAD` (if to-camera) · `SUBTITLES` · `BRAND_LOGO_OVERLAY`.

**B · Concatenate finished clips** — you hold SEVERAL rendered clips (e.g. the storyboard → panels → video flow).
- *Types:* narrative ad / spot, short film, animation, music-video story, generated explainer.
- *Do:* lay the clips back-to-back on V1 in order, each at its OWN duration; add ONE continuous music track on A2 (never per-clip); duck it only under voice; hard cuts by default; pass the platform aspect.
- *Read:* `TIMELINE_JSON` (build it in one `update_timeline`) · `TRACKS_AND_AUDIO` · `FPS_AND_ASPECT` · `TRANSITIONS`.

**C · Montage of media** — you hold a SET of images and/or short clips + a music track.
- *Types:* travel / vlog, event (wedding, conference, party recap), slideshow, product / e-commerce / demo, highlights / sizzle reel, corporate brand film.
- *Do:* place the media in order with per-item durations; ONE music bed on A2; soft transitions or beat-synced cuts; a slow `scale` (Ken-Burns) on stills so they're not static; captions / lower-thirds.
- *Read:* `TIMELINE_JSON` · `TRACKS_AND_AUDIO` · `TRANSITIONS` · `FPS_AND_ASPECT` · `SUBTITLES`.

**D · Vertical social short** — an OVERLAY on any of A–C, not a separate source shape.
- *Types:* Reel / TikTok / Short.
- *Do:* build as 9:16; open on a hook; quicker cuts; big on-screen captions; hard cuts (+ whoosh SFX), never uniform crossfades.
- *Read:* `FPS_AND_ASPECT` (9:16) · `TRANSITIONS` · `SUBTITLES` — on top of whichever of A–C the sources dictate.

## The two rules that never bend (whatever the type)

1. **Cut with TRIMMED clips of the SAME source, never new files** — drop bad takes / dead air by trimming, not by re-encoding or generating new clips. → `references/CUTTING_SILENCES.md`
2. **Assembly ENDS by showing the timeline, not rendering it.** Finish with `show_timeline({ id })` — pass the id from `create_timeline`, nothing else. (On the koi/CLI surface the tool is `show_result({ resourceType: "timeline", timelineId })`.) Render to a flat mp4 ONLY when the user explicitly asks to export / download.

## Address & edit a timeline

- **It's the `id`** from `create_timeline` (`{ success, id, timeline }`). Every tool takes that `id`. You already have it from the response — never hunt for the timeline on disk. Lost it? `recall_creations({ kind: 'timeline' })` → `inspect_creation(id)`.
- **Edit by working the JSON:** `get_timeline` → transform the whole object → `update_timeline` (one atomic write covers any edit, however big). It's a LIVE artefact, so re-read the current state right before every edit. A single trivial one-clip tweak (mute, nudge) can use a unitary tool (`update_clip` / `move_clip` / `trim_clip` / `set_clip_volume`); anything multi-clip → the read-JSON → `update_timeline` path. → shape + examples in `references/TIMELINE_JSON.md`.

## Tools

`create_timeline` · `add_clip_to_timeline` (auto-probes fps/dims on the first video clip) · `get_timeline` / `update_timeline` (read / write whole state) · `set_clip_volume` · `set_clip_transition` · `add_subtitles_to_timeline` · `move_clip` / `trim_clip` / `update_clip` / `remove_clip` · `add_track` / `remove_track` · `show_timeline` (open the editor — the finish) · `render_timeline` (export to mp4, only on request).

## Don't

- Create NEW `.mp4` files to cut a source, or `ffmpeg concat` to glue clips — trim the SAME source and let the timeline stitch (rule 1; `CUTTING_SILENCES.md`).
- Render (or "generate the video") as the finish — assembly ends at `show_timeline({ id })`; render only on an explicit export request (rule 2).
- Open a timeline by passing its `id` as a FILE PATH, or hunt for its `.json` on disk — `show_timeline` takes the bare `id` and resolves it for you (passing the id as a path opens `<cwd>/tl-…` → PathNotFoundException).
- Hunt for the timeline on disk (`shell` / `find` / `ls` / `read_file` on `.koi/timelines/`), or re-derive a path from the `id` — use the `id`; read state with `get_timeline`.
- `read_file` a timeline to inspect it — that RENDERS it to a video; use `get_timeline` for the structure.
- Hand-edit the `.json` with `edit_file` / `write_file` — `update_timeline` is the edit path.
- Drive a multi-clip edit as a long chain of unitary calls — compose the whole state once, `update_timeline` once.
- Leave a video clip that has sound without its paired A-track clip → silent video (`TRACKS_AND_AUDIO.md`).
- Pass `fps` / `width` / `height` to `create_timeline` / `render_timeline` as defensive defaults — breaks inheritance (black flicker / bands; `FPS_AND_ASPECT.md`).
- Let music drown the voice — or duck music that has NO voice over it (decide from the actual audio; `TRACKS_AND_AUDIO.md`).
- Per-clip music in multi-clip assemblies — one continuous track on A2 (`TRACKS_AND_AUDIO.md`).
- Generate clips in 16:9 for a 9:16 target and hope the timeline reframes — it letterboxes; pass `aspectRatio` upstream (`FPS_AND_ASPECT.md`).
