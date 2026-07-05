# Confirmation Questions

Concrete option copy for the confirmation steps. SKILL.md lists which questions to ask — this file gives the verbatim options used in Claude Code. Adapt copy to the runtime's native user-input tool; the intent matters more than the exact wording.

## Round 1 (Always)

Batch all five questions in a single `AskUserQuestion` call.

### Q1: Style

**Send ALL 17 presets as options in ONE call** — never a reduced list of 2-3 (the #1 complaint is only seeing a few when there are 17). Put the 2-3 best content matches FIRST and mark them `recommended: true`; list the remaining presets after them; end with "Custom dimensions". Because the whole list ships in a single prompt, the client can show the top picks and collapse the rest behind a "see all" toggle **without another round-trip** — so do NOT split this into "ask 3, then re-prompt with the rest". One call, all options.

Build each option from the **Full Style Catalog** below (title = preset, description = its one-line look + best-for). Example shape (recommended first, then the rest, then Custom):

```yaml
header: Style
question: Which visual style for this deck?
options:
  - label: "{recommended_preset}"
    recommended: true
    description: "{its look — best for {fit}}"
  - label: "{second_best}"
    recommended: true
    description: "{its look}"
  # …then ALL remaining presets from the catalog, each title + one-line description…
  - label: Custom dimensions
    description: Choose texture, mood, typography, density separately
```

#### Full Style Catalog (17 presets)

| Style | Look | Best for |
|-------|------|----------|
| `blueprint` | Engineering schematics, cool blues, grid lines, dimension marks | Architecture, system design, technical |
| `corporate` | Navy & gold, structured grids, business polish | Investor decks, proposals, quarterly |
| `minimal` | Maximum whitespace, single accent, zen restraint | Executive briefings, keynotes |
| `notion` | Clean SaaS dashboard, neutral, data-forward cards | Product demos, metrics, SaaS |
| `bold-editorial` | Magazine-cover impact, huge type, dramatic contrast | Launches, keynotes, marketing |
| `editorial-infographic` | Publication-quality, cool palette, dense explainer panels | Tech explainers, journalism, research |
| `scientific` | Academic precision, clean figures, labeled diagrams | Biology, chemistry, medical |
| `intuition-machine` | Technical briefing, cool, dense, bilingual-friendly | Academic, research, documentation |
| `dark-atmospheric` | Cinematic dark backgrounds with glowing accents | Entertainment, music, gaming |
| `sketch-notes` | Friendly hand-drawn notes on warm off-white | Tutorials, education, beginners |
| `chalkboard` | Colorful chalk on a dark board | Classroom, teaching, lessons |
| `hand-drawn-edu` | Hand-drawn infographic with macaron pastel zones | Process explainers, onboarding, diagrams |
| `watercolor` | Soft hand-painted washes, wellness palette | Lifestyle, wellness, travel |
| `fantasy-animation` | Magical storybook animation, vibrant, whimsical | Storytelling, fantasy, kids' content |
| `vector-illustration` | Flat friendly vector with bold outlines, retro colors | Creative, children, explainers |
| `pixel-art` | Retro 8-bit game aesthetic, chunky pixels | Gaming, retro, developer culture |
| `vintage` | Aged paper, sepia, heritage stamps | History, heritage, expeditions |

(Per-preset full spec: `references/styles/<preset>.md`. Or pick "Custom dimensions" to combine texture + mood + typography + density freely.)

### Q2: Audience

```yaml
header: Audience
question: Who is the primary reader?
options:
  - label: General readers (Recommended)
    description: Broad appeal, accessible content
  - label: Beginners/learners
    description: Educational focus, clear explanations
  - label: Experts/professionals
    description: Technical depth, domain knowledge
  - label: Executives
    description: High-level insights, minimal detail
```

### Q3: Slide Count

```yaml
header: Slides
question: How many slides?
options:
  - label: "{N} slides (Recommended)"
    description: Based on content length
  - label: "Fewer ({N-3} slides)"
    description: More condensed, less detail
  - label: "More ({N+3} slides)"
    description: More detailed breakdown
```

### Q4: Review Outline

```yaml
header: Outline
question: Review outline before generating prompts?
options:
  - label: Yes, review outline (Recommended)
    description: Review slide titles and structure
  - label: No, skip outline review
    description: Proceed directly to prompt generation
```

### Q5: Review Prompts

```yaml
header: Prompts
question: Review prompts before generating images?
options:
  - label: Yes, review prompts (Recommended)
    description: Review image generation prompts
  - label: No, skip prompt review
    description: Proceed directly to image generation
```

## Round 2 — Custom Dimensions

Triggered only when Q1 of Round 1 = "Custom dimensions". Batch all four dimension questions.

### Texture

```yaml
header: Texture
question: Which visual texture?
options:
  - label: clean
    description: Pure solid color, no texture
  - label: grid
    description: Subtle grid overlay, technical
  - label: organic
    description: Soft textures, hand-drawn feel
  - label: pixel
    description: Chunky pixels, 8-bit aesthetic
```

`paper` is also valid — accept via "Other".

### Mood

```yaml
header: Mood
question: Which color mood?
options:
  - label: professional
    description: Cool-neutral, navy/gold
  - label: warm
    description: Earth tones, friendly
  - label: cool
    description: Blues, grays, analytical
  - label: vibrant
    description: High saturation, bold
  - label: macaron
    description: Pastel blocks on cream
```

`dark`, `neutral` valid via "Other".

### Typography

```yaml
header: Typography
question: Which typography style?
options:
  - label: geometric
    description: Modern sans-serif, clean
  - label: humanist
    description: Friendly, readable
  - label: handwritten
    description: Marker/brush, organic
  - label: editorial
    description: Magazine style, dramatic
```

`technical` valid via "Other".

### Density

```yaml
header: Density
question: Information density?
options:
  - label: balanced (Recommended)
    description: 2-3 key points per slide
  - label: minimal
    description: One focus point, maximum whitespace
  - label: dense
    description: Multiple data points, compact
```

## Outline Review (Step 4)

```yaml
header: Confirm
question: Ready to generate prompts?
options:
  - label: Yes, proceed (Recommended)
    description: Generate image prompts
  - label: Edit outline first
    description: I'll modify outline.md before continuing
  - label: Regenerate outline
    description: Create new outline with different approach
```

## Prompt Review (Step 6)

```yaml
header: Confirm
question: Ready to generate slide images?
options:
  - label: Yes, proceed (Recommended)
    description: Generate all slide images
  - label: Edit prompts first
    description: I'll modify prompts before continuing
  - label: Regenerate prompts
    description: Create new prompts with different approach
```

## Existing Content (Step 0 / Step 1.3)

```yaml
header: Existing
question: Existing content found. How to proceed?
options:
  - label: Continue (Recommended)
    description: Resume from the first incomplete stage — keep the source/analysis/outline already approved, no re-research
  - label: Regenerate outline
    description: Keep images, regenerate outline only
  - label: Regenerate images
    description: Keep outline, regenerate images only
  - label: Backup and regenerate
    description: Backup to {slug}-backup-{timestamp}, then regenerate all
  - label: Exit
    description: Cancel, keep existing content unchanged
```
