# Transitions (default = hard cut)

The renderer cuts hard between clips unless a transition is set explicitly via
`set_clip_transition` (or a `transitionIn` / `transitionOut` object on the clip when you
build the JSON). Hard cuts are the right default — soft transitions easily look amateur if
applied uniformly.

A transition object is `{ type, durationMs, alignment?, params? }`. `transitionIn` fires
at the clip's `startMs`; `transitionOut` at its end. At a join between two adjacent clips,
the outgoing clip's `transitionOut` defines the cross-effect (otherwise the next clip's
`transitionIn` wins).

| Workflow / context | Default | When to add a soft transition |
|---|---|---|
| ad | Hard cut | Rarely — only on a rhetorical "before / after" reveal |
| explainer | Hard cut | Cross-fade (300 ms) between major narrative sections |
| tutorial | Hard cut | None — each step starts crisply |
| demo | Hard cut | Soft fade (200 ms) on the hero product reveal frame |
| social-post / Reels / TikTok | Hard cut + whoosh SFX | Never crossfade — kills the platform's punchy feel |
| Narrative / dialogue scene | Hard cut | Cross-fade on scene-change beats; never within a scene |

When in doubt, leave hard. Soft transitions are an editorial choice, not a polish step.
