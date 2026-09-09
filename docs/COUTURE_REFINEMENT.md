# Rear silhouette refinement

Baseline: 7ebfeeae91c52b6394cd19a1fa161adb775805bc.

The paired, beveled white rear plates were replaced with one connected A-line wrap skirt. Its rear hem is level and has no central split or paired lobes. Python bakes the shallow pleats and panel topology; a separate inward-facing dark lining makes the edge read as thin fabric. The front remains open over the existing black underlayer.

A charcoal hem, woven seams, fitted waist hardware and smaller belt loops define the clothing. The old hanging hip armor was removed. Thirteen finer ponytail locks replace nine thicker strands. Cloth movement is limited to the lower hem and does not affect the simulation.

Source assets and the runtime bundle are saved together. All gameplay, rig and camera behavior is preserved. Blender is unavailable; Python and Three.js provide the editable mesh workflow.

Post-integration checks: 1,200 model frames across four enemy rigs passed, including finite skinned vertices, preserved wrist/ankle endpoints, normalized weights, outward skirt faces, a fixed waist attachment, and a level hem. Existing gameplay scripts and the anatomical rig are byte-identical to the baseline. Actual iPhone/WebGL rendering and performance were not tested.

## Split combat-skirt silhouette pass
The continuous rear wrap was replaced by a high-waist rigid yoke with four independently animated panels. Two narrow rear panels sweep outward and leave a deliberate centre gap, preventing the old paired-lobe silhouette while extending vertical lines down the legs. Two short lateral panels frame the upper thigh without covering the front stride. Only the panel lengths receive secondary motion; the waist remains fixed to the pelvis.

## WebGL silhouette review pass
A real WebGL gameplay capture showed that four hanging panels read as rigid black tabs around the hips. The design was simplified to a thinner raised yoke and two narrow, outward-swept spear panels with tapered tips. This keeps the centre line and upper thighs open, improves the long-leg read, and removes the X-shaped rear cluster. Secondary motion was reduced so the panels trail cleanly instead of behaving like loose armor.

## High-cut waist finish
The second WebGL pass removed the four-tab clutter but made the rear spears too subtle and left a strong horizontal waist ring. The final silhouette pass uses a sculpted high-cut yoke whose lower edge rises over the outer hips, a slimmer curved metal trim, and two slightly broader pale rear spears that remain clearly separated and strongly tapered. The result keeps the legs visually uninterrupted while preserving a readable piece of moving cloth behind the character.
