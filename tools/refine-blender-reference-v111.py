from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V111' in s:
    print('Blender heroine generator already carries REFERENCE_V111')
    raise SystemExit(0)
if '# REFERENCE_V110' not in s:
    raise SystemExit('REFERENCE_V110 generator required before v11.1')

marker='# REFERENCE_V110: fully hidden lower CC0 faces are trimmed after the fade so no intersecting overlay triangles can reappear as chin/neck scallops in three-quarter views.'
if marker not in s:
    raise SystemExit('v11.1 REFERENCE_V110 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V111: the closed head shell compresses only below the jaw anchor, replacing the long UV-sphere bottom cone with a compact under-chin transition while all facial landmarks stay fixed.',1)

old="""def add_anime_head_v60(p,name,mat,segments=96,rings=48):
 # Smooth UV topology replaces row-profile rings that produced horizontal shading bands.
 verts=[]
 top=bpos((0,.179,0));bottom=bpos((0,-.157,0));verts.append(top)
 for r in range(1,rings):
  theta=math.pi*r/rings
  sy=math.cos(theta);rad=math.sin(theta)
  yy=.011+.168*sy
"""
new="""def add_anime_head_v60(p,name,mat,segments=96,rings=48):
 # Smooth UV topology replaces row-profile rings that produced horizontal shading bands.
 verts=[]
 # v11.1 keeps the measured face untouched through the jaw, but shortens the purely structural
 # UV-sphere tail below it.  The mapped bottom remains overlapped by the neck, avoiding any gap.
 jaw_anchor=-.118
 under_chin_scale=.68
 bottom_y=jaw_anchor+(-.157-jaw_anchor)*under_chin_scale
 top=bpos((0,.179,0));bottom=bpos((0,bottom_y,0));verts.append(top)
 for r in range(1,rings):
  theta=math.pi*r/rings
  sy=math.cos(theta);rad=math.sin(theta)
  yy=.011+.168*sy
  render_y=yy if yy>=jaw_anchor else jaw_anchor+(yy-jaw_anchor)*under_chin_scale
"""
if old not in s:
    raise SystemExit('v11.1 HeadShellV60 lower-pole anchor missing')
s=s.replace(old,new,1)

old_append="""   verts.append(bpos((x,yy,z)))
 bottom_idx=len(verts);verts.append(bottom)
"""
new_append="""   verts.append(bpos((x,render_y,z)))
 bottom_idx=len(verts);verts.append(bottom)
"""
if old_append not in s:
    raise SystemExit('v11.1 HeadShellV60 vertex append anchor missing')
s=s.replace(old_append,new_append,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V111: compact lower HeadShell transition with face landmark Y positions frozen')
