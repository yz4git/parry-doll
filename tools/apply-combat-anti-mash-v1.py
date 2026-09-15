from pathlib import Path

path = Path('dist/game.js')
s = path.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    s = s.replace(old, new, 1)

replace_once(
    "this.sequence=0;this.comboWindow=0;this.counter=0;",
    "this.sequence=0;this.comboWindow=0;this.attackChain=0;this.attackChainTimer=0;this.counter=0;",
    'constructor attack-chain state',
)

old_player_attack = """function playerAttack(){
 if(player.cool>0||player.down>0||player.hp<=0)return false;
 const finisher=boss.broken>0,counter=player.counter>0;
 combo=player.comboWindow>0?(combo+1)%3:0;
 const move=MOVES[combo];player.swing={...move,combo,finisher,counter};
 player.attack=finisher?.68:move.duration;player.swingClock=finisher?.25:move.wind;player.motion=finisher?2:combo;player.motionDuration=player.attack;player.motionContact=player.swingClock;
 player.cool=finisher?.65:move.recover;player.comboWindow=.82;
 player.dash=.13;const v=sub(boss.pos,player.pos);player.face=Math.atan2(v.x,v.z);
 const distance=len(v),u=norm(v),stop=.9+boss.spec.scale*.5;
 const speed=Math.min(finisher?9:move.lunge,Math.max(0,(distance-stop)/.13));
 player.vel.x=u.x*speed;player.vel.z=u.z*speed;
 if(counter)player.counter=0;
 sound(220+combo*80,.12,'triangle',.04);
 return true;
}"""

new_player_attack = """function playerAttack(){
 // A new attack cannot overwrite an active swing. Recovery now starts after the motion,
 // so mashing no longer short-circuits the commitment of each strike.
 if(player.cool>0||player.attack>0||player.down>0||player.hp<=0)return false;
 const finisher=boss.broken>0,counter=player.counter>0;
 if(finisher||counter){player.attackChain=0;player.attackChainTimer=0;player.comboWindow=0}
 else{player.attackChain=player.attackChainTimer>0?player.attackChain+1:1;player.attackChainTimer=1.05}
 combo=player.comboWindow>0?(combo+1)%3:0;
 const move=MOVES[combo],overextended=!finisher&&!counter&&player.attackChain>=3;
 player.swing={...move,combo,finisher,counter,overextended};
 player.attack=finisher?.68:move.duration;player.swingClock=finisher?.25:move.wind;player.motion=finisher?2:combo;player.motionDuration=player.attack;player.motionContact=player.swingClock;
 player.cool=player.attack+(finisher?.65:move.recover)+(overextended?.38:0);player.comboWindow=overextended?0:.86;
 player.dash=.13;const v=sub(boss.pos,player.pos);player.face=Math.atan2(v.x,v.z);
 const distance=len(v),u=norm(v),stop=.9+boss.spec.scale*.5;
 const speed=Math.min(finisher?9:move.lunge,Math.max(0,(distance-stop)/.13));
 player.vel.x=u.x*speed;player.vel.z=u.z*speed;
 if(overextended){attackBuffer=0;announce('攻 め す ぎ — 弾 け',.7)}
 if(counter)player.counter=0;
 sound(220+combo*80,.12,'triangle',.04);
 return true;
}"""
replace_once(old_player_attack, new_player_attack, 'playerAttack')

old_resolve = """function resolveSwing(){
 const move=player.swing;player.swing=null;
 if(!move||player.hp<=0||player.down>0||boss.hp<=0)return;
 slash(player,move);const v=sub(boss.pos,player.pos),distance=len(v),reach=2.15+boss.spec.scale*.55;
 if(distance>reach)return;
 const finisher=move.finisher&&boss.broken>0;
 const point=boss.nodes[move.combo===1?2:1].p;
 const force=mul(norm(v),finisher?55:move.counter?36:move.force);force.y=finisher?20:move.counter?12:move.combo===2?10:3;
 const damage=finisher?65:move.damage+(move.counter?14:0);
 if(hurt(boss,damage,force,point)){
  boss.posture+=finisher?0:move.counter?19:move.combo===2?15:8;
  if(finisher){boss.broken=0;boss.posture=0;if(boss.hp>0)announce('決 着 の 一 撃',1.2);ring(point,'#ffd287');hitstop=.15;shake=.5;sound(65,.5,'sawtooth',.1)}
  else if(move.counter){if(boss.hp>0)announce('弾 き 返 し',.7);ring(point,'#baffee');hitstop=.085;shake=.3;}
 }
}"""

new_resolve = """function resolveSwing(){
 const move=player.swing;player.swing=null;
 if(!move||player.hp<=0||player.down>0||boss.hp<=0)return;
 slash(player,move);const v=sub(boss.pos,player.pos),distance=len(v),reach=2.15+boss.spec.scale*.55;
 if(distance>reach)return;
 const finisher=move.finisher&&boss.broken>0,committedBoss=!finisher&&!move.counter&&(boss.wind>0||boss.strike>0);
 const point=boss.nodes[move.combo===1?2:1].p;
 // Normal combo hits can stagger, but only counters/finishers may launch the boss into a full knockdown.
 const force=mul(norm(v),finisher?55:move.counter?36:Math.min(move.force,23));force.y=finisher?20:move.counter?12:move.combo===2?7:3;
 const rawDamage=finisher?65:move.damage+(move.counter?14:0),damage=Math.max(1,Math.round(rawDamage*(committedBoss?.55:1)));
 if(hurt(boss,damage,force,point)){
  // Once the enemy has committed to a telegraphed attack, blind mashing cannot stun-cancel it.
  if(committedBoss){boss.stun=0;boss.down=0}
  boss.posture+=finisher?0:move.counter?19:committedBoss?3:move.combo===2?15:8;
  if(finisher){boss.broken=0;boss.posture=0;if(boss.hp>0)announce('決 着 の 一 撃',1.2);ring(point,'#ffd287');hitstop=.15;shake=.5;sound(65,.5,'sawtooth',.1)}
  else if(move.counter){if(boss.hp>0)announce('弾 き 返 し',.7);ring(point,'#baffee');hitstop=.085;shake=.3;}
 }
}"""
replace_once(old_resolve, new_resolve, 'resolveSwing')

replace_once(
    "function playerParry(){if(player.parryCool>0||player.down>0||player.hp<=0)return false;player.parry=.56;player.parryCool=.62;player.swing=null;player.attack=0;player.cool=Math.min(player.cool,.1);ring(player.nodes[1].p,'#8de7e0');sound(680,.1,'sine',.025);return true}",
    "function playerParry(){if(player.parryCool>0||player.down>0||player.hp<=0)return false;player.parry=.56;player.parryCool=.62;player.swing=null;player.attack=0;player.cool=Math.min(player.cool,.1);player.attackChain=0;player.attackChainTimer=0;player.comboWindow=0;ring(player.nodes[1].p,'#8de7e0');sound(680,.1,'sine',.025);return true}",
    'playerParry reset',
)

old_enemy_else = """ }else{const force=add(mul(norm(v),move?move.force:boss.spec.scale>2?29:18),V(0,boss.spec.scale>2?11:5,0));hurt(player,Math.round(boss.spec.damage*(move?move.damage:1)),force,player.nodes[boss.sequence%2?2:1].p)}}"""
new_enemy_else = """ }else{const force=add(mul(norm(v),move?move.force:boss.spec.scale>2?29:18),V(0,boss.spec.scale>2?11:5,0)),counterHit=player.attack>0,damageScale=counterHit?1.35:1;if(counterHit)announce('COUNTER HIT — 攻撃を止めて弾け',.75);hurt(player,Math.round(boss.spec.damage*(move?move.damage:1)*damageScale),force,player.nodes[boss.sequence%2?2:1].p)}}"""
replace_once(old_enemy_else, new_enemy_else, 'enemy counter-hit punish')

old_step_head = """function step(dt){time+=dt;for(const d of [player,boss]){for(const k of ['invuln','stun','down','attack','parry','cool','parryCool','comboWindow','counter','broken','dash'])d[k]=Math.max(0,d[k]-dt)}if(mode==='play'){"""
new_step_head = """function step(dt){time+=dt;for(const d of [player,boss]){for(const k of ['invuln','stun','down','attack','parry','cool','parryCool','comboWindow','attackChainTimer','counter','broken','dash'])d[k]=Math.max(0,d[k]-dt)}if(player.attackChainTimer===0)player.attackChain=0;if(mode==='play'){"""
replace_once(old_step_head, new_step_head, 'step attack-chain decay')

path.write_text(s, encoding='utf-8')
print('combat anti-mash v1 patch applied')
