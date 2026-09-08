'use strict';
// Damage reaction pass: keep launch moments special and diversify ordinary enemy hits.
const damageCoreHurt=hurt;
const damageBaseEnemyPoseTarget=enemyPoseTarget;
const damageCoreUpdateFeel=updateFeel;

function damageSetReaction(d,type,duration=.28,side=1){
 d.reviewReaction=type;d.reviewReactionT=duration;d.reviewReactionMax=duration;d.reviewReactionSide=side||1;
}
function damageLocalImpulse(d,point,force,localScale=.35,rootScale=.03,torque=.02){
 const center=d.nodes[0].p;
 const sorted=d.nodes.map(n=>({n,d:len(sub(n.p,point))})).sort((a,b)=>a.d-b.d);
 for(let i=0;i<sorted.length;i++){
  const n=sorted[i].n,proximity=1/(1+sorted[i].d*1.6),w=localScale*(i===0?.72:.12+.20*proximity);
  const offset=sub(n.p,center);
  const spin=V(-offset.z*force.z*torque,(offset.x*force.z-offset.z*force.x)*torque,-offset.x*force.x*torque);
  n.prev=sub(n.prev,mul(add(mul(force,w),spin),1/60));
 }
 d.vel=add(d.vel,mul(force,rootScale));
}
function damageReactionFor(d,amount,forceMag){
 const seq=(d.reviewHitSeq=(d.reviewHitSeq||0)+1),edge=Math.hypot(d.pos.x,d.pos.z)>8.75;
 if(edge&&amount>=20)return 'wall';
 if(amount<=14)return seq%3===0?'stagger':'flinch';
 if(amount<=18)return seq%2?'stagger':'flinch';
 if(amount<=29)return seq%3===0?'knockdown':seq%2?'buckle':'heavy';
 if(amount<=44)return seq%2?'spin':'knockdown';
 return forceMag>40?'knockdown':'heavy';
}
function damageApplyEnemyHit(d,amount,force,point){
 const forceMag=len(force),side=Math.sign(force.x*Math.cos(d.face)-force.z*Math.sin(d.face))||((d.reviewHitSeq||0)%2?1:-1);
 const reaction=damageReactionFor(d,amount,forceMag);
 d.hp=Math.max(0,d.hp-amount);d.invuln=.085;d.stun=.08;d.recovery=Math.min(d.recovery,.72);
 const dir=norm(force),horizontal=V(dir.x,0,dir.z),up=V(0,1,0);
 if(reaction==='flinch'){
  damageSetReaction(d,'flinch',.20,side);d.stun=.06;damageLocalImpulse(d,point,add(mul(horizontal,8),mul(up,1.4)),.23,.006,.008);
 }else if(reaction==='stagger'){
  damageSetReaction(d,'stagger',.30,side);d.stun=.14;d.recovery=Math.min(d.recovery,.58);damageLocalImpulse(d,point,add(mul(horizontal,11),mul(up,2.2)),.34,.018,.018);
 }else if(reaction==='heavy'){
  damageSetReaction(d,'heavy',.38,side);d.stun=.24;d.recovery=Math.min(d.recovery,.42);damageLocalImpulse(d,point,add(mul(horizontal,14),mul(up,3.0)),.44,.026,.026);
 }else if(reaction==='buckle'){
  damageSetReaction(d,'buckle',.52,side);d.stun=.31;d.recovery=Math.min(d.recovery,.24);damageLocalImpulse(d,d.nodes[0].p,add(mul(horizontal,7),V(0,-7,0)),.38,.012,.012);
 }else if(reaction==='spin'){
  damageSetReaction(d,'spin',.46,side);d.stun=.28;d.recovery=Math.min(d.recovery,.30);const lateral=V(Math.cos(d.face)*side,0,-Math.sin(d.face)*side);damageLocalImpulse(d,point,add(mul(horizontal,11),add(mul(lateral,10),mul(up,2.5))),.46,.024,.055);
 }else if(reaction==='wall'){
  damageSetReaction(d,'wall',.60,side);d.stun=.38;d.recovery=Math.min(d.recovery,.20);damageLocalImpulse(d,point,add(mul(horizontal,6),V(0,-5,0)),.34,0,.025);groundImpact(d.pos,.48);
 }else{
  damageSetReaction(d,'knockdown',.68,side);d.stun=.55;d.down=.48;d.recovery=0;damageLocalImpulse(d,point,add(mul(horizontal,16),mul(up,5)),.52,.032,.035);
 }
 burst(point,'#edac73',reaction==='flinch'?10:reaction==='stagger'?14:18,reaction==='flinch'?3.2:4.3);
 const heavy=['heavy','buckle','spin','knockdown','wall'].includes(reaction);
 shake=Math.max(shake,heavy?.16:.075);hitstop=Math.max(hitstop,heavy?.065:.035);impact(point,'hit',heavy?1.05:.72);
 return true;
}
hurt=function(d,amount,force,point){
 if(d.player)return damageCoreHurt(d,amount,force,point);
 if(d.invuln>0||d.hp<=0)return false;
 const lethal=d.hp-amount<=0,finisher=amount>=60;
 if(lethal||finisher){
  const u=norm(force),p=finisher?34:24,deathForce=mul(u,p);deathForce.y=finisher?13:7;
  damageSetReaction(d,'launch',1,1);
  return damageCoreHurt(d,amount,deathForce,point);
 }
 return damageApplyEnemyHit(d,amount,force,point);
};

enemyPoseTarget=function(d,n){
 let p=damageBaseEnemyPoseTarget(d,n);
 if(!d.reviewReactionT||d.down>0)return p;
 p={...p};const s=d.spec.scale,side=d.reviewReactionSide||1,t=clamp(d.reviewReactionT/(d.reviewReactionMax||.3),0,1),pulse=Math.sin(t*Math.PI);
 if(d.reviewReaction==='flinch'){
  if(n.name==='chest'||n.name==='head')p.z-=.20*s*pulse;
  if(n.name==='hand'||n.name==='offhand')p.z-=.10*s*pulse;
 }else if(d.reviewReaction==='stagger'){
  if(n.name==='chest'||n.name==='head'||n.name==='shoulder')p.x+=side*.24*s*pulse;
  if(n.name==='head')p.z-=.12*s*pulse;
 }else if(d.reviewReaction==='heavy'){
  if(n.name==='chest'||n.name==='head')p.z-=.34*s*pulse;
  if(n.name==='hip'||n.name==='knee')p.y-=.10*s*pulse;
 }else if(d.reviewReaction==='buckle'||d.reviewReaction==='wall'){
  if(n.name==='hip')p.y-=.24*s*pulse;
  if(n.name==='chest'||n.name==='head')p.y-=.18*s*pulse;
  if(n.name==='knee')p.y-=.17*s*pulse;
  if(n.name==='head')p.z-=.20*s*pulse;
 }else if(d.reviewReaction==='spin'){
  const a=side*.48*pulse,c=Math.cos(a),sn=Math.sin(a),x=p.x,z=p.z;p.x=x*c+z*sn;p.z=-x*sn+z*c;
  if(n.name==='head'||n.name==='chest')p.x+=side*.12*s*pulse;
 }
 return p;
};

updateFeel=function(dt){
 damageCoreUpdateFeel(dt);
 for(const d of [player,boss])if(d&&d.reviewReactionT>0){d.reviewReactionT=Math.max(0,d.reviewReactionT-dt);if(d.reviewReactionT===0)d.reviewReaction='';}
};

if(window.parryDoll&&window.parryDoll.snapshot){
 const damageBaseSnapshot=window.parryDoll.snapshot;
 window.parryDoll.snapshot=()=>({...damageBaseSnapshot(),bossReaction:boss.reviewReaction||'',bossDown:+boss.down.toFixed(3)});
}
