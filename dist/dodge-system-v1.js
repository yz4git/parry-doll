'use strict';
// Dodge system v1.1: gold attacks are PARRY responses, cyan attacks are DODGE-only responses.
(()=>{
 if(window.__parryDodgeSystemV1Loaded)return;window.__parryDodgeSystemV1Loaded=true;
 const CYAN='#67ddff';
 const DODGE_SUCCESS='#ff5ca4';
 let dodgeQueued=false,dodgeTimer=0,dodgeIFrame=0,dodgeCool=0,dodges=0,perfectDodges=0,dodgeSide=1;
 let testForcedMove=null;
 const dodgeTestMode=new URLSearchParams(location.search).has('dodgecheck');

 const EXTRA_DODGE_MOVES=[
  [
   {name:'灰影・交差抜け',kind:'sweep',shape:'cone',response:'dodge',wind:1.04,active:.46,hits:[.18],range:3.7,arc:2.45,speed:1.1,damage:1.05,force:23,recover:1.08,motion:0},
   {name:'残火・貫通走り',kind:'rush',shape:'line',response:'dodge',wind:.93,active:.58,hits:[.18,.44],range:4.7,width:.82,speed:7.4,damage:.72,force:21,recover:1.24,motion:1}
  ],
  [
   {name:'狩猟跳躍・双牙',kind:'leap',shape:'circle',response:'dodge',wind:.98,active:.60,hits:[.45],range:3.45,speed:7.8,damage:1.18,force:29,recover:1.28,motion:2},
   {name:'咆哮衝撃輪',kind:'sweep',shape:'circle',response:'dodge',wind:1.12,active:.48,hits:[.19],range:4.15,speed:0,damage:1.05,force:25,recover:1.18,motion:0}
  ],
  [
   {name:'毒糸・爆輪',kind:'sweep',shape:'circle',response:'dodge',wind:1.06,active:.52,hits:[.22],range:4.65,speed:0,damage:1.02,force:24,recover:1.24,motion:0},
   {name:'穿脚・二条レーン',kind:'rush',shape:'line',response:'dodge',wind:.90,active:.72,hits:[.16,.52],range:5.15,width:.88,speed:6.5,damage:.72,force:23,recover:1.30,motion:1}
  ],
  [
   {name:'崩塔・地割れ環',kind:'stomp',shape:'circle',response:'dodge',wind:1.22,active:.50,hits:[.20],range:4.85,speed:0,damage:1.12,force:34,recover:1.42,motion:2},
   {name:'鐘楼・不可止突進',kind:'rush',shape:'line',response:'dodge',wind:1.06,active:.68,hits:[.22,.52],range:5.45,width:1.18,speed:6.8,damage:.72,force:34,recover:1.48,motion:1}
  ]
 ];

 for(let i=0;i<ENEMY_MOVES.length;i++){
  for(const m of ENEMY_MOVES[i])if(!m.response)m.response='parry';
  for(const m of EXTRA_DODGE_MOVES[i])if(!ENEMY_MOVES[i].some(x=>x.name===m.name))ENEMY_MOVES[i].push(m);
 }

 // Do not leave the new mechanic to random selection. Every third enemy attack is a
 // cyan DODGE-only attack, alternating between the boss's two dodge signatures.
 const dodgeStartEnemyAttackBase=startEnemyAttack;
 startEnemyAttack=function(move){
  const extras=EXTRA_DODGE_MOVES[level]||[];
  if(testForcedMove){move=testForcedMove;testForcedMove=null;}
  else if(extras.length&&boss&&boss.sequence%3===2){
   move=extras[Math.floor(boss.sequence/3)%extras.length];
  }
  return dodgeStartEnemyAttackBase(move);
 };

 const style=document.createElement('style');
 style.textContent=`
 #dodge{width:96px;height:96px;background:radial-gradient(circle at 40% 28%,#245d72ee,#102d3ae8);border:2px solid ${CYAN};color:#bff4ff;box-shadow:inset 0 0 0 4px #071b2455,inset 0 1px #d9fbff8c,0 5px 20px #0006}
 #dodge.ready{box-shadow:0 0 20px #67ddff88,inset 0 0 0 4px #071b2455}
 #responseLegend{position:absolute;right:max(22px,env(safe-area-inset-right));top:116px;display:flex;gap:7px;pointer-events:none;font-weight:800;font-size:10px;letter-spacing:1.5px;text-shadow:0 2px 8px #000}
 #responseLegend span{padding:5px 8px;border:1px solid #ffffff22;background:#07101999;border-radius:4px}
 #responseLegend .parry{color:#ffd98e;border-color:#ffd98e55}#responseLegend .dodge{color:#8eeaff;border-color:#67ddff66}
 #dodgeCue{position:absolute;top:30%;left:0;right:0;text-align:center;pointer-events:none;font-size:clamp(20px,3.4vw,34px);font-weight:900;letter-spacing:6px;color:#8eeaff;text-shadow:0 0 18px #1ca7d4,0 3px 12px #000;opacity:0;transform:scale(.96);transition:opacity .08s,transform .08s}
 #dodgeCue.show{opacity:1;transform:scale(1)}
 @media(max-height:500px){.actions{gap:10px!important}.actions button{width:72px!important;height:72px!important}#dodge{width:84px!important;height:84px!important}#parry{width:90px!important;height:90px!important}#responseLegend{top:66px}}
 @media(max-width:550px) and (min-height:501px){#dodge{width:80px!important;height:80px!important}.actions{gap:6px!important}#responseLegend{top:126px;right:14px}}
 `;
 document.head.appendChild(style);

 const actions=document.querySelector('.actions');
 const dodgeButton=document.createElement('button');dodgeButton.id='dodge';dodgeButton.innerHTML='避ける<small>DODGE</small>';
 if(actions){const parryButton=$('parry');actions.insertBefore(dodgeButton,parryButton||null)}
 const legend=document.createElement('div');legend.id='responseLegend';legend.innerHTML='<span class="parry">◇ PARRY</span><span class="dodge">≫ DODGE</span>';document.body.appendChild(legend);
 const dodgeCue=document.createElement('div');dodgeCue.id='dodgeCue';dodgeCue.textContent='≫ 避 け ろ ≫';document.body.appendChild(dodgeCue);

 function requestDodge(){dodgeQueued=true;dodgeButton.classList.add('pressed')}
 dodgeButton.onpointerdown=e=>{e.preventDefault();dodgeButton.setPointerCapture(e.pointerId);requestDodge()};
 for(const event of ['pointerup','pointercancel','lostpointercapture'])dodgeButton.addEventListener(event,()=>dodgeButton.classList.remove('pressed'));
 addEventListener('keydown',e=>{if(!e.repeat&&(e.code==='KeyL'||e.code==='ShiftLeft'||e.code==='ShiftRight'))requestDodge()},true);
 addEventListener('keyup',e=>{if(e.code==='KeyL'||e.code==='ShiftLeft'||e.code==='ShiftRight')dodgeButton.classList.remove('pressed')},true);

 function startDodge(){
  if(mode!=='play'||!player||player.hp<=0||player.down>0||player.stun>0||dodgeCool>0)return false;
  let x=input.x+(keys.has('KeyD')||keys.has('ArrowRight')?1:0)-(keys.has('KeyA')||keys.has('ArrowLeft')?1:0);
  let z=input.z+(keys.has('KeyS')||keys.has('ArrowDown')?1:0)-(keys.has('KeyW')||keys.has('ArrowUp')?1:0);
  const mag=Math.hypot(x,z),forward=V(Math.sin(cameraRig.yaw),0,Math.cos(cameraRig.yaw)),right=V(-forward.z,0,forward.x);
  let dir;
  if(mag>.18)dir=norm(add(mul(right,x/mag),mul(forward,-z/mag)));
  else{
   const toBoss=norm(V(boss.pos.x-player.pos.x,0,boss.pos.z-player.pos.z)),tangent=V(toBoss.z,0,-toBoss.x);
   dir=mul(tangent,dodgeSide);dodgeSide*=-1;
  }
  player.swing=null;player.attack=0;player.parry=0;player.cool=Math.min(player.cool,.10);player.attackChain=0;player.attackChainTimer=0;player.comboWindow=0;
  attackBuffer=0;parryBuffer=0;player.vel.x=dir.x*8.8;player.vel.z=dir.z*8.8;player.dash=.38;
  // Long enough to cover a late visual read plus the first active hit, but still much
  // shorter than the cooldown so repeated mashing is not a permanent invulnerability.
  dodgeTimer=.38;dodgeIFrame=.34;dodgeCool=.62;
  ring(player.nodes[0].p,DODGE_SUCCESS);sound(920,.09,'triangle',.028);return true;
 }

 const dodgeEnemyImpactBase=enemyImpact;
 enemyImpact=function(move=null){
  if(move?.response==='dodge'){
   // enemyImpact is called only at a scheduled hit. If the dodge window is active,
   // leaving the hit geometry is itself a valid evade and still counts as DODGE.
   if(dodgeIFrame>0){
    dodges++;const perfect=dodgeIFrame>.16;if(perfect)perfectDodges++;
    player.invuln=Math.max(player.invuln,.06);ring(player.nodes[0].p,DODGE_SUCCESS);burst(player.nodes[0].p,DODGE_SUCCESS,18,5);sound(perfect?1420:1050,.11,'triangle',.035);announce(perfect?'PERFECT DODGE':'DODGE',.46);shake=Math.max(shake,.08);return;
   }
   // Cyan attacks are explicitly unparryable. PARRY cannot substitute for DODGE.
   const savedParry=player.parry;player.parry=0;
   const out=dodgeEnemyImpactBase(move);
   if(savedParry>0&&player.hp>0)player.parry=Math.min(savedParry,.08);
   return out;
  }
  return dodgeEnemyImpactBase(move);
 };

 const dodgeTelegraphBase=drawAttackTelegraph;
 drawAttackTelegraph=function(){
  const move=enemyMove();if(move?.response!=='dodge')return dodgeTelegraphBase();
  const timeToHit=(boss.wind>0?boss.wind:0)+(move.hits?.[0]??.18),ready=timeToHit<=.30,pulse=.72+.28*Math.sin(time*13),color=ready?`rgba(103,221,255,${.72+.20*pulse})`:`rgba(60,168,200,${.48+.18*pulse})`,origin=V(boss.pos.x,.045,boss.pos.z),forward=V(Math.sin(boss.aim),0,Math.cos(boss.aim)),right=V(Math.cos(boss.aim),0,-Math.sin(boss.aim));
  ctx.save();
  if(move.shape==='circle'){
   floorRing(origin,move.range,color,ready?3.2:2);floorRing(origin,Math.max(.35,move.range*.72),`rgba(103,221,255,${.22*pulse})`,1.2);
  }else{
   const points=move.shape==='line'?[add(origin,mul(right,-move.width)),add(add(origin,mul(forward,move.range)),mul(right,-move.width)),add(add(origin,mul(forward,move.range)),mul(right,move.width)),add(origin,mul(right,move.width))]:[origin,...Array.from({length:25},(_,i)=>add(origin,V(Math.sin(boss.aim-move.arc+i/24*move.arc*2)*move.range,0,Math.cos(boss.aim-move.arc+i/24*move.arc*2)*move.range)))];
   const ps=clipNear(points).map(project);if(ps.length>=3){ctx.beginPath();ps.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fillStyle=`rgba(33,175,218,${ready?.16:.08})`;ctx.fill();ctx.strokeStyle=color;ctx.lineWidth=ready?3:1.6;ctx.stroke()}
  }
  floorRing(origin,.65+Math.sin(time*12)*.08,color,2.2);ctx.restore();
 };

 const dodgeStepBase=step;
 step=function(dt){
  dodgeCool=Math.max(0,dodgeCool-dt);dodgeTimer=Math.max(0,dodgeTimer-dt);dodgeIFrame=Math.max(0,dodgeIFrame-dt);
  if(dodgeQueued){startDodge();dodgeQueued=false}
  const out=dodgeStepBase(dt);
  const move=mode==='play'&&boss?(boss.wind>0||boss.strike>0?enemyMove():null):null,isDodge=move?.response==='dodge';
  dodgeCue.classList.toggle('show',!!isDodge);dodgeButton.classList.toggle('ready',dodgeCool<=0);
  if(isDodge)dodgeCue.textContent=boss.wind>0?'≫ 避 け ろ ≫':'≫ DODGE ≫';
  return out;
 };

 if(dodgeTestMode){
  window.parryDodgeTest={
   catalog:()=>EXTRA_DODGE_MOVES.map(group=>group.map(m=>({name:m.name,response:m.response,kind:m.kind,shape:m.shape}))),
   placeAtCombatRange:()=>{
    if(mode!=='play'||!player||!boss)return false;
    const fromBoss=norm(V(player.pos.x-boss.pos.x,0,player.pos.z-boss.pos.z));
    const desired=add(boss.pos,mul(fromBoss,2.15)),delta=sub(desired,player.pos);
    player.pos=desired;player.vel=V();boss.vel=V();
    for(const n of player.nodes){n.p=add(n.p,delta);n.prev=add(n.prev,delta)}
    player.face=Math.atan2(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z);
    boss.face=Math.atan2(player.pos.x-boss.pos.x,player.pos.z-boss.pos.z);boss.aim=boss.face;
    return true;
   },
   forceAttack:(response,prime=false)=>{
    if(mode!=='play'||!boss||boss.hp<=0||boss.wind>0||boss.strike>0||boss.stun>0||boss.down>0)return false;
    const extras=EXTRA_DODGE_MOVES[level]||[],normals=(ENEMY_MOVES[level]||[]).filter(m=>m.response!=='dodge');
    const move=response==='dodge'?extras[0]:response==='parry'?(normals.find(m=>(m.hits?.length||0)===1)||normals[0]):null;
    if(!move)return false;
    testForcedMove=move;boss.ai=0;
    startEnemyAttack(move);
    // Diagnostic-only acceleration: preserve the production move/hit logic, but skip the
    // long headless render wait and begin just before the real response window.
    if(prime&&boss.wind>0)boss.wind=Math.min(boss.wind,response==='dodge'?.07:.16);
    return true;
   }
  };
 }

 if(window.parryDoll?.snapshot){
  const snapshotBase=window.parryDoll.snapshot;
  window.parryDoll.snapshot=()=>{const s=snapshotBase(),m=mode==='play'&&boss&&(boss.wind>0||boss.strike>0)?enemyMove():null;return {...s,dodges,perfectDodges,dodgeTimer:+dodgeTimer.toFixed(3),dodgeCool:+dodgeCool.toFixed(3),parryActive:+(player?.parry||0).toFixed(3),response:m?.response||'',enemyMove:m?.name||'',enemyKind:m?.kind||'',enemyShape:m?.shape||'',enemyHitIndex:boss?.hitIndex||0,enemyWind:+(boss?.wind||0).toFixed(3),enemyStrike:+(boss?.strike||0).toFixed(3)};};
 }
})();


// Combat safety v1: no one-shot failures + runaway/frame recovery.
(()=>{
 if(window.__parryCombatSafetyV1Loaded)return;window.__parryCombatSafetyV1Loaded=true;
 const MAX_PLAYER_HIT=28,PLAYER_HIT_IFRAME=.48,MAX_PARTICLES=220,MAX_RINGS=20,MAX_SHAPES=320;
 let frameRecoveries=0,consecutiveFrameErrors=0,lastHealthyFrame=performance.now();
 const lastGood=new WeakMap();
 const finite=n=>Number.isFinite(n);
 const copyV=v=>V(v?.x||0,v?.y||0,v?.z||0);
 function safeVec(v,maxMag=60){
  const q=V(finite(v?.x)?v.x:0,finite(v?.y)?v.y:0,finite(v?.z)?v.z:0),m=len(q);
  return m>maxMag?mul(q,maxMag/(m||1)):q;
 }
 function safePoint(p,fallback=V()){
  return V(finite(p?.x)?p.x:fallback.x,finite(p?.y)?p.y:fallback.y,finite(p?.z)?p.z:fallback.z);
 }
 function trimEffects(){
  if(particles.length>MAX_PARTICLES)particles.splice(0,particles.length-MAX_PARTICLES);
  if(rings.length>MAX_RINGS)rings.splice(0,rings.length-MAX_RINGS);
  if(shapes.length>MAX_SHAPES)shapes.splice(0,shapes.length-MAX_SHAPES);
 }
 function stabilize(d){
  if(!d)return;
  const fallback=lastGood.get(d)||V(d.player?0:0,0,d.player?3:-2);
  if(!finite(d.pos?.x)||!finite(d.pos?.y)||!finite(d.pos?.z))d.pos=copyV(fallback);
  else lastGood.set(d,copyV(d.pos));
  d.vel=safeVec(d.vel,45);
  for(const k of ['hp','invuln','stun','down','attack','parry','cool','parryCool','comboWindow','attackChainTimer','counter','broken','dash','wind','strike','ai','posture']){
   if(k in d&&!finite(d[k]))d[k]=0;
  }
  if(Array.isArray(d.nodes))for(const n of d.nodes){
   const base=add(d.pos,n.rest||V());
   if(n.p)n.p=safePoint(n.p,base);
   if(n.prev)n.prev=safePoint(n.prev,n.p||base);
  }
 }

 const hurtSafetyBase=hurt;
 hurt=function(d,amount,force,point){
  let a=finite(amount)?Math.max(0,amount):0;
  let f=safeVec(force,d?.player?38:72);
  const p=safePoint(point,d?.nodes?.[1]?.p||d?.pos||V());
  if(d?.player){
   a=Math.min(a,MAX_PLAYER_HIT);
   // A single failed PARRY/DODGE can never take the player from alive to dead.
   // At 1 HP the next genuine hit may still defeat the player, so mistakes matter.
   if(d.hp>1&&a>=d.hp)a=Math.max(1,d.hp-1);
  }
  const out=hurtSafetyBase(d,a,f,p);
  if(out&&d?.player){
   d.invuln=Math.max(d.invuln,PLAYER_HIT_IFRAME);
   d.stun=Math.min(d.stun,.95);
  }
  return out;
 };

 const burstSafetyBase=burst;
 burst=function(p,color,count=24,power=6){
  const c=Math.min(48,Math.max(0,finite(count)?Math.floor(count):24));
  const pw=Math.min(10,Math.max(0,finite(power)?power:6));
  const out=burstSafetyBase(safePoint(p),color,c,pw);trimEffects();return out;
 };
 const ringSafetyBase=ring;
 ring=function(p,color){const out=ringSafetyBase(safePoint(p),color);trimEffects();return out;};
 const groundSafetyBase=groundImpact;
 groundImpact=function(p,power){return groundSafetyBase(safePoint(p),Math.min(3.2,Math.max(0,finite(power)?power:1)));};

 const stepSafetyBase=step;
 step=function(dt){
  const safeDt=finite(dt)&&dt>0?Math.min(dt,1/30):1/60;
  const out=stepSafetyBase(safeDt);
  stabilize(player);stabilize(boss);trimEffects();
  hitstop=finite(hitstop)?Math.min(Math.max(0,hitstop),.14):0;
  shake=finite(shake)?Math.min(Math.max(0,shake),.85):0;
  if(typeof feel==='object'&&feel){
   if(!finite(feel.slow))feel.slow=0;else feel.slow=Math.min(Math.max(0,feel.slow),.65);
  }
  return out;
 };

 // Catch any frame-time exception from later visual/combat layers. The core game keeps
 // scheduling frames instead of dying on one bad effect, invalid projection, or overload.
 const frameSafetyBase=frame;
 frame=function(now){
  try{
   const out=frameSafetyBase(now);
   consecutiveFrameErrors=0;lastHealthyFrame=performance.now();
   return out;
  }catch(err){
   frameRecoveries++;consecutiveFrameErrors++;
   console.error('[combat-safety] recovered frame',err);
   acc=0;hitstop=0;trimEffects();stabilize(player);stabilize(boss);
   if(typeof feel==='object'&&feel&&consecutiveFrameErrors>=2)feel.reduced=true;
   last=finite(now)?now:performance.now();lastHealthyFrame=performance.now();
   requestAnimationFrame(frame);
  }
 };

 // Backup watchdog for the rare case where an exception happened in an already queued
 // pre-safety frame before the wrapper became active.
 setInterval(()=>{
  if(document.hidden||mode==='paused'||mode==='title')return;
  const now=performance.now();
  if(now-lastHealthyFrame<1800)return;
  frameRecoveries++;acc=0;hitstop=0;trimEffects();stabilize(player);stabilize(boss);
  if(typeof feel==='object'&&feel)feel.reduced=true;
  last=now;lastHealthyFrame=now;requestAnimationFrame(frame);
 },900);

 const safetyTestMode=new URLSearchParams(location.search).has('safetycheck');
 if(safetyTestMode){
  window.parrySafetyTest={
   takeHit:(amount=999)=>{
    if(mode!=='play'||!player)return false;
    player.invuln=0;return hurt(player,amount,V(80,40,80),player.nodes?.[1]?.p||player.pos);
   },
   stress:(loops=120)=>{
    if(mode!=='play'||!player)return false;
    for(let i=0;i<Math.min(400,Math.max(1,loops|0));i++){
     burst(player.pos,i%2?'#67ddff':'#ffd98e',120,30);ring(player.pos,'#ffffff');
    }
    trimEffects();return true;
   },
   corruptVelocity:()=>{if(!player)return false;player.vel=V(Infinity,NaN,-Infinity);return true;},
   stats:()=>({frameRecoveries,particles:particles.length,rings:rings.length,shapes:shapes.length})
  };
 }

 if(window.parryDoll?.snapshot){
  const safetySnapshotBase=window.parryDoll.snapshot;
  window.parryDoll.snapshot=()=>({...safetySnapshotBase(),safety:{frameRecoveries,particles:particles.length,rings:rings.length,shapes:shapes.length}});
 }
})();
