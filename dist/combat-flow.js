'use strict';
// Combat flow pass: break the permanent face-to-face line with circling, angled entries and recovery exits.
let flowClock=0,flowOrbitSide=1,flowLastSequence=-1;
const FLOW_DESIRED=[3.15,3.85,4.15,3.65];
const FLOW_ORBIT=[1.20,1.95,1.70,.78];
const FLOW_BIAS={combo:.075,thrust:.025,slam:.045,sidestep:.12,leap:.075,rush:.035,sweep:.10,stomp:.025};

const flowStartEnemyAttack=startEnemyAttack;
startEnemyAttack=function(move){
 boss.flowAttackSide=((boss.sequence+level)%2===0?1:-1);
 flowStartEnemyAttack(move);
};

const flowUpdateEnemy=updateEnemy;
updateEnemy=function(dt){
 const beforeWind=boss.wind,beforeStrike=boss.strike,beforeSeq=boss.sequence;
 flowClock+=dt;
 flowUpdateEnemy(dt);
 if(!boss||boss.hp<=0||boss.down>0||boss.broken>0)return;
 const v=sub(player.pos,boss.pos),distance=Math.hypot(v.x,v.z),facing=Math.atan2(v.x,v.z),u=norm(V(v.x,0,v.z));
 const tangent=V(u.z,0,-u.x),move=enemyMove(boss),side=boss.flowAttackSide||flowOrbitSide;
 const bias=(FLOW_BIAS[move?.kind]||.04)*side;

 // During the readable wind-up, bias both body and telegraph to the attack side.
 if(boss.wind>0){
  if(boss.wind>.32){boss.aim+=bias;boss.face=facing+bias*.72;}
  const creep=['combo','sweep','sidestep'].includes(move?.kind)?FLOW_ORBIT[level]*.42:FLOW_ORBIT[level]*.16;
  boss.vel.x+=tangent.x*creep*side;boss.vel.z+=tangent.z*creep*side;
 }
 // On the exact wind->strike transition, commit the same angled line once.
 if(beforeWind>0&&boss.strike>0&&beforeStrike<=0){boss.aim+=bias;boss.face=boss.aim;}

 if(boss.sequence!==beforeSeq||boss.sequence!==flowLastSequence){
  flowLastSequence=boss.sequence;
  flowOrbitSide=((boss.sequence+level)%2===0?1:-1);
 }

 // Neutral/recovery movement: orbit instead of walking straight down the centre line.
 if(boss.wind<=0&&boss.strike<=0&&boss.stun<=0){
  const weave=Math.sin(flowClock*.78+level*1.7)*.34,desired=FLOW_DESIRED[level]+weave;
  const radial=clamp((distance-desired)*1.05,-1.45,1.55);
  const recovery=boss.ai>0?1.25:1;
  const orbit=FLOW_ORBIT[level]*recovery;
  const escape=distance<2.15?-1.35:0;
  const targetVel=add(mul(u,radial+escape),mul(tangent,orbit*flowOrbitSide));
  const blend=boss.ai>0?.42:.30;
  boss.vel.x+=(targetVel.x-boss.vel.x)*blend;boss.vel.z+=(targetVel.z-boss.vel.z)*blend;
  boss.face=facing+flowOrbitSide*(boss.ai>0?.16:.10);
 }
};

// Player attacks step across the opponent rather than lunging through the exact centre every time.
const flowPlayerAttack=playerAttack;
playerAttack=function(){
 const ok=flowPlayerAttack();
 if(!ok)return false;
 const to=norm(V(boss.pos.x-player.pos.x,0,boss.pos.z-player.pos.z)),tangent=V(to.z,0,-to.x);
 const idx=player.swing?.combo||0,side=idx===1?-1:idx===2?1:((parries+perfects)%2?1:-1);
 const lateral=[.72,1.18,.92][idx]*(player.swing?.finisher?.45:1);
 player.vel.x+=tangent.x*lateral*side;player.vel.z+=tangent.z*lateral*side;
 const targetFace=Math.atan2(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z);
 player.face=targetFace+side*(player.swing?.finisher?.025:.075);
 return true;
};

// The core lock-on still handles hit logic, but the rendered body can open its stance while strafing.
const flowPhysics=Doll.prototype.physics;
Doll.prototype.physics=function(dt){
 if(this.player&&mode==='play'&&this.hp>0&&this.down<=0&&this.stun<=0){
  const toBoss=Math.atan2(boss.pos.x-this.pos.x,boss.pos.z-this.pos.z),speed=Math.hypot(this.vel.x,this.vel.z);
  if(this.attack<=0&&this.parry<=0&&speed>.32){
   const moveDir=Math.atan2(this.vel.x,this.vel.z),delta=clamp(angleDelta(moveDir,toBoss),-.72,.72);
   this.face=toBoss+delta*.58;
  }else if(this.attack<=0&&this.parry<=0){
   this.face=toBoss+Math.sin(flowClock*.85)*.035;
  }
 }
 return flowPhysics.call(this,dt);
};

// Recovery from a landed hit carries a little tangential momentum so fighters do not reset to the same line immediately.
const flowResolveSwing=resolveSwing;
resolveSwing=function(){
 const move=player.swing,before=boss.hp;
 const out=flowResolveSwing();
 if(move&&boss.hp<before&&boss.hp>0){
  const to=norm(V(boss.pos.x-player.pos.x,0,boss.pos.z-player.pos.z)),tangent=V(to.z,0,-to.x),side=move.combo===1?-1:1;
  player.vel.x+=tangent.x*.34*side;player.vel.z+=tangent.z*.34*side;
  boss.vel.x-=tangent.x*.24*side;boss.vel.z-=tangent.z*.24*side;
 }
 return out;
};

if(window.parryDoll&&window.parryDoll.snapshot){
 const flowSnapshot=window.parryDoll.snapshot;
 window.parryDoll.snapshot=()=>{
  const spacing=Math.hypot(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z),targetPlayer=Math.atan2(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z),targetBoss=Math.atan2(player.pos.x-boss.pos.x,player.pos.z-boss.pos.z);
  return {...flowSnapshot(),spacing:+spacing.toFixed(3),playerFaceOffset:+angleDelta(player.face,targetPlayer).toFixed(3),bossFaceOffset:+angleDelta(boss.face,targetBoss).toFixed(3),orbitSide:flowOrbitSide};
 };
}
