## Auto-Remesher | Blender Addon [WIP]

This remesher is to serve as a solution to the ugly mesh topology characteristic of current 3D generative technologies, such as TRELLIS or Sparc3D.
This is a remesher catered towards the common failures observed in the outputs produced by state-of-the-art mesh generation deep learning models.

As a proof of concept, Auto-Remesher is current offered as a Blender addon (when complete).


### Target Features

- Generate meshes from text or image prompts directly in Blender.
- Automatically detect intended creases in mesh, and define remeshing regions based on crease boundaries.
- Interactive quad-focused remeshing in detected regions with poly-count controls.


### Pipeline Flow [WIP]

1. Generate mesh with TRELLIS inside of Blender (or just upload a mesh).
2. Generate creases and extract topology regions implied by messy and dense crease boundaries.
3. User guided crease correction + region definition + edge-loop generation.
4. Resultant mesh is nice a clean.


### Advantages Over Other Remeshers [WIP]

- No remeshing pipeline exists that specifically addresses the topological issues of 3D generated meshes.
- Automated but artist friendly in usage and installation.
- Instant Meshes fail to repair holes in generated meshes.
- Most remeshers are closed source.