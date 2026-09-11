'use strict';
// MIRROR BREAK v10 — STAGE DESTRUCTION: KO landing points leave persistent 3D scars and broken architecture.
(()=>{
 if(window.__parryMirrorBreakV10Loaded)return;window.__parryMirrorBreakV10Loaded=true;
 const proto=window.ParryVisual?.VisualScene?.prototype;if(!proto)return;
 const stageState={events:0,lastSerial:0,lastType:null,lastLevel:-1,meshCount:0};window.__mirrorBreakV10State=stageState;
 const TYPE=['DOJO BEAM BREAK','DUNGEON CAGE BREAK','BELFRY SPINE BREAK','ALTAR COLUMN COLLAPSE'];
 const PAL=[['#211713','#9a5935','#ffad58'],['#0d1c1f','#4d7774','#83dfcf'],['#171020','#654b7d','#d6a7ff'],['#131a24','#53677e','#abd9ff']];
 function find(root,pred){let hit=null;root?.traverse?.(o=>{if(!hit&&pred(o))hit=o});return hit}
 function cleanup(vs){const d=vs.__mbStageDamage;if(!d)return;for(const m of d.meshes||[]){vs.scene.remove(m);try{m.material?.dispose?.()}catch{}try{m.geometry?.dispose?.()}catch{}}d.meshes=[];d.level=level;d.serial=0;stageState.meshCount=0}
 function material(vs,color,opacity=1,glow=false){const base=(vs.floor?.material||find(vs.scene,o=>o.isMesh&&o.material)?.material);if(!base?.clone)return null;const m=base.clone();m.color?.set?.(color);if('metalness'in m)m.metalness=glow ? .45 : .32;if('roughness'in m)m.roughness=glow ? .34 : .78;if(m.emissive){m.emissive.set(glow?color:'#000000');m.emissiveIntensity=glow ? .45 : 0}m.transparent=opacity<1;m.opacity=opacity;m.depthWrite=opacity>.85;return m}
 function mesh(vs,geom,mat){const Mesh=vs.floor?.constructor||find(vs.scene,o=>o.isMesh&&!o.isInstancedMesh)?.constructor;if(!Mesh||!geom||!mat)return null;const m=new Mesh(geom.clone(),mat);m.castShadow=true;m.receiveShadow=true;m.frustumCulled=false;vs.scene.add(m);return m}
 function push(vs,m){if(!m)return null;vs.__mbStageDamage.meshes.push(m);stageState.meshCount=vs.__mbStageDamage.meshes.length;return m}
 function setBox(m,x,y,z,sx,sy,sz,rx=0,ry=0,rz=0){m.position.set(x,y,z);m.scale.set(sx,sy,sz);m.rotation.set(rx,ry,rz);return m}
 function buildDamage(vs,hit){
  const lvl=Math.max(0,Math.min(3,hit.level|0)),pal=PAL[lvl],box=find(vs.scene,o=>o.geometry?.type==='BoxGeometry')?.geometry,ico=find(vs.scene,o=>o.geometry?.type==='IcosahedronGeometry')?.geometry,torus=find(vs.scene,o=>o.geometry?.type==='TorusGeometry')?.geometry;if(!box)return;
  const x=Math.max(-9.5,Math.min(9.5,hit.x||0)),z=Math.max(-9.5,Math.min(9.5,hit.z||0)),angle=Math.atan2(x||Math.sin(lvl+1),z||Math.cos(lvl+1)),power=hit.power||1.5;
  const dark=material(vs,pal[0],.95),base=material(vs,pal[1],1),accent=material(vs,pal[2],.96,true);
  for(let i=0;i<10;i++){const a=angle+i*Math.PI/5+(i%2?.13:-.08),L=.72+((i*37)%5)*.19+power*.14,r=.28+L*.48;const m=push(vs,mesh(vs,box,dark?.clone?.()||dark));if(m)setBox(m,x+Math.sin(a)*r,.028,z+Math.cos(a)*r,.045,.022,L,a*.07,a,0)}
  for(let i=0;i<9;i++){const a=angle+i*2.399,r=.32+(i%4)*.30+power*.09,sz=.14+(i%3)*.09;const m=push(vs,mesh(vs,box,base?.clone?.()||base));if(m)setBox(m,x+Math.sin(a)*r,.08+sz*.24,z+Math.cos(a)*r,.14+(i%2)*.08,.10+sz*.27,sz,i*.31,a,i*.19)}
  if(torus){for(let i=0;i<2;i++){const r=push(vs,mesh(vs,torus,accent?.clone?.()||accent));if(r){r.position.set(x,.05+i*.01,z);r.rotation.x=Math.PI/2;r.rotation.z=angle+i*.46;r.scale.setScalar((.90+i*.50)*(1+power*.10));r.material.opacity=i?.30:.44}}}
  // Put the large broken prop beside, not behind, the fallen boss so it reads from the combat camera.
  const ox=Math.sin(angle),oz=Math.cos(angle),sx=oz,sz=-ox,side=(lvl%2?1:-1),px=x+ox*.45+sx*side*(2.05+power*.18),pz=z+oz*.45+sz*side*(2.05+power*.18);
  if(lvl===0){
   const beam=push(vs,mesh(vs,box,base?.clone?.()||base));if(beam)setBox(beam,px,.72,pz,.34,2.85,.35,.25,angle+.12,-1.12);
   const cap=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(cap)setBox(cap,px-sz*.95,.29,pz+sx*.95,.22,1.05,.23,.34,angle+.2,-1.26);
  }else if(lvl===1){
   for(let i=0;i<4;i++){const bar=push(vs,mesh(vs,box,base?.clone?.()||base));if(bar)setBox(bar,px+(i-1.5)*.34,.42+i*.08,pz,.095,1.72,.095,.25+i*.12,angle,-1.16+(i-1.5)*.16)}
   const brace=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(brace)setBox(brace,px,.19,pz,.09,1.25,.09,Math.PI/2,angle+.55,.4);
  }else if(lvl===2){
   const spine=push(vs,mesh(vs,box,base?.clone?.()||base));if(spine)setBox(spine,px,.92,pz,.21,3.25,.21,.18,angle,-.92);
   const cross=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(cross)setBox(cross,px-sz*.66,.42,pz+sx*.66,.13,1.48,.13,.5,angle+.3,1.02);
   if(ico){for(let i=0;i<4;i++){const shard=push(vs,mesh(vs,ico,accent?.clone?.()||accent));if(shard){shard.position.set(px+Math.sin(angle+i*1.57)*(.5+i*.13),.20+i*.13,pz+Math.cos(angle+i*1.57)*(.5+i*.13));shard.scale.setScalar(.19+i*.04);shard.rotation.set(i*.7,angle+i,.3)}}}
  }else{
   const column=push(vs,mesh(vs,box,base?.clone?.()||base));if(column)setBox(column,px,.88,pz,.62,2.95,.62,.13,angle,-1.08);
   const head=push(vs,mesh(vs,box,accent?.clone?.()||accent));if(head)setBox(head,px-sz*1.12,.32,pz+sx*1.12,.76,.28,.76,.18,angle+.2,.22);
   for(let i=0;i<4;i++){const slab=push(vs,mesh(vs,box,(i===0?accent:base)?.clone?.()||(i===0?accent:base)));if(slab)setBox(slab,x+Math.sin(angle+i*1.58)*(.62+i*.17),.11+i*.06,z+Math.cos(angle+i*1.58)*(.62+i*.17),.96,.11,.64,.08*i,angle+i*.5,(i-1.5)*.16)}
  }
  vs.__mbStageDamage.serial=hit.serial;stageState.events++;stageState.lastSerial=hit.serial;stageState.lastType=TYPE[lvl];stageState.lastLevel=lvl;stageState.meshCount=vs.__mbStageDamage.meshes.length;
 }
 function updateDamage(vs){if(!vs.__mbStageDamage)vs.__mbStageDamage={level,serial:0,meshes:[]};if(vs.__mbStageDamage.level!==level)cleanup(vs);const hit=window.__mirrorBreakV9State?.stageHit;if(hit&&hit.level===level&&hit.serial>vs.__mbStageDamage.serial)buildDamage(vs,hit);const age=hit?.time?Math.max(0,(performance.now()-hit.time)/1000):99;if(age<.85){const glow=1-age/.85;for(const m of vs.__mbStageDamage.meshes){if(m.material?.emissive&&m.material.emissiveIntensity>0)m.material.emissiveIntensity=.12+.50*glow}}}
 const baseRender=proto.render;proto.render=function(renderState){updateDamage(this);return baseRender.call(this,renderState)};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v10:true,stageDestruction:true,stageDamageEvents:stageState.events,stageDamageType:stageState.lastType,stageDamageLevel:stageState.lastLevel,stageDamageMeshes:stageState.meshCount}};
 window.parryBossDestructionStageDiagnostics=()=>({v10:true,events:stageState.events,type:stageState.lastType,level:stageState.lastLevel,meshes:stageState.meshCount,serial:stageState.lastSerial});
})();
