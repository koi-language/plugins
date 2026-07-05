---
name: logo-creator
description: Create logos using AI image generation. Discuss style/ratio, generate variations, iterate with user feedback, crop, remove background, and export as SVG. Use when user wants to create a logo, icon, favicon, or brand mark.
triggers:
  - "logo"
  - "brand"
  - "icon"
  - "favicon"
  - "mascot"
  - "emblem"
  - "create logo"
  - "design logo"
---

# Logo Creator Skill

Create professional logos through AI image generation with an iterative design process.

## Workflow

### Step 1: Discovery & Requirements

Before generating, gather requirements from user:

**Ask about:**
1. **Project/Brand name** - What is the logo for?
2. **Style preference** - See [references/styles.md](./references/styles.md) for options:
   - Pixel art / 8-bit retro
   - Minimalist / flat design
   - 3D / isometric
   - Hand-drawn / sketch
   - Mascot / character
   - Monogram / lettermark
   - Abstract / geometric

3. **Aspect ratio** - Default is 1:1 (square), options:
   - `1:1` - Square (favicons, app icons)
   - `16:9` - Wide (headers, banners)
   - `4:3` - Standard
   - `2:3` - Portrait

4. **Color preferences**:
   - Monochrome (black & white)
   - Specific brand colors
   - Let AI decide

5. **Reference images** - Any existing logos or styles to reference?

**Wait for user confirmation before proceeding!**

### Step 2: Generate Logo Variations

Generate 20 logo variations (default) in a grid, enumerating each variation.

**Prompt Tips:**
- Include style keywords: "pixel art", "minimalist", "8-bit", "flat design"
- Specify colors: "black on white", "monochrome", "blue gradient"
- Add context: "tech startup", "food brand", "gaming company"
- Request format: "icon", "emblem", "mascot", "lettermark"

### Step 3: Show the logo to the User   

Show the resultant logos to the user

### Step 4: Iterate with User

Ask user which logos they prefer:
- "Which logos do you like? (e.g., #5, #12, #18)"
- "What do you like about them?"
- "Any changes you'd want?"

Based on feedback go to Step 1 and repeat the process taking into account the user´s feedback until the user agrees with one design

### Step 5: Finalize Logo

Once user approves a logo, process it:

**5a. Generate an image with the choosen logo:**

**5b. Remove background from the image generated at 5a:**

**5c. Convert to SVG:**
```bash
python3 <skill_dir>/scripts/vectorize.py {input.png} {output.svg}
```

### Step 6: Deliver Final Assets

Present final deliverables:

## Quick Reference

### Common Prompt Patterns

**Pixel Art:**
```
Pixel art {subject} logo, 8-bit retro style, black pixels on white background, {size}x{size} grid, minimalist icon
```

**Minimalist:**
```
Minimalist {subject} logo, flat design, clean lines, {color} on white, simple geometric shapes
```

**Mascot:**
```
Cute {animal/character} mascot logo, friendly expression, {style} style, {colors}, suitable for brand icon
```

**Lettermark:**
```
Letter "{letter}" logo, modern typography, {style} design, {colors}, clean professional look
```

### Supported Aspect Ratios

- `1:1` - Square (default for logos)
- `2:3`, `3:2` - Portrait/Landscape
- `3:4`, `4:3` - Standard
- `4:5`, `5:4` - Photo
- `9:16`, `16:9` - Wide
- `21:9` - Ultra-wide

## References

- [references/styles.md](./references/styles.md) - Logo style guide with prompt examples
- [examples/opc-logo-creation.md](./examples/opc-logo-creation.md) - Full example conversation
