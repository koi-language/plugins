# Content Transformation (long-form → carousel)

How to turn a newsletter, blog post, article, or raw notes into carousel slides. Adapted from a proven LinkedIn-carousel workflow. Use this whenever the source is longer than a few bullet points.

## Source intake

Two input paths:

- **Direct content / topic** — the user pastes text or names a topic. Help them structure it (hook → value → CTA). No mandatory approval checkpoint, but still confirm the outline before rendering.
- **URL (newsletter / article / blog)** — fetch with WebFetch, then transform (below). A structure-approval checkpoint IS required before rendering.

### Fetching a URL

Validate it's public (`https://`, not paywalled/auth). If paywalled, ask the user to paste the text or give another URL. Extraction prompt:

```
Extract the main article content from this page. Include:
- Article title and author (if available)
- All section headings
- All body paragraphs
- Key statistics, examples, data points, or case studies
- Preserve the logical flow and structure
Ignore: navigation, headers/footers, sidebars, ads, subscription prompts, social buttons, related links.
```

Verify you got substantial content (>500 words, clear structure, identifiable topic). If extraction is sparse/failed, ask the user to paste the text directly.

## Step 1 — Identify the core angle

Pick ONE framework (see `carousel-structure.md`): Steps, Stats, Mistakes, Lessons, Examples, Storytelling, Comparison, Before/After.

Selection criteria:
- What is the source's STRONGEST value proposition?
- What would stop a scroll?
- What can be explained across 6–10 slides?
- What is most actionable and specific?

If the source covers many angles, prioritize the most actionable + most specific + most self-contained one.

## Step 2 — Extract slide content

**Hook (slide 1)**: most compelling statement/stat/question from the intro, condensed to a punchy headline (~10–20 words). Mark one highlight phrase.

**Content slides (2 … N-1)**: ONE key point each.
- Heading < 60 chars, specific, actionable.
- Body a few short lines (~15–40 words/slide) — these render as images, so keep it scannable.
- Cover WHAT/HOW/WHY in as few words as possible.
- Emphasize one key phrase.
- Examples: extract the punchline, not the full story.

**CTA (final)**: one-sentence summary + 1–3 short takeaways + clear follow/save ask.

Density budget: keep each slide to ~15–40 words. If a concept needs more, split into two slides (e.g. a "4-phase pattern" → phases 1–2, then 3–4).

## Step 3 — Transformation rules

- Newsletter paragraph (~400w) → one slide's worth of headline + a couple of lines (~15–40w). One section → 1–2 slides.
- **Preserve specificity**: keep "23% increase", "Sarah's team cut errors 47%" — drop "significant improvement".
- **Preserve credibility**: keep "Stanford study found…", "According to McKinsey…".
- **Preserve actionability**: keep the "how to apply" parts.
- **Adapt for visual medium**: short sentences (15–20 words), make implicit structure explicit (number the steps), front-load the value.

## Step 4 — Sequencing

| Framework | Order |
|-----------|-------|
| Steps | sequential (1 → 2 → 3) |
| Stats | most surprising first |
| Mistakes | most common → most costly |
| Lessons | fundamental → advanced (or chronological) |
| Examples | relatable → impressive |

Length mapping: <1,000w → 6–7 slides · 1,000–2,500w → 8–9 slides · >2,500w → 10 slides max (focus on ONE theme and say so).

## Step 5 — Quality checklist

- [ ] Each content slide has a clear heading (<60 chars)
- [ ] Hook has a highlight phrase
- [ ] Content slides kept to ~15–40 words (scannable as an image)
- [ ] One bold key phrase per slide
- [ ] 6–10 slides total
- [ ] Active voice, present tense, no vague advice
- [ ] Exact numbers/names/sources preserved
- [ ] Each slide is self-contained; flow is logical
- [ ] CTA has summary + 2–3 takeaways + clear ask

## Step 6 — Approval checkpoint (URL sources)

Before rendering, present the plan and WAIT for approval:

```
I analyzed the content. Here's the carousel approach:

Identified framework: [Steps/Stats/Mistakes/Lessons/Examples/…]
Carousel angle: "[slide-1 title]"
Proposed structure ([X] slides):
  1. Hook: [what grabs attention]
  2. [heading]: [one line]
  …
  X. CTA: [summary + ask]
Key content preserved: [specific stats/examples/frameworks]
Density: ~[X] words across [Y] slides

Want to change the angle, focus a different section, add/remove slides, or adjust the hook?
```

Don't render until the user approves or gives feedback. For direct-content input this checkpoint is optional (the user already structured it), but still confirm the outline.

## Edge cases

- **Too short (<500w)** → 6 slides min; add a context slide; note it'll feel concise.
- **Too long (>4,000w)** → focus one section; offer extra carousels for the rest.
- **Image-heavy** → use available text/captions; note some visual data may be missing.
- **Multi-part series** → note "Part X" in the CTA.
