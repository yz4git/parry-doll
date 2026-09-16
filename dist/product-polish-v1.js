'use strict';
// Product polish v1 — reduce HUD noise and reserve gold/cyan for live reaction windows.
(()=>{
 if(window.__parryProductPolishV1Loaded)return;
 window.__parryProductPolishV1Loaded=true;

 const style=document.createElement('style');
 style.textContent=`
 /* Title/result presentation: the battle HUD must not leak behind the panel. */
 body.pd-title header,
 body.pd-title #bossHud,
 body.pd-title #playerHud,
 body.pd-title #controls,
 body.pd-title #cue,
 body.pd-title #toast,
 body.pd-title #responseLegend,
 body.pd-title #pbPhaseStrip,
 body.pd-title #pbDanger,
 body.pd-title #pbBanner,
 body.pd-title #pbResolve,
 body.pd-title #pbChain,
 body.pd-title #mbBreakHud,
 body.pd-title #mbCores,
 body.pd-title #attackHud,
 body.pd-title #dodgeCue{
   opacity:0!important;visibility:hidden!important;pointer-events:none!important;
 }

 /* Keep only one reaction instruction in combat. */
 body.pd-play #responseLegend,
 body.pd-play #dodgeCue,
 body.pd-play #pbDanger,
 body.pd-play #mbCores{display:none!important}
 body.pd-play #mbBreakHud{opacity:0!important;transform:translateX(-50%) scale(.94)!important}
 body.pd-play #mbBreakHud.exposed{opacity:1!important;transform:translateX(-50%) scale(1.02)!important}
 body.pd-play #mbBreakHud.broken{opacity:.32!important}
 body.pd-play .brand small{display:none!important}
 body.pd-play .brand{opacity:.68}
 body.pd-play #pbPhaseStrip{opacity:.58!important}

 /* Main on-field instruction. Gold means PARRY, cyan means DODGE, only while reading a wind-up. */
 body.pd-play #cue{
   top:25%!important;font-size:clamp(18px,3vw,28px)!important;font-weight:900!important;
   letter-spacing:5px!important;line-height:1!important;transition:color .06s,text-shadow .06s,opacity .08s!important;
 }
 body.pd-play:not(.pd-warning) #cue{opacity:0!important}
 body.pd-parry-warning #cue{color:#ffd36b!important;text-shadow:0 0 20px #d49a22cc,0 3px 12px #000!important}
 body.pd-dodge-warning #cue{color:#67ddff!important;text-shadow:0 0 20px #159dcacc,0 3px 12px #000!important}

 /* Enemy move card is secondary; reaction colour is applied only during its actual wind-up. */
 body.pd-play #attackHud{
   border-color:#ffffff24!important;color:#dce2e5!important;background:#071019b8!important;
   box-shadow:none!important;text-shadow:0 2px 8px #000!important;
 }
 body.pd-play #attackHud small{color:#aab3b8!important}
 body.pd-parry-warning #attackHud{
   border-color:#ffd36b99!important;color:#ffe39a!important;box-shadow:0 0 14px #ffd36b44!important;
 }
 body.pd-dodge-warning #attackHud{
   border-color:#67ddff99!important;color:#9aeaff!important;box-shadow:0 0 14px #67ddff44!important;
 }

 /* Response buttons are neutral at rest. The required button alone lights up on a real telegraph. */
 body.pd-play #parry,
 body.pd-play #dodge{
   background:radial-gradient(circle at 40% 28%,#343b42ee,#171d23ed)!important;
   border:2px solid #77828b!important;color:#edf1f3!important;
   box-shadow:inset 0 0 0 4px #0b111755,inset 0 1px #ffffff2e,0 5px 20px #0008!important;
   text-shadow:0 2px 7px #000!important;
   transition:transform .08s,border-color .08s,color .08s,box-shadow .08s,opacity .08s!important;
 }
 body.pd-play #dodge.ready{box-shadow:inset 0 0 0 4px #0b111755,inset 0 1px #ffffff2e,0 5px 20px #0008!important}
 body.pd-parry-warning #parry{
   border-color:#ffd36b!important;color:#fff1b0!important;
   box-shadow:0 0 25px #ffd36b8c,inset 0 0 0 4px #5a431a55,inset 0 1px #fff4bf77!important;
   transform:scale(1.065)!important;
 }
 body.pd-dodge-warning #dodge{
   border-color:#67ddff!important;color:#c6f3ff!important;
   box-shadow:0 0 25px #67ddff88,inset 0 0 0 4px #103b4a66,inset 0 1px #d9f8ff77!important;
   transform:scale(1.065)!important;
 }
 body.pd-parry-warning #dodge,
 body.pd-dodge-warning #parry{opacity:.43!important;transform:scale(.96)!important}

 /* Slightly calmer upper HUD on short iPhone landscapes. */
 @media(max-height:500px){
   body.pd-play #bossHud{top:22px!important}
   body.pd-play #pbPhaseStrip{top:7px!important}
   body.pd-play header{opacity:.80}
   body.pd-play #attackHud{top:16%!important}
 }
 `;
 document.head.appendChild(style);

 function updateState(){
   const overlay=document.getElementById('overlay');
   const panelVisible=!!overlay&&!overlay.classList.contains('hidden');
   let playing=false,predicting=false,isDodge=false,isParry=false,secret=false;
   try{
     playing=typeof mode!=='undefined'&&mode==='play';
     secret=playing&&typeof level!=='undefined'&&level===4;
     const active=playing&&typeof boss!=='undefined'&&boss&&boss.hp>0&&(boss.wind>0||boss.strike>0);
     const move=active&&typeof enemyMove==='function'?enemyMove():null;
     predicting=!!(active&&boss.wind>0);
     isDodge=!!(predicting&&move?.response==='dodge');
     isParry=!!(predicting&&!isDodge);
   }catch(_){/* load-order safe */}
   document.body.classList.toggle('pd-title',panelVisible||!playing);
   document.body.classList.toggle('pd-play',playing&&!panelVisible);
   document.body.classList.toggle('pd-warning',predicting&&!panelVisible);
   document.body.classList.toggle('pd-dodge-warning',isDodge&&!panelVisible);
   document.body.classList.toggle('pd-parry-warning',isParry&&!panelVisible);
   document.body.classList.toggle('pd-secret',secret&&!panelVisible);
   requestAnimationFrame(updateState);
 }
 updateState();
})();
