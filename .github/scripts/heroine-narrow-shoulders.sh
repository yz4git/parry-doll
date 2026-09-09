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

# Second visual-review pass: narrow the clavicle another step without changing gameplay endpoints.
replace('visual-src/heroine-rig.js',
" shoulderL:[-.275,1.96,0],elbowL:[-.455,1.48,.07],handL:[-.7,1,.2],shoulderR:[.275,1.96,0],elbowR:[.455,1.48,.07],handR:[.7,1,.2],",
" shoulderL:[-.255,1.96,0],elbowL:[-.44,1.48,.07],handL:[-.7,1,.2],shoulderR:[.255,1.96,0],elbowR:[.44,1.48,.07],handR:[.7,1,.2],",
'rest shoulder span v2')
replace('visual-src/heroine-rig.js',
"points['shoulder'+suffix]=points.chest.clone().addScaledVector(right,side*.275*s).addScaledVector(up,.015*s);points['hand'+suffix]=V(hand.p);points['elbow'+suffix]=solveJoint(points['shoulder'+suffix],points['hand'+suffix],V(elbow.p).addScaledVector(right,side*.095*s),.51*s,.51*s);",
"points['shoulder'+suffix]=points.chest.clone().addScaledVector(right,side*.255*s).addScaledVector(up,.012*s);points['hand'+suffix]=V(hand.p);points['elbow'+suffix]=solveJoint(points['shoulder'+suffix],points['hand'+suffix],V(elbow.p).addScaledVector(right,side*.080*s),.51*s,.51*s);",
'live shoulder span v2')

# Keep the continuous arm surface aligned with the narrower clavicle and soften deltoid bulk.
replace('tools/make-heroine-mesh.py',
"if kind=='arm':points=[np.array([side*.275,1.96,0]),np.array([side*.455,1.48,.07]),np.array([side*.7,1,.2])];boneNames=['shoulder'+suffix,'elbow'+suffix];radii=[.082,.075,.061,.073,.046]",
"if kind=='arm':points=[np.array([side*.255,1.96,0]),np.array([side*.44,1.48,.07]),np.array([side*.7,1,.2])];boneNames=['shoulder'+suffix,'elbow'+suffix];radii=[.077,.071,.060,.072,.045]",
'arm mesh shoulder span v2')

# Accessories were still reading wider than the skeleton in WebGL; reduce them independently.
replace('visual-src/heroine.js',
"if(names.includes('shoulder')){a.add('cylinder',silver,[0,.25,0],[width*.90,.04,width*.84]);a.add('plate',white,[0,.08,.46],[.40,.34,.12],[.05,0,0],'porcelain');}",
"if(names.includes('shoulder')){a.add('cylinder',silver,[0,.25,0],[width*.82,.04,width*.78]);a.add('plate',white,[0,.07,.45],[.35,.31,.11],[.045,0,0],'porcelain');}",
'upper arm shoulder armor v2')
replace('visual-src/heroine.js',
"else if(n.name==='shoulder'){a.add('plate',white,[0,.23,-.05],[.52,.40,.48],[.22,0,0],'porcelain');a.add('plate',silver,[0,.22,.32],[.31,.21,.09]);}",
"else if(n.name==='shoulder'){a.add('plate',white,[0,.21,-.04],[.45,.36,.43],[.19,0,0],'porcelain');a.add('plate',silver,[0,.20,.31],[.27,.19,.085]);}",
'shoulder node armor v2')

# Tighten the decorative chest cap and side rails so the upper-body outline reads feminine, not armored-boxy.
replace('visual-src/heroine.js',
"for(const s of [-1,1]){a.add('box',black,[s*.53,.05,-.43],[.10,.83,.09],[0,0,-s*.12],'cloth');a.add('box',silver,[s*.55,.08,-.49],[.050,.3,.04]);a.add('plate',black,[s*.51,.32,.4],[.34,.28,.21],[0,s*.26,0],'cloth');a.add('box',silver,[s*.56,.19,.57],[.042,.38,.04],[0,0,-s*.19]);}",
"for(const s of [-1,1]){a.add('box',black,[s*.49,.05,-.43],[.095,.82,.085],[0,0,-s*.10],'cloth');a.add('box',silver,[s*.51,.08,-.49],[.047,.29,.038]);a.add('plate',black,[s*.47,.31,.4],[.30,.27,.20],[0,s*.23,0],'cloth');a.add('box',silver,[s*.52,.18,.57],[.040,.36,.038],[0,0,-s*.17]);}",
'torso side rails v2')
replace('visual-src/heroine.js',
"else if(n.name==='chest'){a.add('sphere',black,[0,0,0],[.68,.33,.49],[0,0,0],'cloth');a.add('ring',silver,[0,.26,0],[.37,.37,.37],[Math.PI/2,0,0]);}",
"else if(n.name==='chest'){a.add('sphere',black,[0,0,0],[.61,.32,.47],[0,0,0],'cloth');a.add('ring',silver,[0,.25,0],[.34,.34,.34],[Math.PI/2,0,0]);}",
'chest cap width v2')
PY

python3 tools/make-heroine-mesh.py

cd visual-src
npm ci --no-audit --no-fund
npm run build
cd ..

node --check dist/game.js
node --check dist/visual-engine.js

python3 - <<'PY'
from pathlib import Path
rig=Path('visual-src/heroine-rig.js').read_text()
hero=Path('visual-src/heroine.js').read_text()
mesh=Path('tools/make-heroine-mesh.py').read_text()
assert "shoulderL:[-.255" in rig and "shoulderR:[.255" in rig
assert "side*.255*s" in rig
assert "side*.255,1.96" in mesh
assert "[.45,.36,.43]" in hero
assert "width*.82" in hero
assert "[.61,.32,.47]" in hero
print('PASS: heroine narrow-shoulder v2 silhouette anchors')
PY

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add visual-src/heroine-rig.js visual-src/heroine.js visual-src/heroine-mesh-data.js tools/make-heroine-mesh.py dist/visual-engine.js
if git diff --cached --quiet; then
  echo 'No heroine shoulder v2 changes to commit.'
else
  git commit -m 'feat: further refine heroine shoulder silhouette'
  git push origin HEAD:main
fi
