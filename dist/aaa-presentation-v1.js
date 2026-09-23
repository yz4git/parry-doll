'use strict';
// AAA presentation pass v1 — visual hierarchy only. Combat logic and character geometry stay untouched.
(()=>{
  if(window.__parryAAAPresentationV1Loaded)return;
  window.__parryAAAPresentationV1Loaded=true;

  const style=document.createElement('style');
  style.id='pd-aaa-presentation-style';
  style.textContent=`
  :root{
    --pd-ink:#05080d;
    --pd-panel:#09111ad9;
    --pd-panel-2:#0d1823c7;
    --pd-line:#d8e2e91f;
    --pd-text:#f2f5f7;
    --pd-muted:#95a3ad;
    --pd-gold:#f5c96f;
    --pd-gold-hot:#ffe7a1;
    --pd-cyan:#62dcff;
    --pd-cyan-hot:#c9f7ff;
    --pd-danger:#ff674f;
    --pd-danger-hot:#ff9a6f;
    --pd-health:#73c7bb;
  }

  html,body{background:var(--pd-ink)!important;color:var(--pd-text)!important}
  body{font-family:"Helvetica Neue","Arial Narrow",system-ui,-apple-system,sans-serif!important}

  /* A restrained cinematic grade keeps the 3D scene dominant while giving the frame depth. */
  #pdCinemaGrade{
    position:fixed;inset:0;pointer-events:none;z-index:5;opacity:.78;
    background:
      radial-gradient(ellipse at 50% 48%,transparent 0 38%,rgba(4,8,13,.08) 56%,rgba(2,5,9,.48) 100%),
      linear-gradient(180deg,rgba(6,12,19,.26),transparent 24%,transparent 72%,rgba(2,5,9,.34)),
      linear-gradient(105deg,rgba(29,88,109,.055),transparent 34%,transparent 68%,rgba(173,110,38,.045));
    transition:opacity .25s ease,box-shadow .22s ease;
  }
  #pdCinemaGrade::before{
    content:"";position:absolute;inset:0;
    background:linear-gradient(90deg,rgba(255,255,255,.025),transparent 18%,transparent 82%,rgba(255,255,255,.018));
    mix-blend-mode:screen;opacity:.55;
  }
  #pdCinemaGrade::after{
    content:"";position:absolute;inset:0;opacity:0;
    box-shadow:inset 0 0 110px rgba(146,18,22,.52),inset 0 0 28px rgba(255,70,48,.14);
    transition:opacity .18s ease;
  }
  body.pd-low-health #pdCinemaGrade::after{opacity:.72}
  body.pd-title #pdCinemaGrade{opacity:.92}

  /* Layering is explicit so VFX can glow above the grade while HUD remains razor readable. */
  #overlay{z-index:50!important}
  header,#bossHud,#playerHud,#cue,#toast,#attackHud,#pbResolve,#pbChain,#mbBreakHud{z-index:20!important}
  #controls{z-index:24!important}

  /* Title screen — quiet premium materials instead of bright flat blocks. */
  #overlay{
    background:
      radial-gradient(circle at 68% 42%,rgba(42,75,91,.18),transparent 30%),
      radial-gradient(circle at 30% 68%,rgba(142,91,35,.12),transparent 34%),
      linear-gradient(110deg,rgba(3,7,12,.97),rgba(8,15,23,.90) 50%,rgba(3,7,12,.80))!important;
    backdrop-filter:blur(5px) saturate(.82)!important;
  }
  #overlay::before{
    content:"";position:absolute;inset:max(8px,env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) max(8px,env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));
    border:1px solid rgba(221,232,238,.09);pointer-events:none;
    box-shadow:inset 0 0 80px rgba(0,0,0,.18);
  }
  #overlay .panel{
    position:relative!important;
    background:linear-gradient(118deg,rgba(10,18,27,.95),rgba(12,24,34,.79) 72%,rgba(18,27,34,.60))!important;
    border:1px solid rgba(226,233,237,.12)!important;
    border-left:3px solid var(--pd-gold)!important;
    box-shadow:0 24px 80px rgba(0,0,0,.42),inset 0 1px rgba(255,255,255,.05)!important;
    backdrop-filter:blur(14px) saturate(.9)!important;
    clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px));
  }
  #overlay .panel::after{
    content:"";position:absolute;left:13px;right:13px;top:10px;height:1px;
    background:linear-gradient(90deg,var(--pd-gold),rgba(245,201,111,.08) 42%,transparent);
    opacity:.6;pointer-events:none;
  }
  #eyebrow{color:#d5b977!important;font-weight:700!important;letter-spacing:.24em!important}
  #title{
    color:#f4f7f8!important;font-weight:850!important;letter-spacing:.10em!important;
    text-shadow:0 6px 28px rgba(0,0,0,.55)!important;
  }
  #title em{color:var(--pd-gold)!important;text-shadow:0 0 28px rgba(245,201,111,.20)!important}
  #description{color:#d5dde1!important}
  #help{
    margin-top:15px!important;padding:10px 12px!important;
    border-top:1px solid rgba(255,255,255,.07);border-bottom:1px solid rgba(255,255,255,.06);
    background:linear-gradient(90deg,rgba(255,255,255,.025),transparent);
  }
  #help p{color:#aeb9c0!important}
  #help b{color:#e7d2a0!important}
  #start{
    position:relative!important;overflow:hidden!important;
    background:linear-gradient(110deg,#d8aa55,#f2ce80 46%,#c99a4b)!important;
    color:#101318!important;border:1px solid #ffe4a299!important;
    box-shadow:0 8px 26px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.58)!important;
    letter-spacing:.08em!important;text-transform:uppercase!important;
  }
  #start::before{
    content:"";position:absolute;inset:0 auto 0 -38%;width:32%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);
    transform:skewX(-18deg);transition:left .32s ease;pointer-events:none;
  }
  #start:active::before{left:108%}
  #modelViewerOpen,#heroineModelToggle{
    background:linear-gradient(145deg,rgba(20,31,40,.96),rgba(8,14,20,.96))!important;
    border:1px solid rgba(221,232,238,.17)!important;color:#d7e0e5!important;
    box-shadow:inset 0 1px rgba(255,255,255,.04),0 6px 18px rgba(0,0,0,.26)!important;
  }

  /* Top system controls are deliberately subordinate to combat information. */
  header button{
    color:#cbd4d9!important;background:linear-gradient(145deg,rgba(13,22,31,.88),rgba(5,10,16,.76))!important;
    border:1px solid rgba(214,226,232,.12)!important;border-radius:3px!important;
    box-shadow:inset 0 1px rgba(255,255,255,.035),0 4px 14px rgba(0,0,0,.30)!important;
    backdrop-filter:blur(9px)!important;
  }
  body.pd-play header{opacity:.78!important}

  /* Boss HUD: compact command-centre strip, no billboard effect. */
  body.pd-play #bossHud{
    box-sizing:border-box!important;padding:8px 11px 10px!important;
    width:min(500px,48vw)!important;
    background:linear-gradient(180deg,rgba(8,15,23,.88),rgba(7,13,20,.63))!important;
    border:1px solid rgba(224,233,237,.12)!important;border-top-color:rgba(240,221,175,.22)!important;
    border-radius:2px!important;box-shadow:0 12px 28px rgba(0,0,0,.28),inset 0 1px rgba(255,255,255,.035)!important;
    backdrop-filter:blur(10px) saturate(.85)!important;
  }
  body.pd-play #bossHud>div:first-child{
    align-items:baseline!important;margin-bottom:6px!important;text-transform:uppercase;
  }
  body.pd-play #bossName{color:#eef2f4!important;font-size:13px!important;font-weight:850!important;letter-spacing:.14em!important}
  body.pd-play #phase{color:#b9a77f!important;font-size:9px!important;font-weight:800!important;letter-spacing:.20em!important}
  body.pd-play #bossHud .bar{
    height:9px!important;padding:1px!important;background:#020509e8!important;
    border:1px solid rgba(238,222,190,.16)!important;border-radius:1px!important;
    box-shadow:inset 0 2px 5px #000!important;
  }
  body.pd-play #bossHP{
    background:linear-gradient(90deg,#7f2027,#c44335 52%,var(--pd-danger-hot))!important;
    box-shadow:inset 0 1px rgba(255,225,214,.42),0 0 12px rgba(211,71,48,.13)!important;
  }
  body.pd-play #bossHud .posture{
    position:relative!important;width:72%!important;height:3px!important;margin:6px auto 0!important;
    background:rgba(2,6,9,.88)!important;border:0!important;
  }
  body.pd-play #posture{
    background:linear-gradient(90deg,#8f642d,var(--pd-gold),#fff0bd)!important;
    box-shadow:0 0 10px rgba(245,201,111,.32)!important;
  }

  /* Player status becomes a small tactical plate rather than loose text over the scene. */
  body.pd-play #playerHud{
    box-sizing:border-box!important;width:178px!important;padding:9px 11px 10px!important;
    background:linear-gradient(112deg,rgba(8,16,24,.84),rgba(8,15,22,.54))!important;
    border-left:2px solid rgba(113,199,187,.72)!important;border-top:1px solid rgba(225,235,239,.08)!important;
    box-shadow:0 10px 28px rgba(0,0,0,.22)!important;backdrop-filter:blur(8px)!important;
  }
  body.pd-play #playerHud span{
    color:#b9c4ca!important;font-weight:750!important;font-size:9px!important;letter-spacing:.20em!important;
  }
  body.pd-play #stats{color:#c8b889!important;font-weight:700!important}
  body.pd-play #playerHud .bar{
    height:8px!important;margin:7px 0 6px!important;background:#020509e8!important;border-color:rgba(201,224,220,.14)!important;
  }
  body.pd-play #playerHP{
    background:linear-gradient(90deg,#376d6c,var(--pd-health),#a7e1ce)!important;
    box-shadow:inset 0 1px rgba(239,255,249,.42),0 0 9px rgba(97,205,189,.12)!important;
  }

  /* Move identification stays near the boss HUD, but reads like a diegetic tactical label. */
  body.pd-play #attackHud{
    border:0!important;border-left:2px solid rgba(215,225,231,.28)!important;
    border-right:2px solid rgba(215,225,231,.12)!important;border-radius:1px!important;
    background:linear-gradient(90deg,transparent,rgba(5,11,17,.80) 14%,rgba(7,14,21,.88) 50%,rgba(5,11,17,.80) 86%,transparent)!important;
    color:#dfe6e9!important;font-weight:750!important;letter-spacing:.10em!important;
    box-shadow:0 6px 18px rgba(0,0,0,.18)!important;
  }
  body.pd-parry-telegraph #attackHud{border-left-color:var(--pd-gold)!important;color:#f2d997!important}
  body.pd-dodge-telegraph #attackHud{border-left-color:var(--pd-cyan)!important;color:#aeefff!important}

  /* The response cue is intentionally off the character silhouette. */
  body.pd-play #cue{
    top:max(94px,calc(env(safe-area-inset-top) + 82px))!important;
    left:max(18px,env(safe-area-inset-left))!important;right:auto!important;
    min-width:142px!important;padding:7px 12px 8px 13px!important;
    border:1px solid rgba(255,255,255,.11)!important;border-left:3px solid currentColor!important;
    background:linear-gradient(90deg,rgba(5,11,17,.92),rgba(7,14,21,.62) 78%,transparent)!important;
    box-shadow:0 9px 24px rgba(0,0,0,.24)!important;backdrop-filter:blur(8px)!important;
    font-size:clamp(13px,1.7vw,17px)!important;line-height:1!important;letter-spacing:.18em!important;
  }
  body.pd-play #cue::before{
    content:"RESPONSE";display:block;margin-bottom:4px;color:#8f9aa1;
    font-size:7px;font-weight:800;letter-spacing:.26em;text-shadow:none;
  }
  body.pd-parry-warning #cue{color:var(--pd-gold-hot)!important;text-shadow:0 0 17px rgba(245,201,111,.52),0 2px 10px #000!important}
  body.pd-dodge-warning #cue{color:var(--pd-cyan-hot)!important;text-shadow:0 0 17px rgba(98,220,255,.50),0 2px 10px #000!important}

  /* Impact messages use the upper-right negative space instead of covering the duel. */
  body.pd-play #toast{
    top:23%!important;left:auto!important;right:max(24px,env(safe-area-inset-right))!important;width:auto!important;
    max-width:42vw!important;padding:6px 10px 7px 12px!important;text-align:right!important;
    font-size:clamp(16px,2.7vw,26px)!important;font-weight:900!important;letter-spacing:.16em!important;
    color:#f5e6bc!important;background:linear-gradient(90deg,transparent,rgba(5,10,16,.48))!important;
    border-right:2px solid rgba(245,201,111,.72)!important;text-shadow:0 3px 14px #000,0 0 18px rgba(245,201,111,.18)!important;
  }

  /* Tactile controls: desaturated metal at rest; response colours are unmistakable but not neon toys. */
  body.pd-play #stick{
    background:
      radial-gradient(circle at 50% 50%,rgba(80,112,122,.12) 0 36%,transparent 37%),
      radial-gradient(circle at 42% 34%,rgba(81,111,119,.24),rgba(9,17,25,.58) 62%,rgba(4,9,14,.72))!important;
    border:1px solid rgba(199,216,220,.18)!important;
    box-shadow:inset 0 0 0 6px rgba(3,8,13,.26),inset 0 0 28px rgba(117,163,171,.06),0 12px 30px rgba(0,0,0,.22)!important;
  }
  body.pd-play #knob{
    background:radial-gradient(circle at 35% 28%,rgba(183,207,207,.56),rgba(61,82,88,.70) 58%,rgba(27,39,45,.88))!important;
    border:1px solid rgba(222,234,231,.30)!important;
    box-shadow:0 5px 14px rgba(0,0,0,.42),inset 0 1px rgba(255,255,255,.24)!important;
  }
  body.pd-play .actions{gap:12px!important}
  body.pd-play .actions button{
    font-weight:850!important;letter-spacing:.02em!important;
    text-shadow:0 2px 8px #000!important;
    box-shadow:inset 0 0 0 4px rgba(5,10,15,.35),inset 0 1px rgba(255,255,255,.16),0 10px 25px rgba(0,0,0,.34)!important;
    backdrop-filter:blur(8px)!important;
  }
  body.pd-play .actions button small{
    margin-top:2px!important;font-size:9px!important;font-weight:800!important;letter-spacing:.16em!important;opacity:.84;
  }
  body.pd-play #attack{
    background:radial-gradient(circle at 36% 25%,rgba(76,94,105,.90),rgba(25,37,46,.95) 58%,rgba(10,16,22,.98))!important;
    border:2px solid rgba(181,197,204,.50)!important;color:#e3eaed!important;
  }
  body.pd-play #parry{
    background:radial-gradient(circle at 36% 24%,rgba(133,101,48,.94),rgba(57,43,24,.97) 58%,rgba(19,18,18,.99))!important;
    border:2px solid #d8ad57!important;color:#ffe5a1!important;
    box-shadow:inset 0 0 0 4px rgba(65,43,16,.46),inset 0 1px rgba(255,242,189,.32),0 0 14px rgba(222,173,75,.13),0 10px 25px rgba(0,0,0,.36)!important;
  }
  body.pd-play #dodge{
    background:radial-gradient(circle at 36% 24%,rgba(42,112,137,.94),rgba(17,54,70,.97) 58%,rgba(12,20,26,.99))!important;
    border:2px solid #52bddd!important;color:#c5f4ff!important;
    box-shadow:inset 0 0 0 4px rgba(6,48,63,.48),inset 0 1px rgba(218,250,255,.29),0 0 14px rgba(72,200,237,.13),0 10px 25px rgba(0,0,0,.36)!important;
  }

  @keyframes pd-aaa-parry{
    from{transform:scale(1.055);filter:brightness(1.06) saturate(1.05)}
    to{transform:scale(1.105);filter:brightness(1.30) saturate(1.18)}
  }
  @keyframes pd-aaa-dodge{
    from{transform:scale(1.055);filter:brightness(1.06) saturate(1.06)}
    to{transform:scale(1.105);filter:brightness(1.31) saturate(1.20)}
  }
  @keyframes pd-aaa-counter{
    0%{transform:scale(1.035);filter:brightness(1.04)}
    100%{transform:scale(1.085);filter:brightness(1.24)}
  }
  body.pd-parry-warning #parry{
    background:radial-gradient(circle at 34% 22%,#d8aa50,#765019 58%,#261d11 100%)!important;
    border-color:var(--pd-gold-hot)!important;color:#fff9d6!important;
    box-shadow:0 0 12px rgba(255,222,132,.84),0 0 34px rgba(238,177,48,.52),inset 0 0 0 4px rgba(112,72,17,.58),inset 0 2px rgba(255,250,216,.66)!important;
    animation:pd-aaa-parry .24s ease-in-out infinite alternate!important;
  }
  body.pd-dodge-warning #dodge{
    background:radial-gradient(circle at 34% 22%,#45a9ca,#17617d 58%,#0b2935 100%)!important;
    border-color:#a4f1ff!important;color:#f1fdff!important;
    box-shadow:0 0 12px rgba(123,232,255,.84),0 0 34px rgba(42,196,239,.50),inset 0 0 0 4px rgba(13,89,113,.58),inset 0 2px rgba(232,253,255,.62)!important;
    animation:pd-aaa-dodge .24s ease-in-out infinite alternate!important;
  }
  body.pd-parry-warning #dodge,
  body.pd-dodge-warning #parry{
    opacity:.32!important;transform:scale(.94)!important;filter:saturate(.56) brightness(.68)!important;animation:none!important;
  }
  body.pd-warning #attack{
    opacity:.40!important;transform:scale(.94)!important;filter:saturate(.46) brightness(.66)!important;
    background:radial-gradient(circle at 36% 25%,#34434c,#19242b 62%,#0a1117)!important;
    border-color:rgba(123,142,151,.38)!important;color:#88979e!important;animation:none!important;
  }

  /* Counter is deliberately white/gold with a cyan edge: a reward state distinct from PARRY/DODGE. */
  body.pd-counter-ready #attack{
    background:radial-gradient(circle at 34% 22%,#f1f5f5,#b8aa82 31%,#5a4930 59%,#16191b 100%)!important;
    border-color:#fff0b8!important;color:#11161a!important;text-shadow:0 1px rgba(255,255,255,.35)!important;
    box-shadow:0 0 14px rgba(255,230,157,.78),0 0 31px rgba(98,220,255,.20),inset 0 0 0 4px rgba(50,42,28,.42),inset 0 2px rgba(255,255,255,.78)!important;
    animation:pd-aaa-counter .27s ease-in-out infinite alternate!important;
  }

  #pdCounterCallout{
    position:fixed;right:max(28px,env(safe-area-inset-right));bottom:max(146px,calc(env(safe-area-inset-bottom) + 126px));
    min-width:158px;padding:8px 13px 9px;pointer-events:none;z-index:23;
    color:#f7efd8;background:linear-gradient(90deg,transparent,rgba(7,13,19,.88) 21%,rgba(8,15,22,.94));
    border-right:3px solid var(--pd-gold);opacity:0;transform:translateY(7px);
    transition:opacity .12s ease,transform .12s ease;box-shadow:0 9px 26px rgba(0,0,0,.24);
    text-align:right;
  }
  #pdCounterCallout::after{
    content:"";position:absolute;right:24px;bottom:-27px;width:1px;height:23px;
    background:linear-gradient(var(--pd-gold),rgba(98,220,255,.20));transform:rotate(18deg);transform-origin:top;
  }
  #pdCounterCallout small{display:block;color:#aeb9bf;font-size:7px;font-weight:850;letter-spacing:.27em}
  #pdCounterCallout b{display:block;margin-top:2px;font-size:14px;letter-spacing:.17em}
  body.pd-counter-ready.pd-play #pdCounterCallout{opacity:1;transform:translateY(0)}
  body.pd-warning #pdCounterCallout,body.pd-title #pdCounterCallout{opacity:0!important}

  @media(max-height:500px) and (orientation:landscape){
    body.pd-play #bossHud{width:min(470px,46vw)!important;padding:6px 9px 8px!important}
    body.pd-play #playerHud{bottom:128px!important;width:164px!important;padding:7px 9px!important}
    body.pd-play #cue{top:max(76px,calc(env(safe-area-inset-top) + 64px))!important}
    body.pd-play #toast{top:23%!important}
    #pdCounterCallout{bottom:max(118px,calc(env(safe-area-inset-bottom) + 103px));right:max(20px,env(safe-area-inset-right));transform-origin:right bottom}
  }
  @media(max-width:760px){
    body.pd-play #bossHud{width:min(420px,52vw)!important}
    body.pd-play #attackHud{width:min(300px,46vw)!important}
    body.pd-play #cue{min-width:124px!important;padding:6px 9px 7px 10px!important;letter-spacing:.13em!important}
    body.pd-play #toast{max-width:38vw!important}
    #pdCounterCallout{min-width:138px;padding:7px 10px 8px}
  }
  @media(orientation:portrait){
    body.pd-play #bossHud{width:min(84vw,460px)!important}
    body.pd-play #attackHud{width:min(72vw,330px)!important}
    body.pd-play #playerHud{bottom:max(176px,calc(env(safe-area-inset-bottom) + 160px))!important}
    body.pd-play #cue{top:max(130px,calc(env(safe-area-inset-top) + 108px))!important}
    body.pd-play #toast{top:20%!important;right:max(16px,env(safe-area-inset-right))!important;max-width:55vw!important}
    #pdCounterCallout{right:max(18px,env(safe-area-inset-right));bottom:max(170px,calc(env(safe-area-inset-bottom) + 150px))}
  }
  `;
  document.head.appendChild(style);

  const grade=document.createElement('div');
  grade.id='pdCinemaGrade';
  grade.setAttribute('aria-hidden','true');
  document.body.appendChild(grade);

  const counter=document.createElement('div');
  counter.id='pdCounterCallout';
  counter.setAttribute('aria-hidden','true');
  counter.innerHTML='<small>COUNTER WINDOW</small><b>STRIKE NOW</b>';
  document.body.appendChild(counter);

  function syncPresentationState(){
    let low=false;
    try{
      low=document.body.classList.contains('pd-play')&&typeof player!=='undefined'&&player&&Number.isFinite(player.hp)&&player.hp>0&&player.hp<=30;
    }catch(_){/* load-order safe */}
    document.body.classList.toggle('pd-low-health',low);
    requestAnimationFrame(syncPresentationState);
  }
  requestAnimationFrame(syncPresentationState);
})();
