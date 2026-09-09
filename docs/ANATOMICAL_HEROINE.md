# Anatomical heroine

Baseline: 6337819ef1d1ee0c53a718d4e98be8a3de371040.

The heroine now uses an independent 17-bone render skeleton: pelvis, spine, chest, neck, head, shoulder/elbow/wrist chains, and hip/knee/ankle chains. The neutral rig uses a 1.38-unit pelvis and 2.29-unit head center, with a smaller adult face and narrow shoulders. It replaces radius-based doll proportions.

An analytic two-link IK solver preserves existing wrists and ankles. Extreme ragdoll poses allow measured limb extension so hands never disconnect from the sword. The original physics skeleton, camera, range, hit detection and timing are unchanged.

Python/NumPy authors a continuous 9,692-triangle costume mesh with skin indices and normalized joint weights. Three.js skins the mesh; sculpted face geometry, layered hair, fingers, armor, and flexible coat tails provide detail. Hair inertia and cloth deformation read render time only. Blender is not installed in this environment.

Each implementation slice was saved to GitHub before main integration. Checks and any resulting corrections follow main integration.
