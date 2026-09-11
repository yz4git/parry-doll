'use strict';
// MIRROR BREAK v5 — BODY BREAK changes the boss combat language, not only the silhouette.
(()=>{
 if(window.__parryMirrorBreakV5Loaded)return;window.__parryMirrorBreakV5Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const s={bossRef:null,adapted:0,postBreakAttacks:0,profile:'',coreMode:null,coreCycles:0,lastPattern:null,lastSource:'',mobilityScale:1};
 window.__mirrorBreakV5State=s;
 const brokenNow=()=>!!(boss&&state.boss===boss&&state.broken&&state.part);
 const clone=m=>({...m,hits:[...(m?.hits||[])]});
 const cap=(x,a,b)=>Math.max(a,Math.min(b,x));
 const profiles=[
  'KICK STANCE · BLADE LOST',
  'LIMP HUNT · LEAP LOST',
  'FIVE-LEG STANCE · AERIAL LOST',
  'FOOTWORK SHIFT · STOMP BIAS',
  'CORE ERROR · COPY OVERLOAD'
 ];
 function resetLocal(){s.bossRef=boss;s.adapted=0;s.postBreakAttacks=0;s.profile=profiles[level]||'';s.coreMode=null;s.coreCycles=0;s.lastPattern=null;s.lastSource='';s.mobilityScale=1}
 function armLost(move,l){
  const m=clone(move),n=String(m.name||'');
  if(m.kind==='thrust'||n.includes('片腕・灰突き')){m.name='断剣・肩穿ち';m.kind='rush';m.shape='line';m.wind*=1.05;m.active=.38;m.hits=[.16];m.range=Math.min(3.45,m.range||3.45);m.width=.84;m.speed=cap(m.speed||3.8,3.5,4.35);m.damage*=.90;m.force*=.88;m.recover*=1.22;m.motion=1}
  else if(m.kind==='slam'){m.name='断剣・踵落とし';m.kind='slam';m.shape='cone';m.wind*=1.10;m.active=.43;m.hits=[.18];m.range=Math.min(3.05,m.range||3.05);m.arc=Math.min(1.14,m.arc||1.14);m.speed=.55;m.damage*=.88;m.force*=.92;m.recover*=1.28;m.motion=2}
  else{m.name='断剣・灰蹴連';m.kind='combo';m.shape='cone';m.wind*=1.06;m.active=.72;m.hits=[.15,.50];m.range=Math.min(3.10,m.range||3.10);m.arc=Math.min(1.82,m.arc||1.82);m.speed=Math.min(1.55,m.speed||1.4);m.damage*=.80;m.force*=.82;m.recover*=1.18;m.motion=0}
  return m;
 }
 function houndLeg(move){
  const m=clone(move),n=String(m.name||'');
  if(['leap','rush'].includes(m.kind)||n.includes('傷脚')){m.name='傷脚・這い牙';m.kind='rush';m.shape='line';m.wind*=1.08;m.active=.52;m.hits=[.18,.41];m.range=Math.min(3.65,m.range||3.65);m.width=.92;m.speed=cap((m.speed||4.2)*.62,3.4,4.4);m.damage*=.88;m.force*=.84;m.recover*=1.30;m.motion=1}
  else if(m.kind==='sweep'){m.name='傷脚・低尾薙ぎ';m.kind='sweep';m.shape='circle';m.wind*=1.04;m.active=.48;m.hits=[.20];m.range=Math.min(3.35,m.range||3.35);m.speed=0;m.damage*=.92;m.force*=.88;m.recover*=1.22;m.motion=0}
  else{m.name='傷脚・噛み刻み';m.kind='combo';m.shape='cone';m.wind*=1.05;m.active=.68;m.hits=[.14,.49];m.range=Math.min(2.85,m.range||2.85);m.arc=Math.min(1.35,m.arc||1.35);m.speed=Math.min(1.35,m.speed||1.35);m.damage*=.86;m.force*=.86;m.recover*=1.17;m.motion=0}
  return m;
 }
 function spiderLeg(move){
  const m=clone(move),n=String(m.name||'');
  if(m.kind==='leap'){m.name='断脚・吊糸突き';m.kind='thrust';m.shape='line';m.wind*=1.08;m.active=.42;m.hits=[.17];m.range=Math.min(4.05,m.range||4.05);m.width=.86;m.speed=3.65;m.damage*=.90;m.force*=.88;m.recover*=1.30;m.motion=1}
  else if(m.kind==='thrust'||m.kind==='combo'||n.includes('断脚')){m.name='断脚・五方糸';m.kind='sweep';m.shape='circle';m.wind*=1.10;m.active=.64;m.hits=[.18,.47];m.range=Math.min(3.95,m.range||3.95);m.speed=0;m.damage*=.80;m.force*=.86;m.recover*=1.24;m.motion=0}
  else{m.name='五脚・偏輪舞';m.kind='sweep';m.shape='circle';m.wind*=1.07;m.active=.55;m.hits=[.21];m.range=Math.min(4.05,m.range||4.05);m.speed=0;m.damage*=.88;m.force*=.90;m.recover*=1.18;m.motion=0}
  return m;
 }
 function giantArm(move){
  const m=clone(move),n=String(m.name||'');
  if(m.kind==='stomp'||n.includes('砕腕')){m.name=n.includes('砕腕')?'片腕・崩鐘震脚':'片鐘・地鳴り';m.kind='stomp';m.shape='circle';m.wind*=n.includes('砕腕')?1.06:.94;m.active=.52;m.hits=[.19];m.range=Math.min(4.45,m.range||4.45);m.speed=0;m.damage*=n.includes('砕腕')?.88:1.04;m.force*=n.includes('砕腕')?.94:1.08;m.recover*=n.includes('砕腕')?1.16:.96;m.motion=2}
  else if(m.kind==='rush'){m.name='片鐘・肩崩し';m.kind='rush';m.shape='line';m.wind*=1.12;m.active=.48;m.hits=[.19];m.range=Math.min(3.75,m.range||3.75);m.width=1.20;m.speed=Math.min(3.9,m.speed||3.9);m.damage*=.86;m.force*=.92;m.recover*=1.28;m.motion=1}
  else{m.name='片鐘・半月薙ぎ';m.kind='sweep';m.shape='cone';m.wind*=1.12;m.active=.48;m.hits=[.20];m.range=Math.min(4.45,m.range||4.45);m.arc=Math.min(2.05,m.arc||2.05);m.speed=.35;m.damage*=.84;m.force*=.90;m.recover*=1.24;m.motion=0}
  return m;
 }
 function overload(move){
  const m=clone(move),modes=['EDGE','MIRROR','PULSE'],mode=modes[s.coreCycles++%modes.length];s.coreMode=mode;
  if(mode==='EDGE'){m.name='暴走刃・'+m.name;m.wind*=.92;m.speed*=1.12;m.damage*=1.18;m.force*=1.06;m.recover*=1.32}
  else if(mode==='MIRROR'){m.name='遅延鏡・'+m.name;m.wind*=1.28;m.speed*=.94;m.hits=m.hits.map((h,i)=>h+i*.055);m.recover*=.80}
  else{m.name='脈動過負荷・'+m.name;m.range*=1.16;m.force*=1.30;m.speed*=.84;m.damage*=1.05;m.recover*=1.16}
  return m;
 }
 function adapt(move){if(!move||move.__mbV5||!brokenNow())return move;let m;
  if(level===0)m=armLost(move,level);else if(level===1)m=houndLeg(move);else if(level===2)m=spiderLeg(move);else if(level===3)m=giantArm(move);else m=overload(move);
  Object.defineProperty(m,'__mbV5',{value:true,enumerable:false});s.adapted++;s.postBreakAttacks++;s.lastSource=move.name||move.kind||'';return m;
 }
 function adaptCurrentAttack(){
  if(!brokenNow()||!boss?.pattern||boss.pattern.__mbV5)return false;
  const old=boss.pattern,m=adapt(old);if(m===old)return false;
  if(boss.wind>0){const oldTotal=Math.max(.001,boss.windDuration||old.wind||boss.wind),progress=cap(1-boss.wind/oldTotal,0,.92),newTotal=Math.max(.08,m.wind*(boss.enraged?.9:1));boss.windDuration=newTotal;boss.wind=Math.max(.025,newTotal*(1-progress))}
  boss.pattern=m;s.lastPattern=m;return true;
 }
 function mobility(){
  if(!brokenNow()||!boss)return;
  let scale=1;if(level===1)scale=.72;else if(level===2)scale=.78;else if(level===3)scale=.94;
  s.mobilityScale=scale;
  if((level===1||level===2)&&boss.wind<=0&&boss.strike<=0&&boss.down<=0&&boss.stun<=0){boss.vel.x*=scale;boss.vel.z*=scale}
  if(level===3&&boss.wind<=0&&boss.strike<=0&&boss.down<=0){boss.vel.x*=scale;boss.vel.z*=scale}
 }
 function syncHud(){
  if(!brokenNow())return;const hud=document.getElementById('mbBreakHud'),span=hud?.querySelector('span');if(!span)return;
  if(level===4)span.textContent=`CORE ERROR · ${s.coreMode||'UNSTABLE'}`;else span.textContent=s.profile||profiles[level]||'TACTIC SHIFT';
 }
 const v5Start=startEnemyAttack;startEnemyAttack=function(move){const out=v5Start(move);adaptCurrentAttack();syncHud();return out};
 const v5UpdateEnemy=updateEnemy;updateEnemy=function(dt){const out=v5UpdateEnemy(dt);adaptCurrentAttack();mobility();return out};
 const v5Step=step;step=function(dt){const out=v5Step(dt);if(boss!==s.bossRef||state.level!==level){resetLocal()}adaptCurrentAttack();mobility();syncHud();return out};
 const v5Reset=reset;reset=function(l=0){const out=v5Reset(l);resetLocal();return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v5:true,tacticShift:brokenNow(),behaviorProfile:s.profile||profiles[level]||'',adaptedAttacks:s.adapted,postBreakAttacks:s.postBreakAttacks,adaptedPattern:boss?.pattern?.__mbV5?boss.pattern.name:null,adaptedKind:boss?.pattern?.__mbV5?boss.pattern.kind:null,coreOverload:s.coreMode,mobilityScale:s.mobilityScale,lastAdaptedSource:s.lastSource}};
 resetLocal();
})();
