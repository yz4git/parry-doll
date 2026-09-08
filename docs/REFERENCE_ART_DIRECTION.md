# Reference-driven graphics pass

Base: 5b4861f516f62903075bf0293124b187bae13695.

- Render-only adult heroine: smaller face, layered dark ponytail, white coat tails, black underlayer, articulated silver gauntlets and boots.
- Mechanical enemies: exposed pistons, cooling slots, ring joints and emissive reactor cores.
- Sunlit limestone arena with Gothic arcades, spires, suspended ruins and floating islands.
- Python bakes the arch mesh and stone PBR maps. Three.js batches geometry and retains existing adaptive rendering quality. Blender is unavailable in this environment.
- Existing combat, control, camera and visual-proxy behavior is preserved; this pass changes model and environment source only. Hair and cloth motion read the existing render clock and velocity.
- The supplied image sets the art direction; these are lightweight procedural game models, not equivalent to its cinematic character fidelity.

Build: run the existing visual-src npm build after running tools/make-architecture.py and tools/make-materials.py.

Final checks are performed after main integration, as requested.
