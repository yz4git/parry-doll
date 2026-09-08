# Reference-driven graphics pass

Base: 5b4861f516f62903075bf0293124b187bae13695.

- Render-only adult heroine: smaller face, layered dark ponytail, white coat tails, black underlayer, articulated silver gauntlets and boots.
- Mechanical enemies: exposed pistons, cooling slots, ring joints and emissive reactor cores.
- Sunlit limestone arena with Gothic arcades, spires, suspended ruins and floating islands.
- Python bakes the arch mesh and stone PBR maps. Three.js batches geometry and retains existing adaptive rendering quality. Blender is unavailable in this environment.
- Existing combat, control, camera and visual-proxy behavior is preserved; this pass changes model and environment source only. Hair and cloth motion read the existing render clock and velocity.
- The supplied image sets the art direction; these are lightweight procedural game models, not equivalent to its cinematic character fidelity.

Build: run the existing visual-src npm build after running tools/make-architecture.py and tools/make-materials.py.

## Checks after main integration

- `node tests/reference-models.mjs`: 1,200 frames over four enemy rigs, finite geometry/transforms, zero writes to supplied simulation data, local asset references pass.
- Gameplay scripts, rendering bridge, controls and camera code are byte-identical to base 5b4861f.
- Offline mesh inspection checked the assembled heroine and cathedral geometry; adjusted render-only hip height and shoulder width.
- Existing `tests/check.cjs` fails at its legacy `Finisher damage` expectation. It loads only unchanged game.js; the same failure occurs on the baseline and is not fixed by changing gameplay in this graphics task.
- Browser/WebGL output and actual iPhone performance have not been tested. Offline mesh rendering is not a browser screenshot.

