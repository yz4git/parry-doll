'use strict';
// MIRROR BREAK v9 — BOSS DESTRUCTION 2.0: broken-body motion language + part-aware KO physics.
(()=>{
 if(window.__parryMirrorBreakV9Loaded)return;window.__parryMirrorBreakV9Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const styles=['BLADELESS SPIN CRASH','HOLLOW TUMBLE','FIVE-LEG CARTWHEEL','BELL TOWER COLLAPSE','MIRROR CORE FAILURE'];
 const s={bossRef:null,postBreakPoseTicks:0,specialKOs:0,lastKO:null,koBoss:null,koT:0,landing:false,settleBeat:false,landingT:0};
 window.__mirrorBreakV9State=s;
 const brokenNow=d=>!!(d&&d===boss&&state.boss===d&&state.broken&&state.part);
 const horizontal=v=>{const q=V(v?.x||0,0,v?.z||0);return len(q)>.001?norm(q):V(Math.sin(boss?.face||0),0,Math.cos(boss?.face||0))};
 const sideOf=v=>V(v.z,0,-v.x);
 const named=(d,name,preferLast=false)=>{const list=d?.nodes?.filter(n=>n.name===name)||[];return preferLast?list[list.length-1]:list[0]};
 function resetLocal(){s.bossRef=boss;s.postBreakPoseTicks=0;s.lastKO=null;s.koBoss=null;s.koT=0;s.landing=false;s.settleBeat=false;s.landingT=0}
 function attackPhase(d){const m=d?.pattern;if(!m)return 0;if(d.wind>0)return clamp(1-d.wind/Math.max(.001,d.windDuration||m.wind||1),0,1);if(d.strike>0)return clamp(d.strikeElapsed/Math.max(.001,m.active||1),0,1);return 0}
 const basePose=enemyPoseTarget;enemyPoseTarget=function(d,n){
  const p=basePose(d,n);if(!brokenNow(d)||d.hp<=0||level>3)return p;
  s.postBreakPoseTicks++;const sc=d.spec.scale,phase=attackPhase(d),m=d.pattern||{},active=(d.wind>0||d.strike>0)?Math.sin(clamp(phase,0,1)*Math.PI):0;
  if(level===0){
   // One-handed duelist: weight moves to the intact side and kicks carry the attack silhouette.
   if(n.name==='chest'||n.name==='head'){p.x-=.10*sc;p.z+=.06*sc+active*.08*sc}
   if(n.name==='hip')p.x-=.08*sc;
   if((n.name==='knee'||n.name==='foot')&&m.__mbV5){const front=n.rest.x>0?1:-1;p.z+=front*active*(m.kind==='slam'?.48:.30)*sc;p.y+=n.name==='foot'?active*.10*sc:0}
   if(n.name==='offhand')p.x-=.10*sc;
  }else if(level===1){
   // Hound: broken foreleg forces a permanent low hunt and uneven front support.
   if(n.name==='chest'){p.y-=.20*sc;p.z+=.12*sc}
   if(n.name==='head'){p.y-=.24*sc;p.z+=.18*sc+active*.10*sc}
   if(n.name==='hip')p.y-=.10*sc;
   if(n.name==='knee'||n.name==='foot'){const damaged=n.rest.z>0;if(!damaged)p.y-=.04*sc;else p.y-=.13*sc}
  }else if(level===2){
   // Spider: one missing spear-leg makes the whole chassis cant and rotate asymmetrically.
   if(n.name==='hip'){p.x+=.13*sc;p.y-=.05*sc}
   if(n.name==='chest'||n.name==='head'){p.x-=.16*sc;p.y-=.08*sc;p.z+=active*.06*sc}
   if(n.name==='knee'||n.name==='foot'){const support=Math.sign(n.rest.x||1);p.y+=(support<0?.055:-.025)*sc;p.z+=support*active*.11*sc}
  }else if(level===3){
   // Giant: without the bell arm the torso counterbalances over the intact shoulder and legs.
   if(n.name==='chest'||n.name==='head'){p.x-=.14*sc;p.z+=.055*sc}
   if(n.name==='hip')p.x-=.08*sc;
   if(n.name==='offhand')p.x-=.12*sc;
   if((n.name==='knee'||n.name==='foot')&&m.kind==='stomp'){p.y-=active*(n.name==='foot'?.10:.06)*sc;p.z+=Math.sign(n.rest.x||1)*active*.16*sc}
  }
  return p;
 };
 function koPoint(d){return named(d,'chest')?.p||named(d,'hip')?.p||d.pos}
 function startSpecialKO(d,force,point){
  if(d!==boss||level>3||!brokenNow(d))return;
  const dir=horizontal(force),side=sideOf(dir),sc=d.spec.scale,chest=named(d,'chest'),head=named(d,'head'),hip=named(d,'hip');
  s.specialKOs++;s.lastKO=styles[level];s.koBoss=d;s.koT=0;s.landing=false;s.settleBeat=false;s.landingT=0;
  d.wind=d.strike=0;d.pattern=null;d.ai=99;
  if(level===0){
   // Tangential hit spins the bladeless body before it folds onto the arena.
   if(chest)d.impulse(chest.p,add(add(mul(dir,18),mul(side,22)),V(0,9,0)));
   if(head)d.impulse(head.p,add(mul(side,15),V(0,7,0)));
  }else if(level===1){
   // The hound can no longer catch itself on the broken front leg; drive the head low into a tumble.
   if(head)d.impulse(head.p,add(mul(dir,30),V(0,5,0)));
   if(hip)d.impulse(hip.p,add(add(mul(dir,16),mul(side,-9)),V(0,10,0)));
  }else if(level===2){
   // Missing spear leg turns the kill into an off-axis cartwheel/sprawl.
   if(chest)d.impulse(chest.p,add(add(mul(dir,14),mul(side,28)),V(0,12,0)));
   const feet=d.nodes.filter(n=>n.name==='foot');const far=feet.reduce((a,n)=>!a||n.rest.x<a.rest.x?n:a,null);if(far)d.impulse(far.p,add(mul(side,-24),V(0,15,0)));
  }else if(level===3){
   // The giant should read as a collapsing tower, not a light ragdoll launch.
   if(chest)d.impulse(chest.p,add(mul(dir,15),V(0,2.5,0)));
   if(head)d.impulse(head.p,add(mul(dir,12),V(0,1.5,0)));
   if(hip)d.impulse(hip.p,add(mul(dir,8),V(0,.5,0)));
  }
  const p=point||koPoint(d);burst(p,level===3?'#d7b273':'#efb47a',14+level*3,4+sc);ring(p,level===3?'#e1c386':'#ffc37f');
 }
 const baseHurt=hurt;hurt=function(d,amount,force,point){
  const enemy=d===boss&&!d.player,before=d?.hp||0,wasBroken=enemy&&brokenNow(d);const out=baseHurt(d,amount,force,point);
  if(out&&enemy&&before>0&&d.hp<=0&&wasBroken)startSpecialKO(d,force,point);
  return out;
 };
 function dampNodes(d,amount=.34){for(const n of d?.nodes||[]){const velocity=sub(n.p,n.prev);n.prev=sub(n.p,mul(velocity,amount))}}
 function landingCheck(d){
  const chest=named(d,'chest')||named(d,'hip'),sc=d.spec.scale;if(!chest)return false;
  const threshold=level===3?.92*sc:level===1?.58*sc:.68*sc;return chest.p.y<threshold;
 }
 function updateKO(dt){
  if(!s.koBoss||s.koBoss!==boss||boss.hp>0){if(s.koBoss&&s.koBoss!==boss){s.koBoss=null;s.koT=0}s.landing=false;return}
  s.koT+=dt;
  if(!s.landing&&s.koT>.22&&(landingCheck(boss)||s.koT>(level===3?1.35:1.05))){
   s.landing=true;s.landingT=s.koT;const p=koPoint(boss),q=V(p.x,.08,p.z);groundImpact(q,level===3?2.7:level===2?1.8:1.45);ring(q,level===3?'#e3c17e':'#cfa87a');dampNodes(boss,level===3?.22:.34);shake=Math.max(shake,level===3?.32:.20);
  }
  if(s.landing&&!s.settleBeat&&level===3&&s.koT-s.landingT>.28){
   s.settleBeat=true;const p=koPoint(boss),q=V(p.x,.07,p.z);groundImpact(q,1.65);dampNodes(boss,.18);
  }
 }
 const baseStep=step;step=function(dt){const out=baseStep(dt);if(boss!==s.bossRef){resetLocal()}updateKO(dt);return out};
 const baseReset=reset;reset=function(l=0){const out=baseReset(l);resetLocal();return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v9:true,bossDestruction2:true,postBreakPoseTicks:s.postBreakPoseTicks,specialKOs:s.specialKOs,lastSpecialKO:s.lastKO,koStyle:s.koBoss===boss?s.lastKO:null,koTime:+s.koT.toFixed(2),koLanded:s.landing,koSettleBeat:s.settleBeat}};
 resetLocal();
})();
