'use strict';
// Final combat polish v2: true executions, camera dead-zone, split lower-body facing and tighter hit glows.
let p6Execution=false,p6CameraYaw=Number.NaN;
const P6_CAM_DEADZONE=.17; // ~10 degrees: let fighters travel on screen before camera follows.

// A posture-break finisher is a true execution. It may never flow into an enraged survivor.
const p6HurtBase=hurt;
hurt=function(d,amount,force,point){
 if(p6Execution&&d===boss&&d.hp>0)amount=Math.max(amount,d.hp);
 return p6HurtBase(d,amount,force,point);
};
const p6ResolveSwingBase=resolveSwing;
resolveSwing=function(){
 const move=player.swing;
 p6Execution=!!(move&&move.finisher&&boss.broken>0);
 try{return p6ResolveSwingBase();}
 finally{p6Execution=false}
};

// Keep the upper body locked to the opponent while the legs retain movement inertia.
const p6PoseTargetBase=poseTarget;
poseTarget=function(d,n){
 let p=p6PoseTargetBase(d,n);
 if(!d.player||!Number.isFinite(d.p6LowerYaw)||!['knee','foot'].includes(n.name))return p;
 const delta=clamp(angleDelta(d.p6LowerYaw,d.face),-.68,.68),c=Math.cos(delta),s=Math.sin(delta),x=p.x,z=p.z;
 p={...p,x:x*c+z*s,z:-x*s+z*c};
 if(n.name==='foot')p.z+=Math.sin(delta)*Math.sign(n.rest.x||1)*.10*d.spec.scale;
 return p;
};
const p6PhysicsBase=Doll.prototype.physics;
Doll.prototype.physics=function(dt){
 if(this.player&&mode==='play'&&this.hp>0&&this.down<=0){
  const speed=Math.hypot(this.vel.x,this.vel.z),upper=this.face;
  if(!Number.isFinite(this.p6LowerYaw))this.p6LowerYaw=upper;
  let desired=upper,rate=1.35;
  if(speed>.30){desired=Math.atan2(this.vel.x,this.vel.z);rate=this.attack>0?2.15:3.15}
  const err=angleDelta(desired,this.p6LowerYaw),step=Math.min(Math.abs(err),rate*dt);
  this.p6LowerYaw+=Math.sign(err)*step;
 }
 return p6PhysicsBase.call(this,dt);
};

// Replace the stacked camera wrappers with a final composition that preserves all prior cinematic beats,
// but adds yaw dead-zone and body-type framing without immediately recentering every orbit step.
setCamera=function(){
 if(boss.broken>0&&!reviewWasBroken){reviewCine=.95;hitstop=Math.max(hitstop,.11);shake=Math.max(shake,.30)}
 reviewWasBroken=boss.broken>0;reviewCine=Math.max(0,reviewCine-feel.dt);
 const cine=clamp(reviewCine/.95,0,1)*(feel.reduced?.45:1);
 const v=sub(boss.pos,player.pos),distance=Math.hypot(v.x,v.z),desired=Math.atan2(v.x,v.z);
 if(!Number.isFinite(p6CameraYaw))p6CameraYaw=Number.isFinite(cameraRig.yaw)?cameraRig.yaw:desired;
 if(!cameraRig.initialized){p6CameraYaw=desired;cameraRig.initialized=true}
 const yawErr=angleDelta(desired,p6CameraYaw),dead=cine>0?.055:P6_CAM_DEADZONE;
 if(Math.abs(yawErr)>dead){
  const chase=desired-Math.sign(yawErr)*dead,maxRate=(cine>0?2.9:1.85)*feel.dt;
  p6CameraYaw+=clamp(angleDelta(chase,p6CameraYaw),-maxRate,maxRate);
 }
 cameraRig.yaw=p6CameraYaw;
 const forward=V(Math.sin(p6CameraYaw),0,Math.cos(p6CameraYaw)),right=V(-forward.z,0,forward.x),portrait=W<H;
 const giant=Math.max(0,boss.spec.scale-1.3),lookAhead=Math.min(2.4,distance*.43);
 const normalTarget=add(player.pos,add(mul(forward,lookAhead),V(0,1.28+giant*.5,0)));
 const bossFocus=add(boss.pos,V(0,1.20+giant*.62,0));
 let desiredTarget=add(mul(normalTarget,1-cine*.72),mul(bossFocus,cine*.72));
 const smoothing=1-Math.exp(-feel.dt*(cine>0?9:5));
 if(!Number.isFinite(target.x))target={...desiredTarget};
 target.x+=(desiredTarget.x-target.x)*smoothing;target.z+=(desiredTarget.z-target.z)*smoothing;target.y+=(desiredTarget.y-target.y)*smoothing;

 let back=(portrait?5.5:4.35)+Math.max(0,distance-4)*.18-(portrait?.28:.62)*cine;
 let shoulder=(portrait?.65:1.9)+(portrait?.05:.16)*cine;
 let typeUp=0,typeBack=0,typeSide=0;
 if(boss.spec.type==='beast'){typeUp=.68;typeBack=.28;typeSide=.82}
 else if(boss.spec.type==='spider'){typeUp=.88;typeBack=.52;typeSide=.52}
 else if(boss.spec.scale>1.8){typeUp=.10;typeBack=.28;typeSide=.12}
 back+=typeBack;shoulder+=typeSide*(level%2?-1:1);
 const active=player.attack>0||boss.strike>0||boss.broken>0||player.counter>0;
 let contact=clamp((3.40-distance)/1.70,0,1)*(active?1:.45);
 if(boss.spec.scale>1.8)contact*=.66;
 const heavyBeat=player.attack>0&&player.motion===2?1.75:1;
 shoulder+=(W<H?.30:1.05)*contact*(level%2?-.82:1)*heavyBeat;
 const kick=feel.reduced?0:Math.min(.35,feel.zoom*.35);
 function positionCamera(){
  camera=add(player.pos,add(mul(forward,-back+kick),add(mul(right,shoulder),V(0,2.75+giant*.55+(back-4.35)*.16+typeUp,0))));
  const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),u=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up:u};
 }
 positionCamera();
 // Giants may crop feet slightly; keeping the torso large matters more than fitting every extremity.
 for(let attempt=0;attempt<9;attempt++){
  const fits=[player,boss].every(d=>{
   const foot=project(V(d.pos.x,.1,d.pos.z)),head=project(V(d.pos.x,d.nodes[2].rest.y+.28,d.pos.z));
   const bottom=d===boss&&boss.spec.scale>1.8?H*1.07:H*.88;
   return head.z>.3&&foot.z>.3&&head.x>W*.06&&head.x<W*.94&&head.y>H*.10&&foot.y<bottom;
  });
  if(fits)break;back+=boss.spec.scale>1.8?.34:.58;positionCamera();
 }
};

// Suppress the larger earlier hit glow and redraw a smaller node-local spark so the reaction silhouette stays visible.
const p6DrawDollBase=drawDoll;
drawDoll=function(d){
 const hitT=d.hitRegionT||0,localized=hitT>0&&d.hp>0,savedInv=d.invuln;
 if(localized){d.hitRegionT=0;d.invuln=0}
 p6DrawDollBase(d);
 if(localized){
  d.hitRegionT=hitT;d.invuln=savedInv;
  if(typeof hitNodeForRegion==='function'){
   const n=hitNodeForRegion(d,d.hitRegion,d.hitRegionSide);
   if(n){
    const pulse=Math.sin(clamp(hitT/(d.hitRegionMax||.3),0,1)*Math.PI),base=d.player?'#bffcf0':'#ffd39a';
    orb(n.p,Math.max(n.r*1.12,.125*d.spec.scale),base);
    if(pulse>.35)orb(add(n.p,V(0,.035*d.spec.scale,0)),Math.max(n.r*.42,.052*d.spec.scale),'#fff5d6');
   }
  }
 }else d.invuln=savedInv;
};

if(window.parryDoll&&window.parryDoll.snapshot){
 const p6SnapshotBase=window.parryDoll.snapshot;
 window.parryDoll.snapshot=()=>{
  const upper=Math.atan2(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z),lower=Number.isFinite(player.p6LowerYaw)?player.p6LowerYaw:player.face;
  return {...p6SnapshotBase(),cameraDeadzone:P6_CAM_DEADZONE,lowerBodyOffset:+angleDelta(lower,upper).toFixed(3),cameraYawOffset:+angleDelta(p6CameraYaw,upper).toFixed(3)};
 };
}
