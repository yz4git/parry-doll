'use strict';
// MIRROR BREAK v8 — let the KO launch/fall/down beat play before revealing the DOLL CORE reward.
(()=>{
 if(window.__parryMirrorBreakV8DefeatPresentationLoaded)return;window.__parryMirrorBreakV8DefeatPresentationLoaded=true;
 const state=window.__mirrorBreakState,chooser=document.getElementById('mbCoreChoice');if(!state||!chooser)return;
 const ko={pending:false,level:-1,t:0,quietT:0,opened:0,lastMotion:0,lastChestY:0,lastOpenT:0,releasedLevel:-1,start:0,lastFrame:0,boss:null};
 window.__mirrorBreakV8DefeatState=ko;
 const MIN_SHOW=1.85,QUIET_NEED=.30,MAX_SHOW=3.80;
 const style=document.createElement('style');style.textContent='#mbCoreChoice.mb-ko-hold{display:none!important}';document.head.appendChild(style);
 const releasedBosses=new WeakSet();
 function motion(dt){
  if(!boss?.nodes?.length)return 0;const inv=1/Math.max(dt,1/120);let sum=0,max=0;
  for(const n of boss.nodes){const v=len(sub(n.p,n.prev))*inv;sum+=v;max=Math.max(max,v)}
  return max*.62+(sum/boss.nodes.length)*.38;
 }
 function resetHold(){ko.pending=false;ko.level=-1;ko.t=0;ko.quietT=0;ko.lastMotion=0;ko.lastChestY=0;ko.start=0;ko.lastFrame=0;ko.boss=null;chooser.classList.remove('mb-ko-hold')}
 function beginHold(){
  if(ko.pending||!boss||releasedBosses.has(boss))return;
  ko.pending=true;ko.level=level;ko.boss=boss;ko.t=0;ko.quietT=0;ko.start=performance.now();ko.lastFrame=ko.start;
  chooser.classList.add('mb-ko-hold');chooser.classList.remove('show');
  transition=Math.max(transition,999);attackQueued=parryQueued=false;attackBuffer=parryBuffer=0;
 }
 function releaseHold(){
  if(!ko.pending)return;const b=ko.boss,finishedLevel=ko.level,shownAt=ko.t;
  if(b)releasedBosses.add(b);ko.pending=false;ko.opened++;ko.lastOpenT=shownAt;ko.releasedLevel=finishedLevel;
  chooser.classList.remove('mb-ko-hold');chooser.classList.add('show');
 }
 function shouldGate(){return mode==='play'&&level<=3&&boss?.hp<=0&&player?.hp>0&&state.choice&&chooser.classList.contains('show')&&!releasedBosses.has(boss)}
 function gateIfNeeded(){if(shouldGate())beginHold()}
 const observer=new MutationObserver(gateIfNeeded);observer.observe(chooser,{attributes:true,attributeFilter:['class']});
 function watch(now){
  gateIfNeeded();
  if(ko.pending){
   if(mode!=='play'||level!==ko.level||boss!==ko.boss||!boss||boss.hp>0||!state.choice){resetHold()}
   else{
    const dt=Math.min(.05,Math.max(1/240,(now-ko.lastFrame)/1000));ko.lastFrame=now;ko.t=(now-ko.start)/1000;transition=Math.max(transition,999);
    ko.lastMotion=motion(dt);const chest=boss.nodes?.find(n=>n.name==='chest')||boss.nodes?.[1];ko.lastChestY=chest?.p?.y||0;
    const lowEnough=!chest||ko.lastChestY<Math.max(.82,boss.spec.scale*1.05);
    if(ko.t>=MIN_SHOW&&lowEnough&&ko.lastMotion<1.55)ko.quietT+=dt;else ko.quietT=0;
    if((ko.t>=MIN_SHOW&&ko.quietT>=QUIET_NEED)||ko.t>=MAX_SHOW)releaseHold();
   }
  }
  requestAnimationFrame(watch);
 }
 requestAnimationFrame(watch);
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v8DefeatPresentation:true,koPending:ko.pending,koTime:+ko.t.toFixed(2),koQuiet:+ko.quietT.toFixed(2),koMotion:+ko.lastMotion.toFixed(2),koChestY:+ko.lastChestY.toFixed(2),koOpened:ko.opened,koLastOpenT:+ko.lastOpenT.toFixed(2),koReleasedLevel:ko.releasedLevel,koOverlayHeld:chooser.classList.contains('mb-ko-hold')}};
})();
