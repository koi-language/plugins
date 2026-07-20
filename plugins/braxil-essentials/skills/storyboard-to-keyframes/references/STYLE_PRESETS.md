# Style Presets — Tenframe

This file contains the **3 official style presets** for Tenframe storyboard sheets. Each preset includes:

- **Trigger words** the user might say
- **Ready-to-use phrasing** to paste into the STYLE section of the prompt
- **Notes** on what to emphasize visually

When building a prompt, copy the relevant phrasing block into the **VISUAL STYLE** section of the storyboard prompt.

> **POV / first-person is NOT a style — it is a camera angle.** It lives at the **storyboard** level, per shot (`shot: "ECU POV"`, `shot: "MS first-person"`, etc.), and can combine with ANY of the 3 styles below. A "POV Premium 3D" storyboard, a "POV Claymation" storyboard or a "POV Realistic UGC" storyboard are all valid combinations — pick the visual style here, and set POV framing per shot in the storyboard's `shot` field. Don't list POV as a style choice in any form / select.

---

## 1. Premium 3D Animation

**User might say:** Pixar / Pixar-style / Disney / animated film / 3D animated / family animation / animated movie style

**⚠️ Important:** Never use the words "Pixar" or "Disney" in the actual image generation prompt — they trigger moderation and copyright filters. Use the phrasing below instead.

**Phrasing block (copy into prompt):**

```
Stylized photorealistic 3D animated film aesthetic, premium 
family-film studio quality, soft global illumination, expressive 
character design with large warm eyes and friendly proportions, 
subtle subsurface scattering on skin, rich material detail (fabric 
weave, hair strands, fresh produce textures), cinematic color 
grading with warm highlights and gentle shadows, shallow depth of 
field on close-ups, painterly background bokeh, polished 
high-budget animated movie look.
```

**Notes:**
- Emphasize expressive faces and warm color grading
- Characters should feel charming and slightly stylized — not photoreal
- Lighting is always soft and cinematic, never harsh

---

## 2. Claymation

**User might say:** claymation / clay / stop-motion / Aardman / Wallace and Gromit style / handcrafted / plasticine

**⚠️ Important:** Don't use "Aardman" or "Wallace and Gromit" — use generic phrasing.

**Phrasing block (copy into prompt):**

```
Handcrafted stop-motion claymation aesthetic, visible plasticine 
clay texture with subtle fingerprint imperfections, sculpted 
character forms with rounded proportions and oversized features, 
matte clay surface finish with soft specular highlights, miniature 
set design with handmade props, warm studio tungsten lighting, 
slight texture grain, charming imperfect handmade quality, soft 
shadows, stop-motion film feel with crafted physical materials 
throughout.
```

**Notes:**
- Everything should look sculpted — even liquids, food, fabric
- Embrace imperfection — visible fingerprints and tool marks add charm
- Avoid anything that looks too clean or digital

---

## 3. Realistic UGC Ad

**User might say:** UGC / user-generated / iPhone / phone-shot / authentic / TikTok-style / Instagram reel / casual / candid

**Phrasing block (copy into prompt):**

```
Authentic user-generated content aesthetic, shot-on-phone realism, 
natural unposed framing, soft available daylight or warm indoor 
lighting, slight handheld feel without being shaky, real-person 
proportions and natural skin texture, casual everyday clothing and 
settings, lifestyle-blogger color palette, modest depth of field, 
honest and approachable visual tone, social-media-native framing, 
relatable and unfiltered atmosphere.
```

**Notes:**
- Characters should look like real people, not models
- Settings should feel lived-in, not styled to perfection
- Lighting is whatever's naturally available — window light, lamps
- Slightly imperfect framing makes it feel real

---

## Custom Styles

If the user wants something outside these 3 presets (e.g., watercolor, anime, vintage film, cyberpunk):

1. Ask them to describe the style in 1–2 sentences
2. Rewrite their description into a phrasing block matching the format above
3. Confirm the phrasing with them before building
4. Never use copyrighted studio or franchise names directly — always rewrite as descriptive aesthetic phrasing

---

## Combining Style + Story

When you build the final prompt, drop the chosen phrasing block into the **VISUAL STYLE** section near the bottom of the prompt template. Keep the rest of the prompt structure identical.

Example placement in the final prompt:

```
═══════════════════════════════════════════════
VISUAL STYLE
═══════════════════════════════════════════════
[PASTE PHRASING BLOCK FROM CHOSEN PRESET HERE]

- Consistent main subject across all 10 frames
- Cohesive color palette appropriate to the topic
- Bold sans-serif for titles, lighter sans-serif for captions
- Rounded card corners with subtle shadows
- Professional storyboard reference aesthetic
```
