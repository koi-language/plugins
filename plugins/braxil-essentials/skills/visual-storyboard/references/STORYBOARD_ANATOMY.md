# Storyboard Anatomy — Phase 1 Spec

This file is the **authoritative spec** for building a 4K visual panel sheet from a story idea + character references. It is the prompt template that produces the sheet image, plus the workflow that gets you there. The `visual-panels` skill's `SKILL.md` is a thin entrypoint that delegates to this file — read THIS one before writing any prompt.

The output is a single composite image (the SHEET) generated via `generate_image` at 4K. **Never deliver the raw prompt text to the user as the deliverable** — the artefact is the rendered image.

---

## Step 1 — Gather inputs

⛔ **GATHER FIRST — then ask ONLY for what's genuinely missing.** Before any `generate_image` call you need (1) the visual style and (2) each recurring character's reference. But do NOT blindly open a form: first HARVEST what the user already provided —
- **style** from anything they said ANYWHERE in the conversation, OR a NON-EMPTY `stylePrompt` in the source storyboard JSON;
- **character refs** from the user's attachments OR the storyboard's `references`.

Raise the `prompt_form` ONLY for the fields still unknown after harvesting — and skip the form ENTIRELY when nothing is missing. The hard rule is: NEVER **infer** the style from the topic/brand/vibe — if it isn't provided anywhere, ask; never guess. (Opening the full form when the user already gave the style, or it's set in the JSON, is its own reported bug: *"¿por qué me pregunta si ya se lo dije / si ya está en el storyboard?"*)

### The form — 3 fields, ONE wizard, in this order

ALL three fields live in the SAME `prompt_form`. Never split into multiple `prompt_user` rounds. Pre-fill any field the user already answered in their initial message.

#### Field 1 — Visual style (required)

A SELECT with the 3 official presets + a custom option:

- **Premium 3D** — Pixar / DreamWorks family-film aesthetic
- **Claymation** — handcrafted stop-motion plasticine
- **Realistic UGC** — phone-shot social-media aesthetic
- **Custom** — opens a free-text field; user describes it in 1–2 sentences and you compose the phrasing block per `STYLE_PRESETS.md`'s custom-style flow

The phrasing blocks for the 3 presets live in `STYLE_PRESETS.md` (`<skill_directory>/references/STYLE_PRESETS.md`). Read that file BEFORE composing the prompt so the ready-to-paste block lands in section B verbatim.

**NEVER infer the style from the brand, topic, or story's vibe.** A Chanel storyboard is not automatically "live-action luxury", a Pokémon storyboard is not automatically "anime", a kids' product is not automatically "3D family-film" — the user picks the style, not you. **But DO use the style the user actually provided, from any source — don't re-ask for it.** Skip this field whenever EITHER holds: (a) the user named a style ANYWHERE in the conversation (not only their first message — "fotorrealista", "en estilo anime", "el mismo estilo de antes", …); OR (b) the source interactive storyboard JSON has a NON-EMPTY `stylePrompt` (that's the style the user set in the visor — honour it verbatim, never re-ask). Only when the `stylePrompt` is EMPTY **and** no style was mentioned anywhere is the style genuinely missing → then this field is required.

#### Field 2 — Per-character image picker (one optional field per recurring character)

For each recurring character in scope, add ONE optional file picker:

```
{ label: "Imagen de referencia para <CHAR_LABEL> (opcional)",
  files: { multiple: false, extensions: ["png","jpg","jpeg","webp"] } }
```

- **`files: {…}` is MANDATORY** on these fields — that's what makes the step a drop-zone / Browse / thumbnail picker. **NEVER** a plain text input asking the user to type a path or describe the character.
- Always **optional** — leave empty is the normal case; the form proceeds without it.
- A character may already exist in the gallery as an `@handle` — the user can name it in Field 3 (free-text notes) instead of re-uploading. Resolve any such `@handle` and use it as that character's reference.

**Which characters get a picker?**
- **Interactive storyboard JSON path:** every entry in the JSON's `characters` roster (labels like `RATÓN_A`, `GATO_A`, `DUEÑO_A`) gets its own optional picker.
- **Idea-only path (no JSON):** add a picker for each character the story names. When the story is unclear about who's recurring, add one generic `protagonista` picker.
- **Refs already attached / already in the storyboard's `references`:** use them directly — do NOT re-ask for a photo you already have. When there is a SINGLE recurring character and a single attached photo (or the storyboard already carries that character's reference), MAP it and proceed without a picker. Add picker(s) ONLY when the mapping is genuinely ambiguous (several characters and/or several photos and it's unclear which belongs to whom) — then pre-populate them with the uploaded paths for the user to confirm. Never silently mis-map when ambiguous; never re-ask when it's obvious.

**Reminder on `referenceImages`:** any picker the user fills, plus any `@handle` they name in Field 3, MUST appear in the eventual `generate_image` call's `referenceImages` array AND be anchored as `Image N` in the prompt body (see Step 2 → "Positional anchoring — CRITICAL"). Pickers populated but not forwarded = the *"había 4 imágenes y no las ha referenciado"* bug.

#### Field 3 — Free-text notes (optional, ALWAYS last)

A plain text field, NO `files`:

```
{ label: "Anything to keep in mind before I generate? (opcional)",
  allowFreeText: true }
```

User can write any extra direction in their own words AND reference gallery assets with `@` — e.g. *"el gato es @gato_pixar, mantén la cocina oscura, el ratón siempre asustado"*. After the form returns, **resolve every `@handle` mentioned** (`resolve_handle` → use the path as a reference with that subject's alias) and fold the rest of the note into the sheet prompts (CHARACTER / SETTING lines, lighting, per-panel emphasis). This is the user's catch-all before committing — honour it.

### Optional inputs the user may have specified

Apply if given in their initial message; otherwise use defaults — these are NOT in the form (too noisy to ask each time):

- **Panel count** — default 15. Allowed 9, 12, 15, 20.
- **Duration** — default 15 seconds.
- **Aspect ratio and grid** — YOU choose the grid freely per sheet (any uniform cols × rows that fits the panel count, 12 panels max). RECOMMENDED default: pick cols/rows so each cell approximates the VIDEO aspect and derive the sheet aspect from it (`sheetAspect = videoAspect × cols/rows`, e.g. 16:9 video → 3×4 on a `4:3` sheet; 9:16 → 4×3 on a portrait `3:4` sheet), because natively-framed cells feed the video step without implied crops. Whatever you choose: pass the resulting sheet aspect as `aspectRatio` + `resolution: "4k"`, keep the grid UNIFORM with straight pure-black gutters, and stamp it in `metadata.grid`. The panel tools and the panels viewer AUTO-DETECT the real grid from the pixels, so no specific shape is ever mandatory.
- **Video type** — ad / explainer / tutorial / demo / social-post. When the user names one, ALSO read the matching `VIDEO_TYPE_<TYPE>.md` reference file for that type's specific caption style, shot mix and audio cue. Never read all five.
- **Target image model** — default Nano Banana Pro. GPT Image 2 also works (slightly more explicit layout phrasing).

### What about the story overview?

The story overview is normally already in the user's initial message ("haz un storyboard de X") — don't re-ask it as a form field. Use it directly. If the user's message has zero narrative content (literally just *"hazme un storyboard"* with no topic), ask once via `prompt_user`: *"What's the story / topic for the storyboard?"* — then proceed with the form.

---

## Step 2 — Analyse character / product references

For each uploaded reference (character OR product/object), extract:

- **Identifying features** — facial structure, skin tone, hair (colour, length, texture, style), age range, build, distinguishing marks (scars, freckles, tattoos). For products: silhouette, material, colour, label / logo / typography, finish.
- **Clothing and accessories** — garments, colours, materials, fit, layering, signature items (characters only)
- **Design language** — proportions, palette, silhouette readability
- **Personality cues** — posture energy, expression tendency (characters only)

Build a **compact description** (80–150 characters per reference) — the "DNA" that gets woven into the prompt to maintain consistency across panels.

For multiple references, create distinct identifiers (`HERO_A`, `PRODUCT_BOTTLE`, …) that won't blur across panels.

### Positional anchoring — CRITICAL

**Every user-uploaded reference MUST be anchored by position (`Image 1`, `Image 2`, …) in the composed prompt AND included in the `generate_image` call's `referenceImages` array.** Image generators do not magically see the references attached to the chat — they only see what you pass in the tool call, and they only "know" which reference is which subject if the prompt body says so explicitly.

#### Collecting references — interactive storyboard JSON

When the input is an interactive storyboard JSON, the user attaches refs at THREE levels via the visor: **storyboard root**, **each scene**, **each shot**. Walk all three and union them (deduped by path / `@handle`). DO NOT only read shot-level refs — character identity often lives at storyboard / scene level. The flow:

1. Read `storyboard.references` → root-level refs.
2. For each scene, read `scene.references` → scene-level refs.
3. For each shot, read `shot.references` → shot-level refs.
4. Dedupe by absolute path (resolving `@handles` first).
5. Add the user's optional picker uploads from Step 1's `prompt_form`.

**⚠️ The SETTING/LOCATION plate is the most-dropped reference — guarantee it is present (the *"a veces ni siquiera adjunta la imagen de escenario"* bug).** Among the collected refs, a photo that depicts a ROOM / SET / location (not a person or product) is the setting plate. It MUST end up in `referenceImages` and be anchored as `SET_*` per section C2 — exactly like a character ref. Two reliability rules:
- **Persist it.** If the user attached a setting image only to the chat (not yet in the storyboard), write it into the storyboard's `references` (root or the relevant `scene.references`) via `save_storyboard` so EVERY future (re)generation — including a fresh session or an agenda run — re-collects and re-attaches it. A plate that lives only in this chat turn is the one that "sometimes" goes missing.
- **Generate it if missing but the location recurs.** When no plate exists and the same location spans multiple panels, generate one establishing plate FIRST, persist it (`scene.references` and/or a `locations` Library asset), then anchor every panel to it. Do NOT render a multi-panel sheet of a recurring location with NO location anchor at all — that is the root of cross-panel set drift.

#### Multi-ref of the SAME subject — NEVER collapse

When the user attached **multiple photos of the same character** (front view, side view, back view, different outfits, different expressions, candid shots), every single one is load-bearing. Multi-angle / multi-outfit refs are how the model locks face shape, hair, build and wardrobe under varying lighting and poses — each photo carries identity signal the others miss.

**NEVER collapse N refs of the same person into "1 reference for HERO_A".** This is the reported bug — *"le he puesto varias imágenes de la misma chica y ha puesto 1 sola foto de referencia"*. The wrong move is to dedupe at the SUBJECT level and pick a single "best" photo. The right move:

- Pass **EVERY** ref to `referenceImages` with its own array position.
- In the prompt body, anchor the subject ACROSS all its positions: *"Match `HERO_A` to `Image 1`, `Image 2`, `Image 3`, `Image 4` — five reference photos of the same character (front, side, back, candid). Use all five jointly to lock face, hair, build and wardrobe; do not invent features absent from the references."*

Dedupe is by PATH only (don't ship the same file twice) — never by subject identity.

#### Choosing the order

Decide the order BEFORE writing the prompt and stick to it. Canonical order:
1. Hero / most-used character — all of its photos in a contiguous block (front first, then alternate angles, then outfits / expressions).
2. Secondary characters — same pattern, all photos of one character before moving to the next.
3. Product / object references — together in a block.
4. Setting / location plates — last.

Write down the mapping NOW (one line per position, e.g. *"Image 1 = HERO_A front; Image 2 = HERO_A side; Image 3 = HERO_A back; Image 4 = HERO_A candid; Image 5 = HERO_A casual outfit; Image 6 = PRODUCT_BOTTLE"*) and use it verbatim in section C of Step 4 below. **Missing positional anchors = silently-ignored references.**

---

## Step 3 — Break the story into beats

> 🛑 **HARD STOP — When an interactive storyboard JSON is the input, the SHOTS are fixed: do NOT invent new story beats.** The JSON's shots are the source of truth — same events, same order, nothing added or dropped at the STORY level. The default mapping is **one panel per shot, in order**.
>
> **The ONE allowed expansion (this is NOT invention): a shot with notable CAMERA MOVEMENT renders as 2–3 keyframe panels of that SAME shot** — start / middle / end of the move — so the video generator can see the continuous motion clearly (see "Camera-movement shots" right below). This adds PANELS, never SHOTS or events: you're drawing one continuous shot across a few frames, not adding a new beat. A static shot stays exactly one panel.
>
> Still forbidden: re-decomposing the story, adding NEW beats/reactions, padding to hit a per-type's "8–10 panels for ads" / "3–5 for explainers" range, or dropping shots to fit a grid. The *"el storyboard interactivo tenía 5 shots y se inventaron 5 más"* bug is inventing new STORY beats — that stays banned; expanding ONE moving shot into its keyframe panels is not that. So: **panel count = Σ per-shot panels (1 for a static shot, 2–3 for a camera-movement shot)**, and EVERY shot is still represented, in order. Skip ahead to chunking.
>
> ### Camera-movement shots → 2–3 keyframe panels (NEW)
> When a shot's `movement` describes the camera (or a fast subject) MOVING — a push-in / dolly, pan, tilt, crane, orbit, tracking/follow, whip — and the shot is long enough to read as motion (roughly ≥ 3 s, or any `movement` that clearly isn't "static / locked-off"), give it **2 panels** (start + end of the move) or **3 panels** (start + middle + end) when the move is large or long (≈ ≥ 5 s). Each keyframe panel:
> - shares the SAME `shotId` (they are the same shot — the metadata records all of them under that shot, see Chunking), and the SAME action/state/setting; only the camera framing progresses.
> - its caption keeps the shot's type + a sub-range of the shot's timecode (e.g. a 0:08–0:12 dolly-in → panel A `0:08 - 0:10`, panel B `0:10 - 0:12`), and a short note of the move stage (*"start of the push-in, wide"* → *"end of the push-in, tight on the face"*).
> - This is exactly your *"si un plano dura 4 s y la cámara se mueve, pon 2-3 cuadros para que se vea el plano continuo"* — it gives `generate_video` start/mid/end keyframes for that continuous shot. A static / locked-off shot never expands.
>
> The default 15 / per-type ranges below ONLY apply when there's NO JSON input — i.e. the user gave a prose brief and the agent is decomposing from scratch.
>
> **And transcribe each shot FAITHFULLY — the JSON is the SINGLE SOURCE OF TRUTH, not a rough idea to embellish.** One panel per shot, and that panel preserves the shot EXACTLY:
> - **Action** — the panel's scene description IS `shot.action`, rendered as-is. Same events, same order. Invent NOTHING, drop NOTHING, "improve" NOTHING. If shot 7's action is *"OBI_WAN y LUKE echan a correr hacia las escaleras"*, panel 7 is them running to the stairs — NOT an invented "apologetic look / the master sighs" reaction beat. (Translate to English + IP-alias per Step 4, but the WHAT must match the JSON.)
> - **Story premise (`synopsis`) — a HARD CONSTRAINT every panel must obey.** Read the storyboard-level `synopsis` (and the shot's `scene.synopsis` when present): it's the physical/causal logic the piece depends on, and it OVERRIDES a terse `action`. Bake it into EVERY panel; a panel that contradicts it silently breaks the whole story. E.g. premise *"the Pepsi button is mounted HIGH on the machine, out of the child's reach — that's why he stacks cans to climb"*: even a shot whose `action` is *"the boy presses the button"* MUST show the button HIGH and out of reach (the boy reaching/straining or stood on stacked cans), NOT a button at hand height. When `synopsis` and `action` seem to conflict, the premise WINS — render the action THROUGH the premise.
> - **Continuity LOCK (`continuity`) — the storyboard-level INVARIANTS, treated as absolute negatives.** When the JSON carries a `continuity` array, each entry is a rule that holds for EVERY panel and must NEVER be broken or "fixed" — the negatives the premise implies but image models won't infer ("the button stays high, never lower it or make him taller", "the step-cans stay intact, never crushed"). Carry every rule into every panel as a hard constraint. Where `synopsis` tells you WHY, `continuity` tells you WHAT MUST NOT CHANGE — and it's the negatives that stop the unreachable from drifting into reach across the sheet.
> - **Current panel state (`shot.continuity` = { characters, objects }) — the authoritative state for THAT panel.** When a shot carries `continuity`, it is the continuity-table row split into two columns: `characters` = exactly where each character is, their pose, what they wear/hold; `objects` = the state of each key prop/scenery IN THAT FRAME. Render precisely both — they OVERRIDE any default the bare `action` would snap to (e.g. `continuity.characters: "de pie sobre las dos latas apiladas"` + `continuity.objects: "las dos latas intactas, botón ahora alcanzable"` means the panel shows him UP on the cans, not on the ground). This is the structured form of the carry-forward rule below; when `continuity` is present, trust it over re-deriving the state yourself. (Legacy storyboards may still carry a single free-text `shot.state` string — treat it the same way.)
> - **Setting** — the `scene.title` / `location` is WHERE the shot happens; carry it into the panel. Scene *"Nave - El Accidente"* → inside a spaceship corridor; *"Piso Inferior"* → a control room; *"El Baño de Yoda"* → a tiled bathroom with a foam jacuzzi. NEVER flatten the setting to a generic "a dimly lit room" — if the JSON says they're on a ship, the panel is on a ship.
> - **Shot type / movement / duration / dialogue** — copy `shot`, `movement`, `duration`, `dialogue`/`audio` from the JSON shot. Do NOT reassign shot types "for variety", and do NOT apply the narrative-arc / act-structure / emotional-escalation principles listed below — those RESHAPE the story and are **IDEA-ONLY**. A JSON storyboard is already directed; your job is faithful transcription, not re-direction.
>
> **Chunked (multi-PART): re-read the JSON and transcribe EXACTLY that PART's shot range — every time.** Compose each PART sheet straight from the file's shots for that part's panel range; never free-write a part from your summarized memory of the story. *"La hoja 2 se inventa todo"* is exactly this — the agent stopped looking at the JSON after part 1 and improvised. Re-open the file for every PART and transcribe its shots one by one.

Decompose the story overview into the target panel count (default 15). Each beat needs:

1. **Panel number** (1–N)
2. **Per-shot duration** (seconds, fractional allowed at this stage — e.g. 1.5 s, 2 s, 3.5 s). The SUM across all beats is the storyboard's total duration.
3. **Timecode** (e.g. `00:00 – 01:00` for a 15-second / 15-panel breakdown)
4. **Shot type** — Wide, Medium, Close-up, Low Angle, High Angle, Dynamic, Over-the-shoulder, Macro, POV. POV is a camera angle, not a separate style — combines with any visual style.
5. **Scene description** — one sentence describing what's happening visually
6. **Action / Dialogue** — character dialogue or specific action (or "None")

**Narrative arc principles:**
- **Acts structure** — even in 15 panels, follow a three-act structure. Panels 1–3: setup. 4–6: inciting incident. 7–10: rising tension. 11–13: climax / resolution. 14–15: denouement / emotional landing.
- **Shot variety** — vary shot types across the sequence. Never repeat the same shot type in consecutive panels. Alternate between establishing shots and intimate close-ups.
- **Emotional escalation** — build intensity through the middle, peak around 10–12, then resolve. Close-ups for emotional peaks, wide shots for context and breathing room.
- **Character consistency** — surface character-identifying details in panels where they'd be visible at that shot size.

---

## Chunking — split into multiple PART sheets when total duration > 15 s

This step happens BEFORE Step 4 (composing the prompt). It's what stops a 28-second storyboard from being silently cropped to 15 s at render time — the reported bug *"ha hecho los 15 segundos pero no de todo el storyboard sino solo de una parte"*.

### Why chunking exists

There are now **TWO separate groupings** — keep them distinct:

- **Clips** — contiguous groups of shots, each **≤ 15 s** (the `generate_video` `duration` enum is whole seconds 4–15, plus `"auto"`). Each clip renders to ONE downstream video clip. This is the video unit. (It's what the old spec called a "PART".)
- **Sheets** — a 4K storyboard image (= ONE `generate_image` call = the cost). A sheet holds up to **12 panels** and can carry **several WHOLE clips**. This is the image/cost unit.

**The win:** a sheet is NO LONGER tied to one clip. A 30-second storyboard of 3 short scenes is not "3 sheets" — it's 3 clips packed onto ONE sheet of up to 12 panels (one image, three clips), as long as the panels fit. Fewer `generate_image` calls = less money. Downstream, `visual-panels-to-video` is TOLD which panels belong to which clip (via `metadata.clips`, below) and renders one `generate_video` per clip, concatenating them on the timeline.

Two hard limits drive the grouping: a clip ≤ 15 s, a sheet ≤ 12 panels. A clip NEVER spans two sheets.

### How to chunk

**Read `totalDurationSeconds` straight from the JSON root — DON'T hand-sum.** The app stamps `totalDurationSeconds` (and `shotCount`) on the storyboard on every save; it is the authoritative length, always in sync with the current shots. Use that number as `totalSeconds`. **Do NOT add up the per-shot durations yourself** — that arithmetic is exactly where the agent miscounts (a 40 s storyboard = 13 + 4.5 + 22.5 got mis-read as "20 s", producing 2 PART sheets instead of 3). The stamped number overrides any duration named in the brief, the Step 0 form, or the task description. Sanity-cross-check it against the visor's per-scene `SEG` labels if visible. **Fallback only if `totalDurationSeconds` is absent** (an older storyboard saved before the field existed): then, and only then, re-read the file and sum `shot.duration` across EVERY shot of EVERY scene. Then:

#### Step A — group shots into CLIPS (≤ 15 s each — the VIDEO grouping)

Each clip renders to one `generate_video`. You'll get at least `ceil(totalSeconds / 15)` clips — 15 s is the per-clip ceiling. **A clip must also fit ONE sheet, so cap it at ≤ 12 PANELS too** (count camera-movement expansions from Step 3): open a new clip the moment adding the next shot would exceed **EITHER 15 s OR 12 panels**. **(In the arithmetic guard below, every "PART" means one CLIP — sheet-packing is the SEPARATE Step B.)**

1. **Group shots in order, KEEPING EACH CONTINUOUS ACTION WHOLE.** Clip boundaries become hard cuts between rendered clips — place them where the story naturally breaks, NEVER mid-motion:
   - 🔒 **`noCutBefore` shots are INSEPARABLE — never split a glued take across clips.** A shot flagged `"noCutBefore": true` in the interactive JSON is a CONTINUATION of the previous shot (one continuous take, no cut — they share a number). The whole glued run MUST land in the SAME clip; putting a clip boundary between them would turn the intended uninterrupted camera move into a hard cut. Treat a glued run as one atomic unit when grouping (and when checking the ≤15 s / ≤12-panel caps). This is the same idea as a single shot expanded into multiple camera-movement panels (they share a `shotId`) — only here the author pre-split it into glued shots.
   - Keep a whole **scene** in one clip when it fits (≤ 15 s). Use the JSON's `scenes[]` structure as your guide; don't scatter a scene's shots across clips if they fit together.
   - Keep a **continuous, causally-linked action** together (a chase, "draw → shoot → things shatter", an unbroken camera move). Splitting mid-action breaks flow.
   - Cut only at natural breaks: end of a scene, location change, time jump, beat that lands and settles.
   - When a single continuous action exceeds 15 s, cut at its CALMEST internal moment (a held beat, a settle, a reaction), never mid-motion.

   > 🛑 **DO THE ARITHMETIC EXPLICITLY — DO NOT EYEBALL THE GROUPING. This is the #1 chunking bug.** You must NOT guess a PART's duration or its shot range. Write out a **running cumulative sum, shot by shot, in order**, and decide boundaries from it:
   > - List EVERY shot as `shot <number> (<duration>s) → running total <Ys>`. Add the EXACT `duration` of each shot from the JSON — never round mid-add, never approximate ("about 14s" is forbidden).
   > - **Open a new PART the moment adding the next shot would push the running total past 15 s** (or at a clean scene break before 15 s). Reset the running total to 0 at each new PART.
   > - Worked example (43 s storyboard, shots 1-18): *shot1(2)→2, shot2(2)→4, shot3(1.5)→5.5, shot4(1.5)→7, shot5(2)→9, shot6(2)→11, shot7(2)→13 — adding shot8(4)→17 > 15, so **PART 1 = shots 1-7 = 13 s** (NOT "shots 1-6 = 14 s" — that's the miscount). Reset. shot8(4)→4, shot9(2)→6, shot10(2)→8, shot11(3)→11, shot12(2)→13 — adding shot13(3)→16 > 15, so **PART 2 = shots 8-12 = 13 s**. Reset. shots 13-18 = 3+5+2+2+3 = 15+2… continue the sum for **PART 3**.* The point: every boundary is justified by the written running total, not a gut number.
   > - A PART's stated duration is **literally the running total of its shots** — they must match exactly. If you wrote a duration you didn't reach by summing the shots in that PART, you made it up; redo.
   > - **DOUBLE-CHECK each PART in reverse.** Once you've decided "PART X = shots A-B", re-add those exact shots a SECOND time, INDEPENDENTLY — e.g. sum them in reverse order (shot B, B-1, …, A) — and confirm the two sums are identical. If the forward sum and the reverse sum disagree, you summed wrong: re-sum from scratch before doing ANYTHING else. Don't proceed to generate a sheet on a number you only computed once.
2. **Assign each CLIP an integer duration in [4, 15] s** = the exact running-total sum of its shots, rounded, clamped 4–15. Nudge so the per-clip integers sum to `totalDurationSeconds`. Never fractional — only `generate_video`'s integer enum.
3. **No sub-4 s clip:** merge a trailing < 4 s clip into the previous one (kept ≤ 15 s).
4. **A single shot > 15 s is malformed** — surface it to the user (or, in a workflow, ask them to split it in the interactive storyboard), don't truncate.

   > ✅ **VERIFY Step A (both must pass):** Σ clip durations **== `totalDurationSeconds`** from the JSON; and every shot appears exactly once, in order, across the clips (contiguous, no gap/overlap).

#### Step B — pack CLIPS into SHEETS (≤ 12 panels each — the IMAGE/cost grouping)

Now bundle whole clips onto as FEW sheets as possible — this is the money-saver:

1. **Panels per clip** = Σ its shots' panels = (1 per static shot) + (2–3 per camera-movement shot, per Step 3).
2. **Greedily fill sheets, in clip order.** Start sheet 1; add the next clip while the sheet's running panel total stays **≤ 12**; otherwise close it and open a new sheet. **NEVER split a clip across two sheets** — a clip's panels always live on ONE sheet.
3. **Oversized clip:** if one clip's own panels > 12 (many moving shots), trim its camera-movement expansion (drop the middle keyframe on the least-important moving shots) until that clip fits ≤ 12.
4. **Prefer full sheets** — don't leave a sheet at 4 panels when the next clip would fit; fuller sheets = fewer `generate_image` calls = less cost. Leftover positions render as **bare board, not empty cards** (section A).

   > ✅ **VERIFY Step B:** every sheet ≤ 12 panels; no clip split across sheets; Σ panels over all sheets == Σ per-shot panel allocations (Step 3).

### State the split before composing

Print BOTH groupings out loud (chat / `print`), e.g.:

> *"34 s storyboard → **3 clips** (12 s, 11 s, 11 s) → packed into **2 sheets**: SHEET 1 = clips 1–2 (panels 1–9), SHEET 2 = clip 3 (panels 10–12)."*

### Numbering (no banner on the sheet)

- **Nothing is drawn as a banner / header / PART tag on the sheet.** The image is the full-bleed grid only. The PART index lives in `metadata` (`storyboardPart` / `storyboardParts`), the `summary` and the filename, never rendered on the image.
- Panel **numbers** are 1-based per sheet and exist ONLY in the prompt text and metadata (for ordering and the panel tools): they are NEVER rendered on the image. The app's panels viewer overlays its own numbering; baked-in numerals confused users (per-sheet numbers clash with the viewer's global ones).

### One prompt PER sheet + the panel→clip metadata

When there's > 1 sheet, build one prompt per sheet and call `generate_image` once per sheet. Each prompt:
- Section A's title carries the PART tag for THAT sheet
- Section F (Scene Breakdown) lists ONLY that sheet's panels (which may span several clips)
- Sections B, C, D, E, G, H stay essentially identical across sheets (same style, characters, grid layout) so cross-sheet visual continuity is preserved.

**🧷 Every sheet's `metadata` MUST carry the `clips` map** — it tells `visual-panels-to-video` which panels feed which clip (without it, the video step falls back to "1 sheet = 1 clip" and silently drops scenes when a sheet holds several clips):
```
clips: [
  { clipIndex: 1, shotIds: ["sh1","sh2","sh3"], panels: [1,2,3,4], durationSec: 12 },
  { clipIndex: 2, shotIds: ["sh4","sh5"],        panels: [5,6,7],   durationSec: 11 }
]
```
- `clipIndex` is **global**, sequential across the whole storyboard (1, 2, 3 … in timeline order) so clips render in order across sheets.
- `panels` = this clip's 1-based panel numbers ON THIS SHEET (a camera-movement shot contributes its 2–3 consecutive panels).
- `durationSec` = the clip's integer duration; `shotIds` = its JSON shot ids.

Stamp every sheet's `metadata.sourceStoryboard` with the interactive JSON path (when applicable) plus `metadata.storyboardPart: K` and `metadata.storyboardParts: K_total` so `visual-panels-to-video` can recover the chunking later.

### 🔁 Cross-sheet referencing — Sheet K ≥ 2 MUST receive every prior sheet (MANDATORY)

> 🛑🛑 **STRICTLY SEQUENTIAL: NEVER generate the sheets in PARALLEL. This is NON-NEGOTIABLE and the #1 multi-sheet rule.** Multi-PART sheets are rendered ONE AT A TIME, in order: render sheet 1, **WAIT** for it to finish, `show_result` it, THEN render sheet 2 with sheet 1 in `referenceImages`, wait, then sheet 3 with sheets 1-2, and so on. Firing several `generate_image` calls at once (a parallel block, OR back-to-back without awaiting each result) is a HARD BUG: sheet K ≥ 2 **cannot** reference sheet K-1 if K-1 does not exist yet, so every parallel sheet renders BLIND and the SAME actor comes out with a DIFFERENT FACE / hair / wardrobe on each sheet (the exact, furiously-reported drift). There is NO "parallel generation to save time" mode for a multi-sheet storyboard: the dependency chain (each sheet feeds the next as a reference) makes sequential the ONLY correct order. Do NOT announce or attempt *"generación paralela"* / *"genero las N hojas a la vez"*; announce and DO *"una hoja a la vez, en orden, cada una usando la anterior como referencia"*. Exactly ONE `generate_image` in flight at any moment. (Single-sheet storyboards are just the K=1 case: one call, nothing to parallelize.)

This is the rule that keeps multi-PART sheets visually coherent. Without it, sheet 2 has no idea what sheet 1 ended up looking like — characters drift in face / wardrobe / hair, the palette wobbles, the grid gutters and corner-number style re-roll. The reported bug: *"para el segundo storyboard visual no ha puesto el primero como referencia"*.

**For every sheet K from 2 onwards**, the `generate_image` call's `referenceImages` array MUST include:

1. **Every prior approved sheet**, aliased `sheet_part_1`, `sheet_part_2`, …, `sheet_part_{K-1}`, in that order.
2. **After those**, the user-supplied subject references (characters, products, settings) — same as sheet 1.

The aliases are SDK-level names; in the prompt body, anchor them by position (`Image 1`, `Image 2`, …) per the positional-anchoring rule in Step 2 — never write the alias as the only identifier the model sees.

**Continuity block in the prompt body** — for sheets K ≥ 2, weave in (right after the per-shot scene breakdown, before the style block):

> *"`Image 1` (and `Image 2` … `Image {K-1}` when present) are the previously-approved PART sheet(s) of this same storyboard. Preserve EXACTLY from them: every character's face / build / hair / wardrobe, every recurring object's design, the setting, the lighting direction, the palette, the render style, and the sheet FORMAT (the clean full-bleed grid, the thin black gutter lines between cells, and the absence of ANY text or numerals). There is no banner, no cards, no captions, no numbers and no footer. Only the panels in section F change. Treat the PART sheet(s) as the authoritative visual locker for everything that is NOT the new shots."*

**Don't skip either half.** Passing the prior sheet without the continuity block makes the model riff on the style (sees the picture, doesn't know it's the law). Writing the block without the picture leaves it nothing to copy. Both are required.

**Refinements on a sheet that's already approved.** If the user requests changes on sheet K, re-render sheet K with the SAME `referenceImages` payload (`sheet_part_1..K-1` still there) and the SAME continuity block. Do NOT regenerate the prior sheets unless the user explicitly asks.

---

## Step 4 — Compose the storyboard image prompt

Write the prompt as a **single continuous block of FLOWING NATURAL-LANGUAGE PROSE** — a creative director's brief, read aloud as paragraphs. This is the prompt passed to `generate_image` in Step 5. **When chunking produced K > 1 sheets, do this K times — once per PART.**

> 🛑 **FORM — write a brief, not a form. This is the #1 drift to avoid.** Image models parse flowing descriptive prose far better than a filled-in template, and a form-shaped prompt makes the model render form chrome instead of a cinematic sheet. So:
> - ❌ NO decorative banner lines (`═══════`), NO `KEY: value` lines, NO ALL-CAPS section headers, NO bullet lists in the prompt body.
> - ✅ The A–H sections below are your CHECKLIST of what to cover, NOT literal headers to print. Weave them into prose paragraphs.
> - **Gold standard (match this shape):** *"A 12-second professional panel sheet for a sci-fi adventure short, showing 7 sequential cinematic panels in a clean full-bleed 3×4 grid: each panel's image fills its cell edge-to-edge, cells separated only by thin black lines, NO numbers or text anywhere inside the panels, the grid covering the whole page (the last five grid positions left as bare black background). Cinematic film-stock look, warm practical lighting. The story follows a lone astronaut in a worn orange suit who finds a green sprout on Mars… Panel 1, wide establishing shot of the barren red plain: the astronaut walks into frame, small against the vast landscape…"*
> - ❌ Anti-pattern (what NOT to produce): lines like `═══` / `FORMAT: 7 frames` / `CHARACTERS` / `SCENE BREAKDOWN` with bulleted `Panel 1: …`.
>
> Keep the A–H coverage and order, just deliver it as prose. This is exactly the form the original prompt-builder produced.

### Required sections, in order

#### A) Title & Format Header
Open with the panel sheet concept: duration, title, panel count, grid layout, style genre.

Example opener: *"15-second animated panel sheet for a sci-fi adventure short film titled 'The Little Inventor & The Lost Robot'. A complete professional animation storyboard presentation page featuring 15 sequential cinematic panels arranged in a clean 3×5 grid layout."*

**🔗 ONE CONSISTENT WORLD — state it in the opener and mean it.** All panels on the sheet are DIFFERENT CAMERA ANGLES AND MOMENTS OF THE SAME UNCHANGING SET, not separate scenes. The single biggest complaint is panels that drift cell to cell (the sofa, the bottles, the table move or change between panels even though it's "the same room"). The model renders each grid cell semi-independently, so you MUST tell it the world is shared and locked. Add a line like: *"All panels depict the SAME physical location and the SAME objects, seen from different camera angles. Every recurring element — furniture, props, their colours, materials, sizes and relative positions — is IDENTICAL across every panel it appears in; the set does NOT change between panels, only the camera framing and the characters' actions do. Keep the two green bottles, the beige sofa, the low table etc. in the same place and the same look in every panel that shows them."* Name the actual recurring objects of THIS storyboard, not generic ones. AND anchor the set IN-CANVAS too: because the whole sheet is one generation, tell the model that every later panel shows THE SAME set as the establishing panel: *"the corridor in panels 2-11 is EXACTLY the corridor of Panel 1: same architecture, same ceiling light coffers, same wall panelling and floor plates, matched to `Image N` (the set plate)"*. A later panel that only says "the corridor" without pointing back at Panel 1 and the plate is where the set re-rolls. This pairs with the `SET_*` plate anchor (section C2) and the per-shot `continuity` table.

**🛑 The panel count is EXACTLY the number of PANELS on this sheet — state THAT number everywhere, never the grid's cell count.** (Panels ≠ shots: a camera-movement shot expands to 2–3 keyframe panels — see Step 3 — so count the PANELS you actually wrote, not the shots.) A sheet often has a non-round count (7, 10, 11 …); the grid you chose stays as declared and the leftover cells are bare black. The reported bug — *"escribí 7 paneles y generó 12"* — is the prompt saying "7 frames" in one line but "12 sequential cinematic panels in a 3×4 grid" in the layout line, so the model filled all 12 cells and invented panels 8–12. Rules:
- **One number, everywhere.** FORMAT header, the section-A opener, AND section E's layout block must ALL say the same count = the real panel count. Never write "12 sequential panels" when you have 7. Never let the FORMAT line and the LAYOUT line disagree.
- **🚫 Leftover cells are NOT drawn — bare black background.** When the panels don't fill the grid (e.g. 10 panels in a 3×4 = 2 leftover), the unused positions are **plain black with NOTHING on them: no image, no number, no border, no placeholder frame**. State it positively in the prompt: *"exactly 10 panels; the remaining 2 grid positions are left as bare black background, render NO image, number, frame or border there."* The panels fill left-to-right, top-to-bottom; if the last row is partial, the rest of that row is bare black. (This both keeps the leftover area clean AND stops the model inventing extra shots to fill them: there are EXACTLY N panels, nothing else.) **And the black cells keep EXACTLY the same cell size as the filled ones: the grid geometry NEVER stretches, shrinks or collapses to fit fewer panels.** A row that is partly or fully black is still a full-height row (the reported bug: sheets with a black row rendered with uneven row heights, which breaks both the look and the virtual-panel cell math).
- **The grid is YOUR choice — pick it per sheet and declare it ONCE.** Any uniform cols × rows that holds the panel count works (12 panels max per sheet); no shape is mandatory. Recommended default: cells that approximate the video aspect (`sheetAspect = cellAspect × cols/rows`, e.g. 3×4 on a 4:3 sheet for 16:9 video, 4×3 on a 3:4 sheet for 9:16). Hard requirements, whatever you pick: (1) ONE uniform grid per sheet: straight, continuous, pure-black gutters, every row the same height, every column the same width (that is what the auto-detection in the panel tools and the viewer locks onto); (2) leftover cells bare black at the same cell size; (3) the SAME grid named consistently everywhere in the prompt; (4) stamp it in `metadata.grid`.

Example opener for a 7-panel sheet (16:9 video): *"A 12-second panel sheet: **7** sequential cinematic panels in a clean full-bleed 3×4 grid, cells separated by thin black lines, NO numbers, letters or labels rendered anywhere (the last 5 grid positions left as bare black background, nothing drawn there)."*

🚫 **The duration / title / PART you name in this opener is PROMPT FRAMING ONLY: it is NOT drawn anywhere on the sheet** (no title banner, no header strip, no caption text). The rendered sheet is the clean full-bleed grid of panel images, nothing else: no numbers of any kind (see section E).

Recommended orientation: let the sheet follow the video (a 16:9 video reads best on a landscape sheet, a 9:16 video on a PORTRAIT sheet with vertical cells, so panels are natively framed). Avoid rendering vertical-video panels inside landscape cells when a portrait sheet is available: it wastes cell area.

#### B) Style Declaration
A rich style block tailored to the user's specified or inferred visual language. **NOT a fixed line — it adapts to the style.**

The official presets and their ready-to-paste phrasing blocks live in `STYLE_PRESETS.md`. Read that file and paste the matching block here. For custom styles, follow `STYLE_PRESETS.md`'s custom-style flow (1–2 sentences → rewrite as descriptive aesthetic phrasing → confirm with user).

Adapt the language to the style family:
- **3D animation** — family-film studio quality, cinematic rendering, expressive character animation, warm lighting
- **Live-action** — cinematographic style, film stock look, practical lighting, grounded realism
- **Anime** — anime studio quality (Ghibli / Trigger / MAPPA tone depending on the story), cel-shading, dynamic line work
- **2D animation** — hand-drawn quality, colour-palette approach, line weight, shading model
- **Stop-motion / claymation** — handcrafted clay or puppet aesthetic, visible material texture, miniature set design
- **Any other style** (editorial, comic book, watercolor, cyberpunk, …) — adapt accordingly; the style block should read like a creative director's brief for that specific aesthetic

**Never use copyrighted studio or franchise names directly in the prompt** (`Pixar`, `Disney`, `Ghibli`, `Aardman`, `Wallace and Gromit`, …) — they trigger moderation and copyright filters. Rewrite as descriptive aesthetic phrasing. `STYLE_PRESETS.md` already does this correctly for the 3 official presets; mirror the pattern when composing a custom one.

#### C) Character / Product Descriptions
Detailed descriptions of each main character AND each product / object reference, pulled from uploaded references (Step 2) or built from the story overview. Include physical features, clothing, accessories, distinguishing visual elements. Written as flowing prose, not a list.

**When references are uploaded, anchor every described subject to ALL of its image positions** (per the mapping you wrote in Step 2's "Choosing the order"):

- **Single ref:** *"Match `HERO_A` exactly to `Image 1`: <features>. Carry the same face, hair and build across all panels."*
- **Multi ref of the SAME subject (most common):** *"Match `HERO_A` to `Image 1`, `Image 2`, `Image 3`, `Image 4` — four reference photos of the same character (front, side, back, candid). Use all four jointly to lock face, hair, build and wardrobe across all panels; do not invent features absent from the references."* Each photo position MUST be listed — *"Match HERO_A to Image 1"* alone after collecting 4 refs of HERO_A is the reported bug; do NOT pick one and drop the rest.
- **Product / object ref:** *"Match the `PRODUCT_BOTTLE` exactly to `Image 5`: <silhouette, material, label>."*

Without explicit `Image N` anchors the model treats the prose as a suggestion and may drift toward generic priors. With them it locks identity to the supplied photos. This is the difference between *"a Mediterranean woman in a black silk dress"* (the model invents the woman) and *"`HERO_A` — match `Image 1, Image 2, Image 3, Image 4` (front/side/back/candid of the same person): light olive skin, long dark wavy hair, deep brown eyes, slender frame, in a long black silk dress"* (the model uses every photo).

**⚠️ References lock IDENTITY, never POSE or ORIENTATION.** The model also copies HOW the subject sits in its reference (upright, blade up, label facing camera) unless the panel text overrides it. Whenever a panel shows the subject in a DIFFERENT orientation or pose than its reference image (upside down, lying flat, mid-fall, seen from behind, folded, broken), that panel's description MUST declare it explicitly in frame-geometric terms, naming the override: e.g. *"the saber appears INVERTED relative to Image 3: metal hilt at the TOP, blue blade pointing straight DOWN"*. Without that, the reference's canonical orientation wins (the reported bug: a lightsaber that "falls tip-first" rendered blade-up at the moment of floor contact, exactly as posed in its reference plate).

#### C2) Setting / Location — ANCHOR the environment exactly like you anchor characters
**This is the #1 cause of cross-panel drift** (*"the sofa / the bottles / the table change between panels; my escenario reference is ignored"*). Characters stay consistent because section C anchors them to `Image N`; the SET gets NO such anchor — it survives only as loose per-panel text in section F — so the model re-invents the room in every cell. **The set MUST get the SAME forceful `Image N` anchoring as a character.**

- **A reference image that depicts a LOCATION / SET / room (not a person or product) is a SETTING plate.** Identify it among the collected references (Step 2 — storyboard/scene/shot `references` or a user attachment) and give it a per-location identifier, e.g. `SET_SALON`. It MUST appear in `referenceImages` AND be anchored by position in the prompt body.
- **Anchor it forcefully**, e.g.: *"Match the environment to `Image N` (`SET_SALON`) — the authoritative plate for this location. Reproduce its EXACT layout in every panel set here: the same furniture in the same positions (beige sofa, low coffee table), the same recurring props with the SAME count and placement (e.g. the two green bottles on the table, the TV), the same wall/window/door layout, the same materials and colours. Between panels ONLY the camera framing and the characters' actions change — never move, add, remove, restyle or recolour the set or its objects. When a panel shows only part of the room, the visible part MUST still match the plate."*
- **Without this anchor the scenario reference is treated as a suggestion** and drifts cell to cell (the reported bug). With it, the set is locked across the whole sheet — and across PART sheets, because the plate rides in every call's `referenceImages`.
- **Tie it to the continuity table:** per-shot `continuity.objects` says WHICH objects are in this frame and their STATE; the SETTING plate says what they LOOK like and WHERE they sit. The plate locks identity + placement; the `objects` column locks per-panel state changes.
- **One plate per recurring location.** If a storyboard has several locations, anchor each panel to ITS location's plate.
- **🛑 MANDATORY: no plate supplied but a location recurs in 3+ panels? GENERATE the establishing plate FIRST, always.** Before composing the sheet prompt, render ONE establishing plate of that location (a wide, well-lit shot showing the full space and every recurring architectural element and prop in its canonical position, in the chosen style), then anchor every panel set there to it via the same `Image N` mechanism as characters. This is NOT optional: prose alone cannot lock a set, and skipping the plate is the #1 cause of set drift (user-verified bug: the corridor changed architecture between panels of the same sheet: rounded arches in one panel, a mezzanine with pipes in another). Save the plate as a `locations` Library asset so later edits/regenerations and single-panel fixes reuse the exact same set.
- 🛑 **NEVER re-describe the set's props with fresh adjectives in the per-panel breakdown (section F): POINT BACK to the plate instead.** This is the concrete mechanism of the "the table in panel 3 isn't my reference table" bug. When you write *"a low coffee table with three empty green glass beer bottles, an ashtray and paper trash"* inside Panel 3's description, you have just handed the model a NEW free-text brief for that table, and it will invent a plausible-but-different one (wrong wood, wrong shape, wrong bottle layout) instead of copying the plate. Each independent re-description re-rolls the object. The fix: in section F, refer to recurring set elements by DEFERRING to the plate, never by re-specifying them. Write *"the SAME coffee table from `Image N` (the salon plate), with its props in the SAME positions"*, NOT a fresh adjective list. Spell out fresh detail ONLY for what genuinely changed this frame (a new object, a moved prop, a state change per `continuity.objects`); everything recurring is named as "the same X from the plate" so the model copies rather than reinvents.

#### D) Visual Tone
Colour grading, atmosphere, lighting quality, rendering approach. Consistent with section B but focused on mood and technical rendering.

#### E) Storyboard Layout Details — describe the clean full-bleed grid IN PROSE
The physical appearance of the sheet. There is NO template image attached anymore: you DESCRIBE the format here, in prose, woven into the brief.

The sheet is a **clean full-bleed contact-sheet grid**:
- Each panel's image FILLS its cell **edge-to-edge** (full bleed). The grid covers the WHOLE page, running to all four margins.
- Panels are separated ONLY by **solid PURE-BLACK gutter bars (#000000), clearly THICK (about 0.5% of the sheet's width, roughly 15-20px at 4K)**. Nothing else divides them. The thickness and purity are functional, not aesthetic: the app segments the sheet dynamically by finding these black bars, and thin or grayish gutters become indistinguishable from dark lines inside the panel imagery (verified failure). State it explicitly: *"panels separated by solid pure black gutter bars, noticeably thick, never gray, never thin hairlines"*.
- **UNIFORM GRID — say it explicitly in the prompt:** all cells are IDENTICAL in size; every row has exactly the same height and every column exactly the same width; the gutter lines are perfectly straight, parallel and continuous across the whole sheet. Leftover bare-black cells keep the same exact cell size; a partial or empty row is never taller, shorter or merged. Without this line the model sometimes redistributes space when a row is black, producing uneven rows (the reported proportion bug).
- **NO numbers on the panels.** Panels carry NO rendered numerals, letters or labels of any kind: the app's viewer overlays its own numbering. (Baked-in per-sheet numbers clashed with the viewer's global numbering: reported confusion.) State the negative in the prompt: "render NO numbers, letters or labels inside any panel".
- **NOTHING else is drawn:** no title banner, no PART/header strip, no floating cards, no rounded corners, no drop shadows, no caption bars, no timecodes, no shot-type labels, **no footer of any kind, no legend / icon row, no thematic-symbol icons with labels (e.g. "Temptation / Power / Escape / Observation"), no Project / Format / Pacing / Channel-Notes strip, no metadata row or column**. Only the panel images and the thin black separators. The bottom edge of the grid is the bottom edge of the image — there is NOTHING below the last row of panels.

Weave it in as one line, e.g.: *"Lay it out as a clean full-bleed grid of PERFECTLY EQUAL cells: every row exactly the same height, every column exactly the same width, the thin black gutter lines straight and continuous edge to edge; each panel's image fills its cell edge-to-edge, with NO numbers, letters or labels rendered inside any panel; empty grid positions stay bare black at exactly the same cell size. No cards, shadows, captions, banner or footer; the grid covers the entire page."*

Leftover grid positions (when the panels don't fill the grid) are **bare black background: no image, no number, nothing.**

⚠️ **If you restate the panel count / grid here, it MUST equal section A's** — the EXACT panel count, with any leftover grid positions called out as **bare board (no cards drawn there)**, never as "empty cells/cards". A layout line saying "12 sequential panels in a 3×4 grid" while section F lists 7 is the *"escribí 7 y generó 12"* bug: the model fills the grid. One number, everywhere (see section A's grid rule).

#### F) Scene Breakdown
Each panel described as: *"Panel [N]: [Shot type] shot. [Scene description with character action, environment, and emotional beat]."*

**When the input is an interactive storyboard JSON, this section is a FAITHFUL TRANSCRIPTION, not free writing (see the HARD STOP in Step 3).** Panel N = JSON shot N, in order: its scene description IS that shot's `action` (same events, nothing invented or dropped), its shot type is the shot's `shot`, and the environment is the shot's `scene.title`/`location` (e.g. a spaceship corridor — never flattened to "a room"). Re-read the JSON for the exact shot range of THIS PART; don't reconstruct from memory.

**📸 EACH PANEL GETS A SUPER-DESCRIPTION: a forensic, minute, self-contained photograph in words. The bar is not "rich": it is IMPOSSIBLE TO GET WRONG.** You hold ALL the sources: the shot's `action`, its `continuity` row ({ characters, objects, place }), the storyboard-level `continuity` LOCK, the `synopsis`, the character roster and the plates. YOU are the one who can see the finished frame; the image model only executes. Describe each panel as a FORENSIC INVENTORY of the frame, minutely:
  - every visible object NAMED, with its state, its position in frame and its size relative to a named neighbour;
  - the subject dissected: each hand and what it does, gaze direction, mouth/expression, posture, weight, which foot forward;
  - spatial layout: foreground/midground/background, frame left/right, camera height and distance, what the lens is at eye level with;
  - orientation of every directional object (what points up, what points down) with its negative;
  - light: every source in frame, its colour, what it illuminates, where the shadows fall;
  - the explicit ABSENCES (closed world, below) and the proportions (below).
  **The acceptance test for every panel: could two different painters, given ONLY your text, paint two DIFFERENT images? If yes, it is not precise enough: tighten until only ONE image is possible.** A 200-word panel that survives that test beats a 60-word gist every time; anything load-bearing left unsaid, the model fills from its prior, and the prior is usually wrong. The specific contracts:

- **🫙 ONE FROZEN INSTANT — a panel is a photograph, not a clip.** When a shot's `action` narrates several sequential moments (*"pierces the ceiling, falls, and on touching the floor melts it"*), do NOT transcribe the whole chain into one panel: the model renders the moments SIMULTANEOUSLY (the reported bug: a saber said to pass through the ceiling AND melt the floor rendered as a thin ceiling-to-floor beam, tiny in frame). Pick the single most readable instant (usually the decisive one: mid-fall below the ceiling hole), describe ONLY that instant, and encode the other beats as visible STATE: what already happened is evidence in frame (*"a small glowing hole in the ceiling above"*), what has not happened yet is explicitly not yet (*"the floor below still intact"*). If the beat genuinely needs more than one instant, expand it into keyframe panels (Step 3) instead of cramming.
- **🧭 FRAME GEOMETRY — state orientation and prominence, never physics.** *"Falls tip-first"* is physics; the model does not simulate physics. Say what the FRAME shows, geometrically, with the negative spelled out: *"the hilt at the TOP of the panel, the blue blade pointing straight DOWN into the floor, only the last hand-span of blade still visible above the melt point; the blade NEVER points upward"*. Same for size: if a panel's key subject must read (the saber alone in a storeroom), state its prominence explicitly (*"large in the foreground, dominating the frame"*) even in a wide shot; a wide of a big room with a one-meter object otherwise renders the subject tiny.
- **🚫 EXPLICIT ABSENCES — the closed-world rule (presence is the default; absence must be DECLARED).** Track every TRANSIENT element of the sequence (the falling sword, sparks, a character who leaves, a prop that is consumed) across the panel range yourself, panel by panel: in which panels is it IN frame, in which is it GONE. Then, in EVERY panel where a transient element is absent but appeared in nearby panels, NEGATE it explicitly: *"the sword is NO LONGER in this panel — it has already melted through and vanished below; NO hilt, NO blue blade, NO blue glow anywhere in this frame; only the small smoking red-edged hole remains"*. The whole sheet renders on ONE canvas: the model sees the element in neighbouring panels and paints it back into any panel that does not forbid it (the reported bug: the sword correctly absent in the aftermath panel 2, yet re-inserted in panel 3 and still standing in panel 5 after it had already melted through). Describing what IS in the frame is only half the contract; the other half is closing the world: what is not named as present or explicitly negated is exactly where the model improvises.
- **🔒 SCOPE the global locks — a motif stated as always-true gets painted everywhere.** When the storyboard's `continuity` LOCK describes a recurring event (*"the sword always falls tip-first punching small holes"*), do NOT transcribe it into the prompt as an unconditional, sheet-wide fact: phrase it CONDITIONALLY and scoped: *"WHENEVER the sword appears in a panel (panels 1 and 4 only on this sheet), it falls hilt-up, blade straight down..."*, naming the exact panels where the motif applies when the list is short. An unscoped motif paragraph biases every cell toward containing the motif, which is the other half of the sword-reappearing bug. Invariant locks about state (the burn mark, the intact ceiling, hole alignment) stay global; EVENT motifs get scoped to their panels.
- **📏 RELATIVE PROPORTIONS — state size RELATIONSHIPS, never bare adjectives.** The model has no physics and no consistent scale: "a small hole" means small relative to the FRAME, not relative to the object that made it. Whenever two story-critical objects interact (a hole and the blade that melted it, a step-object and who stands on it, a prop and the hand holding it), write their scale relationship explicitly, anchored to a named object, with the negative: *"the melt hole is barely wider than the blade itself, about the hilt's diameter, NEVER wider than the hilt"*; *"the blue blade is about THREE times the length of its hilt"*. Reported bugs from omitting this: a melt hole rendered wider than the whole saber (unbelievable), and a blade rendered stubby at half its reference length.
- **🔦 SMALL-BUT-CRITICAL PROPS — redundancy beats one mention.** When a critical prop renders SMALL in its panel (a saber behind two large faces), a single state word gets lost and the model defaults to how the prop looks in NEIGHBOURING panels on the same canvas. State it three ways: the state itself (*"the saber is IGNITED, its blue blade fully extended"*), its visible EFFECT on the scene (*"its electric-blue glow lights both faces from below"*), and the negative of the wrong state (*"NOT the unlit hilt"*); if the prop is the narrative point of the panel, also give it prominence (*"clearly visible between them"*). Reported bug: the mid-air saber in a two-shot rendered UNLIT even though "ignited" was written once, because panels 2-5 around it all showed the unlit hilt.

**🧩 FIRST classify panels into CONTINUITY RUNS from the STRUCTURED JSON fields — BEFORE writing a single panel description. This is the step the agent keeps skipping, and it is the root of the consistency bug.** The JSON already tells you, mechanically, which shots belong to one unbroken take. Read these structured signals (NOT prose keyword-matching) and group accordingly:
- **`noCutBefore: true` on a shot** = it is glued to the previous shot, no cut between them.
- **Several shots sharing the SAME `number`** = one authored shot the user split into glued sub-shots (one continuous take). In `vago-couch-15s.json` ALL three shots are `"number": 1` with `noCutBefore` on shots 2 and 3.
- **The storyboard-level `synopsis` / `continuity` describing one unbroken take** (a "plano secuencia" / one-er / "sin cortes" / "single continuous shot"). Read it for MEANING, not for a literal string match.
- **`movement` progressing while the subject stays put** (Dolly in → Dolly in → Static) = the camera moves through ONE space, it is not three separate setups.

**When these signals say the whole storyboard (or a run of shots) is ONE continuous take, that run is a SINGLE delta chain: panel 1 establishes, and panels 2…N are each "IDENTICAL to the previous panel except the camera has moved to X".** There is NO cut, so nothing in the world or the character's pose may re-roll between them: the man's body, wardrobe, the sofa, bottles, table, TV content all PERSIST frame to frame, and ONLY the framing advances along the camera move. Treating each glued sub-shot as an independent setup (re-describing the room and the pose from scratch) is exactly what produced the drift the user reported on this very storyboard. A continuous take is the STRONGEST case for the delta rule below, not an exception to it.

**🔗 DESCRIBE EACH PANEL BY ITS DELTA FROM THE PREVIOUS ONE (the most reliable consistency lock) — for ANY run of panels sharing the same moment, not just flagged continuous takes.** The trigger is broader than most agents assume. Apply the delta rule whenever consecutive panels show the SAME character in the SAME ongoing physical situation (same location, same beat, the pose has not changed in the story), which covers BOTH:
> - the SAME continuous shot (a camera move broken into keyframes, or shots flagged `noCutBefore` / sharing a number), AND
> - **DIFFERENT shots across a hard cut that are still the same held moment seen from a tighter / different angle** (e.g. a medium, then a medium-close-up, then a close-up of the same man reclined on the couch). These are SEPARATE shots in the JSON, so the agent treats them as independent and re-describes the pose from scratch each time, and it drifts: this is exactly the reported bug where Panel 3 has his legs extended on the couch and Panel 4 silently sits him up, then Panel 5 changes the hands. Same character + same unbroken moment ⇒ delta rule, even across a cut.
>
> Independently re-listing the pose and hoping the descriptions match is what lets it drift. Instead, **anchor each panel to the one before it and describe ONLY what changes:**
- Open by asserting sameness, THEN state the single delta. E.g.: *"Panel 4: IDENTICAL to Panel 3 — same room, same beige sofa, VAGO_A in the EXACT SAME reclined pose with both legs extended horizontally along the couch, same wardrobe and lighting. The ONLY change: the camera has dollied closer and tilted up, now framing him waist-to-torso. Do NOT change his pose, bend/lower his legs, or sit him up."*
- **This works because the whole sheet is ONE generation** — the model can SEE Panel 3 on the same canvas, so *"identical to Panel 3 except…"* is a constraint it can actually satisfy, far more robust than two independent descriptions that must happen to agree.
- **One delta per step.** The change is exactly one thing (the camera moves, OR he raises the bowl, OR he turns his head). Everything you do NOT name as the delta is, by this instruction, unchanged from the previous panel — including body POSE, torso angle and limb position, not just objects/setting.
- This is the carry-forward rule's strongest form: *"same as the previous panel except X"* generalises the state forward automatically. Use it for EVERY run of panels that share a moment: every continuous-take group AND every cut to a tighter / different angle of the same held beat (per the broadened trigger above).

Distribute character details across panels — mention hair and face in close-ups, full outfit in wide shots, signature accessories when they'd be visible. **Don't front-load all character description into Panel 1.**

Weave dialogue / action notes naturally into the panel descriptions where relevant.

**🔬 PHYSICAL-DETAIL FIDELITY — describe how the action ACTUALLY happens, not a vague gist.** The model renders your words LITERALLY and fills every gap you leave with a plausible-but-often-WRONG detail. This is the *"everything is right except the details"* bug. For action panels (especially close-ups of hands / objects), spell out the real-world mechanics:
- **Singular, not vague plural.** "inserts **coins**" → the model draws a hand fanning 2–3 coins into the slot at once (nobody does that). Write **"inserts a single coin, held between thumb and forefinger,"** — one object, one natural grip. Only say "two coins" if two are genuinely meant to be visible at once.
- **Name the grip / contact / which finger.** "presses the button" → which finger, from what posture. "reaches high on tiptoes to press the LOW button" is self-contradictory (high vs low) and produces an awkward pose — describe the real posture: *"crouches slightly and presses the low button with his index finger."*
- **Zero ambiguity — every target a concrete identifier, never an interpretable one.** Anything the model can't resolve to ONE exact thing, it picks at random. *"presses his floor's button"* → *"presses button **2** (of 16 floor buttons)."* *"grabs his suitcase"* → *"grabs the **red** suitcase on his left."* Numbers, colours, positions — nothing doubly-interpretable survives into the prompt.
- **One physical step per panel.** If the storyboard shows insert-coin then press-button as separate beats, each panel shows exactly that one mechanical action, done the way a real person does it.
- **🎬 CONTINUITY (raccord) — carry the established state into EVERY panel, or the render drops it (the #1 neglected thing).** Once a panel puts the character or world into a non-default state (standing ON the stacked cans, holding the can, a hole melted in the floor, a door opened), **every later panel where it still holds MUST restate it in that panel's description** — even a hand close-up. The model renders each panel semi-independently and snaps back to the default unless you re-state it. Exact bug to never repeat: panels 13-14 said *"on top of the two cans"*, panel 15 said only *"presses the Pepsi button"* → the boy was rendered back on the ground. Panel 15 MUST read *"standing on the two stacked cans, presses the Pepsi button"*. The state persists in the TEXT until a panel explicitly changes it. (Plus the basics: same object/hand position, lighting, screen direction across cuts.)
  - **⚠️ The source `action` may be WRITTEN BY THE USER and incomplete** — they may have typed the interactive storyboard themselves and forgotten to restate the state in a later shot. **DO NOT inherit that omission.** Read the WHOLE shot range, track the world/character state yourself across the sequence, and **RESTATE the carried-forward state in every panel where it logically still holds, EVEN IF that panel's `action` text dropped it.** This OVERRIDES the faithful-transcription rule's "copy the action verbatim" for the purpose of continuity: you never add a new EVENT (the action stays what the JSON says), but you DO re-inject the established state the source forgot. Keeping the world consistent is always what the user wants, even when they didn't type it. **This is where CONTINUITY (raccord) must be airtight — the sheet/video are the last line of defence against a sloppy source.**
>   - **When the shot carries a `continuity` field ({ characters, objects }), that work is already done for you** — it is the explicit, per-panel current-state the author (or the visor) wrote. Render both columns as the ground truth for that panel and you get carry-forward continuity for free; you only fall back to tracking the state yourself across the sequence when `continuity` is absent (legacy shots may instead carry a single free-text `state` string — same treatment). If a panel's `continuity` contradicts its neighbours (an object crushed in one, intact-and-stood-on in the next), the SOURCE is self-contradictory — render the physically coherent reading the `synopsis`/`continuity` LOCK imply and flag it to the user rather than reproducing the impossible state.

This is NOT inventing new events (Step 3's faithful-transcription still holds): the WHAT stays the JSON's action; you're only specifying the HOW with real-world-correct, unambiguous mechanics so the model can't improvise a wrong detail.

#### G) Art-direction & quality cues — PROSE ONLY, NEVER drawn
Technical rendering and quality cues woven into the brief's prose: facial expression quality, camera angle variety, texture detail, environmental detail, atmospheric effects, composition principles. Tailor to the style. ⚠️ These describe the IMAGE QUALITY *inside* the panels — they are NOT a caption, label or footer. NEVER render them as a strip, box, column, legend or icon row on the sheet (the sheet has none — see section E).

**Per-type variations:** when the user named a video type (ad / explainer / tutorial / demo / social-post), pull the type's brief-context note, caption style, shot mix and audio cue from `VIDEO_TYPE_<TYPE>.md`. Don't paraphrase from memory — read the file. That per-type "brief context" is internal guidance that shapes the panels — it is NEVER drawn on the sheet (no footer, no notes column).

#### H) Render quality & format — PROSE ONLY, NEVER drawn
Final technical specs woven into the prose: render quality cues, aspect ratio, format declaration (*"professional panel sheet"*), quality tier (*"masterpiece quality"* / *"production-ready"*). These tell the model HOW to render the image; never draw them as a banner, label or footer on the sheet.

### Prompt length targets

Storyboard image prompts run longer than single-image prompts because they encode the layout structure AND a forensic SUPER-DESCRIPTION per panel (see section F). **The panel breakdown is where the budget goes: 150–250 words PER PANEL for action panels (simple inserts may take less, never below what the two-painters test demands).** Style, layout and quality boilerplate stay tight; panels stay exhaustive.

- 9 panels: 1,400–2,200 words
- 12 panels: 1,800–2,800 words
- 15 panels: 2,200–3,400 words
- 20 panels: 2,800–4,200 words

Never compress the per-panel descriptions to hit a length: if the prompt must shrink, trim the style/quality prose first, the panels last. Every panel description needs enough detail to fully determine its frame and differentiate it from adjacent panels.

---

## Step 5 — Generate the sheet(s) (call `generate_image`)

Once the prompt(s) are composed, call `generate_image` to produce the sheet(s). **Do NOT show the raw prompt to the user as the deliverable** — the artefact is the rendered image.

**When chunking produced K > 1 sheets, this is K separate `generate_image` calls — one per PART, STRICTLY IN SEQUENCE, NEVER in parallel.** Walk PART 1 → PART K, awaiting each fully before starting the next: render PART K, WAIT for its result, `show_result` it, and ONLY THEN start PART K+1 (which must carry PARTs 1…K in its `referenceImages` per the cross-sheet rule above). Do NOT batch the calls, do NOT fire them in a parallel block, do NOT kick off PART K+1 before PART K has returned — a later sheet that renders before its predecessor exists has nothing to lock identity against and the actors' faces drift sheet to sheet (the reported bug). Each call has its OWN prompt (from Step 4) with that PART's panel breakdown; sections B, C, D, E, G, H stay essentially identical across calls (same style / characters / grid layout) for visual continuity. The `show_result` after each PART also lets the user review it early.

Required call shape (per sheet):

- **`prompt`** — the full composed prompt block from Step 4 for THIS PART (long-form is intentional).
- **`referenceImages`** — **EVERY user-uploaded reference, no exceptions, no subject-level dedup.** Pass them as absolute paths or `@handles`, in the exact order you wrote down in Step 2's positional mapping (hero / most-used character first WITH ALL its photos, then secondary characters WITH ALL their photos, then products / objects, then locations). The position in this array IS `Image N` in the prompt body — drop one and the model has no clue what `Image N` is. The reference list is IDENTICAL across PARTs.

  **🎬 The array carries EVERY user reference, and for PART K ≥ 2 the prior approved sheet(s) for continuity. NO format template is attached anymore: the clean-grid format is described IN PROSE (section E).** Build `referenceImages` EXACTLY like this:
  - **PART 1 / single sheet:** `[ …every user reference (Step 2 order: hero + ALL its photos → secondary chars → products → locations)… ]`. No template entry, no extra.
  - **PART K ≥ 2:** `[ sheet_part_1 … sheet_part_{K-1}, …every user reference… ]` (prior approved sheets first, per Step 3) so the clean grid format AND the style stay consistent across sheets.

  **Pre-flight count check (BEFORE the call, every time):**
  1. Count the user-attached refs (storyboard JSON root + every scene + every shot, deduped, `@handles` resolved) plus the form's picker uploads.
  2. `referenceImages.length` MUST equal: on PART 1 / single-sheet, **exactly that user count** (no extras); on PART K ≥ 2, **that user count + (K-1)** (the prior sheets). If it's SHORT, you either collapsed several photos of one subject into one slot (*"le he puesto varias imágenes de la misma chica y ha puesto 1 sola"*) OR, on a later PART, dropped a prior sheet (*"no ha adjuntado el de referencia"*). Re-do the array.

  Each entry's array position IS its `Image N` in the prompt body (anchor every user reference per Step 2). On PART K ≥ 2 the prior sheets are anchored by the continuity block in Step 3.
- **`aspectRatio`** — the SHEET aspect that matches the grid YOU chose (section A). Recommended: derive it so cells approximate the video aspect (`sheetAspect = videoAspect × cols/rows`). Do not pass the VIDEO aspect itself unless your chosen grid genuinely implies it.
- **`resolution`** — `4k`. **MANDATORY.** Combined with the sheet aspect this yields a ≈ 3312 × 2480 px sheet (or its portrait twin). Panel sheets need 4K so each panel's imagery holds detail across the grid. At 1080p the panels compress into mush, that's the reported "ha generado una que no es 4K" bug.
- **`saveTo`** — a directory the user can locate later (`~/.koi/images/` is the default; pass the project folder when one is active).
- **`summary`** — one-liner. Single-sheet storyboard: *"`<title>` — visual panel sheet, `<duration>` s, `<panel-count>` panels, `<aspect>`"*. Multi-PART: *"`<title>` — PART K / K_total, `<duration>` s, `<panel-count>` panels"*. Self-evident in `recall_creations`.
- **`metadata`** — when the input is an interactive storyboard JSON, stamp:
  - `sourceStoryboard: <absolute path of the JSON>`
  - `storyboardPart: K` (1-based, this sheet's index)
  - `storyboardParts: K_total` (the total number of sheets in this chunk)

  This is what `visual-panels-to-video` later uses to re-attach the JSON and resolve each clip's exact duration from the per-shot data. Omit only when there's no source JSON.

After each `generate_image` succeeds, call `show_result` with that sheet's saved path so it opens in the user's working area. For multi-PART, do this PER PART (not just at the end) — the user sees PART 1 land while PART 2 is still rendering.

---

## Step 6 — Companion note

After the image lands, write a **short** (3–5 sentence) note covering:
- Style choices made for anything the user didn't specify
- Which character details came from uploaded references vs inferred from the story
- One or two refinement suggestions (e.g. *"If the panels blend together, I can re-render with stronger black borders between cells"*)
- Handoff: *"When you're happy with this sheet, I can render the final video — composed per-clip prompts + rendered clips + assembled timeline — via `visual-panels-to-video`."*

---

## Handling variations

**User provides a full beat sheet:** Skip Step 3 — map their beats directly to panels. Adjust panel count to match their beat count if it differs from 15.

**User provides only a logline:** Decompose into a full beat sheet using three-act structure before composing. Briefly show the breakdown so the user can redirect.

**User wants to iterate on specific panels:** Re-call `generate_image` with the same references and a revised prompt that adjusts only the affected panels' descriptions. Keep the rest of the prompt unchanged.

**User wants a different panel count:** Redistribute the narrative beats across more or fewer sheets (12 panels max per sheet) and pick whatever uniform grid holds them. Fewer panels means each beat carries more narrative weight; more panels allow transitional moments and reaction shots across additional PART sheets.

**User wants a vertical (9:16) video:** prefer a PORTRAIT sheet (e.g. `aspectRatio: "3:4"` with a 4×3 grid) so every cell is natively vertical. Stamp whatever grid you chose in `metadata.grid`; the panel tools auto-detect it anyway when fixing panels.

**Style is mixed or hybrid:** Build section B to explicitly call out the hybrid nature ("anime-influenced but rendered in 3D", "live-action with animated elements") and which elements follow which visual rules.
