from pathlib import Path

path = Path('dist/game.js')
s = path.read_text(encoding='utf-8')

old = "const rawDamage=finisher?65:move.damage+(move.counter?14:0),damage=Math.max(1,Math.round(rawDamage*(committedBoss?.55:1)));"
new = "const rawDamage=finisher?65:move.damage+(move.counter?14:0),baseDamage=Math.max(1,Math.round(rawDamage*(committedBoss?.55:1))),normalFloor=Math.ceil(boss.spec.hp*.35),damage=finisher||move.counter?baseDamage:Math.max(0,Math.min(baseDamage,boss.hp-normalFloor));"
if old not in s:
    raise SystemExit('damage target not found')
s = s.replace(old, new, 1)

old = "if(hurt(boss,damage,force,point)){"
new = "if(damage<=0&&!finisher&&!move.counter){boss.stun=0;boss.down=0;boss.posture=Math.min(boss.posture,45);announce('GUARD — 弾いて崩せ',.55);ring(point,'#b9c7d1');player.cool=Math.max(player.cool,.42);return;}\n if(hurt(boss,damage,force,point)){"
if old not in s:
    raise SystemExit('hurt target not found')
s = s.replace(old, new, 1)

old = "boss.posture+=finisher?0:move.counter?19:committedBoss?3:move.combo===2?15:8;"
new = "if(finisher)boss.posture=0;else if(move.counter)boss.posture+=24;else boss.posture=Math.min(45,boss.posture+(committedBoss?1:move.combo===2?4:2));"
if old not in s:
    raise SystemExit('posture target not found')
s = s.replace(old, new, 1)

# Parries are the primary posture engine. Increase them enough that successful defense visibly opens the fight.
old = "boss.posture+=perfect?32:24;"
new = "boss.posture+=perfect?38:30;"
if old not in s:
    raise SystemExit('parry posture target not found')
s = s.replace(old, new, 1)

# Keep the overextension lesson visible when players insist on mashing.
old = "if(overextended){attackBuffer=0;announce('攻 め す ぎ — 弾 け',.7)}"
new = "if(overextended){attackBuffer=0;player.cool+=.22;announce('攻 め す ぎ — 弾 け',.8)}"
if old not in s:
    raise SystemExit('overextension target not found')
s = s.replace(old, new, 1)

path.write_text(s, encoding='utf-8')
print('anti-mash v2 applied')
