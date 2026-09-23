'use strict';
// AAA presentation pass v3 — scene grade and de-cluttered counter hierarchy.
(()=>{
  if(window.__parryAAAPresentationV3Loaded)return;
  window.__parryAAAPresentationV3Loaded=true;

  const style=document.createElement('style');
  style.id='pd-aaa-presentation-v3-style';
  style.textContent=`
  #pdSceneTint{
    position:fixed;inset:0;z-index:4;pointer-events:none;opacity:0;
    background:
      radial-gradient(ellipse at 52% 48%,rgba(7,15,22,.02) 0 30%,rgba(5,12,19,.045) 52%,rgba(2,6,10,.16) 100%),
      linear-gradient(180deg,rgba(10,24,34,.11),rgba(6,14,21,.035) 38%,rgba(4,10,16,.055) 66%,rgba(2,6,10,.17)),
      linear-gradient(108deg,rgba(23,72,91,.045),transparent 31%,transparent 68%,rgba(131,83,35,.026));
    transition:opacity .22s ease;
  }
  body.pd-play #pdSceneTint{opacity:1}
  body.pd-title #pdSceneTint{opacity:0}

  /* V1 already supplies edge framing; v3 strengthens it slightly without crushing the combat centre. */
  body.pd-play #pdCinemaGrade{
    opacity:.88!important;
    background:
      radial-gradient(ellipse at 52% 48%,transparent 0 34%,rgba(4,9,14,.055) 54%,rgba(2,5,9,.39) 100%),
      linear-gradient(180deg,rgba(6,13,20,.21),transparent 25%,transparent 68%,rgba(2,5,9,.31)),
      linear-gradient(105deg,rgba(22,72,91,.065),transparent 34%,transparent 68%,rgba(154,96,37,.040))!important;
  }

  /* The new counter flow already owns the prompt; remove the older duplicate centre label. */
  body.pd-play #parrySuccessHud{display:none!important}

  /* Give the scene more breathing room by making persistent utility chrome nearly invisible. */
  body.pd-play header button{
    background:linear-gradient(145deg,rgba(10,18,26,.72),rgba(4,9,14,.60))!important;
    border-color:rgba(214,226,232,.085)!important;
  }

  /* Strong boss identity, but the frame itself stays understated. */
  body.pd-play #bossHud{
    background:linear-gradient(180deg,rgba(7,14,22,.84),rgba(5,11,17,.57))!important;
    border-color:rgba(224,233,237,.095)!important;
    border-top-color:rgba(240,221,175,.19)!important;
  }
  body.pd-play #bossHud::after{
    content:"";position:absolute;left:11px;right:11px;bottom:-1px;height:1px;
    background:linear-gradient(90deg,transparent,rgba(245,201,111,.18),transparent);
    pointer-events:none;
  }

  /* Neutral action cluster: readable at a glance, visually quiet until a response is required. */
  body.pd-play:not(.pd-warning):not(.pd-counter-ready) #attack{opacity:.64!important}
  body.pd-play:not(.pd-warning) #dodge,
  body.pd-play:not(.pd-warning) #parry{filter:saturate(.92) brightness(.94)}
  body.pd-counter-ready #attack{filter:none!important;opacity:1!important}

  /* A subtle floor-side shade anchors the controls without adding another panel. */
  #pdControlShade{
    position:fixed;left:0;right:0;bottom:0;height:min(31vh,142px);z-index:8;pointer-events:none;opacity:0;
    background:linear-gradient(180deg,transparent,rgba(2,6,10,.05) 35%,rgba(2,6,10,.21));
    transition:opacity .2s ease;
  }
  body.pd-play #pdControlShade{opacity:1}
  body.pd-title #pdControlShade{opacity:0}

  @media(max-height:500px) and (orientation:landscape){
    #pdControlShade{height:118px}
    body.pd-play #pdCinemaGrade{opacity:.84!important}
  }
  `;
  document.head.appendChild(style);

  const tint=document.createElement('div');
  tint.id='pdSceneTint';
  tint.setAttribute('aria-hidden','true');
  document.body.appendChild(tint);

  const controlShade=document.createElement('div');
  controlShade.id='pdControlShade';
  controlShade.setAttribute('aria-hidden','true');
  document.body.appendChild(controlShade);
})();
