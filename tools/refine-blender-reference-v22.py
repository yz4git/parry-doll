from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V22' in s:
    print('Blender heroine generator already carries REFERENCE_V22')
    raise SystemExit(0)
if '# REFERENCE_V21' not in s:
    raise SystemExit('REFERENCE_V21 generator required before v2.2')
s=s.replace('# REFERENCE_V21: solid scalp coverage and panel-based fringe.','# REFERENCE_V21: solid scalp coverage and panel-based fringe.\n# REFERENCE_V22: eye-clear tapered fringe proportions.',1)

a=s.index('# Five overlapping panel bangs create a solid, readable fringe')
b=s.index('# Longer side fringe frames',a)
fringe="""# Five overlapping panel bangs stay above/around the eyes; the center lock is only slightly longer.
bang_z=face_z+.018
add_panel(HEAD,'BangOuterL',[(-.138,.096,bang_z),(-.078,.108,bang_z),(-.084,.032,bang_z),(-.126,.012,bang_z)],.0056,HAIR)
add_panel(HEAD,'BangInnerL',[(-.096,.108,bang_z),(-.026,.116,bang_z),(-.036,.016,bang_z),(-.070,-.002,bang_z)],.0058,HAIR_HI)
add_panel(HEAD,'BangCenter',[(-.038,.118,bang_z),(.028,.116,bang_z),(.016,-.014,bang_z),(-.014,-.026,bang_z)],.0060,HAIR)
add_panel(HEAD,'BangInnerR',[(.022,.116,bang_z),(.094,.106,bang_z),(.068,-.002,bang_z),(.034,.016,bang_z)],.0058,HAIR_HI)
add_panel(HEAD,'BangOuterR',[(.076,.108,bang_z),(.138,.094,bang_z),(.126,.010,bang_z),(.084,.032,bang_z)],.0056,HAIR)
# Two fine tapered center-side locks break the silhouette without masking the eyes.
add_ribbon(HEAD,'BangTipL',[(-.057,.050,bang_z+.003),(-.050,.020,bang_z+.004),(-.046,-.010,bang_z+.002)],[.016,.011,.004],.0032,HAIR)
add_ribbon(HEAD,'BangTipR',[(.057,.050,bang_z+.003),(.050,.020,bang_z+.004),(.046,-.008,bang_z+.002)],[.016,.011,.004],.0032,HAIR)
"""
s=s[:a]+fringe+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V22: eye-clear tapered fringe proportions')
