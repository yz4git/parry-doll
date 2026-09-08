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
  // Mirror dynamic values used by the detailed actor renderer while preserving proxy identity.
  for(const k of ['pos','vel','face','hp','down','stun','attack','parry','wind','strike','broken','counter','invuln','hitRegion','hitRegionT','hitRegionMax','hitRegionSide','motion'])p[k]=d[k];
  p.spec=d.spec;p.player=d.player;p.links=d.links;
  while(p.nodes.length<d.nodes.length)p.nodes.push({...d.nodes[p.nodes.length],p:{...d.nodes[p.nodes.length].p},prev:{...d.nodes[p.nodes.length].prev}});
  for(let i=0;i<d.nodes.length;i++){
   const src=d.nodes[i],dst=p.nodes[i];
   dst.name=src.name;dst.r=src.r;dst.rest=src.rest;dst.prev=src.prev;dst.p={...src.p};
  }
  if(d.spec.type==='human')stabilizeHuman(d,p);
  return p;
 }
 function stabilizeHuman(live,proxy){
  const nodes=proxy.nodes,src=live.nodes,idx=name=>src.findIndex(n=>n.name===name);
  const hipI=idx('hip'),chestI=idx('chest'),headI=idx('head');if(hipI<0||chestI<0||headI<0)return;
  const fallen=live.hp<=0||live.down>0;
  // Dead/downed ragdolls retain most of their physical freedom. Upright armored bodies are much stiffer.
  let strength=fallen?.16:live.attack>0||live.wind>0||live.strike>0?.58:live.hitRegionT>0||live.stun>0?.68:.82;
  const hip={...src[hipI].p},liveChest=src[chestI].p;
  const torsoLen=vlen(subv(src[chestI].rest,src[hipI].rest))||.6;
  const torsoLive=subv(liveChest,hip),maxTorso=fallen?1.35:(live.attack>0||live.wind>0||live.strike>0?.82:live.hitRegionT>0?.76:.62);
  const torsoDir=clampDirection(torsoLive,v(0,1,0),maxTorso),torsoGoal=addv(hip,mulv(torsoDir,torsoLen));
  const stableChest=mixv(liveChest,torsoGoal,strength);
  nodes[hipI].p=hip;nodes[chestI].p=stableChest;
  const chestDelta=subv(stableChest,liveChest);

  // Translate the whole upper-limb chains with the corrected chest so armor cannot visually detach from the torso.
  for(let i=0;i<src.length;i++)if(['shoulder','elbow','hand','offhand'].includes(src[i].name))nodes[i].p=addv(src[i].p,chestDelta);

  const neckLen=vlen(subv(src[headI].rest,src[chestI].rest))||.4;
  const shiftedHead=addv(src[headI].p,chestDelta),headLive=subv(shiftedHead,stableChest);
  const headDir=clampDirection(headLive,torsoDir,fallen?1.45:(live.hitRegion==='head'&&live.hitRegionT>0?1.02:.78));
  const headGoal=addv(stableChest,mulv(headDir,neckLen));
  nodes[headI].p=mixv(shiftedHead,headGoal,fallen?.10:.72);

  // Keep an upright fighter's knees below the pelvis without cancelling deliberate knockdowns or giant stomps.
  const allowHighLeg=fallen||(!live.player&&(live.wind>0||live.strike>0)&&typeof enemyMove==='function'&&enemyMove().kind==='stomp');
  if(!allowHighLeg){
   for(let i=0;i<src.length;i++)if(src[i].name==='knee'&&nodes[i].p.y>hip.y+.10*live.spec.scale){
    nodes[i].p.y+=(hip.y+.10*live.spec.scale-nodes[i].p.y)*.72;
   }
  }
 }
 function worldBlade(d,blade){
  const c=Math.cos(d.face),s=Math.sin(d.face),x=blade.x*c+blade.z*s,z=-blade.x*s+blade.z*c;
  return v(x*d.spec.scale,blade.y*d.spec.scale,z*d.spec.scale);
 }
 function addBladeTrail(out,d,blade,dt){
  if(d.spec.type!=='human')return;
  let history=trailByDoll.get(d);if(!history){history=[];trailByDoll.set(d,history)}
  for(const q of history)q.life-=dt;
  while(history.length&&history[0].life<=0)history.shift();
  const active=d.attack>0||d.parry>0||d.wind>0||d.strike>0;
  if(active){
   const hand=d.nodes.find(n=>n.name==='hand');if(hand){
    const tip=addv(hand.p,worldBlade(d,blade)),color=d.parry>0?'#ffe6a8':d.player?'#baffed':'#ffbd77';
    const last=history[history.length-1];
    if(!last||vlen(subv(tip,last.p))>.024)history.push({p:tip,base:{...hand.p},life:.22,color});
    while(history.length>13)history.shift();
   }
  }
  // Render a narrow 3D ribbon around the true blade path rather than a single dotted centerline.
  for(let i=0;i<history.length;i++){
   const a=history[i],b=history[Math.min(i+1,history.length-1)],delta=subv(b.p,a.p),dir=vn(vlen(delta)>.001?delta:v(0,1,0));
   let side=vcross(dir,v(0,1,0));if(vlen(side)<.05)side=v(1,0,0);side=vn(side);
   const normal=vn(vcross(side,dir)),steps=i===history.length-1?1:5;
   for(let k=0;k<steps;k++){
    const q=mixv(a.p,b.p,k/steps),baseQ=mixv(a.base||a.p,b.base||b.p,k/steps),fade=Math.max(.32,a.life/.22),w=.060*d.spec.scale*fade;
    // Two spines (tip and upper blade) make the swept sword volume read as a luminous ribbon instead of loose dots.
    for(const spine of [q,mixv(q,baseQ,.28)]){
     out.push({p:spine,color:a.color},{p:spine,color:a.color});
     out.push({p:addv(spine,mulv(side,w)),color:a.color},{p:addv(spine,mulv(side,-w)),color:a.color});
     out.push({p:addv(spine,mulv(normal,w*.45)),color:a.color},{p:addv(spine,mulv(normal,-w*.45)),color:a.color});
    }
   }
  }
 }

 let seenParries=parries,parryBurst=null;
 function closestPointOnDoll(d,point){
  let best=d.nodes[0]?.p||d.pos,dist=Infinity;
  for(const n of d.nodes){const q=vlen(subv(n.p,point));if(q<dist){dist=q;best=n.p}}
  return best;
 }
 function updateParryBurst(out,dt){
  // The global parry count increments exactly once on a successful deflection and is more robust than timing a short counter window.
  if(parries<seenParries)seenParries=parries;
  if(parries>seenParries){
   const hand=player.nodes.find(n=>n.name==='hand')?.p||player.nodes[1].p;
   const weapon=boss.spec.type==='human'?(boss.nodes.find(n=>n.name==='hand')?.p||closestPointOnDoll(boss,hand)):closestPointOnDoll(boss,hand),contact=mixv(hand,weapon,.55);
   if(boss.spec.type==='human')contact.y+=.24*Math.min(1.4,boss.spec.scale);
   parryBurst={p:contact,life:.20,max:.20};seenParries=parries;
  }
  if(!parryBurst)return;
  parryBurst.life=Math.max(0,parryBurst.life-dt);if(parryBurst.life<=0){parryBurst=null;return}
  const t=1-parryBurst.life/parryBurst.max,r=.055+t*.48,clock=feel.clock*22;
  // Bright core plus short radial 3D spark spokes. Pure gold is reserved for gameplay-significant parries.
  for(let i=0;i<4;i++)out.push({p:addv(parryBurst.p,v(0,(i-1.5)*.018,0)),color:i===0?'#fff8dc':'#ffd66f'});
  for(let i=0;i<12;i++){
   const a=i/12*Math.PI*2+clock*(i%2?.12:-.09),lift=((i%4)-1.5)*.05,dir=v(Math.cos(a),Math.sin(a*1.55)*.28+lift,Math.sin(a));
   for(let j=1;j<=3;j++){
    const q=addv(parryBurst.p,mulv(dir,r*j/3));
    out.push({p:q,color:j===1?'#fff4c5':j===2?'#ffd05c':'#ff9a43'});
   }
  }
 }

 // Automatic iPhone-friendly quality scaling: preserve gameplay while reducing fill-rate/shadow cost under sustained load.
 let quality='high',slowAccum=0,fastAccum=0,lastFrame=performance.now(),visualExtra=0;
 function applyQuality(next){
  if(!scene||quality===next)return;quality=next;
  const dpr=Math.min(devicePixelRatio||1,next==='high'?1.65:next==='medium'?1.42:1.22),shadow=next==='low'?512:next==='medium'?768:1024;
  scene.renderer.setPixelRatio(dpr);scene.renderer.setSize(W,H,false);
  if(scene.key?.shadow){scene.key.shadow.mapSize.set(shadow,shadow);if(scene.key.shadow.map){scene.key.shadow.map.dispose();scene.key.shadow.map=null}}
 }
 function updateQuality(now){
  const ms=Math.min(80,now-lastFrame);lastFrame=now;
  if(ms>22){slowAccum+=ms;fastAccum=0}else if(ms<17.2){fastAccum+=ms;slowAccum=Math.max(0,slowAccum-ms*.35)}else{slowAccum=Math.max(0,slowAccum-ms*.15);fastAccum=Math.max(0,fastAccum-ms*.25)}
  if(slowAccum>1600){applyQuality(quality==='high'?'medium':'low');slowAccum=0}
  if(fastAccum>5000){applyQuality(quality==='low'?'medium':'high');fastAccum=0}
 }

 render=function(){
  if(!available)return baseRender();
  // This is exactly the existing camera update, called once per displayed frame.
  setCamera();
  const recoil=feel.reduced?0:shake,dt=Math.max(1/120,Math.min(.05,feel.dt||1/60));
  try{
   const poses=[player,boss].map(d=>d.attack>0?motionPose(d).blade:d.wind>0?COMBO_POSES[enemyMove(d).motion].ready.blade:IDLE_POSE.blade);
   const visualPlayer=proxyFor(player),visualBoss=proxyFor(boss),parryFx=player.counter>1.02||!!parryBurst,sourceParticles=parryFx?particles.filter(p=>p.color!=='#ffde8e'):particles;
   const visualParticles=sourceParticles.slice();
   addBladeTrail(visualParticles,player,poses[0],dt);addBladeTrail(visualParticles,boss,poses[1],dt);updateParryBurst(visualParticles,dt);visualExtra=visualParticles.length-sourceParticles.length;
   scene.render({width:W,height:H,camera,forward:basis.f,up:basis.up,player:visualPlayer,boss:visualBoss,poses,particles:visualParticles,clock:feel.clock,recoil});
   // Low silhouettes need a little more separation from the moonlit stone without changing gameplay telegraphs.
   if(scene.renderer){scene.renderer.toneMappingExposure=boss.spec.type==='beast'?1.27:boss.spec.type==='spider'?1.23:1.18}
   if(scene.key)scene.key.intensity=boss.spec.type==='beast'?4.05:boss.spec.type==='spider'?3.8:3.5;
   updateQuality(performance.now());
  }catch(error){available=false;failure=String(error);webgl.style.display='none';console.error('Detailed rendering stopped; using original renderer.',error);return baseRender()}
  ctx.clearRect(0,0,W,H);ctx.save();ctx.translate(Math.sin(feel.clock*113)*recoil*14,Math.cos(feel.clock*139)*recoil*8);
  if(mode==='play'&&boss.wind>0)drawAttackTelegraph();
  if(boss.broken>0)floorRing(V(boss.pos.x,.05,boss.pos.z),1.3+Math.sin(feel.clock*7)*.08,'#ffe2a3',2);
  if(player.counter>0)floorRing(V(player.pos.x,.05,player.pos.z),.8,'#99ffee',2);
  for(const r of rings)floorRing(V(r.p.x,.06,r.p.z),(.5-r.life)*7,r.color,Math.max(1,r.life*5));
  if(boss.wind>0&&mode==='play'){const p=project(add(boss.nodes[2].p,V(0,.55,0)));if(p.z>.18){ctx.fillStyle=boss.wind<Math.max(.06,.48-enemyMove().hits[0])?'#ffdc86':'#d48d64';ctx.font='bold 24px system-ui';ctx.textAlign='center';ctx.fillText(boss.wind<Math.max(.06,.48-enemyMove().hits[0])?'◇':'·',p.x,p.y)}}
  // Detailed rendering owns sword trails. Keep impacts/damage overlays from the original feel pass, but suppress old 2D slash ribbons.
  const savedSlashes=feel.slashes,savedParticles=particles;feel.slashes=[];if(player.counter>1.02||parryBurst)particles=particles.filter(p=>p.color!=='#ffde8e');drawFeel();particles=savedParticles;feel.slashes=savedSlashes;ctx.restore();
 };
 window.parryVisualDiagnostics=()=>({available,failure,quality,visualExtra,parryBurstActive:!!parryBurst,...(scene?.diagnostics||{})});
})();