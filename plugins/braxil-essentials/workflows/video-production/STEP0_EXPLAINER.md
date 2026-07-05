# Step 0 — Build the form for **type = explainer**

Use this file when 0a (in `WORKFLOW.md`) resolved `type=explainer`. Build a single
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
| 1 | Duration | select + free-text | Any whole-second value. Suggested presets for explainers: 30s (recommended) / 45s / 60s — short ones rarely fit the narration. Free-text accepts ANY whole-second number (20s, 25s, 90s, 2 min, …) — no quantization, no rounding, no upper cap (per WORKFLOW.md Hard Rule #1). Long videos just become more sheets spliced on the timeline. |
| 2 | Platform | select + free-text | Reels / TikTok / Shorts / YouTube / Web / Instagram feed. Determines aspect ratio at render (9:16 / 16:9 / 1:1 / 4:5). MANDATORY. |
| 3 | Style | select + free-text | Premium 3D / Claymation / Realistic UGC / POV. See `STYLE_PRESETS.md`. |
| 4 | Concept to explain | text | The takeaway in ≤ 2 sentences. What should the viewer understand after watching? |
| 5 | Narrator | text, optional | Brief description if a person delivers the explanation on camera. Leave blank for voiceover-only. |
| 6 | Narrator reference | **file picker**, optional | Only if field 5 has a person. Photo of the narrator. iPhone formats accepted. |
| 7 | Setting | text, optional | Brief description. Reference goes in field 8. |
| 8 | References | **file picker** | Catch-all for setting, product diagrams, brand visuals, mood-board, anything else. Empty answer is allowed. |

## When the form is empty

If 0a + ROUTING CONTEXT together resolved every field except References, skip
`prompt_form` entirely and call `prompt_files` for the references attachment.

## Downstream behavior for explainer

- **Pacing:** narrated, 3–5 s frames. Frame counts in `VIDEO_TYPE_EXPLAINER.md`.
- **Captions:** didactic, descriptive. Full sentences allowed.
- **Footer column 4:** `💬 EXPLAINER NOTES` — sourced from field 3 (Concept).
- **Audio:** voiceover narration over light music. `withAudio: true` per frame
  when the narrator has a line. See `VIDEO_TYPE_EXPLAINER.md`.

Cross-references: `VIDEO_TYPE_EXPLAINER.md` (full pacing / footer / audio spec for explainer)
and `STYLE_PRESETS.md` (style option phrasing).
