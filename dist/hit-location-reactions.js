'use strict';
// Hit-location reactions: choose an actual body zone, then layer a local pose response on top of damage severity.
const hitLocationPreviousHurt=hurt;
const hitLocationPreviousResolveSwing=resolveSwing;
const hitLocationPreviousEnemyImpact=enemyImpact;
const hitLocationBasePoseTarget=poseTarget;
const hitLocationBaseEnemyPoseTarget=enemyPoseTarget;
const hitLocationBaseUpdateFeel=updateFeel;
let hitLocationIntent=null;

function hitRegionName(n){
 if(!n)return 'torso';
 if(n.name==='head')return 'head';
 if(n.name==='shoulder'||n.name==='elbow'||n.name==='hand'||n.name==='offhand')return 'arm';
 if(n.name==='knee'||n.name==='foot')return 'leg';
 return 'torso';
}
function hitNodeForRegion(d,region,side=0){
 let candidates=d.nodes.filter(n=>hitRegionName(n)===region);
 if(!candidates.length)candidates=d.nodes.filter(n=>hitRegionName(n)==='torso');
 if(side&&candidates.some(n=>Math.sign(n.rest.x)===side))candidates=candidates.filter(n=>Math.sign(n.rest.x)===side);
 if(region==='head')return candidates.find(n=>n.name==='head')||candidates[0];
 if(region==='torso')return candidates.find(n=>n.name==='chest')||candidates.find(n=>n.name==='hip')||candidates[0];
 if(region==='arm')return candidates.find(n=>n.name==='shoulder')||candidates.find(n=>n.name==='elbow')||candidates[0];
 return candidates.find(n=>n.name==='knee')||candidates.find(n=>n.name==='foot')||candidates[0];
}
function pointSegmentDistance(p,a,b){
 const ab=sub(b,a),den=dot(ab,ab)||1,t=clamp(dot(sub(p,a),ab)/den,0,1),q=add(a,mul(ab,t));
 return len(sub(p,q));
}
function swordHitNode(d){
 const hand=player.nodes.find(n=>n.name==='hand')?.p||player.nodes[1].p;
 const pose=motionPose(player),blade=add(hand,player.local(mul(pose.blade,player.spec.scale)));
 const candidates=d.nodes.filter(n=>n.name!=='foot');
 let best=candidates[0],score=Infinity;
 for(const n of candidates){
  let s=pointSegmentDistance(n.p,hand,blade);
  // Preserve the visual identity of the three swings while still using the actual blade path.
  if(player.swing?.combo===1&&n.name==='head')s-=.34;
  if(player.swing?.combo===2&&(n.name==='chest'||n.name==='hip'))s-=.22;
  if(player.swing?.combo===0&&(n.name==='shoulder'||n.name==='chest'))s-=.16;
  if(s<score){score=s;best=n;}
 }
 return best;
}
function enemyTargetRegion(move,index){
 const i=Math.max(0,(index||1)-1),name=move?.name||'';
 if(move?.kind==='stomp')return {region:'leg',side:i%2?1:-1};
 if(move?.kind==='slam')return {region:i%3===0?'head':'torso',side:0};
 if(move?.kind==='thrust'||move?.kind==='rush')return {region:'torso',side:i%2?1:-1};
 if(move?.kind==='leap')return {region:i%2?'head':'torso',side:0};
 if(move?.kind==='sweep')return {region:name.includes('尾')||name.includes('八脚')?'leg':'arm',side:i%2?1:-1};
 if(move?.kind==='sidestep')return {region:'arm',side:i%2?1:-1};
 if(move?.kind==='combo'){
  const order=name.includes('三連')?['arm','torso','leg']:['arm','head','torso'];
  return {region:order[i%order.length],side:i%2?1:-1};
 }
 return {region:'torso',side:0};
}
function markHitLocation(d,node,amount,force){
 const region=hitRegionName(node),side=Math.sign(node?.rest?.x||0)||Math.sign(force.x*Math.cos(d.face)-force.z*Math.sin(d.face))||1;
 const heavy=amount>=24||len(force)>28;
 d.hitRegion=region;d.hitRegionSide=side;d.hitRegionT=heavy?.48:.30;d.hitRegionMax=d.hitRegionT;
 d.lastHitRegion=region;
 if(region==='head')d.stun=Math.max(d.stun,heavy?.30:.16);
 if(region==='leg'){d.stun=Math.max(d.stun,heavy?.26:.14);d.recovery=Math.min(d.recovery,heavy?.30:.55);}
 if(region==='arm')d.recovery=Math.min(d.recovery,heavy?.42:.68);
}
function localPlayerDamage(d,amount,force,point,node){
 if(d.invuln>0||d.hp<=0)return false;
 const lethal=d.hp-amount<=0;if(lethal)return hitLocationPreviousHurt(d,amount,force,point);
 const region=hitRegionName(node),mag=len(force),heavy=amount>=18||mag>24;
 d.hp=Math.max(0,d.hp-amount);d.invuln=.28;d.stun=region==='head'?(heavy?.34:.22):region==='leg'?(heavy?.30:.20):(heavy?.27:.18);
 d.swing=null;d.attack=0;d.counter=0;d.cool=Math.max(d.cool,.12);d.recovery=Math.min(d.recovery,heavy?.36:.62);
 const dir=norm(force),horizontal=V(dir.x,0,dir.z),up=V(0,1,0);
 let impulse=add(mul(horizontal,region==='torso'?12:9),mul(up,region==='head'?4:region==='leg'?1.2:2.5));
 if(region==='leg')impulse=add(mul(horizontal,7),V(0,-4,0));
 damageLocalImpulse(d,point,impulse,region==='head'?.42:region==='arm'?.30:region==='leg'?.36:.38,heavy?.022:.010,region==='arm'?.045:.018);
 if(heavy&&amount>=25){d.down=region==='leg'?.34:.46;d.recovery=0;}
 burst(point,'#8ce6df',heavy?18:12,heavy?4.5:3.3);shake=Math.max(shake,heavy?.17:.085);hitstop=Math.max(hitstop,heavy?.065:.038);impact(point,'hit',heavy?1.05:.75);feel.damage=.45;
 markHitLocation(d,node,amount,force);return true;
}

resolveSwing=function(){
 const move=player.swing;
 if(move&&boss&&boss.hp>0){const node=swordHitNode(boss);hitLocationIntent={target:boss,node};}
 try{return hitLocationPreviousResolveSwing();}finally{hitLocationIntent=null;}
};
enemyImpact=function(move=null){
 if(player&&move){const spec=enemyTargetRegion(move,boss.hitIndex),node=hitNodeForRegion(player,spec.region,spec.side);hitLocationIntent={target:player,node};}
 try{return hitLocationPreviousEnemyImpact(move);}finally{hitLocationIntent=null;}
};

hurt=function(d,amount,force,point){
 const node=hitLocationIntent&&hitLocationIntent.target===d?hitLocationIntent.node:d.nodes.reduce((best,n)=>len(sub(n.p,point))<len(sub(best.p,point))?n:best,d.nodes[0]);
 const actualPoint=node?.p||point;
 let result;
 if(d.player)result=localPlayerDamage(d,amount,force,actualPoint,node);
 else result=hitLocationPreviousHurt(d,amount,force,actualPoint);
 if(result)markHitLocation(d,node,amount,force);
 return result;
};

function applyRegionPose(d,n,p){
 if(!d.hitRegionT)return p;
 p={...p};const s=d.spec.scale,side=d.hitRegionSide||1,t=clamp(d.hitRegionT/(d.hitRegionMax||.3),0,1),pulse=Math.sin(t*Math.PI),region=d.hitRegion;
 if(region==='head'){
  if(n.name==='head'){p.x+=side*.28*s*pulse;p.z-=.22*s*pulse;p.y-=.06*s*pulse;}
  if(n.name==='chest')p.x+=side*.10*s*pulse;
 }else if(region==='torso'){
  if(n.name==='chest'||n.name==='head')p.z-=.28*s*pulse;
  if(n.name==='hip')p.z-=.08*s*pulse;
 }else if(region==='arm'){
  const same=Math.sign(n.rest.x||0)===side;
  if(same&&(n.name==='shoulder'||n.name==='elbow'||n.name==='hand'||n.name==='offhand')){p.y-=.24*s*pulse;p.z-=.20*s*pulse;p.x+=side*.18*s*pulse;}
  if(n.name==='chest')p.x+=side*.10*s*pulse;
 }else if(region==='leg'){
  const same=Math.sign(n.rest.x||0)===side;
  if(same&&(n.name==='knee'||n.name==='foot')){p.y-=.22*s*pulse;p.z-=.10*s*pulse;}
  if(n.name==='hip'){p.y-=.15*s*pulse;p.x+=side*.12*s*pulse;}
  if(n.name==='chest'||n.name==='head')p.x-=side*.10*s*pulse;
 }
 return p;
}
poseTarget=function(d,n){return applyRegionPose(d,n,hitLocationBasePoseTarget(d,n));};
enemyPoseTarget=function(d,n){return applyRegionPose(d,n,hitLocationBaseEnemyPoseTarget(d,n));};
updateFeel=function(dt){
 hitLocationBaseUpdateFeel(dt);
 for(const d of [player,boss])if(d&&d.hitRegionT>0){d.hitRegionT=Math.max(0,d.hitRegionT-dt);if(d.hitRegionT===0)d.hitRegion='';}
};

if(window.parryDoll&&window.parryDoll.snapshot){
 const base=window.parryDoll.snapshot;
 window.parryDoll.snapshot=()=>({...base(),bossHitRegion:boss.lastHitRegion||'',playerHitRegion:player.lastHitRegion||''});
}
