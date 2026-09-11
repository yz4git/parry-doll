'use strict';
// MIRROR BREAK v11 — SCAR MIRROR: the final Parry Doll replays how the player destroyed the previous bosses.
(()=>{
 if(window.__parryMirrorBreakV11Loaded)return;window.__parryMirrorBreakV11Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const s={history:[],lastSerial:0,bossRef:null,attackCalls:0,scarIndex:0,scarEchoes:0,lastScar:null,pulseT:0};window.__mirrorBreakV11State=s;
 const LABEL=['BLADELESS','HOLLOW','THREADLESS','BELL TOWER'],COLOR=['#ffb36b','#8ce4d3','#d0a6ff','#abd9ff'];
 const clone=m=>({...m,hits:[...(m?.hits||[])]});
 const hud=document.createElement('div');hud.id='mbScarMemory';Object.assign(hud.style,{position:'absolute',right:'max(24px,env(safe-area-inset-right))',top:'112px',zIndex:'30',pointerEvents:'none',textAlign:'right',fontSize:'8px',letterSpacing:'1.8px',lineHeight:'1.45',color:'#aab7b5',textShadow:'0 2px 8px #000',opacity:'0',transition:'opacity .16s'});document.body.appendChild(hud);
 function refreshHud(proc=null){if(level!==4){hud.style.opacity='0';return}hud.style.opacity='.88';const count=s.history.length;hud.innerHTML=`<b style="display:block;color:#e0c68d;letter-spacing:2.4px">SCAR MEMORY ${count}/4</b>${proc?`<span style="color:#f0e4c8">ECHO · ${proc}</span>`:'<span>DESTRUCTION HISTORY</span>'}`}
 function record(hit){if(!hit||hit.level<0||hit.level>3||!hit.serial||hit.serial<=s.lastSerial)return;s.lastSerial=hit.serial;const e={level:hit.level,style:hit.style||'',part:hit.part||null,kind:hit.kind||null,label:hit.label||null};const old=s.history.findIndex(x=>x.level===e.level);if(old>=0)s.history[old]=e;else s.history.push(e);s.history.sort((a,b)=>a.level-b.level);refreshHud()}
 function scarMove(entry){
  const l=entry.level;
  if(l===0)return{name:'SCAR ECHO · BLADELESS',kind:'combo',shape:'cone',wind:.56,active:.70,hits:[.10,.34,.60],range:3.75,arc:1.72,speed:2.9,damage:.78,force:21,recover:.78,motion:1,__scar:true};
  if(l===1)return{name:'SCAR ECHO · HOLLOW',kind:'rush',shape:'line',wind:.69,active:.52,hits:[.21],range:4.45,width:.86,speed:5.2,damage:.94,force:27,recover:.88,motion:0,__scar:true};
  if(l===2)return{name:'SCAR ECHO · THREADLESS',kind:'sweep',shape:'circle',wind:.82,active:.78,hits:[.15,.44,.69],range:4.15,speed:0,damage:.67,force:18,recover:.82,motion:2,__scar:true};
  return{name:'SCAR ECHO · BELL TOWER',kind:'stomp',shape:'circle',wind:1.0,active:.56,hits:[.20],range:4.65,speed:0,damage:1.08,force:35,recover:1.08,motion:2,__scar:true};
 }
 function scarBeat(entry){const p=boss?.nodes?.find(n=>n.name==='chest')?.p||boss?.nodes?.[1]?.p;if(p){ring(p,COLOR[entry.level]);burst(p,COLOR[entry.level],9,3.6)}sound([520,330,680,220][entry.level],.12,'triangle',.022);s.pulseT=.72;refreshHud(LABEL[entry.level])}
 function forceScar(move,entry){const originals=ENEMY_MOVES[4].slice(),forced=originals.map(()=>clone(move)),cores={...state.cores};ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...forced);state.cores.EDGE=state.cores.MIRROR=state.cores.PULSE=0;try{return baseStart(move)}finally{state.cores.EDGE=cores.EDGE;state.cores.MIRROR=cores.MIRROR;state.cores.PULSE=cores.PULSE;ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...originals)}}
 const baseStart=startEnemyAttack;startEnemyAttack=function(move){
  if(boss!==s.bossRef){s.bossRef=boss;s.attackCalls=0;s.scarIndex=0;refreshHud()}
  if(level!==4||mode!=='play'||!boss||boss.hp<=0||state.broken||!s.history.length)return baseStart(move);
  s.attackCalls++;if(s.attackCalls%4!==0)return baseStart(move);
  const entry=s.history[s.scarIndex++%s.history.length],scar=scarMove(entry),out=forceScar(scar,entry);s.scarEchoes++;s.lastScar=LABEL[entry.level];scarBeat(entry);return out;
 };
 const baseReset=reset;reset=function(l=0){const prev=typeof level==='number'?level:-1,out=baseReset(l);if(l===0&&prev>=4){s.history.length=0;s.lastSerial=0}s.bossRef=boss;s.attackCalls=0;s.scarIndex=0;s.pulseT=0;refreshHud();return out};
 function frame(){const hit=window.__mirrorBreakV9State?.stageHit;if(hit)record(hit);s.pulseT=Math.max(0,s.pulseT-1/60);if(level===4&&s.pulseT<=0)refreshHud();else if(level!==4)hud.style.opacity='0';requestAnimationFrame(frame)}requestAnimationFrame(frame);
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v11:true,scarMirror:true,destructionHistory:s.history.map(x=>({...x})),scarMemoryCount:s.history.length,scarAttackCalls:s.attackCalls,scarEchoes:s.scarEchoes,lastScarEcho:s.lastScar,scarEchoSuppressed:level===4&&!!state.broken}};
 refreshHud();
})();
