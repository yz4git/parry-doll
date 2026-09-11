'use strict';
// MIRROR BREAK v12 — DESTRUCTION ROUTE: each boss KO permanently changes the architecture and movement pressure of the next arena.
(()=>{
 if(window.__parryMirrorBreakV12Loaded)return;window.__parryMirrorBreakV12Loaded=true;
 const proto=window.ParryVisual?.VisualScene?.prototype;if(!proto)return;
 const ROUTE=['ASH GATE','CAGE BREACH','BROKEN SPINE','ALTAR RIFT'];
 const PAL=[['#241814','#8c5b3d','#ffc06c'],['#101d20','#547a77','#8fe7d7'],['#171222','#66507f','#d9b2ff'],['#151c27','#596d86','#b8e3ff']];
 const s={history:[],lastSerial:0,routeLevel:-1,routeSource:-1,routeName:null,routeMeshes:0,routeBuilds:0,pressureTicks:0,lastPressure:null,routeLaneSide:0};window.__mirrorBreakV12State=s;
 const find=(root,pred)=>{let hit=null;root?.traverse?.(o=>{if(!hit&&pred(o))hit=o});return hit};
 function record(hit){if(!hit||hit.level<0||hit.level>3||!hit.serial||hit.serial<=s.lastSerial)return;s.lastSerial=hit.serial;const e={serial:hit.serial,level:hit.level,x:hit.x||0,z:hit.z||0,power:hit.power||1.5,style:hit.style||'',part:hit.part||null,kind:hit.kind||null};const old=s.history.findIndex(q=>q.level===e.level);if(old>=0)s.history[old]=e;else s.history.push(e);s.history.sort((a,b)=>a.level-b.level)}
 function active(){if(level<1||level>4)return null;return s.history.find(e=>e.level===level-1)||null}
 function material(vs,color,opacity=1,glow=false){const base=(vs.floor?.material||find(vs.scene,o=>o.isMesh&&o.material)?.material);if(!base?.clone)return null;const m=base.clone();m.color?.set?.(color);if('metalness'in m)m.metalness=glow?.42:.28;if('roughness'in m)m.roughness=glow?.36:.78;if(m.emissive){m.emissive.set(glow?color:'#000000');m.emissiveIntensity=glow?.42:0}m.transparent=opacity<1;m.opacity=opacity;m.depthWrite=opacity>.82;return m}
 function mesh(vs,geom,mat){const Mesh=vs.floor?.constructor||find(vs.scene,o=>o.isMesh&&!o.isInstancedMesh)?.constructor;if(!Mesh||!geom||!mat)return null;const m=new Mesh(geom.clone(),mat);m.castShadow=true;m.receiveShadow=true;m.frustumCulled=false;vs.scene.add(m);return m}
 function setBox(m,x,y,z,sx,sy,sz,rx=0,ry=0,rz=0){m.position.set(x,y,z);m.scale.set(sx,sy,sz);m.rotation.set(rx,ry,rz);return m}
 function cleanup(vs){const d=vs.__mbDestructionRoute;if(!d)return;for(const m of d.meshes||[]){vs.scene.remove(m);try{m.material?.dispose?.()}catch{}try{m.geometry?.dispose?.()}catch{}}d.meshes=[];d.key='';s.routeMeshes=0}
 function push(vs,m){if(!m)return null;vs.__mbDestructionRoute.meshes.push(m);s.routeMeshes=vs.__mbDestructionRoute.meshes.length;return m}
 function slabPath(vs,box,base,accent,entry,source){const side=source%2?1:-1,originX=Math.max(-2.2,Math.min(2.2,(entry.x||0)*.20)),back=-5.7;for(let i=0;i<7;i++){const t=i/6,x=originX*(1-t)+side*.55*Math.sin(i*.9)*t,z=-.65-(4.25*t),m=push(vs,mesh(vs,box,(i===6?accent:base)?.clone?.()||(i===6?accent:base)));if(m)setBox(m,x,.045+i*.006,z,.55+.08*(i%2),.055,.82,.02*i,side*.08*(i-3),side*.04*(i%3-1))}return{side,back}}
 function build(vs,entry){const source=entry.level,routeLevel=source+1,pal=PAL[source],box=find(vs.scene,o=>o.geometry?.type==='BoxGeometry')?.geometry,ico=find(vs.scene,o=>o.geometry?.type==='IcosahedronGeometry')?.geometry,torus=find(vs.scene,o=>o.geometry?.type==='TorusGeometry')?.geometry;if(!box)return;const dark=material(vs,pal[0],.96),base=material(vs,pal[1],1),accent=material(vs,pal[2],.92,true),{side,back}=slabPath(vs,box,base,accent,entry,source),x0=side*3.6,z0=back;s.routeLaneSide=side;
  for(const old of s.history.filter(e=>e.level<source)){const a=.7+old.level*1.1,ox=-side*(2.6+old.level*.42),oz=-4.15-old.level*.28;for(let j=0;j<2;j++){const sh=push(vs,mesh(vs,box,dark?.clone?.()||dark));if(sh)setBox(sh,ox+j*.34,.08+j*.05,oz-j*.18,.18,.10,.58,.12*j,a+j*.4,.18*(j?1:-1))}}
  if(source===0){
   for(const k of [-1,1]){const post=push(vs,mesh(vs,box,base?.clone?.()||base));if(post)setBox(post,x0+k*1.25,1.48,z0,.28,2.9,.28,0,0,k*.12)}
   const left=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(left)setBox(left,x0-.72,2.55,z0,.22,1.26,.24,.15,0,-1.08);
   const right=push(vs,mesh(vs,box,base?.clone?.()||base));if(right)setBox(right,x0+.78,2.32,z0,.20,1.08,.23,-.10,0,1.16);
  }else if(source===1){
   for(let i=0;i<6;i++){if(i===2)continue;const k=i-2.5,bar=push(vs,mesh(vs,box,base?.clone?.()||base));if(bar)setBox(bar,x0+k*.42,1.28+Math.abs(k)*.09,z0,.10,2.3,.10,.04*k,0,.08*k)}
   const brace=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(brace)setBox(brace,x0+.75,.46,z0+.04,.10,1.7,.10,.6,0,1.08);
   if(torus){const ring=push(vs,mesh(vs,torus,accent?.clone?.()||accent));if(ring){ring.position.set(x0,2.45,z0);ring.rotation.x=Math.PI/2;ring.scale.setScalar(1.15);ring.material.opacity=.28}}
  }else if(source===2){
   const spine=push(vs,mesh(vs,box,base?.clone?.()||base));if(spine)setBox(spine,x0,1.72,z0,.26,4.25,.26,.12,0,-1.03*side);
   for(const k of [-1,1]){const cross=push(vs,mesh(vs,box,(k>0?accent:dark)?.clone?.()||(k>0?accent:dark)));if(cross)setBox(cross,x0+k*.9,1.22+k*.20,z0+.02,.15,1.85,.15,.48*k,0,.90*k)}
   if(ico){for(let i=0;i<4;i++){const sh=push(vs,mesh(vs,ico,accent?.clone?.()||accent));if(sh){sh.position.set(x0+Math.sin(i*1.7)*1.1,.20+i*.20,z0+.35+Math.cos(i*1.7)*.55);sh.scale.setScalar(.20+i*.045);sh.rotation.set(i*.5,i*.9,.2)}}}
  }else{
   for(const k of [-1,1]){const col=push(vs,mesh(vs,box,base?.clone?.()||base));if(col)setBox(col,k*3.55,1.36,z0+.25,.46,2.55,.46,.08*k,0,k*.22);const cap=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(cap)setBox(cap,k*3.05,.32,z0+.35,.72,.20,.72,.16*k,.3,k*.24)}
   for(let i=0;i<5;i++){const crack=push(vs,mesh(vs,box,dark?.clone?.()||dark));if(crack)setBox(crack,(i-2)*.36,.035,-2.7-i*.48,.055,.025,.86,.03*i,(i-2)*.09,0)}
   if(torus){const halo=push(vs,mesh(vs,torus,accent?.clone?.()||accent));if(halo){halo.position.set(0,.05,-4.6);halo.rotation.x=Math.PI/2;halo.scale.setScalar(1.55);halo.material.opacity=.22}}
  }
  vs.__mbDestructionRoute.key=`${routeLevel}:${entry.serial}`;s.routeLevel=routeLevel;s.routeSource=source;s.routeName=ROUTE[source];s.routeBuilds++;s.routeMeshes=vs.__mbDestructionRoute.meshes.length;
 }
 function update(vs){record(window.__mirrorBreakV9State?.stageHit);if(!vs.__mbDestructionRoute)vs.__mbDestructionRoute={key:'',meshes:[]};const entry=active();const key=entry?`${level}:${entry.serial}`:'';if(!entry){if(vs.__mbDestructionRoute.key||vs.__mbDestructionRoute.meshes.length)cleanup(vs);s.routeLevel=-1;s.routeSource=-1;s.routeName=null;return}if(vs.__mbDestructionRoute.key!==key){cleanup(vs);build(vs,entry)}}
 const baseRender=proto.render;proto.render=function(renderState){update(this);return baseRender.call(this,renderState)};
 // Route geometry also changes the next boss' neutral movement. No input, hitbox or attack timing is rewritten:
 // the carry-over only creates a recognizable lane/orbit pressure that the player can exploit.
 const baseUpdateEnemy=updateEnemy;updateEnemy=function(dt){const out=baseUpdateEnemy(dt),entry=active();if(!entry||mode!=='play'||!boss||!player||boss.hp<=0||player.hp<=0||boss.wind>0||boss.strike>0||boss.stun>0||boss.down>0)return out;const source=entry.level,to=V(player.pos.x-boss.pos.x,0,player.pos.z-boss.pos.z),dist=Math.hypot(to.x,to.z)||1,forward=V(to.x/dist,0,to.z/dist),tangent=V(forward.z,0,-forward.x),side=source%2?1:-1;let tag='',amount=0;
  if(source===0){amount=.42;tag='GATE ORBIT';boss.vel.x+=tangent.x*side*amount;boss.vel.z+=tangent.z*side*amount}
  else if(source===1){amount=.55;tag='BREACH FLANK';boss.vel.x+=tangent.x*side*amount;boss.vel.z+=tangent.z*side*amount;if(dist>4.8){boss.vel.x*=1.035;boss.vel.z*=1.035}}
  else if(source===2){const inSpine=Math.abs(boss.pos.x)<1.45&&boss.pos.z<-.45;if(inSpine){amount=.14;tag='SPINE CHOKE';boss.vel.x*=.84;boss.vel.z*=.84;boss.vel.x+=side*.16}else{amount=.26;tag='SPINE ARC';boss.vel.x+=tangent.x*side*.26;boss.vel.z+=tangent.z*side*.26}}
  else{const inRift=Math.abs(boss.pos.x)<.95&&boss.pos.z<-1.45;if(inRift){amount=.52;tag='RIFT SPLIT';boss.vel.x+=side*.52}else{amount=.30;tag='RIFT ORBIT';boss.vel.x+=tangent.x*side*.30;boss.vel.z+=tangent.z*side*.30}}
  s.pressureTicks++;s.lastPressure={source,name:ROUTE[source],tag,amount:+amount.toFixed(2),side,dist:+dist.toFixed(2),vx:+boss.vel.x.toFixed(3),vz:+boss.vel.z.toFixed(3)};return out};
 const baseReset=reset;reset=function(l=0){record(window.__mirrorBreakV9State?.stageHit);const prev=typeof level==='number'?level:-1,out=baseReset(l);if(l===0&&prev>=4){s.history.length=0;s.lastSerial=0;s.routeLevel=-1;s.routeSource=-1;s.routeName=null;s.pressureTicks=0;s.lastPressure=null}return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v12:true,destructionRoute:true,routeHistory:s.history.map(e=>({...e})),routeHistoryCount:s.history.length,routeLevel:s.routeLevel,routeSource:s.routeSource,routeName:s.routeName,routeMeshes:s.routeMeshes,routeBuilds:s.routeBuilds,routePressureTicks:s.pressureTicks,routePressure:s.lastPressure,routeLaneSide:s.routeLaneSide}};
 window.parryDestructionRouteDiagnostics=()=>({v12:true,history:s.history.map(e=>({...e})),level:s.routeLevel,source:s.routeSource,name:s.routeName,meshes:s.routeMeshes,builds:s.routeBuilds,pressureTicks:s.pressureTicks,pressure:s.lastPressure,laneSide:s.routeLaneSide});
})();
