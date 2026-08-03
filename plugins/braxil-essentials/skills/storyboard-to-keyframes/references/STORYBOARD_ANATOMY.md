# Storyboard Anatomy: Phase 1 Spec

Authoritative spec for building a 4K keyframe SHEET from a story idea + character refs. `storyboard-to-keyframes` `SKILL.md` delegates here, read THIS first. Output = one composite image (the SHEET) via `generate_image` at 4K. **Never deliver the raw prompt text; the artefact is the rendered image.**

---

## Step 1: Gather inputs

⛔ **HARVEST FIRST, ask ONLY for what's missing.** Need (1) visual style, (2) each recurring character's ref. Harvest style from anything said ANYWHERE in the conversation OR a NON-EMPTY `stylePrompt` in the source JSON; harvest refs from attachments OR the storyboard's `references`. Raise `prompt_form` only for still-unknown fields; skip entirely if nothing missing. **NEVER infer style from topic/brand/vibe**: if not provided anywhere, ask, never guess.

### The form: 3 fields, ONE `prompt_form`, in order (never split into rounds; pre-fill answered fields)

**Field 1: Visual style (required).** SELECT: **Premium 3D** (Pixar/DreamWorks family-film), **Claymation** (handcrafted stop-motion plasticine), **Realistic UGC** (phone-shot social), **Custom** (free-text 1–2 sentences → compose phrasing per `STYLE_PRESETS.md` custom flow). Preset phrasing blocks live in `STYLE_PRESETS.md` (`<skill_directory>/references/STYLE_PRESETS.md`), read BEFORE composing so the block lands in section B verbatim. Never infer style from brand/topic (Chanel≠luxury-live-action, Pokémon≠anime, kids'≠3D). **Skip Field 1** if EITHER (a) user named a style anywhere ("fotorrealista", "el mismo de antes"), OR (b) source JSON `stylePrompt` NON-EMPTY (honour verbatim). Required only when `stylePrompt` empty AND no style mentioned.

**Field 2: Per-character image picker (one optional field per recurring character):**
```
{ label: "Imagen de referencia para <CHAR_LABEL> (opcional)",
  files: { multiple: false, extensions: ["png","jpg","jpeg","webp"] } }
```
- `files:{…}` MANDATORY (drop-zone/Browse/thumbnail picker); NEVER a text input asking for a path. Always optional.
- A char may exist in the gallery as an `@handle`: user names it in Field 3 instead of uploading; resolve and use as its ref.
- **Which chars get a picker:** JSON path → every entry in the `characters` roster (`RATÓN_A`,`GATO_A`). Idea-only → one per named char; if unclear who recurs, one generic `protagonista`. Refs already attached / in `references` → use directly. SINGLE char + SINGLE photo → MAP and proceed, no picker. Add pickers ONLY when mapping is genuinely ambiguous (several chars/photos, unclear whose) → pre-populate with uploaded paths. Never silently mis-map; never re-ask the obvious.
- Every filled picker + every Field-3 `@handle` MUST reach `referenceImages` AND be anchored `Image N` (Step 2).

**Field 3: Free-text notes (optional, ALWAYS last):**
```
{ label: "Anything to keep in mind before I generate? (opcional)", allowFreeText: true }
```
User adds direction, can `@`-reference gallery assets. After return: resolve every `@handle` (`resolve_handle` → path as ref with that subject's alias) and fold the rest into the prompts (CHARACTER/SETTING lines, lighting, per-panel emphasis).

### Optional inputs (apply if given in the initial message, else default, NOT in the form)
- **Panel count**: default 15; allowed 9,12,15,20.
- **Duration**: default 15 s.
- **Aspect/grid**: YOU pick the grid per sheet (any uniform cols×rows fitting the count, 12 panels max). The sheet is a NEUTRAL READING SURFACE, **NOT the video's format** — aspect ratio is a VIDEO decision made later (one storyboard → many formats), so do NOT tie the sheet to a target platform. Default to comfortable landscape cells (≈`3:2`/`16:9`) with a tidy grid; the video model reframes to whatever format the user picks at generation time. Whatever you pick: pass sheet aspect as `aspectRatio` + `resolution:"4k"`, keep the grid UNIFORM with straight pure-black gutters, stamp `metadata.grid`. Tools + viewer auto-detect the grid from pixels; no shape mandatory.
- **Video type**: ad/explainer/tutorial/demo/social-post; when named, ALSO read `VIDEO_TYPE_<TYPE>.md` for its caption style, shot mix, audio cue (never all five).
- **Target image model**: default Nano Banana Pro; GPT Image 2 also works (slightly more explicit layout phrasing).
- **Story overview**: usually already in the message; use directly. Zero narrative content → ask ONCE via `prompt_user` ("What's the story/topic?"), then proceed.

---

## Step 2: Analyse character / product references

Per uploaded ref extract: **Identifying features** (face structure, skin tone, hair colour/length/texture/style, age, build, marks; products: silhouette, material, colour, label/logo/typography, finish); **Clothing & accessories** (garments, colours, materials, fit, layering, signature items, chars); **Design language** (proportions, palette, silhouette readability); **Personality cues** (posture energy, expression tendency, chars). Build a compact **80–150 char "DNA"** per ref. Multiple refs → distinct non-blurring ids (`HERO_A`, `PRODUCT_BOTTLE`).

### Positional anchoring: CRITICAL (canonical rule; all later sections defer here)
**Every user ref MUST be anchored by position (`Image 1`,`Image 2`,…) in the prompt body AND included in `referenceImages`.** Generators only see what's in the call and only know which ref is which subject if the prompt says so. Missing anchor = silently-ignored ref.

**Collecting from a JSON: refs live at THREE levels; walk all, union deduped by path/`@handle`:** `storyboard.references` (root) → each `scene.references` → each `shot.references` → dedupe by absolute path (resolve `@handles` first) → add Step 1 picker uploads. Don't read only shot-level; identity often lives at root/scene level.

**⚠️ SETTING/LOCATION plate = most-dropped ref.** A photo of a ROOM/SET/location (not person/product) is the setting plate; it MUST reach `referenceImages`, anchored as `SET_*` (C2), like a character. **Persist it:** if attached only to chat, write it into `references` (root or `scene.references`) via `save_storyboard` so every future regeneration/agenda-run re-collects it. **Generate if missing but recurring:** no plate + location spans multiple panels → generate one establishing plate FIRST, persist it (`scene.references` and/or a `locations` Library asset), anchor every panel to it.

**Multi-ref of the SAME subject: NEVER collapse.** Multiple photos of one char (front/side/back, outfits, expressions, candids) are ALL load-bearing. NEVER dedupe at SUBJECT level to one "best" photo. Pass EVERY ref with its own position and anchor the subject across all positions ("Match `HERO_A` to `Image 1,2,3,4`: five photos of the same character; use all jointly to lock face/hair/build/wardrobe; do not invent features absent from the references"). Dedupe by PATH only, never by subject.

**Order (decide before writing, keep):** 1) hero/most-used char, all its photos contiguous (front, then alt angles, then outfits/expressions); 2) secondary chars, same pattern, all of one before the next; 3) extras GROUP sheets; 4) products/objects together; 5) setting/location plates last. Write the mapping now (one line per position, "Image 1=HERO_A front; …; Image 6=PRODUCT_BOTTLE") and reuse verbatim in section C.

---

## 🎬 Step 2b — BUILD THE CAST AND THE SETS **FIRST** (MANDATORY before any sheet render)

**The panels are generated FROM these assets, never from prose alone.** Prose does not stop a face or a room re-rolling cell to cell; a turnaround and a set plate do. Build whatever is missing, THEN render the sheet.

**1. ACTORS — one character TURNAROUND per recurring character, generated with SEEDREAM.**
- **Exists already** (Library, `references`, a previous run)? **Reuse it — never regenerate**: a second generation drifts the identity.
- **Missing → generate it with `generate_image` using SEEDREAM** (current slug/params in the `image-generator` skill). **Seedream specifically, not another model**: a Seedream-born image ALSO clears Seedance's face filter downstream, so `keyframes-to-video` can attach the turnaround as-is with no extra laundering pass.
- **Layout = model-sheet turnaround, 2 rows × 4 columns, wide (16:9)**: top row = four full-body standing views (front, right-side profile, left-side profile, back); bottom row = four head-and-shoulders close-ups (front, three-quarter, side profile, back of the head); plain neutral seamless grey studio backdrop, even flat studio lighting. **Prompt template** (fill `<…>` from the storyboard's `characters` roster):
  > `A photorealistic character model-sheet turnaround of ONE <male/female> character on a plain neutral seamless grey studio backdrop, even flat studio lighting. Match the face and identity to the character in Image 1. Layout: two rows by four columns. Top row = four full-body standing views: front, right-side profile, left-side profile, and back. Bottom row = four head-and-shoulders close-ups: front, three-quarter, side profile, and back of the head. <CHARACTER DESCRIPTION: build, age, hair, facial hair, wardrobe, accessories, footwear>. Keep the face and build IDENTICAL across all eight views. Clean production character-reference sheet aesthetic, photorealistic, no text, no numbers, no logos, no watermark.`
  - User photo of that character → pass it as **Image 1** (identity match). No photo → drop the "Match the face…" line and build from the roster description.
- **PERSIST it** — `save_storyboard` into `references` (root) and/or a `characters` Library asset — so every later regeneration / agenda run re-collects the SAME turnaround instead of inventing a new face.

**1b. EXTRAS — one GROUP SHEET per recurring group of background people, generated with SEEDREAM.**
- **Who counts:** any UNNAMED group that appears in more than one panel or is story-relevant — a caravan of riders, a crowd, soldiers, waiters, a film crew, villagers. **No group sheet → every panel (and later every clip) re-invents their number, faces, wardrobe and ethnicity from scratch** — the same drift bug as an actor without a turnaround, multiplied by the whole group.
- **Seedream specifically** (same reason as the actors: extras have FACES, and only a Seedream-born image clears Seedance's face filter downstream — `keyframes-to-video` attaches this sheet as-is).
- **Layout = group lineup, one row, wide (16:9)**: 4–6 representative extras standing side by side, full body, front view, plain neutral seamless grey studio backdrop, even flat studio lighting. For a large crowd DON'T render dozens: the sheet locks the LOOK (wardrobe, era, palette, types), not the headcount — the panel/clip prompt states the real number. **Prompt template:**
  > `A photorealistic group reference sheet of <4–6> background extras on a plain neutral seamless grey studio backdrop, even flat studio lighting. Layout: one row, all extras standing side by side, full body, front view. <GROUP DESCRIPTION: who they are, age/build variety, wardrobe/uniform, era, props they carry>. Distinct faces, consistent wardrobe style across the group. Clean production character-reference sheet aesthetic, photorealistic, no text, no numbers, no logos, no watermark.`
- **Anchor it like a character** (`EXTRAS_CARAVANA`, `EXTRAS_CROWD`…): every panel where the group appears anchors it positionally ("The riders match the extras in Image N — same wardrobe, same types; the count comes from the action text").
- **PERSIST it** (root `references` and/or Library) and reuse — regenerating drifts the group's look, exactly like an actor.

**2. SETS — one establishing PLATE per recurring location, with the image model of YOUR choice.**
- No face on a room → no filter concern → **pick whatever model renders that look best** (Nano Banana Pro, GPT Image 2, Seedream… your call per the `image-generator` skill). This is the deliberate difference vs the actors, which are Seedream-only.
- One wide canonical view of the location, obeying the storyboard's `lighting` design, so every panel set in it matches.
- Reuse if it exists; otherwise generate and **persist** it (`scene.references` and/or a `locations` Library asset).

**3. THEN render the panels FROM them.** Every panel prompt anchors the cast turnarounds, the extras group sheet(s) and the set plate(s) **positionally** (`Image N`, per the anchoring rule above) and includes them in `referenceImages`. The sheet is composed from these references — cast + extras + sets — not from description alone.

⚡ Cast, extras and sets are independent: **generate them in PARALLEL**; the sheet render waits for all.

> 🔴 **These assets are PERSISTED and re-used downstream — so a later change to the set or to a character must UPDATE THEM, not just the panels.** `keyframes-to-video` re-attaches the set plate and the turnarounds to Seedance on every clip; a stale plate/turnaround silently drags the OLD décor or the OLD identity into the video even when the sheet looks correct. When the user changes the set/décor/background → regenerate the PLATE and persist it over the old one FIRST; when they change a character's look → regenerate that TURNAROUND (Seedream) and persist it FIRST. Then re-render the affected panels against the new reference. See the set/cast rule in `SKILL.md` § Fixing panels.

---

## Step 3: Break the story into beats

> 🛑 **HARD STOP: with a JSON input the SHOTS are fixed; do NOT invent story beats.** JSON shots = source of truth (same events/order, nothing added/dropped at STORY level). Default = **one panel per shot, in order.**
>
> 🔒 **HARD RULE — EXACTLY ONE panel per storyboard shot. NEVER more.** One JSON shot entry = one panel on the sheet, always, whatever its camera movement. **panel count = number of shots**, every shot present, in order. Do NOT expand a moving shot into 2/3 start-mid-end keyframes — that is FORBIDDEN. Convey the movement with the panel's caption/`movement` note and let `generate_video` infer the camera trajectory from that single frame; intermediate keyframes would over-constrain the motion (user's explicit preference: the model invents the path, we do not pin it with in-between frames). Also still forbidden: re-decomposing the story, adding beats/reactions, padding to a per-type range, dropping shots to fit a grid.
> (`noCutBefore` continuation shots are SEPARATE authored shot entries and each still gets its own single panel — that's the author splitting a take, not an automatic expansion. This rule bans the AUTOMATIC one-shot→many-keyframes expansion, nothing the JSON itself authored.)
>
> **Camera-movement shots → STILL exactly ONE panel (never 2–3).** When `movement` describes the camera MOVING (push-in/dolly, pan, tilt, crane, orbit, tracking/follow, whip), render ONE panel for that shot — pick the most readable framing of the move (usually its START, or the decisive instant) and put the movement in the caption ("Wide — slow dolly in") so `generate_video` drives the camera itself. Do NOT emit start/mid/end frames: the video model infers the trajectory from the single keyframe, and pinning intermediate frames only over-constrains and can degrade the motion. (Default-15 / per-type ranges apply ONLY with NO JSON — a prose brief from scratch — and even there it's one panel per beat.)
>
> **Transcribe each shot FAITHFULLY: JSON is the SINGLE SOURCE OF TRUTH, not an idea to embellish:**
> - **Action**: panel scene description IS `shot.action`, as-is; same events/order, invent/drop/"improve" nothing. (Translate to English + IP-alias per Step 4, but the WHAT matches the JSON.)
> - **`synopsis` (story premise): HARD CONSTRAINT every panel obeys.** Read storyboard-level `synopsis` (+ `scene.synopsis`): the physical/causal logic the piece depends on; OVERRIDES a terse `action`. (Premise "button mounted HIGH, out of the child's reach → he stacks cans": even a shot "boy presses button" MUST show it HIGH/unreachable.) Conflict → premise WINS; render the action THROUGH the premise.
> - **`continuity` array (storyboard-level LOCK): INVARIANTS = absolute negatives.** Each entry holds for EVERY panel, NEVER broken/"fixed" (the negatives the premise implies but models won't infer: "button stays high, never lower it or make him taller"; "step-cans stay intact, never crushed"). `synopsis`=WHY, `continuity`=WHAT MUST NOT CHANGE.
> - **`shot.continuity` ({ characters, objects }): authoritative per-panel state.** `characters` = where each char is, pose, wears/holds; `objects` = state of each key prop/scenery IN THAT FRAME. Render both precisely; they OVERRIDE any default the bare `action` snaps to. Structured form of carry-forward; trust it over re-deriving. (Legacy: single free-text `shot.state` string, same treatment.)
> - **Setting**: `scene.title`/`location` = WHERE; carry it in ("Nave-El Accidente"→spaceship corridor). Never flatten to a generic "dimly lit room".
> - **Shot type/movement/duration/dialogue**: copy `shot`/`movement`/`duration`/`dialogue`(`audio`) verbatim; don't reassign types "for variety". Do NOT apply the narrative-arc principles below (they RESHAPE the story = **IDEA-ONLY**). A JSON storyboard is already directed; transcribe, don't re-direct.
> - **Chunked multi-PART:** re-read the JSON and transcribe EXACTLY that PART's shot range every time; never free-write from summarized memory.

**Idea-only decomposition** into the target count (default 15). Each beat: 1) **Panel number** (1–N); 2) **Per-shot duration** (fractional OK here; SUM = total); 3) **Timecode** (`00:00–01:00`); 4) **Shot type**: Wide, Medium, Close-up, Low Angle, High Angle, Dynamic, Over-the-shoulder, Macro, POV (POV = camera angle, not a style; combines with any); 5) **Scene description** (one sentence); 6) **Action/Dialogue** (or "None").

**Narrative-arc principles (IDEA-ONLY):** **Acts**: even in 15 panels follow 3 acts (1–3 setup, 4–6 inciting incident, 7–10 rising tension, 11–13 climax/resolution, 14–15 denouement). **Shot variety**: never repeat a type in consecutive panels; alternate establishing shots and intimate close-ups. **Emotional escalation**: build through the middle, peak ~10–12, resolve; close-ups for peaks, wides for context. **Character consistency**: surface identifying details where visible at that shot size.

---

## Chunking: split into multiple PART sheets when total duration > 15 s

Happens BEFORE Step 4. Stops a 28 s storyboard being silently cropped to 15 s. **TWO distinct groupings:**
- **Clips**: contiguous shot groups, each **≤ 15 s** (`generate_video` `duration` enum = whole seconds 4–15, plus `"auto"`); each → ONE downstream video clip (video unit; old spec's "PART").
- **Sheets**: a 4K storyboard image (= ONE `generate_image` = the cost); holds up to **12 panels**, can carry **several WHOLE clips** (image/cost unit).

Win: a sheet is no longer tied to one clip: a 30 s storyboard of 3 short scenes = 3 clips on ONE 12-panel sheet (fewer calls = less money). `keyframes-to-video` reads `metadata.clips` to know which panels feed which clip and renders one `generate_video` per clip, concatenating. Hard limits: clip ≤15 s, sheet ≤12 panels, a clip NEVER spans two sheets.

**Read `totalDurationSeconds` from the JSON root, DON'T hand-sum.** The app stamps it (+ `shotCount`) on every save; authoritative, always in sync; overrides any duration in brief/form/task. Cross-check vs the visor's per-scene `SEG` labels. **Fallback only if absent** (older storyboard): sum `shot.duration` across EVERY shot of EVERY scene.

### Step A: group shots into CLIPS (≤15 s each, VIDEO grouping)
At least `ceil(totalSeconds/15)` clips. **Cap each clip at ≤12 PANELS too** (one panel per shot, so ≤12 shots): open a new clip the moment the next shot would exceed **EITHER 15 s OR 12 panels**. (Below, every "PART" = one CLIP; sheet-packing is Step B.)
1. **Group in order, keeping each continuous action WHOLE** (boundaries = hard cuts; place at natural breaks, never mid-motion):
   - 🔒 **`noCutBefore:true` = INSEPARABLE:** a continuation of the previous shot (one continuous take, no cut, shares a number). The whole glued run lands in the SAME clip and counts as one atomic unit vs the caps.
   - Keep a whole **scene** in one clip when it fits (use `scenes[]` as guide); keep a **continuous causally-linked action** together (chase, "draw→shoot→shatter", unbroken move). Cut only at natural breaks (scene end, location change, time jump, settled beat). A continuous action >15 s → cut at its CALMEST internal moment.
   > 🛑 **DO THE ARITHMETIC EXPLICITLY: never eyeball (#1 chunking bug).** Write a running cumulative sum shot-by-shot in order: `shot <n> (<dur>s) → total <Y>s`, EXACT durations, no mid-round. Open a new PART the moment the next shot pushes past 15 s (or a clean scene break before 15 s); reset to 0. Ex (43 s,18 shots): shot1(2)→2…shot7(2)→13; +shot8(4)→17>15 ⇒ **PART1=shots1-7=13 s** (NOT "1-6=14 s"). A PART's stated duration = literally its shots' running total (must match; if not derived by summing, redo). **DOUBLE-CHECK in reverse:** re-add the exact shots independently; if forward≠reverse, re-sum.
2. **Assign each CLIP an integer duration [4,15]** = its running-total, rounded, clamped; nudge so per-clip integers sum to `totalDurationSeconds`. Never fractional.
3. **No sub-4 s clip:** merge a trailing <4 s clip into the previous (kept ≤15 s).
4. **A single shot >15 s is malformed**: surface to the user (or ask them to split in the visor); never truncate.
   > ✅ **VERIFY A:** Σ clip durations == `totalDurationSeconds`; every shot appears once, in order, contiguous.

### Step B: pack CLIPS into SHEETS (≤12 panels each, IMAGE/cost grouping)
1. **Panels per clip** = number of shots in the clip (one panel per shot, always).
2. **Greedily fill sheets in clip order:** add the next clip while the sheet's running panel total ≤12, else open a new sheet. **NEVER split a clip across sheets.**
3. **Oversized clip** (own shots >12 panels): it has too many shots for one sheet — split it at a natural cut into two clips (never drop shots, never merge). With one panel per shot, a clip simply cannot exceed 12 shots.
4. **Prefer full sheets** (fewer calls = less cost); leftover positions render as bare board, not empty cards.
   > ✅ **VERIFY B:** every sheet ≤12 panels; no clip split; Σ panels over all sheets == Σ per-shot allocations (Step 3).

**State the split out loud** (chat/`print`): "34 s → 3 clips (12,11,11 s) → 2 sheets: SHEET1=clips1–2 (panels1–9), SHEET2=clip3 (panels10–12)."

**Numbering (no banner on the sheet):** nothing drawn as banner/header/PART tag (image = full-bleed grid only); PART index lives in `metadata` (`storyboardPart`/`storyboardParts`), `summary`, filename. Panel numbers are 1-based per sheet, exist ONLY in prompt text + metadata, NEVER rendered (the viewer overlays its own; baked-in numerals clash).

**One prompt PER sheet.** When >1 sheet: section A title carries THIS sheet's PART tag; section F lists ONLY this sheet's panels (may span several clips); B/C/D/E/G/H stay essentially identical across sheets (same style/characters/grid) for continuity.

**🧷 Every sheet's `metadata` MUST carry the `clips` map** (else `keyframes-to-video` falls back to "1 sheet = 1 clip" and drops scenes):
```
clips: [
  { clipIndex: 1, shotIds: ["sh1","sh2","sh3"], panels: [1,2,3,4], durationSec: 12 },
  { clipIndex: 2, shotIds: ["sh4","sh5"],        panels: [5,6,7],   durationSec: 11 }
]
```
`clipIndex` = **global** sequential across the whole storyboard (timeline order); `panels` = this clip's 1-based panel numbers ON THIS SHEET (one panel per shot, in order); `durationSec` = integer duration; `shotIds` = its JSON ids. Also stamp `metadata.sourceStoryboard` (JSON path), `storyboardPart: K`, `storyboardParts: K_total`.

### 🔁 Cross-sheet referencing: Sheet K ≥ 2 MUST receive every prior sheet (MANDATORY)
> 🛑🛑 **STRICTLY SEQUENTIAL: NEVER generate sheets in PARALLEL (#1 multi-sheet rule).** Render one at a time: sheet1 → **WAIT** → `show_result` → sheet2 with sheet1 in `referenceImages` → wait → sheet3 with sheets1-2 … Firing several at once (parallel block OR back-to-back without awaiting) is a HARD BUG: sheet K≥2 can't reference K-1 if it doesn't exist yet → renders BLIND → the same actor gets a different face/hair/wardrobe per sheet. No "parallel to save time" mode. Exactly ONE `generate_image` in flight at any moment. (Single-sheet = the K=1 case.)

**For every sheet K≥2, `referenceImages` MUST include, in order:** 1) every prior approved sheet, aliased `sheet_part_1 … sheet_part_{K-1}`; 2) then the user subject refs (same as sheet 1). Aliases are SDK names: in the body anchor by position (`Image 1`…) per Step 2.

**Continuity block (K≥2)**: weave in right after the per-shot breakdown, before the style block (paste template):
> *"`Image 1` (and `Image 2` … `Image {K-1}` when present) are the previously-approved PART sheet(s) of this same storyboard. Preserve EXACTLY: every character's face/build/hair/wardrobe, every recurring object's design, the setting, lighting direction, palette, render style, and the sheet FORMAT (clean full-bleed grid, thin black gutter lines, NO text or numerals). No banner, cards, captions, numbers, footer. Only the panels in section F change. Treat the PART sheet(s) as the authoritative visual locker for everything that is NOT the new shots."*

Both halves required: prior sheet without the block → model riffs on style; block without the picture → nothing to copy. **Refinements on an approved sheet:** re-render sheet K with the SAME `referenceImages` + continuity block; don't regenerate prior sheets unless asked.

---

## Step 4: Compose the storyboard image prompt

Write as a **single continuous block of FLOWING NATURAL-LANGUAGE PROSE**: a creative director's brief. K>1 sheets → do this K times.

> 🛑 **Write a brief, not a form (#1 drift).** Models parse prose far better; form-shaped prompts make the model render form chrome. ❌ NO decorative banners (`═══`), `KEY: value` lines, ALL-CAPS headers, bullet lists in the body. ✅ A–H below are a COVERAGE CHECKLIST, not literal headers: weave into prose. Gold standard = one flowing paragraph (format sentence → style → story → "Panel 1, wide establishing shot…"), NOT `═══`/`FORMAT: 7 frames`/`CHARACTERS`/bulleted `Panel 1:`.

### Required sections, in order

**A) Title & Format Header.** Open with duration, title, panel count, grid layout, style genre.
- **🔗 ONE CONSISTENT WORLD, state it and mean it.** All panels = DIFFERENT CAMERA ANGLES/MOMENTS OF THE SAME UNCHANGING SET, not separate scenes (#1 complaint = drift cell to cell). Declare the world shared and locked, naming the ACTUAL recurring objects: every recurring element (furniture, props, colours, materials, sizes, relative positions) is IDENTICAL in every panel it appears; the set does NOT change, only camera framing + actions do. AND anchor in-canvas by pointing later panels back at Panel 1 + the plate ("the corridor in panels 2-11 is EXACTLY the corridor of Panel 1: same architecture, matched to `Image N`"). A later panel saying only "the corridor" is where the set re-rolls. (Pairs with C2 + per-shot `continuity`.)
- **🛑 Panel count = EXACTLY the number of PANELS on this sheet: that number everywhere, never the grid's cell count.** (One panel per shot, so panels == this sheet's shot count.) Non-round counts (7,10,11) normal. Bug: FORMAT line "7 frames" but layout line "12 panels in a 3×4 grid" → model fills all 12 and invents 8–12. Rules: **one number everywhere** (FORMAT header, opener, section E all agree). **🚫 Leftover cells NOT drawn: bare black, nothing on them** (no image/number/border/placeholder); state positively ("exactly 10 panels; the remaining 2 grid positions are bare black background, render NO image, number, frame or border"). Panels fill left-to-right, top-to-bottom; a partial last row → rest bare black. **Black cells keep the SAME cell size**: grid geometry NEVER stretches/shrinks/collapses; a partly/fully black row is still full-height (else uneven rows break the look + virtual-panel cell math).
- **The grid is YOUR choice: pick per sheet, declare ONCE.** Any uniform cols×rows holding the count (12 max). Hard requirements: (1) ONE uniform grid: straight continuous pure-black gutters, every row same height, every column same width (auto-detection locks onto this); (2) leftover cells bare black at the same size; (3) SAME grid named consistently everywhere; (4) stamp `metadata.grid`.
- 🚫 Duration/title/PART named here is PROMPT FRAMING ONLY: NOT drawn anywhere (no title banner/header strip/caption). Orientation: let the sheet follow the video (16:9→landscape; 9:16→PORTRAIT sheet with vertical cells) so panels are natively framed; avoid vertical-video panels in landscape cells when a portrait sheet is available.

**B) Style Declaration.** A rich style block tailored to the user's style: NOT a fixed line, it adapts. Read `STYLE_PRESETS.md`, paste the matching block; custom → its custom-style flow (1–2 sentences → descriptive aesthetic phrasing → confirm). Adapt to family: **3D** (family-film studio quality, cinematic rendering, expressive animation, warm lighting); **Live-action** (cinematographic, film-stock look, practical lighting, grounded realism); **Anime** (studio quality, Ghibli/Trigger/MAPPA tone per story, cel-shading, dynamic line work); **2D** (hand-drawn, palette approach, line weight, shading model); **Stop-motion/claymation** (handcrafted clay/puppet, visible material texture, miniature sets); **any other** (editorial/comic/watercolor/cyberpunk, read like a director's brief for that aesthetic). **Never use copyrighted studio/franchise names** (Pixar, Disney, Ghibli, Aardman, Wallace and Gromit): they trigger moderation/copyright filters; rewrite as descriptive aesthetic phrasing (`STYLE_PRESETS.md` does this for presets; mirror for custom).

**C) Character / Product Descriptions.** Flowing prose (not a list): each main character AND each product/object ref: physical features, clothing, accessories, distinguishing elements. **Anchor every subject to ALL its image positions** (per Step 2 mapping): single ref → "Match `HERO_A` exactly to `Image 1`: <features>"; multi ref of the SAME subject (most common) → "Match `HERO_A` to `Image 1,2,3,4`: four photos of the same character; use all jointly to lock face/hair/build/wardrobe; do not invent features absent from the references" (every position MUST be listed, naming only Image 1 after collecting 4 = the bug); product → "Match `PRODUCT_BOTTLE` to `Image 5`: <silhouette,material,label>". Without explicit `Image N` anchors the model drifts to generic priors.
- **⚠️ References lock IDENTITY, never POSE/ORIENTATION.** The model copies HOW the subject sits in its ref (upright, blade up, label facing camera) unless overridden. When a panel shows a DIFFERENT orientation/pose (upside down, lying flat, mid-fall, from behind, folded, broken), that panel MUST declare it in frame-geometric terms naming the override. Else the ref's canonical orientation wins.

**C2) Setting / Location: anchor the environment exactly like characters (#1 cause of cross-panel drift).** Characters stay consistent because C anchors them to `Image N`; the SET, unanchored, gets re-invented per cell. The set MUST get the SAME forceful `Image N` anchoring.
- A ref of a LOCATION/SET/room is a SETTING plate; give it a per-location id (`SET_SALON`), put in `referenceImages`, anchor by position.
- **Anchor forcefully:** reproduce the plate's EXACT layout in every panel set there: same furniture in same positions, same props with SAME count/placement, same wall/window/door layout, materials, colours; between panels ONLY camera framing + actions change (never move/add/remove/restyle/recolour); a panel showing only part of the room must still match the plate. Locks the set across the sheet AND across PART sheets (the plate rides in every call's `referenceImages`).
- **Tie to the continuity table:** per-shot `continuity.objects` = WHICH objects are in-frame + their STATE; the plate = what they LOOK like and WHERE they sit. **One plate per recurring location.**
- **🛑 MANDATORY: no plate but a location recurs in 3+ panels → GENERATE the establishing plate FIRST, always.** Render ONE plate (wide, well-lit, full space with every recurring architectural element + prop in canonical position, in the chosen style), anchor every panel there via `Image N`. Prose alone can't lock a set. Save as a `locations` Library asset for reuse in later edits/single-panel fixes.
- 🛑 **NEVER re-describe the set's props with fresh adjectives in section F: POINT BACK to the plate** ("the SAME coffee table from `Image N`, props in the SAME positions"). A fresh adjective list is a NEW brief → the model invents a different one. Spell out fresh detail ONLY for what genuinely changed this frame (new object, moved prop, state change per `continuity.objects`).

**D) Visual Tone.** Colour grading, atmosphere, lighting quality, rendering approach, consistent with B but focused on mood + technical rendering.

**E) Storyboard Layout Details: describe the clean full-bleed grid IN PROSE** (no template image attached). The sheet is a clean full-bleed contact-sheet grid:
- Each panel FILLS its cell edge-to-edge (full bleed); the grid covers the WHOLE page to all four margins.
- Panels separated ONLY by **solid PURE-BLACK gutter bars (#000000), clearly THICK (~0.5% of sheet width, ~15-20px at 4K)**, functional: the app segments by finding these bars; thin/grayish gutters become indistinguishable from dark lines inside panels. State "solid pure black gutter bars, noticeably thick, never gray, never thin hairlines".
- **UNIFORM GRID: say it explicitly:** all cells IDENTICAL size; every row same height, every column same width; gutters straight, parallel, continuous. Leftover bare-black cells keep the same size; a partial/empty row is never taller/shorter/merged.
- **NO numbers on panels**: no numerals/letters/labels of any kind (viewer overlays its own; baked-in per-sheet numbers clash). State "render NO numbers, letters or labels inside any panel".
- **NOTHING else drawn:** no title banner, PART/header strip, floating cards, rounded corners, drop shadows, caption bars, timecodes, shot-type labels, **no footer, no legend/icon row, no thematic-symbol icons with labels (e.g. "Temptation/Power/Escape/Observation"), no Project/Format/Pacing/Channel-Notes strip, no metadata row/column**. Only panel images + thin black separators. The grid's bottom edge IS the image's bottom edge: NOTHING below the last row.
- Weave as one line (perfectly equal cells, straight continuous thin black gutters edge to edge, images full-bleed, NO numbers/letters/labels, empty positions bare black at the same cell size, no cards/shadows/captions/banner/footer, grid covers the entire page).
- ⚠️ If you restate count/grid here it MUST equal section A's (leftover positions = bare board, never "empty cells/cards"). **One number, everywhere.**

**F) Scene Breakdown.** Each panel: "Panel [N]: [Shot type] shot. [scene description with character action, environment, emotional beat]." **With a JSON input this is FAITHFUL TRANSCRIPTION** (Step 3 HARD STOP): Panel N = JSON shot N in order; description IS the shot's `action`, type = `shot`, environment = `scene.title`/`location`. Re-read the JSON for THIS PART's exact range.

**📸 EACH PANEL GETS A SUPER-DESCRIPTION: a forensic, self-contained photograph in words: the bar is IMPOSSIBLE TO GET WRONG.** You hold ALL sources (`action`, `shot.continuity` {characters,objects,place}, the `continuity` LOCK, `synopsis`, roster, plates). Describe as a FORENSIC INVENTORY:
- every visible object NAMED with state, position in frame, size vs a named neighbour;
- the subject dissected: each hand and what it does, gaze direction, mouth/expression, posture, weight, which foot forward;
- spatial layout: foreground/midground/background, frame left/right, camera height/distance, what the lens is at eye level with;
- orientation of every directional object (points up/down) with its negative;
- light: every source in frame, its colour, what it lights, where shadows fall;
- the explicit ABSENCES and proportions (below).

**Acceptance test: could two painters, given ONLY your text, paint two DIFFERENT images? If yes, tighten until only ONE is possible.** A 200-word panel that passes beats a 60-word gist; anything load-bearing unsaid, the model fills from its (usually wrong) prior. Contracts:
- **🫙 ONE FROZEN INSTANT: a panel is a photograph, not a clip.** When `action` narrates several sequential moments, do NOT transcribe the whole chain: the model renders them SIMULTANEOUSLY. Pick the single most readable instant (usually the decisive one), describe ONLY that, encode other beats as visible STATE: what already happened = evidence in frame, what hasn't = explicitly "not yet". One shot is still ONE panel — never split it into multiple keyframes; if a beat genuinely needs to be its own frame, that is an authoring decision in the storyboard (a separate shot), not a render-time expansion here.
- **🧭 FRAME GEOMETRY: state orientation and prominence, never physics.** "Falls tip-first" is physics (not simulated). Say what the FRAME shows geometrically, with the negative (what points up/down, what is NOT). Same for size: if a key subject must read, state prominence explicitly ("large in the foreground") even in a wide, else a small object in a big room renders tiny.
- **🚫 EXPLICIT ABSENCES: closed-world rule (presence is default; absence must be DECLARED).** Track every TRANSIENT element (falling sword, sparks, a character who leaves, a consumed prop) panel by panel: IN vs GONE. In EVERY panel where a transient is absent but appeared nearby, NEGATE it explicitly (name it as NO-longer-present). The sheet is ONE canvas: the model sees the element in neighbours and paints it into any panel that doesn't forbid it.
- **🔒 SCOPE the global locks: an always-true motif gets painted everywhere.** When the `continuity` LOCK describes a recurring EVENT, phrase it CONDITIONAL and scoped, naming the exact panels it applies to when the list is short ("WHENEVER the sword appears (panels 1 and 4 only) …"). Invariant STATE locks (burn mark, intact ceiling, hole alignment) stay global; EVENT motifs get scoped to their panels.
- **📏 RELATIVE PROPORTIONS: state size RELATIONSHIPS, never bare adjectives.** No physics/scale: "a small hole" means small vs the FRAME, not vs the object that made it. When two story-critical objects interact (hole + the blade that melted it, step-object + who stands on it, prop + the hand holding it), write the scale relationship anchored to a named object, with the negative (e.g. "barely wider than the blade, NEVER wider than the hilt").
- **🔦 SMALL-BUT-CRITICAL PROPS: redundancy beats one mention.** When a critical prop renders SMALL, one state word gets lost and the model defaults to neighbours. State it THREE ways: the state itself, its visible EFFECT on the scene, and the negative of the wrong state; if it's the narrative point, add prominence.

**🧩 FIRST classify panels into CONTINUITY RUNS from STRUCTURED JSON fields, BEFORE writing any panel** (the skipped step; root of the consistency bug). Read these signals (NOT prose keyword-matching): **`noCutBefore:true`** = glued to previous, no cut; **several shots sharing the SAME `number`** = one authored shot split into glued sub-shots, one continuous take; **storyboard-level `synopsis`/`continuity` describing one unbroken take** (plano secuencia/one-er/"sin cortes", read for MEANING); **`movement` progressing while the subject stays put** (Dolly in→Dolly in→Static = camera moving through ONE space, not three setups).

**When the signals say a run is ONE continuous take, it's a SINGLE delta chain:** panel 1 establishes, panels 2…N each "IDENTICAL to the previous except the camera moved to X". No cut → nothing in the world/pose may re-roll (body, wardrobe, sofa, bottles, table, TV content PERSIST; only framing advances). Treating each glued sub-shot as an independent setup = the reported drift.

**🔗 DESCRIBE EACH PANEL BY ITS DELTA FROM THE PREVIOUS ONE (most reliable consistency lock), for ANY run sharing the same moment.** Trigger is broad: apply whenever consecutive panels show the SAME character in the SAME ongoing physical situation (same location/beat, pose unchanged in-story), covering BOTH the SAME continuous shot (keyframes, `noCutBefore`, shared number) AND **different shots across a hard cut still in the same held moment from a tighter/different angle** (medium → medium-CU → CU of the same reclined man, SEPARATE JSON shots, so the agent re-describes the pose and drifts: Panel 3 legs extended, Panel 4 silently sits him up, Panel 5 changes the hands). Anchor each panel to the one before, describe ONLY the change:
- Assert sameness THEN the single delta ("Panel 4: IDENTICAL to Panel 3, same room, pose, wardrobe, lighting. The ONLY change: the camera dollied closer, framing him waist-to-torso. Do NOT change his pose or sit him up.").
- Works because the whole sheet is ONE generation: the model SEES Panel 3 on the same canvas, so "identical to Panel 3 except…" is a satisfiable constraint.
- **One delta per step** (camera moves, OR he raises the bowl, OR he turns his head). Everything NOT named as the delta is unchanged, including body POSE, torso angle, limb position, not just objects/setting. Strongest form of carry-forward; use for EVERY shared-moment run.

Distribute character details across panels: hair/face in close-ups, full outfit in wides, signature accessories when visible; **don't front-load all description into Panel 1.** Weave dialogue/action notes naturally.

**🔬 PHYSICAL-DETAIL FIDELITY: describe how the action ACTUALLY happens, not a vague gist** (the model renders literally and fills gaps with plausible-but-WRONG detail). For action panels (esp. hand/object close-ups):
- **Singular, not vague plural.** "inserts coins" → the model fans 2–3 coins at once → write "inserts a single coin, held between thumb and forefinger"; say "two coins" only if two are genuinely visible.
- **Name the grip/contact/which finger.** "presses the button" → which finger, what posture; "reaches high on tiptoes to press the LOW button" is self-contradictory → "crouches slightly and presses the low button with his index finger".
- **Zero ambiguity: every target a concrete identifier.** "presses his floor's button" → "presses button 2 (of 16)"; "grabs his suitcase" → "grabs the red suitcase on his left". Numbers/colours/positions: nothing doubly-interpretable survives.
- **One physical step per panel** (insert-coin and press-button as separate beats → each panel one action).
- **🎬 CONTINUITY (raccord): carry the established state into EVERY panel, or the render drops it (#1 neglected thing).** Once a panel sets a non-default state (standing ON stacked cans, holding the can, a hole melted, a door opened), every later panel where it still holds MUST restate it, even a hand close-up (the model snaps to default unless restated). Bug: panels 13-14 "on top of the two cans", panel 15 only "presses the Pepsi button" → rendered back on the ground; panel 15 MUST read "standing on the two stacked cans, presses the Pepsi button". State persists in the TEXT until a panel explicitly changes it. (Plus basics: same object/hand position, lighting, screen direction across cuts.)
  - **⚠️ The source `action` may be USER-WRITTEN and incomplete** (they forgot to restate the state in a later shot). DO NOT inherit the omission: read the WHOLE shot range, track world/character state yourself, RESTATE the carried-forward state in every panel where it logically still holds even if that panel's `action` dropped it. This OVERRIDES faithful-transcription's "copy verbatim" for continuity: never add a new EVENT, but DO re-inject the state the source forgot.
  - **When the shot carries `continuity` ({characters,objects}), that work is done**: render both columns as ground truth for free; only track state yourself when it's absent (legacy free-text `state`, same treatment). If a panel's `continuity` contradicts its neighbours (crushed in one, intact-and-stood-on in the next), the SOURCE is self-contradictory: render the physically coherent reading the `synopsis`/`continuity` LOCK imply and flag it, don't reproduce the impossible.
This is NOT inventing events (Step 3 holds): the WHAT stays the JSON's action; you specify the HOW with real-world-correct, unambiguous mechanics.

**G) Art-direction & quality cues: PROSE ONLY, NEVER drawn.** Woven into prose: facial-expression quality, camera-angle variety, texture detail, environmental detail, atmospheric effects, composition principles; tailor to style. ⚠️ These describe IMAGE QUALITY *inside* the panels, never a caption/label/footer, never a strip/box/column/legend/icon row. **Per-type:** when a video type is named, pull its brief-context, caption style, shot mix, audio cue from `VIDEO_TYPE_<TYPE>.md` (read it, don't paraphrase); that per-type brief context shapes the panels but is NEVER drawn.

**H) Render quality & format: PROSE ONLY, NEVER drawn.** Final specs woven in: render-quality cues, aspect ratio, format declaration ("professional panel sheet"), quality tier ("masterpiece quality"/"production-ready"). Tell the model HOW to render; never a banner/label/footer.

### Prompt length targets
Longer than single-image prompts (they encode layout + a forensic super-description per panel). **Budget goes to the panel breakdown: 150–250 words PER PANEL for action panels** (simple inserts less, never below what the two-painters test demands); style/layout/quality boilerplate stays tight.
- 9 panels: 1,400–2,200 words · 12: 1,800–2,800 · 15: 2,200–3,400 · 20: 2,800–4,200.
Never compress per-panel descriptions to hit a length, trim style/quality prose first, panels last. Every panel needs enough detail to fully determine its frame and differentiate it from neighbours.

---

## Step 5: Generate the sheet(s) (`generate_image`)

Call `generate_image` per prompt. **Don't show the raw prompt as the deliverable.** K>1 sheets = K separate calls, in strict sequence per "🔁 Cross-sheet referencing" above (render PART K, WAIT, `show_result`, ONLY THEN K+1, carrying PARTs 1…K in `referenceImages`; B/C/D/E/G/H stay identical). `show_result` after each PART lets the user review early.

Required call shape (per sheet):
- **`label`**: `"visual_storyboard"`. MANDATORY. The router ranks any catalog model carrying this label first (the model curated for dense multi-panel sheets, e.g. GPT Image 2) and picks it; without the label the call falls to the generic image bucket and the sheet comes back at thumbnail quality.
- **`prompt`**, the full composed block from Step 4 for THIS PART (long-form intentional).
- **`referenceImages`**: EVERY user ref, no exceptions, no subject-level dedup. Absolute paths or `@handles`, in the exact Step 2 order (hero + ALL photos → secondary chars + ALL photos → products → locations). Array position IS `Image N`. Identical across PARTs. **PART1/single:** `[ …every user ref (Step 2 order)… ]` (no template entry: the clean-grid format is described IN PROSE, section E). **PART K≥2:** `[ sheet_part_1 … sheet_part_{K-1}, …every user ref… ]`.
  - **Pre-flight count check (every time):** count user-attached refs (JSON root + every scene + every shot, deduped, `@handles` resolved) + form picker uploads. `referenceImages.length` MUST equal: PART1/single = exactly that user count (no extras); PART K≥2 = user count + (K-1). If SHORT, you collapsed several photos of one subject OR dropped a prior sheet: redo.
- **`aspectRatio`**: the SHEET aspect matching your grid (a neutral reading surface — NOT a video format; aspect is chosen per video later).
- **`resolution`**: `4k`. MANDATORY (≈3312×2480 px or portrait twin). At 1080p panels compress to mush.
- **`saveTo`**: a locatable dir (`~/.koi/images/` default; the project folder when active).
- **`summary`**: single: "`<title>`: keyframe sheet, `<duration>`s, `<panel-count>` panels, `<aspect>`"; multi-PART: "`<title>`: PART K / K_total, `<duration>`s, `<panel-count>` panels".
- **`metadata`**: with a JSON input, stamp the clips metadata per Chunking Step B above (`sourceStoryboard`, `storyboardPart`/`storyboardParts`, `clips`). `keyframes-to-video` uses these to re-attach the JSON and resolve each clip's duration. Omit only with no source JSON.

After each success, `show_result` with the saved path (per PART, not just at the end).

---

## Step 6: Companion note
After the image lands, a short (3–5 sentence) note: style choices made for anything unspecified; which character details came from uploaded refs vs inferred; one or two refinement suggestions (e.g. "if panels blend together, I can re-render with stronger black borders"); handoff: "When you're happy with this sheet, I can render the final video (per-clip prompts + clips + assembled timeline) via `keyframes-to-video`."

---

## Handling variations
- **Full beat sheet provided:** skip Step 3, map beats directly to panels; adjust count to their beat count.
- **Only a logline:** decompose into a full beat sheet (three-act) first; briefly show the breakdown so the user can redirect.
- **Iterate on specific panels:** re-call with the same references and a revised prompt adjusting only the affected panels; keep the rest unchanged.
- **Different panel count:** redistribute beats across more/fewer sheets (12 max) and pick any uniform grid. Fewer = more weight each; more = transitional/reaction shots across added PART sheets.
- The sheet grid is a reading surface, not a format commitment: pick a tidy uniform grid (landscape cells are fine and default). The video's aspect ratio is asked from the user AT VIDEO GENERATION and the model reframes — do NOT pre-shape the sheet to a target platform.
- **Mixed/hybrid style:** build section B to call out the hybrid ("anime-influenced but rendered in 3D", "live-action with animated elements") and which elements follow which rules.
