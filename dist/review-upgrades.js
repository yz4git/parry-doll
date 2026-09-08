'use strict';
// Product-pass presentation overrides are kept separate from the combat core.
const reviewStyle=document.createElement('style');
reviewStyle.textContent=`
#toast{top:18%;font-size:clamp(16px,2.8vw,24px);letter-spacing:2.5px;text-shadow:0 2px 10px #000}
#cue{top:27%;font-size:clamp(14px,2.5vw,18px);letter-spacing:3px;text-shadow:0 2px 10px #000}
@media(max-height:500px){#toast{top:17%}#cue{top:26%}}
`;
document.head.appendChild(reviewStyle);
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

const REVIEW_PREP={
 '二連・袈裟返し':{twist:-.48,crouch:.05,lean:-.08,hand:[1.02,2.18,-.38],elbow:[.92,1.92,-.30]},
 '踏み込み突き':{twist:.18,crouch:.18,lean:-.30,hand:[.42,1.28,-.78],elbow:[.78,1.48,-.58]},
 '溜め・一刀落とし':{crouch:.12,lean:-.18,hand:[.10,3.08,-.38],elbow:[.66,2.42,-.34],twoHand:true},
 '横歩き・逆薙ぎ':{twist:.78,crouch:.08,lean:.08,hand:[-1.02,1.18,.10],elbow:[-.42,1.52,.16]},
 '二連噛み':{xScale:.86,zScale:.94,crouch:.18,headZ:-.42,frontRetract:.28},
 '跳びかかり':{xScale:.70,zScale:.72,crouch:.52,headZ:-.28,allLegPull:.32},
 '牙の直進突撃':{xScale:.82,zScale:1.06,crouch:.34,headZ:.18,frontRetract:.46},
 '尾の回転薙ぎ':{xScale:1.28,zScale:1.08,crouch:.10,twist:.82},
 '双脚刺突':{xScale:1.16,crouch:.10,headZ:-.22,frontRetract:.82,frontLift:.20},
 '八脚回転':{xScale:1.48,zScale:1.08,crouch:.13,twist:.92},
 '天蓋落とし':{xScale:.64,zScale:.68,crouch:.48,headZ:-.22,allLegPull:.38},
 '三連脚槍':{xScale:1.28,zScale:.90,crouch:.18,frontRetract:.56,legWave:.26},
 '鐘砕き・溜め落とし':{crouch:.10,lean:-.14,hand:[.08,3.28,-.45],elbow:[.74,2.56,-.42],twoHand:true},
 '大薙ぎ':{twist:-.82,crouch:.08,hand:[1.32,1.18,-.16],elbow:[.98,1.48,-.22]},
 '震脚':{crouch:.12,stomp:.92,hand:[.58,1.55,.12],elbow:[.72,1.72,.02]},
 '巨腕の押し込み':{twist:.12,crouch:.34,lean:-.38,hand:[.92,1.42,.74],elbow:[.82,1.58,.46]}
};
function reviewPrepTarget(d,n,p,move,wind){
 const r=REVIEW_PREP[move.name];if(!r)return p;const s=d.spec.scale,t=wind*wind*(3-2*wind);
 if(r.hand&&n.name==='hand')return add(p,mul(sub(mul(V(...r.hand),s),p),t));
 if(r.elbow&&n.name==='elbow'&&n.rest.x>0)return add(p,mul(sub(mul(V(...r.elbow),s),p),t));
 if(r.twoHand&&n.name==='offhand'){const h=mul(V(...r.hand),s),q=add(h,V(-.20*s,-.08*s,-.08*s));return add(p,mul(sub(q,p),t));}
 p.y-=(r.crouch||0)*t*s;p.z+=(r.lean||0)*t*s;
 if(r.xScale)p.x*=1+(r.xScale-1)*t;if(r.zScale)p.z*=1+(r.zScale-1)*t;
 if(r.twist){const a=r.twist*t,c=Math.cos(a),sn=Math.sin(a),x=p.x,z=p.z;p.x=x*c+z*sn;p.z=-x*sn+z*c;}
 if(n.name==='head')p.z+=(r.headZ||0)*t*s;
 if(n.name==='foot'||n.name==='knee'){
  const front=n.rest.z>.18*s;
  if(r.allLegPull){p.x*=1-r.allLegPull*t;p.z*=1-r.allLegPull*t*.72;}
  if(front){p.z-=(r.frontRetract||0)*t*s;p.y+=(r.frontLift||0)*t*s;}
  if(r.legWave)p.y+=Math.sign(n.rest.x||1)*Math.sign(n.rest.z||1)*r.legWave*t*s;
  if(r.stomp&&n.rest.x>0)p.y+=r.stomp*t*s;
 }
 return p;
}
enemyPoseTarget=function(d,n){
 const move=enemyMove(d),p=d.spec.type==='human'?poseTarget(d,n):{...n.rest},scale=d.spec.scale;
 const wind=d.wind>0?1-clamp(d.wind/(d.windDuration||move.wind),0,1):0;
 const action=d.strike>0?clamp(d.strikeElapsed/move.active,0,1):0;
 const lift=move.kind==='leap'&&d.strike>0?Math.sin(Math.PI*clamp(action/.82,0,1))*1.9:0;
 if(d.wind>0)return reviewPrepTarget(d,n,p,move,clamp(wind*1.35,0,1));
 if(d.strike>0){
  if(move.kind==='thrust'&&(n.name==='head'||n.name==='knee'))p.z+=Math.sin(action*Math.PI)*.65*scale;
  if(move.kind==='stomp'&&(n.name==='foot'||n.name==='knee')&&n.rest.x>0)p.y+=Math.max(0,Math.sin(action*Math.PI*2))*.9*scale;
  if(move.kind==='combo'&&d.spec.type!=='human'&&n.name==='head')p.z+=Math.sin(action*Math.PI*move.hits.length*2)*.45*scale;
  if(move.kind==='sweep'){const a=action*Math.PI*1.8,c=Math.cos(a),sn=Math.sin(a),x=p.x;p.x=x*c+p.z*sn;p.z=-x*sn+p.z*c;}
 }
 p.y+=lift;return p;
};
