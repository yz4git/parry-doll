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
 const hidden=new Set();let restoreTimer=0,scanTimer=0,observer=null,suppressUntil=0;
 const hasCounterText=el=>/COUNTER\s*READY/i.test((el?.textContent||'').replace(/\s+/g,' ').trim());
 function visible(el){if(!el?.isConnected)return false;const cs=getComputedStyle(el),r=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)>.05&&r.width>1&&r.height>1}
 function cardFor(el){
  let card=el;
  for(let i=0;i<3;i++){
   const p=card?.parentElement;if(!p||p===document.body||p===document.documentElement||!hasCounterText(p))break;
   const r=p.getBoundingClientRect(),area=Math.max(0,r.width*r.height),screen=Math.max(1,innerWidth*innerHeight);
   if(area>screen*.30)break;card=p;
  }
  return card;
 }
 function counterCards(){
  const out=new Set();for(const el of document.querySelectorAll('body *')){if(!hasCounterText(el))continue;const childHas=[...el.children].some(hasCounterText);if(childHas)continue;const card=cardFor(el);if(card&&card!==document.body)out.add(card)}return [...out]
 }
 function hideCounterCards(){
  if(performance.now()>suppressUntil)return;
  for(const el of counterCards()){
   hidden.add(el);el.dataset.mbSpentCounter='1';el.style.setProperty('display','none','important');el.style.setProperty('visibility','hidden','important');el.style.setProperty('opacity','0','important');
  }
 }
 function stopSuppression(restore=true){
  clearTimeout(restoreTimer);clearInterval(scanTimer);restoreTimer=scanTimer=0;observer?.disconnect();observer=null;document.body.classList.remove('mb-counter-spent');
  if(restore){for(const el of hidden){if(!el?.isConnected)continue;el.style.removeProperty('display');el.style.removeProperty('visibility');el.style.removeProperty('opacity');delete el.dataset.mbSpentCounter}hidden.clear()}
 }
 function retireSpentCounter(){
  stopSuppression(true);if(player)player.counter=0;document.body.classList.add('mb-counter-spent');suppressUntil=performance.now()+1350;hideCounterCards();
  observer=new MutationObserver(()=>hideCounterCards());observer.observe(document.body,{subtree:true,childList:true,characterData:true});scanTimer=setInterval(hideCounterCards,32);
  restoreTimer=setTimeout(()=>stopSuppression(true),1380);
 }
 const baseResolve=resolveSwing;resolveSwing=function(){const before=!!(state.boss===boss&&state.broken),out=baseResolve();if(!before&&state.boss===boss&&state.broken)retireSpentCounter();return out};
 const baseReset=reset;reset=function(l=0){stopSuppression(true);return baseReset(l)};
 function visibleCounterCount(){return counterCards().filter(visible).length}
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{},hud=document.getElementById('mbBreakHud');return{...d,v5Ui:true,tacticVisible:!!(hud?.classList.contains('mb-tactic')&&getComputedStyle(hud).visibility!=='hidden'&&Number(getComputedStyle(hud).opacity)>.25),spentCounterHidden:hidden.size>0,counterSuppression:performance.now()<suppressUntil,visibleCounterReady:visibleCounterCount()}};
})();
