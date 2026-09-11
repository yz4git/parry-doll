'use strict';
// MIRROR BREAK final adapter — run presentation + guaranteed core mirroring after adaptive secret-AI selection.
(()=>{
 if(window.__parryMirrorBreakFinalAdapterLoaded)return;window.__parryMirrorBreakFinalAdapterLoaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const eyebrow=document.getElementById('eyebrow'),desc=document.getElementById('description'),help=document.getElementById('help');
 if(eyebrow)eyebrow.textContent='MIRROR BREAK • BODY BREAK • DOLL CORE';
 if(desc)desc.innerHTML='完璧に弾き、部位を砕き、その力を奪え。<br>最後に待つのは、育てた自分自身。';
 if(help){const rows=help.querySelectorAll('p');if(rows[2])rows[2].innerHTML='<b>弾く</b> PERFECTで弱点露出 → 反撃でBODY BREAK';if(rows[3])rows[3].textContent='敵撃破後にDOLL COREを選択。取得した力は最終戦の傀儡零式にもコピーされる。'}
 const badge=document.createElement('div');badge.id='mbRunBadge';badge.textContent='MIRROR BREAK';Object.assign(badge.style,{position:'absolute',left:'50%',bottom:'max(8px, env(safe-area-inset-bottom))',transform:'translateX(-50%)',zIndex:'25',pointerEvents:'none',fontSize:'8px',letterSpacing:'3px',color:'#b9a97f',opacity:'.62',textShadow:'0 2px 8px #000'});document.body.appendChild(badge);

 const cleanStyle=document.createElement('style');cleanStyle.textContent=`
 body:has(#mbBreakHud.exposed) #pbDanger{opacity:0!important;transform:translateX(-50%) scale(.96)!important}
 #mbBreakHud.exposed~#pbDanger{opacity:0!important}
 `;document.head.appendChild(cleanStyle);

 const baseAnnounce=announce;announce=function(text,duration){if(String(text||'').replace(/\s/g,'').includes('弱点露出'))return;return baseAnnounce(text,duration)};
 function simplifyParryLabels(){
  const danger=document.getElementById('pbDanger');if(danger?.textContent?.includes('BREAK CHANCE'))danger.classList.remove('show');
  for(const el of document.querySelectorAll('body *')){
   const text=(el.textContent||'').trim();if(!text.includes('COUNTER READY')||!text.includes('PERFECT PARRY'))continue;
   const child=[...el.querySelectorAll('small,span,em')].find(n=>(n.textContent||'').trim()==='PERFECT PARRY');if(child)child.textContent='';
  }
 }
 const uiEnemyImpact=enemyImpact;enemyImpact=function(move=null){const before=parries,beforePerfect=perfects,out=uiEnemyImpact(move);if(parries>before){simplifyParryLabels();requestAnimationFrame(simplifyParryLabels);setTimeout(simplifyParryLabels,60);const fx=document.getElementById('combat-fx-v2');if(fx){const token=String((Number(fx.dataset.mbFadeToken)||0)+1);fx.dataset.mbFadeToken=token;fx.style.opacity=perfects>beforePerfect?'.68':'.78';fx.style.transition='opacity 70ms linear';setTimeout(()=>{if(fx.dataset.mbFadeToken===token)fx.style.opacity='1'},perfects>beforePerfect?245:190)}}return out};

 function dominant(saved){const max=Math.max(saved.EDGE,saved.MIRROR,saved.PULSE);if(max<=0)return null;if(saved.EDGE===max)return'EDGE';if(saved.MIRROR===max)return'MIRROR';return'PULSE'}
 function mirror(move,saved){if(!move)return move;const m={...move,hits:[...(move.hits||[])]},d=dominant(saved);if(d==='EDGE'){m.name=m.name.startsWith('写刃・')?m.name:'写刃・'+m.name;m.damage*=1+.055*saved.EDGE;m.speed*=1+.035*saved.EDGE}else if(d==='MIRROR'){m.name=m.name.startsWith('遅鏡・')?m.name:'遅鏡・'+m.name;m.wind*=1+.11*saved.MIRROR;m.recover*=.88;m.hits=m.hits.map((h,i)=>h+i*.035*saved.MIRROR)}else if(d==='PULSE'){m.name=m.name.startsWith('脈動・')?m.name:'脈動・'+m.name;m.force*=1+.10*saved.PULSE;m.range*=1+.035*saved.PULSE}return m}
 const baseStart=startEnemyAttack;startEnemyAttack=function(move){if(level!==4||!ENEMY_MOVES[4]?.length)return baseStart(move);const saved={...state.cores},originals=ENEMY_MOVES[4].slice(),adapted=originals.map(m=>mirror(m,saved));ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...adapted);state.cores.EDGE=state.cores.MIRROR=state.cores.PULSE=0;try{return baseStart(mirror(move,saved))}finally{state.cores.EDGE=saved.EDGE;state.cores.MIRROR=saved.MIRROR;state.cores.PULSE=saved.PULSE;ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...originals)}};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return {...d,mirrorDominant:dominant(state.cores),finalAdapter:true,uiSimplified:true,perfectFxTrimmed:true}};
})();

// V2/V3/V4/V5/UI/V6/V7 deliberately load after every v1/final wrapper so the newest
// presentation, persistent damage, DOLL CORE styles and final CORE ECHO doctrine compose last.
(()=>{if(window.__parryMirrorBreakV2Queued)return;window.__parryMirrorBreakV2Queued=true;const src=document.currentScript?.src||'',q=src.includes('?')?'?'+src.split('?').slice(1).join('?'):'',s=document.createElement('script');s.src='./mirror-break-v2.js'+q;s.onload=()=>{if(window.__parryMirrorBreakV3Queued)return;window.__parryMirrorBreakV3Queued=true;const v3=document.createElement('script');v3.src='./mirror-break-v3.js'+q;v3.onload=()=>{if(window.__parryMirrorBreakV4Queued)return;window.__parryMirrorBreakV4Queued=true;const v4=document.createElement('script');v4.src='./mirror-break-v4.js'+q;v4.onload=()=>{if(window.__parryMirrorBreakV5Queued)return;window.__parryMirrorBreakV5Queued=true;const v5=document.createElement('script');v5.src='./mirror-break-v5.js'+q;v5.onload=()=>{if(window.__parryMirrorBreakV5UiQueued)return;window.__parryMirrorBreakV5UiQueued=true;const ui=document.createElement('script');ui.src='./mirror-break-v5-ui.js'+q;ui.onload=()=>{if(window.__parryMirrorBreakV6Queued)return;window.__parryMirrorBreakV6Queued=true;const v6=document.createElement('script');v6.src='./mirror-break-v6.js'+q;v6.onload=()=>{if(window.__parryMirrorBreakV7Queued)return;window.__parryMirrorBreakV7Queued=true;const v7=document.createElement('script');v7.src='./mirror-break-v7.js'+q;document.body.appendChild(v7)};document.body.appendChild(v6)};document.body.appendChild(ui)};document.body.appendChild(v5)};document.body.appendChild(v4)};document.body.appendChild(v3)};document.body.appendChild(s)})();
