'use strict';
// Gameplay rhythm v1: responsive mobile input, meaningful whiffs, stronger perfect defense rewards,
// and slightly tighter boss recovery without changing response colors or hit geometry.
(()=>{
 if(window.__parryGameplayRhythmV1Loaded)return;window.__parryGameplayRhythmV1Loaded=true;

 const GP_ATTACK_BUFFER=.46;
 const GP_CHAIN_CANCEL=.16;
 const GP_HIT_RECOVERY_BONUS=.10;
 const GP_WHIFF_PENALTY=.09;
 const GP_PERFECT_DODGE_COUNTER=.82;
 const GP_PERFECT_PARRY_COUNTER=1.55;
 let bufferedAttack=0,lastBoss=null;

 function applyRhythmTuning(){
  // Tighten only downtime. Telegraph/active timings and hit geometry remain unchanged.
  for(const group of ENEMY_MOVES){
   for(const move of group){
    if(!Number.isFinite(move.__gameplayRhythmBaseRecover))move.__gameplayRhythmBaseRecover=move.recover;
    move.recover=Math.max(.72,move.__gameplayRhythmBaseRecover*.90);
   }
  }
  // Player's first two links form one phrase; the heavy third hit retains commitment.
  MOVES[0].recover=.23;
  MOVES[1].recover=.25;
  MOVES[2].recover=.44;
 }
 applyRhythmTuning();

 const gpPlayerAttackBase=playerAttack;
 playerAttack=function(){
  applyRhythmTuning();
  return gpPlayerAttackBase();
 };

 const gpPlayerParryBase=playerParry;
 playerParry=function(){
  // Do not let a pre-contact attack startup become a risk-free parry cancel.
  // Immediately after the strike has committed, defensive cancel remains available.
  if(player?.swing&&player.swingClock>0)return false;
  return gpPlayerParryBase();
 };

 const gpResolveSwingBase=resolveSwing;
 resolveSwing=function(){
  const move=player?.swing?{...player.swing}:null,before=boss?.hp??0;
  const out=gpResolveSwingBase();
  if(!move||!player||!boss||player.hp<=0)return out;
  const landed=boss.hp<before;
  if(landed){
   // Hit-confirmed attacks flow forward; keep at least a sliver of commitment.
   player.cool=Math.max(player.attack+.055,player.cool-GP_HIT_RECOVERY_BONUS);
  }else if(!move.finisher&&!move.counter){
   // Whiffing should matter so spacing and lateral movement have a purpose.
   player.cool+=GP_WHIFF_PENALTY;
   player.attackChainTimer=Math.min(player.attackChainTimer,.72);
  }
  return out;
 };

 const gpAnnounceBase=announce;
 announce=function(t,d){
  const out=gpAnnounceBase(t,d);
  if(t==='PERFECT PARRY'&&player){
   player.counter=Math.max(player.counter,GP_PERFECT_PARRY_COUNTER);
   boss.posture=Math.min(100,boss.posture+4);
  }else if(t==='PERFECT DODGE'&&player&&boss){
   // A perfect evade should create a short attack turn instead of only incrementing a stat.
   player.counter=Math.max(player.counter,GP_PERFECT_DODGE_COUNTER);
   boss.stun=Math.max(boss.stun,.16);
   boss.ai=Math.max(boss.ai,.52);
  }
  return out;
 };

 const gpResetBase=reset;
 reset=function(l=0){
  bufferedAttack=0;
  const out=gpResetBase(l);
  applyRhythmTuning();
  if(boss)boss.ai=Math.min(boss.ai,.95);
  lastBoss=boss;
  return out;
 };

 const gpStepBase=step;
 step=function(dt){
  // Capture taps before the core consumes attackQueued. This is intentionally longer than
  // the core buffer so a thumb tap during late recovery survives until the next legal link.
  if(mode==='play'&&attackQueued)bufferedAttack=GP_ATTACK_BUFFER;
  bufferedAttack=Math.max(0,bufferedAttack-dt);

  const beforeAttack=player?.attack||0,beforeSwing=!!player?.swing;
  const out=gpStepBase(dt);

  if(boss&&boss!==lastBoss){
   lastBoss=boss;
   applyRhythmTuning();
   boss.ai=Math.min(boss.ai,1.0);
  }

  if(mode==='play'&&bufferedAttack>0&&player&&boss&&player.hp>0&&boss.hp>0&&player.down<=0&&player.stun<=0){
   // If the core already accepted this tap, do not fire a duplicate.
   const accepted=(player.attack>beforeAttack+.02)||(!beforeSwing&&!!player.swing);
   if(accepted)bufferedAttack=0;
   else if(player.attack<=0&&player.cool<=GP_CHAIN_CANCEL){
    // Late-recovery cancel: only a small tail of recovery is converted into responsiveness.
    player.cool=0;
    if(playerAttack())bufferedAttack=0;
   }
  }
  return out;
 };

 // Small UI feedback: when a buffered link is waiting, the attack button subtly signals
 // that the tap was accepted instead of feeling lost.
 const style=document.createElement('style');
 style.textContent=`
 #attack.buffered{box-shadow:0 0 13px rgba(205,239,255,.28),inset 0 0 0 2px rgba(220,246,255,.18)}
 #stats.gp-counter{color:#ffe29a;text-shadow:0 0 10px #d9a72f88}
 `;
 document.head.appendChild(style);
 const attackButton=$('attack');
 const gpHudStepBase=step;
 // step is already wrapped above; update visuals from RAF so this remains presentation-only.
 let lastUi=0;
 function uiTick(now){
  if(attackButton)attackButton.classList.toggle('buffered',bufferedAttack>.04);
  const stats=$('stats');
  if(stats)stats.classList.toggle('gp-counter',!!player&&player.counter>.05);
  lastUi=now;requestAnimationFrame(uiTick);
 }
 requestAnimationFrame(uiTick);

 if(window.parryDoll?.snapshot){
  const gpSnapshotBase=window.parryDoll.snapshot;
  window.parryDoll.snapshot=()=>({...gpSnapshotBase(),
   gameplayRhythm:true,
   bufferedAttack:+bufferedAttack.toFixed(3),
   attackRecoveries:MOVES.map(m=>+m.recover.toFixed(3)),
   perfectDodgeCounter:GP_PERFECT_DODGE_COUNTER,
   perfectParryCounter:GP_PERFECT_PARRY_COUNTER
  });
 }
})();
