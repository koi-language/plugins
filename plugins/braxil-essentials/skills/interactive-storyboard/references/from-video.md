# Storyboard FROM AN EXISTING VIDEO: watch it, then transcribe 1:1

When the input is a source video (the user hands you a video and asks to storyboard it, reverse-engineer it, "hazme un storyboard de este vídeo"), the storyboard is NOT a creative invention: it is a FAITHFUL 1:1 transcription of that exact video, toma a toma, from what is ON SCREEN. Never from the title or a guess.

## STEP 0: WATCH the video with `read_file`. Mandatory, and your FIRST action.

Call `read_file` on the video path: it attaches the WHOLE video natively (motion + audio + every frame) and you literally watch it on your next turn. Watching it IS the analysis.

Do NOT reconstruct the video piecemeal: NO `ffprobe`/`ffmpeg`, NO `extract_frame`, NO `transcribe_audio`, NO shell. Those shatter the footage into disconnected stills plus a separate audio dump; you lose the cuts, the motion, the timing, and the shot-to-line sync, which is exactly what a 1:1 storyboard needs. If `read_file` says the video is too large even after downscaling, tell the user to trim it; do NOT fall back to frame extraction.

## Transcription rules

- **One shot per CUT, in order.** Segment at every hard cut. Every plano in the video = exactly ONE shot in the storyboard. Do not merge two shots, do not split one continuous take, do not add or drop any. 23 cuts = 23 shots.
- **Exact timecodes.** Each shot's `duration` = its real on-screen length (out-second minus in-second). Track the running in/out as you go.
- **The real camera, read off the footage.** `shot` = the actual framing (matched to a preset); `movement` = the actual camera move. Observe, do not guess.
- **The real action, precise.** `action` = exactly what happens on screen in that shot, at the zero-ambiguity bar (concrete identifiers, exact mechanics, carry-forward state).
- **Dialogue and sound verbatim.** `dialogue` = the spoken lines exactly as said in that shot (you heard them when you watched; write them word for word, no separate transcription step); `sfx`/`music` = what is actually heard.
- **Write the real `synopsis`**: the premise of the story you just watched. Mandatory in this flow.
- **1:1, zero reinterpretation.** The bar: someone could RE-SHOOT the exact original video from your storyboard alone: same cuts, same timing, same framings, same action, same lines. Anything that drifts is a bug.

## VERIFY before you save (this is where 1:1 is won or lost)

Two numbers must match the real video EXACTLY:

1. **Total duration.** `read_file` returned the video's exact total length (`durationSec` in its result; use THAT number, do not re-measure). The sum of all shot durations MUST equal it. If they do not match, you missed a shot, merged two, or mistimed one: rewatch and fix before saving. Do NOT shave or pad a duration to force the total.
2. **Shot count.** The number of shots MUST equal the number of cuts. The #1 failure is missing fast cuts: a video can cut twice within the same second. If you are not certain you caught EVERY cut, `read_file` the video again and re-watch the dense stretches before saving. Rewatching always beats shipping a storyboard with fewer planos than the original.

Only call `save_storyboard` once BOTH checks pass. A storyboard that is "close" but drops planos or drifts in length is the reported bug; do not ship it.
