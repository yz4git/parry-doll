'use strict';
// AAA presentation pass v4 — semantic reward and danger colours.
(()=>{
  if(window.__parryAAAPresentationV4Loaded)return;
  window.__parryAAAPresentationV4Loaded=true;

  const style=document.createElement('style');
  style.id='pd-aaa-presentation-v4-style';
  style.textContent=`
  /* Defense language stays consistent from telegraph through reward. */
  body.pd-success-beat:not(.pd-success-dodge) #toast.pd-toast-impact{
    color:#ffe8a9!important;
    border-right-color:#f5c96f!important;
    text-shadow:0 3px 14px #000,0 0 19px rgba(245,201,111,.30)!important;
  }
  body.pd-success-dodge #toast.pd-toast-impact{
    color:#c9f7ff!important;
    border-right-color:#62dcff!important;
    text-shadow:0 3px 14px #000,0 0 19px rgba(98,220,255,.34)!important;
  }

  /* Low vitality switches the status plate from calm teal to danger red, without touching controls. */
  body.pd-low-health.pd-play #playerHud{
    border-left-color:rgba(255,103,79,.80)!important;
    background:linear-gradient(112deg,rgba(25,10,12,.74),rgba(11,11,16,.40))!important;
  }
  body.pd-low-health.pd-play #playerHud span{color:#e2bab4!important}
  body.pd-low-health.pd-play #playerHP{
    background:linear-gradient(90deg,#7a272a,#d34b3d,#ff8a68)!important;
    box-shadow:inset 0 1px rgba(255,231,222,.44),0 0 11px rgba(255,87,61,.18)!important;
  }
  body.pd-low-health.pd-play #stats{color:#f0a890!important}

  /* Boss damage stays warmer/redder than the player danger state for quick ownership. */
  body.pd-play #bossHP{
    background:linear-gradient(90deg,#741e25,#b93a31 55%,#ef795a)!important;
  }

  /* Reward state owns the ATTACK button only after a successful defense. */
  body.pd-counter-ready #attack small{color:#2b3033!important;opacity:.82!important}
  body.pd-counter-ready #attack{letter-spacing:.035em!important}
  `;
  document.head.appendChild(style);
})();
