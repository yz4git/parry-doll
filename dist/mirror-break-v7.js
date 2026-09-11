'use strict';
// MIRROR BREAK v7 — THE PARRY DOLL turns the player's DOLL CORE build into real signature attacks.
(()=>{
 if(window.__parryMirrorBreakV7Loaded)return;window.__parryMirrorBreakV7Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const s={bossRef:null,attackCalls:0,echoIndex:0,echoes:0,lastEcho:null,history:[],pulseT:0};
 window.__mirrorBreakV7State=s;
 const clone=m=>({...m,hits:[...(m?.hits||[])]});
 const color={EDGE:'#ffd98b',MIRROR:'#b2fff0',PULSE:'#a9dcff'};
 function brokenFinal(){return !!(level===4&&boss&&state.boss===boss&&state.broken)}
 function pool(){const out=[],c=state.cores||{};for(const key of ['EDGE','MIRROR','PULSE'])for(let i=0;i<(c[key]||0);i++)out.push(key);return out}
 function echoMove(key){
  if(key==='EDGE')return{name:'CORE ECHO · EDGE',kind:'combo',shape:'cone',wind:.58,active:.66,hits:[.10,.34,.58],range:3.65,arc:1.72,speed:2.85,damage:.72,force:19,recover:.82,motion:0};
  if(key==='MIRROR')return{name:'CORE ECHO · MIRROR',kind:'combo',shape:'cone',wind:.78,active:.92,hits:[.11,.49,.81],range:3.55,arc:1.62,speed:1.55,damage:.70,force:18,recover:.78,motion:0};
  return{name:'CORE ECHO · PULSE',kind:'stomp',shape:'circle',wind:1.02,active:.52,hits:[.19],range:4.35,speed:0,damage:1.02,force:31,recover:1.08,motion:2};
 }
 function resetLocal(){s.bossRef=boss;s.attackCalls=0;s.echoIndex=0;s.echoes=0;s.lastEcho=null;s.history.length=0;s.pulseT=0}
 function echoBeat(key){const p=boss?.nodes?.find(n=>n.name==='chest')?.p||boss?.nodes?.[1]?.p;if(p){ring(p,color[key]);burst(p,color[key],7,3.2)}sound(key==='EDGE'?560:key==='MIRROR'?760:300,.10,'triangle',.018);s.pulseT=.42}
 function scheduleEcho(){
  if(level!==4||mode!=='play'||!boss||boss.hp<=0||brokenFinal())return null;const p=pool();if(!p.length)return null;
  s.attackCalls++;if(s.attackCalls%3!==0)return null;const key=p[s.echoIndex++%p.length];return{key,move:echoMove(key)};
 }
 function forceThroughAdaptive(move,call){
  const originals=ENEMY_MOVES[4].slice(),forced=originals.map(()=>clone(move));ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...forced);
  try{return call(move)}finally{ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...originals)}
 }
 const v7Start=startEnemyAttack;startEnemyAttack=function(move){
  if(boss!==s.bossRef)resetLocal();const echo=scheduleEcho();if(!echo)return v7Start(move);
  const out=forceThroughAdaptive(echo.move,m=>v7Start(m));s.echoes++;s.lastEcho=echo.key;s.history.push(echo.key);if(s.history.length>12)s.history.shift();echoBeat(echo.key);return out;
 };
 const v7Reset=reset;reset=function(l=0){const out=v7Reset(l);resetLocal();return out};
 const v7Step=step;step=function(dt){const out=v7Step(dt);if(boss!==s.bossRef)resetLocal();s.pulseT=Math.max(0,s.pulseT-dt);return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v7:true,coreEcho:true,coreEchoCalls:s.attackCalls,coreEchoes:s.echoes,lastCoreEcho:s.lastEcho,coreEchoHistory:[...s.history],coreEchoSuppressed:brokenFinal()}};
 resetLocal();
})();
