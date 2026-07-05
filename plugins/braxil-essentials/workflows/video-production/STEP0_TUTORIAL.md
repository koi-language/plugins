# Step 0 — Build the form for **type = tutorial**

Use this file when 0a (in `WORKFLOW.md`) resolved `type=tutorial`. Build a single
`prompt_form` call with the fields below. **Skip any row already resolved** —
either by 0a (the user wrote the value verbatim) or by ROUTING CONTEXT (the
routing agent already picked it). Never re-ask resolved fields, not even as
a pre-checked default.

All labels, questions, hints, and option titles stay in English regardless of
the user's chat language (Hard Rule #5).

**Read the current `prompt_form` schema first** with `get_tool_info("prompt_form")`.
This file describes WHAT each field collects; never paste literal JSON property
names from memory.

## Fields (in order; omit any already resolved)

| # | Field | Kind | Notes |
|---|---|---|---|
| 1 | Duration | select + free-text | Any whole-second value. Suggested presets for tutorials: 60s (recommended) / 90s / 2 min — tutorials need room for the steps. Free-text accepts ANY whole-second number (45s, 3 min, …) — no quantization, no rounding, no upper cap (per WORKFLOW.md Hard Rule #1). Long videos just become more sheets spliced on the timeline. |
| 2 | Platform | select + free-text | Reels / TikTok / Shorts / YouTube / Web / Instagram feed. Determines aspect ratio at render (9:16 / 16:9 / 1:1 / 4:5). MANDATORY. |
| 3 | Style | select + free-text | Premium 3D / Claymation / Realistic UGC / POV. See `STYLE_PRESETS.md`. |
| 4 | Subject being taught | text | What's being taught? App, tool, technique, recipe, exercise, etc. |
| 5 | Setup screenshots / photos | **file picker** | Screenshots of the app / packaging / setup photos. Used as references when rendering. Empty allowed only if the subject is purely conceptual. |
| 6 | End state | text, optional | What should the viewer be able to do after watching? |
| 7 | Instructor | text, optional | Brief description if a person appears on camera. |
| 8 | Setting | text, optional | Brief description. |
| 9 | References | **file picker** | Catch-all for instructor refs, setting, mood-board, anything else not covered by field 5. Empty answer is allowed. |

## When the form is empty

If 0a + ROUTING CONTEXT together resolved every field except References, skip
`prompt_form` entirely and call `prompt_files` for the references attachment.

## Downstream behavior for tutorial

- **Pacing:** step-by-step, 4–6 s frames so viewers can read along.
  Frame counts in `VIDEO_TYPE_TUTORIAL.md`.
- **Captions:** instructive. Often paired with a step number ("Step 1 — …").
- **Footer column 4:** `📚 INSTRUCTOR NOTES` — sourced from field 5 (End state)
  plus inline tips per step.
- **Audio:** voiceover instructions; music kept low. See `VIDEO_TYPE_TUTORIAL.md`.

Cross-references: `VIDEO_TYPE_TUTORIAL.md` (full pacing / footer / audio spec for tutorial)
and `STYLE_PRESETS.md` (style option phrasing).
