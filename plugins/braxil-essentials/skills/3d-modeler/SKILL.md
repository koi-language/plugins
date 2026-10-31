---
name: 3d-modeler
description: "MANDATORY before build_model3d. Models ONE object (a specific car, a boat, a machine, a piece of furniture, a landmark) or ONE set (a street, a room, a circuit, a square) in Blender for the 3D previz, so it has the SAME proportions as its reference photos and reads at a glance as what it is. Use it when the previz needs a specific object or place that the scene-3d library shapes / groups cannot reproduce faithfully — above all when there are reference photos (location photos, a character's vehicle, a product). Triggers (any language): \"modela\", \"modelo 3D\", \"que se parezca a la foto\", \"como en la foto\", \"más realista el coche / el sitio\", build_model3d, get_model3d."
---

# 3D modeler (build_model3d)

You model in **Blender Python**: you write a script, `build_model3d` runs it
in a clean Blender, exports the result as `.glb` and returns a review you
LOOK at and correct against. It runs locally: free, a few seconds per build.
**Never ask the user for permission to model:** it costs nothing, so when the
previz needs a model, build it and say what you are doing.

## What matters, in this order

1. **Proportions identical to the photos.** Overall length : width : height,
   where every part starts and ends, the size of each part relative to the
   others. This is what the review checks first.
2. **It reads at once as what it is**, and as THAT one (this car, not a car):
   every telling part present with its real shape: a Formula 1 has its
   needle nose, front and rear wings with endplates, sidepods, airbox, halo,
   exposed wheels; a building has its storeys, windows, balconies, roof line.
3. **Colours and materials** that identify it (livery, facade colour, glass,
   chrome, rubber).

Detail is NOT a goal. Model the parts that make it recognisable and keep
the silhouette right; skip bolts, panel gaps, textures, logos. Never model
SURFACE marks as geometry or colour: weathered patches, stains, cracks,
painted lines, tile or plank patterns, dirt. A surface is ONE flat colour.
The video model copies whatever pattern the previz shows. Typical
budget: an object 2k–30k triangles, a set up to ~150k.

## Workflow

1. **Reuse first:** `get_model3d` (list, or by `locationId`). If the object or
   place is already modeled, use it; rebuild only on new references.
2. **Read every reference photo** (the location's photos / plate, the
   storyboard references, the photos the user gave). From them write down,
   as constants at the top of the script, the real dimensions of the whole
   and of every telling part. Anchor them on a known real size (F1 car
   5.6 × 2.0 × 0.95 m, wheel Ø 0.72 m; saloon car 4.5 × 1.8 × 1.45; door
   2.05 m; storey 3–3.5 m; person 1.75 m; lane 3.5 m; kerb 0.15 m) and
   derive the rest by measuring ratios in the photo (pixels of part / pixels
   of the anchor, corrected for perspective).
3. **Estimate each photo's camera** in the model's frame, and pass it with
   the photo in `references`:
   - `lens` from the field of view: phone main camera ≈ 26 mm, normal ≈ 35–50,
     strong compression (background huge behind the subject) ≈ 85–200.
   - Height: where the horizon line crosses the subject (the horizon is at
     the camera's height); eye level ≈ 1.6 m, trackside photographers ≈ 1 m.
   - Pitch: horizon in the middle of the frame = level camera.
   - `position` / `target` from where the subject sits in frame and how big
     it looks for that lens (distance ≈ real size × focal / (frame size on
     the 36 mm sensor)).
4. **Write the script** (see "Script contract"). Block the main volumes first
   at the measured sizes, then the telling parts.
5. **`build_model3d`** with `name`, `kind`, `script` (or `scriptFile`) and
   `references`. ALWAYS pass `name` (what it is, in the user's language:
   "Coche de F1", "Fachada de la juguetería") and a one-line `description`
   of what THIS build does ("Bloqueo de volúmenes a escala real",
   "Alerón delantero más ancho, morro más bajo"), on every rebuild too: the
   user sees them on the progress card, it is how they follow the work.
   LOOK at every attached image:
   - turnaround (objects: front / side / back / three-quarter; sets: three
     corners + top): proportions and that it reads as what it is;
   - per photo: `[photo | model from the photo camera | blend]`. In the blend
     the model must sit ON the photo, outline over outline.
   - Whole model off the same way (shifted, larger, smaller, tilted) → the
     **camera** estimate is wrong: fix the camera, not the model.
   - One part off → fix that part's numbers in the script.
6. **Iterate**: rebuild with the same `id` and the corrected `script` (or edit
   the returned `model.script` file and call `build_model3d { id }`, which
   rebuilds from it). Repeat until the blend matches (outline errors of a
   few percent), up to ~5 rounds. Say what still differs if you stop.
7. **Use it** in the scene: a prop `{ shape: "racecar", model: "<id>", … }`
   (keep the closest library `shape` as fallback; the model replaces it, at
   its modeled size; `size` scales it uniformly), or `set.model: "<id>"`
   (replaces the procedural floor / walls / ceiling). Pass `locationId` when
   the set is a saved location, so every scene there reuses it.

## Script contract

- Clean scene. Your script creates the geometry; cameras and lights it makes
  are dropped. Modifiers are applied on export (bevel, mirror, subdivision,
  solidify… are fine).
- Units: metres. Axes: x right, **y forward: the object's FRONT faces +y**
  (vehicles: nose at +y), z up.
- `kind: "object"`: modeled anywhere; it is re-centred on x/y with its
  bottom at z = 0 (the reference cameras move with it). Your cameras must be
  in the same frame you modeled in.
- `kind: "set"`: authored in SCENE coordinates (floor at z = 0, the playable
  area around the origin, y towards the back) and NOT moved. Include the
  ground. Exterior ground ≥ 80 × 80 m so no edge shows.
- Available names: `bpy`, `bmesh`, `math`, `Vector`, `Matrix`, `KIND`,
  `REF_CAMS` (the reference cameras: `[{obj, path, w, h}]`), and:
  - `pbr(name, color="#hex", rough=0.5, metal=0.0, coat=0.0,
    transmission=0.0, ior=1.45, emission=None, emission_strength=3.0,
    alpha=1.0)` → a material that survives the export exactly. Car paint:
    `rough=0.3, coat=1`; chrome: `metal=1, rough=0.15`; glass:
    `transmission=1, rough=0.05` or dark `#1a1f24, rough=0.1`; rubber:
    `#151515, rough=0.85`; carbon: `#1e2125, rough=0.35`.
  - `assign(obj, mat)` → gives a mesh exactly that material.
- Use only scalar material inputs (no textures, no node graphs): the export
  keeps those.

### Building shapes that read

- **Side profiles** for anything streamlined (car bodies, noses, hulls): a
  closed outline of `(y, z)` points from the photo, extruded across x with
  bmesh, a bevel modifier on the edges and smooth shading. Narrow the top
  (tumblehome) by scaling the upper vertices in x.
- **Mirror** symmetric objects: model one half, `MIRROR` modifier on x.
- **Revolve** round parts (wheels, tyres, rims, columns, lamps) with
  `bmesh.ops.spin` or cylinders; a tyre is a torus-like ring, a rim a
  lighter disc inset in it.
- **Thin parts** (wings, endplates, fins, railings, awnings) as thin boxes or
  `SOLIDIFY` planes: they carry the identity, never skip them.
- **Buildings / facades**: a box per volume; windows as dark inset boxes in
  rows at the measured spacing; balconies, cornices and the roof line as
  thin boxes. Background buildings: plain volumes with the right heights.
- Separate object per part, named (`front_wing`, `halo`, `facade_east`…).

```python
# Example skeleton (object)
L, W, H = 5.6, 2.0, 0.95          # measured
paint = pbr("paint", "#c8102e", 0.3, coat=1.0)
carbon = pbr("carbon", "#1e2125", 0.35)
tyre = pbr("tyre", "#151515", 0.85)

def profile(name, pts, width, mat, top=1.0, bevel=0.03):
    bm = bmesh.new()
    z0, z1 = min(z for _, z in pts), max(z for _, z in pts)
    vs = []
    for side in (-1, 1):
        for y, z in pts:
            k = 1 + (top - 1) * (z - z0) / max(1e-6, z1 - z0)
            vs.append(bm.verts.new((side * width * k / 2, y, z)))
    n = len(pts)
    bm.faces.new(vs[:n][::-1]); bm.faces.new(vs[n:])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vs[i], vs[j], vs[n + j], vs[n + i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    m = ob.modifiers.new("bevel", "BEVEL"); m.width = bevel; m.segments = 2
    assign(ob, mat)
    return ob

profile("chassis", [(2.78, 0.12), (1.6, 0.33), (0.45, 0.63), (-0.28, 0.99), (-2.32, 0.32), (-2.32, 0.1)], 0.62, paint, top=0.5)
```

## Hard rules

- Never call image / video generation to make a model: the model is built by
  your script.
- Never invent a shape when there is a photo: measure it.
- Characters are not modeled here (the previz uses mannequins).
- Internal text (script names, comments) in English.
