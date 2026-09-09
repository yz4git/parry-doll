# Core heroine model rebuild

Baseline: 1116dc9bb0aef89bc2581e3b00e1f0ba78f14c86.

Scope follows the user steering: body, face, hair and proportions. Existing costume panels and decoration are retained; no new costume design was added. Existing combat, camera, input and anatomical rig endpoints remain unchanged.

- Python/SciPy monotone profiles replace cylindrical torso and limb sections with smooth chest, waist, pelvic, thigh, knee and calf contours. The weighted body has 16,784 triangles.
- Python bakes a 3,185-vertex adult head with jaw, cheek, orbital and nasal volumes. Separate curved almond eyes, lids and lips follow the facial surface.
- Layered hair sheets replace tube strands: a fitted scalp cap, swept bangs, face-framing locks and a high ponytail. A deterministic Pillow/NumPy alpha map supplies finer strand edges.
- Skin and hair shading were refined. Clothing geometry is unchanged apart from removal of thigh plates that hid the leg contour.

Verification after main integration: 1,200 frames across four enemies passed with finite geometry and skinned positions, normalized weights, preserved wrist/ankle positions, and no mutation of supplied simulation data. Offline mesh inspections covered the full body and face; these approximate material appearance and are not WebGL screenshots. Actual iPhone rendering/performance remains untested. The supplied cinematic image is the modeling reference, not a claim of equal fidelity.
