'use strict';
// AAA presentation pass v2 — cinematic combat focus and reward-state polish.
(()=>{
  if(window.__parryAAAPresentationV2Loaded)return;
  window.__parryAAAPresentationV2Loaded=true;

  const style=document.createElement('style');
  style.id='pd-aaa-presentation-v2-style';
  style.textContent=`
  /* Keep the neutral combat frame quieter; action states get the visual budget. */
  body.pd-play:not(.pd-warning):not(.pd-counter-ready) #attack{
    opacity:.72!important;
    filter:saturate(.72) brightness(.82)!important;
    border-color:rgba(176,194,202,.32)!important;
    box-shadow:inset 0 0 0 4px rgba(5,10,15,.30),inset 0 1px rgba(255,255,255,.10),0 8px 21px rgba(0,0,0,.27)!important;
  }
  body.pd-play:not(.pd-warning):not(.pd-counter-ready) #attack:active,
  body.pd-play:not(.pd-warning):not(.pd-counter-ready) #attack.pressed{
    opacity:.93!important;filter:brightness(1.02)!important;
  }

  /* Player status is readable but no longer competes with the duel. */
  body.pd-play #playerHud{
    width:170px!important;
    background:linear-gradient(112deg,rgba(7,14,21,.70),rgba(7,14,21,.36))!important;
    border-left-color:rgba(113,199,187,.52)!important;
    border-top-color:rgba(225,235,239,.055)!important;
    box-shadow:0 8px 22px rgba(0,0,0,.17)!important;
  }
  body.pd-play #playerHud span{color:#aab6bc!important}
  body.pd-play #stats{opacity:.86}

  /* Dynamic scene framing. It darkens the edges, never the character contact area. */
  #pdCombatFocus{
    position:fixed;inset:0;z-index:6;pointer-events:none;opacity:0;
    background:radial-gradient(ellipse at 52% 50%,transparent 0 31%,rgba(1,4,7,.08) 48%,rgba(1,4,7,.54) 100%);
    transition:opacity .16s ease,background .16s ease;
  }
  body.pd-parry-warning #pdCombatFocus{
    opacity:.64;
    background:
      radial-gradient(ellipse at 52% 50%,transparent 0 28%,rgba(2,5,8,.09) 46%,rgba(1,3,6,.54) 100%),
      linear-gradient(108deg,rgba(245,201,111,.025),transparent 28%,transparent 72%,rgba(245,201,111,.018));
  }
  body.pd-dodge-warning #pdCombatFocus{
    opacity:.64;
    background:
      radial-gradient(ellipse at 52% 50%,transparent 0 28%,rgba(2,5,8,.09) 46%,rgba(1,3,6,.54) 100%),
      linear-gradient(108deg,rgba(98,220,255,.025),transparent 28%,transparent 72%,rgba(98,220,255,.018));
  }
  body.pd-counter-ready #pdCombatFocus{
    opacity:.43;
    background:
      radial-gradient(ellipse at 52% 50%,transparent 0 35%,rgba(2,5,8,.05) 52%,rgba(1,3,6,.39) 100%),
      radial-gradient(circle at 61% 48%,rgba(255,233,170,.045),transparent 22%);
  }

  @keyframes pd-focus-success-gold{
    0%{opacity:.72;background:radial-gradient(circle at 52% 50%,rgba(255,245,211,.12) 0,rgba(245,201,111,.055) 13%,transparent 31%,rgba(0,0,0,.28) 72%,rgba(0,0,0,.50) 100%)}
    100%{opacity:.13;background:radial-gradient(circle at 52% 50%,rgba(255,245,211,0) 0,rgba(245,201,111,0) 22%,transparent 38%,rgba(0,0,0,.03) 100%)}
  }
  @keyframes pd-focus-success-cyan{
    0%{opacity:.72;background:radial-gradient(circle at 52% 50%,rgba(232,253,255,.12) 0,rgba(98,220,255,.055) 13%,transparent 31%,rgba(0,0,0,.28) 72%,rgba(0,0,0,.50) 100%)}
    100%{opacity:.13;background:radial-gradient(circle at 52% 50%,rgba(232,253,255,0) 0,rgba(98,220,255,0) 22%,transparent 38%,rgba(0,0,0,.03) 100%)}
  }
  body.pd-success-beat:not(.pd-success-dodge) #pdCombatFocus{
    animation:pd-focus-success-gold .38s cubic-bezier(.16,.72,.2,1) both;
  }
  body.pd-success-beat.pd-success-dodge #pdCombatFocus{
    animation:pd-focus-success-cyan .38s cubic-bezier(.16,.72,.2,1) both;
  }

  /* Result typography gets one clean impact instead of constant glow. */
  @keyframes pd-toast-impact{
    0%{transform:translateX(12px) scale(.88);opacity:.10;filter:blur(1.2px)}
    28%{transform:translateX(0) scale(1.10);opacity:1;filter:blur(0)}
    62%{transform:translateX(0) scale(1.02);opacity:1}
    100%{transform:translateX(0) scale(1);opacity:1}
  }
  @keyframes pd-toast-sweep{
    0%{transform:translateX(-120%) skewX(-22deg);opacity:0}
    22%{opacity:.72}
    100%{transform:translateX(280%) skewX(-22deg);opacity:0}
  }
  body.pd-play #toast.pd-toast-impact{
    animation:pd-toast-impact .36s cubic-bezier(.12,.76,.25,1) both!important;
  }
  body.pd-play #toast.pd-toast-impact::after{
    content:"";position:absolute;left:0;top:48%;width:56px;height:2px;
    background:linear-gradient(90deg,transparent,#fff8dd,rgba(245,201,111,.68),transparent);
    box-shadow:0 0 11px rgba(255,231,157,.58);
    animation:pd-toast-sweep .34s ease-out both;
    pointer-events:none;
  }
  body.pd-success-dodge #toast.pd-toast-impact::after{
    background:linear-gradient(90deg,transparent,#ecfdff,rgba(98,220,255,.72),transparent);
    box-shadow:0 0 11px rgba(98,220,255,.52);
  }
  body.pd-play #toast.pd-toast-impact{
    font-size:clamp(18px,3vw,29px)!important;
  }

  /* A short cinematic slash line gives successful defense a authored frame. */
  #pdImpactSlash{
    position:fixed;left:19%;right:19%;top:49%;height:1px;z-index:19;pointer-events:none;opacity:0;
    transform:rotate(-5deg) scaleX(.2);transform-origin:center;
  }
  @keyframes pd-slash-gold{
    0%{opacity:0;transform:rotate(-5deg) scaleX(.12)}
    22%{opacity:.82;transform:rotate(-5deg) scaleX(1)}
    100%{opacity:0;transform:rotate(-5deg) scaleX(1.18)}
  }
  @keyframes pd-slash-cyan{
    0%{opacity:0;transform:rotate(5deg) scaleX(.12)}
    22%{opacity:.78;transform:rotate(5deg) scaleX(1)}
    100%{opacity:0;transform:rotate(5deg) scaleX(1.18)}
  }
  body.pd-success-beat:not(.pd-success-dodge) #pdImpactSlash{
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.88) 46%,#f5c96f 51%,transparent);
    box-shadow:0 0 10px rgba(245,201,111,.72);
    animation:pd-slash-gold .28s ease-out both;
  }
  body.pd-success-beat.pd-success-dodge #pdImpactSlash{
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.86) 46%,#62dcff 51%,transparent);
    box-shadow:0 0 10px rgba(98,220,255,.68);
    animation:pd-slash-cyan .28s ease-out both;
  }

  /* Counter callout reads as a continuation of the successful defense, not another alert. */
  body.pd-counter-ready #pdCounterCallout{
    border-right-color:#f2d48a!important;
    background:linear-gradient(90deg,transparent,rgba(6,12,18,.76) 18%,rgba(8,15,22,.92))!important;
  }
  body.pd-counter-ready #pdCounterCallout b{color:#fff3cb!important}
  body.pd-counter-ready #pdCounterCallout small{color:#9fb2bb!important}

  /* Slightly reduce persistent top-right chrome in compact landscape. */
  @media(max-height:500px) and (orientation:landscape){
    body.pd-play header{opacity:.62!important}
    body.pd-play #playerHud{width:158px!important}
    body.pd-play #toast.pd-toast-impact{font-size:clamp(17px,2.7vw,27px)!important}
    #pdImpactSlash{left:16%;right:16%}
  }

  @media(prefers-reduced-motion:reduce){
    body.pd-play #toast.pd-toast-impact,
    body.pd-success-beat #pdCombatFocus,
    body.pd-success-beat #pdImpactSlash{animation-duration:.01ms!important;animation-iteration-count:1!important}
  }
  `;
  document.head.appendChild(style);

  const focus=document.createElement('div');
  focus.id='pdCombatFocus';
  focus.setAttribute('aria-hidden','true');
  document.body.appendChild(focus);

  const slash=document.createElement('div');
  slash.id='pdImpactSlash';
  slash.setAttribute('aria-hidden','true');
  document.body.appendChild(slash);

  const toast=document.getElementById('toast');
  let beatTimer=0;
  let lastText='';
  function playBeat(text){
    const value=(text||'').trim();
    if(!value||value===lastText)return;
    lastText=value;
    const isDodge=/DODGE/i.test(value);
    const isReward=/PERFECT|DODGE|PARRY|COUNTER|BREAK|FINISH/i.test(value);
    if(!isReward)return;
    document.body.classList.toggle('pd-success-dodge',isDodge);
    document.body.classList.remove('pd-success-beat');
    toast?.classList.remove('pd-toast-impact');
    void document.body.offsetWidth;
    document.body.classList.add('pd-success-beat');
    toast?.classList.add('pd-toast-impact');
    clearTimeout(beatTimer);
    beatTimer=setTimeout(()=>{
      document.body.classList.remove('pd-success-beat','pd-success-dodge');
      toast?.classList.remove('pd-toast-impact');
    },420);
  }
  if(toast){
    const observer=new MutationObserver(()=>playBeat(toast.textContent));
    observer.observe(toast,{childList:true,characterData:true,subtree:true});
  }
})();
