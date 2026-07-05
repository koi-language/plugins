# Quick Start — A 30-Second Explainer

This walks through a full end-to-end interaction for the most representative case: a **30-second explainer with one sheet of 8 frames** at variable durations. It shows the conversation flow, the `prompt_form` call, the `generate_image` prompt, the per-frame `generate_video` calls and the timeline assembly.

A second example at the bottom shows a **45-second ad split into 3 sheets of 10 frames** (the multi-sheet case).

---

## Setup

The user has just typed:

> *"Hazme un video explicativo corto sobre la app Superbloom. Algo de 30 segundos, estilo realista."*

The agent classifies → workflow match: `create-video`. Routes via `run_workflow("create-video")`.

---

## Step 0 — Gather inputs

What the user gave:
- type → **explainer** ✓
- duration → **30 s** ✓
- topic → **Superbloom app** (named product) ✓
- style → realistic → **Realistic UGC** ✓ (the closest preset; confirm in the form)

What's missing:
- product mode (named product is implicit since they named "Superbloom" — confirm with a yes/no)
- character (does the explainer feature a person?)
- setting (where does it happen?)
- references (always ask)

ONE `prompt_form` call with these 4 fields:

```yaml
actionType: direct
intent: prompt_form
title: "Just a few details for your 30s Superbloom explainer"
fields:
  - name: personOnScreen
    label: "Does the explainer feature a real person on screen, or is it voiceover + UI only?"
    type: select
    options: ["Person on screen", "Voiceover + UI only"]
  - name: setting
    label: "Where does it take place?"
    type: text
    placeholder: "e.g. living room, café, walking outdoors"
  - name: stylePreset
    label: "Confirm style"
    type: select
    options: ["Realistic UGC (recommended)", "Premium 3D Animation", "Claymation", "POV-Style"]
  - name: references
    label: "Reference images (product, person, location). Optional — you can skip."
    type: files
```

User answers:
- Person on screen → **Person on screen**
- Setting → **kitchen counter in the morning**
- Style → **Realistic UGC**
- References → drops `superbloom_app_screenshot.png` (the UI to show in close-ups)

---

## Step 1 — Light plan

```
> Got it. Here's the plan for your 30-second Superbloom explainer:
>
> 1. **Type:** Explainer, 30 seconds
> 2. **Topic:** How the Superbloom app helps you start your morning
> 3. **Style:** Realistic UGC (phone-shot, kitchen morning light)
> 4. **Character:** A real person on camera, casual morning vibe
> 5. **Setting:** Kitchen counter, morning daylight
> 6. **Product handling:** Named product → "Superbloom" + UI close-ups
>    pull from `superbloom_app_screenshot.png` you attached.
> 7. **Sheet plan:** 1 sheet, 7 frames at varied durations:
>    3s + 4s + 5s + 5s + 4s + 5s + 4s = 30 s
> 8. **Arc:**
>    1. Wake up & reach for phone (3s) →
>    2. Open Superbloom (4s) →
>    3. See today's morning plan (5s, UI close-up) →
>    4. First task: hydrate, fill a glass (5s) →
>    5. Check off the task (4s, UI close-up) →
>    6. Move to the next task — stretch (5s) →
>    7. Close-up of the day's progress ring filling (4s)
>
> Want me to show the full panel-by-panel breakdown (labels, captions,
> icons, voiceover lines) before I build the visual storyboard, or shall
> I go ahead and build it?
```

User: *"go ahead"*.

---

## Step 4 — Build the visual storyboard

The prompt the agent builds (NOT shown to user):

```
Create a single landscape (16:9) storyboard reference sheet for a
30-second video titled "SUPERBLOOM MORNING ROUTINE" with the subtitle
"TOTAL VIDEO TIME: 30 SECONDS" centered at the top.

═══════════════════════════════════════════════
OVERALL LAYOUT
═══════════════════════════════════════════════
- Warm cream/beige background, clean modern design.
- Top-left: small circular hero thumbnail of a phone with the
  Superbloom app open, framed by sunlit kitchen tiles.
- Top-right: legend box (rounded rectangle) with 4 icons in 2×2 grid:
    • Phone icon = DEVICE
    • Tap icon = ACTION
    • Clock = TIME HINT
    • Checkmark = TASK COMPLETE

═══════════════════════════════════════════════
SECTION DIVIDER
═══════════════════════════════════════════════
One black horizontal banner above the grid:
    "PART 1 — A MORNING WITH SUPERBLOOM (7 frames · 30 s total)"

═══════════════════════════════════════════════
FRAME GRID (2 rows × 4 columns, last cell empty)
═══════════════════════════════════════════════
Each frame is a rounded white card with subtle shadow containing:
- Number circle in top-left
- ALL-CAPS label next to the number
- Duration tag "Xs" in top-right (PER-FRAME, varies)
- 1–2 small legend icons below the label
- Central illustration
- Short imperative caption at the bottom
- Optional voiceover line in italic grey below the caption, in the
  form '> [VO] "line"'

CHARACTER: A woman in her late 20s, soft hair tied back, wearing a
relaxed beige sweater. Same person across every frame.
SETTING: A bright kitchen with white tiles, wooden cutting board on
the counter, morning sunlight coming from a window on the left. Same
kitchen across every frame.

FRAMES:
1. WAKE UP — 3s — icons:[Phone, Clock] — caption:"Morning starts soft."
   illustration: medium close-up of the woman on a pillow, reaching for
   her phone on the bedside table, soft morning light through window
   blinds.
   > [VO] "Mornings used to feel rushed."

2. OPEN APP — 4s — icons:[Phone, Tap] — caption:"Tap to begin."
   illustration: over-the-shoulder shot of her hand tapping the
   Superbloom app icon on a phone home screen; reference the actual
   app icon from `superbloom_app_screenshot`.
   > [VO] "Until I started opening Superbloom first thing."

3. TODAY'S PLAN — 5s — icons:[Phone] — caption:"Your day, ready."
   illustration: tight close-up of the phone screen showing
   Superbloom's morning plan UI exactly as in `superbloom_app_screenshot`
   — a vertical list of three tasks with green progress dots on the
   left. No hand in frame, just the phone screen filling 80% of the
   card.
   > [VO] "It builds my morning around three small wins."

4. FIRST TASK — 5s — icons:[Action] — caption:"Hydrate first."
   illustration: the woman at the kitchen counter, filling a glass of
   water from a tap, sunlit kitchen tiles behind her, phone propped
   against the wall showing the same UI.
   > [VO] "Hydration. Stretch. A real breakfast."

5. CHECK OFF — 4s — icons:[Tap, Checkmark] — caption:"Tap. Done."
   illustration: close-up of her thumb tapping a green checkmark on
   the Superbloom UI; the task row animates from grey to green. Pull
   the row layout from `superbloom_app_screenshot`.

6. NEXT TASK — 5s — icons:[Action] — caption:"Stretch counts."
   illustration: medium shot of the woman doing a gentle morning
   stretch in the kitchen, same outfit, same lighting, phone visible
   on the counter behind her.
   > [VO] "It nudges, it doesn't push."

7. PROGRESS RING — 4s — icons:[Checkmark, Clock] — caption:"Whole day, started."
   illustration: extreme close-up of the phone screen — a circular
   progress ring filling from 0 to full, the Superbloom logo at the
   center. No hand in frame.
   > [VO] "By 8am, my day has already begun."

Invariant: 3 + 4 + 5 + 5 + 4 + 5 + 4 = 30 seconds.

Shot mix: frames 1, 4, 6 are character action; frames 2, 3, 5, 7 are
phone/UI close-ups (heavier on UI, matches explainer guidance in
VIDEO_TYPE_EXPLAINER.md for SaaS topics).

═══════════════════════════════════════════════
FOOTER (4 columns with icons)
═══════════════════════════════════════════════
🎬 VIDEO FLOW: "7 frames varying 3–5 s. Smooth cuts on voiceover
breaks, hard cuts on action. Builds toward the progress-ring reveal."
📷 CAMERA TIPS: "Mix medium and close-ups. Over-the-shoulder for
action frames. Tight phone screens for UI frames. Hand-held feel."
☀️ LIGHT & STYLE: "Soft morning daylight from window left. Warm
neutral palette. Lived-in kitchen aesthetic."
💬 EXPLAINER NOTES: "Audience assumes zero context — show, don't tell.
The one insight: 'Superbloom shapes the first hour'. Voiceover tone:
warm, conversational, one breath per line."

═══════════════════════════════════════════════
VISUAL STYLE
═══════════════════════════════════════════════
Authentic user-generated content aesthetic, shot-on-phone realism,
natural unposed framing, soft available daylight or warm indoor
lighting, slight handheld feel without being shaky, real-person
proportions and natural skin texture, casual everyday clothing and
settings, lifestyle-blogger color palette, modest depth of field,
honest and approachable visual tone, social-media-native framing,
relatable and unfiltered atmosphere.

- Consistent main subject across all frames
- Cohesive color palette appropriate to the topic
- Bold sans-serif for titles, lighter sans-serif for captions, italic
  smaller grey for voiceover lines
- Rounded card corners with subtle shadows
- Professional storyboard reference aesthetic
```

The `generate_image` call:

```yaml
actionType: direct
intent: generate_image
prompt: "<the prompt above>"
aspectRatio: "16:9"
resolution: "4K"
outputFormat: png
referenceImages:
  - alias: superbloom_app_screenshot
    path: "<absolute path to the file the user dropped>"
saveTo: "<.koi/sessions/<sid>/storyboards/>"
```

---

## Step 5 — Show and refine

```
> Here's PART 1. Have a look at every frame. Want this version as-is,
> or would you like to refine anything (label, caption, duration,
> voiceover line, icons, or illustration)?
```

The user approves: *"está bien"*.

---

## Step 6 — Generate the final video

7 frames → 7 `generate_video` calls in sequence (parallel works too if the runtime allows it).

Per-frame call for **frame 3** (the longest UI close-up):

```yaml
actionType: direct
intent: generate_video
prompt: |
  Animate panel 3 of `storyboard` (label: "TODAY'S PLAN"). One continuous shot, no cuts. Slow push-in on the phone screen as the three tasks fade in from top. Voiceover line: "It builds my morning around three small wins." — voice is warm, conversational, one breath. No third-person shots. Preserve identity of `superbloom_app_screenshot` exactly (same icons, same colors, same layout).
referenceImages:
  - alias: storyboard
    path: "<path to the approved sheet PNG>"
  - alias: superbloom_app_screenshot
    path: "<the user's reference>"
duration: 5
quality: high
withAudio: true
saveTo: "<.koi/sessions/<sid>/clips/>"
```

Repeat for frames 1, 2, 4, 5, 6, 7 with their respective durations and prompts. Frames without dialogue (frame 5 here) omit the voiceover line.

Then assemble:

```yaml
batch:
  - actionType: direct
    intent: create_timeline
    name: "Superbloom Morning Routine — 30s"
    aspectRatio: "16:9"
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip1>"
    duration: 3
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip2>"
    duration: 4
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip3>"
    duration: 5
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip4>"
    duration: 5
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip5>"
    duration: 4
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip6>"
    duration: 5
  - actionType: direct
    intent: add_clip_to_timeline
    timeline: "<id>"
    path: "<clip7>"
    duration: 4
  - actionType: direct
    intent: add_track
    timeline: "<id>"
    type: music
    prompt: "Soft acoustic morning music bed, low energy, no melodic competition with voiceover, organic instruments."
  - actionType: direct
    intent: render_timeline
    timeline: "<id>"
    saveTo: "<.koi/sessions/<sid>/output/>"
```

Finally `show_result` the rendered MP4.

---

## Multi-Sheet Example — 45-Second Ad

Same workflow, this time the user wants a 45-second ad of fast cuts. The plan in Step 1:

```
> 1. Type: Ad, 45 seconds
> 7. Sheet plan: 30 frames × 1.5s = 45 s → 3 sheets of 10 frames
>    each (PART 1 + PART 2 + PART 3, classic 2×5 grid each)
```

Step 4 runs three times:

1. **Sheet PART 1** — generate with the user's product / character refs only. Show, refine, approve.
2. **Sheet PART 2** — generate with the same product / character refs PLUS `sheet_part_1` as a `referenceImage`. The prompt contains the continuity block from `STORYBOARD_ANATOMY.md`. Show, refine, approve.
3. **Sheet PART 3** — same again, this time with `sheet_part_1` AND `sheet_part_2` as `referenceImages`. Show, refine, approve.

Step 6: 30 per-frame `generate_video` calls (each frame's `sheet_alias` points at its source sheet — `sheet_part_1` for frames 1–10, `sheet_part_2` for frames 11–20, `sheet_part_3` for frames 21–30). Single timeline, 30 clips, one music track added at the end.

That's the multi-sheet flow.

---

## Common Pitfalls (Read Before Building Anything)

1. **Forgetting `aspectRatio: "16:9"` / `resolution: "4K"` / `outputFormat: "png"` on `generate_image`** — the sheet renders at default ~1K, captions blur, and the per-frame `generate_video` calls read a pixelated brief. The hard rule lives in `WORKFLOW.md`; obey it.
2. **Re-describing the panels inside the per-frame `generate_video` prompt** — the sheet does it for you. Per-frame prompts must be ≤ 6 lines and meta-only.
3. **Skipping the continuity block on sheets 2+** — even with `sheet_part_1` in `referenceImages`, the model needs the prose instruction to actually preserve identity. Pass both.
4. **Splitting at frame 11 just because the cap allows it** — split at narrative beats, not at index boundaries.
5. **Using a different legend on sheet 2** — the legend is frozen at sheet 1. Same 4 icons, same placement, same captions.
6. **`withAudio: false` on a frame that has a `[VO]` dialogue line** — the line is in the sheet but won't be voiced; the model renders silent video. Match the flag to the slot.
7. **Forgetting the invariant after a refinement** — when the user changes a frame's duration, another frame has to absorb the delta. Re-validate `sum === total` before re-generating.
