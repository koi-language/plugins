---
name: video-production
description: "Create a NEW video FROM SCRATCH (blank canvas) — when the user has only an IDEA/brief (\"make me a video about X\", \"un anuncio de Y\", \"explainer sobre Z\") and there is no storyboard yet. Runs the full pipeline: idea → storyboard → visual sheets → final video, any whole-second duration ≥ 4 s with NO upper cap (long videos just become more sheets spliced together), any type (ad, explainer, tutorial, demo, social post, dialogue scene). DO NOT activate this workflow when the user ALREADY HAS an artifact and just wants to transform it — those are single SKILL tasks, delegate to a worker, NOT this workflow: (a) convert an existing storyboard → visual panel sheets = the `visual-panels` skill; (b) render a video from an existing visual panels = the `visual-panels-to-video` skill; (c) edit/author an storyboard = the `storyboard` skill; (d) animate a SINGLE image, or produce ONE short single-shot clip = direct video generation (image-to-video / `generate_video`), NOT this workflow. SCOPE: this workflow (and the storyboard as its first step) is ONLY for videos with MULTIPLE shots / an actual story or script — never for a single shot or for animating one image. If a 'make a video' brief is AMBIGUOUS about scope (could be a single shot / animating one image vs. a multi-shot story), ASK the user before launching this workflow rather than assuming it. Triggers (blank-canvas MULTI-SHOT / story video creation only): make a multi-shot/story video, create a video, generate a video, quiero un video, hazme un video (con varios planos / una historia), un anuncio, explainer video, tutorial video, demo video, social post video, video about <topic>. NON-triggers (do NOT match): \"pasa este storyboard a visual\", \"convierte el storyboard\", \"haz el video de este storyboard\", \"renderiza este storyboard\" (→ use the skill); \"anima esta imagen\", \"haz un shot corto de…\", a single clip / one-shot (→ direct video generation); or any request that starts from an existing storyboard/sheet."
---

## 🎯 What You Build

A two-stage pipeline:

1. **One or more 16:9 4K visual panel sheets** (built by the `visual-panels` skill), each containing a variable-frame grid that describes the video shot-by-shot. The sheet's anatomy is documented in `STORYBOARD_ANATOMY.md`.
2. **The final video** (built by the `visual-panels-to-video` skill) — generated as N short clips (ONE per sheet, NOT per frame), each at the duration the storyboard assigned that PART, then concatenated on a timeline so the pacing the user signed off on is honored exactly.

**Key difference from the older 15-second ad workflow:** frames are not fixed at 10 × 1.5s. The number of frames and the duration of each are decided by the narrative — a dialogue beat may be 5s, a montage cut 0.8s, an establishing shot 3s. The only invariant is `sum(frame_durations) === total_video_duration`. See `LENGTH_BLOCKS.md` for the per-sheet caps and the multi-sheet consistency rules.

Companion files are the source of truth — consult them as needed.

> 📍 **Where the visual-sheet references live.** The sheet anatomy, the style presets and the per-type specs are owned by the **`visual-panels` skill** — they are NOT siblings of this WORKFLOW.md anymore. They live in that skill's `references/` directory. To read one, get the skill's absolute `directory` (Step 2 activates `visual-panels` and the activation returns `directory` + `resources`; in earlier steps call `list_skills` and read the `directory` of the `visual-panels` entry), then `read_file` `<that directory>/references/<file>`. NEVER hardcode `~/.koi/skills/...` — in a dev checkout the skill resolves to the plugin repo path.

**Visual-sheet references** (owned by the `visual-panels` skill — read from its `references/` dir as the steps mention them):
- `STORYBOARD_ANATOMY.md` — exact spec of every part of a sheet
- `STYLE_PRESETS.md` — the 4 official visual style presets (Premium 3D / Claymation / Realistic UGC / POV)
**Per-type specs** (in the same `visual-panels/references/` dir — read ONLY the one matching the resolved `type` slug from Step 0 — never all five; each file is the single source of truth for its type's pacing, captions, dialogue, footer column 4, audio cue and mix):
- `VIDEO_TYPE_AD.md` — fires when `type == "ad"`
- `VIDEO_TYPE_EXPLAINER.md` — fires when `type == "explainer"`
- `VIDEO_TYPE_TUTORIAL.md` — fires when `type == "tutorial"`
- `VIDEO_TYPE_DEMO.md` — fires when `type == "demo"`
- `VIDEO_TYPE_SOCIAL_POST.md` — fires when `type == "social-post"`

The mapping between user wording and `type` slug lives in §"Per-type spec routing" below.

**Workflow-local files** (siblings of this WORKFLOW.md):
- `LENGTH_BLOCKS.md` — duration→sheet-count quantization, multi-sheet split, cross-sheet consistency, final render pipeline
- `QUICK_START.md` — an end-to-end example for a 30-second explainer

**Per-type Step 0 forms** (read ONLY the one matching the resolved `type` in Step 0):
- `STEP0_AD.md`
- `STEP0_EXPLAINER.md`
- `STEP0_TUTORIAL.md`
- `STEP0_DEMO.md`
- `STEP0_SOCIAL.md`

---

## 🚦 Hard Rules

1. **Total duration is the USER'S CHOICE, any whole-second value ≥ `D_min`. NO UPPER CAP — a 2-hour video is just more clips spliced together.** Where `D_min` is the per-sheet minimum reported by `get_tool_info("generate_video")` (see Hard Rule #18 — NEVER hardcode it). No quantization, no rounding. If the user asks for 20 s, the answer is "OK, 20 s" — NOT "let's round to 15 or 30". The workflow splits any total into the minimum number of sheets needed, each sized within the tool-reported `[D_min, D_max]` range, summing exactly to the requested total. So a 20 s total (with today's typical `D_max = 15`) → 2 sheets (e.g. 10 + 10, or 12 + 8, or 15 + 5 — narrative-driven). 40 s → 3 sheets. 90 s → 6 sheets. 7200 s (2 h) → ~480 sheets. The user never has to think in fixed blocks. For very long requests (≥ 5 min) sanity-check ONCE with the user that they understand the cost/wait implications (each sheet is one `generate_video` call), but do NOT refuse or cap.
2. **`sum(panel_durations) === sheet's own duration` for EVERY sheet, AND `sum(sheet_durations) === total_video_duration`.** Per-sheet duration is variable (within the tool-reported `[D_min, D_max]`, see Hard Rule #18); it's NOT fixed. Both invariants are non-negotiable. Validate before generating the sheet AND before generating the video.
3. **Per-panel duration: min 1 s, max equal to the tool-reported `D_max`.** Below 1 s the sheet becomes an unreadable slideshow; above `D_max` a single panel can't render in one `generate_video` call.
4. **Per-sheet caps: tool-reported `[D_min, D_max]` AND at most 10 panels.** The duration floor/ceiling come from `get_tool_info("generate_video")` (Hard Rule #18); the 10-panel cap is for sheet readability at 4K — beyond 10, panels shrink and captions blur. Each sheet sums to its OWN clip duration, distributed across 1–10 panels of variable duration. For totals > `D_max`, split into multiple sheets — sheet 2 onwards MUST receive sheet 1 as a `referenceImage` named `sheet_part_1` (and same for sheets 3, 4, …) so style / character / setting stay consistent across PARTs. See `LENGTH_BLOCKS.md` for the split-into-sheets heuristic.
5. **English only** — captions, dialogue lines, sheet text, footer copy, **AND every `prompt_form` / `prompt_user` / `prompt_files` field label, helper text, option label and placeholder**. The user-facing chat reply stays in the user's language; everything else (sheet contents, form UI strings) is English regardless of the language the user is writing in.
6. **Always plan before building.** Never assume. Never skip Step 0.
7. **Sheets first, video second.** Never emit `generate_video` before the user has approved every sheet.
8. **No long product descriptions.** When a real product is involved, use the product name + a short `[REFERENCE IMAGE OF {PRODUCT}]` placeholder — never a paragraph.
9. **You invent the icons per topic.** No icon library. Pick 4 conceptually-fitting icons for the legend (matching the topic), 1–2 per frame. The same 4 legend icons repeat across every sheet of a multi-sheet video.
10. **NEVER invent the topic, character, product, setting, or references.** If the user only said "make me a video" without specifying, stop and ask (Step 0). Reference images and `@`-handles must come from the user in THIS conversation — never from `recall_memory` or the cross-project library unless the user explicitly named them.
11. **Every `generate_image` call for a sheet MUST carry `aspectRatio: "16:9"`, `resolution: "4K"` (fallback "2K" only if "4K" is rejected), `outputFormat: "png"`, AND `label: "visual_storyboard"`.** Omitting any of these is a SHIP-STOPPER — without `4K` the sheet renders at default ~1K and captions go illegible; without `label: "visual_storyboard"` the router falls back to the generic image bucket and the panel grid comes back at thumbnail quality.
12. **Every `generate_video` call MUST carry `referenceImages`** with at least the frame's source sheet as the first entry (alias `storyboard` or `sheet_part_N`). Writing prose like "use the attached storyboard" without populating `referenceImages` does nothing — the model can't see what you don't pass.
13. **Cross-sheet consistency on multi-sheet videos: sheets 2…N MUST receive sheet 1 as a `referenceImage` named `sheet_part_1`** (and any other already-approved earlier sheets) so the character / wardrobe / lighting / setting stay locked across PARTs. See `LENGTH_BLOCKS.md`.
14. **Every intermediate / process file goes inside the `Workflow workspace` from RUNTIME CONTEXT** — `step5_output.json`, scratch JSON, transient outputs, anything the workflow produces that isn't the final deliverable. Construct the path as `<Workflow workspace>/<filename>` using the ABSOLUTE value of the `Workflow workspace` row from your RUNTIME CONTEXT table — never a relative path, never a path derived from where WORKFLOW.md lives, never the plugin source directory. Writing into the plugin source tree (e.g. `plugins/plugins/video-production/workflows/...`) is a hard failure: the workspace is auto-permissioned, the plugin tree is not.
15. **The storyboard-refinement task is a MULTI-TURN HUMAN CONVERSATION, not a one-shot job. It ends with `prompt_user`, NEVER with `return` — until the user explicitly picks "Looks good — generate the visual sheets" on a `prompt_user` you emitted.** The task name might read like "author the storyboard JSON" but the assigned worker's contract is: write the JSON, `show_result` it, then sit in a `prompt_user` loop (option set: *"Refine it"* / *"Looks good — generate the visual sheets"*). Each iteration ends with another `prompt_user`. The ONLY turn that emits `return` is the one in which the user picks "Looks good"; that `return` carries the storyboard path payload. Emitting `return` after `show_result` (or after a refinement edit) hands control back to the coordinator, the workflow auto-advances to Step 2, and the user never gets to refine — **this is the canonical bug this rule exists to prevent. If your task description omits this rule but the work clearly involves refining a storyboard JSON in the visor, apply it anyway — the omission is a planner summary error, not authorization to skip the rule.**
16. **Panel count per sheet MUST stay within the per-type spec's range — at storyboard authoring time (Step 1b), NOT at visual rendering time (Step 2).** Per-type ranges (`VIDEO_TYPE_AD.md`'s "Panels per sheet: 8–10" / `VIDEO_TYPE_EXPLAINER.md`'s "3–5" / `VIDEO_TYPE_TUTORIAL.md`'s "3–4" / `VIDEO_TYPE_DEMO.md`'s "5–7" / `VIDEO_TYPE_SOCIAL_POST.md`'s "8–10") are inputs to the LIGHT PLAN and the JSON authoring — they determine how many shots the storyboard ends up with. Reading the spec is not enough — you must commit to a number INSIDE its range and build the arc with exactly that many shots in the JSON. **For an ad, that means 8–10 shots per 15-second sheet, NEVER 4.** Self-check before showing the plan: if `type == "ad"` and any sheet's arc has fewer than 8 shots, the count is wrong and you re-do it before presenting. Defaulting to "4 shots × 3.75 s" for every type is the bias this rule breaks.

    **At STEP 2 (visual rendering) the per-type range is IRRELEVANT** — the JSON already has the right shot count. The visual sheet renders **one panel per JSON shot, exactly, in order**. Adding panels to "hit the per-type range" or dropping panels to "fit a grid" is the reported bug *"el storyboard interactivo tenía 5 shots y se inventaron 5 más"*. The visual side is a 1:1 projection of the JSON's shots; the per-type range had its say upstream.

17. **🛑 THE TWO MANDATORY ARTIFACTS, IN ORDER, EACH PRODUCED BY ITS DEDICATED SKILL.** This workflow produces EXACTLY two creative artifacts before the final video:

    **(1) The storyboard JSON** — `~/.koi/storyboards/<id>.json`, built by activating the **`storyboard`** skill. This is Step 1b's deliverable, ALWAYS, both fork branches.

    **(2) The visual panel sheet(s)** — 4K PNG images, built by activating the **`visual-panels`** skill. This is Step 2's deliverable, ALWAYS.

    These two skills are NON-NEGOTIABLE. Do NOT substitute either with:
    - A `.md` script / treatment / outline / brief / "video plan" doc.
    - A `.txt` shot list.
    - A `.json` you wrote without activating `storyboard` (the skill body carries the v6 schema, the path convention, character continuity, lighting design and shot vocabulary — guessing the schema produces a file the visor cannot open).
    - A `generate_image` call for the sheet that bypasses `visual-panels` (the skill carries the sheet anatomy, style presets, per-type footers, chunking math and continuity rules — a free-hand `generate_image` produces an off-brand panel grid).

    If you find yourself about to `write_file` something that ends in `.md` (or any non-JSON / non-image extension) as the first artifact of this workflow → STOP. The first artifact MUST be the `storyboard` JSON. The Light Plan from Step 1 is rendered IN CHAT via `prompt_user`'s `message` field — NOT as a file on disk. The user reads it inline and picks the fork.

    `step5_output.json` and other scratch files inside the `Workflow workspace` are infrastructure (handoffs between steps), not creative artifacts — they don't count against this rule.

18. **🛑 NEVER hardcode the per-sheet duration range. ALWAYS query the `generate_video` tool for it.** Call `get_tool_info("generate_video")` at the START of Step 1 (right before computing the sheet plan), pull the `duration` enum's MIN and MAX from the returned schema, and use **those** numbers as the per-sheet floor and ceiling. The supported range evolves as models change — what's 4–15 today may be 3–20 tomorrow, and any number baked into this workflow or any sibling file will drift out of sync silently. Concretely:

    - Compute `sheet_count = ceil(total_duration / D_max)` where `D_max` came from `get_tool_info`.
    - When distributing seconds across sheets, every sheet's duration must satisfy `D_min ≤ duration ≤ D_max` — both bounds read from `get_tool_info`.
    - When a literal range (e.g. "4–15") appears in this workflow's prose or in `LENGTH_BLOCKS.md`'s examples, treat it as an ILLUSTRATIVE snapshot — NOT the source of truth. The tool's reported range overrides any literal you see.
    - Same rule applies to the `storyboard` JSON authoring: every shot's `duration` must fit the model's reported per-shot range.

---

## 🧱 Task decomposition rules (FOR THE WORKFLOW TRANSLATOR)

The workflow translator (an LLM call inside `run_workflow.js`) reads this file and emits a `task_create` list. It treats every `###`-level Step heading as one task. Honour these rules when emitting the list — otherwise the user gets bypassed mid-flow.

### Exactly FIVE tasks, no more, no less

This workflow has FIVE `###`-level steps and they map 1:1 to the tasks you emit:

1. **Step 0 — Gather inputs** → 1 task
2. **Step 1 — Light Plan, storyboard authoring, refinement loop** → 1 task (NOT three — Step 1b and Step 1c are `####`-level sub-sections INSIDE Step 1, they are NOT separate steps).
3. **Step 2 — Build the visual panels(s)** → 1 task
4. **Step 3 — Show and refine the visual panels** → 1 task
5. **Step 4 — Generate the final video** → 1 task

Do NOT create tasks for sub-sections (e.g. "#### Step 1b — Build the storyboard JSON" or "#### Product handling guidance" or "#### Just build it escape hatch"). Those are implementation details handled INSIDE Step 1 by its worker.

### What the Step 1 task description MUST contain

Step 1 is a MULTI-TURN HUMAN CONVERSATION (see Hard Rule #15). When you write its task description, the LAST sentence MUST be (verbatim or equivalent):

> "This task is a multi-turn human conversation. End every turn with `prompt_user`. Emit `return` ONLY on the turn the user picks *'Looks good — generate the visual sheets'* on a `prompt_user` you just emitted — never on the same turn as a `show_result`, never as a 'deliverable' bullet that says 'return the file path', never as a final cleanup step. The storyboard-refinement loop is the contract."

If your draft Step 1 description ends with "1. Write the JSON. 2. show_result. 3. Return the file path." — STOP. That shape collapses Step 1 into a one-shot job and bypasses the user. Re-write it as the multi-turn shape above (light plan → fork → JSON authoring → visor → refinement loop → return only on "Looks good").

---

## 🎯 Per-type spec routing

Pacing / caption tone / dialogue / footer / audio cue / mix differ by video type. They live in five per-type files; nothing is duplicated across them. Once you've resolved the `type` slug in Step 0, `read_file` ONLY the matching one — do not read all five.

| Type slug | Per-type file | User wording that resolves to this type |
|---|---|---|
| **ad** | `VIDEO_TYPE_AD.md` | anuncio / ad / commercial / campaign / spot / brand video / product ad / promo / promotional / paid ad |
| **explainer** | `VIDEO_TYPE_EXPLAINER.md` | explainer / explicativo / explainer video / how it works / como funciona / overview / introduction / intro video / concept video / pitch video / what is X |
| **tutorial** | `VIDEO_TYPE_TUTORIAL.md` | tutorial / how to / step-by-step / como hacer / instructional / guide / walkthrough / lesson / training video / paso a paso |
| **demo** | `VIDEO_TYPE_DEMO.md` | demo / product demo / demostración / showcase / unboxing / hands-on / first-look / review / product video |
| **social-post** | `VIDEO_TYPE_SOCIAL_POST.md` | social / social post / reel / TikTok / Instagram / shorts / story / vertical short / IG video / IG reel / for social / para social / corto |

> **Heuristics, not rules.** The per-type files give starting points for panel count and per-panel duration; the narrative drives the final numbers within each sheet, ALWAYS inside the per-type's panel range (per Hard Rule #16). The invariants are strict — every sheet's panels sum to that sheet's OWN duration (within the tool-reported `[D_min, D_max]`, see Hard Rule #18), sheet count = `ceil(total_duration / D_max)`, panels per sheet ≤ 10 (per Hard Rules #1–4). Those invariants belong to the workflow, not to any one type.

### Custom / other types (dialogue scene, music video, narrative short, …)

For anything outside the 5 above:

1. Ask the user which of the 5 is the **closest fit** (the user picks).
2. `read_file` that per-type file and use it as the base.
3. Adapt the footer column 4 header and the audio cue with the user's explicit confirmation. Example for a dialogue scene:
   - Base: **explainer** (dialogue-driven, slow pacing).
   - Override the column 4 header to `🎭 SCENE NOTES` and the content to talk about the relationship between the characters, the emotional arc, and the tone of the dialogue.
   - Pacing leans toward 4–8 s per frame to let dialogue breathe.
4. Never invent a brand-new column 4 header without showing it to the user first.

---

## 🗣️ The Conversation Flow

### Step 0 — Gather inputs (MANDATORY GATE)

Step 0 is a **two-phase gate**. Phase 0a (resolve what you already know) runs in your head. Phase 0b (build a form for what's still unknown) calls `prompt_form` ONCE. Never re-ask a field 0a resolved — not even as a pre-checked "confirm" default. Confirmation belongs in the Step 1 plan, not in the form.

The 9 fields you need before Step 1: **type, duration, topic, product-mode, style, character, setting, platform, references**.

> ⚠ **Platform is MANDATORY.** It determines the final aspect ratio (16:9 for YouTube / web, 9:16 for Reels / TikTok / Shorts, 1:1 for Instagram feed, 4:5 for Instagram portrait). Without it the video gets rendered in the wrong shape and has to be redone. If the user didn't say where the video goes, ASK.

#### 0prelude — Tell the user the process in ONE short paragraph

**BEFORE** anything else in Step 0 (before 0a, before the form, before `prompt_user` for a missing type) — open with ONE short paragraph in the user's chat language explaining the three-stage process they're signing up for. This sets expectations: the user knows there are TWO review/refinement gates ahead and they won't be blindsided when the workflow shows them a storyboard instead of a video on the first turn.

Content of the paragraph (translate / paraphrase into the user's chat language — never paste literal English):

1. We'll start by building an **storyboard** — *like a comic*: every panel shows the story, the shots and the framing, and the user can edit/refine every part (durations, dialogue, action, camera).
2. From that storyboard we'll generate **visual panels** — 4K sketches of every shot, also tunable before moving on.
3. Finally we'll **animate those panels into the final video**.

**Constraints on the paragraph:**

- ONE paragraph. NOT a bulleted list, NOT two paragraphs, NOT a section header followed by sub-points. Conversational tone.
- The user's chat language (Spanish, English, Portuguese, …) — never English-by-default when the user wrote in another language.
- Do NOT recite the skill names (`storyboard`, `visual-panels`) — those are internal. Speak in product terms ("storyboard", "panels", "video").
- Do NOT enumerate Hard Rules, durations, panel counts, or technical parameters — the user just needs to know there will be a storyboard, a visual sheet, and a final video, with refinement opportunities along the way.
- Emit this paragraph via `print` (or as the leading text of the next `prompt_form` if you batch it together with 0b). It IS the first thing the user sees from this workflow.

**Worked example for a user who wrote in Spanish:**

> *"Para crear el vídeo vamos a pasar por tres fases que podrás revisar y afinar en cada una: primero construimos un **storyboard interactivo** — funciona como un cómic donde ves la historia panel a panel con los planos, la acción y los diálogos, y puedes ajustar cada cosa; después generamos los **paneles visuales** con bocetos a 4K de cada shot, también editables; y por último **animamos esos paneles** para producir el vídeo final."*

**For a user who wrote in English:**

> *"To make the video we'll go through three reviewable stages: first we build an **storyboard** — works like a comic where you see the story panel by panel with the shots, action and dialogue, and you can tweak every part; then we turn that into **visual panels** (4K sketches of every shot, also tunable); and finally we **animate those panels** into the finished video."*

Adapt the wording to the user's tone; the structure (three stages, with the comic / panels / video framing) is what must stay.

#### 0a — Resolve everything you can

**First**, scan the ROUTING CONTEXT block (if the runtime injected one at the top of this task). Anything listed there is GIVEN — treat as resolved. The upstream router has already done some extraction for you.

**Then**, read the user's first message and resolve more fields. Common triggers:

| User wrote (any language) | Resolves |
|---|---|
| anuncio / ad / commercial / spot / promo / paid ad / brand video / product ad | **type=ad** |
| explainer / explicativo / video que explica | **type=explainer** |
| tutorial / cómo hacer / how-to / paso a paso | **type=tutorial** |
| demo / demostración / product demo | **type=demo** |
| social post (without naming a platform) | **type=social-post** |
| "15s" / "30 segundos" / "1 minuto" / "medio minuto" (cap 60) | **duration** = parsed integer |
| Named product/brand ("mi Coca-Cola", "mi producto X") | **product-mode=named** |
| "genérico" / "generic" / "no specific product" | **product-mode=generic** |
| Premium 3D / Pixar-like / Claymation / UGC / phone-shot / POV | **style** = matched preset |
| User described what the video is ABOUT in plain prose | **topic** = verbatim from the user |
| Instagram Reels / Reel / IG Reel / "para Reels" | **platform=reels** → **aspect_ratio=9:16** |
| TikTok / "para TikTok" / "para Tik Tok" | **platform=tiktok** → **aspect_ratio=9:16** |
| YouTube Shorts / Shorts / "para Shorts" | **platform=shorts** → **aspect_ratio=9:16** |
| YouTube (sin "Shorts") / "para YouTube" / "vídeo de YouTube" | **platform=youtube** → **aspect_ratio=16:9** |
| "para web" / "web embed" / "landing page" / LinkedIn / Vimeo | **platform=web** → **aspect_ratio=16:9** |
| Instagram feed / "para el feed de Insta" (sin "Reels") | **platform=instagram-feed** → **aspect_ratio=1:1** or **4:5** (ask which) |

A field resolved here is DONE: it does NOT appear in the form, not even as a pre-checked default. If the user wrote three concrete topics ("how to create a password, how to use MFA, how to store passwords"), the topic is resolved — do not ask "what is the training about?".

#### 0b — Build the form for what's still unknown

**Branch on whether `type` is known:**

- **`type` known** (from ROUTING CONTEXT or 0a) → read the matching sibling file in the workflow directory and build the form per its spec:
  - `type=ad`         → `STEP0_AD.md`
  - `type=explainer`  → `STEP0_EXPLAINER.md`
  - `type=tutorial`   → `STEP0_TUTORIAL.md`
  - `type=demo`       → `STEP0_DEMO.md`
  - `type=social-post`→ `STEP0_SOCIAL.md`

- **`type` NOT known** (user wrote only "quiero un video") → ask with `prompt_user` listing all 5 type options (Ad / Explainer / Tutorial / Demo / Social post — never drop "Ad"). Once the user picks, read the matching `STEP0_<TYPE>.md` and build the form.

Each `STEP0_<TYPE>.md` is self-contained: it lists every field the form should contain for that sub-type, in intent terms (text / select / file picker). Read the current `prompt_form` schema via `get_tool_info("prompt_form")` and translate that intent into the schema's current shape — never paste literal JSON from memory.

**Universal rules layered on top of the per-type spec:**

- Skip any field already resolved by 0a or ROUTING CONTEXT.
- All labels, questions, hints, options in **English** (Hard Rule #5), regardless of the user's chat language.
- Any field asking for files / images / references / logos / screenshots uses the **file picker**, never a plain text input. (The runtime auto-coerces as a safety net if you forget — set it explicitly anyway.)
- The form always contains a generic **References** file-picker (catch-all, empty answer OK), in addition to any type-specific picker.
- Do NOT mix a separate `prompt_user` alongside the form unless used BEFORE the form for a yes/no question about reusing a prior `@`-handle.

**Worked example.** ROUTING CONTEXT contains `type=explainer`. User's message: *"I want a security training for employees for SOC 2 compliance about how to create a password, how to use MFA, how to store passwords."*
- 0a resolves: **type=explainer** (from context), **topic="how to create a password, how to use MFA, how to store passwords"** (verbatim from the user), **product-mode=none** (no product mentioned in a security training context).
- Read `STEP0_EXPLAINER.md`. Build the form with only the unresolved fields: Duration, Style, (skip Concept — already given by the topic), Narrator?, Setting?, References.
- The form does NOT contain a "Video Type" row, a "Topic" row, or a "Product Mode" row. The Step 1 plan reads "Explainer, … about MFA / passwords / password storage".

Only proceed to Step 1 once you have **type + duration + topic + style + product-mode + character + setting + platform** (from 0a, ROUTING CONTEXT, or the form answers) AND the references question has been asked (answer can be empty).

### Step 1 — Light Plan

> ⚠ **CRITICAL — THE PLAN MUST APPEAR VERBATIM IN CHAT.** This step's artifact is the plan TEXT itself, rendered as a structured response the user can read. Saying *"He preparado el plan / I've prepared the plan / He diseñado el plan maestro"* WITHOUT showing the plan is a step-1 failure — the user has no way to evaluate or refine an invisible plan. Render the 8 fields below as visible chat content (numbered list, table, or whatever fits the chat) BEFORE the fork question. If your reply doesn't contain all 8 fields, you haven't done Step 1.

Render a **light plan** — short, scannable, USER'S CHAT LANGUAGE. The plan reflects what the user said, never what you invented. The 8 mandatory fields:

1. **Video type** + **total duration** (e.g. "Explainer, 30 seconds")
2. **Topic / narrative arc** (one sentence — verbatim from the user)
3. **Style preset**
4. **Character** (the one the user picked, or "none")
5. **Setting**
6. **Product handling** (named / generic / none)
7. **Sheet plan** — sheet count is `ceil(total_duration / D_max)`, where `D_max` is the per-sheet maximum reported by `get_tool_info("generate_video")` (Hard Rule #18 — call this BEFORE proposing the sheet plan; NEVER hardcode the cap). Examples assuming today's typical `D_max = 15` (but read the live value, do not trust the example): 12 s → 1 sheet of 12 s; 20 s → 2 sheets (10 + 10, 12 + 8, or 15 + 5 — pick a split that lands on a narrative beat); 33 s → 3 sheets (11 + 11 + 11, or 15 + 12 + 6); 90 s → 6 sheets. Each sheet's duration is within `[D_min, D_max]`; panels per sheet are 1–10. The split is narrative-driven (end each sheet on an act boundary, a transition, a beat) — don't fall back to "always equal slices".

   ⚠ **MANDATORY: `read_file` the per-type spec for the chosen type BEFORE proposing panel count or per-panel durations.** Panels-per-sheet and per-panel duration are type-driven (an ad's quick cuts ≠ an explainer's narrated beats ≠ a tutorial's step-by-step). Use §"Per-type spec routing" above to pick the right file (`VIDEO_TYPE_AD.md` / `VIDEO_TYPE_EXPLAINER.md` / `VIDEO_TYPE_TUTORIAL.md` / `VIDEO_TYPE_DEMO.md` / `VIDEO_TYPE_SOCIAL_POST.md`). These files live in the **`visual-panels` skill's `references/` dir** (not here) — `list_skills`, find the `visual-panels` entry, and `read_file` `<its directory>/references/VIDEO_TYPE_<TYPE>.md`. Read ONLY the one that matches the type at hand and copy its numbers — do not improvise.

   ⚠ **READING the spec is NOT enough — you must APPLY its numbers.** Quote the spec's "Panels per sheet" range and "Per-panel duration" range INSIDE your plan (field 7), then commit to a specific count and build the arc with exactly that many panels. Reading "8–10 panels × 1.5–2 s" for an ad and then proposing "4 panels × 3.75 s" is the bug — that's explainer pacing applied to an ad. Self-check: count the panels in your arc; if the number is outside the spec's range for this type, RE-DO the arc before presenting. Defaulting to "4 panels × 3.75 s" for every type is the bias this rule exists to break.

8. **The frame-by-frame arc as a single-line flow** — labels + durations separated by arrows. THIS IS THE MOST IMPORTANT FIELD: it's what tells the user what the video is actually about, panel by panel. Skipping it means showing no plan.
   > *"1. Wake up (3s) → 2. Open app (4s) → 3. See the dashboard (5s) → 4. Daily check-in (3s) → 5. Reward (3s) → 6. Mission preview (4s) → 7. Tomorrow (4s) → 8. CTA (4s)"*

**Concrete examples** (translate to the user's chat language). The pacing in each example is dictated by the type — DO NOT copy the panel count/duration from the wrong type's example.

**Example A — 30 s Explainer** (3–5 panels per sheet, 3–5 s per panel):

> Esto es lo que se me ha ocurrido para tu video:
>
> 1. **Tipo:** Explainer
> 2. **Duración:** 30 segundos
> 3. **Tema:** Cómo crear contraseñas, usar MFA y guardarlas (formación SOC 2)
> 4. **Estilo:** Premium 3D
> 5. **Personaje:** ninguno
> 6. **Setting:** modern office
> 7. **Producto:** ninguno
> 8. **Plan de hojas:** 2 hojas × 15 s
>    - PART 1 (4 paneles × 3.75 s = 15 s)
>    - PART 2 (4 paneles × 3.75 s = 15 s)
> 9. **Arco panel a panel:**
>    *1. Hook "¿Por qué SOC 2?" (3.75s) → 2. Contraseña fuerte (3.75s) → 3. MFA en acción (3.75s) → 4. Bóveda de contraseñas (3.75s) | 5. Auditoría (3.75s) → 6. Caso real (3.75s) → 7. Checklist (3.75s) → 8. CTA (3.75s)*

**Example B — 15 s Ad** (8–10 panels per sheet, 1.5–2 s per panel — punchy quick cuts, NOT 4 panels of 3.75 s):

> Esto es lo que se me ha ocurrido para tu anuncio:
>
> 1. **Tipo:** Ad
> 2. **Duración:** 15 segundos
> 3. **Tema:** Sandalias doradas Pamen Wazkez para fiesta
> 4. **Estilo:** Realistic UGC
> 5. **Personaje:** una persona joven en una habitación con luz natural
> 6. **Setting:** dormitorio moderno + suelo de madera
> 7. **Producto:** Pamen Wazkez (sandalias doradas)
> 8. **Plan de hojas:** 1 hoja × 15 s
>    - PART 1 (10 paneles × 1.5 s = 15 s)
> 9. **Arco panel a panel:**
>    *1. Caja se abre (1.5s) → 2. Sandalia en mano (1.5s) → 3. Detalle del brillo (1.5s) → 4. Pies entrando (1.5s) → 5. Lazo se ajusta (1.5s) → 6. Giro frente al espejo (1.5s) → 7. Sonrisa cómplice (1.5s) → 8. Salida del piso (1.5s) → 9. Logo over (1.5s) → 10. CTA "Brilla esta noche" (1.5s)*

Then close the reply with the fork question:

> ¿Quieres que abramos un storyboard editable en el visor para afinarlo panel a panel (duración, encuadre, acción, diálogos) antes de generar las láminas, o procedo directamente con las láminas visuales?

Then ASK the user — this is THE FORK between refining the idea panel by panel in the visor, or going straight to the visual sheets.

> ⚠ **MANDATORY: use `prompt_user` for the fork, NOT `print` + `return`.** Calling `print` and returning immediately hands control back to the coordinator without ever waiting for the user — that's the bug. `prompt_user` blocks until the user picks. Use this exact shape (the plan goes in `message`, the question + options handle the fork):
>
> ```
> prompt_user({
>   message: "<the 8-field plan rendered in the user's chat language>",
>   question: "<the user's chat language: 'How do you want to proceed?'>",
>   options: [
>     "Open the editable storyboard in the visor (refine panel by panel)",
>     "Go straight to the visual sheets"
>   ]
> })
> ```
>
> Option labels in English (Hard Rule #5). The `message` carries the plan in the user's chat language. Do NOT emit a separate `print` with the plan before `prompt_user` — `prompt_user`'s own `message` field renders it. Do NOT include a `return` action in the same batch as `prompt_user` — `prompt_user` is the wait point.

Remember the option text the user picked (the runtime returns it). Both options take the SAME first action — authoring the storyboard JSON. The user's pick only changes whether you SHOW it in the visor or proceed silently.

#### Step 1b — Build the storyboard JSON (ALWAYS, regardless of fork choice)

The storyboard JSON is the **first creative artifact** of this workflow (per Hard Rule #17) AND the canonical handoff to Step 2. It lives at `~/.koi/storyboards/<id>.json`, follows the v6 schema, and is the file the GUI visor opens when the user picks "Refine in visor". Step 2 reads it as the source of truth for every panel.

You build it whether the user wanted to see it or not; the fork choice from Step 1 only controls *visibility* (show in visor vs. silent), NEVER whether the JSON exists nor whether you replace it with a different format.

> 🛑 **HARD STOP — NO `.md`, NO `.txt`, NO PROSE DOC.** The deliverable of Step 1b is a `.json` file at `~/.koi/storyboards/<id>.json`. Not a "video brief". Not a "shot list document". Not a "script". Not a "treatment". Not an `outline.md` in the Workflow workspace. If you find yourself about to call `write_file` with a path that does NOT end in `.json` inside `~/.koi/storyboards/`, STOP — you're about to violate Hard Rule #17. The Light Plan from Step 1 was already shown to the user via `prompt_user`'s `message` field; the user has already read it. Now you produce the JSON.
>
> ⚠ **MANDATORY: activate the skill `storyboard` FIRST, AS ITS OWN BATCH.** The skill is the SOLE source of truth for the JSON's shape — it carries the canonical v6 schema, the on-disk path convention (`~/.koi/storyboards/<id>.json`), the cinematic vocabulary (shot / angle / movement), the invariants (`sum(shot.duration) === total`), the character-continuity rules, the lighting / pencil-sketch style enforcement, and the full authoring playbook. Anything you "remember" about storyboard JSON shape from prior sessions or training data is stale or wrong; the skill body overrides every prior. Activating it is NOT optional, NOT a "best-effort try" — without the skill body in `# Active Skill Instructions`, the JSON you produce will be hallucinated and the visor won't open it.
>
> Authoring is a **TWO-TURN flow**:
>
> 1. **Turn A — activate only.** Emit `activate_skill` for `storyboard` and STOP the batch. No `write_file`, no `show_result`, no `return` in the same batch. You need the activation tool result to land in your context before you can write a single line of JSON.
> 2. **Turn B — author, then branch.** On the next iteration, with the skill body now visible in `# Active Skill Instructions`, follow the skill's authoring playbook to write the JSON. The actions after `write_file` depend on which option the user picked at the Step 1 fork:
>
>    - **If the user picked "Open the editable storyboard…"** → same batch: `write_file` + `show_result` (so the visor opens with the storyboard loaded) + `prompt_user` (two options: *"Refine it"* / *"Looks good — generate the visual sheets"*). NO `return` in this batch — `prompt_user` is the wait point. The Refinement loop below takes over from here.
>    - **If the user picked "Go straight to the visual sheets"** → same batch: `write_file` ONLY. No `show_result` (the user explicitly opted out of seeing it). No `prompt_user`. Then emit `return` with the storyboard path so the coordinator advances to Step 2 immediately. The visor doesn't open; Step 2 will read the JSON behind the scenes.
>
> Putting `activate_skill` and `write_file` in the same batch is the failure mode — the runtime executes them in order but you DECIDED the `write_file` content without ever seeing the activation result. The JSON you write in that scenario is hallucinated from priors. That's exactly the bug to avoid.

When you reach Turn B (skill body loaded), the skill's playbook tells you the exact schema, the on-disk path, the invariants, the language rule, and the authoring flow. Follow the skill body literally — do not paraphrase its schema from memory.

#### Step 1c — Storyboard refinement loop (only when the user picked "Open the editable storyboard…")

Entered after the Turn B `prompt_user` returns. Two outcomes per `prompt_user`:

- **"Looks good — generate the visual sheets"** → THIS is the only turn in which you emit `return` (with the storyboard path payload) so the coordinator advances to Step 2.
- **"Refine it"** → the user iterates. Edits land from TWO places, and both are equally valid:
  1. **Directly in the visor** — every field is editable inline; the visor persists changes to disk in real time, and the file watcher reflects them back into your context on the next turn.
  2. **In chat with you** — they describe changes ("primer plano del logo en panel 3", "haz el panel 5 más corto", "muévelo a la escena anterior", "cambia la iluminación a noche").

  When the user proposes a change in chat, follow the skill's "Flow: modifying an EXISTING storyboard" section — it covers the read-first / edit / re-validate sequence, the invariants to preserve, and the success check. Do not duplicate that logic from memory; the skill body is authoritative.

  After applying EVERY change, end the batch with `prompt_user` (two options: *"More changes"* / *"Looks good — generate the visual sheets"*) — NOT with `return`. Every iteration of the loop ends the same way. The loop only terminates the turn the user picks *"Looks good"*.

> 🛑 **CRITICAL — Hard Rule #15 applies in this branch: the task ENDS WITH `prompt_user`, NEVER WITH `return`** (until the user picks *"Looks good — generate the visual sheets"*). Returning early hands control back to the coordinator and the workflow auto-advances to Step 2 — the user never gets to refine. The ONLY `return` the worker emits in this branch is on the turn the user picks "Looks good"; that `return` carries the storyboard path payload. If your task description doesn't explicitly mention this rule, treat it as a planner summary omission and apply the rule from Hard Rule #15 anyway.

> 🛑 **DO NOT pre-create the "Generate visual panel sheets" task while the storyboard is still being refined.** If you use `task_create` to lay out the workflow plan, list ONLY the tasks up to and including "Refine storyboard in the visor". Adding the downstream tasks before the user has confirmed the storyboard creates an open pending-task list that pressures you to auto-progress through it. Create them AFTER the user picks "Looks good", in the same turn as you start Step 2.

The storyboard JSON is the handoff artifact for Step 2 in BOTH branches — the only difference is that in the "Go straight to the visual sheets" branch you wrote it once and immediately returned, while in the refinement branch the user iterated on it via the visor. Either way, Step 2 reads the same JSON path.

> ⏱ **The refined storyboard's summed durations are now the authoritative `total_duration` — the Step 0 number is STALE.** The `duration` you captured in Step 0 (the user's "un anuncio de 60 segundos") was only the SIZING target for the FIRST draft. During this refinement loop the user adds / deletes / retimes shots in the visor, so `sum(shot.duration)` of the JSON on disk changes on purpose — and that sum is now the real video length. Before advancing to Step 2, `read_file` the storyboard and RECOMPUTE `total_duration = sum(shot.duration)` from the current JSON. From here on, Step 2's sheet plan (`sheet_count = ceil(total_duration / D_max)`) and Step 3's clip durations derive from THIS recomputed total — NEVER from the Step 0 value, the Light-Plan number, or anything cached. If the user trimmed it from 60 s to 48 s, the video is 48 s; do not pad it back. (The sole exception: the user explicitly demanded a hard runtime that must hold regardless of edits — then refit the shots to it and say so.)

#### Product handling guidance (part of Step 1's plan)

Don't ask *"do you need a product?"* upfront — confusing. Weave it into the plan:

> *"For the supplement, do you want me to use a specific product name, or keep it generic? If you have a product, I'll use the name + a short `[REFERENCE IMAGE]` placeholder so you can attach the real product image when we render the frames."*

**Three product modes (you detect, user doesn't pick):**
- **Named product** → product name + `[REFERENCE IMAGE OF {PRODUCT NAME}]` placeholder in hero / product frames
- **Generic** → designed generic, no placeholder
- **None needed** → no product references at all

If the user uploads a product image during the chat → treat as named, use the product name, insert the placeholder, and tell them to re-attach the image during the per-frame `generate_video` calls in Step 4.

#### "Just build it" escape hatch (a branch of Step 1)

Triggered ONLY when the user explicitly opts out with *"just build it"*, *"sorpréndeme"*, *"don't ask, just do it"*, *"use your judgment"*, *"you choose"*. The default of "user only typed `quiero un video`" is NOT this case — that goes to Step 0.

When this fires:

1. List 4–6 assumptions you're making (type, duration, style, character, setting, product handling, narrative arc).
2. Build immediately.

Even here, NEVER invent a `@`-handle that wasn't already attached or named by the user — describe the character / product generically in prose instead.

### Step 2 — Build the visual panels(s)

This step turns the approved storyboard JSON (from Step 1b) into the **second mandatory artifact** (per Hard Rule #17): the polished 4K panel SHEET image(s). **The full playbook lives in the `visual-panels` skill** — activate it and follow its SKILL.md. Do NOT re-derive the sheet anatomy, the chunking math, the style presets or the consistency rules from memory; the skill body (and its `references/`) is the only source of truth.

> 🛑 **TWO non-negotiable invariants at this step** (both already enforced in `STORYBOARD_ANATOMY.md`, repeated here so the planner can't miss them):
>
> 1. **Panels = JSON shots, 1:1, in order.** The visual sheet is a projection of the JSON. If the JSON has 5 shots, the sheet has 5 panels. NEVER add panels to "hit the per-type 8–10 range" — that range was already applied at Step 1b's planning, the JSON's shot count is the final word.
> 2. **Sheet K ≥ 2 MUST receive every prior approved sheet as `referenceImages`** with aliases `sheet_part_1` … `sheet_part_{K-1}`, anchored positionally in the prompt (`Image 1` …), AND with a continuity block telling the model to preserve character/wardrobe/lighting/palette/legend/footer from those references. Skipping this is the reported bug *"para el segundo storyboard visual no ha puesto el primero como referencia"* — characters drift, the legend wobbles, the palette re-rolls.

> 🛑 **HARD STOP — NO `.md` PANEL DESCRIPTION DOCS.** The deliverable of Step 2 is a set of 4K PNG sheet image(s), produced by `generate_image` calls the `visual-panels` skill prescribes (`label: "visual_storyboard"`, `resolution: "4K"`, `aspectRatio: "16:9"`, etc.). NOT a `sheets.md` listing the panels in prose. NOT a `storyboard-spec.md`. NOT a "visual breakdown" doc. If you find yourself about to `write_file` a `.md` here, STOP — you're about to violate Hard Rule #17 and skip the skill that knows how to render the panel grid at 4K. The user wants to SEE the storyboard, not read a description of it.
>
> ⚠ **MANDATORY: activate `visual-panels` FIRST, AS ITS OWN BATCH.** Skipping the activation and calling `generate_image` directly with a hand-written prompt produces an off-brand panel grid (wrong font sizes, missing footer columns, broken legend, wrong style preset phrasing) that fails the Quality Checks at the bottom of this file. The skill body holds the panel anatomy, the 4 style preset blocks, the per-type footer column 4 copy, and the continuity rules for multi-sheet videos — every one of those is mandatory and none of them is derivable from priors.

> 1. **Turn A — activate only.** Emit `activate_skill` for `visual-panels` and STOP the batch (no `read_file`, no `generate_image`, no `return` in the same batch). The activation result lands the skill body in `# Active Skill Instructions` AND returns the skill's absolute `directory` + `resources` — you need both before you can read the anatomy/style/per-type references it owns.
> 2. **Turn B — build, following the skill.** With the skill body now visible, follow it literally:
>    - `read_file` the storyboard JSON at the path the previous step returned (`~/.koi/storyboards/<id>.json`). It is the source of truth — if chat and JSON disagree, the JSON wins (the user may have hand-edited the visor).
>    - **Chunk** the shots into sheets per the skill's § STEP B (each sheet ≤ 15 s and ≤ 10 panels; minimize sheet count; end on beat boundaries; the last sheet may be short).
>    - **Build one sheet at a time, in order**, per the skill's STEP C–E: every `generate_image` call carries `aspectRatio: "16:9"`, `resolution: "4K"` (fallback `"2K"`), `outputFormat: "png"`, `label: "visual_storyboard"`; the prompt follows `references/STORYBOARD_ANATOMY.md`, drops the chosen `references/STYLE_PRESETS.md` block, and copies footer column 4 from the matching `references/VIDEO_TYPE_<TYPE>.md` (the slug resolved in Step 0). Sheet K ≥ 2 passes ALL prior approved sheets as `referenceImages` (`sheet_part_1`, …) plus the continuity block, and reuses the JSON `seed`.
>    - Name `referenceImages` as `{ alias, path }` and wire each alias by name into the prompt (never "the attached image"); inspect dropped files before describing them; never invent a reference for an unattached subject.

The per-sheet approval loop itself is Step 3 below. Do NOT show the image prompt to the user — feed it to `generate_image`.

### Step 3 — Show and refine the visual panels

1. `show_result` the generated sheet.
2. Ask for refinement, frame-by-frame if needed:
   > *"Would you like this version as-is, or would you like to refine something? If you want changes, tell me which frame(s) and what to change (label, caption, duration, dialogue, icons, or illustration details)."*
3. If the user asks for refinements:
   - Update the plan / prompt and re-generate. Same `referenceImages` payload (including any prior `sheet_part_N` if multi-sheet).
   - Show again, ask again.
4. Only when the user confirms THIS sheet is ready, move on to the next sheet (if multi-sheet) or to Step 4.

**Re-validate the invariant after every refinement:** `sum(panel_durations) === sheet's own clip duration` (within tool-reported `[D_min, D_max]`, Hard Rule #18) must still hold per sheet, AND `sum(sheet_clip_durations) === total_video_duration` across sheets must still hold. If the user added a 5-second beat to sheet 2, either another panel in sheet 2 shrinks, OR the sheet itself grows (still ≤ `D_max`) and another sheet shrinks, OR the total grows by 5 s — confirm which one with the user.

Before finishing this task, save a `step5_output.json` inside the **Workflow workspace** from your RUNTIME CONTEXT (per Hard Rule #14). The full target path is `<value of the "Workflow workspace" row from RUNTIME CONTEXT>/step5_output.json` — copy the workspace value verbatim, do NOT use a relative path and do NOT derive the path from the WORKFLOW.md location. The file contains everything Step 4 needs: type, total_duration_seconds, sheet_count, sheets[] (each with index, absolute path, panels[] of n/label/duration_s/dialogue, AND the sheet's own clip_duration_s — the whole-second value within the tool-reported `[D_min, D_max]` that the `visual-panels` skill assigned the PART), voiceover_lines_by_sheet, any subject reference aliases+paths, audio_plan from the per-type spec (`VIDEO_TYPE_<TYPE>.md`'s "Audio cue" section — whether music is needed + brief), **platform** + **aspect_ratio** (driving the `create_timeline` shape in Step 4), and **storyboard_path** (absolute path to the `~/.koi/storyboards/<id>.json` — Step 4's `visual-panels-to-video` skill uses it as the per-clip timing + per-shot audio authority). Use absolute paths throughout.

### Step 4 — Generate the final video

This step is generic: it animates the approved visual panel sheet(s) into the final video. **The full playbook lives in the `visual-panels-to-video` skill** — activate it and follow its SKILL.md. Don't re-derive the per-sheet render rules, the audio contract, the per-clip duration logic or the timeline assembly from memory; that skill (and the `timeline-assembler` skill it delegates to) is the source of truth.

> 1. **Turn A — activate only.** Emit `activate_skill` for `visual-panels-to-video` and STOP the batch. The activation lands the skill body in `# Active Skill Instructions`.
> 2. **Turn B — render + assemble, following the skill.**
>    - `read_file` `step5_output.json` from `<Workflow workspace from RUNTIME CONTEXT>/step5_output.json` (Hard Rule #14) — it holds the inputs the skill expects: the ordered sheet paths, panel data, voiceover lines, subject references, `audio_plan`, `type`, `platform` / `aspect_ratio`, and the storyboard JSON path. Don't search the disk; if the file is missing, surface the error.
>    - Hand the skill its inputs: the **sheets** (in order), the **references** manifest (characters / products / settings to lock identity), and the **storyboard JSON** path — which is the AUTHORITY for per-clip timing and per-shot action / dialogue / SFX / music. Per the skill: render ONE `generate_video` per sheet (each clip's `duration` taken from the storyboard, NOT a hardcoded 15), pass the platform `aspectRatio` and `withAudio: true` on every clip, generate a single full-length music track only when the plan needs it and there are ≥ 2 sheets, then concatenate every clip back-to-back on a timeline (each at its OWN duration, cumulative cursor) and render.
>    - Assembly mechanics (tracks, music ducking to ≈ −28 dB, subtitles, the preview → render → show_result hand-off) come from the `timeline-assembler` skill, which `visual-panels-to-video` points you to. **Always create a NEW timeline for the video, and END by `show_result`-ing that timeline** (it's where the finished video lives — the user lands there to play / tweak / re-render).

The video is assembled on a TIMELINE only — never `ffmpeg concat` or any other glue tool.

---

## 🎨 Style Presets

There are **4 official presets** (full phrasing in `STYLE_PRESETS.md`):

1. **Premium 3D Animation** (Pixar-adjacent, phrased to avoid moderation triggers — never say "Pixar")
2. **Claymation** (stop-motion handcrafted aesthetic)
3. **Realistic UGC** (phone-shot, casual, authentic lifestyle)
4. **POV-Style** (first-person immersive perspective)

If the user wants something outside these four, they can describe a custom style and you adapt — always confirm the phrasing during the plan.

---

## 🎬 Video Types

There are **5 supported types** (see §"Per-type spec routing" above for the file map; full spec for each in its own `VIDEO_TYPE_<TYPE>.md`):

| Type | Pacing | Footer column 4 | Audio default |
|---|---|---|---|
| **ad** | Punchy, 1–2s frames | 🎯 BRAND NOTES | Music + (optional) voiceover hook |
| **explainer** | Narrated, 3–5s frames | 💬 EXPLAINER NOTES | Voiceover narration over light music |
| **tutorial** | Step-by-step, 4–6s frames | 📚 INSTRUCTOR NOTES | Voiceover instructions |
| **demo** | Product in use, 2–3s frames | 🛠️ PRODUCT NOTES | Voiceover or SFX-only |
| **social-post** | Rhythmic, 1–2s frames | 📱 CHANNEL NOTES | Music-driven, often no voiceover |

Custom video kinds (dialogue scene, narrative short, music video, …) follow the same anatomy with the closest-matching type as base and a confirmed adaptation.

---

## 🔁 Character & Setting Consistency

If the user is building a follow-up and wants the same character / setting as before:

- Check the chat history. If there's a prior sheet or video with a described character, ask:
  > *"Do you mean the same character we built earlier — [brief description]?"*
- If yes, reuse that exact description AND pass the prior sheet as a `referenceImage` in this new build.
- If the user is in a fresh chat and wants continuity, ask them to paste / describe / attach the character from the previous session.

Don't maintain a separate "character card" output. Rely on chat context + reference images.

---

## 🚫 Out-of-Scope Requests

**ANY whole-second duration ≥ `D_min` (the tool-reported floor from `get_tool_info("generate_video")`) is in scope.** 20 s, 25 s, 40 s, 2 minutes, 30 minutes — all fine. They just become more sheets (each within `[D_min, D_max]`, Hard Rule #18) spliced on the timeline. Per Hard Rule #1: no quantization, no rounding, no cap.

The only nudge: for very long videos (**≥ 5 minutes**, i.e. lots of sheets), confirm ONCE that the user is aware each sheet is a separate `generate_video` call (cost + wait), then proceed. Do NOT refuse, do NOT propose splitting into "chapters", do NOT cap.

**If the user asks for a different aspect ratio** (9:16, 1:1, 4:5):

> *"The visual panels is 16:9 by design — that's what gives the panels space. The FINAL video can be reframed to 9:16 / 1:1 / 4:5 at the per-frame `generate_video` step. Want me to proceed with the sheet in 16:9 and render the clips in your target ratio?"*

---

## 📁 Knowledge Files

**Pipeline references:**
- `STORYBOARD_ANATOMY.md` — exact spec of every part of a sheet, including the variable-grid layout chooser and the optional dialogue slot
- `STYLE_PRESETS.md` — the 4 visual styles, ready-to-paste phrasing
- `VIDEO_TYPE_<TYPE>.md` — five per-type spec files, one per slug (ad / explainer / tutorial / demo / social-post). Each holds the pacing heuristics, footer label and audio cue for its type. The §"Per-type spec routing" table at the top of this file maps the resolved `type` slug to the matching file — read ONLY the one that fires.
- `LENGTH_BLOCKS.md` — the multi-sheet system, cross-sheet consistency rules, final render pipeline
- `QUICK_START.md` — full worked example of a 30-second explainer

**Per-type Step 0 form specs** (read ONLY the one matching the resolved `type`):
- `STEP0_AD.md` — form fields for ads
- `STEP0_EXPLAINER.md` — form fields for explainers
- `STEP0_TUTORIAL.md` — form fields for tutorials
- `STEP0_DEMO.md` — form fields for product demos
- `STEP0_SOCIAL.md` — form fields for social posts (Reels / Shorts / TikTok)

Consult these as needed. They are the source of truth.

---

## ✅ Quality Checks Before Delivering Any Prompt

When calling `generate_image` to generate a sheet, verify both the tool-call parameters AND the prompt content.

**Tool-call parameters:**
- [ ] `aspectRatio: "16:9"`
- [ ] `resolution: "4K"` (or the highest bucket the model exposes — never default / medium)
- [ ] `outputFormat: "png"`
- [ ] `label: "visual_storyboard"` — routes to the 4K panel-grid model
- [ ] `referenceImages` populated with the user's refs AND (for sheets 2+) every prior approved sheet as `sheet_part_K`

**Prompt content:**
- [ ] Title is in ALL CAPS
- [ ] Subtitle reads exactly `"TOTAL VIDEO TIME: <N> SECONDS"`
- [ ] Hero thumbnail described in top-left
- [ ] Legend box has exactly 4 icons in 2×2, conceptually fitting the topic, IDENTICAL across every sheet of a multi-sheet video
- [ ] One black banner divider with `PART <K> — [DESCRIPTIVE LABEL] (<N> frames · <S> s total)`
- [ ] Exactly `<frameCount>` frames, each with: label, per-frame duration tag, 1–2 icons, illustration description, short caption, AND a dialogue line where applicable
- [ ] `sum(frame_durations) === sheet_total_seconds`
- [ ] Across all sheets: `sum(sheet_totals) === total_video_duration`
- [ ] Footer has all 4 columns (VIDEO FLOW, CAMERA TIPS, LIGHT & STYLE, [TYPE-SPECIFIC NOTES])
- [ ] Style phrasing matches one of the 4 presets (or a confirmed custom)
- [ ] No long product descriptions — only product name + `[REFERENCE IMAGE]` placeholder if applicable
- [ ] Character described consistently across every frame AND every sheet
- [ ] Mix of action shots and product / detail close-ups appropriate to the video type

When calling `generate_video` per SHEET (one call per sheet, NOT per panel — handled by the `visual-panels-to-video` skill), verify:

- [ ] `referenceImages` populated with the sheet itself as the first entry (alias `sheet_part_K` or `storyboard` for single-sheet)
- [ ] For sheet K ≥ 2: every prior approved sheet is ALSO in `referenceImages` (`sheet_part_1`, …, `sheet_part_{K-1}`)
- [ ] `duration` = the sheet's OWN clip duration (the whole-second value from the storyboard / `clip_duration_s`, within the tool-reported `[D_min, D_max]` — see Hard Rule #18), NOT a hardcoded number
- [ ] Total `generate_video` calls = sheet count (NOT panel count)
- [ ] Prompt includes a per-shot direction block from the storyboard JSON — each shot's framing, camera movement, action, timing and sound (per the `visual-panels-to-video` skill). It does NOT re-describe the visual STYLE or the subjects' appearance (sheet + refs carry those).
- [ ] If the sheet has dialogue lines in any panel, they appear in the prompt in panel order
- [ ] **Audio block bullet (c) — conditional**: present when `audio_plan` generates a separate A2 music track (prompt forbids the model adding music in the clip), OMITTED when there's no separate music track (no contradiction to prevent)

After assembling the timeline and BEFORE `render_timeline`, verify:

- [ ] The A2 music clip (if any) is ducked ONLY where voice plays over it (`set_clip_volume(<clipId>, { change: { gain: 0.04 } })` / `volumePoints`). If the video has NO voiceover/dialogue (ambient music over action), the music is NOT ducked — ducking a wordless scene makes it sound empty. The agent decides from the actual audio.

If any item fails, fix before delivering.
