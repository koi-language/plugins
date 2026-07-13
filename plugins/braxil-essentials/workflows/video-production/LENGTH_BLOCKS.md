# Length Blocks — Multi-Sheet & Final Render Pipeline

> ⚠ **All numeric duration ranges in this file are ILLUSTRATIVE snapshots, NOT the source of truth.** Per WORKFLOW.md Hard Rule #18, the live per-sheet `[D_min, D_max]` comes from `get_tool_info("generate_video")` at runtime. Today's typical values happen to be `D_min = 4`, `D_max = 15` (and the worked examples below use those), but the tool's reported range overrides any literal you see here. If the tool reports a different range tomorrow, the math still works — just substitute the new `D_min` / `D_max` into the formulas.

This file documents two things:

1. **How to map a total duration to one or more panel sheets**, given the per-sheet caps from `STORYBOARD_ANATOMY.md`.
2. **The render pipeline** for the final video — the chain of `generate_video` + timeline calls that stitches per-frame clips into the final file.

> 📍 Files referenced below by bare name — `STORYBOARD_ANATOMY.md` and any `VIDEO_TYPE_<TYPE>.md` — are owned by the **`visual-panels` skill** and live in its `references/` directory (NOT next to this file). To read one: `list_skills` → the `visual-panels` entry's `directory` → `read_file` `<directory>/references/<file>`. The actual sheet-chunking logic also lives in that skill (SKILL.md § STEP B); the duration→sheet-count table below is the create-video workflow's quantized view of it.

---

## 🧱 The Caps

**Per-sheet duration: 4–15 seconds.** Each sheet renders as one `generate_video` call. The engine accepts whole-second `duration` values in the [4, 15] range; that's the per-sheet floor and ceiling. Sheet duration is NOT fixed at 15 — it's whatever the narrative needs, within [4, 15].

**Per-sheet panel cap: at most 10 panels.** Beyond 10 the sheet becomes illegible at 4K — panels shrink, captions blur, legend icons go unreadable. 10 panels in a 15-second sheet is the original "classic" 2×5 ad anatomy.

**Total video duration: ANY whole-second value ≥ 4 s. NO upper cap.** Per WORKFLOW.md Hard Rule #1: 20 s, 33 s, 90 s, 2 hours — all fine. They just become more sheets spliced on the timeline.

**Sheet count: minimum N such that `N × 15 ≥ total_duration`** — i.e. `sheet_count = ceil(total_duration / 15)`. So 20 s → 2 sheets; 33 s → 3; 90 s → 6; 7200 s (2 h) → 480.

---

## 🪓 Splitting Into Sheets

Given a `total_duration`, compute `sheet_count = ceil(total_duration / 15)`, then distribute the seconds across the sheets — each in [4, 15], summing exactly to `total_duration`. The split is **narrative-driven**, not mechanical.

1. **Each sheet ends on a narrative beat** (act boundary, transition, reveal) — never fade out mid-action. Pick the split points that make the story land cleanly.
2. **Each sheet's duration is in [4, 15].** A 17 s total cannot be 15 + 2 (2 s is below the floor); use 9 + 8, 10 + 7, 12 + 5, etc. Whenever an "obvious" split would leave a sub-4 s sheet, rebalance so every sheet is ≥ 4 s.
3. **Balance is a default, not a rule.** A 30 s explainer can be 15 + 15 if the narrative splits evenly, or 12 + 18 — wait, 18 > 15, so it'd actually be 12 + 15 + 3 (rebalance: 10 + 10 + 10). The right split is the one that matches the script's act structure.
4. **Panel numbers continue across sheets.** Sheet 1's panels are `1..N1`; sheet 2's are `N1+1..N1+N2`; etc.
5. **The legend box is frozen at sheet 1** and reused identically on every later sheet (see `STORYBOARD_ANATOMY.md` § Zone 2).
6. **The header title is constant** across sheets (e.g. `"SUPERBLOOM MORNING ROUTINE"`); only the banner divider changes (`PART 1`, `PART 2`, …).
7. **The footer chrome is constant**; only the per-column copy may shift per PART.

---

## 📊 Reference — Duration to Sheet Count

`sheet_count = ceil(total_duration / 15)`. The per-sheet durations are then distributed narratively (each 4–15 s, summing to total). A few worked totals so the shape is concrete:

| Total duration | Sheet count | Example split (narrative-driven — many other valid splits exist) |
|---|---|---|
| 8 s | 1 | 8 |
| 15 s | 1 | 15 |
| 20 s | 2 | 10 + 10  •  12 + 8  •  15 + 5 |
| 25 s | 2 | 13 + 12  •  15 + 10 |
| 30 s | 2 | 15 + 15  •  12 + 18 → ❌ (18 > 15)  →  10 + 10 + 10 (3 sheets) when the story has 3 acts |
| 33 s | 3 | 11 + 11 + 11  •  15 + 13 + 5  •  12 + 12 + 9 |
| 45 s | 3 | 15 + 15 + 15  •  12 + 18 → ❌ → 14 + 16 → ❌ → 15 + 15 + 15 or 13 + 16 → ❌ → use 15 + 15 + 15 / 12 + 17 → ❌ — basically respect the ≤15 cap |
| 60 s | 4 | 15 + 15 + 15 + 15  •  12 + 12 + 18 → ❌ — keep each ≤ 15 |
| 90 s | 6 | 15 × 6  •  12 + 12 + 18 → ❌ — typically 15 + 15 + 15 + 15 + 15 + 15, or finer-grained per the story |
| 7200 s (2 h) | 480 | 15 × 480 (or finer per narrative; rare in practice — confirm with the user that they understand the cost/wait) |

Within each sheet, panel count is driven by the video type's pacing heuristic within the 1–10 panels range. The pacing numbers live ONLY in the per-type spec — read the matching file (`VIDEO_TYPE_AD.md` / `VIDEO_TYPE_EXPLAINER.md` / `VIDEO_TYPE_TUTORIAL.md` / `VIDEO_TYPE_DEMO.md` / `VIDEO_TYPE_SOCIAL_POST.md`) once you know the type. The mapping between user wording and `type` slug is the §"Per-type spec routing" table in `WORKFLOW.md`.

---

## 🧮 Worked Examples

### 12 s ad
- Type: **ad** (1.5–2 s/panel)
- **1 sheet × 12 s**: 8 panels × 1.5 s = 12 s.

### 20 s explainer (the case that triggered removing the quantization rule)
- Type: **explainer** (3–5 s/panel)
- **2 sheets**, narrative-split as **12 + 8**:
  - PART 1 (12 s): 3 panels (4 + 4 + 4)
  - PART 2 (8 s): 2 panels (4 + 4) — landing on the resolution beat
- Sheet 2 receives sheet 1 as `referenceImages: [{ alias: "sheet_part_1", path: ... }]`.

### 25 s tutorial
- Type: **tutorial** (4–6 s/panel)
- **2 sheets**, split as **13 + 12**:
  - PART 1 (13 s): 3 panels (5 + 4 + 4) — setup + first task
  - PART 2 (12 s): 3 panels (4 + 4 + 4) — second task + CTA

### 30 s ad
- Type: **ad** (1.5–2 s/panel)
- **2 sheets × 15 s**:
  - PART 1: 10 panels × 1.5 s
  - PART 2: 10 panels × 1.5 s
- Sheet 2 receives sheet 1 as `sheet_part_1`.

### 45 s demo
- Type: **demo** (2–3 s/panel)
- **3 sheets × 15 s**:
  - PART 1–3: 6 panels × 2.5 s each
- Sheets 2 and 3 receive every prior approved sheet.

### 90 s explainer
- Type: **explainer** (3–5 s/panel)
- **6 sheets × 15 s** (could also be 7 sheets of varying durations if the script begs for it):
  - PART 1–6: 4 panels × 3.75 s each
- Each subsequent sheet receives ALL prior approved sheets as references.

### 60 s social post (TikTok-style)
- Type: **social-post** (1.5–2 s/panel)
- **4 sheets × 15 s**:
  - PART 1–4: 10 panels × 1.5 s
- Each subsequent sheet receives ALL prior approved sheets as references.
- At render time, the timeline reframes 16:9 → 9:16 for the final social-post output.

---

## 🔁 Cross-Sheet Consistency Rules

When generating sheet K (K ≥ 2), the `generate_image` call MUST include:

1. All approved earlier sheets in `referenceImages`, each with alias `sheet_part_<j>`:
   ```
   referenceImages: [
     { alias: "sheet_part_1", path: "<path-to-sheet-1.png>" },
     // …repeat for sheet 2, …, K-1
     // …followed by any user-attached subject refs (product, character,
     //  setting) with their semantic aliases
   ]
   ```
2. A continuity block in the prompt (full text in `STORYBOARD_ANATOMY.md` § Multi-Sheet Continuity Block) that says, in essence:
   - "Preserve EXACTLY from `sheet_part_1`: character face/build/hair/wardrobe, setting, lighting direction, palette, render style, legend box (identical 4 icons in identical placement), footer chrome (titles unchanged)."
   - "Only change in PART K: frame labels, captions, dialogue lines, illustrations, the banner divider's PART K label, and the frame numbers."

Both are required. Passing the reference image without the continuity block leads the model to riff on the style; writing the continuity block without the reference image leaves it nothing to copy.

**Refinement loop applies to every sheet independently.** If the user requests changes on sheet 2, re-generate sheet 2 with the SAME `referenceImages` payload (sheet 1 still there) and the SAME continuity block. Do not regenerate sheet 1 unless the user explicitly asks.

---

## 🎬 The Final Render Pipeline

> 📍 **The authority for the final-render pipeline is now the `visual-panels-to-video` skill** (`list_skills` → its `directory` → SKILL.md). It supersedes the algorithm sketch below in one important way: **per-clip duration is the sheet's OWN duration** (the whole-second 4–15 value the storyboard assigned that PART — taken from the storyboard JSON when present), NOT a fixed 15 s. The timeline concatenates clips back-to-back at each clip's own duration (cumulative cursor), not at fixed 15 s slots. The sketch below is the original equal-15 s-sheet view; follow the skill for the real, variable-duration behaviour.

After every sheet is approved, run the final-render step: **one `generate_video` call per sheet** (NOT per panel), then stitch the sheet-clips on a timeline.

### Algorithm

```
# Inputs come from <runWorkspaceDir>/step5_output.json:
sheets                  # list with sheet_path, sheet_index, panels[], dialogue_lines
total_duration_seconds  # 15 / 30 / 45 / 60
type                    # ad | explainer | tutorial | demo | social-post
audio_plan              # voiceover-music | voiceover-only | music-only | sfx-only
platform / aspect_ratio # 16:9 | 9:16 | 1:1 | 4:5

# ── 1. Per-sheet video clips ────────────────────────────────────────
# Music-exclusion line is added to the prompt ONLY when stitching >=2
# sheets and the audio plan includes music — otherwise per-clip music
# would cause audible discontinuities at the 15s seams. For a single-
# sheet video (N=1) there are no seams; music inside the clip is fine.
multi_sheet_music = (len(sheets) >= 2) and (audio_plan in {"voiceover-music", "music-only"})

clips = []
for sheet in sheets:
    sheet_alias = "storyboard" if len(sheets) == 1 else f"sheet_part_{sheet.sheet_index}"

    # For sheet K >= 2, include EVERY prior approved sheet so the model can
    # preserve identity / wardrobe / lighting / setting from sheet 1 onward.
    references = [{ alias: sheet_alias, path: sheet.sheet_path }]
    for prior in sheets[: sheet.sheet_index - 1]:
        references.append({ alias: f"sheet_part_{prior.sheet_index}", path: prior.sheet_path })
    references.extend(user_subject_refs)  # product, character, setting refs

    clip_path = generate_video(
        prompt = build_per_sheet_prompt(sheet, sheet_alias,
                                        exclude_music = multi_sheet_music),
        referenceImages = references,
        duration = 15,
        quality = "high",
        withAudio = sheet.has_dialogue OR audio_plan starts with "voiceover",
        saveTo = <project clips dir>
    )
    clips.append({ path: clip_path, duration: 15, sheet_index: sheet.sheet_index })

# ── 2. Single music track for the whole video (ONLY ONE call) ───────
# Only generated when multi-sheet AND audio plan includes music. For
# single-sheet videos music (if any) was baked into the clip render in
# step 1, so we don't lay a second track here.
music_path = None
if multi_sheet_music:
    music_path = generate_audio(
        type = "music",
        duration = total_duration_seconds,   # full length, no seams
        prompt = <music brief derived from VIDEO_TYPE_<TYPE>.md's "Audio cue" section + plan tone>,
        saveTo = <project audio dir>
    )

# ── 3. Build the timeline ───────────────────────────────────────────
timeline_id = create_timeline(
    name = "<video-title>",
    aspectRatio = aspect_ratio,   # from step5_output.json, NOT hardcoded
)

# Video track — concatenate sheet clips at 15s each.
cursor_ms = 0
for clip in clips:
    add_clip_to_timeline(
        timeline = timeline_id,
        track = "V1",
        path = clip.path,
        startMs = cursor_ms,
        durationMs = 15_000,
    )
    cursor_ms += 15_000

# Music track — single continuous file from step 2.
if music_path:
    add_clip_to_timeline(
        timeline = timeline_id,
        track = "A2",                                  # A1 reserved for voiceover from clips
        path = music_path,
        startMs = 0,
        durationMs = total_duration_seconds * 1000,
    )

# Optional: subtitles on tutorial / explainer.
if type in {"tutorial", "explainer"}:
    add_subtitles_to_timeline(timeline = timeline_id, ...)

# ── 4. Render ───────────────────────────────────────────────────────
render_timeline(timeline = timeline_id, saveTo = <project output dir>)
show_result(...)
```

**Hard rules:**
- ONE `generate_video` call per SHEET (not per panel).
- Per-clip music exclusion applies ONLY when stitching ≥ 2 sheets. For a single-sheet (15 s) video, music inside the clip is fine — there are no seams to worry about.
- When multi-sheet + music is needed: ONE `generate_audio` call for the FULL music track (not per clip, not per sheet).
- `create_timeline` is the ONLY assembly path. Never `ffmpeg concat` or any other glue tool.
- `aspectRatio` comes from the platform field resolved in Step 0 — never default to 16:9 blindly.

**Number of `generate_video` calls = sheet count = `total_duration / 15`.** A 30 s video → 2 calls. A 60 s video → 4 calls. NEVER one call per panel — that is the bug this pipeline exists to prevent.

### Per-Sheet Prompt Template (the minimal one)

```
Animate the full 15-second sequence storyboarded in `<sheet_alias>`,
panel by panel in order, honoring each panel's duration tag exactly.
One continuous video; the panel transitions are cuts within the same clip.

[if sheet has dialogue / voiceover lines, listed in panel order]
Voiceover lines (deliver in panel order, natural pacing):
  panel <N1> — "<line 1>"
  panel <N2> — "<line 2>"
  ...

[only for sheet_index >= 2 in a multi-sheet video]
Preserve character / wardrobe / lighting / palette / setting EXACTLY
from `sheet_part_1` — this is PART <K> of a multi-PART video.

[optional identity lock, only when user attached subject refs]
Preserve identity of `hero_character` and `product_pack` exactly.

[optional negative guidance the sheet can't express]
No text overlays beyond what the sheet's captions show.
No camera zoom unless the panel illustration implies it.
```

Pass `duration: 15` — never a per-panel duration. The model reads the panel durations FROM the sheet image (each panel has a per-panel duration tag rendered into the pixels) and paces the 15-second clip accordingly.

### Why per-sheet, not per-panel

The render engine can produce 15 seconds in a single call when given the panel sheet as a reference. Running one call per panel multiplies the number of API calls by 5–10× without improving the result — and worse, it breaks cross-panel continuity because each call sees only its single panel's framing.

Per-sheet is the right granularity:
- **One render = one 15-second beat block** = one sheet. Matches the user's storyboard mental model.
- **Cross-panel continuity is preserved** because the model sees the whole sheet.
- **Dialogue / voiceover flows naturally** across the 15-second sequence instead of being chopped into per-panel renders that need to be stitched without seams.
- **Cross-sheet continuity** (for 30 / 45 / 60 s videos) is handled by passing prior sheets as `referenceImages` on each sheet K ≥ 2.
- **Stitching is cheap** at the timeline stage — N sheet-clips concatenated, plus music / subtitles / reframe (16:9 → 9:16 for social).

---

## 🚫 What This Pipeline DOES NOT Do

- **No automatic music selection.** Music is added by an explicit `add_track` call after `add_clip_to_timeline`. The music prompt comes from the per-type `VIDEO_TYPE_<TYPE>.md`'s "Audio cue" section + the user's tone description.
- **No automatic transition styling.** Cuts are hard by default. Soft transitions (cross-fade, slide) are added per-clip via `set_clip_transition` when the type warrants it (explainer often, ad rarely, social-post never except for whooshes).
- **No automatic VO speaker voice.** The `withAudio: true` on per-frame calls produces a default voice. To use a specific voice (`@narrator`, `@tom`), pass that handle into the per-frame `generate_video` call's prompt — the runtime resolves it via `@`-handles.
- **No frame-rate / codec tuning.** The render uses the defaults of `render_timeline`. If the user needs a specific output (e.g. H.265 4K, 60 fps), pass those parameters to `render_timeline` explicitly.

Anything above is out of scope for this workflow and belongs in a follow-up post-production pass.
