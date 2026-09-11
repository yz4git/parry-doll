'use strict';
// MIRROR BREAK v8 — preserve KO launch/down presentation before opening DOLL CORE reward.
(()=>{
 if(window.__parryMirrorBreakV8DefeatPresentationLoaded)return;window.__parryMirrorBreakV8DefeatPresentationLoaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const ko={pending:false,level:-1,t:0,quietT:0,releasedLevel:-1,opened:0,lastMotion:0,lastChestY:0};
 window.__mirrorBreakV8DefeatState=ko;
 const MIN_SHOW=1.55,QUIET_NEED=.28,MAX_SHOW=2.45;
 function resetPending(){ko.pending=false;ko.level=-1;ko.t=0;ko.quietT=0;ko.lastMotion=0;ko.lastChestY=0}
 function nodeMotion(dt){
  if(!boss?.nodes?.length)return 0;const inv=1/Math.max(dt,1/120);let sum=0,max=0;
  for(const n of boss.nodes){const v=len(sub(n.p,n.prev))*inv;sum+=v;max=Math.max(max,v)}
  return max*.62+(sum/boss.nodes.length)*.38;
 }
 function beginPresentation(){
  ko.pending=true;ko.level=level;ko.t=0;ko.quietT=0;ko.releasedLevel=-1;
  // v1 uses choiceFor as its immediate-open guard. Reserve this level while the KO plays.
  state.choiceFor=level;transition=Math.max(transition,999);attackQueued=parryQueued=false;attackBuffer=parryBuffer=0;
 }
 const baseReset=reset;reset=function(l=0){const out=baseReset(l);resetPending();ko.releasedLevel=-1;return out};
 const baseStep=step;step=function(dt){
  const rewardKO=mode==='play'&&boss?.hp<=0&&player?.hp>0&&level<=3&&!state.choice&&state.choiceFor!==level&&ko.releasedLevel!==level;
  if(rewardKO&&!ko.pending)beginPresentation();
  if(ko.pending&&ko.level===level)transition=Math.max(transition,999);
  const out=baseStep(dt);
  if(!ko.pending)return out;
  if(mode!=='play'||level!==ko.level||!boss||boss.hp>0){resetPending();return out}
  ko.t+=dt;ko.lastMotion=nodeMotion(dt);const chest=boss.nodes?.find(n=>n.name==='chest')||boss.nodes?.[1];ko.lastChestY=chest?.p?.y||0;
  const lowEnough=!chest||ko.lastChestY<Math.max(.82,boss.spec.scale*1.05);
  if(ko.t>=MIN_SHOW&&lowEnough&&ko.lastMotion<1.55)ko.quietT+=dt;else ko.quietT=0;
  if((ko.t>=MIN_SHOW&&ko.quietT>=QUIET_NEED)||ko.t>=MAX_SHOW){
   const finishedLevel=ko.level;resetPending();ko.releasedLevel=finishedLevel;ko.opened++;
   // Release v1's guard. On the next fixed step it opens the existing chooser, after the KO has been visible.
   state.choiceFor=-1;transition=Math.max(transition,999);
  }
  return out;
 };
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v8DefeatPresentation:true,koPending:ko.pending,koTime:+ko.t.toFixed(2),koQuiet:+ko.quietT.toFixed(2),koMotion:+ko.lastMotion.toFixed(2),koChestY:+ko.lastChestY.toFixed(2),koOpened:ko.opened,koReleasedLevel:ko.releasedLevel}};
})();
