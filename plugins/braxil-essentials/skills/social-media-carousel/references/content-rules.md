# Content & Style Rules

Quality rules for carousel content. Every slide is a generated image.

## Content Rules

1. **One idea per slide.** Remove redundancy; clarity over comprehensiveness.
2. **Data traceability.** Keep exact numbers, names, and sources on the slide ("23% increase", "Stanford study"). Never soften to vague claims.
3. **Self-contained.** Each slide makes sense on its own — no "like slide 2". Every prompt carries its real content.
4. **No placeholders.** No "[insert data]" / "TBD". All text final before rendering.
5. **Mobile-first.** Few words, large type, high contrast, text inside the safe zone (`platform-specs.md`).

## Style Rules

### 1. Narrative headlines (tell the story, not label it)

| Bad | Good |
|-----|------|
| "Key Statistics" | "Usage doubled in 6 months" |
| "Our Solution" | "One platform replaces five tools" |
| "Benefits" | "Teams save 10 hours weekly" |
| "Be more specific" | "Replace vague words with exact terms" |

### 2. Avoid AI clichés

Cut: "dive into", "explore", "journey", "let's look at", "exciting", "amazing", "revolutionary", "in conclusion".

### 3. Meaningful CTA (not just "Thanks")

End with a clear ask: Save 🔖 / Follow / Comment / visit a link — plus a one-line summary or takeaway. For a series, "Part X — follow for the rest".

### 4. Consistent visual language

Same palette, type hierarchy, margins, accent, numbering, and header/footer across every slide.

## Carousel Structure

| Position | Type | Purpose |
|----------|------|---------|
| 1 | Hook | Bold claim / question / stat + swipe cue |
| 2 … N-1 | Value | One point each, narrative heading, bold takeaway |
| N | CTA | Summary + clear ask |

## Key Specifications

| Spec | Value |
|------|-------|
| Aspect ratio | 4:5 / 1:1 / 9:16 (never 16:9) — per platform |
| Slide count | 6–10 optimal; platform caps in `platform-specs.md` |
| Required slides | Hook + CTA minimum |
| Watermarks / fake UI | None |
| Words per slide | ≤ 30–40 (these are images, keep it scannable) |
| Language | source language; keep technical tokens in English |
| Tone | Direct, confident; active voice, present tense |
