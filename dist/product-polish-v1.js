'use strict';
// Product polish v3 — two-stage response telegraphs: identify early, press only inside the real success window.
(()=>{
 if(window.__parryProductPolishV1Loaded)return;
 window.__parryProductPolishV1Loaded=true;

 const style=document.createElement('style');
 style.textContent=`
 /* Title/result presentation: battle UI must never leak behind the panel. */
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

 /* Combat hierarchy: boss identity + HP is the only persistent information in the upper centre. */
 body.pd-play #responseLegend,
 body.pd-play #dodgeCue,
 body.pd-play #pbDanger,
 body.pd-play #mbCores,
 body.pd-play #pbPhaseStrip{display:none!important}
 body.pd-play .brand{display:none!important}
 body.pd-play header{
   left:auto!important;right:max(22px,env(safe-area-inset-right))!important;width:auto!important;
   gap:8px!important;opacity:.72!important;z-index:12!important;
 }
 body.pd-play header button{
   min-width:42px!important;padding:7px 10px!important;background:#0a1118b8!important;
   border-color:#ffffff20!important;box-shadow:0 3px 12px #0005!important;font-size:12px!important;
 }
 body.pd-play #bossHud{
   top:max(15px,env(safe-area-inset-top))!important;left:50%!important;transform:translateX(-50%)!important;
   width:min(410px,44vw)!important;z-index:10!important;filter:drop-shadow(0 3px 8px #000a)!important;
 }
 body.pd-play #bossHud>div:first-child{margin-bottom:5px!important;font-size:13px!important;letter-spacing:1.5px!important}
 body.pd-play #bossName{font-weight:760!important;text-shadow:0 2px 8px #000!important}
 body.pd-play #phase{font-size:10px!important;letter-spacing:1.4px!important;color:#d4c7aa!important}
 body.pd-play #bossHud .bar{height:8px!important}
 body.pd-play #bossHud .posture{margin-top:5px!important;opacity:.86!important}

 /* Move name is transient and gets its own row below the health bar instead of colliding with phase/name text. */
 body.pd-play #attackHud{
   position:fixed!important;top:max(68px,calc(env(safe-area-inset-top) + 53px))!important;
   left:50%!important;right:auto!important;width:min(320px,48vw)!important;height:22px!important;
   transform:translateX(-50%)!important;justify-content:center!important;padding:0 10px!important;
   border:1px solid #ffffff24!important;color:#dce2e5!important;background:linear-gradient(90deg,transparent,#071019d8 16%,#071019d8 84%,transparent)!important;
   box-shadow:none!important;text-shadow:0 2px 8px #000!important;z-index:11!important;
 }
 body.pd-play #attackHud small{color:#aab3b8!important}
 body.pd-parry-telegraph #attackHud{
   border-color:#ffd36b7a!important;color:#ffe39a!important;box-shadow:0 0 12px #ffd36b33!important;
 }
 body.pd-dodge-telegraph #attackHud{
   border-color:#67ddff7a!important;color:#9aeaff!important;box-shadow:0 0 12px #67ddff33!important;
 }

 /* Secondary systems only appear when they actually matter. */
 body.pd-play #mbBreakHud{opacity:0!important;transform:translateX(-50%) scale(.94)!important}
 body.pd-play #mbBreakHud.exposed{opacity:1!important;transform:translateX(-50%) scale(1.02)!important}
 body.pd-play #mbBreakHud.broken{opacity:.28!important}
 body.pd-play #pbResolve{opacity:.74!important}
 body.pd-play #pbChain{z-index:12!important}

 /* Main on-field instruction. Gold = PARRY, cyan = DODGE, only while reading a wind-up. */
 body.pd-play #cue{
   top:102px!important;left:max(24px,env(safe-area-inset-left))!important;right:auto!important;width:auto!important;
   padding:5px 10px!important;border-left:2px solid currentColor!important;border-radius:2px!important;
   background:linear-gradient(90deg,#071019c7,#07101955 78%,transparent)!important;
   text-align:left!important;font-size:clamp(13px,1.9vw,17px)!important;font-weight:900!important;
   letter-spacing:3.5px!important;line-height:1.05!important;transition:color .06s,text-shadow .06s,opacity .08s!important;
   z-index:13!important;
 }
 body.pd-play:not(.pd-warning) #cue{opacity:0!important}
 body.pd-parry-warning #cue{color:#ffd36b!important;text-shadow:0 0 20px #d49a22cc,0 3px 12px #000!important}
 body.pd-dodge-warning #cue{color:#67ddff!important;text-shadow:0 0 20px #159dcacc,0 3px 12px #000!important}

 /* Response buttons always carry their response colour.
    The actionable window adds a much stronger pulse, not the first appearance of colour. */
 @keyframes pd-response-pulse{
   from{filter:brightness(1.06) saturate(1.08)}
   to{filter:brightness(1.34) saturate(1.28)}
 }
 body.pd-play #parry,
 body.pd-play #dodge{
   text-shadow:0 2px 7px #000!important;
   transition:transform .08s,border-color .08s,color .08s,background .08s,box-shadow .08s,opacity .08s,filter .08s!important;
 }
 body.pd-play #parry{
   background:radial-gradient(circle at 38% 26%,#71582fe8,#2b261be8 62%,#171b20f2)!important;
   border:2px solid #caa554!important;color:#ffe6a0!important;
   box-shadow:inset 0 0 0 4px #4a351f45,inset 0 1px #fff1bc4d,0 0 13px #d8a93b28,0 5px 20px #0008!important;
 }
 body.pd-play #dodge{
   background:radial-gradient(circle at 38% 26%,#245d72e8,#123342e8 62%,#151d24f2)!important;
   border:2px solid #4ebbd9!important;color:#bff3ff!important;
   box-shadow:inset 0 0 0 4px #0b39484d,inset 0 1px #d9fbff4d,0 0 13px #48c8ed28,0 5px 20px #0008!important;
 }
 body.pd-play #dodge.ready{
   box-shadow:inset 0 0 0 4px #0b39484d,inset 0 1px #d9fbff4d,0 0 13px #48c8ed28,0 5px 20px #0008!important;
 }
 body.pd-parry-warning #parry{
   background:radial-gradient(circle at 36% 24%,#b48a3ff2,#604414f2 58%,#2a2217f5)!important;
   border-color:#ffe28a!important;color:#fff7cb!important;
   box-shadow:0 0 16px #ffd36bcc,0 0 38px #ffbf35a8,inset 0 0 0 4px #7b581b88,inset 0 2px #fff9d6b8!important;
   transform:scale(1.11)!important;
   animation:pd-response-pulse .24s ease-in-out infinite alternate!important;
 }
 body.pd-dodge-warning #dodge{
   background:radial-gradient(circle at 36% 24%,#3f9fc2f2,#15536bf2 58%,#112b36f5)!important;
   border-color:#8bedff!important;color:#effdff!important;
   box-shadow:0 0 16px #67ddffcc,0 0 38px #33c9ffa8,inset 0 0 0 4px #12627d88,inset 0 2px #eaffffb8!important;
   transform:scale(1.11)!important;
   animation:pd-response-pulse .24s ease-in-out infinite alternate!important;
 }
 body.pd-parry-warning #dodge,
 body.pd-dodge-warning #parry{opacity:.40!important;transform:scale(.94)!important;filter:saturate(.72) brightness(.78)!important;animation:none!important}

 @keyframes pd-counter-pulse{
   from{filter:brightness(1.02) saturate(1.05);transform:scale(1.045)}
   to{filter:brightness(1.26) saturate(1.22);transform:scale(1.09)}
 }
 body.pd-counter-ready #attack{
   background:radial-gradient(circle at 38% 26%,#8a395eef,#3d1c2def 62%,#171b20f2)!important;
   border-color:#ff8fbd!important;color:#ffe5f1!important;
   box-shadow:0 0 16px #ff6aa0aa,0 0 32px #ff4f8a55,inset 0 0 0 4px #6b23445f,inset 0 2px #fff0f6a8!important;
   animation:pd-counter-pulse .28s ease-in-out infinite alternate!important;
 }

 @media(max-height:500px){
   body.pd-play #bossHud{top:max(12px,env(safe-area-inset-top))!important}
   body.pd-play #attackHud{top:max(64px,calc(env(safe-area-inset-top) + 50px))!important}
 }
 @media(max-width:760px){
   body.pd-play #bossHud{width:min(380px,43vw)!important}
   body.pd-play #attackHud{width:min(290px,45vw)!important;font-size:11px!important}
   body.pd-play header{gap:5px!important}
   body.pd-play header button{padding:6px 8px!important}
 }
 `;
 document.head.appendChild(style);

 let secretLabel=null;
 function findSecretLabel(){
   if(secretLabel?.isConnected)return secretLabel;
   secretLabel=[...document.querySelectorAll('div,span,small')].find(el=>el.children.length===0&&el.textContent?.trim()==='MIRROR BREAK')||null;
   return secretLabel;
 }

 function updateState(){
   const overlay=document.getElementById('overlay');
   const panelVisible=!!overlay&&!overlay.classList.contains('hidden');
   let playing=false,active=false,ready=false,isDodge=false,isParry=false,secret=false,counterReady=false;
   try{
     playing=typeof mode!=='undefined'&&mode==='play';
     secret=playing&&typeof level!=='undefined'&&level===4;
     counterReady=!!(playing&&typeof player!=='undefined'&&player&&player.hp>0&&player.counter>0&&typeof boss!=='undefined'&&boss&&boss.hp>0);
     active=!!(playing&&typeof boss!=='undefined'&&boss&&boss.hp>0&&(boss.wind>0||boss.strike>0));
     if(active)counterReady=false;
     const move=active&&typeof enemyMove==='function'?enemyMove():null;
     isDodge=!!(active&&move?.response==='dodge');
     isParry=!!(active&&!isDodge);
     if(active&&move){
       const hits=Array.isArray(move.hits)?move.hits:[.15];
       const next=Math.min(Math.max(0,boss.hitIndex||0),Math.max(0,hits.length-1));
       const timeToHit=boss.wind>0?boss.wind+(hits[0]??.15):Math.max(0,(hits[next]??0)-(boss.strikeElapsed||0));
       // Leave execution margin for mobile touch dispatch. Early colour teaches the response;
       // the strong button/cue only appears when pressing now can actually succeed.
       ready=timeToHit<=(isDodge?.30:.44);
     }
   }catch(_){/* load-order safe */}
   document.body.classList.toggle('pd-title',panelVisible||!playing);
   document.body.classList.toggle('pd-play',playing&&!panelVisible);
   document.body.classList.toggle('pd-warning',ready&&!panelVisible);
   document.body.classList.toggle('pd-dodge-telegraph',isDodge&&!panelVisible);
   document.body.classList.toggle('pd-parry-telegraph',isParry&&!panelVisible);
   document.body.classList.toggle('pd-dodge-warning',ready&&isDodge&&!panelVisible);
   document.body.classList.toggle('pd-parry-warning',ready&&isParry&&!panelVisible);
   document.body.classList.toggle('pd-secret',secret&&!panelVisible);
   document.body.classList.toggle('pd-counter-ready',counterReady&&!panelVisible);
   const attackSmall=document.querySelector('#attack small');
   if(attackSmall)attackSmall.textContent=counterReady&&!panelVisible?'COUNTER':'ATTACK';
   const label=findSecretLabel();
   if(label)label.style.display=playing&&!secret?'none':'';
   requestAnimationFrame(updateState);
 }
 updateState();
})();
