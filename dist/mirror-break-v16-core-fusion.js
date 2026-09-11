'use strict';
// MIRROR BREAK v16 — CORE FUSION: mixed DOLL CORE builds become real combat rules and copied final-boss attacks.
(()=>{
 if(window.__parryMirrorBreakV16Loaded)return;window.__parryMirrorBreakV16Loaded=true;
 const state=window.__mirrorBreakState,v3=window.__mirrorBreakV3State,v6=window.__mirrorBreakV6State;if(!state||!v3||!v6)return;
 const DEF={
  REFLECT_EDGE:{name:'REFLECT EDGE',jp:'鏡刃連斬',color:'#e9dd9a',rule:'PERFECT → 次の反撃命中後に鏡写しの追撃。'},
  RUPTURE_DRIVE:{name:'RUPTURE DRIVE',jp:'崩震駆動',color:'#f0c884',rule:'PERFECT → 次の反撃が強制吹き飛ばし。RUIN ROUTE向け。'},
  RESONANT_MIRROR:{name:'RESONANT MIRROR',jp:'共鳴鏡',color:'#a9f4ee',rule:'連続パリィ → 姿勢とRESOLVEへ共鳴衝撃。'},
  ZERO_TRACE:{name:'ZERO TRACE',jp:'零式共鳴',color:'#fff0b0',rule:'3核融合。PERFECTで蓄積し、反撃で全系統を同期。'}
 };
 const s={armed:null,armT:0,procT:0,lastProc:'',reflectHits:0,reflectEchoes:0,ruptureHits:0,resonantProcs:0,zeroProcs:0,armedAttacks:0,resonantCool:0,choicePasses:0,finalBoss:null,finalCalls:0,finalFusionAttacks:0,lastFinalFusion:null};
 window.__mirrorBreakV16State=s;
 function fusion(c=state.cores){
  const e=c?.EDGE||0,m=c?.MIRROR||0,p=c?.PULSE||0;
  if(e>0&&m>0&&p>0)return{id:'ZERO_TRACE',lv:Math.min(e,m,p),...DEF.ZERO_TRACE};
  if(e>0&&m>0)return{id:'REFLECT_EDGE',lv:Math.min(e,m),...DEF.REFLECT_EDGE};
  if(e>0&&p>0)return{id:'RUPTURE_DRIVE',lv:Math.min(e,p),...DEF.RUPTURE_DRIVE};
  if(m>0&&p>0)return{id:'RESONANT_MIRROR',lv:Math.min(m,p),...DEF.RESONANT_MIRROR};
  return null;
 }
 const style=document.createElement('style');style.textContent=`
 #mbSynergyHud{display:none;margin-top:4px;padding-top:4px;border-top:1px solid #b8c8c020;line-height:1.25;text-align:right;text-shadow:0 2px 8px #000}#mbSynergyHud.show{display:block}#mbSynergyHud b{display:block;margin:0;color:#e9dd9a;font-size:8px;letter-spacing:1.8px}#mbSynergyHud small{display:block;margin-top:2px;color:#95aaa5;font-size:6.5px;letter-spacing:1px}#mbSynergyHud em{display:block;margin-top:1px;color:#c8dbd6;font-size:6.5px;font-style:normal;letter-spacing:1.2px}#mbSynergyHud.hot em{color:#ffe4a2;text-shadow:0 0 8px #f2cd7988}
 #mbSynergyProc{min-height:9px;margin-top:3px;font-size:7px;font-weight:800;letter-spacing:1.7px;opacity:0;transform:translateX(4px);transition:opacity .08s,transform .08s;text-shadow:0 0 9px currentColor,0 2px 7px #000}#mbSynergyProc.show{opacity:.95;transform:none}
 body.mb-final-duel #mbSynergyHud,body.mb-final-duel #mbSynergyProc,body.mb-ruin-finisher #mbSynergyHud,body.mb-ruin-finisher #mbSynergyProc,body.mb-chain-destruction #mbSynergyHud,body.mb-chain-destruction #mbSynergyProc{display:none!important;opacity:0!important;visibility:hidden!important}
 #mbCoreChoice .mb-fusion-preview{display:block;margin-top:7px;padding-top:6px;border-top:1px solid #c6d4cc18;color:#80928e;font-size:7px;letter-spacing:1.2px}#mbCoreChoice .mb-fusion-preview.unlock{color:#f0d28d}#mbCoreChoice .mb-fusion-current{margin-top:8px;text-align:center;color:#8fa5a0;font-size:8px;letter-spacing:1.8px}#mbCoreChoice .mb-fusion-current b{color:#f0d28d}
 @media(max-height:500px){#mbSynergyHud{margin-top:2px;padding-top:2px}#mbSynergyHud b{font-size:7px}#mbSynergyHud small,#mbSynergyHud em,#mbSynergyProc{font-size:6px}#mbCoreChoice .mb-fusion-preview{margin-top:4px;padding-top:4px;font-size:6.5px}#mbCoreChoice .mb-fusion-current{margin-top:5px;font-size:7px}}
 `;document.head.appendChild(style);
 function ensureHud(){
  const host=document.getElementById('mbCores');if(!host)return null;let hud=document.getElementById('mbSynergyHud');if(!hud){hud=document.createElement('div');hud.id='mbSynergyHud';hud.innerHTML='<b></b><small></small><em></em>';host.appendChild(hud)}let proc=document.getElementById('mbSynergyProc');if(!proc){proc=document.createElement('div');proc.id='mbSynergyProc';host.appendChild(proc)}return{hud,proc};
 }
 function showProc(text,color='#f0d28d'){s.lastProc=text;s.procT=.62;const ui=ensureHud();if(ui){ui.proc.textContent=text;ui.proc.style.color=color;ui.proc.classList.add('show')}}
 function syncHud(){
  const ui=ensureHud();if(!ui)return;const f=fusion();if(!f){ui.hud.classList.remove('show','hot');ui.hud.querySelector('b').textContent='';ui.hud.querySelector('small').textContent='';ui.hud.querySelector('em').textContent='';ui.proc.classList.toggle('show',s.procT>0&&!!s.lastProc);return}
  ui.hud.classList.add('show');ui.hud.querySelector('b').textContent=`${f.name} ${f.lv}`;ui.hud.querySelector('b').style.color=f.color;ui.hud.querySelector('small').textContent=f.jp;
  let status=f.rule;if(f.id==='REFLECT_EDGE'&&s.armT>0&&s.armed===f.id)status='COUNTER ECHO READY';else if(f.id==='RUPTURE_DRIVE'&&s.armT>0&&s.armed===f.id)status='RUIN LAUNCH READY';else if(f.id==='RESONANT_MIRROR'&&v6.mirrorChainT>0)status='CHAIN PULSE READY';else if(f.id==='ZERO_TRACE')status=`ZERO TRACE ${v3.zeroCharges>0?`READY ×${v3.zeroCharges}`:`SYNC ${f.lv}`}`;
  ui.hud.querySelector('em').textContent=status;ui.hud.classList.toggle('hot',(s.armT>0&&!!s.armed)||(f.id==='RESONANT_MIRROR'&&v6.mirrorChainT>0)||(f.id==='ZERO_TRACE'&&v3.zeroCharges>0));
  ui.proc.classList.toggle('show',s.procT>0&&!!s.lastProc);if(s.procT<=0){ui.proc.textContent='';ui.proc.classList.remove('show')}
 }
 function enhanceChoice(){
  if(!state.choice)return;const chooser=document.getElementById('mbCoreChoice'),grid=chooser?.querySelector('.mb-core-grid');if(!grid||grid.children.length!==3)return;const keys=['EDGE','MIRROR','PULSE'],cur=fusion();[...grid.children].forEach((b,i)=>{let el=b.querySelector('.mb-fusion-preview');if(!el){el=document.createElement('span');el.className='mb-fusion-preview';b.appendChild(el)}const next={...state.cores};next[keys[i]]=(next[keys[i]]||0)+1;const f=fusion(next),unlock=!!f&&(!cur||f.id!==cur.id);el.classList.toggle('unlock',unlock);el.textContent=f?(unlock?`UNLOCK · ${f.name}`:`AMPLIFY · ${f.name} ${f.lv}`):'PURE CORE · NO FUSION'});const panel=chooser.querySelector('.mb-panel');let now=panel?.querySelector('.mb-fusion-current');if(panel&&!now){now=document.createElement('div');now.className='mb-fusion-current';panel.appendChild(now)}if(now){const f=fusion();now.innerHTML=f?`ACTIVE FUSION&nbsp; <b>${f.name} ${f.lv}</b>`:'MIX TWO CORE TYPES TO UNLOCK FUSION'}s.choicePasses++;
 }
 function arm(f,point){if(!f||f.id==='RESONANT_MIRROR'||f.id==='ZERO_TRACE')return;s.armed=f.id;s.armT=1.34+.12*f.lv;if(point){ring(point,f.color);burst(point,f.color,4+f.lv,2.5+.2*f.lv)}showProc(`${f.name} READY`,f.color)}
 function resonantPulse(f){if(!boss||boss.hp<=0||s.resonantCool>0)return;const p=boss.nodes?.find(n=>n.name==='chest')?.p||boss.nodes?.[1]?.p||boss.pos;boss.posture=Math.min(115,(boss.posture||0)+8+3*f.lv);boss.stun=Math.max(boss.stun||0,.10+.035*f.lv);player.counter=Math.max(player.counter||0,.25+.04*f.lv);if(window.__phaseBreakV2State)window.__phaseBreakV2State.resolve=Math.min(100,(window.__phaseBreakV2State.resolve||0)+5+2*f.lv);ring(p,f.color);ring(V(boss.pos.x,.06,boss.pos.z),'#bfffe9');burst(p,f.color,7+f.lv*2,3.1+.25*f.lv);shake=Math.max(shake,.09+.02*f.lv);hitstop=Math.max(hitstop,.035+.006*f.lv);sound(410,.08,'triangle',.015);s.resonantProcs++;s.resonantCool=.16;showProc('RESONANT MIRROR · PULSE',f.color)}
 const baseEnemyImpact=enemyImpact;enemyImpact=function(move=null){
  const bp=parries,bpf=perfects,preChain=v6.mirrorChainT||0,bz=v3.zeroCharges||0,out=baseEnemyImpact(move),didParry=parries>bp,didPerfect=perfects>bpf,f=fusion(),point=player?.nodes?.find(n=>n.name==='hand')?.p||player?.nodes?.[1]?.p;
  if(didPerfect&&f){if(f.id==='REFLECT_EDGE'||f.id==='RUPTURE_DRIVE')arm(f,point);else if(f.id==='ZERO_TRACE'&&(v3.zeroCharges||0)>bz)showProc('ZERO TRACE · CHARGED',f.color)}
  if(didParry&&f?.id==='RESONANT_MIRROR'&&preChain>0)resonantPulse(f);return out;
 };
 const basePlayerAttack=playerAttack;playerAttack=function(){
  const f=fusion(),use=!!(f&&s.armT>0&&s.armed===f.id&&player?.counter>0),ok=basePlayerAttack();if(ok&&use&&player.swing){player.swing.__mbFusion=f.id;player.swing.__mbFusionLv=f.lv;if(f.id==='REFLECT_EDGE'){player.swing.damage+=.75*f.lv;const to=boss&&player?norm(sub(boss.pos,player.pos)):V();player.vel=add(player.vel,mul(to,.65+.18*f.lv))}else if(f.id==='RUPTURE_DRIVE'){player.swing.damage+=1.15*f.lv;player.swing.force+=8+3.2*f.lv;const to=boss&&player?norm(sub(boss.pos,player.pos)):V();player.vel=add(player.vel,mul(to,1.0+.28*f.lv))}s.armedAttacks++;s.armT=0;s.armed=null;showProc(f.name,f.color)}return ok;
 };
 function delayedReflect(ref,lv,color){setTimeout(()=>{if(boss!==ref||!ref||ref.hp<=0||mode!=='play')return;const p=ref.nodes?.find(n=>n.name==='chest')?.p||ref.nodes?.[1]?.p||ref.pos,dir=player&&ref?norm(sub(ref.pos,player.pos)):V(0,0,1),inv=ref.invuln;ref.invuln=0;try{hurt(ref,1.6+1.05*lv,mul(dir,4.2+lv),p)}finally{ref.invuln=Math.max(ref.invuln,inv,.035)}ref.posture=Math.min(115,(ref.posture||0)+4+2*lv);ring(p,color);burst(p,color,5+lv*2,2.8+.2*lv);sound(720,.06,'triangle',.012);s.reflectEchoes++;showProc('REFLECT EDGE · ECHO',color)},82)}
 const baseResolveSwing=resolveSwing;resolveSwing=function(){
  const move=player.swing?{...player.swing}:null,before=boss?.hp||0,bz=v3.zeroCharges||0,ref=boss,out=baseResolveSwing(),landed=!!(ref&&ref===boss&&boss.hp<before),f=fusion();if(landed&&move?.__mbFusion==='REFLECT_EDGE'){const lv=move.__mbFusionLv||1,p=boss.nodes?.find(n=>n.name==='chest')?.p||boss.nodes?.[1]?.p;s.reflectHits++;player.comboWindow=Math.max(player.comboWindow||0,.28+.04*lv);player.cool=Math.min(player.cool||.2,.13);if(p){ring(p,DEF.REFLECT_EDGE.color);burst(p,DEF.REFLECT_EDGE.color,5+lv,2.5)}delayedReflect(boss,lv,DEF.REFLECT_EDGE.color)}else if(landed&&move?.__mbFusion==='RUPTURE_DRIVE'){const lv=move.__mbFusionLv||1,p=boss.nodes?.find(n=>n.name==='chest')?.p||boss.nodes?.[1]?.p||boss.pos;s.ruptureHits++;boss.posture=Math.min(115,(boss.posture||0)+6+3*lv);boss.stun=Math.max(boss.stun||0,.12+.04*lv);groundImpact(V(boss.pos.x,.06,boss.pos.z),1.0+.18*lv);ring(p,DEF.RUPTURE_DRIVE.color);burst(p,DEF.RUPTURE_DRIVE.color,8+lv*2,3.6+.3*lv);shake=Math.max(shake,.13+.025*lv);hitstop=Math.max(hitstop,.045+.007*lv);showProc('RUPTURE DRIVE · LAUNCH',DEF.RUPTURE_DRIVE.color)}if(f?.id==='ZERO_TRACE'&&(v3.zeroCharges||0)<bz){s.zeroProcs++;showProc('ZERO TRACE · RELEASE',f.color)}return out;
 };
 function fusionMove(f){
  if(f.id==='REFLECT_EDGE')return{name:`CORE FUSION · ${f.name}`,kind:'combo',shape:'cone',wind:.58,active:.78,hits:[.09,.28,.47,.66],range:3.75,arc:1.68,speed:2.75,damage:.66,force:17,recover:.78,motion:0};
  if(f.id==='RUPTURE_DRIVE')return{name:`CORE FUSION · ${f.name}`,kind:'rush',shape:'line',wind:.70,active:.48,hits:[.19],range:4.25,width:.86,speed:4.15,damage:.88,force:31,recover:.92,motion:1};
  if(f.id==='RESONANT_MIRROR')return{name:`CORE FUSION · ${f.name}`,kind:'stomp',shape:'circle',wind:.86,active:.84,hits:[.15,.57],range:4.05,speed:0,damage:.64,force:22,recover:.88,motion:2};
  return{name:`CORE FUSION · ${f.name}`,kind:'combo',shape:'circle',wind:.90,active:.90,hits:[.11,.40,.73],range:4.15,speed:1.85,damage:.80,force:26,recover:.96,motion:0};
 }
 const clone=m=>({...m,hits:[...(m?.hits||[])]});
 function forceFusion(move,call){const originals=ENEMY_MOVES[4].slice(),saved={...state.cores},forced=originals.map(()=>clone(move));ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...forced);state.cores.EDGE=state.cores.MIRROR=state.cores.PULSE=0;try{return call(move)}finally{state.cores.EDGE=saved.EDGE;state.cores.MIRROR=saved.MIRROR;state.cores.PULSE=saved.PULSE;ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...originals)}}
 const baseStart=startEnemyAttack;startEnemyAttack=function(move){if(boss!==s.finalBoss){s.finalBoss=boss;s.finalCalls=0}const f=fusion(),eligible=level===4&&mode==='play'&&boss?.hp>0&&state.boss===boss&&!state.broken&&!!f;if(eligible){s.finalCalls++;if(s.finalCalls%4===0){const m=fusionMove(f),p=boss.nodes?.find(n=>n.name==='chest')?.p||boss.nodes?.[1]?.p;if(p){ring(p,f.color);burst(p,f.color,7+f.lv*2,3.2+.2*f.lv)}s.finalFusionAttacks++;s.lastFinalFusion=f.name;s.lastProc=`DOLL COPY · ${f.name}`;return forceFusion(m,x=>baseStart(x))}}return baseStart(move)};
 const baseReset=reset;reset=function(l=0){const prev=typeof level==='number'?level:-1,out=baseReset(l);s.armed=null;s.armT=0;s.procT=0;s.lastProc='';s.resonantCool=0;s.finalBoss=boss;s.finalCalls=0;if(l===0&&prev>=4){s.reflectHits=s.reflectEchoes=s.ruptureHits=s.resonantProcs=s.zeroProcs=s.armedAttacks=s.finalFusionAttacks=0;s.lastFinalFusion=null}syncHud();return out};
 const baseStep=step;step=function(dt){const out=baseStep(dt);s.armT=Math.max(0,s.armT-dt);s.procT=Math.max(0,s.procT-dt);s.resonantCool=Math.max(0,s.resonantCool-dt);if(s.armT<=0)s.armed=null;if(boss!==s.finalBoss){s.finalBoss=boss;s.finalCalls=0}enhanceChoice();syncHud();return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{},f=fusion();return{...d,v16:true,coreFusionCombat:true,coreFusion:f?.name||null,coreFusionLevel:f?.lv||0,coreFusionArmed:s.armed,coreFusionArm:+s.armT.toFixed(2),reflectEdgeHits:s.reflectHits,reflectEdgeEchoes:s.reflectEchoes,ruptureDriveHits:s.ruptureHits,resonantMirrorProcs:s.resonantProcs,zeroTraceFusionProcs:s.zeroProcs,fusionArmedAttacks:s.armedAttacks,finalFusionCalls:s.finalCalls,finalFusionAttacks:s.finalFusionAttacks,lastFinalFusion:s.lastFinalFusion,fusionChoiceEnhanced:s.choicePasses>0,lastFusionProc:s.lastProc}};
 window.parryCoreFusionDiagnostics=()=>{const f=fusion();return{v16:true,fusion:f?.name||null,level:f?.lv||0,armed:s.armed,arm:+s.armT.toFixed(2),reflectHits:s.reflectHits,reflectEchoes:s.reflectEchoes,ruptureHits:s.ruptureHits,resonantProcs:s.resonantProcs,zeroProcs:s.zeroProcs,finalFusionAttacks:s.finalFusionAttacks,lastFinalFusion:s.lastFinalFusion}};
 ensureHud();enhanceChoice();syncHud();
})();
