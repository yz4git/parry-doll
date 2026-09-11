'use strict';
// Rendering-only bridge: never writes simulation, input, timing, hit, or camera state.
(()=>{
 const baseRender=render,gameCanvas=$('game'),webgl=document.createElement('canvas');
 webgl.id='visual-scene';webgl.setAttribute('aria-hidden','true');
 Object.assign(webgl.style,{position:'fixed',inset:'0',width:'100%',height:'100%',pointerEvents:'none'});
 gameCanvas.parentNode.insertBefore(webgl,gameCanvas);
 let scene=null,available=false,failure='';
 try{scene=new window.ParryVisual.VisualScene(webgl);available=true}catch(error){failure=String(error);webgl.style.display='none';console.warn('Detailed rendering unavailable; using the original renderer.',error)}
 webgl.addEventListener('webglcontextlost',event=>{event.preventDefault();available=false;webgl.style.display='none'});
 webgl.addEventListener('webglcontextrestored',()=>{available=!!scene;webgl.style.display=available?'':'none'});

 // Detailed-render framing adjustment: keep the Giant's crown below the HUD without pulling the camera farther away.
 const detailedSetCameraBase=setCamera;
 setCamera=function(){
  detailedSetCameraBase();
  if(boss?.spec?.scale>1.8){
   const visualTarget=add(target,V(0,1.10,0)),f=norm(sub(visualTarget,camera)),r=norm(V(-f.z,0,f.x)),u=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);
   basis={f,right:r,up:u};
  }
 };

 // Visual-only skeleton proxies. The live PBD dolls remain untouched for combat and hit detection.
 const proxyByDoll=new WeakMap(),trailByDoll=new WeakMap();
 let parrySuccessT=0,parrySuccessPerfect=false;
 const PARRY_SUCCESS_MAX=.62;
 const v=(x=0,y=0,z=0)=>({x,y,z}),subv=(a,b)=>v(a.x-b.x,a.y-b.y,a.z-b.z),addv=(a,b)=>v(a.x+b.x,a.y+b.y,a.z+b.z),mulv=(a,s)=>v(a.x*s,a.y*s,a.z*s);
 const vcross=(a,b)=>v(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
 const vlen=a=>Math.hypot(a.x,a.y,a.z),vn=a=>{const l=vlen(a)||1;return mulv(a,1/l)},vdot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
 const mixv=(a,b,t)=>v(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t,a.z+(b.z-a.z)*t);
 function clampDirection(dir,reference,maxAngle){
  const d=vn(dir),r=vn(reference),dot=Math.max(-1,Math.min(1,vdot(d,r))),angle=Math.acos(dot);
  if(angle<=maxAngle)return d;
  let tangent=subv(d,mulv(r,dot)),tl=vlen(tangent);
  if(tl<1e-5)tangent=v(1,0,0);else tangent=mulv(tangent,1/tl);
  return addv(mulv(r,Math.cos(maxAngle)),mulv(tangent,Math.sin(maxAngle)));
 }
 function proxyFor(d){
  let p=proxyByDoll.get(d);
  if(!p){
   p=Object.create(Object.getPrototypeOf(d));
   p.spec=d.spec;p.player=d.player;p.links=d.links;
   p.nodes=d.nodes.map(n=>({...n,rest:{...n.rest},p:{...n.p},prev:{...n.prev}}));
   proxyByDoll.set(d,p);
  }
  for(const k of ['pos','vel','face','hp','down','stun','attack','parry','wind','strike','broken','counter','invuln','hitRegion','hitRegionT','hitRegionMax','hitRegionSide','motion'])p[k]=d[k];
  p.spec=d.spec;p.player=d.player;p.links=d.links;
  while(p.nodes.length<d.nodes.length)p.nodes.push({...d.nodes[p.nodes.length],p:{...d.nodes[p.nodes.length].p},prev:{...d.nodes[p.nodes.length].prev}});
  for(let i=0;i<d.nodes.length;i++){
   const src=d.nodes[i],dst=p.nodes[i];dst.name=src.name;dst.r=src.r;dst.rest=src.rest;dst.prev=src.prev;dst.p={...src.p};
  }
  if(d.spec.type==='human'){stabilizeHuman(d,p);if(d.player&&d.attack>0)applyPlayerAttackReadability(d,p);if(d.player&&parrySuccessT>0)applyPlayerParrySuccess(d,p)}
  else if(d.spec.type==='spider')separateSpiderSilhouette(d,p);
  p.visualParrySuccess=d.player?parrySuccessT/PARRY_SUCCESS_MAX:0;p.visualParryPerfect=d.player&&parrySuccessPerfect;if(d.player&&parrySuccessT>0)p.parry=Math.max(p.parry||0,.08);
  return p;
 }
 function stabilizeHuman(live,proxy){
  const nodes=proxy.nodes,src=live.nodes,idx=name=>src.findIndex(n=>n.name===name);
  const hipI=idx('hip'),chestI=idx('chest'),headI=idx('head');if(hipI<0||chestI<0||headI<0)return;
  const fallen=live.hp<=0||live.down>0,reacting=live.hitRegionT>0||live.stun>0;
  let strength=fallen?.14:reacting?.52:live.attack>0||live.wind>0||live.strike>0?.50:.74;
  const hip={...src[hipI].p},liveChest=src[chestI].p,torsoLen=vlen(subv(src[chestI].rest,src[hipI].rest))||.6;
  const torsoLive=subv(liveChest,hip),maxTorso=fallen?1.40:(reacting?.88:live.attack>0||live.wind>0||live.strike>0?.74:.50);
  const torsoDir=clampDirection(torsoLive,v(0,1,0),maxTorso),torsoGoal=addv(hip,mulv(torsoDir,torsoLen)),stableChest=mixv(liveChest,torsoGoal,strength);
  nodes[hipI].p=hip;nodes[chestI].p=stableChest;const chestDelta=subv(stableChest,liveChest);
  for(let i=0;i<src.length;i++)if(['shoulder','elbow','hand','offhand'].includes(src[i].name))nodes[i].p=addv(src[i].p,chestDelta);
  const neckLen=vlen(subv(src[headI].rest,src[chestI].rest))||.4,shiftedHead=addv(src[headI].p,chestDelta),headLive=subv(shiftedHead,stableChest);
  const headDir=clampDirection(headLive,torsoDir,fallen?1.48:(live.hitRegion==='head'&&live.hitRegionT>0?1.16:reacting?.96:.78)),headGoal=addv(stableChest,mulv(headDir,neckLen));
  nodes[headI].p=mixv(shiftedHead,headGoal,fallen?.10:.72);
  const allowHighLeg=fallen||(!live.player&&(live.wind>0||live.strike>0)&&typeof enemyMove==='function'&&enemyMove().kind==='stomp');
  if(!allowHighLeg)for(let i=0;i<src.length;i++)if(src[i].name==='knee'&&nodes[i].p.y>hip.y+.10*live.spec.scale)nodes[i].p.y+=(hip.y+.10*live.spec.scale-nodes[i].p.y)*.72;
 }
 // MIRROR_BREAK_ATTACK_READABILITY_V1
 function applyPlayerAttackReadability(live,proxy){
  if(live.attack<=0||live.motion<0||typeof motionPose!=='function')return;
  const pose=motionPose(live);if(!pose)return;
  const s=live.spec.scale,duration=Math.max(.01,live.motionDuration||.42),elapsed=Math.max(0,duration-live.attack),contact=Math.max(.045,live.motionContact||.12),after=clamp((elapsed-contact)/Math.max(.08,duration-contact),0,1),before=clamp(elapsed/contact,0,1);
  const smooth=x=>x*x*(3-2*x),phase=elapsed<contact?smooth(before):1-smooth(after)*.22;
  const toWorld=q=>addv(live.pos,live.local(mulv(q,s))),by=name=>proxy.nodes.find(n=>n.name===name),hand=by('hand'),offhand=by('offhand'),chest=by('chest'),head=by('head'),hip=by('hip');
  // Snap the weapon wrist toward the authored attack arc. Gameplay PBD remains untouched; only the render proxy moves.
  if(hand){const desired=toWorld(pose.hand),weight=live.motion===2?.96:.90;hand.p=mixv(hand.p,desired,weight)}
  if(offhand&&live.motion===2){const q=addv(pose.hand,v(-.18,-.06,-.10)),desired=toWorld(q);offhand.p=mixv(offhand.p,desired,.78)}
  const right=v(Math.cos(live.face),0,-Math.sin(live.face)),forward=v(Math.sin(live.face),0,Math.cos(live.face));
  const swingSide=live.motion===0?(-.16+.34*after):live.motion===1?(.14-.30*after):0;
  const drive=(live.motion===2?.22:.10)*phase*s,lean=Math.max(0,pose.lean||0)*.16*s;
  if(chest)chest.p=addv(chest.p,addv(mulv(right,swingSide*phase*s),mulv(forward,drive+lean)));
  if(head)head.p=addv(head.p,addv(mulv(right,swingSide*phase*s*.42),mulv(forward,(drive+lean)*.45)));
  if(hip)hip.p=addv(hip.p,mulv(forward,drive*.24));
 }
 function applyPlayerParrySuccess(live,proxy){
  const t=clamp(parrySuccessT/PARRY_SUCCESS_MAX,0,1),pulse=Math.sin((1-t)*Math.PI),ease=Math.min(1,pulse*1.18),right=v(Math.cos(live.face),0,-Math.sin(live.face)),forward=v(Math.sin(live.face),0,Math.cos(live.face));
  const by=name=>proxy.nodes.find(n=>n.name===name),hip=by('hip'),chest=by('chest'),head=by('head'),shoulders=proxy.nodes.filter(n=>n.name==='shoulder'),elbows=proxy.nodes.filter(n=>n.name==='elbow'),hand=by('hand'),offhand=by('offhand');
  if(hip)hip.p=addv(hip.p,v(0,-.045*ease*live.spec.scale,0));
  if(chest)chest.p=addv(chest.p,addv(mulv(forward,-.10*ease*live.spec.scale),v(0,.055*ease*live.spec.scale,0)));
  if(head)head.p=addv(head.p,addv(mulv(forward,.035*ease*live.spec.scale),v(0,.02*ease*live.spec.scale,0)));
  if(hand)hand.p=addv(hand.p,addv(mulv(right,.30*ease*live.spec.scale),addv(v(0,.23*ease*live.spec.scale,0),mulv(forward,-.08*ease*live.spec.scale))));
  if(offhand)offhand.p=addv(offhand.p,addv(mulv(right,-.14*ease*live.spec.scale),v(0,.10*ease*live.spec.scale,0)));
  for(const n of shoulders)n.p=addv(n.p,mulv(right,Math.sign(n.rest.x)*.08*ease*live.spec.scale));
  for(const n of elbows)n.p=addv(n.p,addv(mulv(right,Math.sign(n.rest.x)*.12*ease*live.spec.scale),v(0,.08*ease*live.spec.scale,0)));
 }
 function separateSpiderSilhouette(live,proxy){
  const right=v(Math.cos(live.face),0,-Math.sin(live.face)),forward=v(Math.sin(live.face),0,Math.cos(live.face)),s=live.spec.scale;
  for(const n of proxy.nodes){if(n.name!=='knee'&&n.name!=='foot')continue;const z=(n.rest.z/s),lane=clamp((z+.8)/1.6,0,1),side=Math.sign(n.rest.x||1),fan=[-.62,-.18,.24,.68][Math.max(0,Math.min(3,Math.round(lane*3)))],lateral=(.18+.34*Math.abs(fan))*side*s,depth=(fan*(n.name==='foot'?.82:.62))*s,height=(n.name==='knee'?(-.16+.72*lane):(-.10+.32*lane))*s;n.p=addv(n.p,addv(mulv(right,lateral),addv(mulv(forward,depth),v(0,height,0))))}
 }
 function worldBlade(d,blade){const c=Math.cos(d.face),s=Math.sin(d.face),x=blade.x*c+blade.z*s,z=-blade.x*s+blade.z*c;return v(x*d.spec.scale,blade.y*d.spec.scale,z*d.spec.scale)}
 function collectBladeTrail(out,d,blade,dt){
  if(d.spec.type!=='human')return;let history=trailByDoll.get(d);if(!history){history=[];trailByDoll.set(d,history)}
  for(const q of history)q.life-=dt;while(history.length&&history[0].life<=0)history.shift();
  if(d.attack>0||d.parry>0||d.wind>0||d.strike>0){const hand=d.nodes.find(n=>n.name==='hand');if(hand){const tip=addv(hand.p,worldBlade(d,blade)),last=history[history.length-1];if(!last||vlen(subv(tip,last.p))>.018)history.push({p:tip,life:.20});while(history.length>18)history.shift()}}
  if(history.length<2)return;const color=d.parry>0?'#ffe5a3':d.player?'#9fffe9':'#ffad67',baseWidth=(d.player?.19:.15)*d.spec.scale*(d.attack>0&&d.motion===2?1.62:d.attack>0&&d.motion===1?1.18:1);out.push({points:history.map(q=>({...q.p})),color,width:baseWidth});
 }
 const ribbonMeshes=[],ribbonCoreMeshes=[];
 function makeRibbonMesh(color){
  if(!scene?.scene||!scene.floor?.geometry||!scene.sparks?.material)return null;
  const BufferGeometry=Object.getPrototypeOf(Object.getPrototypeOf(scene.floor.geometry)).constructor,Attribute=scene.floor.geometry.getAttribute('position').constructor,Mesh=scene.floor.constructor,Material=scene.sparks.material.constructor;
  const geometry=new BufferGeometry(),position=new Attribute(new Float32Array(32*2*3),3),indices=[];geometry.setAttribute('position',position);for(let i=0;i<31;i++){const a=i*2,b=a+1,c=a+2,d=a+3;indices.push(a,b,c,b,d,c)}geometry.setIndex(indices);geometry.setDrawRange(0,0);
  const material=new Material({color,transparent:true,opacity:.72,depthWrite:false,side:2}),mesh=new Mesh(geometry,material);mesh.frustumCulled=false;mesh.visible=false;scene.scene.add(mesh);return mesh;
 }
 function ensureRibbonMeshes(){if(ribbonMeshes.length||!available)return;for(const c of ['#8dffe8','#ff9f55']){const m=makeRibbonMesh(c);if(m)ribbonMeshes.push(m)}for(const c of ['#efffff','#fff1d6']){const m=makeRibbonMesh(c);if(m){m.material.opacity=.92;ribbonCoreMeshes.push(m)}}}
 function updateRibbonMesh(mesh,trail){
  if(!mesh||!trail?.points||trail.points.length<2){if(mesh)mesh.visible=false;return}const points=trail.points,n=Math.min(32,points.length),attr=mesh.geometry.getAttribute('position'),width=Math.max(.035,trail.width||.09);
  for(let i=0;i<n;i++){const q=points[points.length-n+i],prev=points[points.length-n+Math.max(0,i-1)],next=points[points.length-n+Math.min(n-1,i+1)],tangent=vn(subv(next,prev)),view=vn(subv(camera,q));let side=vcross(tangent,view);if(vlen(side)<.001)side=v(1,0,0);side=vn(side);const g=i/(n-1),w=width*(.25+.75*Math.pow(Math.sin(Math.PI*Math.min(.98,Math.max(.02,g))),.55));attr.setXYZ(i*2,q.x+side.x*w,q.y+side.y*w,q.z+side.z*w);attr.setXYZ(i*2+1,q.x-side.x*w,q.y-side.y*w,q.z-side.z*w)}
  attr.needsUpdate=true;mesh.geometry.setDrawRange(0,(n-1)*6);mesh.material.color.set(trail.color);mesh.material.opacity=.82;mesh.visible=true;
 }
 let seenParries=parries,seenPerfects=perfects,parryBurst=null;
 function closestPointOnDoll(d,point){let best=d.nodes[0]?.p||d.pos,dist=Infinity;for(const n of d.nodes){const q=vlen(subv(n.p,point));if(q<dist){dist=q;best=n.p}}return best}
 function triggerParrySuccess(){const hand=player.nodes.find(n=>n.name==='hand')?.p||player.nodes[1].p,weapon=boss.spec.type==='human'?(boss.nodes.find(n=>n.name==='hand')?.p||closestPointOnDoll(boss,hand)):closestPointOnDoll(boss,hand),contact=mixv(hand,weapon,.55);if(boss.spec.type==='human')contact.y+=.24*Math.min(1.4,boss.spec.scale);parryBurst={p:contact,life:.18,max:.18};parrySuccessT=PARRY_SUCCESS_MAX;parrySuccessPerfect=perfects>seenPerfects;seenPerfects=perfects;seenParries=parries;showParrySuccessHud()}
 const visualEnemyImpactBase=enemyImpact;enemyImpact=function(move=null){const before=parries,out=visualEnemyImpactBase(move);if(parries>before)triggerParrySuccess();return out};
 const visualUpdateFeelBase=updateFeel;updateFeel=function(dt){visualUpdateFeelBase(dt);parrySuccessT=Math.max(0,parrySuccessT-dt);if(parrySuccessT<=0)parrySuccessHud.className=''};
 function updateParryBurst(out,dt){if(parries<seenParries){seenParries=parries;seenPerfects=perfects}if(parries>seenParries)triggerParrySuccess();if(!parryBurst)return;parryBurst.life=Math.max(0,parryBurst.life-dt);if(parryBurst.life<=0){parryBurst=null;return}const t=1-parryBurst.life/parryBurst.max,r=.055+t*.48,clock=feel.clock*22;for(let i=0;i<4;i++)out.push({p:addv(parryBurst.p,v(0,(i-1.5)*.018,0)),color:i===0?'#fff8dc':'#ffd66f'});for(let i=0;i<12;i++){const a=i/12*Math.PI*2+clock*(i%2?.12:-.09),lift=((i%4)-1.5)*.05,dir=v(Math.cos(a),Math.sin(a*1.55)*.28+lift,Math.sin(a));for(let j=1;j<=3;j++)out.push({p:addv(parryBurst.p,mulv(dir,r*j/3)),color:j===1?'#fff4c5':j===2?'#ffd05c':'#ff9a43'})}}
 const parrySuccessHud=document.createElement('div');parrySuccessHud.id='parrySuccessHud';parrySuccessHud.innerHTML='<b>COUNTER READY</b><small>PARRY SUCCESS</small>';document.body.appendChild(parrySuccessHud);
 const parrySuccessStyle=document.createElement('style');parrySuccessStyle.textContent=`#parrySuccessHud{position:fixed;left:max(190px,calc(env(safe-area-inset-left) + 190px));bottom:154px;pointer-events:none;opacity:0;transform:translateX(-8px) scale(.96);transition:opacity .08s,transform .12s;color:#d8fff4;text-shadow:0 2px 9px #000;letter-spacing:2px;font-size:11px;font-weight:800;border-left:2px solid #ffd979;padding:4px 8px;background:linear-gradient(90deg,#0a1820c7,transparent)}#parrySuccessHud b{display:block;color:#ffe09a;font-size:13px;letter-spacing:2.6px}#parrySuccessHud small{font-size:8px;opacity:.78;letter-spacing:1.6px}#parrySuccessHud.show{opacity:1;transform:none}#parrySuccessHud.perfect b{color:#fff1bd}@media(max-height:500px){#parrySuccessHud{bottom:123px;left:max(168px,calc(env(safe-area-inset-left) + 168px))}}`;document.head.appendChild(parrySuccessStyle);
 function showParrySuccessHud(){parrySuccessHud.className='show'+(parrySuccessPerfect?' perfect':'');parrySuccessHud.querySelector('small').textContent=parrySuccessPerfect?'PERFECT PARRY':'PARRY SUCCESS'}
 const visualResetBase=reset;reset=function(l=0){parrySuccessT=0;parrySuccessPerfect=false;parryBurst=null;parrySuccessHud.className='';trailByDoll.delete(player);trailByDoll.delete(boss);const out=visualResetBase(l);seenParries=parries;seenPerfects=perfects;return out};
 let quality='high',slowAccum=0,fastAccum=0,lastFrame=performance.now(),qualityLockUntil=0,visualExtra=0;
 const modelViewer={active:false,preset:'full',yaw:-.46,pitch:.055,distance:4.65,auto:true,weapon:true,baseFace:0};
 function modelViewerScale(){return Math.max(.72,player?.spec?.scale||1)}
 function modelViewerPreset(name){const s=modelViewerScale();modelViewer.preset=name;if(name==='face'){modelViewer.distance=1.38*s;modelViewer.pitch=.015}else if(name==='upper'){modelViewer.distance=2.55*s;modelViewer.pitch=.035}else{modelViewer.distance=4.65*s;modelViewer.pitch=.055}return modelViewerState()}
 function modelViewerTarget(d=player){
  const nodes=d?.nodes||[],head=nodes.find(n=>n.name==='head')?.p,chest=nodes.find(n=>n.name==='chest')?.p,hip=nodes.find(n=>n.name==='hip')?.p,feet=nodes.filter(n=>n.name==='foot').map(n=>n.p);
  const fallback=d?.pos||v(0,0,0),minFoot=feet.length?feet.reduce((a,b)=>a.y<b.y?a:b):fallback;
  if(modelViewer.preset==='face'&&head)return v(head.x,head.y+.015*modelViewerScale(),head.z);
  if(modelViewer.preset==='upper'&&head&&chest)return mixv(chest,head,.48);
  if(head)return v(head.x,(head.y+minFoot.y)*.5+.10*modelViewerScale(),head.z);
  return v(fallback.x,(fallback.y||0)+1.15*modelViewerScale(),fallback.z);
 }
 function modelViewerCamera(d=player){
  const target=modelViewerTarget(d),s=modelViewerScale(),minD=.82*s,maxD=7.2*s;modelViewer.distance=Math.max(minD,Math.min(maxD,modelViewer.distance));modelViewer.pitch=Math.max(-.38,Math.min(.58,modelViewer.pitch));
  const a=modelViewer.baseFace+modelViewer.yaw,h=Math.cos(modelViewer.pitch)*modelViewer.distance,cam=v(target.x+Math.sin(a)*h,target.y+Math.sin(modelViewer.pitch)*modelViewer.distance,target.z+Math.cos(a)*h),f=vn(subv(target,cam));
  return{camera:cam,forward:f,up:v(0,1,0)};
 }
 function modelViewerState(){return{active:modelViewer.active,preset:modelViewer.preset,yaw:modelViewer.yaw,pitch:modelViewer.pitch,distance:modelViewer.distance,auto:modelViewer.auto,weapon:modelViewer.weapon,available}}
 function modelViewerOpen(){if(!available)return false;modelViewer.active=true;modelViewer.baseFace=player?.face||0;modelViewerPreset('full');modelViewer.yaw=-.46;modelViewer.auto=true;modelViewer.weapon=true;parrySuccessT=0;parryBurst=null;return true}
 function modelViewerClose(){modelViewer.active=false;if(scene?.actors?.[1]?.root)scene.actors[1].root.visible=true;if(scene?.actors?.[0]?.weapon)scene.actors[0].weapon.visible=true;return true}

 function applyQuality(next){if(!scene||quality===next)return;quality=next;const dpr=Math.min(devicePixelRatio||1,next==='high'?1.65:next==='medium'?1.42:1.22),shadow=next==='low'?512:next==='medium'?768:1024;scene.renderer.setPixelRatio(dpr);scene.renderer.setSize(W,H,false);if(scene.key?.shadow){scene.key.shadow.mapSize.set(shadow,shadow);if(scene.key.shadow.map){scene.key.shadow.map.dispose();scene.key.shadow.map=null}}}
 function updateQuality(now){const ms=Math.min(80,now-lastFrame);lastFrame=now;if(ms>22){slowAccum+=ms;fastAccum=0}else if(ms<17.2){fastAccum+=ms;slowAccum=Math.max(0,slowAccum-ms*.35)}else{slowAccum=Math.max(0,slowAccum-ms*.15);fastAccum=Math.max(0,fastAccum-ms*.25)}if(now<qualityLockUntil)return;if(slowAccum>2200&&quality!=='low'){applyQuality(quality==='high'?'medium':'low');slowAccum=0;fastAccum=0;qualityLockUntil=now+3200}else if(fastAccum>7000&&quality!=='high'){applyQuality(quality==='low'?'medium':'high');slowAccum=0;fastAccum=0;qualityLockUntil=now+4200}}
 render=function(){
  if(!available)return baseRender();
  const dt=Math.max(1/120,Math.min(.05,feel.dt||1/60));
  if(modelViewer.active){
   try{
    if(modelViewer.auto)modelViewer.yaw+=dt*.19;
    const visualPlayer=proxyFor(player),visualBoss=proxyFor(boss),view=modelViewerCamera(visualPlayer);
    visualPlayer.face=modelViewer.baseFace;visualPlayer.vel=v(0,0,0);visualPlayer.attack=0;visualPlayer.parry=0;visualPlayer.wind=0;visualPlayer.strike=0;visualPlayer.down=0;visualPlayer.stun=0;visualPlayer.hitRegionT=0;visualPlayer.motion=0;
    if(scene.actors?.[1]?.root)scene.actors[1].root.visible=false;if(scene.actors?.[0]?.root)scene.actors[0].root.visible=true;if(scene.actors?.[0]?.weapon)scene.actors[0].weapon.visible=modelViewer.weapon;
    ribbonMeshes.forEach(m=>m.visible=false);ribbonCoreMeshes.forEach(m=>m.visible=false);
    scene.render({width:W,height:H,camera:view.camera,forward:view.forward,up:view.up,player:visualPlayer,boss:visualBoss,poses:[IDLE_POSE.blade,IDLE_POSE.blade],particles:[],clock:feel.clock,recoil:0});
    if(scene.actors?.[1]?.root)scene.actors[1].root.visible=false;if(scene.actors?.[0]?.weapon)scene.actors[0].weapon.visible=modelViewer.weapon;
    scene.renderer.toneMappingExposure=1.24;if(scene.key)scene.key.intensity=4.0;ctx.clearRect(0,0,W,H);updateQuality(performance.now());return;
   }catch(error){modelViewer.active=false;console.error('Model viewer rendering stopped.',error)}
  }
  if(scene.actors?.[1]?.root)scene.actors[1].root.visible=true;if(scene.actors?.[0]?.weapon)scene.actors[0].weapon.visible=true;setCamera();const recoil=feel.reduced?0:shake;
  try{const poses=[player,boss].map(d=>d.attack>0?motionPose(d).blade:d.wind>0?COMBO_POSES[enemyMove(d).motion].ready.blade:IDLE_POSE.blade),visualPlayer=proxyFor(player),visualBoss=proxyFor(boss),parryFx=parrySuccessT>0||!!parryBurst,sourceParticles=parryFx?particles.filter(p=>p.color!=='#ffde8e'):particles,visualParticles=sourceParticles.slice(),visualTrails=[];collectBladeTrail(visualTrails,player,poses[0],dt);collectBladeTrail(visualTrails,boss,poses[1],dt);updateParryBurst(visualParticles,dt);visualExtra=visualParticles.length-sourceParticles.length;ensureRibbonMeshes();ribbonMeshes.forEach((m,i)=>updateRibbonMesh(m,visualTrails[i]));ribbonCoreMeshes.forEach((m,i)=>{const t=visualTrails[i];if(t)updateRibbonMesh(m,{...t,width:(t.width||.09)*.32,color:i===0?'#f4ffff':'#fff3dc'});else m.visible=false});scene.render({width:W,height:H,camera,forward:basis.f,up:basis.up,player:visualPlayer,boss:visualBoss,poses,particles:visualParticles,clock:feel.clock,recoil});if(scene.renderer)scene.renderer.toneMappingExposure=boss.spec.type==='beast'?1.27:boss.spec.type==='spider'?1.23:1.18;if(scene.key)scene.key.intensity=boss.spec.type==='beast'?4.05:boss.spec.type==='spider'?3.8:3.5;updateQuality(performance.now())}catch(error){available=false;failure=String(error);webgl.style.display='none';console.error('Detailed rendering stopped; using original renderer.',error);return baseRender()}
  ctx.clearRect(0,0,W,H);ctx.save();ctx.translate(Math.sin(feel.clock*113)*recoil*14,Math.cos(feel.clock*139)*recoil*8);if(mode==='play'&&boss.wind>0)drawAttackTelegraph();if(boss.broken>0)floorRing(V(boss.pos.x,.05,boss.pos.z),1.3+Math.sin(feel.clock*7)*.08,'#ffe2a3',2);if(player.counter>0)floorRing(V(player.pos.x,.05,player.pos.z),.8,'#99ffee',2);for(const r of rings){if(parrySuccessT>0&&(r.color==='#ffdf91'||r.color==='#8de7e0'))continue;floorRing(V(r.p.x,.06,r.p.z),(.5-r.life)*7,r.color,Math.max(1,r.life*5))}if(boss.wind>0&&mode==='play'){const p=project(add(boss.nodes[2].p,V(0,.55,0)));if(p.z>.18){ctx.fillStyle=boss.wind<Math.max(.06,.48-enemyMove().hits[0])?'#ffdc86':'#d48d64';ctx.font='bold 24px system-ui';ctx.textAlign='center';ctx.fillText(boss.wind<Math.max(.06,.48-enemyMove().hits[0])?'◇':'·',p.x,p.y)}}const savedSlashes=feel.slashes,savedParticles=particles,savedImpacts=feel.impacts,savedFlash=feel.flash;feel.slashes=[];if(parrySuccessT>0||parryBurst){particles=particles.filter(p=>p.color!=='#ffde8e');feel.impacts=feel.impacts.filter(f=>f.kind!=='parry');feel.flash=Math.min(feel.flash,.012)}drawFeel();feel.flash=savedFlash;feel.impacts=savedImpacts;particles=savedParticles;feel.slashes=savedSlashes;ctx.restore();
 };
 window.ParryModelViewer={
  open:modelViewerOpen,close:modelViewerClose,isAvailable:()=>available,state:modelViewerState,
  preset:modelViewerPreset,rotate:(yaw,pitch)=>{modelViewer.yaw+=yaw;modelViewer.pitch+=pitch;modelViewer.auto=false;return modelViewerState()},
  zoom:factor=>{const s=modelViewerScale();modelViewer.distance=Math.max(.82*s,Math.min(7.2*s,modelViewer.distance*factor));return modelViewerState()},
  setAuto:value=>{modelViewer.auto=!!value;return modelViewerState()},toggleAuto:()=>{modelViewer.auto=!modelViewer.auto;return modelViewerState()},
  setWeapon:value=>{modelViewer.weapon=!!value;return modelViewerState()},toggleWeapon:()=>{modelViewer.weapon=!modelViewer.weapon;return modelViewerState()},
  reset:()=>{modelViewer.yaw=-.46;modelViewer.auto=true;modelViewer.weapon=true;return modelViewerPreset('full')},diagnostics:modelViewerState
 };
 window.parryVisualDiagnostics=()=>({available,failure,quality,visualExtra,modelViewer:modelViewerState(),parryBurstActive:!!parryBurst,parrySuccess:+parrySuccessT.toFixed(3),trailPoints:[player,boss].map(d=>trailByDoll.get(d)?.length||0),ribbons:ribbonMeshes.filter(m=>m.visible).length,ribbonCores:ribbonCoreMeshes.filter(m=>m.visible).length,...((scene?.diagnostics)||{})});
})();
