from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V24' in s:
    print('Blender heroine generator already carries REFERENCE_V24')
    raise SystemExit(0)
if '# REFERENCE_V23' not in s:
    raise SystemExit('REFERENCE_V23 generator required before v2.4')
s=s.replace('# REFERENCE_V23: projected portrait features for reliable front/profile readability.','# REFERENCE_V23: projected portrait features for reliable front/profile readability.\n# REFERENCE_V24: eyebrow-height fringe with open eye line.',1)

# Lift the broad bang panels above the eye plates. Keep only one narrow center lock between the eyes.
a=s.index('# Five overlapping panel bangs stay above/around the eyes;')
b=s.index('# Longer side fringe frames',a)
fringe="""# Broad fringe now terminates above the eye line; only the narrow center lock drops between the eyes.
bang_z=face_z+.018
add_panel(HEAD,'BangOuterL',[(-.138,.100,bang_z),(-.078,.112,bang_z),(-.082,.058,bang_z),(-.128,.046,bang_z)],.0056,HAIR)
add_panel(HEAD,'BangInnerL',[(-.096,.112,bang_z),(-.028,.120,bang_z),(-.036,.057,bang_z),(-.072,.050,bang_z)],.0058,HAIR_HI)
add_panel(HEAD,'BangCenter',[(-.028,.121,bang_z),(.024,.120,bang_z),(.014,.012,bang_z),(-.010,-.004,bang_z)],.0060,HAIR)
add_panel(HEAD,'BangInnerR',[(.026,.120,bang_z),(.096,.110,bang_z),(.072,.050,bang_z),(.036,.057,bang_z)],.0058,HAIR_HI)
add_panel(HEAD,'BangOuterR',[(.078,.112,bang_z),(.138,.098,bang_z),(.128,.046,bang_z),(.082,.058,bang_z)],.0056,HAIR)
# Fine temple tips sit outside the eye centers and stop at the upper lash line.
add_ribbon(HEAD,'BangTipL',[(-.094,.072,bang_z+.003),(-.088,.052,bang_z+.004),(-.082,.038,bang_z+.002)],[.014,.009,.0035],.0032,HAIR)
add_ribbon(HEAD,'BangTipR',[(.094,.072,bang_z+.003),(.088,.052,bang_z+.004),(.082,.038,bang_z+.002)],[.014,.009,.0035],.0032,HAIR)
"""
s=s[:a]+fringe+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V24: eyebrow-height fringe with open eye line')
