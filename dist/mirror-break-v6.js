'use strict';
// MIRROR BREAK v6 — DOLL CORE changes player decisions, not only numeric output.
(()=>{
 if(window.__parryMirrorBreakV6Loaded)return;window.__parryMirrorBreakV6Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const s={edgeReadyT:0,edgeDrives:0,edgeHits:0,mirrorChainT:0,mirrorRefreshes:0,mirrorChainInputs:0,pulseCrushes:0,lastProc:'',procT:0,choicePasses:0};
 window.__mirrorBreakV6State=s;
 const INFO={
  EDGE:{role:'RIPOSTE DRIVE',jp:'追刃',rule:'PERFECT → 次の反撃が高速接近。命中後そのまま連撃へ。'},
  MIRROR:{role:'CHAIN DEFLECT',jp:'連鏡',rule:'PERFECT → パリィ硬直を即解除。短時間、連続弾きが可能。'},
  PULSE:{role:'RESONANCE CRUSH',jp:'震核',rule:'3段目命中 → 姿勢とRESOLVEへ共鳴衝撃。'}
 };
 const style=document.createElement('style');style.textContent=`
 #mbCoreChoice .mb-panel{position:relative;overflow:hidden}
 #mbCoreChoice .mb-panel:after{content:'THE PARRY DOLL WILL COPY THIS BUILD';display:block;margin-top:10px;text-align:center;color:#778c89;font-size:7px;letter-spacing:2.4px}
 #mbCoreChoice .mb-core{position:relative;overflow:hidden;transition:border-color .12s,transform .12s,box-shadow .12s}
 #mbCoreChoice .mb-core:before{content:'';position:absolute;left:0;top:0;bottom:0;width:2px;opacity:.75}
 #mbCoreChoice .mb-core.core-edge:before{background:#f1c56f}#mbCoreChoice .mb-core.core-mirror:before{background:#9ffff0}#mbCoreChoice .mb-core.core-pulse:before{background:#8cc9ff}
 #mbCoreChoice .mb-core.core-edge:active{border-color:#e6bd72aa;box-shadow:0 0 20px #dcae4d24}#mbCoreChoice .mb-core.core-mirror:active{border-color:#9fffe0aa;box-shadow:0 0 20px #75e6cf24}#mbCoreChoice .mb-core.core-pulse:active{border-color:#99d7ffaa;box-shadow:0 0 20px #63b7ef24}
 #mbCoreChoice .mb-core-role{display:block;margin-top:8px;padding-top:7px;border-top:1px solid #b8c8c020;color:#f0dfb5;font-size:9px;font-weight:800;letter-spacing:2px}
 #mbCoreChoice .mb-core-rule{display:block;margin-top:4px;color:#aabbb7;font-size:9px;line-height:1.4;letter-spacing:.4px}
 #mbCoreChoice .mb-build-preview{margin-top:7px;text-align:center;color:#9fb0ad;font-size:8px;letter-spacing:2px}
 #mbCoreChoice .mb-build-preview b{color:#e6c985;font-weight:700}
 @media(max-height:500px){#mbCoreChoice .mb-core-role{margin-top:5px;padding-top:4px;font-size:8px}#mbCoreChoice .mb-core-rule{margin-top:2px;font-size:8px;line-height:1.25}#mbCoreChoice .mb-panel:after{margin-top:6px}}
 `;document.head.appendChild(style);
 function proc(name,point,color){s.lastProc=name;s.procT=.48;if(point){ring(point,color);burst(point,color,5,2.7)}sound(name==='EDGE DRIVE'?610:name==='MIRROR CHAIN'?790:330,.08,'triangle',.014)}
 function enhanceChoice(){
  if(!state.choice)return;const chooser=document.getElementById('mbCoreChoice'),grid=chooser?.querySelector('.mb-core-grid');if(!grid||grid.children.length!==3)return;
  const keys=['EDGE','MIRROR','PULSE'];[...grid.children].forEach((b,i)=>{const key=keys[i],d=INFO[key];b.classList.add('core-'+key.toLowerCase());if(!b.querySelector('.mb-core-role')){const role=document.createElement('span');role.className='mb-core-role';role.textContent=d.role+' · '+d.jp;const rule=document.createElement('span');rule.className='mb-core-rule';rule.textContent=d.rule;b.append(role,rule)}});
  const panel=chooser.querySelector('.mb-panel');let preview=panel?.querySelector('.mb-build-preview');if(panel&&!preview){preview=document.createElement('div');preview.className='mb-build-preview';panel.appendChild(preview)}
  if(preview){const c=state.cores;preview.innerHTML=`CURRENT BUILD&nbsp; <b>E${c.EDGE}</b> · <b>M${c.MIRROR}</b> · <b>P${c.PULSE}</b>`}
  s.choicePasses++;
 }
 const v6EnemyImpact=enemyImpact;enemyImpact=function(move=null){
  const p0=parries,pf=perfects,out=v6EnemyImpact(move),didPerfect=perfects>pf;
  if(didPerfect){
   const edge=state.cores.EDGE||0,mirror=state.cores.MIRROR||0,point=player?.nodes?.find(n=>n.name==='hand')?.p||player?.nodes?.[1]?.p;
   if(edge>0){s.edgeReadyT=Math.max(s.edgeReadyT,1.18+.16*edge);proc('EDGE READY',point,'#ffe0a0')}
   if(mirror>0){s.mirrorChainT=Math.max(s.mirrorChainT,.84+.12*mirror);player.parryCool=Math.min(player.parryCool,.035);s.mirrorRefreshes++;proc('MIRROR CHAIN',point,'#aaffea')}
  }
  return out;
 };
 const v6PlayerParry=playerParry;playerParry=function(){
  const mirror=state.cores.MIRROR||0,chain=mirror>0&&s.mirrorChainT>0;
  if(chain)player.parryCool=0;
  const ok=v6PlayerParry();if(ok&&chain){s.mirrorChainInputs++;s.mirrorChainT=Math.max(s.mirrorChainT,.48+.10*mirror)}return ok;
 };
 const v6PlayerAttack=playerAttack;playerAttack=function(){
  const edge=state.cores.EDGE||0,drive=edge>0&&s.edgeReadyT>0&&player?.counter>0;
  const ok=v6PlayerAttack();if(ok&&drive&&player.swing){
   player.swing.__mbEdgeDrive=true;player.swing.damage+=3.1*edge;player.swing.force+=2.4*edge;
   const to=boss&&player?norm(sub(boss.pos,player.pos)):V();player.vel=add(player.vel,mul(to,2.25+.65*edge));s.edgeReadyT=0;s.edgeDrives++;proc('EDGE DRIVE',player.nodes.find(n=>n.name==='hand')?.p||player.nodes[1].p,'#ffe0a0');
  }
  return ok;
 };
 const v6ResolveSwing=resolveSwing;resolveSwing=function(){
  const move=player.swing?{...player.swing}:null,beforeHp=boss?.hp||0,beforePosture=boss?.posture||0,out=v6ResolveSwing(),landed=!!(boss&&boss.hp<beforeHp);
  if(!landed||!move)return out;
  const point=boss.nodes?.find(n=>n.name==='chest')?.p||boss.nodes?.[1]?.p||boss.pos;
  if(move.__mbEdgeDrive){const lv=state.cores.EDGE||0;boss.posture=Math.min(115,boss.posture+4+2*lv);player.comboWindow=Math.max(player.comboWindow,.30+.055*lv);player.cool=Math.min(player.cool,.15);s.edgeHits++;proc('EDGE DRIVE',point,'#ffe0a0')}
  if(move.combo===2&&!move.counter&&(state.cores.PULSE||0)>0){
   const lv=state.cores.PULSE,bump=7+3*lv;boss.posture=Math.min(115,boss.posture+bump);boss.stun=Math.max(boss.stun,.08+.035*lv);
   if(window.__phaseBreakV2State)window.__phaseBreakV2State.resolve=Math.min(100,(window.__phaseBreakV2State.resolve||0)+6+2*lv);
   ring(V(boss.pos.x,.06,boss.pos.z),'#9bdcff');ring(point,'#b9fff1');burst(point,'#9bdcff',7+lv*2,3.4+lv*.4);shake=Math.max(shake,.11+.025*lv);hitstop=Math.max(hitstop,.045+.008*lv);s.pulseCrushes++;proc('PULSE CRUSH',point,'#9bdcff');
  }
  s.lastPostureGain=Math.max(0,(boss.posture||0)-beforePosture);return out;
 };
 const v6Reset=reset;reset=function(l=0){const out=v6Reset(l);s.edgeReadyT=s.mirrorChainT=s.procT=0;s.lastProc='';return out};
 const v6Step=step;step=function(dt){const out=v6Step(dt);s.edgeReadyT=Math.max(0,s.edgeReadyT-dt);s.mirrorChainT=Math.max(0,s.mirrorChainT-dt);s.procT=Math.max(0,s.procT-dt);enhanceChoice();return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v6:true,coreStyle:true,edgeReady:+s.edgeReadyT.toFixed(2),edgeDrives:s.edgeDrives,edgeHits:s.edgeHits,mirrorChain:+s.mirrorChainT.toFixed(2),mirrorRefreshes:s.mirrorRefreshes,mirrorChainInputs:s.mirrorChainInputs,pulseCrushes:s.pulseCrushes,lastCoreProc:s.lastProc,choiceEnhanced:s.choicePasses>0}};
 enhanceChoice();
})();
