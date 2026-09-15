from pathlib import Path

path = Path('dist/dodge-system-v1.js')
text = path.read_text(encoding='utf-8')
marker = '// Combat safety v1: no one-shot failures + runaway/frame recovery.'
if marker in text:
    print('combat safety v1 already present')
    raise SystemExit(0)

safety = r'''

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
'''

path.write_text(text + safety, encoding='utf-8')
print('appended combat safety v1')
