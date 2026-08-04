---
name: screenwriting
description: >
  Professional screenwriting craft: develop and write screenplays, short-film scripts, video scripts, loglines, treatments, beat sheets and episode outlines with real dramatic structure (John Yorke's five-act model) and real cinema grammar (The Filmmaker's Handbook). Use whenever the user wants to WRITE or IMPROVE a script / guion / guión / screenplay / teleplay / "guion para un corto/video/pelicula", a treatment, a logline, a beat sheet / escaleta de guion, a story or plot for a film, series, short or ad, or asks for feedback/notes/doctoring on an existing script ("mejora este guion", "dale estructura", "why does my second act sag"). Also the craft library for ANY story development: premise, protagonist want/need, antagonist, midpoint, scene writing, dialogue, subtext, episode/series engines. If the user wants a multi-shot VIDEO produced, this skill owns only the HIGH-LEVEL story ARCHITECTURE — premise, five-act structure, sequences, the SCENE MAP (which scenes exist, their order, each scene's dramatic function/goal/location/characters) and the characters (bible, arcs, voice). It does NOT write the scenes themselves: in the video pipeline each scene — its `action`, its `dialogue`, and its planos — is written ENTIRELY by `cinematic-video-prompt-engineer`, which realises far more naturalistic scenes and dialogue than a page script. So for a video: this skill decides WHAT story and WHICH scenes; cinematic writes HOW each scene plays. The storyboard skill's rule 1a sends the high-level story here; rule 1b sends each scene to cinematic. (EXCEPTION — a STANDALONE screenplay/podcast/speech delivered as TEXT, not a video: there this skill writes the FULL script including scenes and dialogue, as classic screenwriting.)
---

## What this skill is

A working screenwriter's craft system distilled from two sources:

- **John Yorke, "Into the Woods"**: the five-act structure, want/need, the midpoint, the Roadmap of Change, fractal scene/act design, character, dialogue, exposition, subtext, TV/series structure.
- **The Filmmaker's Handbook (Ascher and Pincus)**: producibility only — page-per-minute timing and what survives the edit (see `production-craft.md`). This skill does NOT decide shots / framing / angle / camera / coverage / cuts: that shot design belongs to `cinematic-video-prompt-engineer`, the sole cinematography authority.

The craft lives in `references/`. Load ONLY what the current task needs:

| File | Load when |
|---|---|
| [references/story-structure.md](references/story-structure.md) | ALWAYS for new stories, restructuring, or diagnosis. The five-act shape, building blocks, midpoint, Roadmap of Change, mirroring, authoring checklist. |
| [references/scene-craft.md](references/scene-craft.md) | Writing or fixing individual scenes: beats, turning points, "come in late, get out early", showing not telling. |
| [references/character-dialogue-subtext.md](references/character-dialogue-subtext.md) | Creating characters, writing dialogue, hiding exposition, subtext problems, "my characters all sound the same". |
| [references/tv-and-series-structure.md](references/tv-and-series-structure.md) | Episodic work: series vs serial, story engines, season arcs, keeping a returning cast alive, theme. |
| [references/structure-worked-examples.md](references/structure-worked-examples.md) | Calibration: full act maps of Raiders, Hamlet, Being John Malkovich, The Godfather; act 1/5 mirrors; translating other gurus' vocabularies (Field, Snyder, McKee, Vogler...). |
| [references/production-craft.md](references/production-craft.md) | Practical producibility: page-per-minute timing, coverage planning, what survives the edit, scripts about film sets. |

## Workflow: writing a new script

1. **Scope the ask.** Format (feature, short, episode, ad, video script), rough length, tone, audience, and the user's language. One script page equals about one minute of screen time. If the user gave characters, world, or plot points, those are REQUIREMENTS: never alter them to fit the structure; bend the structure instead.
2. **Load `references/story-structure.md`** and develop, in this order:
   - Premise: "Once upon a time, something happened." What if...?
   - Protagonist with an ACTIVE, tangible want, and the flaw/need underneath it.
   - Antagonist as the embodiment of what the protagonist lacks.
   - The five-act roadmap: inciting incident (crisis of act 1), commitment (end of act 2), MIDPOINT (key knowledge, point of no return), worst point (act 4 crisis), climax and resolution mirroring act 1.
3. **Beat sheet / escaleta.** One line per scene: who wants what, who blocks it, what turns. Check the mirrors (act 1 vs act 5, act 2 vs act 4) and that every scene changes something.
4. **Write scenes** — **STANDALONE screenplay/text deliverable ONLY** — with `references/scene-craft.md` and `references/character-dialogue-subtext.md` loaded: in late, out early, action/reaction beats to an unexpected reaction, subtext over statement, exposition hidden in conflict. **For a produced VIDEO, STOP at the beat sheet / scene map (step 3): do NOT write the scenes or the dialogue — hand each scene to `cinematic-video-prompt-engineer`**, which writes the scene content and dialogue naturalistically.
5. **Self-check** against the authoring checklists at the end of story-structure.md and scene-craft.md before delivering.
6. **Deliver**: write the script to a file and open it with `show_result` (it appears in the user's work area); do not dump a whole screenplay into the chat. Standard screenplay conventions (sluglines, action, dialogue) unless the user wants another format. The script's content is ALWAYS in the user's language.

## Workflow: notes / doctoring an existing script

1. Read the whole script first. Never give notes from a skim.
2. Diagnose structurally before line-editing: find the inciting incident, midpoint, and worst point. Most "dialogue problems" are structure or character problems (Mercurio's rule). Map what exists onto the five acts and look for the missing or misplaced beat.
3. Check the fundamentals in order: protagonist want/need, antagonist strength ("a story is only as good as its counter-argument"), scene turning points, then dialogue and subtext last.
4. Give notes as: what works, the ONE structural problem that matters most, then targeted fixes. Reference the craft by name (midpoint, worst point, mirror) so the user learns the vocabulary.

## Hard rules

- Structure is a diagnostic, not a paint-by-numbers kit. Write dialectically; use the five acts to check and fix, not to fill in a template mechanically. Deliberate subversions of the archetype are legitimate and draw their power from it.
- Never alter the user's explicit creative requirements (style, characters, plot points, ending) to make structure "work". Propose; never silently replace.
- The user's language for all deliverable content. Craft vocabulary (midpoint, inciting incident) may stay in English if there is no natural translation.
- If the end goal is a produced VIDEO: this skill produces the HIGH-LEVEL story ONLY — premise, structure, sequences, the scene map and the characters. Do NOT write the scenes, the `action` or the `dialogue`, and do NOT design the planos: each scene is written ENTIRELY by `cinematic-video-prompt-engineer` (it renders more naturalistic scenes + dialogue than a page script). Do not hand-build storyboard JSON here, and do not substitute a script when the user asked for a storyboard (or vice versa; when ambiguous, ask).
