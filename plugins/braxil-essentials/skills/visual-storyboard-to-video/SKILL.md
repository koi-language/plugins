---
name: visual-panels-to-video
description: Turning one or more approved VISUAL panels sheets (the 4K panel-grid images built by the `visual-panels` skill) into the FINAL video. Takes the sheet images, an optional references manifest (characters / products / settings to lock identity), and — when available — the INTERACTIVE storyboard JSON (the authority for per-clip timing, per-shot action, dialogue, SFX and music). Composes the cinematic per-shot video prompt for each clip, renders one video per CLIP — a clip is a group of consecutive panels (e.g. panels 4–7), and a single sheet can hold several clips (see each sheet's `metadata.clips`) — with each clip's duration driven by the interactive storyboard when present, generates a single music track when needed, and assembles every clip back-to-back on a timeline into one continuous video. Use whenever you have approved panel sheets and need the rendered video (e.g. Step 4 of the create-video workflow). Pairs with `visual-panels` (its upstream) and `timeline-assembler` (which it delegates assembly to).
---

This skill is the OUTPUT stage of the storyboard pipeline. Upstream, `visual-panels` produced the approved 4K sheet image(s). This skill **composes the video prompt AND renders** each sheet into a video clip, then stitches them into the final film. It is intentionally workflow-agnostic — give it the inputs below and it produces the video.

It delegates the actual assembly mechanics to the **`timeline-assembler`** skill (track layout, fps / aspect inheritance, music ducking, transitions, subtitles, preview-before-render handoff). Read that skill's SKILL.md (via its activation `directory` / `list_skills`) before assembling — do NOT re-derive those rules here.

## 🛑 STEP 0 — RECOVER + READ THE INTERACTIVE JSON FIRST (MANDATORY, before any `generate_video`)

**The sheet image is NOT the script — the interactive storyboard JSON is.** Before composing a single video prompt you MUST recover and `read_file` the source interactive storyboard JSON. **NEVER imagine / infer the scene from the sheet's pixels when a `sourceStoryboard` exists** — that's the reported bug: the agent looked at the visual sheet, hallucinated a scene ("a vending machine in a hallway" for a storyboard that was actually a man slumped on a sofa), and fired `generate_video` with a made-up prompt, never reading the JSON.

Hard rules for this step:
1. **Recover the JSON via `inspect_creation`** (see INPUTS → `interactiveStoryboard`): `inspect_creation({ filePath: "<sheet path>" })` → `creation.metadata.sourceStoryboard` → `read_file` THAT JSON. The JSON is the AUTHORITY for the premise, per-shot action, timing, continuity, dialogue and audio.
2. **NEVER pass the panel SHEET as `startFrame`** to `generate_video`. A multi-panel sheet is not a literal first frame — it goes into `referenceImages` (look/identity), never `startFrame`. Using the sheet as `startFrame` is a bug.
3. **NEVER skip straight to a raw `generate_video`** off the sheet pixels + an invented prompt. The prompt is composed FROM the JSON (STEP B), shot by shot.
4. Only when `inspect_creation` returns NO `sourceStoryboard` may you fall back to the sheet's pixels (INPUTS step 2). Never ask the user to name the project — the metadata resolves it.

## ────────────────────────────────────────
## INPUTS
## ────────────────────────────────────────

You receive (from the task description, or from `step5_output.json` when run inside the create-video workflow):

- **`sheets`** — an ORDERED list of approved visual panel sheet images (PART 1 … PART N), with absolute paths. Required. Each sheet renders to ONE clip.

  **🛑 Resolving `sheets` when you're NOT handed an explicit list (ad-hoc "genera el vídeo" request) — the sheets MUST belong to the storyboard the user means.** A single session often holds SEVERAL videos (e.g. a horse ad AND a Star Wars short); the most-recent image on disk / in the ledger is frequently the WRONG project. **This is the reported bug: asked to render the Star Wars video, the agent rendered the horse project's sheets.** Resolve them scoped, never by recency:
  - The target storyboard is almost always the **ACTIVE document in the `# WORKING AREA`** (the storyboard the user is looking at). Take its `id` (the storyboard JSON's `id`, e.g. `star-wars-laser-comedy`).
  - Call **`recall_creations({ kind: 'image', storyboard: '<that id>' })`** — it returns ONLY the visual sheets whose `metadata.sourceStoryboard` ties them to THAT storyboard. Order them by `storyboardPart` (PART 1 … PART N). This is the ONLY correct way to gather the sheets.
  - 🚫 NEVER take "the most recent sheets", NEVER `ls`/`shell` the images dir, NEVER mix sheets from different storyboards. The `storyboard` scope is what keeps the horse project out of the Star Wars render.
  - If no storyboard is active, or the result spans more than one storyboard, or it comes back empty (sheets predate the `storyboard` link), **STOP and ask the user which storyboard to render** (offer the candidates by name). Never guess by recency.
- **`references`** — OPTIONAL manifest of the recurring subjects to keep consistent: characters, products, hero settings — each with a semantic alias and a path or `@handle` (e.g. `{ hero_character: "/…/leo.png", product_pack: "@acme_bottle" }`). Pass these into every clip's `referenceImages` so identity stays locked. **Also pull the interactive storyboard's own `references` arrays** — at the STORYBOARD root, on each SCENE, and on each SHOT (the user can attach them per level in the visor). For each clip, include the references in scope (the sheet's shots' shot-level refs + their scenes' refs + the storyboard-level refs), resolving any `@handle` to a path.
- **`interactiveStoryboard`** — path to the source `~/.koi/storyboards/<id>.json`. **When present it is the AUTHORITY** for: per-clip timing (per-shot `duration`), what each shot does (`action`), the per-shot continuity state (`continuity` = { characters, objects }; legacy shots may carry a single `state` string), the spoken lines (`dialogue`), and the sound (`sfx`, `music`, `audio`), plus the storyboard-level `synopsis` (story premise), `continuity` (the LOCK rules — story-wide invariants/negatives), `characters`, `lighting` and `aspect`. Prefer it over reading values off the sheet image — the JSON is exact; the pixels are an approximation. The `synopsis` + storyboard `continuity` LOCK + per-shot `continuity` row are what keep the clip from contradicting the story (the high button staying high, the step-can staying intact) — transcribe them, don't drop them.

  Recovery order when it wasn't handed to you directly. **NEVER ask the user which storyboard / project it is — the sheet's metadata ALREADY records its source storyboard; you must RESOLVE it. Asking "do you have the interactive project / its name?" is the reported bug.**

  1. **Read the sheet's metadata with `inspect_creation` — MANDATORY, the auto-recovery path.** Call `inspect_creation` with `filePath: "<the sheet's absolute path>"` — it resolves the media-library row (via `getByPath`) and returns `creation.metadata`. That `metadata.sourceStoryboard` is the ABSOLUTE PATH of the interactive storyboard JSON (plus `storyboardPart` / `storyboardParts`). ⚠️ **`read_file` does NOT give you this** — it returns the PIXELS (vision), not the media-library metadata; reading the sheet image alone makes you wrongly conclude "no JSON link" and imagine a scene. When `inspect_creation` returns a `sourceStoryboard` → `read_file` THAT JSON and use it as the authority. You already have it — do NOT ask. (When the Info panel shows a "Storyboard: <name>" link, `metadata.sourceStoryboard` IS set, and `inspect_creation` will return it.)

  2. **ONLY if `inspect_creation` returns no `sourceStoryboard` → FALL BACK to the sheet's pixels.** `read_file` the sheet PNG; vision returns the panels, captions, banner and timecodes. Use those to derive per-shot durations and beats. The sheet is the authority in this case — it carries everything you need.

  ⛔ **DO NOT search the filesystem for a "matching" storyboard JSON.** No `shell ls .koi/storyboards/`, no `recall_creations` to "find what the sheet might come from", no reading every JSON in the folder and guessing which one matches the sheet's vibe. This is the reported confabulation bug: agent listed `~/.koi/storyboards/`, found `soc2_compliance_explainer.json` next to two unrelated stories, decided it "corresponds" to a sheet that is actually a pocket-watch / grandfather story ("El valor del tiempo"), and proceeded to render the wrong content. **The metadata is the only auto-link from sheet → JSON. No metadata = no JSON. Period.** Use the pixels instead (step 2) — never ask the user to name the JSON.

  **Never ask the user to identify the storyboard** — step 1 (metadata via `inspect_creation`) resolves it and step 2 (pixels) covers the rest. Only in the rare case a sheet has NEITHER a `sourceStoryboard` in its metadata NOR legible pixels do you surface the gap with a single `print` (not a blocking question) and proceed best-effort. Never invent the link.
- **`audio_plan` / `type` / `aspect_ratio` (platform)** — OPTIONAL. Whether music is needed and its brief, the video type, and the destination aspect ratio. In the create-video workflow these are pre-resolved in `step5_output.json`.
- **`targetGenerator`** — OPTIONAL hint (Seedance / Kling / Sora / Veo / Runway / Luma / Hailuo / Wan / Higgsfield). When given, tailor the prompt's camera language and shot pacing to that model's strengths (see STEP B "Adapt to style and tool"). When absent, write a model-agnostic brief.

If `sheets` is missing or empty, surface the error — there is nothing to render.

## ────────────────────────────────────────
## STEP A — Enumerate the CLIPS (a sheet can hold several) and resolve each clip's duration
## ────────────────────────────────────────

**🛑 A sheet is NOT a clip — a sheet (image) can hold SEVERAL clips.** `visual-panels` now packs multiple clips onto one sheet (to save image-gen cost) and records the split in each sheet's **`metadata.clips`** array: `[{ clipIndex, shotIds, panels, durationSec }, …]`. So:

- **Read every sheet's `metadata.clips`** (via `inspect_creation` on each sheet path). Concatenate them and **sort by global `clipIndex`** → that ordered list is your render plan. You call **one `generate_video` per CLIP**, in `clipIndex` order across ALL sheets — NOT one per sheet.
- **Fallback (old sheets with no `metadata.clips`):** treat the whole sheet as one clip — the legacy "1 sheet = 1 clip" behaviour. Only then does a sheet equal a clip.

Each clip needs a `duration`. **Read the supported values from the tool — call `get_tool_info("generate_video")` and read the `duration` schema. NEVER hardcode the range** (today's typical is whole seconds [4,15] + `"auto"`, but trust the tool). Use `D_min`/`D_max` for the tool-reported floor/ceiling.

Resolve each clip's duration in this priority order:

1. **`clip.durationSec` from `metadata.clips` (PREFERRED).** Already the exact integer duration `visual-panels` computed for that clip — use it, clamped to `[D_min, D_max]`. If you also have the interactive JSON (`metadata.sourceStoryboard`, `read_file` it), cross-check: `durationSec` should equal the sum of that clip's `shotIds`' `shot.duration`.
2. **No JSON (and none recoverable from metadata) — read the sheet's pixels.** `read_file` the sheet PNG (vision returns the panels, captions, banner and timecodes). From the visible content: (a) sum the per-panel timecodes to get the sheet's total `S` in seconds; (b) use the banner total (`PART K — … (<n> frames · <S> s total)`) if present; (c) clamp `S` to a whole second in `[D_min, D_max]`. The sheet is its own authority in this branch.
3. **Neither metadata nor legible sheet pixels** — fall back to `D_max`, AND surface the uncertainty to the user via `print` so they can correct if needed.

NEVER hardcode `duration: 15` for every sheet when the storyboard says otherwise — a 10-second PART must render a 10-second clip, or the timeline drifts out of sync with the pacing the user approved. State the per-clip durations before rendering, e.g. *"3 clips: PART 1 → 14 s, PART 2 → 10 s, PART 3 → 10 s."*

⚠ **The storyboard total overrides any duration stated in the task / brief.** If the task description says "a 60-second ad" but the (possibly user-edited) interactive storyboard now sums to 48 s, the video is 48 s — the storyboard is the authority, period. The brief's number was only the original sizing target; the user retimed it in the visor on purpose. Do NOT pad, stretch, or add filler clips to hit the old number. The sole exception is an explicit hard-target instruction in the task ("must stay exactly 60 s") — only then refit.

### ⛔ Fail-fast — a single CLIP > 15 s is malformed (a sheet may exceed 15 s — that's fine now)

A SHEET can legitimately exceed 15 s of content now (it holds several clips). What must NOT exceed the per-clip cap is one **clip**. After resolving durations, sanity-check **each clip** (its `durationSec` from `metadata.clips`, or its `shotIds`' summed `shot.duration`):

- If any clip's duration **> 15 s** → upstream chunking is buggy (Step A's clip-grouping must never produce a >15 s clip). Do NOT silently compress to fit by dropping shots — that's the *"ha hecho los 15 segundos pero solo de una parte"* bug. **STOP** and surface it:

  > *"Clip `<clipIndex>` sums to `<X>` s but a rendered clip caps at 15 s. Please re-build the panel sheets with the `visual-panels` skill — its Chunking step splits the shots into ≤15 s clips I'll then render and concatenate."*

- **No `metadata.clips` at all AND the whole sheet's shots sum > 15 s** (an old single-sheet that was never chunked) → same STOP: ask for a re-build so it gets chunked into ≤15 s clips.

Never auto-compress. Never auto-truncate. A render with dropped shots looks "OK" at first glance but loses entire scenes — that's the silent failure this fail-fast prevents.

## ────────────────────────────────────────
## STEP B — Render one `generate_video` per GROUP OF PANELS (e.g. panels 4–7 → ONE video; that group is called a "clip") — never one-per-panel, never one-per-sheet — SEQUENTIALLY with frame-chaining
## ────────────────────────────────────────

One `generate_video` per **clip**, where a **clip is a GROUP of consecutive panels** — its `metadata.clips[].panels` array. Example: `panels: [4,5,6,7]` → **ONE rendered video** that animates panels 4 through 7 as a single continuous clip. So, to be crystal clear:

- **NOT one video per panel.** Panels 4–7 are ONE video, not four. A clip almost always spans several panels.
- **NOT one video per sheet.** A 12-panel sheet might be 3 clips → 3 videos (e.g. clip 1 = panels 1–4, clip 2 = panels 5–9, clip 3 = panels 10–12).
- The unit is the **clip** (a panel range), resolved from `metadata.clips` in Step A.

**Tell the model which PANELS are this clip's frames.** Cite the clip's `panels` range explicitly in the prompt: *"Use `Image 1` as the blueprint but follow ONLY panels 4–7 — they are THIS clip's beats, in order; ignore the sheet's other panels (they belong to other clips)."* That's what lets one sheet feed several clips without content bleeding between them.

**Several panels can belong to ONE continuous take (one CUT): animate THROUGH them, never cut between them.** A CUT is NOT always one panel. Two cases, SAME handling:
- **(a) A camera-movement shot's 2-3 keyframe panels** (they share that shot's `shotId`): the start / middle / end of one move (push-in, pan, crane…).
- **(b) Consecutive shots flagged `noCutBefore`** (or sharing a `number`): a glued continuous take / plano secuencia, authored as several shots but with NO cut between them.

In BOTH cases those panels are ONE CUT: cite ALL of them in that cut's panel reference and move smoothly through them as a single continuous take, the action progressing panel by panel, with NO internal cut. A real cut (cambio de plano) falls ONLY where the JSON is NOT glued (a shot WITHOUT `noCutBefore`).

**Render the clips SEQUENTIALLY, not in parallel.** Render clip 1, wait for it to land, then render clip 2 passing clip 1 as a `referenceVideos` entry. Repeat for clip 3 with clip 2 as its reference video, and so on. Reasons:

- **Full motion/state context, not just a still frame.** Passing the PREVIOUS RENDERED VIDEO as a reference gives the model the actual movement, lighting evolution, debris trajectory, character pose progression — everything the still last-frame would lose. The seam at the cut inherits not just a matching pixel state but matching CAMERA ENERGY and CHARACTER MOMENTUM, so the next clip continues naturally instead of restarting cold.
- **World-state continuity carries automatically.** If something got broken/dirtied/moved in clip K-1, the reference video carries every visual consequence — clip K can't silently reset to a pristine state.
- **You can sanity-check before committing the next render.** A wrong clip K-1 (wrong action, drifted identity) is cheaper to re-roll once than to discover after spawning all N renders in parallel.

Sequential flow per clip K ≥ 2:

1. Wait for clip K-1 to complete and verify its `savedTo` exists.
2. In the next clip's `generate_video` call, include the previous clip's path in `referenceVideos` (alias it e.g. `prev_clip`). Keep the rest of the reference setup (the clip's OWN sheet + every prior sheet + character / product refs).
3. Render. Wait. Repeat for clip K+1 with clip K as the new `prev_clip`.

Use ONLY the IMMEDIATE predecessor as `prev_clip` — the chain is 1→2, 2→3, 3→4. Don't pile up every earlier clip into `referenceVideos`; the last sheet covers older history and the immediate predecessor covers state at the seam.

Clip 1 has no predecessor — render it normally (no `referenceVideos` unless the user supplied an external opening reference).

> 🛑 **MANDATORY — ATTACH THE REFERENCES ON EVERY CLIP. This is not optional.** A clip rendered from text alone has no visual blueprint, no character identity and no continuity — it will drift from the storyboard. Before every `generate_video` call, attach, in this order:
> 1. **The panel sheet(s)** — the current sheet (`sheet_part_K`) ALWAYS; for K ≥ 2, also every prior approved sheet (`sheet_part_1 … sheet_part_{K-1}`).
> 2. **The reference images** — when the storyboard / manifest carries character / product / location refs that this clip needs (recurring subjects), append them after the sheets. Pull them from the `references` manifest AND the interactive storyboard's `references` arrays (root + scene + shot), resolving `@handle`s.
> 3. **The previous clip** (K ≥ 2) — pass clip K-1 in `referenceVideos` as `prev_clip` (→ `Video 1`) for seam continuity.
>
> The tool now **REJECTS the call** (`success:false`) if your prompt cites `Image N` / `Video N` but those slots aren't attached — so the citations in the prompt body and the attached files must always match. If you cite `Image 1` (the sheet) you MUST attach the sheet.
>
> **Pre-call self-check — do it on EVERY call, it takes two seconds and prevents the most common failure:** count the entries in `referenceImages`; the highest `Image N` you cite anywhere in the prompt body MUST equal that count. Same for `referenceVideos` ↔ `Video N`. If a reference you wanted to cite is NOT actually attached — it didn't resolve, you don't have its path, or you're rendering clip 1 with only the sheet — then DO NOT write `Image N` / `Video N` for it: describe that subject in plain words instead (e.g. "a tall woman with dark wavy hair in a red coat") and only cite the positions you really attached. A dangling `Image 2` with a single image attached makes the tool reject the entire call and forces a retry — which is exactly the loop to avoid. Never invent a citation hoping a file is there.

For each CLIP (in global `clipIndex` order across all sheets), call `generate_video` with:

- **`prompt`** — composed per "Per-clip prompt construction" below; it MUST cite the clip's `panels` on its sheet (Step B).
- **`referenceImages`** — first entry is the clip's OWN sheet, alias `sheet_part_K` (K = that sheet's index; or `storyboard` for a single-sheet storyboard). When the clip sits on sheet ≥ 2, ALSO include every prior approved sheet (`sheet_part_1` … `sheet_part_{K-1}`). Then append the `references` manifest entries (`hero_character`, `product_pack`, …), each as `{ alias, path }`. **Order is load-bearing** — position 1 in the array IS `Image 1` in the prompt body. Aliases are semantic names for the auto-legend and debug logs; the prompt cites positions (`Image 1`, `Image 2`, …), not aliases. Decide the order before writing the prompt.
- **`referenceVideos`** (K ≥ 2 ONLY) — `[{ alias: "prev_clip", path: <clip K-1's savedTo> }]`. The previous rendered clip becomes the model's motion / state / camera-energy reference. Cited as `Video 1` in the prompt body. Videos have a counter independent of images. Omit for K=1. Only the IMMEDIATE predecessor — never pile up earlier clips here.
- **`duration`** — the CLIP's resolved duration from STEP A (`clip.durationSec`, a whole second within the tool-reported `[D_min, D_max]`). NOT a hardcoded number, NOT the sheet's total.
- **`aspectRatio`** — the target `aspect_ratio` (platform). MANDATORY: the clip must come back already framed for the destination (9:16 Reels/TikTok/Shorts, 16:9 YouTube/web, 1:1 / 4:5 Instagram). The sheet stays 16:9 (a reading surface); the model reframes it at render. Rendering 16:9 clips into a 9:16 timeline gives black bars — a ship-stopper.
- **`quality: "high"`**.
- **`withAudio: true`** — ALWAYS set it to `true` (its default is `false`, so OMITTING it = a silent clip = a hard failure). **`withAudio` controls the clip's DIEGETIC sound: SFX, dialogue, voiceover, ambient. It does NOT control music.** Do NOT confuse "no background music in this clip" with "no audio": excluding music is done ONLY by the PROMPT's closing Audio line (see below), NEVER by `withAudio`. Setting `withAudio: false` to keep music out ALSO kills the SFX/voices the scene needs. The ONLY time `withAudio` may be `false` is a deliberately, fully silent clip with zero SFX/dialogue/ambient (essentially never for a storyboard scene).
- **`saveTo: <a directory>`**.

### Per-clip prompt construction

The prompt is a **director's brief**, not a checklist or compliance form. Natural language, structured but flowing. No decorative banners, no caps-shouting, no "use this exact wording" verbatim blocks — models respond better to a concise brief than to a 700-word bookkeeping form.

The interactive storyboard JSON is the script for this clip: per shot it carries the **duration**, **shot / framing / angle**, **camera movement**, **action**, and **sound** (`dialogue` / `sfx` / `music` / `audio`). Transcribe that into the brief — it is the authority, not the tiny labels on the sheet image.

**Reference syntax — positional naming (`Image 1`, `Image 2`, … `Video 1`).** Video model providers explicitly recommend positional references for accurate binding: *"When uploading images in a specific order, use Image 1, Image 2 … Image N in your prompt for accurate referencing."* Images and videos have **separate counters** — the first image is `Image 1`, the first video is `Video 1`. The alias you pass to the tool call (`{ alias: "sheet_part_K", path }`) is a semantic name for the auto-legend and debug logs — the **prompt body cites positions, not aliases.**

Canonical order — decide BEFORE writing the prompt and stick to it: current sheet (`sheet_part_K`) first, prior sheets (`sheet_part_1` … `K-1`) next, then identity refs (character, product, location), then `prev_clip` as `Video 1`.

The runtime auto-prepends a one-line legend (*"Image 1 = sheet_part_K, Image 2 = sheet_part_1, …, Video 1 = prev_clip"*) — you don't need to repeat it. Just cite `Image N` / `Video N` directly in the prompt body.

Build the prompt in this 5-part shape:

#### 1. References block + format line (header)

State each reference's role in plain language, citing it by position, then declare the format. **Crucially, name THIS clip's panel range on the sheet** — the clip's `panels` (e.g. *"follow ONLY panels 4–7 of `Image 1`, in order — they are this clip's beats; ignore the rest of the sheet, they belong to other clips"*) — so the model animates the right portion of a multi-clip sheet. If those panels include a camera-movement shot's 2–3 keyframes, say so: *"panels 5–7 are the start/middle/end of one continuous push-in — move smoothly through them, don't cut."*

Pattern: *"Use `Image 1` as the authoritative shot blueprint — follow its exact beat progression, framing structure, and emotional pacing. **Do NOT render the panel sheet itself: ignore its borders, panel frames, text labels, duration tags, headers, swatches and any chrome.** Use `Image 2` (and any further character / product / location refs at `Image 3` …) as the authoritative `<subject>` reference — match face, build, hair, wardrobe / paint, lights, badge exactly in every shot of this clip and every other clip."*

Append the format line on the next sentence: *"Create a cinematic `<duration>`-second `<aspect>` `<type>` video [of `<subject>`]."* The aspect comes from the target platform, not the sheet's 16:9 reading frame.

#### 2. `Video 1` continuation block (K ≥ 2 ONLY, ~80–110 words)

One paragraph covering BOTH halves: the temporal-continuation contract AND the photos-beat-prev_clip identity rule. **Both halves are non-negotiable** — the first prevents world-state reset between clips, the second prevents identity drift from propagating across clips.

Pattern (substitute K and the actual image positions for the identity refs): *"`Video 1` is PART {K-1} of this multi-PART video. PART K continues DIRECTLY from its last frame: same camera energy, same character momentum, same lighting, same world-state. Anything broken, moved, consumed or dirtied at the end of `Video 1` stays that way at t=0 — do not reset the scene. For identity, the photo references (`Image 3`, `Image 4`, …) beat both the panel sheet and `Video 1` — `Video 1` is a generated approximation and may have drift (hairline, wardrobe shade, paint tone, prop detail); pull identity from the photos, not from `Video 1`. Hierarchy: reference photo > sheet > `Video 1`, for everything identity-related."*

`Video 1` is the IMMEDIATE predecessor only (clip K-1). Older history (PART 1 … K-2) is covered stylistically by their sheets at positions `Image 2` … `Image {K-1}` in `referenceImages`.

Omit this entire block for K = 1.

#### 3. Style brief (1 dense comma-separated line)

Palette, lighting, texture, mood — the look the clip aims for, pulled from the storyboard's `style` / `lighting` / `aspect` fields when present. Push the style language into motion / cinematic terms:

- **3D animation / family-film** — animation principles (squash & stretch, anticipation, follow-through), warm practicals, volumetric light, expressive readable silhouettes.
- **Live-action / cinematic** — film grammar (handheld, Steadicam, crane), practical / motivated lighting, subtle performance, naturalistic ambience.
- **Anime** — speed lines, impact frames, dramatic snap zooms, limited animation on holds, sakuga for action peaks, particle effects, light bloom.
- **2D / hand-drawn** — smears and multiples, held poses with moving holds, consistent line weight, painterly backgrounds, parallax layers, fluid secondary motion.
- **Stop-motion / claymation** — handcrafted clay or puppet aesthetic, visible material texture, miniature set design, tungsten warm light, soft shadows.
- **Other** — adapt accordingly; the brief should read like a creative director's line, not a checklist.

Example: *"Final style: premium hospitality brand film, warm coastal daylight, white-and-gold palette, clean editorial framing, subtle 35mm texture, smooth transitions, no on-screen text."*

**Continuity lock (1 short paragraph, right after the style brief) — when the JSON carries `synopsis` and/or `continuity`.** State the story premise in one line, then list the `continuity` rules as ABSOLUTE constraints the whole clip must obey and never "fix". These are the negatives the model won't infer on its own. Pattern: *"Story premise: the boy can't reach the high Pepsi button, so he stacks cans to climb. Hard continuity rules, true in every shot: the Pepsi button stays mounted high and out of reach until he is up on the cans — never lower it or make him taller; the cans he stands on stay intact, never crushed; same machine, same can colours throughout."* Omit only when the JSON has neither field. This block is cheap (~40–70 words) and is the single most effective guard against the "unreachable became reachable" / "the step-object got destroyed" drift.

**Per-tool tailoring** (when `targetGenerator` is given):
- **Seedance** excels at character animation and lip-sync — prioritise expressive character beats and dialogue moments; keep camera moves moderate.
- **Kling** handles dynamic camera — push ambitious moves (orbits, crane, push-ins).
- **Sora** handles cinematic composition — emphasise framing, lensing, and shot grammar.
- **Veo** handles long coherent sequences — let shots breathe; longer holds are OK.
- **Runway / Luma / Hailuo / Wan / Higgsfield** — model-agnostic, conservative camera language unless the user signals otherwise.

#### 4. Numbered CUTS — director's beats (one CUT per JSON shot)

> 🛑 **FAITHFUL TRANSCRIPTION, NEVER INVENT A SHOT. This is the #1 rule of this step.** The CUTs come ONLY from the JSON's shots for THIS clip (never invented), in JSON order. A CUT is one continuous TAKE: most shots are their own take, but a camera-movement shot's keyframe panels AND a run of `noCutBefore`-glued / shared-`number` shots collapse into ONE take (see "Several panels = one continuous take" above). Split this clip's shots into takes (a real cut falls ONLY where a shot is NOT glued to the previous) and emit EXACTLY one CUT per take, no more, no fewer. Do NOT add, drop, reorder, invent, or split a continuous take into extra cuts, and do NOT merge two real takes: no made-up establishing / reaction / transition / cutaway / insert beat the storyboard doesn't have. Each CUT's direction IS its shot('s) `action` (plus `continuity` / `dialogue` / `sfx`), transcribed faithfully, NOT a reimagined or embellished scene.
>
> Your ONLY two inputs are: (1) the **interactive storyboard JSON = the script** (what happens, in what order, for how long), and (2) **THIS clip's panels on the CURRENT sheet = the look**. Reference ONLY this clip's panels (its `panels` range) on the current sheet; ignore other clips' panels and any other sheet. If a shot's `action` is terse or unclear, render exactly what the JSON says and only tighten the physical mechanics (point 4 below); NEVER fill a gap by inventing a new plano or guessing extra coverage.
>
> **Inventing planos, or a CUT count that doesn't match the JSON's real cut boundaries for this clip, is the reported bug ("se inventa algunos planos"). Before writing the CUTs, split the clip's shots into continuous takes (a `noCutBefore`-glued run = ONE take) and state the count: "this clip has N takes → N CUTs", then make the list match.**

**Build the take ↔ panel(s) correspondence FIRST — it's how each CUT gets its exact panel reference.** The mapping is NOT "shot N = panel N", and a CUT can own SEVERAL panels. Walk this clip's shots **in JSON order** alongside its `panels` **in ascending order**, assigning panels to the current take until the clip's `panels` range is fully consumed:
- a **STATIC shot** consumes exactly ONE panel and is its own CUT;
- a **CAMERA-MOVEMENT shot** consumes its 2-3 consecutive keyframe panels (same `shotId`) as ONE CUT;
- a **`noCutBefore`-glued run** (consecutive shots flagged `noCutBefore`, or sharing a `number`) does NOT open a new cut: the glued shot's panel(s) accumulate onto the SAME CUT as the previous shot — several shots, several panels, ONE continuous-take CUT.

The result is a clean 1:1 **take ↔ CUT**; each CUT's panel reference (item 2) is ALL the panel(s) its take consumed. Worked example A — shots `[static, move, static]` over panels `[4,5,6,7]`, middle shot a 2-panel camera move → **CUT 1 → panel 4, CUT 2 → panels 5-6, CUT 3 → panel 7**. Worked example B — a 3-shot plano secuencia where shots 2 and 3 are `noCutBefore` over panels `[1,2,3]` → **ONE CUT → panels 1-3** (the action progresses across the three panels, no internal cut). (Σ panels assigned MUST equal the clip's full `panels` count; if it doesn't, recount the camera-move expansions and glued runs.)

ONE entry per continuous TAKE (not per panel, and not always per shot): sub-beat panels of one shot AND a `noCutBefore`-glued run of shots are ONE continuous take, so they share a single CUT. **Lay each entry out as a CUT HEADER LINE with the description directly BELOW it, never crammed inline.** This is the REQUIRED format (it reads as a real cut list):

```
CUT 1 (0:00 - 0:01.5)
WS, Steadicam. Dense crowd milling through a narrow stone alley; Jasón seen from behind, matching their slow pace. Use panel 1 of `Image 1` (the sheet) as the visual reference for this cut. SFX: market murmur, distant haggling.

CUT 2 (0:01.5 - 0:03)
LS. Three Roman legionaries marching in formation, shoving merchant stalls aside with large red rectangular shields. Use panel 2 of `Image 1` as the visual reference for this cut.
```

Each entry carries:

1. **CUT header: `CUT N (START - END)` with the RUNNING timecode, on its OWN line.** The timecode is a CUMULATIVE clock WITHIN this clip: it starts at `0:00`; each cut spans its TAKE's duration (the sum of its shot('s) `duration` — a glued multi-shot take sums all of them), so CUT N's START is the running total of all previous takes and its END is START + this take's duration. Format `M:SS`, with a decimal ONLY when the boundary is fractional (`0:01.5`, not `0:01`). Worked example (shots of 1.5 s, 1.5 s, 2 s): `CUT 1 (0:00 - 0:01.5)`, `CUT 2 (0:01.5 - 0:03)`, `CUT 3 (0:03 - 0:05)`. The END of the LAST cut MUST equal the clip's resolved duration (STEP A); if it doesn't, you mis-summed the shots, redo.
2. **Panel reference (ALWAYS): tie the cut to its EXACT frame(s).** On the description line, name THIS cut's panel(s) and tell the model to use them: *"Use panel X of `Image 1` (the sheet) as the visual reference for this cut."* A cut may own SEVERAL panels (a camera move's keyframes, or a `noCutBefore`-glued continuous take) — then cite ALL of them and say they are one continuous take: *"use panels 5-7 of `Image 1` as the start, middle and end of this single continuous take, no cut between them."* Panel numbers come from the take↔panel map you built above. This pins each cut's look to the EXACT frame(s) the user approved on the sheet so the rendered shot matches the panels instead of drifting. It is the single most important fidelity line: never omit it.
3. **Framing + camera:** shot size (CU/MS/WS/…), angle, and movement (dolly-in, orbit, static, …) in cinematic verbs, at the START of the description line (optional but recommended: the "si quieres el tipo de tiro" the user asked for).
4. **Scene direction** — what happens: blocking, staging, environmental action, character acting beat. Keep it tight — one sentence per shot is plenty; the storyboard image + identity refs carry the look, so the prose only needs to drive the motion. **🔬 But nail the PHYSICAL MECHANICS of the action — the model renders your words literally and improvises a plausible-but-wrong detail for anything vague.** Singular over loose plural ("inserts a single coin held between thumb and forefinger" — NOT "inserts coins", which renders as a hand fanning several at once); name the grip / finger / posture (not "presses the button" but "presses the low button with his index finger"); zero ambiguity — every target a concrete identifier ("button 2 of 16", "the red suitcase on his left"), never an interpretable one ("his floor", "his suitcase"); one mechanical step per shot, done the way a real person does it. **🎬 CONTINUITY / raccord (most-neglected — get this right): carry the established state into EVERY shot's prose, or the model drops it.** Once a shot establishes a non-default state (standing ON the stacked cans, holding the can, a melted hole, soot on the face), every later shot where it still holds MUST restate it — *"still standing on the two stacked cans, he presses the Pepsi button"*, NOT just *"presses the Pepsi button"* (which renders him back on the ground — the exact bug). The state lives in the TEXT of each shot until one explicitly changes it; same object/hand/world state, lighting and screen direction across the cut. **⚠️ The source `action` may have been written by the USER and be incomplete — a later shot may drop a state that's clearly still in effect. DO NOT inherit that omission:** read the whole shot range, track the world/character state yourself, and restate the carried-forward state in every shot where it still logically holds, EVEN IF that shot's `action` dropped it. You never invent a new EVENT — you only re-inject the established state the source forgot. The video is the LAST line of defence against a sloppy storyboard, so here raccord must be airtight. This is the *"everything's right except the details / continuity"* fix. **When the JSON shot carries a `continuity` field ({ characters, objects }; or a legacy `state` string), that tracking is already done — it IS the authoritative current-state for that beat; transcribe both columns into the shot direction ("still standing on the two intact stacked cans, he presses the high button") instead of re-deriving it. If a shot's `continuity` contradicts a neighbour (crushed here, stood-on next), the source is self-contradictory — render the physically coherent reading the `synopsis`/`continuity` LOCK imply and surface the conflict to the user; never animate the impossible state.**
5. **Dialogue** (if any) — `Character: "<line>"`.
6. **SFX** — sound effects and ambient audio inline at the end.

Example (one cut, in the required layout):

```
CUT 5 (0:04 - 0:05)
CU low-angle, slow dolly-in. Ruby's gloved hand brushes red dust, revealing a green sprout; focus racks from hand to leaf. Use panel 5 of `Image 1` as the visual reference for this cut. SFX: faint suit-radio static, soft regolith crunch.
```

When the JSON is absent, treat each sheet panel as its own shot.

The cuts in the rendered video fall WHERE THE JSON CHANGES SHOT — your numbered list IS the cut list.

**🎯 CAMERA VIEWPOINT — when the panel shows a non-default angle (rear, side, POV, overhead, low-angle), state it inline AND negate the opposite in the same sentence.** Video models default to a front hero shot otherwise (a *"from behind, drives away"* panel routinely renders as a front hero shot). The reference image anchors LOOK / identity, NOT framing — the angle must be forced in words.

- rear → *"Camera behind the car, rear only — taillights and diffuser visible, driving away from camera. No front, no headlights."*
- POV / first-person → *"First-person POV, the subject's hands visible at the bottom of frame interacting with the object. The subject themselves is never shown — only their hands and arms."*
- side / over-the-shoulder / top-down / low-angle — same pattern: name the angle inline and negate the opposite.

**🎬 Causal order.** The world state advances chronologically — never show the aftermath before its cause (no wrecked room before the wrecking, no empty plate before it's eaten). The shot numbers ARE the causal order; the narrative across them must respect it. No need for a separate "SEQUENCE COHERENCE" paragraph — the numbered list already implies it.

**Don't re-describe the visual STYLE in prose for every shot** — the sheet render + the style brief (point 3) carry it. Don't re-name the subjects' appearance per shot — the named `referenceImages` carry that.

**Don't reproduce the sheet's chrome.** The old "preserve on-screen text" instruction is gone — it made the model copy the storyboard's captions / borders into the video. Point 1 above already forbids reproducing the sheet; reaffirm here that no in-panel labels, frame numbers, duration tags or banner text bleed into the final clip. The only text that may appear is genuine in-WORLD text physically part of a depicted object (a product label, a street sign that's part of the scene), and that comes from the subject `referenceImages`, never from the sheet.

#### 5. Closing audio line

End the prompt with a single audio philosophy line — picked from the audio plan:

- **Single-sheet video, or music baked into the clip:** *"Audio: Diegetic sound only — natural ambience, environmental foley, and subject-driven sound."*
- **Multi-sheet with separate music track on the timeline:** *"Audio: Diegetic SFX, dialogue and ambience only — music is laid on a separate timeline track and is not part of this clip."*

This closing line establishes the overall audio philosophy for the generation. Individual shots still include their own SFX notes inline; the closing line covers the music question.

**`withAudio: true` is a tool parameter, NOT prompt text.** Don't write `withAudio: true` into the prompt body — that's the runtime contract for SFX/dialogue/ambient. The prompt's audio job is to describe the diegetic soundscape inline in the shot directions + this closing line about music exclusion. NEVER set `withAudio: false` to keep music out — that silences SFX and voices too.

### Word-count targets

The new per-shot structure adds some weight vs the pre-merge narrative style, but the brief still compresses. Targets:

- **K = 1, ≤ 6 shots:** ~250–400 words total.
- **K = 1, 7–10 shots:** ~400–600 words total.
- **K ≥ 2 (any shot count):** add ~80–110 words for the `Video 1` block. The `prev_clip` paragraph is the only non-negotiable cost — the rest still compresses.

Don't pad, but don't sacrifice per-shot clarity — every shot needs enough motion direction for the model to differentiate it from the next.

## ────────────────────────────────────────
## STEP C — Music track (single, full-length, only when needed)
## ────────────────────────────────────────

When the audio plan calls for music AND there are **≥ 2 sheets**: generate music as ONE separate track, not per clip. Independent clip renders can't keep a continuous melody across the seam, so per-clip music thumps every clip boundary.

- ONE `generate_audio` call, `type: "music"`, `duration: <total video seconds = sum of all clip durations>`, `prompt` derived from the type's music brief + tone.
- Single-sheet video (one clip, no seams): music inside the clip render is fine — skip this separate track if the clip already carries it.
- Voiceover-only / SFX-only plans: no music at all — skip.

## ────────────────────────────────────────
## STEP D — Assemble the timeline (concatenate every clip into one video)
## ────────────────────────────────────────

Follow the `timeline-assembler` skill. The shape:

1. **Always `create_timeline` a NEW timeline** — one fresh timeline per video built from storyboards. NEVER reuse, append to, or overwrite an existing timeline (the user's other timelines stay untouched). Give it a descriptive `name` (e.g. the storyboard / video title) and the target `aspectRatio`. Do NOT pass fps / width / height — inheritance handles it. Keep the returned `timelineId` — it's what you show at the end.
2. **V1 — concatenate the clips in order, back-to-back, using each clip's OWN duration.** Walk a cumulative cursor; do NOT assume uniform 15 s slots:
   ```
   cursorMs = 0
   for clip in clips (in sheet order):
       add_clip_to_timeline(track="V1", path=clip.path,
                            startMs=cursorMs, durationMs=clip.durationSec * 1000)
       cursorMs += clip.durationSec * 1000
   ```
   `add_clip_to_timeline` auto-detects each clip's audio stream and wires it into the mix — do NOT pass `hasAudio`.
3. **A2 — music** (if generated in STEP C): one clip at `startMs: 0`, `durationMs: totalMs`. **Duck it ONLY where it competes with voice — decide from the actual audio, don't duck reflexively:**
   - Clips/sections that carry **voiceover or dialogue** → duck the music there to ≈ −28 dB (`set_clip_volume(<musicClipId>, { change: { gain: 0.04 } })`, or `volumePoints` for the speaking stretches) so the words sit on top.
   - Sections with **NO voice** — music scoring an action beat, an intro/outro, a wordless montage, SFX-only — **do NOT duck.** The music is the main audio there; ducking it to −28 dB makes the scene sound empty. Leave it at a normal present level.
   - Whether to duck is the agent's call based on whether voice is actually present in the video (from the storyboard's `dialogue` / voiceover plan). A music-only / action-driven video with no narration gets NO duck. See the assembler skill's "Audio mixing levels".
4. (Optional) subtitles for tutorial / explainer per the assembler skill's "Subtitles" matrix.
5. **Hand-off — ALWAYS end by showing the TIMELINE.** Sequence: `show_result({ resourceType: "timeline", timelineId })` (preview the assembled timeline) → `render_timeline` → then the FINAL artifact you show is the **timeline that contains the video**: `show_result({ resourceType: "timeline", timelineId })`. The timeline is where the finished video lives — opening it lets the user play, tweak, and re-render. You MAY also `show_result({ resourceType: "video", path })` for the rendered file, but the timeline show is mandatory and is the last thing the user lands on. Full sequence in the assembler skill's "The render hand-off."

The final video length = the sum of the per-clip durations (which, when the interactive storyboard is present, equals the storyboard's total duration). Concatenation is timeline-only — NEVER `ffmpeg concat` or any other glue tool; the timeline handles multi-track mix, per-clip durations, aspect reframe and crash-safe state.

## Continuity formula (Seedance-class multi-shot models) and reference hygiene

**Reference hygiene: pass CLEAN panel crops, never the raw sheet, when the model accepts several references.** Feeding the whole panel SHEET (with gutter lines, borders and any baked chrome) as the visual blueprint contaminates the render: the grid lines bleed into textures as banding/striping artifacts (reported: striped lines across a character's hair). Extract each clip's panels with `extract_panel` (clean crops, no gutters, no numbers) and pass those as the shot blueprint images, plus the separate character/prop reference images. Only fall back to the whole sheet when the model's reference slots cannot fit the crops, and then keep the explicit "ignore the sheet chrome" negative.

**Panels are ACTION REFERENCES, never start frames: say it in the prompt.** A panel depicts one representative moment WITHIN its cut (often mid-action), not the cut's first frame. Two rules: (1) input-side, never pass a panel (or the sheet) as `startFrame` (only frame-chained final frames from the previous clip qualify as start frames); (2) PROMPT-side, make the role explicit in the generated text, per cut and once globally: e.g. *"the panels of Image 1 are reference stills of a moment WITHIN each cut, NOT starting frames: begin each cut naturally before its reference moment and flow the motion through it"*. Without this, Seedance-class models freeze the panel as the literal first frame and every cut starts as a still photo of the panel (reported).

**The multi-shot continuity formula (what actually keeps cuts coherent):**
1. **Identical subject nouns in every cut.** Describe each character with the SAME short noun phrase in every CUT block ("the MASTER", "the DISCIPLE"); re-describing them differently per cut is what makes the model re-cast them.
2. **Same reference set for every clip of the sequence.** The exact same character/prop/set images ride on every generate_video call of the piece, in the same order.
3. **Lock lighting and set phrasing verbatim** across cuts and across clips (copy the same sentence, do not paraphrase).
4. **Max ~5 camera setups per generation.** Seedance-class models hold hard cuts + consistency reliably up to about 5 shots per clip: if a clip's storyboard beats exceed that, split it into two generate_video calls chained by frame.
5. **FRAME-CHAINING is the plano-secuencia formula (anchor-and-extend):** for full continuity between consecutive clips, extract the FINAL FRAME of the rendered clip N and pass it as the FIRST frame / anchor reference of clip N+1 (the provider's startFrame/lastFrame params when available, else first reference image with "continue exactly from this frame"). This preserves set, wardrobe, light and positions across the join better than any text.
6. **True plano secuencia (one continuous take, no cuts):** describe it as ONE shot with a single continuous camera move (never CUT blocks), and generate it as one clip; if it exceeds the model's duration cap, split at a motivated camera moment and frame-chain (rule 5): the join reads as an invisible cut.
7. **One master audio bed:** keep music OFF the clips (separate timeline track, as this skill already does) and describe only diegetic SFX per cut, so joins never fight the soundtrack.

## Voice consistency across clips (read once)

With `withAudio: true` the voiceover is generated independently per clip; reference-to-video models match the voice to the visible character, so passing the same character ref across sheets gives high-but-not-guaranteed consistency. If the voice audibly drifts between clips, the deterministic fallback is: `withAudio: false` on every clip (silent), generate ONE TTS pass of the whole script via `generate_audio` with a fixed `voice`, and lay it as a second audio track. Trades lip-sync precision for identical voice — use only when drift actually shows up.

## Iteration

**Specific clip needs a re-roll:** call `generate_video` again for that sheet with the same references and a revised prompt that adjusts only the affected per-shot directions (point 4). Keep the rest (references block, `Video 1` block, style brief, audio line) identical so the diff is surgical. For K ≥ 2 the prev_clip still points at clip K-1; if K-1 itself was re-rolled, propagate forward (K's prev_clip is K-1's NEW path).

**Total duration change:** re-resolve per-CLIP durations in STEP A; the JSON's per-shot weighting (relative durations) usually scales naturally — don't uniformly scale unless the user said so.

**Target generator changes:** swap the per-tool tailoring paragraph (point 3) and re-render. The shot grammar stays; only camera-language choices shift.

## Don't

- Don't hardcode `duration: 15` per clip — use each CLIP's resolved duration (`clip.durationSec`, STEP A); the interactive storyboard is the timing authority.
- **Don't search disk for the storyboard JSON.** `shell ls .koi/storyboards/`, `read_dir`, `recall_creations` of kind `storyboard` to "find what the sheet might come from" — all banned. The metadata link is the only auto-recovery; if it's missing, read the sheet's pixels (vision) and use those as the authority. NEVER pick a JSON whose content has nothing to do with the sheet's visible scene — that's the reported confabulation bug *"de repente cambia de tema, era un viejo con un reloj de bolsillo y dijo que era un storyboard de SOC 2 compliance"*.
- Don't compress a >15 s CLIP into a 15 s render by dropping shots — STOP and ask the user to re-chunk upstream (see STEP A's fail-fast). (A SHEET may exceed 15 s — that's fine, it holds several clips; only a single CLIP must stay ≤15 s.) Silently truncating is the reported *"ha hecho los 15 segundos pero no de todo el storyboard sino solo de una parte"* bug.
- Don't render one clip per panel, and NOT one clip per sheet either — render one clip per **CLIP** (a panel range from `metadata.clips`, e.g. panels 4–7 → one video). A sheet can be several clips.
- Don't treat the panel sheet as a layout to copy — its annotations (numbers, titles, captions, legend, footer notes, borders, frame lines) are PLANNING marks. The reference exists ONLY to keep the imagery consistent; the clip reproduces the SCENE picture and NONE of the annotations or borders.
- Don't burn ANY text into the video — no titles, captions, labels, subtitles or descriptions (e.g. "EL QUESO", "SALTA EL GATO"). Spoken lines are AUDIO, not on-screen text.
- Don't drop the JSON's per-shot direction — DO put each shot's framing, camera movement, action, timing and sound into the prompt (STEP B point 4). What you DON'T re-describe is the visual STYLE and the subjects' appearance (the sheet render + named references carry those).
- Don't add cuts the storyboard JSON doesn't have — the cuts (cambios de plano) are FAITHFUL to the JSON. A real cut falls ONLY where a shot is NOT glued to the previous; sub-beat panels of one shot AND a `noCutBefore`-glued run of shots are ONE continuous take (one CUT, possibly several panels), never separate cuts.
- Don't let the model flip the camera viewpoint — if a panel is a REAR / side / overhead / POV shot, force it in words AND negate the opposite ("rear only, no front/headlights"). The model defaults to a front hero shot otherwise.
- Don't break causal order — never show the aftermath before its cause (no wrecked room before the wrecking, no empty plate before it's eaten). The scene state only advances.
- Don't reset the world state between clips — PART K opens in the state PART K-1 ended in (damage / mess / changes persist).
- Don't bake music into per-clip renders when stitching ≥ 2 sheets — separate full-length track via STEP C.
- Don't duck the music reflexively — duck it ONLY under voiceover/dialogue; leave ambient/action music (no voice) at a normal level. The agent decides from whether voice is present.
- Don't ship a silent clip — `withAudio: true` ALWAYS (default is false → omitting it = silent). `withAudio` carries SFX/dialogue/ambient; it does NOT control music. NEVER set `withAudio: false` to keep music out — that kills SFX/voices too. Exclude music via the closing audio line (point 5) only.
- Don't render clips in 16:9 for a vertical target — pass the platform `aspectRatio` to every `generate_video`.
- Don't concatenate outside the timeline (no `ffmpeg concat`).
- Don't reuse / append to an existing timeline — `create_timeline` a NEW one for every video built from storyboards.
- Don't finish without `show_result`-ing the TIMELINE that holds the final video — it's the mandatory last artifact the user lands on.
