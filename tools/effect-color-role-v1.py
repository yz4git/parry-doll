from pathlib import Path
import colorsys,re

ROOT=Path('dist')
HEX=re.compile(r'#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?')
RGB=re.compile(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(\s*,\s*[^\)]+)?\)')

EFFECT_FILES={
 'combat-effects-v2.js','combat-polish-v2.js','combat-product-pass.js','combat-readability.js',
 'combat-flow.js','combat-director-v2.js','damage-reactions.js','hit-location-reactions.js',
 'phase-break.js','phase-break-v2.js','phase-break-v3.js','parry-cinematic-v3.js',
 'stage-break.js','stage-break-v2.js','stage-break-v3.js','review-upgrades.js',
 'mirror-break-v1.js','mirror-break-final-adapter.js','mirror-break-v2.js','mirror-break-v3.js',
 'mirror-break-v4.js','mirror-break-v5.js','mirror-break-v5-ui.js','mirror-break-v6.js','mirror-break-v7.js',
 'mirror-break-v8-defeat-presentation.js','mirror-break-v9-boss-destruction.js','mirror-break-v10-stage-destruction.js',
 'mirror-break-v11-scar-mirror.js','mirror-break-v12-destruction-route.js','mirror-break-v13-chain-destruction.js'
}

def reserved_rgb(r,g,b):
    h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255);h*=360
    if s<.22 or v<.28:return None
    if 32<=h<=78:return 'yellow'
    if 165<=h<=250:return 'blue'
    return None

def recolor_triplet(r,g,b):
    kind=reserved_rgb(r,g,b)
    if kind=='yellow': return (255,82,96)
    if kind=='blue': return (255,92,164)
    return None

def recolor_text(text):
    def hx(m):
        s=m.group(0);rgb=s[1:7];a=s[7:] if len(s)>7 else ''
        r,g,b=(int(rgb[i:i+2],16) for i in (0,2,4));n=recolor_triplet(r,g,b)
        if not n:return s
        return '#%02x%02x%02x'%n+a
    def rg(m):
        r,g,b=map(int,m.group(1,2,3));n=recolor_triplet(r,g,b)
        if not n:return m.group(0)
        prefix='rgba' if m.group(4) else 'rgb';tail=m.group(4) or ''
        return f'{prefix}({n[0]},{n[1]},{n[2]}{tail})'
    return RGB.sub(rg,HEX.sub(hx,text))

changed=[]
for name in sorted(EFFECT_FILES):
    p=ROOT/name
    if not p.exists():continue
    old=p.read_text()
    new=recolor_text(old)
    if new!=old:
        p.write_text(new);changed.append(name)

# Core game: recolor only lines that actually create effects, while keeping the PARRY telegraph palette intact.
game=ROOT/'game.js'
text=game.read_text()
lines=[]
for line in text.splitlines(True):
    if any(tok in line for tok in ('burst(','ring(','groundImpact(','impact(','orb(')) and 'drawAttackTelegraph' not in line:
        # The small gold diamond marker is an allowed PARRY telegraph and is not touched here.
        line=recolor_text(line)
    lines.append(line)
new=''.join(lines)
if new!=text:game.write_text(new);changed.append('game.js')

# DODGE blue is reserved for prediction only; dodge start/success feedback becomes magenta-white.
dodge=ROOT/'dodge-system-v1.js'
text=dodge.read_text()
if "const DODGE_SUCCESS='#ff5ca4';" not in text:
    text=text.replace("const CYAN='#67ddff';", "const CYAN='#67ddff';\n const DODGE_SUCCESS='#ff5ca4';")
text=text.replace('ring(player.nodes[0].p,CYAN);sound(', 'ring(player.nodes[0].p,DODGE_SUCCESS);sound(')
text=text.replace('ring(player.nodes[0].p,CYAN);burst(player.nodes[0].p,CYAN,18,5);', 'ring(player.nodes[0].p,DODGE_SUCCESS);burst(player.nodes[0].p,DODGE_SUCCESS,18,5);')
dodge.write_text(text)
if 'dodge-system-v1.js' not in changed:changed.append('dodge-system-v1.js')

# Guardrails: yellow/cyan may remain in the prediction layer, but not in effect-only files.
viol=[]
for name in sorted(EFFECT_FILES):
    p=ROOT/name
    if not p.exists():continue
    t=p.read_text()
    for m in HEX.finditer(t):
        rgb=m.group(0)[1:7];r,g,b=(int(rgb[i:i+2],16) for i in (0,2,4))
        if reserved_rgb(r,g,b):viol.append((name,m.group(0)))
    for m in RGB.finditer(t):
        r,g,b=map(int,m.group(1,2,3))
        if reserved_rgb(r,g,b):viol.append((name,m.group(0)))
if viol:
    raise SystemExit('reserved effect colors remain: '+repr(viol[:30]))

check=dodge.read_text()
assert "const CYAN='#67ddff';" in check
assert "const DODGE_SUCCESS='#ff5ca4';" in check
assert 'rgba(103,221,255' in check
assert 'ring(player.nodes[0].p,DODGE_SUCCESS)' in check
print('changed:',', '.join(changed))
print('effect color roles OK: yellow=PARRY prediction, cyan=DODGE prediction')
