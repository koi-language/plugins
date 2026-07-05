# Confirmation Questions

Verbatim option copy for the confirmation step. Adapt wording to the runtime's native user-input tool (e.g. `AskUserQuestion`); intent matters more than exact phrasing. Batch all applicable questions into one call.

## Round 1 (always)

### Q1: Platform

```yaml
header: Platform
question: Which platform is this carousel for?
options:
  - label: "Instagram (Recommended)"
    description: 4:5 (1080×1350), up to 20 slides
  - label: LinkedIn
    description: 4:5 (1080×1350), up to 20 slides
  - label: TikTok
    description: 9:16 (1080×1920), photo mode
  - label: Facebook / X
    description: 1:1 (1080×1080); X caps at 4 slides
```

### Q2: Style

**Send ALL 17 presets as options in ONE call** — never a reduced list of 2-3 (the #1 complaint is only seeing a few when there are 17). Put the 2-3 best content matches FIRST and mark them `recommended: true`; list the remaining presets after; end with "Custom dimensions". The whole list ships in a single prompt, so the client can show the top picks and collapse the rest behind a "see all" toggle **without another round-trip** — do NOT split this into "ask 3, then re-prompt with the rest". One call, all options.

Build each option from the **Full Style Catalog** below (title = preset, description = look + best-for). Example shape:

```yaml
header: Style
question: Which visual style?
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
| `bold-editorial` | Magazine-cover impact, huge type, dramatic contrast | Launches, hot takes, personal brand |
| `editorial-infographic` | Publication-quality, cool palette, dense explainer panels | Tech explainers, data threads |
| `corporate` | Navy & gold, structured grids, business polish | B2B, thought-leadership, finance |
| `minimal` | Maximum whitespace, single accent, zen restraint | Quotes, one big idea per slide |
| `notion` | Clean SaaS dashboard, neutral, data-forward cards | Product, metrics, SaaS tips |
| `blueprint` | Engineering schematics, cool blues, grid lines | Technical, architecture, how-it-works |
| `scientific` | Academic precision, clean figures, labeled diagrams | Science, health, research |
| `intuition-machine` | Technical briefing, cool, dense, bilingual-friendly | Academic, AI/ML, documentation |
| `dark-atmospheric` | Cinematic dark backgrounds with glowing accents | Entertainment, gaming, bold reveals |
| `sketch-notes` | Friendly hand-drawn notes on warm off-white | Tutorials, education, relatable tips |
| `chalkboard` | Colorful chalk on a dark board | Teaching, lessons, step-by-step |
| `hand-drawn-edu` | Hand-drawn infographic with macaron pastel zones | Process explainers, onboarding |
| `watercolor` | Soft hand-painted washes, wellness palette | Lifestyle, wellness, coaching |
| `fantasy-animation` | Magical storybook animation, vibrant, whimsical | Storytelling, creative, kids |
| `vector-illustration` | Flat friendly vector with bold outlines, retro colors | Creative, explainers, playful brands |
| `pixel-art` | Retro 8-bit game aesthetic, chunky pixels | Gaming, dev, nostalgia |
| `vintage` | Aged paper, sepia, heritage stamps | History, heritage, storytelling |

(Per-preset full spec: `references/styles/<preset>.md`. Or pick "Custom dimensions" to combine texture + mood + typography + density freely. Beyond these, the **Default Style** in SKILL.md is a clean professional editorial look used when the user doesn't pick.)

### Q3: Slide count

```yaml
header: Slides
question: How many slides?
options:
  - label: "{N} slides (Recommended)"
    description: 6–10 is optimal for engagement
  - label: "Fewer ({N-2})"
    description: More condensed
  - label: "More ({N+2})"
    description: More detail (respect platform caps)
```

### Q4: Review structure

```yaml
header: Review
question: Review the slide structure before generating?
options:
  - label: "Yes, review first (Recommended)"
    description: See headings + flow before generating
  - label: No, generate directly
    description: Trust the outline and proceed
```

## Round 2 — Custom dimensions

Triggered only when Q2 = "Custom dimensions". Batch four questions — texture, mood, typography, density — using the SAME option copy as slide-deck. Texture: clean / grid / organic / pixel / paper. Mood: professional / warm / cool / vibrant / dark / neutral / macaron. Typography: geometric / humanist / handwritten / editorial / technical. Density: minimal / balanced / dense. The four answers replace the preset.

## Structure Review (Step 4)

```yaml
header: Confirm
question: Ready to generate?
options:
  - label: "Yes, generate (Recommended)"
    description: Generate the slides
  - label: Edit structure first
    description: I'll adjust the outline before continuing
  - label: Regenerate structure
    description: Try a different angle / framework
```
