# The timeline JSON shape (for `update_timeline`) + worked examples

The exact structure you build / transform when you edit a timeline by working the JSON
directly (`get_timeline` → transform → `update_timeline`, the default and fastest path for
any non-trivial edit). This is the authoritative shape; keep it in sync with
`koi/src/runtime/state/timelines.js` (the `_validateClip` validator, the `_passthrough`
list, `_validateTransition`, `_validateTitleProps`, `_validateVolumePoints`, and settings
validation).

## Read / write contract

- `get_timeline(id?)` returns `{ id, name, version, settings, clips }`. No args needed for
  the timeline the user has open (defaults to the active document).
- `update_timeline({ id, state: { settings, clips } })` — `state` MUST contain `settings`
  and `clips`; the `id` comes from the param, **not** from `state`.
- **Start from what `get_timeline` returned** and change only what you need. Include only the
  fields you actually set — omitted optional fields default sensibly, so don't invent values.
  Leave view-only fields exactly as they came back.
- `tracks` are **not** a top-level array. They are implicit from the settings counts plus
  each clip's `track` field. The format is deliberately flat so an LLM can merge / diff /
  regenerate a whole timeline in one write.

Never hand-edit the on-disk `.json` with `edit_file` / `write_file` — `update_timeline` IS
the "edit the JSON" path, minus the risk of a malformed write breaking the visor.

> **What survives an `update_timeline`.** The write keeps: the required fields, the trim
> fields, `linkId`, and everything in the field reference below (all of it round-trips).
> A handful of GUI-only fields do **NOT** round-trip and are silently dropped if you send
> them — `opacity`, `blur`, `sourceFps`, `timelineRefName`. Don't rely on setting those
> here; they're maintained by the GUI.

## `settings`

```json
{
  "projectFps": 30,
  "projectWidth": 1080,
  "projectHeight": 1920,
  "videoTracks": 2,
  "audioTracks": 2,
  "activeVideoTrack": "V1",
  "activeAudioTrack": "A1",
  "pixelsPerSecond": 100,
  "previewSplit": 0.5,
  "playheadMs": 0,
  "trackHeight": 64,
  "shotCutVersion": 0
}
```

- `projectFps` / `projectWidth` / `projectHeight` — **inherited from the first video clip**
  (see `FPS_AND_ASPECT.md`). Do NOT change them unless the user wants a different render shape.
- `videoTracks` / `audioTracks` — counts (1–10). Tracks V1..Vn and A1..An exist implicitly
  from these counts; a clip's `track` must fall within them.
- View-only fields (`pixelsPerSecond` 10–400, `previewSplit` 0.1–0.9, `playheadMs`,
  `trackHeight`, `activeVideoTrack`, `activeAudioTrack`, `shotCutVersion`) — leave EXACTLY as
  `get_timeline` returned them. They are GUI state, not render state.

## `clips[]` — full field reference

### Required (every clip)
| Field | Type | Notes |
|---|---|---|
| `id` | string | `"clip-<hex8>"`. KEEP existing ids when editing; mint a fresh unique one for a NEW clip. Never regenerate a valid id. |
| `track` | string | `"V1"`/`"V2"`/`"A1"`/`"A2"`… V-tracks stack (higher = on top), A-tracks all mix. Must be within the settings counts. `title:` and `timeline:` clips are V-track only. |
| `path` | string | Absolute source file, or a sentinel: `"title:<id>"` (title card), `"timeline:<id>"` (nested timeline), `"placeholder-image:<n>"` / `"placeholder-video:<n>"` / `"placeholder-audio:<n>"` (AI placeholder awaiting generation). |
| `startMs` | int | Position ON THE TIMELINE, ms (≥ 0). |
| `durationMs` | int | Visible length, ms (≥ 50). |

### Trim — place a SEGMENT of a source (how you cut / drop silences)
| Field | Type | Notes |
|---|---|---|
| `sourceInMs` | int | Where IN THE SOURCE this clip starts (ms; 0 = from the top). |
| `sourceTotalMs` | int | The source's true length (ms); keep accurate so a trim never runs past the end. `0` = unknown / not applicable (images, titles). |

### Audio & linking
| Field | Type | Notes |
|---|---|---|
| `linkId` | string \| null | Shared id pinning a V clip to its auto-paired A peer (move / trim / remove together). Keep it consistent between the two. `null` = unlinked. |
| `hasAudio` | bool | Whether the clip feeds the mix. `false` on the V clip when its A peer carries the sound (avoids double-mix), and on genuinely silent layers (images, titles). |
| `volumePoints` | array | Gain automation: `[{ "t": ms, "v": gain }]`. `t` in `[0, durationMs]`, `v` linear gain in `[0, 2]`. See `TRACKS_AND_AUDIO.md`. |

### Visual transform (per clip; only persist when non-default, to keep the JSON clean)
| Field | Type | Default | Notes |
|---|---|---|---|
| `scale` | double | 1.0 | Zoom factor (1.0 = fit, 1.15–1.3 = punch-in, 2.0 = 2×). |
| `offsetX` / `offsetY` | double | 0 | Re-frame after a zoom so the subject stays centred. **A FRACTION OF THE CANVAS, not pixels** — `0` = centred, `+0.5` = shifted half a canvas right / down, `-0.5` = half left / up. Keep it small (roughly `-0.3…0.3`). ⚠️ A value ≥ 1 (e.g. writing pixels like `-40`) pushes the clip entirely off-frame → the clip renders **BLACK**. To nudge N pixels, divide by the canvas size: N px up on a 1920-tall canvas = `offsetY: -N/1920` (e.g. 40 px → `-0.02`). |
| `rotation` | double | 0 | Degrees. |
| `transformEnabled` | bool | — | Master toggle for the free-transform block. |
| `featherPx` / `featherSides` | double / int | 0 | Edge feather (amount / which sides bitmask). |
| `cornerRadiusPx` | double | 0 | Rounded corners (PiP / overlays). |
| `shadowBlurPx` / `shadowColorArgb` | double / int | 0 | Drop shadow. `…Argb` is a packed ARGB int. |
| `hue` / `saturation` / `brightness` / `contrast` | double | neutral | Colour grade. |
| `sourceWidthPx` / `sourceHeightPx` | int | probed | Source native pixel size (stamped on add). |
| `aspectW` / `aspectH` | double | — | AI placeholder canvas aspect — drives the rendered crop rectangle. Round-trip verbatim on AI clips. |

### Transitions
`transitionIn` / `transitionOut` — object `{ type, durationMs, alignment?, params? }`.
`transitionIn` fires at the clip's `startMs`; `transitionOut` at its end. At a join between
two adjacent clips, the outgoing clip's `transitionOut` defines the cross-effect (otherwise
the next clip's `transitionIn` wins). `durationMs` ≥ 50 and ≤ half the clip's `durationMs`.

- **`type`** (one of): `crossfade`, `fade-black`, `fade-white`, `dissolve`, `slide-left`,
  `slide-right`, `slide-up`, `slide-down`, `wipe-left`, `wipe-right`, `wipe-up`, `wipe-down`,
  `circle-open`, `circle-close`, `pixelize`, `zoom-in`, `radial`.
- **`alignment`** (one of, default `center`): `center`, `start-on-cut`, `end-on-cut`.
- **`params`** — optional free object passed through to the renderer.

See `TRANSITIONS.md` for when to use which.

### Title clips — `titleProps`
A title clip has no real file: `path` is `"title:<id>"` and the text/typography live in a
sibling `titleProps` object. Title clips are V-track only.

| `titleProps` field | Type | Notes |
|---|---|---|
| `text` | string | **Required.** The rendered text. |
| `fontFamily` | string | |
| `fontSize` | number | |
| `colorArgb` | int | Packed ARGB fill colour. |
| `fontWeight` | int | e.g. 400 / 700. |
| `align` | int | 0 = left, 1 = center, 2 = right (GUI enum). |
| `italic` | bool | |
| `outlineWidth` / `outlineColorArgb` | number / int | Text outline. |
| `shadowBlur` / `shadowColorArgb` | number / int | Text shadow. |

### AI clips — `aiState`
A clip generated (or awaiting generation) by AI carries `aiState`. Round-trip it verbatim;
do not fabricate it. Shape:

| `aiState` field | Type | Notes |
|---|---|---|
| `placeholderPath` | string | **Required.** The original `placeholder-image:/video:/audio:<n>` sentinel the clip carried before generation. |
| `lastRenderedPath` | string | Most recent successful generation result (null until one completes). |
| `lastPrompt` | string | Prompt text last submitted for this clip. |
| `lastAttachments` | string[] | File paths submitted with `lastPrompt`. |
| `lastChatId` | string | Chat session that ran the last generation. |
| `placeholderSourceInMs` | int | The clip's `sourceInMs` at the moment it was switched to AI. |

Related top-level clip fields for AI keyframe wiring (round-trip verbatim):
`aiStartFrameClipId`, `aiEndFrameClipId`, `aiStartFrameMode`.

### 🚨 SWAPPING a clip's `path` (replacing a clip with a re-rendered / edited version) — RESET THE SOURCE WINDOW

**Whenever you point an existing clip at a DIFFERENT media file — an AI edit of that clip, a re-render, a swapped take — you MUST also reset the source window in the same write:**

```jsonc
"path": "<the new file>",
"sourceInMs": 0,        // the new file is STANDALONE and starts at 0
"sourceTotalMs": 0,     // unknown → let the app re-probe the real length
"sourceWidthPx": 0,     // unknown → re-probe (the render may have other dims)
"sourceHeightPx": 0
```

**Why — this is a 100%-reproducible freeze if you skip it.** `sourceInMs` is an offset into the **OLD** source. A re-rendered clip is a brand-new file that begins at 0, so the old offset now points somewhere inside (or past) it. Real reported case: a clip trimmed as the tail of a 7142 ms take (`sourceInMs 3250` + `durationMs 3892`) had its `path` swapped to the 3752 ms rendered edit while `sourceInMs` stayed `3250` → the player seeked 3250 ms into a 3752 ms file, leaving ~500 ms of content for a 3892 ms clip, and **froze on the last frame for the remaining ~3.4 s**. The timeline looked right; playback was broken.

Also mind these, in the same edit:
- **`durationMs` vs the new file's real length.** If the render came back shorter than the slot (asked 3892 ms, got 3752 ms), the tail is a frozen frame. Either shorten `durationMs` to the real length (and close the gap / ripple the rest yourself — it moves everything after it), or accept the short freeze deliberately. Never leave it unnoticed.
- **The linked AUDIO peer** (same `linkId`): decide explicitly whether it follows the new file (swap its `path` and reset its `sourceInMs` too) or keeps the ORIGINAL audio (leave it — its own `sourceInMs`/`durationMs` still refer to the old source and stay valid). Both are legitimate; silently half-updating them is not.
- **`aiState`**: set `lastRenderedPath` to the new file and keep `placeholderPath` / `placeholderSourceInMs` untouched — they describe the ORIGINAL, and the inspector's "AI ↔ Rendered" toggle needs them to restore it.

ℹ️ The `assign_generated_media_to_clip` tool already does all of the above for you — **prefer it** over hand-editing the JSON for this case. This section is for when you're rewriting the object yourself via `update_timeline`.

### Other
| Field | Type | Notes |
|---|---|---|
| `shotCuts` | int[] | Detected shot-cut points inside the source, in SOURCE-ms (the clip's "tomas"; read by `extract_take`). Round-trip verbatim. |

---

## Worked examples (one per clip type)

### 1. Video clip cut into two trimmed segments (drop the middle), each with its audio peer
Keep 0–4 s and 9–15 s of one source; the 4–9 s fluff is simply not placed. The source has
audio, so each V clip gets an A1 peer at the SAME start / duration / sourceIn, linked, and
the V clip is `hasAudio:false`.

```json
{
  "id": "<timelineId>",
  "state": {
    "settings": { "projectFps": 30, "projectWidth": 1920, "projectHeight": 1080,
                  "videoTracks": 2, "audioTracks": 2 },
    "clips": [
      { "id": "clip-a1", "track": "V1", "path": "/…/take.mp4",
        "startMs": 0, "durationMs": 4000, "sourceInMs": 0, "sourceTotalMs": 15000,
        "linkId": "seg1", "hasAudio": false },
      { "id": "clip-a2", "track": "A1", "path": "/…/take.mp4",
        "startMs": 0, "durationMs": 4000, "sourceInMs": 0, "sourceTotalMs": 15000,
        "linkId": "seg1" },

      { "id": "clip-b1", "track": "V1", "path": "/…/take.mp4",
        "startMs": 4000, "durationMs": 6000, "sourceInMs": 9000, "sourceTotalMs": 15000,
        "linkId": "seg2", "hasAudio": false },
      { "id": "clip-b2", "track": "A1", "path": "/…/take.mp4",
        "startMs": 4000, "durationMs": 6000, "sourceInMs": 9000, "sourceTotalMs": 15000,
        "linkId": "seg2" }
    ]
  }
}
```

### 2. Static image clip (on V1)
An image has no duration of its own — you pick `durationMs`; `sourceTotalMs` is 0 and it's
silent (`hasAudio:false`). A `scale`/`offset` gives a slow Ken-Burns push if you want one.

```json
{ "id": "clip-img", "track": "V1", "path": "/…/photo.png",
  "startMs": 0, "durationMs": 4000, "sourceInMs": 0, "sourceTotalMs": 0,
  "hasAudio": false, "scale": 1.08 }
```

### 3. Title card (on V2, over the video)
```json
{ "id": "clip-title", "track": "V2", "path": "title:intro-1",
  "startMs": 0, "durationMs": 2500, "sourceInMs": 0, "sourceTotalMs": 0,
  "hasAudio": false,
  "titleProps": { "text": "Chapter One", "fontFamily": "Inter", "fontSize": 96,
                  "fontWeight": 700, "align": 1, "colorArgb": 4294967295,
                  "outlineWidth": 3, "outlineColorArgb": 4278190080 } }
```

### 4. Music clip with a duck curve (on A2)
One continuous music file sized to the whole video, louder in the 2 s intro then ducked
under the voice via `volumePoints`.

```json
{ "id": "clip-music", "track": "A2", "path": "/…/score.mp3",
  "startMs": 0, "durationMs": 30000, "sourceInMs": 0, "sourceTotalMs": 30000,
  "volumePoints": [ { "t": 0, "v": 0.25 }, { "t": 2000, "v": 0.04 },
                    { "t": 27000, "v": 0.04 }, { "t": 30000, "v": 0.25 } ] }
```

### 5. Clip with transitions (cross-dissolve in, fade to black out)
```json
{ "id": "clip-hero", "track": "V1", "path": "/…/hero.mp4",
  "startMs": 0, "durationMs": 8000, "sourceInMs": 0, "sourceTotalMs": 8000,
  "hasAudio": false,
  "transitionIn":  { "type": "dissolve",   "durationMs": 400, "alignment": "center" },
  "transitionOut": { "type": "fade-black", "durationMs": 600, "alignment": "end-on-cut" } }
```

### 6. Logo / image overlay (on V2, with a cross-dissolve out)
A transparent PNG painting over V1 for 3 s, scaled down and offset toward the top-right
corner (see `BRAND_LOGO_OVERLAY.md`). Offsets are canvas FRACTIONS — `0.35` right and
`0.38` up put it in a corner; pixel values like `380` would fly it off-screen (BLACK).

```json
{ "id": "clip-logo", "track": "V2", "path": "/…/brand_logo.png",
  "startMs": 3000, "durationMs": 3000, "sourceInMs": 0, "sourceTotalMs": 0,
  "hasAudio": false, "scale": 0.25, "offsetX": 0.35, "offsetY": -0.38,
  "cornerRadiusPx": 12,
  "transitionOut": { "type": "dissolve", "durationMs": 400, "alignment": "end" } }
```

### 7. AI clip (placeholder awaiting generation)
Before generation, the clip points at a placeholder sentinel and carries `aiState` with the
prompt. After a successful render the `path` becomes the rendered file and
`aiState.lastRenderedPath` is set — but `aiState` stays. Round-trip it verbatim.

```json
{ "id": "clip-ai1", "track": "V1", "path": "placeholder-video:0",
  "startMs": 0, "durationMs": 5000, "sourceInMs": 0, "sourceTotalMs": 0,
  "hasAudio": false, "aspectW": 9, "aspectH": 16,
  "aiState": { "placeholderPath": "placeholder-video:0",
               "lastPrompt": "slow dolly-in on a neon-lit alley at night, rain",
               "lastAttachments": [] } }
```

### 8. Nested timeline clip (compose a timeline inside another)
A sub-timeline is placed by its `timeline:<id>` sentinel on a V-track; it carries its own
A-tracks internally and is expanded at playback time.

```json
{ "id": "clip-sub", "track": "V1", "path": "timeline:tl-9f3a2c1b",
  "startMs": 0, "durationMs": 12000, "sourceInMs": 0, "sourceTotalMs": 12000 }
```

---

If your edit reports success the user sees it on the next paint; if it failed, the visor
won't change — surface the failure, don't claim success.
