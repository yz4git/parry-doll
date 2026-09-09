from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V37' in s:
    print('Blender heroine generator already carries REFERENCE_V37')
    raise SystemExit(0)
if '# REFERENCE_V36' not in s:
    raise SystemExit('REFERENCE_V36 generator required before v3.7')
s=s.replace('# REFERENCE_V36: portrait anatomy rebuild, larger almond eyes and dark layered forehead locks.','# REFERENCE_V36: portrait anatomy rebuild, larger almond eyes and dark layered forehead locks.\n# REFERENCE_V37: separate skull width from hair span and retarget portrait features to the narrower face.',1)

# The measured head span includes hair. Keep hair on head_w, but narrow only the connected skull shell.
a=s.index("add_anatomical_head(HEAD,'HeadShellV36',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_anatomical_head(HEAD,'HeadShellV37',[
 (-.140,head_w*.052,head_d*.142,head_d*.192,.052),
 (-.130,head_w*.120,head_d*.194,head_d*.252,.046),
 (-.117,head_w*.195,head_d*.250,head_d*.310,.038),
 (-.101,head_w*.260,head_d*.294,head_d*.356,.031),
 (-.082,head_w*.315,head_d*.336,head_d*.400,.023),
 (-.058,head_w*.365,head_d*.374,head_d*.442,.014),
 (-.031,head_w*.410,head_d*.408,head_d*.474,.006),
 (-.003,head_w*.438,head_d*.436,head_d*.492,-.001),
 (.026,head_w*.450,head_d*.456,head_d*.492,-.006),
 (.055,head_w*.442,head_d*.472,head_d*.474,-.011),
 (.083,head_w*.420,head_d*.478,head_d*.444,-.016),
 (.108,head_w*.385,head_d*.470,head_d*.402,-.021),
 (.130,head_w*.335,head_d*.450,head_d*.350,-.026),
 (.148,head_w*.270,head_d*.420,head_d*.290,-.030)
],SKIN,76)
"""
s=s[:a]+head+s[b:]

# Pull the ears inward with the narrower skull while preserving the external hair envelope.
s=s.replace("(side*head_w*.485,-.018,-.014)","(side*head_w*.445,-.018,-.014)",1)

# Retarget the visible portrait to the narrower face. Eyes become larger relative to skin width,
# slightly closer set, with stronger iris/pupil readability and longer upper lash arcs.
a=s.index('# Anatomy v3.6:')
b=s.index('# Hair v3.6:',a)
face=s[a:b]
face=face.replace('eye_x=head_w*.147','eye_x=head_w*.128')
face=face.replace('eye_rx=head_w*.126','eye_rx=head_w*.116')
face=face.replace('eye_ry=.0192','eye_ry=.0210')
face=face.replace("(head_w*.043,.0125,.0029)","(head_w*.046,.0135,.0030)")
face=face.replace("(head_w*.016,.0062,.0019)","(head_w*.017,.0068,.0020)")
face=face.replace("head_w*.102,.020,head_d*.074","head_w*.096,.021,head_d*.072")
face=face.replace("outer+side*head_w*.027","outer+side*head_w*.031")
face=face.replace(".00185,HAIR)",".00205,HAIR)")
face=face.replace(".00145,HAIR)",".00160,HAIR)")
face=face.replace("ex-side*eye_rx*.76,.073","ex-side*eye_rx*.82,.071")
face=face.replace("ex+side*eye_rx*.94,.069","ex+side*eye_rx*1.02,.067")
# A subtle lower lash cue helps the almond opening read at normal game distance without heavy makeup.
needle=" add_strand(HEAD,f'LowerLidV36_{side}',[(inner,eye_y-.001,face_front+.0020),(ex,eye_y-.013,face_front+.0030),(outer,eye_y-.001,face_front+.0020)],.00085,SKIN)\n"
if needle not in face: raise SystemExit('v37 lower-lid anchor missing')
face=face.replace(needle,needle+" add_strand(HEAD,f'LowerLashV37_{side}',[(inner,eye_y-.001,face_front+.0046),(ex,eye_y-.011,face_front+.0050),(outer,eye_y-.001,face_front+.0046)],.00055,HAIR)\n",1)
# Bring mouth features slightly closer to the camera so they survive bright sky lighting.
face=face.replace("head_d*.519)","head_d*.524)")
face=face.replace("head_d*.522)","head_d*.527)")
face=face.replace("head_d*.523)","head_d*.528)")
face=face.replace("head_d*.521)","head_d*.526)")
s=s[:a]+face+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V37: narrower skull inside preserved hair span and retargeted portrait features')
