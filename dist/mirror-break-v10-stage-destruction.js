'use strict';
// MIRROR BREAK v10 — STAGE DESTRUCTION: KO landing points leave persistent 3D scars and broken architecture.
(()=>{
 if(window.__parryMirrorBreakV10Loaded)return;window.__parryMirrorBreakV10Loaded=true;
 const proto=window.ParryVisual?.VisualScene?.prototype;if(!proto)return;
 const stageState={events:0,lastSerial:0,lastType:null,lastLevel:-1,meshCount:0};window.__mirrorBreakV10State=stageState;
 const TYPE=['DOJO BEAM BREAK','DUNGEON CAGE BREAK','BELFRY SPINE BREAK','ALTAR COLUMN COLLAPSE'];
 const PAL=[['#34251f','#9a5935','#e19150'],['#142528','#527d79','#79c4b7'],['#241b31','#68527f','#c8a0eb'],['#202936','#56687b','#99c9f4']];
 function find(root,pred){let hit=null;root?.traverse?.(o=>{if(!hit&&pred(o))hit=o});return hit}
 function cleanup(vs){const d=vs.__mbStageDamage;if(!d)return;for(const m of d.meshes||[]){vs.scene.remove(m);try{m.material?.dispose?.()}catch{}try{m.geometry?.dispose?.()}catch{}}d.meshes=[];d.level=level;d.serial=0;stageState.meshCount=0}
 function material(vs,color,opacity=1,glow=false){const base=(vs.floor?.material||find(vs.scene,o=>o.isMesh&&o.material)?.material);if(!base?.clone)return null;const m=base.clone();m.color?.set?.(color);if('metalness'in m)m.metalness=glow?.45:.32;if('roughness'in m)m.roughness=glow?.34:.78;if(m.emissive){m.emissive.set(glow?color:'#000000');m.emissiveIntensity=glow?.45:0}m.transparent=opacity<1;m.opacity=opacity;m.depthWrite=opacity>.85;return m}
 function mesh(vs,geom,mat){const Mesh=vs.floor?.constructor||find(vs.scene,o=>o.isMesh&&!o.isInstancedMesh)?.constructor;if(!Mesh||!geom||!mat)return null;const m=new Mesh(geom.clone(),mat);m.castShadow=true;m.receiveShadow=true;m.frustumCulled=false;vs.scene.add(m);return m}
 function push(vs,m){if(!m)return null;vs.__mbStageDamage.meshes.push(m);stageState.meshCount=vs.__mbStageDamage.meshes.length;return m}
 function setBox(m,x,y,z,sx,sy,sz,rx=0,ry=0,rz=0){m.position.set(x,y,z);m.scale.set(sx,sy,sz);m.rotation.set(rx,ry,rz);return m}
 function buildDamage(vs,hit){
  const lvl=Math.max(0,Math.min(3,hit.level|0)),pal=PAL[lvl],box=find(vs.scene,o=>o.geometry?.type==='BoxGeometry')?.geometry,ico=find(vs.scene,o=>o.geometry?.type==='IcosahedronGeometry')?.geometry,torus=find(vs.scene,o=>o.geometry?.type==='TorusGeometry')?.geometry;if(!box)return;
  const x=Math.max(-10,Math.min(10,hit.x||0)),z=Math.max(-10,Math.min(10,hit.z||0)),angle=Math.atan2(x||Math.sin(lvl+1),z||Math.cos(lvl+1)),power=hit.power||1.5;
  const dark=material(vs,pal[0],.88),base=material(vs,pal[1],1),accent=material(vs,pal[2],.88,true);
  // A dark radial floor fracture stays after the boss has settled.
  for(let i=0;i<8;i++){const a=angle+i*Math.PI/4+(i%2?.13:-.08),L=.65+((i*37)%5)*.17+power*.12,r=.35+L*.48;const m=push(vs,mesh(vs,box,dark?.clone?.()||dark));if(m)setBox(m,x+Math.sin(a)*r,.025,z+Math.cos(a)*r,.035,.018,L,a*.07,a,0)}
  // Raised rubble gives the scar a physical silhouette in the WebGL scene.
  for(let i=0;i<7;i++){const a=angle+i*2.399,r=.35+(i%4)*.28+power*.08,sz=.12+(i%3)*.08;const m=push(vs,mesh(vs,box,base?.clone?.()||base));if(m)setBox(m,x+Math.sin(a)*r,.07+sz*.22,z+Math.cos(a)*r,.12+(i%2)*.06,.08+sz*.25,sz,i*.31,a,i*.19)}
  if(torus){for(let i=0;i<2;i++){const r=push(vs,mesh(vs,torus,accent?.clone?.()||accent));if(r){r.position.set(x,.045+i*.008,z);r.rotation.x=Math.PI/2;r.rotation.z=angle+i*.46;r.scale.setScalar((.72+i*.42)*(1+power*.08));r.material.opacity=i?.24:.36}}}
  const ox=Math.sin(angle),oz=Math.cos(angle),px=x+ox*(1.45+power*.12),pz=z+oz*(1.45+power*.12);
  if(lvl===0){
   const beam=push(vs,mesh(vs,box,base?.clone?.()||base));if(beam)setBox(beam,px,.58,pz,.26,2.15,.27,.18,angle,-1.05);
   const cap=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(cap)setBox(cap,px-oz*.72,.23,pz+ox*.72,.17,.78,.18,.30,angle+.2,-1.22);
  }else if(lvl===1){
   for(let i=0;i<3;i++){const bar=push(vs,mesh(vs,box,base?.clone?.()||base));if(bar)setBox(bar,px+(i-1)*.28,.34+i*.06,pz,.075,1.35,.075,.25+i*.12,angle,-1.18+(i-1)*.18)}
   const brace=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(brace)setBox(brace,px,.15,pz,.07,.95,.07,Math.PI/2,angle+.55,.4);
  }else if(lvl===2){
   const spine=push(vs,mesh(vs,box,base?.clone?.()||base));if(spine)setBox(spine,px,.76,pz,.16,2.65,.16,.15,angle,-.88);
   const cross=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(cross)setBox(cross,px-oz*.48,.34,pz+ox*.48,.10,1.15,.10,.5,angle+.3,1.02);
   if(ico){for(let i=0;i<3;i++){const shard=push(vs,mesh(vs,ico,accent?.clone?.()||accent));if(shard){shard.position.set(px+Math.sin(angle+i*2.1)*(.45+i*.16),.18+i*.12,pz+Math.cos(angle+i*2.1)*(.45+i*.16));shard.scale.setScalar(.16+i*.035);shard.rotation.set(i*.7,angle+i,.3)}}}
  }else{
   const column=push(vs,mesh(vs,box,base?.clone?.()||base));if(column)setBox(column,px,.70,pz,.48,2.25,.48,.12,angle,-1.02);
   for(let i=0;i<3;i++){const slab=push(vs,mesh(vs,box,(i===0?accent:base)?.clone?.()||(i===0?accent:base)));if(slab)setBox(slab,x+Math.sin(angle+i*2.05)*(.55+i*.18),.10+i*.06,z+Math.cos(angle+i*2.05)*(.55+i*.18),.82,.09,.55,.08*i,angle+i*.5,(i-1)*.18)}
  }
  vs.__mbStageDamage.serial=hit.serial;stageState.events++;stageState.lastSerial=hit.serial;stageState.lastType=TYPE[lvl];stageState.lastLevel=lvl;stageState.meshCount=vs.__mbStageDamage.meshes.length;
 }
 function updateDamage(vs){
  if(!vs.__mbStageDamage)vs.__mbStageDamage={level,serial:0,meshes:[]};if(vs.__mbStageDamage.level!==level)cleanup(vs);
  const hit=window.__mirrorBreakV9State?.stageHit;if(hit&&hit.level===level&&hit.serial>vs.__mbStageDamage.serial)buildDamage(vs,hit);
  const age=hit?.time?Math.max(0,(performance.now()-hit.time)/1000):99;if(age<.75){const glow=1-age/.75;for(const m of vs.__mbStageDamage.meshes){if(m.material?.emissive&&m.material.emissiveIntensity>0)m.material.emissiveIntensity=.10+.45*glow}}
 }
 const baseRender=proto.render;proto.render=function(renderState){updateDamage(this);return baseRender.call(this,renderState)};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v10:true,stageDestruction:true,stageDamageEvents:stageState.events,stageDamageType:stageState.lastType,stageDamageLevel:stageState.lastLevel,stageDamageMeshes:stageState.meshCount}};
 window.parryBossDestructionStageDiagnostics=()=>({v10:true,events:stageState.events,type:stageState.lastType,level:stageState.lastLevel,meshes:stageState.meshCount,serial:stageState.lastSerial});
})();
