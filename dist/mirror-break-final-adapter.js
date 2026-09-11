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
 function dominant(saved){const max=Math.max(saved.EDGE,saved.MIRROR,saved.PULSE);if(max<=0)return null;if(saved.EDGE===max)return'EDGE';if(saved.MIRROR===max)return'MIRROR';return'PULSE'}
 function mirror(move,saved){if(!move)return move;const m={...move,hits:[...(move.hits||[])]},d=dominant(saved);if(d==='EDGE'){m.name=m.name.startsWith('写刃・')?m.name:'写刃・'+m.name;m.damage*=1+.055*saved.EDGE;m.speed*=1+.035*saved.EDGE}else if(d==='MIRROR'){m.name=m.name.startsWith('遅鏡・')?m.name:'遅鏡・'+m.name;m.wind*=1+.11*saved.MIRROR;m.recover*=.88;m.hits=m.hits.map((h,i)=>h+i*.035*saved.MIRROR)}else if(d==='PULSE'){m.name=m.name.startsWith('脈動・')?m.name:'脈動・'+m.name;m.force*=1+.10*saved.PULSE;m.range*=1+.035*saved.PULSE}return m}
 const baseStart=startEnemyAttack;startEnemyAttack=function(move){if(level!==4||!ENEMY_MOVES[4]?.length)return baseStart(move);const saved={...state.cores},originals=ENEMY_MOVES[4].slice(),adapted=originals.map(m=>mirror(m,saved));ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...adapted);state.cores.EDGE=state.cores.MIRROR=state.cores.PULSE=0;try{return baseStart(mirror(move,saved))}finally{state.cores.EDGE=saved.EDGE;state.cores.MIRROR=saved.MIRROR;state.cores.PULSE=saved.PULSE;ENEMY_MOVES[4].splice(0,ENEMY_MOVES[4].length,...originals)}};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{};return {...d,mirrorDominant:dominant(state.cores),finalAdapter:true}};
})();
