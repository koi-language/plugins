# Platform Specs

Canvas size, aspect ratio, slide limits and safe zones for each social platform. The skill renders **square or vertical** images (never 16:9) and keeps text inside safe margins so platform UI never covers it.

## Canvas & Slide Limits

| Platform | Default canvas | Aspect | Allowed ratios | Max slides | Notes |
|----------|----------------|--------|----------------|------------|-------|
| **Instagram** (feed carousel) | 1080 × 1350 px | 4:5 | 1:1, 4:5 (default), 1.91:1 | 20 | 4:5 takes the most feed height — use it unless told otherwise |
| **LinkedIn** (image carousel) | 1080 × 1350 px | 4:5 | 1:1, 4:5 | 20 | Native multi-image carousel |
| **TikTok** (photo mode) | 1080 × 1920 px | 9:16 | 9:16 | 35 | Full-screen vertical; keep text well inside safe zone |
| **Facebook** (carousel) | 1080 × 1080 px | 1:1 | 1:1, 4:5 | 10 | Square is safest for link/cards |
| **Twitter / X** | 1080 × 1080 px | 1:1 | 1:1, 16:9 | 4 | Hard 4-image cap |

**Default rule**: if the user names a platform but no ratio, use the platform's default. If no platform is given, default to **Instagram 4:5 (1080 × 1350)** — the most common and most reusable across Instagram + LinkedIn + Facebook.

## Exact dimensions per network — never generate bigger

Every network displays carousel images at **≈1080 px wide** and downscales anything larger. These are the real upload dimensions — there is no benefit to going above them:

| Network | Ratio | Exact px to target | `aspectRatio` | `resolution` |
|---------|-------|--------------------|---------------|--------------|
| Instagram (portrait) | 4:5 | **1080 × 1350** | `4:5` | `1k` |
| Instagram (square) | 1:1 | **1080 × 1080** | `1:1` | `1k` |
| Instagram (Reels/Story) | 9:16 | **1080 × 1920** | `9:16` | `1k` |
| LinkedIn (carousel / PDF) | 4:5 | **1080 × 1350** | `4:5` | `1k` |
| LinkedIn (square) | 1:1 | **1080 × 1080** | `1:1` | `1k` |
| TikTok (photo) | 9:16 | **1080 × 1920** | `9:16` | `1k` |
| Facebook | 1:1 / 4:5 | **1080 × 1080** / **1080 × 1350** | `1:1` / `4:5` | `1k` |
| Twitter / X | 1:1 | **1080 × 1080** | `1:1` | `1k` |

**No network needs 2K/4K. A 2560×2560 or 2048×2560 image for Instagram is pure waste** — Instagram re-encodes it down to 1080 px wide, so you pay ~4–6× the credits for zero visible quality.

### How to hit these sizes

`generate_image` does NOT take pixel width/height — it takes `aspectRatio` + `resolution` enums (the `resolution` value is a ceiling on the LONGEST edge: `1k`≈1024, `2k`≈2048, `4k`≈4096). For social ALWAYS pass:

- `aspectRatio`: `4:5` / `1:1` / `9:16` (per the table)
- **`resolution: "1k"`** → long edge ≈1024 (so ~1024×1280 for 4:5, ~1024×1024 for 1:1, ~1024×1820 for 9:16) — matches what the networks actually serve.
- `quality: "medium"`.

**If a generated slide still comes out much larger than ~1280 px on the long edge** (e.g. 2560), the auto-picked model's smallest tier is oversized: check the live catalog with `get_tool_info(generate_image)` and pick a model/resolution whose ceiling is ~1K. Never omit `resolution` (omitting it defaults to 2K) and never request `2k`/`4k` for social. Generate every slide in the deck at the **same** ratio and resolution.

## Safe Zones (CRITICAL)

Feeds overlay UI on top of the image (username, caption, action buttons, the "1/N" dots, the swipe affordance). Text or key visuals under that UI get clipped or hidden.

| Edge | Keep clear | Why |
|------|-----------|-----|
| Top | ≥ 8% (≈110 px on 1350) | Profile row / status bar on full-screen formats |
| Bottom | ≥ 12% (≈160 px on 1350; more on 9:16) | Caption, action buttons, progress dots |
| Left / Right | ≥ 6% (≈65 px) | Rounded crop + reply rail |
| 9:16 (TikTok) | Keep all text within the centre 80% vertically and 86% horizontally | Right-side action rail + bottom caption are large |

Rule of thumb baked into every prompt: **all headline and body text lives inside a centred safe area with generous margins; no text touches any edge.**

## Export / File Specs

| Property | Value |
|----------|-------|
| Format | PNG (generation), JPG acceptable for upload |
| Color | sRGB |
| Min long edge | 1080 px (never upscale below) |
| Naming | `NN-slide-{slug}.png`, zero-padded, in swipe order |

## Per-Platform Authoring Notes

- **Instagram** — first slide is the scroll-stopper; cover ratio sets the whole carousel ratio. Strong hook + visible swipe cue. Save/Share drive reach.
- **LinkedIn** — slightly more formal tone; frameworks and numbered insights perform. Document (PDF) carousels allow more slides and richer text.
- **TikTok photo mode** — punchy, trend-aware, minimal text per slide; the right action rail and bottom caption eat space, so centre everything.
- **Facebook** — square + product/offer oriented; clear single CTA.
- **Twitter / X** — max 4 images; front-load the payoff, no long build-ups.
