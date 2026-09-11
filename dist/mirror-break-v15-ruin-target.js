'use strict';
// MIRROR BREAK v15 — RUIN TARGET: make carried destruction readable and intentionally executable instead of accidental.
(()=>{
 if(window.__parryMirrorBreakV15Loaded)return;window.__parryMirrorBreakV15Loaded=true;
 const state=window.__mirrorBreakState,v12=window.__mirrorBreakV12State,v13=window.__mirrorBreakV13State,v14=window.__mirrorBreakV14State;if(!state||!v12||!v13||!v14)return;
 const ROUTES=['ASH GATE','CAGE BREACH','BROKEN SPINE','ALTAR RIFT'];
 const COLORS=['#ffc475','#94ead8','#ddb9ff','#d3ecff'];
 const s={visible:false,ready:false,source:-1,route:null,target:null,threshold:0,pulse:0,lastBoss:null,lastReady:false,updates:0,consumed:false};window.__mirrorBreakV15State=s;
 const style=document.createElement('style');style.textContent=`
 #mbRuinTarget{position:fixed;left:50%;top:50%;z-index:29;pointer-events:none;opacity:0;transform:translate(-50%,-50%) scale(.90);min-width:118px;padding:5px 10px;text-align:center;background:linear-gradient(90deg,transparent,#071019cf 18%,#071019cf 82%,transparent);border-left:1px solid #9fd9cf55;border-right:1px solid #9fd9cf55;text-shadow:0 2px 10px #000;transition:opacity .12s,transform .12s,filter .12s;white-space:nowrap}
 #mbRuinTarget.show{opacity:.72;transform:translate(-50%,-50%) scale(1)}#mbRuinTarget.ready{opacity:1;filter:drop-shadow(0 0 8px #f0d38366);border-color:#f2d48e99;background:linear-gradient(90deg,transparent,#10140fe8 15%,#10140fe8 85%,transparent)}
 #mbRuinTarget small{display:block;color:#a9c5c0;font-size:7px;letter-spacing:2.6px}#mbRuinTarget b{display:block;margin-top:2px;color:#d9eee8;font-size:10px;letter-spacing:3px}#mbRuinTarget.ready b{color:#ffe29b;font-size:11px}#mbRuinTarget em{display:block;margin-top:2px;color:#91aaa5;font-size:6px;letter-spacing:1.5px;font-style:normal}#mbRuinTarget.ready em{color:#e7cf98}
 #mbRuinTarget:before{content:'◇';position:absolute;left:50%;top:-19px;transform:translateX(-50%);font-size:19px;color:#a9eee077;text-shadow:0 0 10px #80ddcc88}#mbRuinTarget.ready:before{content:'◆';color:#ffe29bd9;text-shadow:0 0 13px #f6d37faa}
 body.mb-ruin-finisher #mbRuinTarget,body.mb-chain-destruction #mbRuinTarget{opacity:0!important;visibility:hidden!important}
 @media(max-height:500px){#mbRuinTarget{min-width:104px;padding:4px 8px}#mbRuinTarget b{font-size:9px}#mbRuinTarget.ready b{font-size:10px}}
 `;document.head.appendChild(style);
 const hud=document.createElement('div');hud.id='mbRuinTarget';hud.innerHTML='<small>RUIN ROUTE</small><b>CHAIN ZONE</b><em></em>';document.body.appendChild(hud);
 const entry=()=>level>=1&&level<=4?v12.history?.find?.(e=>e.level===level-1)||null:null;
 const targetFor=source=>{const side=source%2?1:-1;if(source===3)return{x:0,z:-4.05,r:2.45};return{x:side*3.6,z:-5.35,r:source===2?2.65:2.35}};
 const hpThreshold=source=>Math.max(18,Math.min(38,Math.max(1,boss?.spec?.hp||boss?.hp||1)*(.115+source*.012)));
 const currentKey=e=>e?`${level}:${e.level}:${e.serial}`:'';
 const routeSpent=e=>!e||v13.consumed?.has?.(currentKey(e))||v13.history?.some?.(h=>h.level===level&&h.source===e.level);
 function hide(){s.visible=false;s.ready=false;hud.classList.remove('show','ready')}
 function positionMarker(target){let p=null;try{p=project(V(target.x,.22,target.z))}catch(_){return false}if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.y)||p.z<=.22)return false;const vw=window.innerWidth||W||852,vh=window.innerHeight||H||393,x=Math.max(64,Math.min(vw-64,p.x)),y=Math.max(88,Math.min(vh-92,p.y));hud.style.left=x+'px';hud.style.top=y+'px';return true}
 function update(dt=1/60){s.updates++;const e=entry();if(!e||mode!=='play'||!boss||!player||boss.hp<=0||player.hp<=0||state.boss!==boss||!state.broken||v14.activeT>0||window.__phaseBreakV2State?.cineT>0){hide();return}const source=e.level,spent=routeSpent(e),target=targetFor(source),limit=hpThreshold(source),ready=!spent&&boss.hp<=limit;s.source=source;s.route=ROUTES[source];s.target=target;s.threshold=limit;s.consumed=spent;if(spent){hide();return}const visible=positionMarker(target);s.visible=visible;s.ready=visible&&ready;hud.classList.toggle('show',visible);hud.classList.toggle('ready',visible&&ready);hud.querySelector('small').textContent=ready?'EXECUTION READY':'RUIN ROUTE';hud.querySelector('b').textContent=ROUTES[source];hud.querySelector('em').textContent=ready?'BODY BROKEN · LAUNCH HERE':`CHAIN ZONE · EXECUTE ≤ ${Math.ceil(limit)} HP`;
  if(ready&&!s.lastReady){sound(520,.09,'sine',.015);s.pulse=.01}s.lastReady=ready;if(ready){s.pulse-=dt;if(s.pulse<=0){ring(V(target.x,.08,target.z),COLORS[source]);s.pulse=.68}}else s.pulse=0;
 }
 const baseStep=step;step=function(dt){const out=baseStep(dt);update(dt);return out};
 const baseReset=reset;reset=function(l=0){const out=baseReset(l);s.lastBoss=boss;s.lastReady=false;s.pulse=0;s.source=-1;s.route=null;s.target=null;s.threshold=0;s.consumed=false;hide();return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return{...d,v15:true,ruinTargeting:true,ruinTargetVisible:s.visible,ruinExecutionReady:s.ready,ruinTargetSource:s.source,ruinTargetRoute:s.route,ruinTargetThreshold:+s.threshold.toFixed(1),ruinTarget:s.target?{...s.target}:null,ruinTargetConsumed:s.consumed,ruinTargetUpdates:s.updates}};
 window.parryRuinTargetDiagnostics=()=>({v15:true,visible:s.visible,ready:s.ready,source:s.source,route:s.route,threshold:+s.threshold.toFixed(1),target:s.target?{...s.target}:null,consumed:s.consumed,updates:s.updates});
 update();
})();
