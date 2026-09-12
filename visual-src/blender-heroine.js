import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {HeroineRig,axes,solveJoint} from './heroine-rig.js';

const Y=new THREE.Vector3(0,1,0);
const TMP=new THREE.Vector3();
const INSTANCES=new Set();
// Measured from the user-provided four-view sheet, normalized to the Blender model's 2.42u nominal height.
// These are visual-only retarget values. Gameplay/PBD nodes remain untouched.
const REF_SHOULDER_HALF=.172;
const REF_HIP_HALF=.151;

// PORTRAIT_MATERIAL_V128: keep the exported PBR intent stable in Three.js/iPhone Safari.
function tunePortraitMaterials(root){
 const seen=new Set();
 root.traverse(o=>{
  if(!o.isMesh)return;
  const mats=Array.isArray(o.material)?o.material:[o.material];
  for(const m of mats){
   if(!m||seen.has(m))continue;seen.add(m);
   const n=(m.name||'').toLowerCase();
   if(n==='skin'){
    m.metalness=0;m.roughness=.62;m.envMapIntensity=.72;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.035);m.clearcoatRoughness=.70}
   }else if(n==='sclera'){
    m.metalness=0;m.roughness=.36;m.envMapIntensity=1.05;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.32);m.clearcoatRoughness=.18}
   }else if(n==='iris'||n==='iris inner'){
    m.metalness=0;m.roughness=.40;m.envMapIntensity=.92;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,n==='iris inner'?.22:.18);m.clearcoatRoughness=.20}
   }else if(n==='pupil'){
    m.metalness=0;m.roughness=.26;m.envMapIntensity=.70;
   }else if(n==='lip'){
    m.metalness=0;m.roughness=.40;m.envMapIntensity=.88;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.30);m.clearcoatRoughness=.24}
   }else if(n==='eye wetline'){
    m.metalness=0;m.roughness=.20;m.envMapIntensity=1.18;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.52);m.clearcoatRoughness=.12}
   }
   m.needsUpdate=true;
  }
 });
}

function referenceRetarget(d,base){
 const s=d.spec.scale,right=new THREE.Vector3(Math.cos(d.face),0,-Math.sin(d.face)),forward=new THREE.Vector3(Math.sin(d.face),0,Math.cos(d.face)),up=base.neck.clone().sub(base.pelvis).normalize();
 const p={};for(const [name,q] of Object.entries(base))p[name]=q.clone();
 p.shoulderL=p.chest.clone().addScaledVector(right,-REF_SHOULDER_HALF*s).addScaledVector(up,.010*s);
 p.shoulderR=p.chest.clone().addScaledVector(right, REF_SHOULDER_HALF*s).addScaledVector(up,.010*s);
 p.hipL=p.pelvis.clone().addScaledVector(right,-REF_HIP_HALF*s).addScaledVector(up,.004*s);
 p.hipR=p.pelvis.clone().addScaledVector(right, REF_HIP_HALF*s).addScaledVector(up,.004*s);
 for(const side of ['L','R']){
  const sign=side==='L'?-1:1;
  p['elbow'+side]=solveJoint(p['shoulder'+side],p['hand'+side],base['elbow'+side].clone().addScaledVector(right,sign*.050*s),.50*s,.50*s);
  p['knee'+side]=solveJoint(p['hip'+side],p['foot'+side],base['knee'+side].clone().addScaledVector(forward,.18*s),.62*s,.62*s);
 }
 return p;
}

export class BlenderHeroine{
 constructor(d,scene,{assetBase}){
  this.root=new THREE.Group();this.root.name='blender-heroine-runtime';scene.add(this.root);INSTANCES.add(this);
  this.driverRoot=new THREE.Group();this.rig=new HeroineRig(this.driverRoot);this.groups={};this.ready=false;this.failed='';this.weaponVisible=true;
  this.face={eyeL:null,eyeR:null,mouth:null,hair:null,lidL:null,lidR:null};this.expression={blink:0,modular:false,blinkReady:false,blinkOverride:null};
  this.weapon=new THREE.Group();this.weapon.name='blender-heroine-weapon-runtime';this.root.add(this.weapon);
  const url=new URL('assets/models/heroine-blender.glb',assetBase).href;
  new GLTFLoader().load(url,gltf=>{
   this.model=gltf.scene;this.model.name='blender-heroine-model';this.model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false}});tunePortraitMaterials(this.model);this.root.add(this.model);
   for(const name of ['BL_PELVIS','BL_TORSO','BL_HEAD','BL_UPPER_ARM_L','BL_FOREARM_L','BL_HAND_L','BL_UPPER_ARM_R','BL_FOREARM_R','BL_HAND_R','BL_THIGH_L','BL_SHIN_L','BL_FOOT_L','BL_THIGH_R','BL_SHIN_R','BL_FOOT_R'])this.groups[name]=this.model.getObjectByName(name)||null;
   this.face.eyeL=this.model.getObjectByName('BL_EYE_L')||null;this.face.eyeR=this.model.getObjectByName('BL_EYE_R')||null;this.face.mouth=this.model.getObjectByName('BL_MOUTH')||null;this.face.hair=this.model.getObjectByName('BL_HAIR_ASSET')||null;this.face.lidL=this.model.getObjectByName('BL_EYELID_L')||null;this.face.lidR=this.model.getObjectByName('BL_EYELID_R')||null;
   const lidReady=lid=>{const index=lid?.morphTargetDictionary?.Blink;return !!lid&&Number.isInteger(index)&&!!lid.morphTargetInfluences};
   this.expression.blinkReady=lidReady(this.face.lidL)&&lidReady(this.face.lidR);
   this.expression.modular=!!(this.face.eyeL&&this.face.eyeR&&this.face.mouth&&this.face.hair);
   const sword=this.model.getObjectByName('BL_SWORD');if(sword){sword.parent?.remove(sword);this.weapon.add(sword);sword.position.set(0,0,0);sword.quaternion.identity();sword.scale.set(1,1,1)}
   this.ready=Object.values(this.groups).every(Boolean);if(!this.ready)this.failed='Blender heroine is missing one or more runtime groups';this.weapon.visible=this.weaponVisible;
  },undefined,error=>{this.failed=String(error);console.warn('Blender heroine asset failed to load.',error)});
 }
 setWeaponVisible(value){this.weaponVisible=!!value;this.weapon.visible=this.weaponVisible}
 setBlinkOverride(value=null){this.expression.blinkOverride=value==null?null:THREE.MathUtils.clamp(Number(value)||0,0,1);if(this.expression.blinkOverride!=null)this.applyBlink(this.expression.blinkOverride)}
 applyBlink(value){const blink=THREE.MathUtils.clamp(value,0,1);for(const lid of [this.face.lidL,this.face.lidR]){const index=lid?.morphTargetDictionary?.Blink;if(Number.isInteger(index)&&lid.morphTargetInfluences)lid.morphTargetInfluences[index]=blink}this.expression.blink=blink}
 expressionState(){return{ready:this.ready,failed:this.failed,blink:this.expression.blink,blinkReady:this.expression.blinkReady,blinkOverride:this.expression.blinkOverride,lidL:!!this.face.lidL,lidR:!!this.face.lidR}}
 setPoint(name,point,quat,scale){const g=this.groups[name];if(!g)return;g.position.copy(point);g.quaternion.copy(quat);g.scale.setScalar(scale)}
 setSegment(name,a,b,face,widthScale){const g=this.groups[name];if(!g)return;const delta=b.clone().sub(a),length=delta.length();g.position.copy(a).lerp(b,.5);g.quaternion.copy(axes(delta,face));g.scale.set(widthScale,Math.max(.001,length),widthScale)}
 update(d,pose,clock=0){
  if(!this.ready)return;const s=d.spec.scale,points=referenceRetarget(d,this.rig.update(d)),torsoDir=points.neck.clone().sub(points.pelvis),torsoQ=axes(torsoDir,d.face);
  const torsoMid=points.pelvis.clone().lerp(points.neck,.5);this.setPoint('BL_PELVIS',points.pelvis,torsoQ,s);this.setPoint('BL_TORSO',torsoMid,torsoQ,s);this.setPoint('BL_HEAD',points.head,torsoQ,s);
  for(const side of ['L','R']){
   this.setSegment('BL_UPPER_ARM_'+side,points['shoulder'+side],points['elbow'+side],d.face,s);
   this.setSegment('BL_FOREARM_'+side,points['elbow'+side],points['hand'+side],d.face,s);
   this.setPoint('BL_HAND_'+side,points['hand'+side],axes(points['hand'+side].clone().sub(points['elbow'+side]),d.face),s);
   this.setSegment('BL_THIGH_'+side,points['hip'+side],points['knee'+side],d.face,s);
   this.setSegment('BL_SHIN_'+side,points['knee'+side],points['foot'+side],d.face,s);
   this.setPoint('BL_FOOT_'+side,points['foot'+side],torsoQ,s);
  }
  const hand=d.nodes.find(n=>n.name==='hand');if(hand&&this.weapon){TMP.set(pose.x,pose.y,pose.z);const bladeLength=TMP.length();TMP.applyAxisAngle(Y,d.face);this.weapon.position.set(hand.p.x,hand.p.y,hand.p.z);this.weapon.quaternion.setFromUnitVectors(Y,TMP.normalize());this.weapon.scale.set(s,s*bladeLength/1.51,s);this.weapon.visible=this.weaponVisible}
  const head=this.groups.BL_HEAD;if(head){
   const pony=head.getObjectByName('BL_PONY_DYNAMIC');if(pony){pony.rotation.x=Math.sin(clock*2.1)*.025-Math.min(.14,Math.hypot(d.vel?.x||0,d.vel?.z||0)*.014);pony.rotation.z=Math.sin(clock*1.7)*.035}
   if(this.expression.modular){
    let blink=0;
    if(this.expression.blinkOverride!=null)blink=this.expression.blinkOverride;
    else if(d.hp<=0)blink=1;
    else{
     const busy=(d.attack>0)||(d.parry>0)||(d.down>0)||(d.stun>0);
     if(!busy){const period=4.6,duration=.16,phase=((clock+.37)%period+period)%period;blink=phase<duration?Math.sin(Math.PI*phase/duration):0}
    }
    if(this.expression.blinkReady)this.applyBlink(blink);else{this.face.eyeL.scale.set(1,1,1);this.face.eyeR.scale.set(1,1,1);this.expression.blink=0}
   }
  }
 }
 dispose(){INSTANCES.delete(this);this.rig.dispose();this.root.traverse(o=>{if(o.isMesh){o.geometry?.dispose?.();const materials=Array.isArray(o.material)?o.material:[o.material];materials.filter(Boolean).forEach(m=>m.dispose?.())}});this.root.removeFromParent()}
}

window.ParryHeroineBlink={
 set:value=>{for(const h of INSTANCES)h.setBlinkOverride(value);return[...INSTANCES].map(h=>h.expressionState())},
 auto:()=>{for(const h of INSTANCES)h.setBlinkOverride(null);return[...INSTANCES].map(h=>h.expressionState())},
 state:()=>[...INSTANCES].map(h=>h.expressionState())
};
