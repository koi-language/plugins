# Carousel Outline Template

Structure for an AI-illustrated carousel outline. The `<STYLE_INSTRUCTIONS>` block is the SINGLE SOURCE OF TRUTH for style; per-slide prompts copy it verbatim (they do NOT re-read style files). The style system is the same as slide-deck — see `references/styles/<preset>.md` and `references/dimensions/*.md`. For how to assemble `STYLE_INSTRUCTIONS` from a preset or custom dimensions, follow the same construction used by slide-deck (Design Aesthetic, Background, Typography, Color Palette, Visual Elements, Density Guidelines, Style Rules).

## Header

```markdown
# Carousel Outline

**Topic**: [topic]
**Platform**: [Instagram | LinkedIn | TikTok | Facebook | Twitter/X]
**Aspect Ratio**: [4:5 1080×1350 | 1:1 1080×1080 | 9:16 1080×1920]
**Framework**: [Steps | Stats | Mistakes | Lessons | Examples | Storytelling | Comparison | Before/After]
**Style**: [preset name OR "custom"]
**Dimensions**: [texture] + [mood] + [typography] + [density]
**Language**: [output language]
**Slide Count**: N slides
```

## STYLE_INSTRUCTIONS

```markdown
<STYLE_INSTRUCTIONS>
Design Aesthetic: [2-3 sentences combining the four dimensions]
Background:
  Texture: [from texture dimension]
  Base Color: [from mood palette]
Typography:
  Headlines: [visual description, NOT a font name]
  Body: [visual description]
Color Palette:
  Primary Text: [Name] ([Hex]) - [usage]
  Background: [Name] ([Hex]) - [usage]
  Accent 1: [Name] ([Hex]) - [usage]
  Accent 2: [Name] ([Hex]) - [usage]
Visual Elements:
  - [element 1]
  - [element 2]
Density Guidelines:
  - Content per slide: [from density dimension]
  - Whitespace: [from density dimension]
Style Rules:
  Do: [from dimension combination]
  Don't: [anti-patterns]
</STYLE_INSTRUCTIONS>
```

## Slide entries

### Hook (Slide 1)

```markdown
## Slide 1 of N
**Type**: Hook
**Filename**: 01-slide-hook.png

// NARRATIVE GOAL
Stop the scroll; promise the payoff.

// KEY CONTENT
Headline: [bold claim / question / number+promise]
Highlight: [the one scroll-stopper word/phrase]
Swipe cue: Swipe → (visible)

// VISUAL
[Composition, focal point, accent treatment]

// LAYOUT
Layout: title-hero (or key-stat for a stat hook)
```

### Value (Slides 2 … N-1)

```markdown
## Slide X of N
**Type**: Value
**Filename**: {NN}-slide-{slug}.png

// NARRATIVE GOAL
[the one idea this slide delivers]

// KEY CONTENT
Kicker: [optional 01/02…]
Headline: [narrative, not a label — "Usage doubled in 6 months", not "Key stats"]
Body:
- [point with the LITERAL number/label/caption]
- [point]
Key takeaway: [the one phrase to emphasize]

// VISUAL
[supporting icon/diagram; keep real data, not placeholders]

// LAYOUT
Layout: [optional from layouts.md]
```

### CTA (Slide N)

```markdown
## Slide N of N
**Type**: CTA
**Filename**: {NN}-slide-cta.png

// NARRATIVE GOAL
Convert the swipe into an action.

// KEY CONTENT
Headline: [memorable close / summary line]
Ask: Save 🔖 / Follow / Comment / [link]
Handle: [@author if supplied]

// VISUAL
[clean, on-brand close]

// LAYOUT
Layout: quote-callout or key-stat
```

## Rules

- Filenames: zero-padded `NN-slide-{slug}.png`, kebab-case slug ≤ 30 chars, in swipe order.
- Hook is always slide 1, CTA always slide N.
- Keep numbers/labels/captions LITERAL in the outline so prompts can copy them (no "a data grid of results").
- Generate every slide at the same aspect ratio.
- Reuse `references/layouts.md` (same gallery as slide-deck) for `Layout:` hints — but favor vertical/square-friendly layouts (title-hero, key-stat, bullet-list, icon-grid, split is risky on 9:16).
