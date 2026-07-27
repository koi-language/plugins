# Gemini Omni Flash — usage guide (video)

> Per-model USAGE guide (how to get good results out of this model: prompting
> technique, workflows, do/don't). Parameter tables live in
> `references/models.md` — do not duplicate them here. You call the model
> through BRAXIL's `generate_video` tool; there is NO Python/SDK to run.

Gemini Omni Flash is a fast & cheap model for **first-frame-to-video**,
**reference-guided video**, and **plain-language video editing**. It renders
**on-screen text unusually well** and generates its own **audio track** by
default.

## When to reach for it

- **Video editing** (`google/gemini-omni-flash/edit`) — the default, best
  instruction editor. Give a plain-language instruction and it keeps
  everything else in the frame the same: "make it night", "remove the logo",
  "add a cat that jumps onto his lap". Output dims/length follow the source.
- **First-frame-to-video** (`google/gemini-omni-flash/image-to-video`) —
  animate from a single `startFrame` image.
- **Reference-guided** (`google/gemini-omni-flash/reference-to-video`) —
  compose from up to 10 `referenceImages` (style / character / object refs).
- Reach for a cinematic model (Veo, Kling, Seedance, Luma) instead when you
  need higher fidelity, `seed`, `resolution` control, or 4K.

> ⚠ **Regional restriction**: video-to-video edits are unavailable in the EEA,
> Switzerland, the UK and some US states. A v2v edit that returns quickly with
> an empty/blank output is almost always this restriction, not a prompt bug.

## Model limits (see `references/models.md` for the exact tables)

- `aspectRatio`: **`16:9` or `9:16` only** (clamped to the nearest
  orientation). Edits follow the source aspect.
- `duration`: any integer **3–10 s** (clamped). No `seed`, no `resolution`.
- References: up to **10** images on the reference-to-video slug.

## Prompting

Simple, direct prompts win — especially for edits. Overly descriptive prompts
cause unintended changes.

### Single scene / continuous shot

By default Gemini Omni Flash invents a small multi-shot narrative. To force a
single unbroken scene, say so explicitly:

- "In a single unbroken scene" / "In a single continuous shot" / "No scene cuts"

Example:

```none
Continuous, unbroken handheld shot of a fluffy tabby cat sitting on a sunny
windowsill, looking out into a leafy garden. The cat's tail twitches slowly,
and its ears rotate slightly toward ambient noises. Sunbeams illuminate dust
motes in the air. Sound design: gentle breeze, distant bird chirps, quiet
mechanical purring. No dialogue.
```

### Editing

Keep edit instructions short. When touching one aspect, add "Keep everything
else the same":

- "Make this video anime"
- "Make the phone invisible"
- "Put a fashionable hat on this person"
- "Change the lighting to be more dramatic"
- `Change the text on the sign to say "Braxil"`
- "Add a cat that jumps onto his lap, he begins to pet it"

### Removing unwanted elements

Add plain negatives: "No dialogue", "No embellishments", "No extra sound
effects".

### Timing / when things happen

Natural language or a timecode syntax both work — great for making your own
cuts, rhythm, or rapid-fire sequences:

- "after 3 seconds, a woman enters the scene"
- "every 2s cut to a new frame"
- "in a rapid fire sequence, every half a second (12 frames at 24fps) change the scene to a new location"

```none
[0-3s] A person is walking
[3-6s] They stop and turn around
[6-10s] They start running
```

### Text in videos works really well

Unlike previous video models, Gemini Omni Flash renders substantial, readable
on-screen text correctly. If text appears naturally (signs, labels, UI),
define exactly what it says:

- One word on the screen at a time: "did, you, know, that, Omni, can, do, awesome, text?" — each word appears for 1s with a different animated style. No dialogue.
- There is a street sign that says: "This is an AI generation by Omni", a storefront that says: "All you need AI", a car with the number plate "OMN111".

### Meta prompting

You can hand the model attention-steering instructions verbatim:

- "Consider micro-detail, expression and timing to create a very rich, detailed but entirely natural scene."
- "Be extremely detailed in your descriptions of characters and environments. Apply costume design principles to characters."
- "Include plenty of appropriate detail in the background elements to make the scene feel realistic and natural."

## Reference images and image-role tags

On `reference-to-video` (and when an image should act as first frame vs.
reference) you make each image's role explicit with tags **inside the prompt**
— the tool binds `referenceImages` positionally, so YOU write the tags.

### Simple tags (recommended)

- **`<FIRST_FRAME>`** — use the image as the starting frame: `<FIRST_FRAME> a woman is walking`.
- **`<IMAGE_REF_N>`** — use the image as a reference (indexing starts at 0): `in the style of <IMAGE_REF_0> a woman <IMAGE_REF_1> is walking`.

Example with 6 reference images:

```none
[0-3s] A studio fashion sequence. Starting with woman <IMAGE_REF_0>, she is holding <IMAGE_REF_1>
[3-6s] Then we see the man <IMAGE_REF_2> holding <IMAGE_REF_3>
[6-10s] And finally another woman <IMAGE_REF_4> who is holding <IMAGE_REF_5> while walking.
```

### Explicit source/reference declarations

For complex multi-image cases, declare roles with prefix tags plus a natural
instruction suffix:

- `[# Sources <FIRST_FRAME>@Image1]` — first image is the starting frame.
- `[# References <IMAGE_REF_0>@Image1]` — first image is a reference.
- `[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2]` — both are references.
- `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]` — first is the start frame, second is a reference.

Then guide with a suffix: "Use the given image as the starting frame." or
"Use the given image(s) as references for video generation. The images should
not be used as literal initial frames."

Example:

```none
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] a woman <IMAGE_REF_0> is walking. Use Image1 as the starting frame. Use Image2 as a reference for the video generation.
```

## Audio

Gemini Omni Flash generates an audio track by default. Steer it in the prompt,
which matters most when you want music:

- "Include calm background music"
- "The video has a high energy techno beat"
- "The audio is a low tinny radio broadcast in the background, playing a song"
- "Audio design: [a description of the audio you want]"

**Editing a clip that has audio**: by default the existing audio layer is
preserved (and may be adapted). To get a brand-new audio layer tailored to the
new visuals, the source must reach the model without an audio stream — if any
audio is present the model preserves/modifies it instead of starting fresh.

## Gotchas

- v2v edit returns quickly with empty output → regional restriction (EEA / CH /
  UK / some US states), not the prompt.
- Long/overwrought edit prompts drift; keep them terse and add "Keep everything
  else the same".
- No `seed`/`resolution` control and `16:9`/`9:16` only — pick a cinematic model
  when you need those.
