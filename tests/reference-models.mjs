import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url)),noop=()=>{},els=new Map();
function element(id=''){if(els.has(id))return els.get(id);const e={id,style:{},classList:{add:noop,remove:noop},addEventListener:noop,setAttribute:noop,appendChild:noop,getContext:()=>new Proxy({createLinearGradient:()=>({addColorStop:noop})},{get:(o,k)=>o[k]||noop}),querySelector:()=>element(id+'child')};els.set(id,e);return e}
const doc={getElementById:element,createElement:()=>element('e'+els.size),head:element('head'),body:element('body'),addEventListener:noop,querySelectorAll:()=>[]};
const c={console,Math,Number,Set,innerWidth:1000,innerHeight:600,devicePixelRatio:1,document:doc,window:{},addEventListener:noop,requestAnimationFrame:noop};vm.createContext(c);
for(const f of ['game.js','review-upgrades.js','damage-reactions.js','hit-location-reactions.js','combat-readability.js','combat-flow.js','combat-product-pass.js','combat-polish-v2.js'])vm.runInContext(fs.readFileSync(root+'dist/'+f,'utf8'),c);
globalThis.window={};globalThis.location={href:'file://'+root+'dist/index.html'};globalThis.document={currentScript:{src:'file://'+root+'dist/visual-engine.js'},createElementNS(){const events={};return{addEventListener(n,f){events[n]=f},removeEventListener:noop,set src(s){queueMicrotask(()=>events.load?.call(this))}}}};
const THREE=await import('../visual-src/node_modules/three/build/three.module.js');const {Actor}=await import('../visual-src/engine.js');const {makeEnvironment}=await import('../visual-src/environment.js');
const mats=Object.fromEntries(['skin','hair','porcelain','metal','cloth','glow'].map(k=>[k,new THREE.MeshStandardMaterial({vertexColors:true})]));
let frames=0;
for(let l=0;l<4;l++){
 vm.runInContext(`reset(${l});mode='play'`,c);const scene=new THREE.Scene(),env=makeEnvironment(scene,new URL('file://'+root+'dist/'));let actors;
 for(let frame=0;frame<300;frame++){
  vm.runInContext(`if(${frame}%40===0)playerAttack();if(${frame}%67===0)playerParry();updateFeel(1/60);step(1/60)`,c);
  const state=JSON.parse(vm.runInContext('JSON.stringify({player,boss,poses:[IDLE_POSE.blade,IDLE_POSE.blade]})',c));const before=JSON.stringify(state);
  if(!actors)actors=[state.player,state.boss].map(d=>new Actor(d,scene,mats));
  actors.forEach((a,i)=>a.update(i?state.boss:state.player,state.poses[i],frame/60));env.update(frame/60);scene.updateMatrixWorld(true);
  assert.equal(JSON.stringify(state),before,'Render actor mutated its simulation input');
  const hero=actors[0],rig=hero.rig;
  if(rig){assert.equal(rig.skeleton.bones.length,17);for(const side of ['L','R']){const hand=state.player.nodes.find(n=>n.name===(side==='L'?'offhand':'hand'));assert(rig.world['hand'+side].distanceTo(new THREE.Vector3(hand.p.x,hand.p.y,hand.p.z))<1e-8,'Wrist endpoint changed');const foot=state.player.nodes.find(n=>n.name==='foot'&&Math.sign(n.rest.x)===(side==='L'?-1:1));assert(rig.world['foot'+side].distanceTo(new THREE.Vector3(foot.p.x,foot.p.y,foot.p.z))<1e-8,'Foot endpoint changed');}
   const g=hero.body.geometry,point=new THREE.Vector3();for(let i=0;i<g.attributes.position.count;i+=53){hero.body.getVertexPosition(i,point);assert(point.toArray().every(Number.isFinite),'Non-finite skinned vertex');assert(point.distanceTo(rig.world.pelvis)<6,'Exploded skin binding');}
   if(frame===0){const w=g.attributes.skinWeight;for(let i=0;i<w.count;i++)assert(Math.abs(w.getX(i)+w.getY(i)+w.getZ(i)+w.getW(i)-1)<1e-5,'Bad skin weights');let sideIndex=0,maxX=-Infinity;for(let j=0;j<g.attributes.position.count;j++){const y=g.attributes.position.getY(j),x=g.attributes.position.getX(j);if(y>1.45&&y<1.9&&x>maxX){maxX=x;sideIndex=j}}assert(g.attributes.normal.getX(sideIndex)>0,'Inward body surface');}
  }
  scene.traverse(o=>{assert(o.matrixWorld.elements.every(Number.isFinite),'Non-finite model transform');if(frame===0&&o.geometry)assert(Array.from(o.geometry.attributes.position.array).every(Number.isFinite),'Non-finite geometry')});frames++;
 }
 assert(actors[0].hair.length>=8,'Missing layered hair');assert(actors[0].tails.length===1&&actors[0].skirt,'Missing split combat skirt');
 const skirt=actors[0].skirt,yoke=skirt.children.find(m=>m.name==='high-waist-yoke'),left=skirt.children.find(m=>m.name==='rear-left'),right=skirt.children.find(m=>m.name==='rear-right'),trim=skirt.children.find(m=>m.name==='waist-trim');assert(yoke&&left&&right&&trim,'Missing streamlined split skirt');assert(!skirt.children.some(m=>m.name==='side-left'||m.name==='side-right'),'Legacy side tabs returned');
 assert.equal(skirt.name,'split-combat-skirt');yoke.geometry.computeBoundingBox();left.geometry.computeBoundingBox();right.geometry.computeBoundingBox();
 assert(yoke.geometry.boundingBox.max.y>.38&&yoke.geometry.boundingBox.min.y<.17,'High-cut yoke profile collapsed');assert(left.geometry.boundingBox.max.x<-.34&&right.geometry.boundingBox.min.x>.34,'Rear panels close the centre leg gap');assert(left.geometry.boundingBox.min.y<-1.1&&right.geometry.boundingBox.min.y<-1.1,'Rear panels too short to create vertical leg lines');
 for(const panel of [left,right]){const pos=panel.geometry.attributes.position,base=panel.userData.base,normal=panel.geometry.attributes.normal,count=6;const mid=Math.floor(pos.count*.5);assert(normal.getZ(mid)<-.25,'Rear panel outer face does not face the rear camera');for(let i=0;i<pos.count;i++)assert(Number.isFinite(pos.getX(i)+pos.getY(i)+pos.getZ(i)),'Non-finite skirt panel');for(let i=0;i<count;i++)assert(Math.abs(pos.getY(i)-base[i*3+1])<.05,'Panel waist attachment drifted');const topXs=[],bottomXs=[];for(let i=0;i<count;i++){topXs.push(base[i*3]);const j=pos.count-count+i;bottomXs.push(base[j*3])}assert(Math.max(...bottomXs)-Math.min(...bottomXs)<Math.max(...topXs)-Math.min(...topXs)*.75+Math.min(...topXs)*-.75,'Rear panel does not taper strongly enough');}
 actors.forEach(a=>a.dispose());
}
const html=fs.readFileSync(root+'dist/index.html','utf8');for(const [,path]of html.matchAll(/(?:src|href)\s*=\s*['"]\.\/([^?'"\s]+)[?'"]/g))assert(fs.existsSync(root+'dist/'+path),'Missing entry asset '+path);
console.log(`PASS: ${frames} model frames, four enemy rigs, finite geometry and transforms, read-only simulation inputs, skin binding/weights, wrist/ankle endpoints, outward surfaces, local entry assets`);
