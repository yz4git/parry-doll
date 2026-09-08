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
  scene.traverse(o=>{assert(o.matrixWorld.elements.every(Number.isFinite),'Non-finite model transform');if(frame===0&&o.geometry)assert(Array.from(o.geometry.attributes.position.array).every(Number.isFinite),'Non-finite geometry')});frames++;
 }
 assert(actors[0].hair.length>=8,'Missing layered hair');assert(actors[0].tails.length===2,'Missing split coat');actors.forEach(a=>a.dispose());
}
const html=fs.readFileSync(root+'dist/index.html','utf8');for(const [,path]of html.matchAll(/(?:src|href)\s*=\s*['"]\.\/([^?'"\s]+)[?'"]/g))assert(fs.existsSync(root+'dist/'+path),'Missing entry asset '+path);
console.log(`PASS: ${frames} model frames, four enemy rigs, finite geometry and transforms, read-only simulation inputs, local entry assets`);
