# Step 0 — Build the form for **type = social-post**

Use this file when 0a (in `WORKFLOW.md`) resolved `type=social-post`. Build a single
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
| 1 | Duration | select + free-text | Any whole-second value. Suggested presets for social: 15s (recommended) / 30s / 60s — social skews short. Free-text accepts ANY whole-second number (8s, 20s, 90s, …) — no quantization, no rounding, no upper cap (per WORKFLOW.md Hard Rule #1). Long videos just become more sheets spliced on the timeline. |
| 2 | Platform | select + free-text | TikTok / Instagram Reels / YouTube Shorts / Generic vertical. Confirms 9:16 reframe at render. |
| 3 | Style | select + free-text | Premium 3D / Claymation / Realistic UGC / POV. See `STYLE_PRESETS.md`. |
| 4 | Hook | text | ≤ 1 sentence — the first 2-second grab. Drives the opening frame. |
| 5 | Topic / payoff | text | What the rest of the post is about. Required when not resolved by 0a. |
| 6 | Talent | text, optional | Brief description if a person appears (creator-style POV is common in this format). |
| 7 | Setting | text, optional | Brief description. |
| 8 | References | **file picker** | Catch-all for talent refs, brand visuals, mood-board, anything else. Empty answer is allowed. |

## When the form is empty

If 0a + ROUTING CONTEXT together resolved every field except References, skip
`prompt_form` entirely and call `prompt_files` for the references attachment.

## Downstream behavior for social-post

- **Pacing:** rhythmic, 1–2 s frames synced to a beat. Frame counts in
  `VIDEO_TYPE_SOCIAL_POST.md`.
- **Captions:** punchy, often emoji-friendly. The hook is FRAME 1.
- **Footer column 4:** `📱 CHANNEL NOTES` — sourced from field 4 (Hook) +
  field 2 (Platform) conventions.
- **Audio:** music-driven, often no voiceover. Sound is added at the timeline
  stage on a single track. See `VIDEO_TYPE_SOCIAL_POST.md`.
- **Aspect ratio:** the storyboard sheet stays 16:9; per-frame `generate_video`
  calls reframe to 9:16 based on field 2.

Cross-references: `VIDEO_TYPE_SOCIAL_POST.md` (full pacing / footer / audio spec for social-post)
and `STYLE_PRESETS.md` (style option phrasing).
