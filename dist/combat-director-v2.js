'use strict';
// Gameplay-only director: breaks fixed 0->1->2->3 attack loops without changing hit rules or telegraph windows.
(()=>{
 if(window.__parryCombatDirectorV2Loaded)return;window.__parryCombatDirectorV2Loaded=true;
 const state={boss:null,level:-1,last:-1,prev:-1,plans:0,counts:[0,0,0,0],lastKind:'',phase:1};
 const identity=[
  {combo:1.20,thrust:1.08,slam:.88,sidestep:1.06},
  {combo:.92,leap:1.10,rush:1.22,sweep:1.05},
  {thrust:1.15,sweep:1.08,leap:.96,combo:1.16},
  {slam:1.16,sweep:1.08,stomp:1.12,rush:.94}
 ];
 const pursuit=new Set(['thrust','rush','leap']);
 const close=new Set(['combo','sweep','sidestep','slam','stomp']);
 const rhythmBreak=new Set(['slam','stomp','leap','sweep']);
 const phaseNow=()=>typeof window.parryPhaseBreakDiagnostics==='function'?(window.parryPhaseBreakDiagnostics()?.phase||1):1;
 function resetState(){state.boss=boss;state.level=level;state.last=state.prev=-1;state.plans=0;state.counts=[0,0,0,0];state.lastKind='';state.phase=phaseNow()}
 function hash01(n){const x=Math.sin(n*12.9898+level*78.233+state.plans*17.17)*43758.5453;return x-Math.floor(x)}
 function choose(moves,distance){
  const phase=phaseNow(),parryRate=parries/Math.max(1,boss.sequence),playerLow=player.hp<player.spec.hp*.38;
  let best=0,bestScore=-1e9;
  for(let i=0;i<moves.length;i++){
   const m=moves[i],kind=m.kind;
   let score=(identity[level]?.[kind]||1)*1.5;
   // Match the attack to the actual spacing, but never make one distance map to only one answer.
   if(distance>4.7)score+=pursuit.has(kind)?1.75:-.55;
   else if(distance<2.45)score+=close.has(kind)?1.20:-.35;
   else if(distance>3.5)score+=pursuit.has(kind)?.72:.12;
   else score+=close.has(kind)?.52:.20;
   // Do not fall back into a four-move metronome or immediate repetition.
   if(i===state.last)score-=3.2;
   if(i===state.prev)score-=1.05;
   score-=state.counts[i]*.11;
   if(kind===state.lastKind)score-=.55;
   // Strong parry play gets rhythm changes, not invisible speed cheating.
   if(parryRate>.58&&rhythmBreak.has(kind))score+=.72;
   if(parryRate>.74&&m.hits?.length>1)score-=.22;
   // Final phases lean into boss identity and pressure; low player HP gets a small mercy bias.
   if(phase>=3)score+=(identity[level]?.[kind]||1)*.30;
   if(playerLow&&['slam','leap','stomp'].includes(kind))score-=.32;
   score+=(hash01((boss.sequence+1)*11+i*7)-.5)*.46;
   if(score>bestScore){bestScore=score;best=i}
  }
  return best;
 }
 const baseUpdateEnemy=updateEnemy;
 updateEnemy=function(dt){
  if(!boss)return baseUpdateEnemy(dt);
  if(state.boss!==boss||state.level!==level)resetState();
  // Level 4 already has its own adaptive mirror AI. Do not fight that director.
  if(level===4)return baseUpdateEnemy(dt);
  const planning=mode==='play'&&boss.hp>0&&boss.down<=0&&boss.broken<=0&&boss.stun<=0&&boss.wind<=0&&boss.strike<=0&&boss.ai<=0;
  if(!planning)return baseUpdateEnemy(dt);
  const moves=ENEMY_MOVES[level];if(!moves?.length)return baseUpdateEnemy(dt);
  const distance=Math.hypot(player.pos.x-boss.pos.x,player.pos.z-boss.pos.z),slot=((boss.sequence%moves.length)+moves.length)%moves.length,idx=choose(moves,distance),original=moves[slot];
  if(idx!==slot)moves[slot]=moves[idx];
  try{
   const out=baseUpdateEnemy(dt);
   // A plan counts only if this frame actually entered wind-up.
   if(boss.wind>0){state.prev=state.last;state.last=idx;state.lastKind=moves[idx]?.kind||'';state.counts[idx]++;state.plans++;state.phase=phaseNow()}
   return out;
  }finally{if(idx!==slot)moves[slot]=original}
 };
 const baseReset=reset;
 reset=function(l=0){const out=baseReset(l);resetState();return out};
 window.parryCombatDirectorV2Diagnostics=()=>({level:state.level,phase:state.phase,plans:state.plans,last:state.last,prev:state.prev,counts:[...state.counts],lastKind:state.lastKind});
})();
