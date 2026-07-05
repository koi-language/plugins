---
name: flight-path-to-video
description: "Use this skill whenever the user has an image — JUST uploaded OR the active/open document — with a sketched red line, arrow, or path drawn on it, and wants to turn that route into an AI VIDEO (or a video prompt) that follows it: a drone flight path, camera move, object trajectory, character route, or FPV flight. The drawn line is the camera/subject trajectory. If the user pairs a drawn red line/arrow/path with ANY 'make a video / animate / genera un vídeo' request, activate this — even if they never say 'drone'. Triggers (ES + EN): sigue la línea roja, siguiendo la línea, sigue la trayectoria, sigue la ruta, sigue el camino, la flecha que dibujé, la línea que pinté, haz un vídeo siguiendo la línea/ruta, vídeo que siga el trazo, ruta de vuelo, trayectoria de cámara, recorrido de cámara; red line, follow the path, follow the arrow, follow the route, drawn path, sketched line, flight path, camera path, FPV flight, drone path."
---

## Core Principle

The red path is a **director's instruction to Claude**, not a visual element. It defines the motion trajectory. The final prompt must:

1. Follow the path faithfully (start point → waypoints → end point)
2. **Explicitly instruct the model to remove all path annotations** from the final output
3. Read as clean, professional cinematic direction — no map language, no "follow the red arrow"

---

## Workflow

### Step 1 — Analyze the reference image

Study the uploaded image carefully and extract:

**The scene:**
- What environment is depicted? (city, nature, stadium, fantasy, interior, etc.)
- Visual register — photorealistic, CGI render, animated, painterly fantasy, noir, sci-fi (this determines the Style line later)
- Perspective: aerial/top-down, ground-level, isometric, or mixed?
- Time of day, lighting mood, and dominant colour palette
- Key landmarks, structures, or visual anchors visible along the path

**The path:**
- Where does it **start**? (describe the location within the image — e.g. "lower-left corner near the canal bridge", "ground level at the base of the tower")
- Where does it **end**? (describe the end position and implied camera height/angle)
- What happens **in between**? (Does it spiral, curve, thread through gaps, ascend, descend, bank around a corner?)
- How many distinct **waypoints** or sections does it have?
- What is the **implied motion style**? (A tight spiral = ascending drone. A sweeping S-curve = FPV banking. A straight line from ground to sky = crane reveal.)
- What is the **implied speed**? (Short video at high coverage = fast/dynamic. Leisurely curve = slow and cinematic.)

If no image is uploaded, ask the user to upload one. **The reference image is mandatory.**

---

### Step 2 — Gather the brief

Collect any missing context in a **single message** (don't ask multiple times):

1. **Duration** — how long should the video be? (Default: 15 seconds)
2. **Guide character** — optional. Does the user want a character or object leading the camera? (e.g. a bird, a fairy, a vehicle)
3. **Any specific constraints** — style, camera behaviour, atmosphere, character rules

If the user has provided this inline, skip the questions and proceed.

---

### Step 3 — Classify the visual register

Before writing, identify which visual register the reference image belongs to. This governs the Style line and the tone of the motion description language:

| Visual Register | Image Signals | Style Line | Motion Language |
|---|---|---|---|
| **Photorealistic / cinematic** | Real photography, natural lighting | `Deep focus, practical lighting. High contrast, grounded realism.` | Grounded, observational, documentary-precise |
| **CGI / rendered realism** | 3D render feel, hyper-clean surfaces | `Deep focus, practical lighting. High contrast, cinematic CGI realism.` | Polished, precise, technically smooth |
| **Animated / stylised** | Flat colour, toon shading, exaggerated proportions | `Deep focus, stylised animation. Bold colour contrast, graphic clarity.` | Expressive, fluid, character-driven |
| **Painterly / fantasy** | Hand-painted feel, impressionistic detail | `Painterly depth, soft atmospheric perspective. Rich tonal range.` | Lyrical, floating, organic |
| **Noir / stylised realism** | High contrast, desaturated, graphic shadow | `Deep focus, high contrast noir. Stylised shadow and silhouette.` | Sharp, deliberate, tension-driven |

---

### Step 4 — Write the prompt

Use the following structure. Every section is required.

---

**PROMPT TEMPLATE:**

```
Use the uploaded image as a [route-planning terrain map / aerial reference / ground-level scene guide]. The [red line / sketched path / drawn arrow] is only a camera path reference and must be completely removed from the final video — no lines, arrows, annotations, or overlays of any kind should appear at any point.

Create a [DURATION]-second [single continuous / segmented] [16:9 / cinematic widescreen] [FPV flight / drone arc / camera move / character path] through [brief scene description].

[If segmented, add timing breakdown:]
Follow this route in this exact order: [0s → Ns → Ns → Ns → END]. The movement must feel like one continuous [flight / move / track], not a jump between landmarks.

Route:
Start: [Describe starting position from the image — location, height, angle]
[Waypoint 1 at Ns]: [What happens here — direction change, speed shift, subject interaction]
[Waypoint 2 at Ns]: [What happens here]
[Endpoint at Ns]: [Final position, framing, and closing beat — e.g. push-in, wide reveal, slow settle]

[If a guide character is used:]
Guide character: [Description of character or object leading the camera — species, size, movement style]

Environment:
[2–4 sentences describing the world — architectural details, surface materials, lighting, atmosphere, time of day. Match the visual register of the reference image exactly. Do not describe elements not visible in the image unless stylistically implied.]

Camera Motion:
[2–3 sentences describing the camera behaviour — speed, banking, smoothness, altitude, parallax, any slow-motion beats. Reference the specific path sections: "opens low on the approach...", "banks hard around the corner...", "settles into a slow push at the end..."]

Visual Progression:
[2–3 sentences describing how the shot changes emotionally or compositionally from start to finish — what the viewer discovers, how scale shifts, where the energy peaks]

Avoid: [list of specific exclusions — visible path/line/overlay, cuts, watermarks, any visual elements absent from the reference, any style inconsistencies, any prohibited camera behaviours]

Style: [Style line from the visual register table above]
Audio: Diegetic sound only — natural ambience, environmental foley, and subject-driven sound.
```

---

### Step 5 — Review the prompt against the path

Before delivering, run a mental walkthrough:

- Does the starting position match where the path begins in the image?
- Are all major bends, spirals, or direction changes accounted for as waypoints?
- Does the endpoint describe both a position *and* a closing camera action?
- Is the path erasure instruction clearly stated at the top?
- Is the motion language consistent with the visual register classification?
- Are there any map or annotation terms in the prompt? (Remove them if so.)

---

### Step 6 — Review the prompt against the path

Use the prompt to generate a video with it. The prompt to create the video will be a clean copy-paste block with no surrounding explanation unless the user asks for it. After the prompt block, optionally add a brief note (2–3 sentences max) on key creative decisions — especially if you made interpretive choices about path speed, waypoints, or the closing beat that the user might want to override.

## Output

The output will be the generated video.

---

## Style Reference Table (Quick Lookup)

| Visual Register | Style Line |
|---|---|
| Photorealistic / cinematic | `Deep focus, practical lighting. High contrast, grounded realism.` |
| CGI / rendered realism | `Deep focus, practical lighting. High contrast, cinematic CGI realism.` |
| Animated / stylised | `Deep focus, stylised animation. Bold colour contrast, graphic clarity.` |
| Painterly / fantasy | `Painterly depth, soft atmospheric perspective. Rich tonal range.` |
| Noir / stylised realism | `Deep focus, high contrast noir. Stylised shadow and silhouette.` |

---

## Worked Examples

### Example 1 — Photorealistic aerial spiral (Leaning Tower of Pisa)

```
Use the uploaded image as a route-planning terrain map. The red line is only a sketched camera path and must be completely removed from the final video — no lines, arrows, pins, or overlays should be visible at any point.

Create a smooth, cinematic 15-second aerial video using the exact reference image as the visual base. DJI Mavic drone camera style with realistic drone cinematography.

Route:
Start: Ground level near the base of the Leaning Tower of Pisa, on the grassy area — low altitude, establishing the tower's base and lean.
Waypoints: Continuous ascending spiral circling the tower — smoothly rising, maintaining a close-to-medium distance from the tower, gradually revealing full height and architectural detail as it climbs.
Endpoint at 15s: Elevated high above the tower, looking out over the historic city of Pisa — red-roofed buildings, cathedral dome, surrounding landscape visible.

Environment:
Historic cathedral square, Piazza dei Miracoli. White marble Romanesque architecture. Natural daylight, clear blue sky, warm late-morning light. Green manicured grass, tourists visible at ground level diminishing in scale as the camera rises.

Camera Motion:
Steady, cinematic, professional drone tracking. Smooth spiral ascent with natural parallax — the tower rotates slowly in frame as the camera circles it. Gentle forward tracking and slight dynamic banking on the circular path. Smooth acceleration from ground level upward. No abrupt direction changes.

Visual Progression:
Opens close and grounded — the tower's lean and stonework fill the frame. Pulls back and upward as the spiral widens, revealing the full tower height and its famous tilt. Ends with the tower small against the expanse of the city and sky — scale fully revealed.

Avoid: visible red arrows, path lines, pins, text, or any overlays at any point. No cuts. No camera rising without maintaining tower proximity until the final elevation. No desaturated or stylised rendering.

Style: Deep focus, practical lighting. High contrast, grounded realism.
Audio: Diegetic sound only — natural ambience, wind, distant crowds.
```

---

### Example 2 — FPV flight through fantasy city (Alice in Wonderland-inspired)

```
Use the uploaded image as a route-planning terrain map. The red line is only a sketched camera path and must be completely removed from the final video — no lines, arrows, annotations, or overlays of any kind should appear.

Create a 15-second single continuous 16:9 cinematic FPV flight through the same Alice in Wonderland-inspired fantasy downtown. No cuts. Invisible first-person drone camera only.

Follow this route in this exact order: 0s → 3s → 6s → 9s → 12s → 15s. The movement must feel like one continuous forward flight, not a jump between landmarks.

Route:
Start at 0s: [Starting position from image — low street level, facing the main boulevard]
3s: [First waypoint — threading between the giant mushroom columns]
6s: [Banking around the clock tower with the oversized face]
9s: [Threading through the market archways, low and fast]
12s: [Rising above the rooftops — the full city sprawl becomes visible]
Endpoint at 15s: Hovering still above the central plaza — held for one beat before the shot ends.

Environment:
[Describe from reference image]

Camera Motion:
[Describe from reference image path]

Visual Progression:
[Describe from reference image]

Avoid: visible blue line, visible arrows, path overlays, annotations, subtitles, text, logos, watermarks, cuts, camera rising too high too early, environment rendered photorealistically if stylised in reference.

Style: Deep focus, stylised animation. Bold colour contrast, graphic clarity.
Audio: Diegetic sound only — natural ambience, environmental foley, subject-driven sound.
```

---

### Example 3 — Anime-style tennis court orbit

```
Use the uploaded image as a route map. The sketched path line must be completely invisible in the final video — no overlays, annotations, or route markers of any kind.

Create a 15-second single continuous cinematic low drone arc through the same clay tennis court scene. No cuts. Fluid FPV camera only.

Route:
Start: Near baseline, close to the clay surface — our player's impact fills the frame at the moment of a shot.
Arc: Pulls back and curves around the full perimeter of the court — sweeping wide around the far end behind the opponent, banking smoothly on each corner.
Endpoint at 15s: Arrives at centre court, low, pushing slowly toward the net — slow-motion hold on the net and ball hanging in the teal air.

Environment:
Clay tennis court rendered in bold anime art style. Deep terracotta red surface with crisp white court lines. Dark net across the centre. Vivid flat teal sky — saturated, graphic, no clouds. Bright hard sunlight casting sharp shadows on the clay. Bold anime outlines on all surfaces and characters. Manga speed lines on impact moments and fast ball movement. Clay dust and particles disturbed by footwork. No photorealistic elements — everything in the same unified stylised anime art style as the character reference.

Camera Motion:
Low cinematic drone arc throughout — staying close to the clay surface, never rising above player head height except briefly on corner banks. Fluid continuous motion from the near baseline around the full perimeter of the court to the centre push. Smooth banking on corners. Slow-motion hold at the final centre push. The court is the stage — the camera moves around it like a sports broadcast reimagined as anime cinematography.

Visual Progression:
Opens explosive and close — our player's impact fills the frame. Pulls back as the arc widens to show the full court and both players. Tightens again as the camera rounds the far end behind the opponent. Ends low and central — the net and the ball the final image, hanging in the teal air.

Avoid: visible blue line, visible arrows, path overlays, annotations, subtitles, text, logos, watermarks, cuts, camera rising too high above court level, court rendered photorealistically, teal sky rendered as photorealistic sky, character design inconsistent with reference image, manga speed lines absent on impact moments, clay dust absent on footwork, ball absent from flight, slow-motion final beat absent.

Style: Deep focus, stylised anime art. Vivid saturated colour, bold outlines, graphic contrast, teal sky.
Audio: Diegetic sound only — natural ambience, environmental foley, and subject-driven sound.
```

---

## Notes

- The path erasure instruction is non-negotiable. It must appear at the top of every prompt, before the creative direction. This is what prevents the model from rendering the sketch as a visual element.
- Waypoint timing is approximate guidance, not hard timestamps. Frame them as motion phases rather than exact cuts — the model interprets pacing from context, not millisecond precision.
- When the path implies speed, encode that in the Camera Motion block rather than in the route description. "Opens fast and low, gradually decelerating into the final reveal" is more useful than "fast at waypoint 1, slow at endpoint."
- If the user's reference image is very low-fidelity (a quick phone sketch), interpret generously. The path intent matters more than precise pixel accuracy.
