'use strict';
// PHASE BREAK v1 — additive boss-phase layer. Keeps core combat/input physics intact.
(()=>{
 if(window.__parryPhaseBreakLoaded)return;window.__parryPhaseBreakLoaded=true;

 const PHASES=[
  ['正統剣術','抜刀暴走','灰の剣鬼'],
  ['狩りの間合い','骨鎖解放','飢餓暴走'],
  ['脚槍陣','天蓋遊猟','断糸狂舞'],
  ['鐘守','崩鐘','天を砕く者'],
  ['模倣','学習','鏡殺']
 ];
 const PHASE_SUB=[
  ['ORTHODOX BLADE','DRAWN FURY','ASH DEMON'],
  ['HUNT','BONE UNBOUND','STARVING BEAST'],
  ['SPEAR LEGS','CANOPY HUNT','THREADLESS FRENZY'],
  ['BELL WARDEN','BROKEN BELL','SKY BREAKER'],
  ['IMITATE','LEARN','MIRROR KILL']
 ];
 const PHASE_COLORS=['#d8b26f','#f08c5b','#ffcf70'];
 const pb={bossRef:null,phase:1,chain:0,chainT:0,lastParryAt:-9,resolve:0,danger:null,transitionT:0,secretSpawned:false,secretWon:false,baseSpeed:0,baseDamage:0,parryAttempts:0,attacks:0};

 if(bosses.length<5){
  bosses.push({name:'傀儡零式',sub:'THE PARRY DOLL',type:'human',scale:1.02,hp:240,color:'#d6d4cf',speed:2.75,damage:16,wind:.82,attackName:'鏡返し'});
 }
 if(ENEMY_MOVES.length<5){
  ENEMY_MOVES.push([
   {name:'鏡写し・三段',kind:'combo',shape:'cone',wind:.78,active:.92,hits:[.12,.42,.72],range:3.55,arc:1.75,speed:1.65,damage:.72,force:18,recover:.88,motion:0},
   {name:'写身突き',kind:'thrust',shape:'line',wind:.86,active:.30,hits:[.14],range:4.65,width:.62,speed:4.8,damage:1.15,force:24,recover:.92,motion:1},
   {name:'逆写し・横薙ぎ',kind:'sidestep',shape:'cone',wind:.82,active:.38,hits:[.15],range:3.65,arc:2.35,speed:2.35,damage:1.0,force:22,recover:.86,motion:1},
   {name:'断絶・鏡落とし',kind:'slam',shape:'cone',wind:1.08,active:.42,hits:[.17],range:3.45,arc:1.05,speed:1.0,damage:1.45,force:30,recover:1.15,motion:2}
  ]);
 }

 function ensureUI(){
  if(document.getElementById('pbPhaseStrip'))return;
  const style=document.createElement('style');
  style.textContent=`
   #pbPhaseStrip{position:absolute;top:47px;left:28%;width:44%;max-width:650px;text-align:center;pointer-events:none;font-size:9px;letter-spacing:2.2px;color:#d8c59d;text-shadow:0 2px 8px #000;opacity:.92}
   #pbPhaseStrip b{font-size:11px;color:#ffe0a3;font-weight:700;margin-left:7px}
   #pbDanger{position:absolute;left:50%;top:22%;transform:translateX(-50%) scale(.96);min-width:190px;text-align:center;pointer-events:none;padding:6px 12px;border:1px solid #d7b36d55;background:linear-gradient(90deg,#07101800,#071018d8 18%,#071018d8 82%,#07101800);font-size:11px;letter-spacing:2px;color:#ffe0a2;opacity:0;transition:opacity .08s,transform .08s;text-shadow:0 2px 9px #000}
   #pbDanger.show{opacity:1;transform:translateX(-50%) scale(1)}#pbDanger strong{color:#fff1c9;margin-right:6px}
   #pbChain{position:absolute;left:max(25px,env(safe-area-inset-left));bottom:243px;pointer-events:none;font-size:11px;letter-spacing:2px;color:#ffe3a4;text-shadow:0 2px 9px #000;opacity:0;transform:translateY(4px);transition:opacity .1s,transform .1s}#pbChain.show{opacity:1;transform:none}
   #pbResolve{position:absolute;left:max(25px,env(safe-area-inset-left));bottom:220px;width:155px;pointer-events:none}#pbResolve label{display:flex;justify-content:space-between;font-size:8px;letter-spacing:1.7px;color:#9ebeb8;margin-bottom:3px}#pbResolve .track{height:3px;background:#071017c9}.track i{display:block;width:0;height:100%;background:linear-gradient(90deg,#6bc9c3,#f4d289);box-shadow:0 0 8px #9de0cb77;transition:width .15s}
   #pbBanner{position:absolute;left:0;right:0;top:34%;text-align:center;pointer-events:none;opacity:0;transform:scale(.88);transition:opacity .14s,transform .14s;text-shadow:0 3px 18px #000}#pbBanner.show{opacity:1;transform:scale(1)}#pbBanner small{display:block;font-size:10px;letter-spacing:5px;color:#e5c382}#pbBanner b{display:block;margin-top:5px;font-size:26px;letter-spacing:8px;color:#fff0c7}
   @media(max-height:500px){#pbPhaseStrip{top:8px;left:28%;width:44%}#pbDanger{top:24%}#pbChain{bottom:195px}#pbResolve{bottom:174px}}
  `;
  document.head.appendChild(style);
  const phase=document.createElement('div');phase.id='pbPhaseStrip';
  const danger=document.createElement('div');danger.id='pbDanger';
  const chain=document.createElement('div');chain.id='pbChain';
  const resolve=document.createElement('div');resolve.id='pbResolve';resolve.innerHTML='<label><span>RESOLVE</span><span id="pbResolveText">0%</span></label><div class="track"><i id="pbResolveBar"></i></div>';
  const banner=document.createElement('div');banner.id='pbBanner';banner.innerHTML='<small>PHASE BREAK</small><b></b>';
  const bossHud=$('bossHud');bossHud.parentNode.insertBefore(phase,bossHud);
  const playerHud=$('playerHud');playerHud.parentNode.insertBefore(chain,playerHud);playerHud.parentNode.insertBefore(resolve,playerHud);
  const cue=$('cue');cue.parentNode.insertBefore(danger,cue);cue.parentNode.insertBefore(banner,cue);
  $('eyebrow').textContent='PHASE BREAK • THREE-STAGE BOSS DUELS';
 }
 ensureUI();

 function phaseFor(d=boss){if(!d?.spec?.hp)return 1;const r=d.hp/d.spec.hp;return r<=.25?3:r<=.60?2:1}
 function phaseName(p=pb.phase){return PHASES[level]?.[p-1]||`PHASE ${p}`}
 function phaseSub(p=pb.phase){return PHASE_SUB[level]?.[p-1]||''}
 function cloneBossSpec(){
  if(!boss||boss.__pbSpecCloned)return;
  boss.spec={...boss.spec};boss.__pbSpecCloned=true;pb.baseSpeed=boss.spec.speed;pb.baseDamage=boss.spec.damage;
 }
 function tuneBoss(){
  if(!boss)return;cloneBossSpec();const p=pb.phase;
  const speed=[1,1.07,1.15][p-1]*(level===1?1.025:level===4?1.05:1);
  const damage=[1,1.045,1.09][p-1]*(level===4?1.04:1);
  boss.spec.speed=pb.baseSpeed*speed;boss.spec.damage=pb.baseDamage*damage;
  if(p>=2)boss.enraged=true;
 }
 function initBoss(force=false){
  if(!boss)return;if(!force&&pb.bossRef===boss)return;
  pb.bossRef=boss;pb.phase=phaseFor();pb.chain=0;pb.chainT=0;pb.danger=null;pb.transitionT=0;pb.baseSpeed=boss.spec.speed;pb.baseDamage=boss.spec.damage;
  cloneBossSpec();tuneBoss();updatePhaseUI();
 }
 function updatePhaseUI(){
  const strip=$('pbPhaseStrip');if(strip)strip.innerHTML=`PHASE 0${pb.phase}<b>${phaseName()}</b><span style="opacity:.62;margin-left:7px">${phaseSub()}</span>`;
  const bar=$('pbResolveBar'),txt=$('pbResolveText');if(bar)bar.style.width=clamp(pb.resolve,0,100)+'%';if(txt)txt.textContent=pb.resolve>=100?'READY':Math.round(pb.resolve)+'%';
  if(level===4){$('phase').textContent='SECRET';$('round').textContent='THE PARRY DOLL'}else $('phase').textContent=`PHASE 0${pb.phase}`;
 }
 function showBanner(text,sub='PHASE BREAK',duration=1.15){
  const el=$('pbBanner');if(!el)return;el.querySelector('small').textContent=sub;el.querySelector('b').textContent=text;el.classList.add('show');pb.transitionT=Math.max(pb.transitionT,duration);
 }
 function doPhaseBreak(next){
  pb.phase=next;tuneBoss();boss.wind=0;boss.strike=0;boss.pattern=null;boss.stun=Math.max(boss.stun,next===3?1.22:1.02);boss.ai=Math.max(boss.ai,.85);
  const p=boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1]?.p||boss.pos;
  ring(V(boss.pos.x,.05,boss.pos.z),PHASE_COLORS[next-1]);ring(V(boss.pos.x,.05,boss.pos.z),'#fff0bd');burst(p,PHASE_COLORS[next-1],next===3?38:26,next===3?8:6);
  impact(p,'break',next===3?2.1:1.65);shake=Math.max(shake,next===3?.36:.26);hitstop=Math.max(hitstop,next===3?.09:.06);feel.flash=Math.max(feel.flash,next===3?.15:.09);feel.slow=Math.max(feel.slow,next===3?.24:.14);
  $('pbDanger')?.classList.remove('show');if($('attackHud'))$('attackHud').textContent='';showBanner(phaseName(next),next===3?'FINAL PHASE':'PHASE BREAK',next===3?1.35:1.05);combatSound('break');updatePhaseUI();
 }

 function classify(move){
  if(!move)return null;
  if(move.kind==='combo')return {type:'chain',label:'連 続 弾 き',hint:`${move.hits?.length||2}連撃`};
  if(move.kind==='thrust'||move.kind==='rush')return {type:'thrust',label:'突 き',hint:'前へ踏み込み弾き'};
  if(move.kind==='sweep'||move.kind==='sidestep')return {type:'sweep',label:'薙 ぎ',hint:'横へ回り込め'};
  if(['slam','stomp','leap'].includes(move.kind))return {type:'crush',label:'破 壊 攻 撃',hint:'斬って潰せ'};
  return {type:'normal',label:'攻 撃',hint:'見切れ'};
 }
 function phaseMove(move){
  const m={...move,hits:[...(move.hits||[])]},p=pb.phase;
  if(p===2){m.wind*=.96;m.recover*=.91;m.speed*=1.06}
  if(p===3){m.wind*=.90;m.recover*=.82;m.speed*=1.12}
  if(p===3){
   if(level===0&&m.kind==='combo'){m.active=1.02;m.hits=[.10,.34,.58,.82]}
   else if(level===1&&m.kind==='rush'){m.active=.82;m.hits=[.13,.39,.66]}
   else if(level===2&&m.kind==='combo'){m.active=1.22;m.hits=[.10,.34,.58,.82,1.06]}
   else if(level===3&&m.kind==='sweep'){m.active=.72;m.hits=[.16,.48]}
   else if(level===4&&m.kind==='combo'){m.active=1.20;m.hits=[.09,.32,.55,.78,1.02]}
  }
  return m;
 }

 const pbStartEnemyAttack=startEnemyAttack;
 startEnemyAttack=function(move){
  initBoss();const tuned=phaseMove(move);pb.danger=classify(tuned);return pbStartEnemyAttack(tuned);
 };

 const pbPlayerParry=playerParry;
 playerParry=function(){const ok=pbPlayerParry();if(ok)pb.parryAttempts++;return ok};
 const pbPlayerAttack=playerAttack;
 playerAttack=function(){const ok=pbPlayerAttack();if(ok)pb.attacks++;return ok};

 const pbEnemyImpact=enemyImpact;
 enemyImpact=function(move=null){
  const before=parries,beforePerfect=perfects,wasPerfect=player.parry>.22,now=time;const danger=pb.danger||classify(move);
  const out=pbEnemyImpact(move);
  if(parries>before){
   pb.chain=now-pb.lastParryAt<.88?pb.chain+1:1;pb.lastParryAt=now;pb.chainT=.85;
   const perfect=perfects>beforePerfect||wasPerfect;pb.resolve=Math.min(100,pb.resolve+(perfect?18:12)+Math.min(8,pb.chain*2));
   if(pb.chain>=2){boss.posture=Math.min(115,boss.posture+Math.min(8,pb.chain*1.35));const el=$('pbChain');el.textContent=`DEFLECT × ${pb.chain}`;el.classList.add('show')}
   if(danger?.type==='thrust'){
    const toBoss=norm(sub(boss.pos,player.pos)),toward=player.vel.x*toBoss.x+player.vel.z*toBoss.z;
    if(toward>.35){boss.posture=Math.min(115,boss.posture+10);announce('見 切 り 弾 き',.55);pb.resolve=Math.min(100,pb.resolve+8)}
   }
   updatePhaseUI();
  }
  return out;
 };

 const pbResolveSwing=resolveSwing;
 resolveSwing=function(){
  const swing=player.swing?{...player.swing}:null,crush=boss?.wind>0&&(pb.danger||classify(enemyMove()))?.type==='crush',hp=boss?.hp||0,posture=boss?.posture||0;
  const out=pbResolveSwing();
  const landed=boss&&boss.hp<hp;
  if(landed){
   if(swing?.counter)pb.resolve=Math.min(100,pb.resolve+12);
   else pb.resolve=Math.min(100,pb.resolve+(swing?.combo===2?7:3));
   if(crush&&boss.hp>0){boss.wind=0;boss.strike=0;boss.pattern=null;boss.stun=Math.max(boss.stun,.72);boss.ai=Math.max(boss.ai,1);boss.posture=Math.min(115,Math.max(posture,boss.posture)+20);ring(boss.nodes[1].p,'#ffdc87');announce('破 壊 阻 止',.65);impact(boss.nodes[1].p,'break',1.45);shake=Math.max(shake,.22);hitstop=Math.max(hitstop,.065);pb.resolve=Math.min(100,pb.resolve+14)}
   updatePhaseUI();
  }
  return out;
 };

 function spawnSecret(){
  if(pb.secretSpawned)return;pb.secretSpawned=true;try{localStorage.setItem('parry-doll-secret-unlocked','1')}catch(_){};
  $('overlay').classList.add('hidden');mode='play';level=4;transition=0;const health=Math.min(100,player.hp+45);boss=new Doll(bosses[4]);
  const shift=sub(V(0,0,3),player.pos);player.pos=V(0,0,3);player.vel=V();for(const n of player.nodes){n.p=add(n.p,shift);n.prev={...n.p}}
  player.swing=null;player.attack=0;player.cool=0;player.counter=0;player.hp=health;player.invuln=1.2;cameraRig.initialized=false;initBoss(true);updateHUD();updatePhaseUI();
  $('pbDanger')?.classList.remove('show');if($('attackHud'))$('attackHud').textContent='';showBanner('傀 儡 零 式','SECRET DUEL',1.75);announce('THE PARRY DOLL',1.2);sound(95,.6,'sawtooth',.08);feel.slow=.35;
 }

 const pbReset=reset;
 reset=function(l=0){const out=pbReset(l);pb.bossRef=null;pb.phase=1;pb.chain=0;pb.chainT=0;pb.lastParryAt=-9;pb.danger=null;pb.transitionT=0;if(l===0){pb.resolve=0;pb.secretSpawned=false;pb.secretWon=false}initBoss(true);return out};

 const pbStep=step;
 step=function(dt){
  const beforeBoss=boss;pbStep(dt);
  if(boss&&boss!==beforeBoss)initBoss(true);else initBoss();
  if(mode==='play'&&boss?.hp>0){const next=phaseFor();if(next>pb.phase)doPhaseBreak(next)}
  if(mode==='won'&&level===3&&!pb.secretSpawned)spawnSecret();
  else if(mode==='won'&&level===4&&!pb.secretWon){pb.secretWon=true;showOverlay('鏡 像 討 伐',`THE PARRY DOLLを撃破。PARRY ${parries}回 / PERFECT ${perfects}回 / ${Math.floor(elapsed)}秒`,'もう一度挑む')}
  pb.chainT=Math.max(0,pb.chainT-dt);if(pb.chainT<=0){pb.chain=0;$('pbChain')?.classList.remove('show')}
  pb.transitionT=Math.max(0,pb.transitionT-dt);if(pb.transitionT<=0)$('pbBanner')?.classList.remove('show');
  const danger=$('pbDanger');
  if(danger){if(mode==='play'&&boss?.wind>0&&pb.transitionT<=0){const d=pb.danger||classify(enemyMove());danger.innerHTML=`<strong>${d?.label||'攻 撃'}</strong>${d?.hint||''}`;danger.classList.add('show')}else danger.classList.remove('show')}
  updatePhaseUI();
 };

 const pbAnnounce=announce;
 announce=function(text,duration){if(typeof text==='string'&&text.startsWith('覚 醒 —'))return;return pbAnnounce(text,duration)};

 initBoss(true);updatePhaseUI();
 window.parryPhaseBreakDiagnostics=()=>({level,phase:pb.phase,phaseName:phaseName(),chain:pb.chain,resolve:+pb.resolve.toFixed(1),danger:pb.danger?.type||null,secretSpawned:pb.secretSpawned,secretWon:pb.secretWon,boss:boss?.spec?.name,hp:boss?.hp,ratio:boss?.spec?.hp?+(boss.hp/boss.spec.hp).toFixed(3):0,speed:+(boss?.spec?.speed||0).toFixed(3),damage:+(boss?.spec?.damage||0).toFixed(3)});
})();
