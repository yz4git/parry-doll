'use strict';
// MIRROR BREAK v5 UI finish — keep post-break tactics readable and retire the consumed parry card at its source.
(()=>{
 if(window.__parryMirrorBreakV5UiLoaded)return;window.__parryMirrorBreakV5UiLoaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const style=document.createElement('style');style.textContent=`
 body.mb-final-duel #mbBreakHud.mb-tactic,
 body.mb-final-duel #mbBreakHud.mb-tactic.broken{left:max(14px,env(safe-area-inset-left))!important;right:auto!important;top:27%!important;transform:none!important;opacity:.92!important;visibility:visible!important;min-width:0!important;text-align:left!important}
 body.mb-final-duel.mb-mirror-shifting #mbBreakHud.mb-tactic{opacity:.92!important;visibility:visible!important;transform:none!important}
 body.mb-counter-spent #parrySuccessHud{opacity:0!important;visibility:hidden!important;transform:translateX(-8px) scale(.96)!important}
 @media(max-height:500px){body.mb-final-duel #mbBreakHud.mb-tactic,body.mb-final-duel #mbBreakHud.mb-tactic.broken{top:28%!important}}
 `;document.head.appendChild(style);
 let guardTimer=0,retired=0;
 function elementVisible(el){
  if(!el?.isConnected)return false;const cs=getComputedStyle(el),r=el.getBoundingClientRect();
  return cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)>.05&&r.width>1&&r.height>1;
 }
 function clearGuard(){clearTimeout(guardTimer);guardTimer=0;document.body.classList.remove('mb-counter-spent')}
 function retireSpentCounter(){
  clearGuard();if(player)player.counter=0;
  const hud=document.getElementById('parrySuccessHud');if(hud){hud.classList.remove('show','perfect');hud.dataset.mbSpentCounter='1'}
  document.body.classList.add('mb-counter-spent');retired++;
  guardTimer=setTimeout(()=>{document.body.classList.remove('mb-counter-spent');if(hud?.isConnected)delete hud.dataset.mbSpentCounter;guardTimer=0},220);
 }
 const baseResolve=resolveSwing;resolveSwing=function(){const before=!!(state.boss===boss&&state.broken),out=baseResolve();if(!before&&state.boss===boss&&state.broken)retireSpentCounter();return out};
 const baseReset=reset;reset=function(l=0){clearGuard();return baseReset(l)};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{
  const d=priorDiag?priorDiag():{},hud=document.getElementById('mbBreakHud'),counterHud=document.getElementById('parrySuccessHud');
  return{...d,v5Ui:true,tacticVisible:!!(hud?.classList.contains('mb-tactic')&&getComputedStyle(hud).visibility!=='hidden'&&Number(getComputedStyle(hud).opacity)>.25),spentCounterRetired:retired,counterGuard:document.body.classList.contains('mb-counter-spent'),counterHudVisible:elementVisible(counterHud)};
 };
})();
