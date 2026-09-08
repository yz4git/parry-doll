'use strict';
// Product-pass presentation overrides are kept separate from the combat core.
let reviewCine=0,reviewWasBroken=false;
setCamera=function(){
 const v=sub(boss.pos,player.pos),distance=Math.hypot(v.x,v.z),desired=Math.atan2(v.x,v.z);
 const smoothing=1-Math.exp(-feel.dt*5);
 if(!cameraRig.initialized){cameraRig.yaw=desired;cameraRig.initialized=true}
 else if(distance>.6)cameraRig.yaw+=clamp(angleDelta(desired,cameraRig.yaw),-2.1*feel.dt,2.1*feel.dt);
 const forward=V(Math.sin(cameraRig.yaw),0,Math.cos(cameraRig.yaw)),right=V(-forward.z,0,forward.x),portrait=W<H;
 const giant=Math.max(0,boss.spec.scale-1.3),lookAhead=Math.min(2.4,distance*.43);
 const desiredTarget=add(player.pos,add(mul(forward,lookAhead),V(0,1.28+giant*.5,0)));
 if(!Number.isFinite(target.x))target={...desiredTarget};
 target.x+=(desiredTarget.x-target.x)*smoothing;target.z+=(desiredTarget.z-target.z)*smoothing;target.y=desiredTarget.y;
 let back=(portrait?5.5:4.35)+Math.max(0,distance-4)*.18,shoulder=portrait?.65:1.9;
 const kick=feel.reduced?0:Math.min(.35,feel.zoom*.35);
 function positionCamera(){
  camera=add(player.pos,add(mul(forward,-back+kick),add(mul(right,shoulder),V(0,2.75+giant*.55+(back-4.35)*.16,0))));
  const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),up=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up};
 }
 positionCamera();
 for(let attempt=0;attempt<10;attempt++){
  const fits=[player,boss].every(d=>[V(d.pos.x,.1,d.pos.z),V(d.pos.x,d.nodes[2].rest.y+.28,d.pos.z)].every(p=>{const q=project(p);return q.z>.3&&q.x>W*.07&&q.x<W*.93&&q.y>H*.15&&q.y<H*.86}));
  if(fits)break;back+=.65;positionCamera();
 }
};
