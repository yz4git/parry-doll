'use strict';
// MIRROR BREAK v5 UI finish — keep post-break tactics readable in every phase and retire spent counter prompts.
(()=>{
 if(window.__parryMirrorBreakV5UiLoaded)return;window.__parryMirrorBreakV5UiLoaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const style=document.createElement('style');style.textContent=`
 body.mb-final-duel #mbBreakHud.mb-tactic,
 body.mb-final-duel #mbBreakHud.mb-tactic.broken{left:max(14px,env(safe-area-inset-left))!important;right:auto!important;top:27%!important;transform:none!important;opacity:.92!important;visibility:visible!important;min-width:0!important;text-align:left!important}
 body.mb-final-duel.mb-mirror-shifting #mbBreakHud.mb-tactic{opacity:.92!important;visibility:visible!important;transform:none!important}
 @media(max-height:500px){body.mb-final-duel #mbBreakHud.mb-tactic,body.mb-final-duel #mbBreakHud.mb-tactic.broken{top:28%!important}}
 `;document.head.appendChild(style);
 const hidden=new Set();let restoreTimer=0;
 function restoreCounterNodes(){clearTimeout(restoreTimer);restoreTimer=0;for(const el of hidden){if(!el?.isConnected)continue;el.style.removeProperty('visibility');el.style.removeProperty('opacity')}hidden.clear()}
 function retireSpentCounter(){
  if(player)player.counter=0;
  for(const el of document.querySelectorAll('body *')){
   if((el.textContent||'').trim()!=='COUNTER READY')continue;
   hidden.add(el);el.style.setProperty('visibility','hidden','important');el.style.setProperty('opacity','0','important');
  }
  restoreTimer=setTimeout(restoreCounterNodes,900);
 }
 const baseResolve=resolveSwing;resolveSwing=function(){const before=!!(state.boss===boss&&state.broken),out=baseResolve();if(!before&&state.boss===boss&&state.broken)retireSpentCounter();return out};
 const baseReset=reset;reset=function(l=0){restoreCounterNodes();return baseReset(l)};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{},hud=document.getElementById('mbBreakHud');return{...d,v5Ui:true,tacticVisible:!!(hud?.classList.contains('mb-tactic')&&getComputedStyle(hud).visibility!=='hidden'&&Number(getComputedStyle(hud).opacity)>.25),spentCounterHidden:hidden.size>0}};
})();
