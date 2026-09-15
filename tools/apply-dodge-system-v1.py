from pathlib import Path


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text()
    if new in text:
        print(f'{label}: already applied')
        return
    if old not in text:
        raise SystemExit(f'{label}: target not found in {path}')
    p.write_text(text.replace(old,new,1))
    print(f'{label}: applied')

# Let the core and combat director see the newly appended dodge-only moves.
replace_once(
    'dist/game.js',
    "boss.face=facing;const move=ENEMY_MOVES[level][boss.sequence%4],startRange=",
    "boss.face=facing;const move=ENEMY_MOVES[level][boss.sequence%ENEMY_MOVES[level].length],startRange=",
    'core dynamic enemy move count'
)

# Load the dodge system immediately after the base game and before later wrappers.
replace_once(
    'dist/index.html',
    "script.onload=()=>{\n    const upgrades=document.createElement('script');",
    "script.onload=()=>{\n    const dodgeSystem=document.createElement('script');\n    dodgeSystem.src='./dodge-system-v1.js?v='+version;\n    dodgeSystem.onload=()=>{\n    const upgrades=document.createElement('script');",
    'index dodge loader open'
)
replace_once(
    'dist/index.html',
    "    document.body.appendChild(upgrades);\n  };\n  document.body.appendChild(script);",
    "    document.body.appendChild(upgrades);\n    };\n    document.body.appendChild(dodgeSystem);\n  };\n  document.body.appendChild(script);",
    'index dodge loader close'
)
replace_once(
    'dist/index.html',
    "<p><b>弾く</b> パリィ / K　金色の合図に合わせる</p>",
    "<p><b>弾く</b> パリィ / K　金色の◇攻撃に合わせる</p><p><b>避ける</b> DODGE / L　シアンの≫攻撃は回避専用</p>",
    'title help dodge explanation'
)

# Director must score every move, including the two added dodge moves per boss.
replace_once(
    'dist/combat-director-v2.js',
    "const state={boss:null,level:-1,last:-1,prev:-1,plans:0,counts:[0,0,0,0],lastKind:'',phase:1};",
    "const state={boss:null,level:-1,last:-1,prev:-1,plans:0,counts:[],lastKind:'',lastResponse:'',phase:1};",
    'director dynamic state'
)
replace_once(
    'dist/combat-director-v2.js',
    "function resetState(){state.boss=boss;state.level=level;state.last=state.prev=-1;state.plans=0;state.counts=[0,0,0,0];state.lastKind='';state.phase=phaseNow()}",
    "function resetState(){state.boss=boss;state.level=level;state.last=state.prev=-1;state.plans=0;state.counts=Array(ENEMY_MOVES[level]?.length||4).fill(0);state.lastKind='';state.lastResponse='';state.phase=phaseNow()}",
    'director reset counts'
)
replace_once(
    'dist/combat-director-v2.js',
    "score-=state.counts[i]*.11;\n   if(kind===state.lastKind)score-=.55;",
    "score-=(state.counts[i]||0)*.11;\n   if(kind===state.lastKind)score-=.55;\n   const response=m.response||'parry';\n   if(response==='dodge')score+=state.lastResponse==='dodge'?-1.10:.62;\n   else if(state.lastResponse==='dodge')score+=.28;",
    'director response alternation scoring'
)
replace_once(
    'dist/combat-director-v2.js',
    "state.prev=state.last;state.last=idx;state.lastKind=moves[idx]?.kind||'';state.counts[idx]++;state.plans++;state.phase=phaseNow()",
    "state.prev=state.last;state.last=idx;state.lastKind=moves[idx]?.kind||'';state.lastResponse=moves[idx]?.response||'parry';state.counts[idx]=(state.counts[idx]||0)+1;state.plans++;state.phase=phaseNow()",
    'director remember response'
)

# Make the existing HUD/cue use the same gold-vs-cyan language as the world telegraph.
replace_once(
    'dist/combat-product-pass.js',
    "#attackHud.show{opacity:1;transform:none}#attackHud.ready{color:#ffd98e}#attackHud.finish{color:#ffe7aa;font-size:clamp(13px,2vw,17px);letter-spacing:3.5px}",
    "#attackHud.show{opacity:1;transform:none}#attackHud.ready{color:#ffd98e}#attackHud.dodge{color:#8eeaff;text-shadow:0 0 12px #28bde8,0 2px 8px #000}#attackHud.finish{color:#ffe7aa;font-size:clamp(13px,2vw,17px);letter-spacing:3.5px}",
    'product dodge hud color'
)
replace_once(
    'dist/combat-product-pass.js',
    "if(boss.wind>0||boss.strike>0){\n  const move=enemyMove(),ready=boss.wind>0&&boss.wind<Math.max(.06,.48-move.hits[0]);\n  p5AttackName.textContent=move.name;p5AttackHud.className='show'+(ready?' ready':'');\n  return;\n }",
    "if(boss.wind>0||boss.strike>0){\n  const move=enemyMove(),ready=boss.wind>0&&boss.wind<Math.max(.06,.48-move.hits[0]),dodge=move.response==='dodge';\n  p5AttackName.textContent=(dodge?'≫ DODGE · ':'◇ PARRY · ')+move.name;p5AttackHud.className='show'+(dodge?' dodge':ready?' ready':'');\n  return;\n }",
    'product response-labelled attack hud'
)
replace_once(
    'dist/combat-product-pass.js',
    "if(boss.wind>0&&boss.wind<Math.max(.06,.48-enemyMove().hits[0]))$('cue').textContent='弾 け';\n  else if(boss.strike>0&&boss.hitIndex<enemyMove().hits.length)$('cue').textContent='続 け て 弾 け';\n  else $('cue').textContent='';",
    "const responseMove=enemyMove(),dodgeOnly=responseMove?.response==='dodge';\n  if(dodgeOnly&&(boss.wind>0||boss.strike>0))$('cue').textContent='≫ 避 け ろ ≫';\n  else if(boss.wind>0&&boss.wind<Math.max(.06,.48-responseMove.hits[0]))$('cue').textContent='◇ 弾 け ◇';\n  else if(boss.strike>0&&boss.hitIndex<responseMove.hits.length)$('cue').textContent='◇ 続 け て 弾 け ◇';\n  else $('cue').textContent='';",
    'product response cue'
)

print('dodge system patch complete')
