#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path

def rep(path,old,new,label):
 p=Path(path);s=p.read_text()
 if new in s:return
 if old not in s:raise SystemExit(f'{label}: anchor missing')
 p.write_text(s.replace(old,new))

rep('dist/visual-upgrade.js',
"function modelViewerTarget(){\n  const nodes=player?.nodes||[],head=nodes.find(n=>n.name==='head')?.p,chest=nodes.find(n=>n.name==='chest')?.p,hip=nodes.find(n=>n.name==='hip')?.p,feet=nodes.filter(n=>n.name==='foot').map(n=>n.p);\n  const fallback=player?.pos||v(0,0,0),minFoot=feet.length?feet.reduce((a,b)=>a.y<b.y?a:b):fallback;",
"function modelViewerTarget(d=player){\n  const nodes=d?.nodes||[],head=nodes.find(n=>n.name==='head')?.p,chest=nodes.find(n=>n.name==='chest')?.p,hip=nodes.find(n=>n.name==='hip')?.p,feet=nodes.filter(n=>n.name==='foot').map(n=>n.p);\n  const fallback=d?.pos||v(0,0,0),minFoot=feet.length?feet.reduce((a,b)=>a.y<b.y?a:b):fallback;",
'viewer target doll')
rep('dist/visual-upgrade.js',
"function modelViewerCamera(){\n  const target=modelViewerTarget(),s=modelViewerScale()",
"function modelViewerCamera(d=player){\n  const target=modelViewerTarget(d),s=modelViewerScale()",
'viewer camera doll')
rep('dist/visual-upgrade.js',
"const view=modelViewerCamera(),visualPlayer=proxyFor(player),visualBoss=proxyFor(boss);",
"const visualPlayer=proxyFor(player),visualBoss=proxyFor(boss),view=modelViewerCamera(visualPlayer);",
'viewer proxy camera')

rep('dist/model-viewer.js',
"#modelViewerOpen{margin-top:10px;width:100%;border:1px solid rgba(210,236,246,.34);background:rgba(11,22,31,.58);color:#eaf8ff;padding:12px 16px;font:600 12px/1.1 system-ui;letter-spacing:.18em;border-radius:3px;backdrop-filter:blur(10px)}",
"#modelViewerOpen{position:fixed;z-index:60;right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom));width:auto;margin:0;border:1px solid rgba(210,236,246,.38);background:rgba(11,22,31,.72);color:#eaf8ff;padding:10px 14px;font:600 11px/1.05 system-ui;letter-spacing:.16em;border-radius:3px;backdrop-filter:blur(12px);box-shadow:0 8px 26px rgba(0,0,0,.22)}",
'viewer title entry')
rep('dist/model-viewer.js',
"const gesture=$('modelViewerGesture'),hidden=['header','bossHud','playerHud','controls','cue','toast'].map(id=>$(id)).filter(Boolean);let savedOverlay='',pointers=new Map(),single=null,pinch=null;",
"const gesture=$('modelViewerGesture'),hidden=[document.querySelector('header'),...['bossHud','playerHud','controls','cue','toast','parrySuccessHud'].map(id=>$(id))].filter(Boolean);let savedOverlay='',pointers=new Map(),single=null,pinch=null;",
'viewer hud hiding')
PY
node --check dist/visual-upgrade.js
node --check dist/model-viewer.js
python3 - <<'PY'
from pathlib import Path
v=Path('dist/visual-upgrade.js').read_text();u=Path('dist/model-viewer.js').read_text()
assert 'modelViewerCamera(visualPlayer)' in v
assert 'function modelViewerTarget(d=player)' in v
assert "document.querySelector('header')" in u
assert '#modelViewerOpen{position:fixed' in u
print('PASS: model viewer framing and UI polish')
PY
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add dist/visual-upgrade.js dist/model-viewer.js
if git diff --cached --quiet; then
 echo 'No model viewer polish changes.'
else
 git commit -m 'fix: polish model viewer framing and UI'
 git push origin HEAD:main
fi
