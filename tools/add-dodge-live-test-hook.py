from pathlib import Path
p=Path('dist/dodge-system-v1.js')
s=p.read_text()
old="let dodgeQueued=false,dodgeTimer=0,dodgeIFrame=0,dodgeCool=0,dodges=0,perfectDodges=0,dodgeSide=1;"
new=old+"\n let testForcedMove=null;\n const dodgeTestMode=new URLSearchParams(location.search).has('dodgecheck');"
if 'const dodgeTestMode=' not in s:
    if old not in s: raise SystemExit('state anchor missing')
    s=s.replace(old,new,1)
old_block="""startEnemyAttack=function(move){
  const extras=EXTRA_DODGE_MOVES[level]||[];
  if(extras.length&&boss&&boss.sequence%3===2){
   move=extras[Math.floor(boss.sequence/3)%extras.length];
  }
  return dodgeStartEnemyAttackBase(move);
 };"""
new_block="""startEnemyAttack=function(move){
  const extras=EXTRA_DODGE_MOVES[level]||[];
  if(testForcedMove){move=testForcedMove;testForcedMove=null;}
  else if(extras.length&&boss&&boss.sequence%3===2){
   move=extras[Math.floor(boss.sequence/3)%extras.length];
  }
  return dodgeStartEnemyAttackBase(move);
 };"""
if new_block not in s:
    if old_block not in s: raise SystemExit('startEnemyAttack anchor missing')
    s=s.replace(old_block,new_block,1)
anchor=""" if(window.parryDoll?.snapshot){
"""
hook=""" if(dodgeTestMode){
  window.parryDodgeTest={
   catalog:()=>EXTRA_DODGE_MOVES.map(group=>group.map(m=>({name:m.name,response:m.response,kind:m.kind,shape:m.shape}))),
   placeAtCombatRange:()=>{
    if(mode!=='play'||!player||!boss)return false;
    const fromBoss=norm(V(player.pos.x-boss.pos.x,0,player.pos.z-boss.pos.z));
    const desired=add(boss.pos,mul(fromBoss,2.15)),delta=sub(desired,player.pos);
    player.pos=desired;player.vel=V();boss.vel=V();
    for(const n of player.nodes){n.p=add(n.p,delta);n.prev=add(n.prev,delta)}
    player.face=Math.atan2(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z);
    boss.face=Math.atan2(player.pos.x-boss.pos.x,player.pos.z-boss.pos.z);boss.aim=boss.face;
    return true;
   },
   forceAttack:(response)=>{
    if(mode!=='play'||!boss||boss.hp<=0||boss.wind>0||boss.strike>0||boss.stun>0||boss.down>0)return false;
    const extras=EXTRA_DODGE_MOVES[level]||[],normals=(ENEMY_MOVES[level]||[]).filter(m=>m.response!=='dodge');
    const move=response==='dodge'?extras[0]:response==='parry'?normals[0]:null;
    if(!move)return false;
    testForcedMove=move;boss.ai=0;
    startEnemyAttack(move);
    return true;
   }
  };
 }

"""
if 'window.parryDodgeTest=' not in s:
    if anchor not in s: raise SystemExit('snapshot anchor missing')
    s=s.replace(anchor,hook+anchor,1)
p.write_text(s)
print('dodge live test hook patched')
