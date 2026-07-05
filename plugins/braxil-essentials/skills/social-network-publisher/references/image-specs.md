# Image specs per social network — generate at THESE sizes, never 4K

Social networks downscale (or outright reject) oversized images. Generating a
4K / 2048px+ image for a post is wasted compute AND triggers failures — most
notably **X returns `413 Payload Too Large`** when the image file exceeds ~5 MB.

**Hard rule:** for any image destined for a social post, generate (or resize)
to a **long edge ≤ 1440 px** and a **file ≤ 5 MB**. Default to **1080 px**.
NEVER generate social images at 2048 px, 4K, or "max quality" — the platform
throws away the extra pixels anyway.

Pick the aspect ratio for the format, then the size below.

| Network        | Format                | Generate at   | File limit | Notes |
|----------------|-----------------------|---------------|------------|-------|
| **X (Twitter)**| landscape 16:9        | 1600 × 900    | **≤ 5 MB** | >5 MB ⇒ 413. Export JPEG q≈85. |
| X              | square 1:1            | 1080 × 1080   | ≤ 5 MB     | |
| **Instagram**  | square 1:1            | 1080 × 1080   | ≤ 8 MB     | IG caps width at 1080 — anything wider is downscaled. |
| Instagram      | portrait 4:5          | 1080 × 1350   | ≤ 8 MB     | Best feed real estate. |
| Instagram      | story / reel 9:16     | 1080 × 1920   | ≤ 8 MB     | |
| **Facebook**   | feed square / portrait| 1080 × 1080 / 1080 × 1350 | ≤ 8 MB | |
| Facebook       | link / landscape      | 1200 × 630    | ≤ 8 MB     | |
| **LinkedIn**   | feed square           | 1200 × 1200   | ≤ 5 MB     | |
| LinkedIn       | link / landscape      | 1200 × 627    | ≤ 5 MB     | |
| **TikTok**     | image post 9:16       | 1080 × 1920   | ≤ 5 MB     | TikTok is video-first; image posts are portrait. |

## Multi-network post (the common case)
When the SAME image goes to several networks at once (X + Facebook + Instagram),
generate ONE image at **1080 × 1080** (square — safe everywhere) or **1080 × 1350**
(portrait), export JPEG. That single asset satisfies every network's limit and
will never 413.

## How to hit the size (use Braxil's own media tools, never a script)
- When you GENERATE the image, request the target dimensions above (e.g. a
  1080×1080 square) — do NOT generate at 4K and hope.
- If an image you already have is too big (wrong dimensions or > 5 MB), resize
  it with Braxil's image tools to the spec BEFORE publishing. Never run a
  Python/PIL/ImageMagick script to do it.
