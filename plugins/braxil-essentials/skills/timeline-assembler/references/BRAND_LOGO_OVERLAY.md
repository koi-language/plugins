# Brand / logo overlays (show a transparent logo while a brand is named)

Whenever a video mentions / talks about a brand, put that brand's **logo on
screen at the exact moment it's spoken**, as a clean transparent overlay. This is
the canonical how-to; any skill or reference that says "show the brand logo"
points here.

It's part of the timeline edit — the logo is just one more clip in the `clips`
array, so add it in the same `update_timeline` as the rest (see the main skill).

## 1. Find the real logo — on the web

Search the web for the OFFICIAL logo of that exact brand, preferably a
**transparent PNG** (`"<brand> logo transparent png"`). Take the clean, current,
official mark — not a fan art, not an old version, not a screenshot with
background.

## 2. Verify it IS the right logo — always, before using it

**MUST:** `read_file` the candidate image to actually SEE it and confirm it's the
correct brand's logo (right brand, current design, clean, not cropped, not a
look-alike). Never drop a logo you haven't looked at — using the wrong / mangled
logo of a real brand is a serious mistake. If you're not sure it's the right one,
find a better source; don't guess.

## 3. Ensure it's transparent

- Already a **transparent PNG** → perfect, use it as is.
- Has a solid/white/coloured background (jpg, or a png with a box behind it) →
  run **`background_removal`** to cut it out to transparency FIRST. Never place a
  logo sitting inside a visible rectangle over the footage — it must float on the
  frame with no background.

## 4. Choose WHERE it goes — and check contrast against the actual frame

The logo sits in a corner / side where it reads cleanly: **top-right, top-left,
bottom-right, bottom-left**, or wherever it contrasts best. It must NOT cover the
speaker's face or the main action.

**Contrast matters — look at the real frame.** A coloured or dark logo needs a
lighter area behind it (and vice-versa). To be sure, **extract the frame where
the logo will appear** (`extract_frame` / `extract_take`) and `read_file` it,
then pick the corner with the best contrast for THIS logo. If no corner
contrasts well, the subtle shadow in step 5 (or a very faint scrim) lifts it off
the frame.

## 5. Place it — image clip, ABOVE the video, zoom-in → hold → dissolve-out

Add the logo as an **image clip on a track ABOVE the main video** (`V2` or
higher, so it paints OVER `V1`), timed to the brand mention, **≤ 5 s** total:

- `track`: `"V2"` (or higher if V2 is busy) — never on V1, it must overlay.
- `path`: the transparent logo PNG. `startMs`: the moment the brand is named.
  `durationMs`: ≤ 5000.
- **Enter with a zoom:** `transitionIn: { type: "zoom-in", durationMs: 320 }` — it
  pops in scaling up.
- **Leave with a dissolve fade:** `transitionOut: { type: "dissolve", durationMs: 450 }`
  (or `"crossfade"`) — it fades away, never a hard cut off.
- **Subtle shadow** so it lifts off the frame: `shadowBlurPx: 12` (small/soft) +
  `shadowColorArgb: 0x66000000` (≈40% black). Keep it subtle — a drop shadow, not
  a heavy glow.
- **Size + position:** scale it to read but not dominate, and place it in the
  chosen corner via `offsetX` / `offsetY` (and `scale` for size). Leave a
  comfortable margin from the edge.

Result: as the brand is named, its logo tastefully zooms in the corner, holds a
couple of seconds with a soft shadow, and dissolves away — never covering the
subject, always the correct, verified, transparent mark.
