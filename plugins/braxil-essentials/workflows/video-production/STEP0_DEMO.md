# Step 0 — Build the form for **type = demo**

Use this file when 0a (in `WORKFLOW.md`) resolved `type=demo`. Build a single
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
| 1 | Duration | select + free-text | Any whole-second value. Suggested presets for demos: 30s (recommended) / 45s / 60s. Free-text accepts ANY whole-second number (8s, 20s, 90s, 2 min, …) — no quantization, no rounding, no upper cap (per WORKFLOW.md Hard Rule #1). Long videos just become more sheets spliced on the timeline. |
| 2 | Platform | select + free-text | Reels / TikTok / Shorts / YouTube / Web / Instagram feed. Determines aspect ratio at render (9:16 / 16:9 / 1:1 / 4:5). MANDATORY. |
| 3 | Style | select + free-text | Premium 3D / Claymation / Realistic UGC / POV. See `STYLE_PRESETS.md`. |
| 4 | Product name | text | Brand name + product name. Required — demo without a product makes no sense. |
| 5 | Product photos | **file picker** | Logo, packaging, hero shots, feature close-ups. Multiple files allowed. iPhone formats accepted. |
| 6 | Key features to demo | text | 2–5 features the demo must show, one per line. Drives which frames get built. |
| 7 | Presenter | text, optional | Brief description if a person uses / shows the product. |
| 8 | Setting | text, optional | Where is the product used? Brief description. |
| 9 | References | **file picker** | Catch-all for presenter refs, setting, brand visuals, anything else not covered by field 5. Empty answer is allowed. |

## When the form is empty

If 0a + ROUTING CONTEXT together resolved every field except References, skip
`prompt_form` entirely and call `prompt_files` for the references attachment.

## Downstream behavior for demo

- **Pacing:** product-in-use, 2–3 s frames. Frame counts in `VIDEO_TYPE_DEMO.md`.
- **Captions:** declarative ("Tap to pair." / "Charges in 90 minutes.").
- **Footer column 4:** `🛠️ PRODUCT NOTES` — sourced from field 5 (Key features).
- **Audio:** voiceover or SFX-only; product sounds emphasised. See `VIDEO_TYPE_DEMO.md`.

Cross-references: `VIDEO_TYPE_DEMO.md` (full pacing / footer / audio spec for demo)
and `STYLE_PRESETS.md` (style option phrasing).
