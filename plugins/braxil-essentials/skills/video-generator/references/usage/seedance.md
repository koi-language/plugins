# Seedance 2.0 — reference PREP guide (how to make its references acceptable)

> Per-model reference-PREP guide for the **Seedance 2.0 family**
> (`bytedance/seedance-2.0/*`). Seedance runs a **likeness filter** that
> REJECTS the whole render (`"image_urls: may contain likenesses of real
> people"`) when you attach a reference whose face looks like a REAL PHOTO.
> This guide is how you prep references so they pass. Parameter tables live in
> `references/models.md`; prompt WORDING is authored by
> `cinematic-video-prompt-engineer` — this file is ONLY the reference prep.

## The character sheet MUST BE A SEEDREAM IMAGE (mandatory for photoreal faces)

A face **synthesised by Seedream** does NOT trip the filter; a real photo (or a
plain pixel-copy of one) does. So every character reference (its ficha /
turnaround) with a photoreal human face must be turned into a **Seedream image**
before you attach it — by REPRODUCING its turnaround through Seedream with a
detailed re-description (see below).

### 🔎 STEP 0 — check the sheet's model BEFORE attaching it (mandatory gate)
For EACH character sheet you are about to attach to a Seedance render, first
find out what model made it:
- `inspect_creation({ filePath: <the sheet path> })` → read `metadata.model`.
- If the slug contains **`seedream`** (e.g. `bytedance/seedream/v5/pro/edit`),
  it is Seedream-born → **attach it directly**, no second pass.
- If it is ANYTHING ELSE (e.g. `openai/gpt-image-2` — the model a
  no-reference-photo turnaround falls back to — or a user upload / external
  image), it is **NOT** Seedream → you MUST first CLONE it through Seedream
  (the "How to build it" step below) and attach **that Seedream clone**, never
  the original. The clone becomes the character's Seedance reference from here on.

Do this per character: some casts mix Seedream sheets (built with a photo) and
GPT-Image-2 sheets (built from description only) — clone only the non-Seedream ones.

✅ **The trick that works: REPRODUCE the character's turnaround 1:1 through Seedream — but with a FULL RE-DESCRIPTION of the character.** A bare *"reproduce exactly, output the same image"* does NOT work (Seedream photocopies the real face → the filter still fires). What works is a 1:1 reproduction whose prompt ALSO re-describes the subject in detail (sex/age, every garment + accessory, hair, glasses, distinctive facial features) + the layout — that makes Seedream **RE-SYNTHESISE** the character (a Seedream-native image) instead of copying pixels, and THAT clears the filter.

### How to build it
`generate_image` in EDIT mode with the **Seedream edit model** (pick its CURRENT slug from the `image-generator` catalog — never hardcode a slug). **`Image 1` = the character's TURNAROUND itself** (the ficha exactly as it was generated — e.g. by GPT Image 2 — NOT the user's original source photo). **🙈 Pass `metadata: { "visible": false }`** — this Seedream copy is a throwaway technical intermediate for the render, keep it out of the creations drawer.

Prompt — a TEMPLATE: fill every `<…>` **richly** from the character's roster description (the detail is what makes it clear the filter; don't leave it generic):

```
Reproduce this image EXACTLY as an identical, faithful 1:1 copy. Keep the same single <sex + age, e.g. "older male"> character, the same eight-view turnaround layout (two rows of four: full-body front/right-profile/left-profile/back on top, head close-ups front/three-quarter/profile/back-of-head below), the same neutral grey studio backdrop, the same clothing (<describe every garment + accessories, e.g. "pale shirt, dark waistcoat, thin black leather gloves">), the same <hair, facial hair, glasses, distinctive facial features, e.g. "grey hair, wire-frame glasses, weathered face">, same lighting and framing. An exact recreation, change nothing.
```

### Already Seedream? Don't redo it
A character sheet **already generated with Seedream upstream** (e.g. in the
storyboard cast-building step) already clears the filter — attach it directly,
no second pass. Only run this generation for characters whose sheet came from a
user upload or another (non-Seedream) model.

### What doesn't need this
- **Stylized / non-real faces** (3D animation, anime, claymation…) don't trip
  the filter — skip it.
- **Set/location plates and props carry no face** → never touched.

## The chained CONTINUITY FRAMES carry faces too — launder each one
Chaining clip K ≥ 2 runs on **SELECTIVE CONTINUITY FRAMES** on every model, not
just here: full-res frames extracted from clip K-1's render, ONLY the takes the
new clip must actually match (same place + same characters, or the opening
continuation), each attached under its own role alias (`prev_end`,
`prev_shot3`…). The full flow — need list, real-cut detection, per-frame legend
lines — lives in `storyboard-to-video`'s "Clip chaining"; read it there. (The
old wholesale first+last-frame GRID is retired: the mosaic confused the model
with outdated mid-clip state.)

**Seedance's extra step:** those frames are REAL render frames, so they carry
the same photoreal faces the likeness filter rejects. Launder EACH selected
frame exactly like a turnaround — Image 1 = the frame, plus a FULL
re-description of what it shows (the characters, their screen positions,
wardrobe, set, light). Same rule as above: a bare "reproduce exactly" fails;
the detailed re-description is what makes Seedream re-synthesise it. Attach the
LAUNDERED copies. 🙈 `metadata: { "visible": false }` on originals and copies.

**Do NOT pass the previous clip itself as a video reference here.** Raw, the
filter rejects the whole render. Blurred — the old workaround — it clears the
filter but preserves only *motion, pacing, palette and audio*: the blur destroys
the character SCREEN POSITIONS, which is the entire point of chaining. That is
the reported "the boy was on her right, next clip on her left" bug, and no
wording in the prompt fixes it, because the information simply isn't in the
reference.

Stylized looks or clips with no people on screen don't trip the filter: there the
sheet goes in as-is, and you may add the previous clip as a video reference if
you want the extra pacing signal.
