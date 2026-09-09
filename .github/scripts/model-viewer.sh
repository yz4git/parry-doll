#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

p=Path('dist/visual-upgrade.js')
s=p.read_text()

anchor="let quality='high',slowAccum=0,fastAccum=0,lastFrame=performance.now(),qualityLockUntil=0,visualExtra=0;"
insert="""let quality='high',slowAccum=0,fastAccum=0,lastFrame=performance.now(),qualityLockUntil=0,visualExtra=0;\n const modelViewer={active:false,preset:'full',yaw:-.46,pitch:.055,distance:4.65,auto:true,weapon:true,baseFace:0};\n function modelViewerScale(){return Math.max(.72,player?.spec?.scale||1)}\n function modelViewerPreset(name){const s=modelViewerScale();modelViewer.preset=name;if(name==='face'){modelViewer.distance=1.38*s;modelViewer.pitch=.015}else if(name==='upper'){modelViewer.distance=2.55*s;modelViewer.pitch=.035}else{modelViewer.distance=4.65*s;modelViewer.pitch=.055}return modelViewerState()}\n function modelViewerTarget(){\n  const nodes=player?.nodes||[],head=nodes.find(n=>n.name==='head')?.p,chest=nodes.find(n=>n.name==='chest')?.p,hip=nodes.find(n=>n.name==='hip')?.p,feet=nodes.filter(n=>n.name==='foot').map(n=>n.p);\n  const fallback=player?.pos||v(0,0,0),minFoot=feet.length?feet.reduce((a,b)=>a.y<b.y?a:b):fallback;\n  if(modelViewer.preset==='face'&&head)return v(head.x,head.y+.015*modelViewerScale(),head.z);\n  if(modelViewer.preset==='upper'&&head&&chest)return mixv(chest,head,.48);\n  if(head)return v(head.x,(head.y+minFoot.y)*.5+.10*modelViewerScale(),head.z);\n  return v(fallback.x,(fallback.y||0)+1.15*modelViewerScale(),fallback.z);\n }\n function modelViewerCamera(){\n  const target=modelViewerTarget(),s=modelViewerScale(),minD=.82*s,maxD=7.2*s;modelViewer.distance=Math.max(minD,Math.min(maxD,modelViewer.distance));modelViewer.pitch=Math.max(-.38,Math.min(.58,modelViewer.pitch));\n  const a=modelViewer.baseFace+modelViewer.yaw,h=Math.cos(modelViewer.pitch)*modelViewer.distance,cam=v(target.x+Math.sin(a)*h,target.y+Math.sin(modelViewer.pitch)*modelViewer.distance,target.z+Math.cos(a)*h),f=vn(subv(target,cam));\n  return{camera:cam,forward:f,up:v(0,1,0)};\n }\n function modelViewerState(){return{active:modelViewer.active,preset:modelViewer.preset,yaw:modelViewer.yaw,pitch:modelViewer.pitch,distance:modelViewer.distance,auto:modelViewer.auto,weapon:modelViewer.weapon,available}}\n function modelViewerOpen(){if(!available)return false;modelViewer.active=true;modelViewer.baseFace=player?.face||0;modelViewerPreset('full');modelViewer.yaw=-.46;modelViewer.auto=true;modelViewer.weapon=true;parrySuccessT=0;parryBurst=null;return true}\n function modelViewerClose(){modelViewer.active=false;if(scene?.actors?.[1]?.root)scene.actors[1].root.visible=true;if(scene?.actors?.[0]?.weapon)scene.actors[0].weapon.visible=true;return true}\n"""
if 'const modelViewer={active:false' not in s:
    if anchor not in s: raise SystemExit('quality anchor missing')
    s=s.replace(anchor,insert)

old="""render=function(){\n  if(!available)return baseRender();setCamera();const recoil=feel.reduced?0:shake,dt=Math.max(1/120,Math.min(.05,feel.dt||1/60));"""
new="""render=function(){\n  if(!available)return baseRender();\n  const dt=Math.max(1/120,Math.min(.05,feel.dt||1/60));\n  if(modelViewer.active){\n   try{\n    if(modelViewer.auto)modelViewer.yaw+=dt*.19;\n    const view=modelViewerCamera(),visualPlayer=proxyFor(player),visualBoss=proxyFor(boss);\n    visualPlayer.face=modelViewer.baseFace;visualPlayer.vel=v(0,0,0);visualPlayer.attack=0;visualPlayer.parry=0;visualPlayer.wind=0;visualPlayer.strike=0;visualPlayer.down=0;visualPlayer.stun=0;visualPlayer.hitRegionT=0;visualPlayer.motion=0;\n    if(scene.actors?.[1]?.root)scene.actors[1].root.visible=false;if(scene.actors?.[0]?.root)scene.actors[0].root.visible=true;if(scene.actors?.[0]?.weapon)scene.actors[0].weapon.visible=modelViewer.weapon;\n    ribbonMeshes.forEach(m=>m.visible=false);ribbonCoreMeshes.forEach(m=>m.visible=false);\n    scene.render({width:W,height:H,camera:view.camera,forward:view.forward,up:view.up,player:visualPlayer,boss:visualBoss,poses:[IDLE_POSE.blade,IDLE_POSE.blade],particles:[],clock:feel.clock,recoil:0});\n    if(scene.actors?.[1]?.root)scene.actors[1].root.visible=false;if(scene.actors?.[0]?.weapon)scene.actors[0].weapon.visible=modelViewer.weapon;\n    scene.renderer.toneMappingExposure=1.24;if(scene.key)scene.key.intensity=4.0;ctx.clearRect(0,0,W,H);updateQuality(performance.now());return;\n   }catch(error){modelViewer.active=false;console.error('Model viewer rendering stopped.',error)}\n  }\n  if(scene.actors?.[1]?.root)scene.actors[1].root.visible=true;if(scene.actors?.[0]?.weapon)scene.actors[0].weapon.visible=true;setCamera();const recoil=feel.reduced?0:shake;"""
if 'if(modelViewer.active)' not in s:
    if old not in s: raise SystemExit('render anchor missing')
    s=s.replace(old,new)

api_anchor="window.parryVisualDiagnostics=()=>({available,failure,quality,visualExtra,parryBurstActive:!!parryBurst,parrySuccess:+parrySuccessT.toFixed(3),trailPoints:[player,boss].map(d=>trailByDoll.get(d)?.length||0),ribbons:ribbonMeshes.filter(m=>m.visible).length,ribbonCores:ribbonCoreMeshes.filter(m=>m.visible).length,...((scene?.diagnostics)||{})});"
api="""window.ParryModelViewer={\n  open:modelViewerOpen,close:modelViewerClose,isAvailable:()=>available,state:modelViewerState,\n  preset:modelViewerPreset,rotate:(yaw,pitch)=>{modelViewer.yaw+=yaw;modelViewer.pitch+=pitch;modelViewer.auto=false;return modelViewerState()},\n  zoom:factor=>{const s=modelViewerScale();modelViewer.distance=Math.max(.82*s,Math.min(7.2*s,modelViewer.distance*factor));return modelViewerState()},\n  setAuto:value=>{modelViewer.auto=!!value;return modelViewerState()},toggleAuto:()=>{modelViewer.auto=!modelViewer.auto;return modelViewerState()},\n  setWeapon:value=>{modelViewer.weapon=!!value;return modelViewerState()},toggleWeapon:()=>{modelViewer.weapon=!modelViewer.weapon;return modelViewerState()},\n  reset:()=>{modelViewer.yaw=-.46;modelViewer.auto=true;modelViewer.weapon=true;return modelViewerPreset('full')},diagnostics:modelViewerState\n };\n window.parryVisualDiagnostics=()=>({available,failure,quality,visualExtra,modelViewer:modelViewerState(),parryBurstActive:!!parryBurst,parrySuccess:+parrySuccessT.toFixed(3),trailPoints:[player,boss].map(d=>trailByDoll.get(d)?.length||0),ribbons:ribbonMeshes.filter(m=>m.visible).length,ribbonCores:ribbonCoreMeshes.filter(m=>m.visible).length,...((scene?.diagnostics)||{})});"""
if 'window.ParryModelViewer={' not in s:
    if api_anchor not in s: raise SystemExit('diagnostics anchor missing')
    s=s.replace(api_anchor,api)
p.write_text(s)

ui=Path('dist/model-viewer.js')
ui.write_text(r'''\'use strict\';
(()=>{
 if(window.__parryModelViewerUILoaded)return;window.__parryModelViewerUILoaded=true;
 const api=()=>window.ParryModelViewer,$=id=>document.getElementById(id),start=$('start'),titleOverlay=$('overlay');if(!start||!titleOverlay)return;
 const style=document.createElement('style');style.textContent=`
 #modelViewerOpen{position:static;z-index:auto;width:auto;margin:0;border:1px solid rgba(210,236,246,.38);background:rgba(11,22,31,.72);color:#eaf8ff;padding:10px 12px;font:600 11px/1.05 system-ui;letter-spacing:.13em;border-radius:3px;backdrop-filter:blur(12px);box-shadow:0 8px 26px rgba(0,0,0,.22);white-space:nowrap}
 #modelViewerOpen small{display:block;margin-top:5px;font-size:8px;letter-spacing:.28em;opacity:.62}#modelViewerOpen:disabled{opacity:.42}
 #modelViewerUI{display:none;position:fixed;inset:0;z-index:80;color:#edf8ff;font-family:system-ui,-apple-system,sans-serif;user-select:none;-webkit-user-select:none;touch-action:none;overflow:hidden}
 #modelViewerUI.show{display:block}#modelViewerUI::before{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 50% 46%,transparent 0 36%,rgba(5,12,18,.06) 58%,rgba(3,8,13,.58) 100%)}
 #modelViewerGesture{position:absolute;inset:0;touch-action:none}
 .mv-top{position:absolute;z-index:3;top:max(14px,env(safe-area-inset-top));left:max(18px,env(safe-area-inset-left));right:max(18px,env(safe-area-inset-right));display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none}
 .mv-title{pointer-events:none;text-shadow:0 2px 14px #000}.mv-title b{display:block;font-size:15px;letter-spacing:.28em}.mv-title small{display:block;margin-top:5px;font-size:8px;letter-spacing:.25em;opacity:.65}
 .mv-close,.mv-chip{pointer-events:auto;border:1px solid rgba(225,243,250,.30);background:rgba(8,18,26,.64);color:#f4fbff;backdrop-filter:blur(12px);border-radius:3px;min-height:40px;padding:0 14px;font-size:11px;letter-spacing:.10em}
 .mv-bottom{position:absolute;z-index:4;left:max(14px,env(safe-area-inset-left));right:max(14px,env(safe-area-inset-right));bottom:max(12px,env(safe-area-inset-bottom));display:flex;justify-content:center;gap:7px;align-items:center;pointer-events:none;flex-wrap:wrap}
 .mv-bottom button{pointer-events:auto}.mv-chip.active{border-color:rgba(141,231,255,.82);box-shadow:0 0 18px rgba(116,221,255,.16);background:rgba(32,66,78,.68)}
 .mv-hint{position:absolute;z-index:2;left:50%;bottom:max(67px,calc(env(safe-area-inset-bottom) + 62px));transform:translateX(-50%);font-size:9px;letter-spacing:.12em;white-space:nowrap;opacity:.56;text-shadow:0 1px 8px #000;pointer-events:none}
 .mv-hidden{visibility:hidden!important;pointer-events:none!important}
 @media(max-height:390px){.mv-chip,.mv-close{min-height:34px;padding:0 11px;font-size:10px}.mv-hint{bottom:max(55px,calc(env(safe-area-inset-bottom) + 50px))}}
 `;document.head.appendChild(style);
 const open=document.createElement('button');open.id='modelViewerOpen';open.type='button';open.innerHTML='モデルを見る<small>MODEL VIEWER</small>';const titleActions=document.createElement('div');titleActions.id='titleActions';start.parentNode.insertBefore(titleActions,start);titleActions.appendChild(start);titleActions.appendChild(open);
 const ui=document.createElement('div');ui.id='modelViewerUI';ui.innerHTML=`<div id="modelViewerGesture"></div><div class="mv-top"><div class="mv-title"><b>PARRY DOLL</b><small>HEROINE MODEL VIEWER</small></div><button class="mv-close" id="mvClose">戻る</button></div><div class="mv-hint">ドラッグ：回転　・　ピンチ：拡大縮小</div><div class="mv-bottom"><button class="mv-chip active" data-preset="full">全身</button><button class="mv-chip" data-preset="upper">上半身</button><button class="mv-chip" data-preset="face">顔</button><button class="mv-chip active" id="mvAuto">AUTO</button><button class="mv-chip active" id="mvWeapon">武器</button><button class="mv-chip" id="mvReset">RESET</button></div>`;document.body.appendChild(ui);
 const gesture=$('modelViewerGesture'),hidden=[document.querySelector('header'),...['bossHud','playerHud','controls','cue','toast','parrySuccessHud','pbPhaseStrip','pbResolve','pbChain','pbDanger','pbBanner','pbCineBars','pbResolveBurst'].map(id=>$(id))].filter(Boolean);let savedOverlay='',pointers=new Map(),single=null,pinch=null;
 function sync(){const a=api(),state=a?.state?.();if(!state)return;ui.querySelectorAll('[data-preset]').forEach(b=>b.classList.toggle('active',b.dataset.preset===state.preset));$('mvAuto').classList.toggle('active',state.auto);$('mvAuto').textContent=state.auto?'AUTO':'MANUAL';$('mvWeapon').classList.toggle('active',state.weapon)}
 function enter(){const a=api();if(!a?.isAvailable?.()){open.disabled=true;open.innerHTML='MODEL VIEWER 利用不可<small>WEBGL REQUIRED</small>';return}if(!a.open())return;savedOverlay=titleOverlay.style.display;titleOverlay.style.display='none';hidden.forEach(e=>e.classList.add('mv-hidden'));ui.classList.add('show');sync()}
 function leave(){api()?.close?.();ui.classList.remove('show');hidden.forEach(e=>e.classList.remove('mv-hidden'));titleOverlay.style.display=savedOverlay;pointers.clear();single=pinch=null}
 open.addEventListener('click',enter);$('mvClose').addEventListener('click',leave);$('mvReset').addEventListener('click',()=>{api()?.reset?.();sync()});$('mvAuto').addEventListener('click',()=>{api()?.toggleAuto?.();sync()});$('mvWeapon').addEventListener('click',()=>{api()?.toggleWeapon?.();sync()});ui.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{api()?.preset?.(b.dataset.preset);sync()}));
 const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
 gesture.addEventListener('pointerdown',e=>{gesture.setPointerCapture?.(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===1)single={id:e.pointerId,x:e.clientX,y:e.clientY};else if(pointers.size===2){const [a,b]=[...pointers.values()];pinch={d:dist(a,b),model:api()?.state?.().distance||4};single=null}e.preventDefault()});
 gesture.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;const prev=pointers.get(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===1&&single){const dx=e.clientX-prev.x,dy=e.clientY-prev.y;api()?.rotate?.(-dx*.008,dy*.006);single.x=e.clientX;single.y=e.clientY;sync()}else if(pointers.size===2&&pinch){const [a,b]=[...pointers.values()],d=Math.max(24,dist(a,b)),state=api()?.state?.();if(state?.distance)api()?.zoom?.((pinch.model*(pinch.d/d))/state.distance);sync()}e.preventDefault()});
 function endPointer(e){pointers.delete(e.pointerId);if(pointers.size===1){const [id,p]=[...pointers.entries()][0];single={id,x:p.x,y:p.y}}else single=null;if(pointers.size<2)pinch=null}
 gesture.addEventListener('pointerup',endPointer);gesture.addEventListener('pointercancel',endPointer);gesture.addEventListener('wheel',e=>{api()?.zoom?.(Math.exp(e.deltaY*.0015));sync();e.preventDefault()},{passive:false});
 document.addEventListener('keydown',e=>{if(!ui.classList.contains('show'))return;if(e.key==='Escape'){leave();return}if(e.key==='ArrowLeft')api()?.rotate?.(.12,0);else if(e.key==='ArrowRight')api()?.rotate?.(-.12,0);else if(e.key==='ArrowUp')api()?.rotate?.(0,-.08);else if(e.key==='ArrowDown')api()?.rotate?.(0,.08);else if(e.key==='+'||e.key==='=')api()?.zoom?.(.88);else if(e.key==='-')api()?.zoom?.(1.13);sync()});
 window.parryModelViewerUI={open:enter,close:leave,isOpen:()=>ui.classList.contains('show')};
})();
''')

idx=Path('dist/index.html');h=idx.read_text()
old="const cinematic=document.createElement('script');cinematic.src='./parry-cinematic-v3.js?v='+version;document.body.appendChild(cinematic)"
new="const cinematic=document.createElement('script');cinematic.src='./parry-cinematic-v3.js?v='+version;cinematic.onload=()=>{const viewer=document.createElement('script');viewer.src='./model-viewer.js?v='+version;document.body.appendChild(viewer)};document.body.appendChild(cinematic)"
if "viewer.src='./model-viewer.js?v='+version" not in h:
    if old not in h: raise SystemExit('index cinematic anchor missing')
    h=h.replace(old,new)
idx.write_text(h)
PY

node --check dist/visual-upgrade.js
node --check dist/model-viewer.js
python3 - <<'PY'
from pathlib import Path
u=Path('dist/visual-upgrade.js').read_text();m=Path('dist/model-viewer.js').read_text();i=Path('dist/index.html').read_text()
assert 'window.ParryModelViewer={' in u
assert 'if(modelViewer.active)' in u
assert 'modelViewerOpen' in m and 'data-preset="face"' in m
assert "viewer.src='./model-viewer.js?v='+version" in i
print('PASS: model viewer integration anchors')
PY

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add dist/visual-upgrade.js dist/model-viewer.js dist/index.html
if git diff --cached --quiet; then
  echo 'No model viewer changes to commit.'
else
  git commit -m 'feat: add heroine model viewer mode'
  git push origin HEAD:main
fi
