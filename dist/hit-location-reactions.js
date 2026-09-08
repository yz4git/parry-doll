'use strict';
// Hit-location + strike-direction reactions for both enemy and player.
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
  if(player.swing?.combo===1&&n.name==='head')s-=.34;
  if(player.swing?.combo===2&&(n.name==='chest'||n.name==='hip'))s-=.22;
  if(player.swing?.combo===0&&(n.name==='shoulder'||n.name==='chest'))s-=.16;
  if(s<score){score=s;best=n;}
 }
 return best;
}
function playerStrikeDirection(move){
 const combo=move?.finisher?2:clamp(move?.combo??0,0,2),clip=COMBO_POSES[combo];
 const from=mul(clip.ready.blade,player.spec.scale),to=mul(clip.hit.blade,player.spec.scale);
 let dir=player.local(sub(to,from));
 if(move?.counter)dir=add(dir,player.local(V((combo===1?.25:-.25),.08,.35)));
 return norm(dir);
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
function enemyStrikeDirection(move,index){
 const i=Math.max(0,(index||1)-1),side=i%2?1:-1;
 let local=V(0,0,1);
 if(move?.kind==='slam')local=V(side*.10,-1,.24);
 else if(move?.kind==='stomp')local=V(side*.08,-1,.04);
 else if(move?.kind==='thrust'||move?.kind==='rush')local=V(side*.08,.02,1);
 else if(move?.kind==='leap')local=V(side*.12,-.72,.82);
 else if(move?.kind==='sweep'||move?.kind==='sidestep')local=V(side,move?.kind==='sweep'?-0.08:.12,.22);
 else if(move?.kind==='combo'){
  const dirs=[V(-1,-.48,.30),V(1,.36,.28),V(.10,-.88,.32)];
  local=dirs[i%dirs.length];
 }
 return norm(boss.local(local));
}
function hitDirectionLocal(d,direction){
 const dir=norm(direction||V()),right=V(Math.cos(d.face),0,-Math.sin(d.face)),forward=V(Math.sin(d.face),0,Math.cos(d.face));
 return {x:dot(dir,right),y:dir.y,z:dot(dir,forward)};
}
function hitDirectionVariant(region,q){
 const ax=Math.abs(q.x),ay=Math.abs(q.y);
 if(region==='head'){
  if(ay>.56)return q.y>0?'lift':'crush';
  if(ax>.42)return q.x>0?'snap-right':'snap-left';
  return q.z<0?'drive-back':'fold-forward';
 }
 if(region==='torso'){
  if(q.y>.56)return 'lift';
  if(q.y<-.56)return 'fold';
  if(ax>.40)return q.x>0?'bend-right':'bend-left';
  return q.z<0?'drive-back':'twist-forward';
 }
 if(region==='arm'){
  if(q.y>.44)return 'lift';
  if(q.y<-.44)return 'drop';
  if(ax>.36)return q.x>0?'sweep-right':'sweep-left';
  return q.z<0?'drive-back':'fold-in';
 }
 if(q.y>.42)return 'lift';
 if(q.y<-.42)return 'collapse';
 if(ax>.34)return q.x>0?'sweep-right':'sweep-left';
 return q.z<0?'buckle':'recoil';
}
function markHitLocation(d,node,amount,force,direction){
 const region=hitRegionName(node),dir=direction&&len(direction)>.001?direction:force,local=hitDirectionLocal(d,dir);
 const side=Math.sign(node?.rest?.x||0)||Math.sign(local.x)||1,heavy=amount>=24||len(force)>28;
 d.hitRegion=region;d.hitRegionSide=side;d.hitRegionT=heavy?.52:.32;d.hitRegionMax=d.hitRegionT;
 d.hitDirX=local.x;d.hitDirY=local.y;d.hitDirZ=local.z;d.hitVariant=hitDirectionVariant(region,local);
 d.lastHitRegion=region;d.lastHitVariant=d.hitVariant;
 if(region==='head')d.stun=Math.max(d.stun,heavy?.32:.17);
 if(region==='leg'){d.stun=Math.max(d.stun,heavy?.28:.15);d.recovery=Math.min(d.recovery,heavy?.28:.52);}
 if(region==='arm')d.recovery=Math.min(d.recovery,heavy?.40:.66);
}
function localPlayerDamage(d,amount,force,point,node,direction){
 if(d.invuln>0||d.hp<=0)return false;
 const lethal=d.hp-amount<=0;if(lethal)return hitLocationPreviousHurt(d,amount,force,point);
 const region=hitRegionName(node),mag=len(force),heavy=amount>=18||mag>24,travel=norm(direction&&len(direction)>.001?direction:force);
 d.hp=Math.max(0,d.hp-amount);d.invuln=.28;d.stun=region==='head'?(heavy?.34:.22):region==='leg'?(heavy?.30:.20):(heavy?.27:.18);
 d.swing=null;d.attack=0;d.counter=0;d.cool=Math.max(d.cool,.12);d.recovery=Math.min(d.recovery,heavy?.36:.62);
 let impulse=mul(travel,region==='torso'?11:8.5);impulse.y=clamp(impulse.y,-4.5,5);
 if(region==='head')impulse.y+=travel.y>0?1.8:travel.y<0?-1.2:1;
 if(region==='leg')impulse.y=Math.min(impulse.y,-1.2);
 damageLocalImpulse(d,point,impulse,region==='head'?.42:region==='arm'?.30:region==='leg'?.36:.38,heavy?.018:.008,region==='arm'?.050:.020);
 if(heavy&&amount>=25){d.down=region==='leg'?.34:.44;d.recovery=0;}
 burst(point,'#8ce6df',heavy?18:12,heavy?4.5:3.3);shake=Math.max(shake,heavy?.17:.085);hitstop=Math.max(hitstop,heavy?.065:.038);impact(point,'hit',heavy?1.05:.75);feel.damage=.45;
 return true;
}

resolveSwing=function(){
 const move=player.swing;
 if(move&&boss&&boss.hp>0){const node=swordHitNode(boss);hitLocationIntent={target:boss,node,direction:playerStrikeDirection(move)};}
 try{return hitLocationPreviousResolveSwing();}finally{hitLocationIntent=null;}
};
enemyImpact=function(move=null){
 if(player&&move){
  const spec=enemyTargetRegion(move,boss.hitIndex),node=hitNodeForRegion(player,spec.region,spec.side);
  hitLocationIntent={target:player,node,direction:enemyStrikeDirection(move,boss.hitIndex)};
 }
 try{return hitLocationPreviousEnemyImpact(move);}finally{hitLocationIntent=null;}
};

hurt=function(d,amount,force,point){
 const intent=hitLocationIntent&&hitLocationIntent.target===d?hitLocationIntent:null;
 const node=intent?.node||d.nodes.reduce((best,n)=>len(sub(n.p,point))<len(sub(best.p,point))?n:best,d.nodes[0]);
 const actualPoint=node?.p||point,direction=intent?.direction||norm(force);
 let result;
 if(d.player)result=localPlayerDamage(d,amount,force,actualPoint,node,direction);
 else result=hitLocationPreviousHurt(d,amount,force,actualPoint);
 if(result){
  markHitLocation(d,node,amount,force,direction);
  // Add a small local directional kick without turning ordinary hits back into launches.
  if(!d.player&&d.hp>0&&d.down===0)damageLocalImpulse(d,actualPoint,mul(norm(direction),5.5),.12,0,.010);
 }
 return result;
};

function applyRegionPose(d,n,p){
 if(!d.hitRegionT)return p;
 p={...p};const s=d.spec.scale,side=d.hitRegionSide||1,t=clamp(d.hitRegionT/(d.hitRegionMax||.3),0,1),pulse=Math.sin(t*Math.PI),region=d.hitRegion,v=d.hitVariant||'';
 const dirSide=Math.sign(d.hitDirX||0)||side;
 if(region==='head'){
  if(v==='snap-right'||v==='snap-left'){
   const k=v==='snap-right'?1:-1;if(n.name==='head'){p.x+=k*.36*s*pulse;p.z-=.12*s*pulse;p.y-=.03*s*pulse;}if(n.name==='chest')p.x+=k*.14*s*pulse;
  }else if(v==='lift'){
   if(n.name==='head'){p.y+=.18*s*pulse;p.z-=.31*s*pulse;}if(n.name==='chest')p.z-=.14*s*pulse;
  }else if(v==='crush'){
   if(n.name==='head'){p.y-=.20*s*pulse;p.z+=.08*s*pulse;}if(n.name==='chest')p.y-=.08*s*pulse;
  }else if(v==='drive-back'){
   if(n.name==='head'){p.z-=.34*s*pulse;p.y+=.05*s*pulse;}if(n.name==='chest')p.z-=.15*s*pulse;
  }else{
   if(n.name==='head'){p.z+=.28*s*pulse;p.y-=.13*s*pulse;}if(n.name==='chest')p.z+=.10*s*pulse;
  }
 }else if(region==='torso'){
  if(v==='bend-right'||v==='bend-left'){
   const k=v==='bend-right'?1:-1;if(n.name==='chest'||n.name==='head')p.x+=k*(n.name==='head'?.24:.32)*s*pulse;if(n.name==='hip')p.x-=k*.08*s*pulse;
  }else if(v==='lift'){
   if(n.name==='chest'){p.y+=.09*s*pulse;p.z-=.24*s*pulse;}if(n.name==='head'){p.y+=.12*s*pulse;p.z-=.29*s*pulse;}
  }else if(v==='fold'){
   if(n.name==='chest'){p.y-=.11*s*pulse;p.z+=.31*s*pulse;}if(n.name==='head'){p.y-=.15*s*pulse;p.z+=.38*s*pulse;}if(n.name==='hip')p.z+=.09*s*pulse;
  }else if(v==='drive-back'){
   if(n.name==='chest')p.z-=.38*s*pulse;if(n.name==='head')p.z-=.28*s*pulse;if(n.name==='hip')p.z-=.12*s*pulse;
  }else{
   if(n.name==='chest'||n.name==='head'||n.name==='shoulder'||n.name==='elbow'||n.name==='hand'||n.name==='offhand'){
    const a=dirSide*.30*pulse,c=Math.cos(a),sn=Math.sin(a),x=p.x,z=p.z;p.x=x*c+z*sn;p.z=-x*sn+z*c;
   }
  }
 }else if(region==='arm'){
  const same=Math.sign(n.rest.x||0)===side;
  if(same&&(n.name==='shoulder'||n.name==='elbow'||n.name==='hand'||n.name==='offhand')){
   if(v==='lift'){p.y+=.30*s*pulse;p.x+=side*.11*s*pulse;}
   else if(v==='drop'){p.y-=.34*s*pulse;p.z-=.14*s*pulse;}
   else if(v==='sweep-right'||v==='sweep-left'){const k=v==='sweep-right'?1:-1;p.x+=k*.34*s*pulse;p.z-=.08*s*pulse;}
   else if(v==='drive-back')p.z-=.34*s*pulse;
   else{p.x-=side*.18*s*pulse;p.z+=.18*s*pulse;}
  }
  if(n.name==='chest')p.x+=dirSide*.11*s*pulse;
 }else if(region==='leg'){
  const same=Math.sign(n.rest.x||0)===side;
  if(same&&(n.name==='knee'||n.name==='foot')){
   if(v==='lift'){p.y+=.30*s*pulse;p.z+=.08*s*pulse;}
   else if(v==='collapse'){p.y-=.30*s*pulse;p.z-=.08*s*pulse;}
   else if(v==='sweep-right'||v==='sweep-left'){const k=v==='sweep-right'?1:-1;p.x+=k*.34*s*pulse;p.y-=.08*s*pulse;}
   else if(v==='buckle'){p.y-=.23*s*pulse;p.z-=.22*s*pulse;}
   else p.z+=.18*s*pulse;
  }
  if(n.name==='hip'){p.y-=(v==='collapse'||v==='buckle'?.18:.10)*s*pulse;p.x+=dirSide*.12*s*pulse;}
  if(n.name==='chest'||n.name==='head')p.x-=dirSide*.10*s*pulse;
 }
 return p;
}
poseTarget=function(d,n){return applyRegionPose(d,n,hitLocationBasePoseTarget(d,n));};
enemyPoseTarget=function(d,n){return applyRegionPose(d,n,hitLocationBaseEnemyPoseTarget(d,n));};
updateFeel=function(dt){
 hitLocationBaseUpdateFeel(dt);
 for(const d of [player,boss])if(d&&d.hitRegionT>0){d.hitRegionT=Math.max(0,d.hitRegionT-dt);if(d.hitRegionT===0){d.hitRegion='';d.hitVariant='';}}
};

if(window.parryDoll&&window.parryDoll.snapshot){
 const base=window.parryDoll.snapshot;
 window.parryDoll.snapshot=()=>({...base(),bossHitRegion:boss.lastHitRegion||'',bossHitVariant:boss.lastHitVariant||'',playerHitRegion:player.lastHitRegion||'',playerHitVariant:player.lastHitVariant||''});
}
