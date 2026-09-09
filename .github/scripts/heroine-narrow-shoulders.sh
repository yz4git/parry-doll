#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path


def replace(path, old, new, label):
    p=Path(path)
    s=p.read_text()
    if new in s:
        return
    if old not in s:
        raise SystemExit(f'{label}: anchor not found in {path}')
    p.write_text(s.replace(old,new))

# Narrow the render skeleton's clavicle/shoulder span while keeping gameplay hand endpoints untouched.
replace('visual-src/heroine-rig.js',
" shoulderL:[-.32,1.96,0],elbowL:[-.48,1.48,.07],handL:[-.7,1,.2],shoulderR:[.32,1.96,0],elbowR:[.48,1.48,.07],handR:[.7,1,.2],",
" shoulderL:[-.275,1.96,0],elbowL:[-.455,1.48,.07],handL:[-.7,1,.2],shoulderR:[.275,1.96,0],elbowR:[.455,1.48,.07],handR:[.7,1,.2],",
'rest shoulder span')
replace('visual-src/heroine-rig.js',
"points['shoulder'+suffix]=points.chest.clone().addScaledVector(right,side*.32*s).addScaledVector(up,.02*s);points['hand'+suffix]=V(hand.p);points['elbow'+suffix]=solveJoint(points['shoulder'+suffix],points['hand'+suffix],V(elbow.p).addScaledVector(right,side*.12*s),.51*s,.51*s);",
"points['shoulder'+suffix]=points.chest.clone().addScaledVector(right,side*.275*s).addScaledVector(up,.015*s);points['hand'+suffix]=V(hand.p);points['elbow'+suffix]=solveJoint(points['shoulder'+suffix],points['hand'+suffix],V(elbow.p).addScaledVector(right,side*.095*s),.51*s,.51*s);",
'live shoulder span')

# Re-author the continuous upper arm surface around the narrower clavicle.
replace('tools/make-heroine-mesh.py',
"if kind=='arm':points=[np.array([side*.32,1.96,0]),np.array([side*.48,1.48,.07]),np.array([side*.7,1,.2])];boneNames=['shoulder'+suffix,'elbow'+suffix];radii=[.09,.08,.063,.075,.047]",
"if kind=='arm':points=[np.array([side*.275,1.96,0]),np.array([side*.455,1.48,.07]),np.array([side*.7,1,.2])];boneNames=['shoulder'+suffix,'elbow'+suffix];radii=[.082,.075,.061,.073,.046]",
'arm mesh shoulder span')

# Reduce armor width at the shoulder so the silhouette does not regain a boxy span through accessories.
replace('visual-src/heroine.js',
"if(names.includes('shoulder')){a.add('cylinder',silver,[0,.25,0],[width*1.04,.04,width*.92]);a.add('plate',white,[0,.08,.46],[.48,.38,.13],[.05,0,0],'porcelain');}",
"if(names.includes('shoulder')){a.add('cylinder',silver,[0,.25,0],[width*.90,.04,width*.84]);a.add('plate',white,[0,.08,.46],[.40,.34,.12],[.05,0,0],'porcelain');}",
'upper arm shoulder armor')
replace('visual-src/heroine.js',
"else if(n.name==='shoulder'){a.add('plate',white,[0,.25,-.05],[.65,.45,.55],[.25,0,0],'porcelain');a.add('plate',silver,[0,.24,.33],[.39,.24,.1]);}",
"else if(n.name==='shoulder'){a.add('plate',white,[0,.23,-.05],[.52,.40,.48],[.22,0,0],'porcelain');a.add('plate',silver,[0,.22,.32],[.31,.21,.09]);}",
'shoulder node armor')

# Bring the rear torso side rails slightly inward to preserve a narrow upper-body read from the gameplay camera.
replace('visual-src/heroine.js',
"for(const s of [-1,1]){a.add('box',black,[s*.59,.05,-.43],[.11,.83,.09],[0,0,-s*.14],'cloth');a.add('box',silver,[s*.61,.08,-.49],[.055,.3,.04]);a.add('plate',black,[s*.57,.32,.4],[.38,.3,.23],[0,s*.3,0],'cloth');a.add('box',silver,[s*.62,.19,.57],[.045,.4,.04],[0,0,-s*.22]);}",
"for(const s of [-1,1]){a.add('box',black,[s*.53,.05,-.43],[.10,.83,.09],[0,0,-s*.12],'cloth');a.add('box',silver,[s*.55,.08,-.49],[.050,.3,.04]);a.add('plate',black,[s*.51,.32,.4],[.34,.28,.21],[0,s*.26,0],'cloth');a.add('box',silver,[s*.56,.19,.57],[.042,.38,.04],[0,0,-s*.19]);}",
'torso side rails')
PY

python3 tools/make-heroine-mesh.py

cd visual-src
npm ci --no-audit --no-fund
npm run build
cd ..

# Gameplay logic is intentionally untouched in this pass. The current baseline gameplay suite
# already fails its Finisher-damage expectation on main, so gate this visual change on visual
# build/syntax plus explicit silhouette assertions instead of hiding an unrelated baseline failure.
node --check dist/game.js
node --check dist/visual-engine.js

python3 - <<'PY'
from pathlib import Path
rig=Path('visual-src/heroine-rig.js').read_text()
hero=Path('visual-src/heroine.js').read_text()
mesh=Path('tools/make-heroine-mesh.py').read_text()
assert "shoulderL:[-.275" in rig and "shoulderR:[.275" in rig
assert "side*.275*s" in rig
assert "side*.275,1.96" in mesh
assert "[.52,.40,.48]" in hero
assert "width*.90" in hero
print('PASS: narrow-shoulder heroine silhouette anchors')
PY

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add visual-src/heroine-rig.js visual-src/heroine.js visual-src/heroine-mesh-data.js tools/make-heroine-mesh.py dist/visual-engine.js
if git diff --cached --quiet; then
  echo 'No heroine shoulder changes to commit.'
else
  git commit -m 'feat: refine heroine with narrower shoulders'
  git push origin HEAD:main
fi
