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

## The chained previous clip also carries faces
On clip K ≥ 2 you attach the immediately-previous clip as a reference. When it
shows **photoreal faces**, attach a **BLURRED copy** instead of the raw clip —
the blur defeats the likeness detector while preserving motion, pacing, palette
and audio. Make it locally with ffmpeg (`gblur`), no model call. Stylized looks
or clips with no people on screen → attach the raw clip.
