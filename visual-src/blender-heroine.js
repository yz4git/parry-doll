import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {HeroineRig,axes} from './heroine-rig.js';

const Y=new THREE.Vector3(0,1,0);
const TMP=new THREE.Vector3();

export class BlenderHeroine{
 constructor(d,scene,{assetBase}){
  this.root=new THREE.Group();this.root.name='blender-heroine-runtime';scene.add(this.root);
  this.driverRoot=new THREE.Group();this.rig=new HeroineRig(this.driverRoot);this.groups={};this.ready=false;this.failed='';this.weaponVisible=true;
  this.weapon=new THREE.Group();this.weapon.name='blender-heroine-weapon-runtime';this.root.add(this.weapon);
  const url=new URL('assets/models/heroine-blender.glb',assetBase).href;
  new GLTFLoader().load(url,gltf=>{
   this.model=gltf.scene;this.model.name='blender-heroine-model';this.model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false}});this.root.add(this.model);
   for(const name of ['BL_PELVIS','BL_TORSO','BL_HEAD','BL_UPPER_ARM_L','BL_FOREARM_L','BL_HAND_L','BL_UPPER_ARM_R','BL_FOREARM_R','BL_HAND_R','BL_THIGH_L','BL_SHIN_L','BL_FOOT_L','BL_THIGH_R','BL_SHIN_R','BL_FOOT_R'])this.groups[name]=this.model.getObjectByName(name)||null;
   const sword=this.model.getObjectByName('BL_SWORD');if(sword){sword.parent?.remove(sword);this.weapon.add(sword);sword.position.set(0,0,0);sword.quaternion.identity();sword.scale.set(1,1,1)}
   this.ready=Object.values(this.groups).every(Boolean);if(!this.ready)this.failed='Blender heroine is missing one or more runtime groups';this.weapon.visible=this.weaponVisible;
  },undefined,error=>{this.failed=String(error);console.warn('Blender heroine asset failed to load.',error)});
 }
 setWeaponVisible(value){this.weaponVisible=!!value;this.weapon.visible=this.weaponVisible}
 setPoint(name,point,quat,scale){const g=this.groups[name];if(!g)return;g.position.copy(point);g.quaternion.copy(quat);g.scale.setScalar(scale)}
 setSegment(name,a,b,face,widthScale){const g=this.groups[name];if(!g)return;const delta=b.clone().sub(a),length=delta.length();g.position.copy(a).lerp(b,.5);g.quaternion.copy(axes(delta,face));g.scale.set(widthScale,Math.max(.001,length),widthScale)}
 update(d,pose,clock=0){
  if(!this.ready)return;const s=d.spec.scale,points=this.rig.update(d),torsoDir=points.neck.clone().sub(points.pelvis),torsoQ=axes(torsoDir,d.face);
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
  const head=this.groups.BL_HEAD;if(head){const pony=head.getObjectByName('BL_PONY_DYNAMIC');if(pony){pony.rotation.x=Math.sin(clock*2.1)*.025-Math.min(.14,Math.hypot(d.vel?.x||0,d.vel?.z||0)*.014);pony.rotation.z=Math.sin(clock*1.7)*.035}}
 }
 dispose(){this.rig.dispose();this.root.traverse(o=>{if(o.isMesh){o.geometry?.dispose?.();const materials=Array.isArray(o.material)?o.material:[o.material];materials.filter(Boolean).forEach(m=>m.dispose?.())}});this.root.removeFromParent()}
}
