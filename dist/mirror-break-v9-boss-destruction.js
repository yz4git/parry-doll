'use strict';
// MIRROR BREAK v9 — BOSS DESTRUCTION 2.0: broken-body motion language + part-aware KO physics.
(()=>{
 if(window.__parryMirrorBreakV9Loaded)return;window.__parryMirrorBreakV9Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const styles=['BLADELESS SPIN CRASH','HOLLOW TUMBLE','FIVE-LEG CARTWHEEL','BELL TOWER COLLAPSE','MIRROR CORE FAILURE'];
 const s={bossRef:null,postBreakPoseTicks:0,specialKOs:0,lastKO:null,koBoss:null,koT:0,koStartedAt:0,landing:false,settleBeat:false,landingT:0,landingAt:0};
 window.__mirrorBreakV9State=s;
 const brokenNow=d=>!!(d&&d===boss&&state.boss===d&&state.broken&&state.part);
 const horizontal=v=>{const q=V(v?.x||0,0,v?.z||0);return len(q)>.001?norm(q):V(Math.sin(boss?.face||0),0,Math.cos(boss?.face||0))};
 const sideOf=v=>V(v.z,0,-v.x);
 const named=(d,name,preferLast=false)=>{const list=d?.nodes?.filter(n=>n.name===name)||[];return preferLast?list[list.length-1]:list[0]};
 function resetLocal(){s.bossRef=boss;s.postBreakPoseTicks=0;s.lastKO=null;s.koBoss=null;s.koT=0;s.koStartedAt=0;s.landing=false;s.settleBeat=false;s.landingT=0;s.landingAt=0}
 function attackPhase(d){const m=d?.pattern;if(!m)return 0;if(d.wind>0)return clamp(1-d.wind/Math.max(.001,d.windDuration||m.wind||1),0,1);if(d.strike>0)return clamp(d.strikeElapsed/Math.max(.001,m.active||1),0,1);return 0}
 const basePose=enemyPoseTarget;enemyPoseTarget=function(d,n){
  const p=basePose(d,n);if(!brokenNow(d)||d.hp<=0||level>3)return p;
  s.postBreakPoseTicks++;const sc=d.spec.scale,phase=attackPhase(d),m=d.pattern||{},active=(d.wind>0||d.strike>0)?Math.sin(clamp(phase,0,1)*Math.PI):0;
  if(level===0){
   if(n.name==='chest'||n.name==='head'){p.x-=.10*sc;p.z+=.06*sc+active*.08*sc}
   if(n.name==='hip')p.x-=.08*sc;
   if((n.name==='knee'||n.name==='foot')&&m.__mbV5){const front=n.rest.x>0?1:-1;p.z+=front*active*(m.kind==='slam'?.48:.30)*sc;p.y+=n.name==='foot'?active*.10*sc:0}
   if(n.name==='offhand')p.x-=.10*sc;
  }else if(level===1){
   if(n.name==='chest'){p.y-=.20*sc;p.z+=.12*sc}
   if(n.name==='head'){p.y-=.24*sc;p.z+=.18*sc+active*.10*sc}
   if(n.name==='hip')p.y-=.10*sc;
   if(n.name==='knee'||n.name==='foot'){const damaged=n.rest.z>0;if(!damaged)p.y-=.04*sc;else p.y-=.13*sc}
  }else if(level===2){
   if(n.name==='hip'){p.x+=.13*sc;p.y-=.05*sc}
   if(n.name==='chest'||n.name==='head'){p.x-=.16*sc;p.y-=.08*sc;p.z+=active*.06*sc}
   if(n.name==='knee'||n.name==='foot'){const support=Math.sign(n.rest.x||1);p.y+=(support<0?.055:-.025)*sc;p.z+=support*active*.11*sc}
  }else if(level===3){
   if(n.name==='chest'||n.name==='head'){p.x-=.14*sc;p.z+=.055*sc}
   if(n.name==='hip')p.x-=.08*sc;
   if(n.name==='offhand')p.x-=.12*sc;
   if((n.name==='knee'||n.name==='foot')&&m.kind==='stomp'){p.y-=active*(n.name==='foot'?.10:.06)*sc;p.z+=Math.sign(n.rest.x||1)*active*.16*sc}
  }
  return p;
 };
 function koPoint(d){return named(d,'chest')?.p||named(d,'hip')?.p||d.pos}
 function dampNodes(d,amount=.34){for(const n of d?.nodes||[]){const velocity=sub(n.p,n.prev);n.prev=sub(n.p,mul(velocity,amount))}}
 function startSpecialKO(d,force,point){
  if(d!==boss||level>3||!brokenNow(d))return;
  const dir=horizontal(force),side=sideOf(dir),sc=d.spec.scale,chest=named(d,'chest'),head=named(d,'head'),hip=named(d,'hip');
  s.specialKOs++;s.lastKO=styles[level];s.koBoss=d;s.koT=0;s.koStartedAt=performance.now();s.landing=false;s.settleBeat=false;s.landingT=0;s.landingAt=0;
  d.wind=d.strike=0;d.pattern=null;d.ai=99;
  // The base lethal hit already injects a second 1.8x impulse. Keep some of it, but tame it before
  // applying the boss-specific silhouette so a dramatic finish stays inside the arena/camera.
  dampNodes(d,level===3?.18:.28);
  if(level===0){
   if(chest)d.impulse(chest.p,add(add(mul(dir,10),mul(side,16)),V(0,6.2,0)));
   if(head)d.impulse(head.p,add(mul(side,10),V(0,4.8,0)));
  }else if(level===1){
   if(head)d.impulse(head.p,add(mul(dir,19),V(0,3.2,0)));
   if(hip)d.impulse(hip.p,add(add(mul(dir,10),mul(side,-7)),V(0,7.5,0)));
  }else if(level===2){
   if(chest)d.impulse(chest.p,add(add(mul(dir,9),mul(side,20)),V(0,8.5,0)));
   const feet=d.nodes.filter(n=>n.name==='foot');const far=feet.reduce((a,n)=>!a||n.rest.x<a.rest.x?n:a,null);if(far)d.impulse(far.p,add(mul(side,-17),V(0,10.5,0)));
  }else if(level===3){
   if(chest)d.impulse(chest.p,add(mul(dir,10),V(0,1.6,0)));
   if(head)d.impulse(head.p,add(mul(dir,8),V(0,.9,0)));
   if(hip)d.impulse(hip.p,add(mul(dir,5),V(0,.25,0)));
  }
  const p=point||koPoint(d);burst(p,level===3?'#d7b273':'#efb47a',14+level*3,4+sc);ring(p,level===3?'#e1c386':'#ffc37f');
 }
 const baseHurt=hurt;hurt=function(d,amount,force,point){
  const enemy=d===boss&&!d.player,before=d?.hp||0,wasBroken=enemy&&brokenNow(d);const out=baseHurt(d,amount,force,point);
  if(out&&enemy&&before>0&&d.hp<=0&&wasBroken)startSpecialKO(d,force,point);
  return out;
 };
 function landingCheck(d){
  const chest=named(d,'chest')||named(d,'hip'),sc=d.spec.scale;if(!chest)return false;
  const threshold=level===3?.92*sc:level===1?.58*sc:.68*sc;return chest.p.y<threshold;
 }
 function updateKO(now=performance.now()){
  if(!s.koBoss||s.koBoss!==boss||boss.hp>0){if(s.koBoss&&s.koBoss!==boss){s.koBoss=null;s.koStartedAt=0;s.koT=0}s.landing=false;return}
  s.koT=s.koStartedAt?Math.max(0,(now-s.koStartedAt)/1000):s.koT;
  if(!s.landing&&s.koT>.22&&(landingCheck(boss)||s.koT>(level===3?1.35:1.05))){
   s.landing=true;s.landingT=s.koT;s.landingAt=now;const p=koPoint(boss),q=V(p.x,.08,p.z);groundImpact(q,level===3?2.7:level===2?1.8:1.45);ring(q,level===3?'#e3c17e':'#cfa87a');dampNodes(boss,level===3?.22:.34);shake=Math.max(shake,level===3?.32:.20);
  }
  if(s.landing&&!s.settleBeat&&level===3&&now-s.landingAt>280){
   s.settleBeat=true;const p=koPoint(boss),q=V(p.x,.07,p.z);groundImpact(q,1.65);dampNodes(boss,.18);
  }
 }
 function syncBoss(){if(boss!==s.bossRef)resetLocal()}
 const baseStep=step;step=function(dt){const out=baseStep(dt);syncBoss();return out};
 const baseReset=reset;reset=function(l=0){const out=baseReset(l);resetLocal();return out};
 let rafLast=performance.now();function koFrame(now){rafLast=now;syncBoss();updateKO(now);requestAnimationFrame(koFrame)}requestAnimationFrame(koFrame);
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v9:true,bossDestruction2:true,postBreakPoseTicks:s.postBreakPoseTicks,specialKOs:s.specialKOs,lastSpecialKO:s.lastKO,koStyle:s.koBoss===boss?s.lastKO:null,koTime:+s.koT.toFixed(2),koLanded:s.landing,koSettleBeat:s.settleBeat}};
 resetLocal();
})();
