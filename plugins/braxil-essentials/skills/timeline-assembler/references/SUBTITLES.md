# Subtitles

`add_subtitles_to_timeline` lays a synthetic subtitle track. Add it when:

- **Tutorial** → always. Step-by-step viewers read along.
- **Explainer** → optional, recommended for social-feed distribution where viewers may
  scroll with sound off.
- **Ad / Demo** → captions are usually baked into the storyboard already (CAPTION row of
  each panel), so a separate subtitle track duplicates them. Skip unless the user
  explicitly asked.
- **Social-post** → captions are part of the visual language — usually rendered as big
  animated text in the V-track clips themselves, not as a subtitle track.

When you do add subtitles, derive the segments from the panel `caption` / `dialogue`
fields the workflow already produced; never re-write them at the timeline stage.
