# FPS, dimensions & aspect ratio

How the timeline gets its frame rate and output size, and why the aspect ratio has to be
decided at clip-generation time, not at render time.

## FPS and dimensions inherit from the first video clip

The timeline does NOT have a hardcoded frame rate or output size. When the FIRST video
clip is dropped via `add_clip_to_timeline`, it ffprobes the source for `avg_frame_rate`,
`width`, `height` and stamps them onto `timeline.settings.{projectFps, projectWidth,
projectHeight}`. The renderer reads those before falling back to its 30 fps × 1920×1080
default.

**Why this matters:** a 24 fps source playing inside a 30 fps timeline (or 1080×1920
vertical clips in a 1920×1080 horizontal timeline) produces visible black flickers at
every clip seam and black bands around the frame. Inheritance keeps source and output
aligned by default.

**Rules:**
- DO NOT pass `fps`, `width`, or `height` to `create_timeline` unless the user explicitly
  asked for a specific render shape.
- DO NOT pass them to `render_timeline` either — let the inherited values drive the render.
- The inheritance only fires for the FIRST video clip on an empty timeline. Later clips on
  a populated timeline don't silently change the project's framerate.
- If the clips are heterogeneous (mixed 24 / 30 fps sources), the FIRST clip wins. Either
  re-encode the rest to match in pre-production, OR explicitly set the target fps in
  `settings` before dropping any clip.

## Aspect ratio comes from the platform, applied to every clip

Pass `aspectRatio` to EVERY `generate_video` call upstream. The timeline does NOT reframe
clips on its own — if the clips are 16:9 and the timeline ends up 9:16, the renderer
letterboxes (black bars top + bottom). The reframe must happen at clip generation time,
not at render time.

| Platform | Aspect ratio | Frame size (typical) |
|---|---|---|
| Reels / TikTok / Shorts | 9:16 | 1080 × 1920 |
| YouTube / Vimeo / Web | 16:9 | 1920 × 1080 |
| Instagram feed (square) | 1:1 | 1080 × 1080 |
| Instagram feed (portrait) | 4:5 | 1080 × 1350 |
