# Seedance — reference guide

> Per-model reference guide for the **Seedance family** — always **2.5**
> (`bytedance/seedance-2.5/*`; 2.0 is never used). Parameter tables live in
> `references/models.md`; prompt WORDING is authored by
> `cinematic-video-prompt-engineer` — this file is ONLY about the references.

## References go in DIRECTLY — no Seedream pass, ever

Attach every reference **as it is**: character sheets / turnarounds, the
user's photos, location plates, props, continuity frames. **Never** run a
reference through Seedream (or any other image model) to "re-synthesise" it
before a Seedance render — no 1:1 clones, no laundered copies, no
`inspect_creation` gate on which model made a sheet. The user's decision: the
references Seedance gets are the real ones, period.

## If Seedance rejects a reference (likeness filter)

Seedance may answer `"image_urls: may contain likenesses of real people"`.
Follow `video-generator`'s "When a generation FAILS":

1. Retry the IDENTICAL request, unchanged, two or three times — these
   rejections are often random.
2. Still rejected → **stop and tell the user**: which reference trips it and
   the options (e.g. another model that accepts the same references). Never
   swap the reference for a re-generated copy, never drop it, never thin the
   prompt.

## Chaining (clip K ≥ 2)

Chaining runs on **SELECTIVE CONTINUITY FRAMES** on every model: full-res
frames extracted from clip K-1's render, ONLY the takes the new clip must
match, each under its own role alias (`prev_end`, `prev_shot3`…) — the flow
lives in `storyboard-to-video`'s "Clip chaining". On Seedance they are attached
**as-is**, like on every other model.

**Reference AUDIO** (the previous clip's extracted tail, via `referenceAudio`)
goes in as-is on every Seedance slug that lists reference audio; give it a
legend line saying the soundscape continues its bed.

**Prefer the continuity frames over the previous clip as a video reference**:
the frames carry the exact screen positions of every character, which is what
keeps "who is where" across the cut.
