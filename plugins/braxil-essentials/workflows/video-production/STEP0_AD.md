# Step 0 — Build the form for **type = ad**

Use this file when 0a (in `WORKFLOW.md`) resolved `type=ad`. Build a single
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
| 1 | Duration | select + free-text | Any whole-second value. Suggested presets for ads: 15s (recommended) / 30s / 60s. Free-text accepts ANY whole-second number (8s, 20s, 25s, 90s, 2 min, …) — no quantization, no rounding, no upper cap (per WORKFLOW.md Hard Rule #1). Long videos just become more sheets spliced on the timeline. |
| 2 | Platform | select + free-text | Reels / TikTok / Shorts / YouTube / Web / Instagram feed. Determines aspect ratio at render (9:16 / 16:9 / 1:1 / 4:5). MANDATORY. |
| 3 | Style | select + free-text | Premium 3D / Claymation / Realistic UGC / POV. See `STYLE_PRESETS.md`. |
| 4 | Product name | text | Brand name + product name if relevant. Required when product-mode=named. |
| 5 | Product photos | **file picker** | Logo, packaging, hero product shots. Multiple files allowed. iPhone formats accepted. |
| 6 | Brand vibe / audience | text, optional | "Who's it for and what should they feel? — e.g. premium, accessible, fun, trusted." Feeds the BRAND NOTES footer column on the sheet. |
| 7 | Character | text, optional | Brief description if a person appears. Reference goes in field 9. |
| 8 | Setting | text, optional | Brief description. Reference goes in field 9. |
| 9 | References | **file picker** | Catch-all for talent / setting / mood-board / other references not covered by the Product photos field. Empty answer is allowed. |

## When the form is empty

If 0a + ROUTING CONTEXT together resolved every field except References, skip
`prompt_form` entirely and call `prompt_files` for the references attachment.
Do not build a one-row form just to satisfy the references rule.

## Downstream behavior for ad

- **Pacing:** punchy, 1–2 s frames. Frame counts in `VIDEO_TYPE_AD.md`.
- **Captions:** imperative, verbs-only (`"Open."` / `"Pour."`). Short.
- **Footer column 4:** `🎯 BRAND NOTES` — sourced from field 5 (Brand vibe).
- **Audio:** music track at the timeline stage, foley emphasis on hero shot;
  voiceover only if the ad has an explicit hook line. See `VIDEO_TYPE_AD.md`.

Cross-references: `VIDEO_TYPE_AD.md` (full pacing / footer / audio spec for ad)
and `STYLE_PRESETS.md` (style option phrasing).
