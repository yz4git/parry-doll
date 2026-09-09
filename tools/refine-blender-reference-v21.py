from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V21' in s:
    print('Blender heroine generator already carries REFERENCE_V21')
    raise SystemExit(0)
if '# REFERENCE_V20' not in s:
    raise SystemExit('REFERENCE_V20 generator required before v2.1')
s=s.replace('# REFERENCE_V20: fuller bodice curve, longer fringe, deeper ponytail and broader front couture.','# REFERENCE_V20: fuller bodice curve, longer fringe, deeper ponytail and broader front couture.\n# REFERENCE_V21: solid scalp coverage and panel-based fringe.',1)

# Add reliable top/front scalp coverage without bringing the rear scalp over the face.
needle="for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.414,.006,-.030),(head_w*.093,.080,head_d*.150),HAIR,28,18)\n"
insert=needle+"""add_sphere(HEAD,'HairTopCap',(0,.078,-head_d*.105),(head_w*.500,.071,head_d*.405),HAIR,42,24)
add_sphere(HEAD,'HairFrontCrown',(0,.082,head_d*.105),(head_w*.455,.046,head_d*.235),HAIR,38,22)
"""
if needle not in s:raise SystemExit('hair temple anchor not found')
s=s.replace(needle,insert,1)

# Replace the ribbon-teeth fringe with five overlapping silhouette panels.
a=s.index('# Layered bangs cross the forehead')
b=s.index('# Longer side fringe frames',a)
fringe="""# Five overlapping panel bangs create a solid, readable fringe instead of thin vertical teeth.
bang_z=face_z+.018
add_panel(HEAD,'BangOuterL',[(-.145,.092,bang_z),(-.070,.108,bang_z),(-.078,-.004,bang_z),(-.128,-.032,bang_z)],.0060,HAIR)
add_panel(HEAD,'BangInnerL',[(-.092,.108,bang_z),(-.012,.116,bang_z),(-.024,-.030,bang_z),(-.064,-.060,bang_z)],.0062,HAIR_HI)
add_panel(HEAD,'BangCenter',[(-.032,.117,bang_z),(.032,.116,bang_z),(.018,-.048,bang_z),(-.012,-.070,bang_z)],.0064,HAIR)
add_panel(HEAD,'BangInnerR',[(.012,.116,bang_z),(.092,.107,bang_z),(.064,-.060,bang_z),(.024,-.030,bang_z)],.0062,HAIR_HI)
add_panel(HEAD,'BangOuterR',[(.070,.108,bang_z),(.145,.090,bang_z),(.128,-.034,bang_z),(.078,-.004,bang_z)],.0060,HAIR)
# Small broken tips keep the lower edge from reading as a straight helmet line.
add_ribbon(HEAD,'BangTipL',[(-.064,.030,bang_z+.003),(-.055,-.018,bang_z+.004),(-.046,-.074,bang_z+.002)],[.020,.015,.006],.0035,HAIR)
add_ribbon(HEAD,'BangTipR',[(.064,.030,bang_z+.003),(.055,-.018,bang_z+.004),(.046,-.070,bang_z+.002)],[.020,.015,.006],.0035,HAIR)
"""
s=s[:a]+fringe+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V21: solid scalp coverage and panel-based fringe')
