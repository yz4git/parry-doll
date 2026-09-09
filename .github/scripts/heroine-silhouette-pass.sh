#!/usr/bin/env bash
set -euo pipefail

cat > dist/parry-cinematic-v3.js <<'EOF'
'use strict';
// Key-art parry presentation: additive screen-space burst, cinematic camera push and hero rim.
(()=>{
 if(window.__parryCinematicV3Loaded)return;window.__parryCinematicV3Loaded=true;
 const baseCanvas=$('game'),fx=document.createElement('canvas');fx.id='parry-cinematic-v3';fx.setAttribute('aria-hidden','true');
 Object.assign(fx.style,{position:'fixed',inset:'0',width:'100%',height:'100%',pointerEvents:'none',zIndex:'7'});baseCanvas.parentNode.insertBefore(fx,baseCanvas.nextSibling);
 const c=fx.getContext('2d',{alpha:true});let dpr=1,last=performance.now(),beat=null;
 const clamp01=x=>Math.max(0,Math.min(1,x)),rand=(a,b)=>a+Math.random()*(b-a);
 function resize(){const nd=Math.min(devicePixelRatio||1,1.35),w=Math.max(1,Math.round(W*nd)),h=Math.max(1,Math.round(H*nd));if(fx.width!==w||fx.height!==h){fx.width=w;fx.height=h;dpr=nd}c.setTransform(dpr,0,0,dpr,0,0)}
 function contactPoint(){
  const hand=player?.nodes?.find(n=>n.name==='hand')?.p||player?.nodes?.[1]?.p||player?.pos||V();
  if(!boss?.nodes?.length)return {...hand};
  let best=boss.nodes[0].p,dist=Infinity;for(const n of boss.nodes){const q=sub(n.p,hand),dd=len(q);if(dd<dist){dist=dd;best=n.p}}
  return mul(add(hand,best),.5);
 }
 function makeBurst(point,perfect){
  const p2=project(point),cx=p2&&p2.z>.01?p2.x:W*.52,cy=p2&&p2.z>.01?p2.y:H*.50;
  const rays=[],sparks=[],streaks=[];
  for(let i=0;i<(perfect?46:34);i++){const a=rand(-Math.PI,Math.PI),bias=i%4===0?rand(-.18,.18):rand(-.8,.8);rays.push({a:a+bias,len:rand(65,perfect?245:180),w:rand(.7,perfect?4.1:3),delay:rand(0,.06),warm:Math.random()>.24})}
  for(let i=0;i<(perfect?34:26);i++){const a=rand(-Math.PI,Math.PI),sp=rand(90,perfect?330:240);sparks.push({a,sp,size:rand(1.2,4.5),life:rand(.18,.42),spin:rand(-8,8)})}
  const base=perfect?-.28:-.22;for(let i=0;i<4;i++)streaks.push({a:base+(i-1.5)*rand(.22,.38)+(i%2?1.55:0),offset:rand(-18,18),w:rand(2.5,perfect?9:6.8),len:rand(.45,.82)*Math.hypot(W,H)});
  beat={point:{...point},cx,cy,perfect,life:perfect?.48:.37,max:perfect?.48:.37,rays,sparks,streaks};
  hitstop=Math.max(hitstop,perfect?.158:.126);shake=Math.max(shake,perfect?.72:.56);
  if(typeof feel==='object'&&feel)feel.slow=Math.max(feel.slow||0,perfect?.18:.10);
 }
 function glowLine(x1,y1,x2,y2,color,w,a,blur=18){c.save();c.globalCompositeOperation='lighter';c.globalAlpha=a;c.strokeStyle=color;c.shadowColor=color;c.shadowBlur=blur;c.lineCap='round';c.lineWidth=w;c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.stroke();c.restore()}
 function draw(){
  resize();c.clearRect(0,0,W,H);if(!beat)return;
  const t=1-beat.life/beat.max,fade=Math.pow(1-t,.56),flash=clamp01((.18-t)/.18),p2=project(beat.point),cx=p2&&p2.z>.01?p2.x:beat.cx,cy=p2&&p2.z>.01?p2.y:beat.cy;
  // Brief exposure lift plus darker edges makes the clash read like a promo-frame photograph.
  c.save();const vign=c.createRadialGradient(cx,cy,35,cx,cy,Math.max(W,H)*.78);vign.addColorStop(0,'rgba(0,0,0,0)');vign.addColorStop(.50,`rgba(4,7,12,${.06*fade})`);vign.addColorStop(1,`rgba(0,0,0,${.38*fade})`);c.fillStyle=vign;c.fillRect(0,0,W,H);c.restore();
  if(flash>0){c.save();c.globalCompositeOperation='screen';c.globalAlpha=(beat.perfect?.50:.34)*flash;c.fillStyle='#fff9e9';c.fillRect(0,0,W,H);c.restore()}
  const coreR=(beat.perfect?150:112)*(1+t*.7);c.save();c.globalCompositeOperation='lighter';const g=c.createRadialGradient(cx,cy,0,cx,cy,coreR);g.addColorStop(0,`rgba(255,255,255,${.98*fade})`);g.addColorStop(.08,`rgba(255,239,190,${.82*fade})`);g.addColorStop(.34,`rgba(255,176,72,${.28*fade})`);g.addColorStop(.68,`rgba(112,222,255,${.12*fade})`);g.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=g;c.fillRect(cx-coreR,cy-coreR,coreR*2,coreR*2);c.restore();
  for(const s of beat.streaks){const cs=Math.cos(s.a),sn=Math.sin(s.a),px=cx-sn*s.offset,py=cy+cs*s.offset,l=s.len*(.5+.5*Math.sin(Math.min(1,t*1.7)*Math.PI*.72));glowLine(px-cs*l*.52,py-sn*l*.52,px+cs*l*.48,py+sn*l*.48,'#ffffff',s.w,fade*.78,s.w*4.2);glowLine(px-cs*l*.46,py-sn*l*.46,px+cs*l*.42,py+sn*l*.42,beat.perfect?'#ffd46a':'#bff7ff',s.w*2.0,fade*.25,s.w*6)}
  for(const r of beat.rays){if(t<r.delay)continue;const q=clamp01((t-r.delay)/(1-r.delay)),grow=Math.sin(Math.min(1,q)*Math.PI*.76),L=r.len*grow,cs=Math.cos(r.a),sn=Math.sin(r.a),a=fade*(1-q*.45);glowLine(cx+cs*8,cy+sn*8,cx+cs*L,cy+sn*L,r.warm?'#ffd073':'#d8fbff',r.w,a,r.w*4)}
  // Expanding double shock ring.
  for(let k=0;k<2;k++){const q=clamp01(t-k*.08);if(q<=0)continue;const r=(30+q*(beat.perfect?190:145))*(1+k*.18);c.save();c.globalCompositeOperation='lighter';c.globalAlpha=fade*(.58-k*.18);c.strokeStyle=k?'#9eefff':'#ffe099';c.lineWidth=Math.max(1,5*(1-q));c.shadowColor=c.strokeStyle;c.shadowBlur=18;c.beginPath();c.ellipse(cx,cy,r,r*.45,-.16,0,Math.PI*2);c.stroke();c.restore()}
  c.save();c.globalCompositeOperation='lighter';for(const s of beat.sparks){const q=Math.min(1,t/(s.life/beat.max)),dist=s.sp*t,ang=s.a+s.spin*t*.035,x=cx+Math.cos(ang)*dist,y=cy+Math.sin(ang)*dist+t*t*65;c.globalAlpha=fade*(1-q*.42);c.fillStyle=Math.random()>.38?'#fff4c7':'#ffad45';c.fillRect(x,y,s.size*(1-q*.55),s.size*(1-q*.55))}c.restore();
  // Readable but brief key-art title treatment.
  const textA=fade*clamp01((.34-t)/.12)*clamp01(t/.045);if(textA>0){c.save();c.globalAlpha=textA;c.textAlign='center';c.font=`600 ${beat.perfect?Math.max(24,Math.min(42,W*.043)):Math.max(21,Math.min(34,W*.036))}px system-ui,sans-serif`;c.letterSpacing='0.22em';c.shadowColor=beat.perfect?'#ffd36b':'#c9f7ff';c.shadowBlur=22;c.fillStyle='#ffffff';c.fillText(beat.perfect?'PERFECT PARRY':'PARRY',cx,Math.min(H-54,cy+96));c.restore()}
 }
 const baseEnemyImpact=enemyImpact;enemyImpact=function(move=null){const bp=parries,bpf=perfects,p=contactPoint(),out=baseEnemyImpact(move);if(parries>bp)makeBurst(p,perfects>bpf);return out};
 const baseSetCamera=setCamera;setCamera=function(){baseSetCamera();if(!beat||!basis?.f)return;const phase=Math.sin(clamp01(1-beat.life/beat.max)*Math.PI),strength=(beat.perfect?.64:.46)*phase;camera=add(camera,mul(basis.f,strength));camera.y-=.07*phase;const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),u=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up:u}};
 const baseRender=render;render=function(){baseRender();const now=performance.now(),dt=Math.min(.05,Math.max(1/120,(now-last)/1000));last=now;draw();if(beat){beat.life=Math.max(0,beat.life-dt);if(beat.life<=0)beat=null}};
 const baseReset=reset;reset=function(l=0){beat=null;return baseReset(l)};
 window.parryCinematicV3Diagnostics=()=>beat?{active:true,perfect:beat.perfect,life:+beat.life.toFixed(3)}:{active:false};
})();
EOF

python3 - <<'PY'
from pathlib import Path

# Load the cinematic pass last so its camera/render wrapper stays outermost.
p=Path('dist/index.html');s=p.read_text()
if "parry-cinematic-v3.js" not in s:
    old="const st2=document.createElement('script');st2.src='./stage-break-v2.js?v='+version;document.body.appendChild(st2)"
    new="const st2=document.createElement('script');st2.src='./stage-break-v2.js?v='+version;st2.onload=()=>{const cinematic=document.createElement('script');cinematic.src='./parry-cinematic-v3.js?v='+version;document.body.appendChild(cinematic)};document.body.appendChild(st2)"
    if old not in s: raise SystemExit('stage-break-v2 loader anchor not found')
    s=s.replace(old,new)
    p.write_text(s)

# Slightly longer-leg, shorter-torso visual rig while gameplay endpoints remain untouched.
p=Path('visual-src/heroine-rig.js');s=p.read_text()
old="const pelvis=V(source[0].p).addScaledVector(up,.28*s),points={pelvis,spine:pelvis.clone().addScaledVector(up,.26*s),chest:pelvis.clone().addScaledVector(up,.56*s),neck:pelvis.clone().addScaledVector(up,.71*s),head:pelvis.clone().addScaledVector(up,.91*s)};"
new="const pelvis=V(source[0].p).addScaledVector(up,.33*s),points={pelvis,spine:pelvis.clone().addScaledVector(up,.24*s),chest:pelvis.clone().addScaledVector(up,.52*s),neck:pelvis.clone().addScaledVector(up,.66*s),head:pelvis.clone().addScaledVector(up,.85*s)};"
if old not in s and new not in s: raise SystemExit('heroine rig torso anchor not found')
s=s.replace(old,new)
old="points['hip'+suffix]=pelvis.clone().addScaledVector(right,side*.18*s).addScaledVector(up,-.02*s);"
new="points['hip'+suffix]=pelvis.clone().addScaledVector(right,side*.17*s).addScaledVector(up,.005*s);"
if old not in s and new not in s: raise SystemExit('heroine rig hip anchor not found')
s=s.replace(old,new)
p.write_text(s)

# Refine the weighted costume: tighter waist and cleaner upper-thigh taper.
p=Path('tools/make-heroine-mesh.py');s=p.read_text()
old="rx=np.interp(y,[1.30,1.4,1.57,1.73,1.86,1.99],[.245,.245,.183,.21,.26,.225]);rz=np.interp(y,[1.30,1.48,1.67,1.85,1.99],[.145,.123,.135,.158,.12])"
new="rx=np.interp(y,[1.30,1.4,1.57,1.73,1.86,1.99],[.238,.232,.169,.198,.252,.218]);rz=np.interp(y,[1.30,1.48,1.67,1.85,1.99],[.137,.118,.130,.154,.116])"
if old not in s and new not in s: raise SystemExit('heroine mesh torso profile anchor not found')
s=s.replace(old,new)
old="points=[np.array([side*.165,1.40,-.005]),np.array([side*.22,.78,.045]),np.array([side*.275,.16,.22])];boneNames=['hip'+suffix,'knee'+suffix];radii=[.105,.112,.086,.088,.055]"
new="points=[np.array([side*.158,1.415,-.005]),np.array([side*.214,.78,.045]),np.array([side*.272,.16,.22])];boneNames=['hip'+suffix,'knee'+suffix];radii=[.100,.107,.082,.087,.054]"
if old not in s and new not in s: raise SystemExit('heroine mesh leg profile anchor not found')
s=s.replace(old,new)
p.write_text(s)

# Character styling: smaller head, more layered armor and longer flowing hair.
p=Path('visual-src/heroine.js');s=p.read_text()
old="const white='#e8e5df',black='#171b27',silver='#aeb9c5',skin='#edc1ab',hair='#25232c';"
new="const white='#ece9e3',black='#151923',silver='#b9c4cf',skin='#edc1ab',hair='#2a252c';"
if old not in s and new not in s: raise SystemExit('heroine palette anchor not found')
s=s.replace(old,new)
old="a.add('box',silver,[0,.18,-.59],[.065,.34,.025]);a.add('box',black,[0,.39,-.57],[1.2,.065,.035],[0,0,0],'cloth');"
new="a.add('box',silver,[0,.18,-.59],[.065,.34,.025]);a.add('box',black,[0,.39,-.57],[1.2,.065,.035],[0,0,0],'cloth');a.add('plate',white,[0,.18,-.585],[.72,.24,.045],[0,0,0],'porcelain');a.add('plate',white,[0,-.12,-.56],[.56,.18,.04],[0,0,0],'porcelain');a.add('box',silver,[0,.02,-.625],[.055,.62,.025]);"
if old not in s and new not in s: raise SystemExit('heroine torso detail anchor not found')
s=s.replace(old,new)
old="if(names.includes('elbow')&&!names.includes('shoulder')){a.add('plate',silver,[0,-.01,.48],[.48,.55,.2]);a.add('plate',black,[0,.13,.57],[.39,.38,.1]);}"
new="if(names.includes('elbow')&&!names.includes('shoulder')){a.add('plate',white,[0,-.02,.49],[.52,.58,.21],[0,0,0],'porcelain');a.add('plate',black,[0,.13,.575],[.35,.34,.085]);a.add('box',silver,[0,.08,.615],[.06,.48,.04]);}"
if old not in s and new not in s: raise SystemExit('heroine forearm detail anchor not found')
s=s.replace(old,new)
old="if(names.includes('shoulder'))a.add('cylinder',silver,[0,.25,0],[width*1.06,.045,width*.94]);"
new="if(names.includes('shoulder')){a.add('cylinder',silver,[0,.25,0],[width*1.04,.04,width*.92]);a.add('plate',white,[0,.08,.46],[.48,.38,.13],[.05,0,0],'porcelain');}if(names.includes('knee')&&names.includes('hip')){a.add('plate',white,[0,.06,.48],[.34,.50,.11],[0,0,0],'porcelain');a.add('box',silver,[0,.12,.57],[.055,.46,.03]);}"
if old not in s and new not in s: raise SystemExit('heroine shoulder/thigh detail anchor not found')
s=s.replace(old,new)
old="for(let i=0;i<13;i++){const a=new Assembly(mats),x=(i-6)*.071,g=taper([[x,.52,-.66],[x+.12,.24,-1.14],[x+.20,-1.1,-1.2],[x-.12,-2.7,-.95],[x+.28,-4.35-(i%3)*.24,-.7]],.17);a.add(g,i%3?'#27252e':'#393540',[0,0,0],[1,1,.67],[0,0,0],'hair');g.dispose();const p=a.build();this.nodes[2].add(p);this.hair.push(p);}"
new="for(let i=0;i<17;i++){const a=new Assembly(mats),x=(i-8)*.058,fan=(i-8)*.018,g=taper([[x,.54,-.66],[x*.82+.10,.16,-1.15],[x+fan,-1.18,-1.19],[x*.72-.12,-2.95,-.92],[x+fan*2+.22,-4.85-(i%4)*.18,-.63]],.145);a.add(g,i%4?'#29262f':'#403943',[0,0,0],[1,1,.70],[0,0,0],'hair');g.dispose();const p=a.build();this.nodes[2].add(p);this.hair.push(p);}"
if old not in s and new not in s: raise SystemExit('heroine ponytail anchor not found')
s=s.replace(old,new)
old="p.scale.setScalar(n.r*(i===2?.90:n.name==='shoulder'?.78:n.name==='elbow'||n.name==='knee'?.75:1))"
new="p.scale.setScalar(n.r*(n.name==='head'?.84:n.name==='shoulder'?.74:n.name==='elbow'||n.name==='knee'?.72:1))"
if old not in s and new not in s: raise SystemExit('heroine node scale anchor not found')
s=s.replace(old,new)
p.write_text(s)

# Keep a concise design note for later visual passes.
d=Path('docs/COUTURE_REFINEMENT.md');text=d.read_text() if d.exists() else '# Couture refinement\n'
marker='## Key-art heroine and parry pass'
if marker not in text:
    text += "\n## Key-art heroine and parry pass\nThe combat silhouette now uses a slightly higher visual pelvis, shorter upper-body spacing, a smaller head, tighter waist and upper-thigh profile, longer multi-strand ponytail, and layered white/silver armor accents on the back, forearms, shoulders and thighs. Gameplay endpoints and hitboxes are unchanged. Perfect parries receive a dedicated screen-space cinematic layer with large diagonal clash streaks, dense sparks, a double shock ring, brief exposure lift, edge darkening, stronger hit-stop and a small camera push.\n"
    d.write_text(text)
PY

python3 tools/make-heroine-mesh.py
(
  cd visual-src
  npm ci
  npm run build
)
node --check dist/parry-cinematic-v3.js
node tests/reference-models.mjs

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add dist/parry-cinematic-v3.js dist/index.html dist/visual-engine.js visual-src/heroine.js visual-src/heroine-rig.js visual-src/heroine-mesh-data.js tools/make-heroine-mesh.py docs/COUTURE_REFINEMENT.md
if git diff --cached --quiet; then exit 0; fi
git commit -m 'feat: push parry and heroine toward key art'
git push origin HEAD:main
