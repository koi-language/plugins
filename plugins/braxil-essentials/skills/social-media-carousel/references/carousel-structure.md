# Carousel Structure & Best Practices

How to structure a high-engagement social carousel. Every slide is a generated image.

## The Spine: Hook → Value → CTA

Every carousel is three acts:

| Slide | Role | Job |
|-------|------|-----|
| 1 | **Hook** | Stop the scroll. If this fails, nobody swipes. |
| 2 … N-1 | **Value** | One idea per slide, in logical order. |
| N | **CTA** | Tell them what to do: save, follow, comment, visit. |

Recommended length: **6–10 slides** (optimal for LinkedIn/Instagram engagement). Hard caps per platform live in `platform-specs.md`.

## Content Frameworks

Pick the ONE that fits the source best:

| Framework | Shape | Carousel title pattern |
|-----------|-------|------------------------|
| **Steps / Process** | sequential | "How to [outcome]" · "X steps to [result]" |
| **Stats / Data** | most surprising first | "X stats about [topic]" |
| **Mistakes** | common → costly | "X mistakes [audience] make" |
| **Lessons** | fundamental → advanced | "X lessons from [experience]" |
| **Examples / Cases** | relatable → impressive | "X examples of [concept]" |
| **Storytelling** | hook → setup → challenge → turn → result → lesson → CTA | "How we [transformation]" |
| **Comparison** | A-side / B-side / verdict | "[A] vs [B]: what actually wins" |
| **Before / After** | before → process → after → takeaway | "I redesigned [thing]" |

## Slide 1: The Hook

The single most important slide.

| Hook type | Example | Highlight word |
|-----------|---------|----------------|
| Bold claim | "90% of landing pages make this mistake" | mistake |
| Surprising stat | "87% of AI projects fail" | fail |
| Question | "Why do your ads get clicks but no conversions?" | — |
| Number + promise | "7 Python tricks I wish I learned sooner" | 7 |
| Contrarian | "Stop writing blog posts (do this instead)" | Stop |
| Before/after | Show the transformation up front | — |

Rules:
- 1–2 sentences, ~50–100 words max.
- Mark ONE "highlight" phrase (the scroll-stopper) and emphasize it via color/weight in the slide.
- Add a visible **swipe cue** ("Swipe →" / arrow) so people know there's more.
- Promise the payoff; make them swipe to get it.

## Slides 2 … N-1: Value

One point per slide. Never cram two ideas.

- **Heading**: < 60 characters, specific and actionable.
  - Good: "Replace vague words with exact terms" · Bad: "Be more specific"
- **Body**: keep it tight — a few short lines, ~30–40 words per slide. Dense text doesn't render legibly as an image; if a point needs more, split it across two slides.
- Structure each point as WHAT (concept) → HOW (apply) → WHY (benefit), woven naturally, not labelled.
- **Emphasize one phrase** per slide — the key takeaway (larger/bolder/accent color).
- Break long sentences: 15–20 words max. Front-load the punchline, then context.
- Keep exact numbers, names, sources ("23% increase", "Stanford study found…") — never soften to "significant increase".

## Slide N: CTA

Not just "Thanks". Include:
- A one-sentence summary of the pattern/lesson.
- 2–3 takeaway bullets.
- A clear ask: **Save** 🔖 / **Follow** / **Comment** / visit a link.
- For a series: "Part X — follow for the full series".

## Swipe Psychology

| Principle | Application |
|-----------|-------------|
| Curiosity gap | Hook promises value that requires swiping |
| Numbered progress | "3/7" / page dots create a completion drive |
| Visual continuity | Consistent design signals "there's more" |
| Increasing value | Save the best tip for near the end |
| Swipe cue | Arrow or "Swipe →" on slide 1 |

## Text Hierarchy (mobile-readable)

Carousels are read on phones. Sizes are at 1080px-wide canvas; scale for 9:16.

| Element | Size | Weight |
|---------|------|--------|
| Slide number / kicker | 96–120px | Black (900) |
| Headline | 48–72px | Bold (700–900) |
| Body | 24–32px | Regular (400) |
| Caption / tag | 18–22px | Medium (500) |

Readability rules:
- Max ~30–40 words per slide — these are images, not documents.
- Line height 1.5–1.6. Min text contrast 4.5:1 (WCAG AA).
- Keep ALL text inside the safe zone (see `platform-specs.md`) — feeds overlay UI on the edges.

## Visual Consistency (across the whole deck)

Keep identical on every slide: background palette, font family, text alignment, margins, accent color, numbering format, header/footer. Inconsistency reads as "different posts" and kills the swipe.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Weak hook | Bold claim / question / number + promise on slide 1 |
| Too much text per slide | One idea; cut to the punchline |
| No visual consistency | Same colors, fonts, margins, footer throughout |
| No swipe indicator | Add "Swipe →" / arrow on slide 1 |
| No CTA on last slide | Ask to save, follow, share, or comment |
| Text under platform UI | Respect the safe zone on every edge |
| Vague advice | Keep exact numbers, names, sources |
| Square on Instagram | Use 4:5 (1080×1350) for more feed height |
