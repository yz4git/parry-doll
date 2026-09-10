from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V70' in s:
    print('Blender heroine generator already carries REFERENCE_V70')
    raise SystemExit(0)
if '# REFERENCE_V69' not in s:
    raise SystemExit('REFERENCE_V69 generator required before v7.0')

s=s.replace(
    '# REFERENCE_V69: sculpted adult-anime portrait planes, tapered jaw and restrained continuous profile.',
    '# REFERENCE_V69: sculpted adult-anime portrait planes, tapered jaw and restrained continuous profile.\n# REFERENCE_V70: volumetric portrait eyes, unified nose form and curved natural lips.',
    1,
)

# Slightly longer lower face and a more tapered adult-anime jaw while keeping the stable UV topology.
s=s.replace("top=bpos((0,.179,0));bottom=bpos((0,-.151,0));verts.append(top)","top=bpos((0,.179,0));bottom=bpos((0,-.161,0));verts.append(top)",1)
s=s.replace("yy=.014+.165*sy","yy=.009+.170*sy",1)
s=s.replace("width=.132*(1.0-.300*lower+.030*cheek)","width=.132*(1.0-.355*lower+.032*cheek)",1)
# Move the orbital bowl to the new eye centres so the eyes read as seated in the skull.
s=s.replace("ex=side*.0415","ex=side*.0475",1)

# Portrait palette: retain the dark limbal ring but make the inner iris warm grey-brown, not metallic grey.
s=s.replace("IRIS=material('Iris',(0.050,0.038,0.040),.01,.52)","IRIS=material('Iris',(0.036,0.028,0.031),.01,.56)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.205,0.150,0.136),.01,.54)","IRIS_INNER=material('Iris Inner',(0.165,0.118,0.108),.01,.58)",1)
s=s.replace("LIP=material('Lip',(0.30,0.105,0.120),0,.68)","LIP=material('Lip',(0.34,0.120,0.140),0,.62)",1)

# Reference-like eye spacing and aspect: large eyes, but no joined goggle silhouette.
s=s.replace('eye_x=.0450','eye_x=.0485',1)
s=s.replace('eye_rx=.0425','eye_rx=.0365',1)
s=s.replace('eye_ry=.0129','eye_ry=.0152',1)
s=s.replace('eye_y+.0137','eye_y+.0146',1)
s=s.replace('eye_y-.0081','eye_y-.0090',1)

# Replace flat fan-triangulated iris/pupil discs with shallow smooth ellipsoids. This removes the ring/triangle look at iPhone scale.
s=s.replace(
    "add_ellipse_surface(HEAD,f'IrisV60_{side}',ex,eye_y,face_front+.0014,.0223,.0117,IRIS,48)",
    "add_sphere(HEAD,f'IrisV70_{side}',(ex,eye_y,face_front+.0018),(.0136,.0113,.00155),IRIS,40,24)",
    1,
)
s=s.replace(
    "add_ellipse_surface(HEAD,f'IrisInnerV60_{side}',ex,eye_y-.0002,face_front+.0020,.0165,.0088,IRIS_INNER,42)",
    "add_sphere(HEAD,f'IrisInnerV70_{side}',(ex,eye_y-.0001,face_front+.0030),(.0099,.0085,.00145),IRIS_INNER,36,22)",
    1,
)
s=s.replace(
    "add_ellipse_surface(HEAD,f'PupilV60_{side}',ex,eye_y-.0002,face_front+.0026,.0033,.0040,PUPIL,32)",
    "add_sphere(HEAD,f'PupilV70_{side}',(ex,eye_y-.0001,face_front+.0040),(.0036,.0045,.00135),PUPIL,28,18)",
    1,
)

# Replace the separate bridge/tip balls with one connected tapered nose solid that merges back into the face.
s=s.replace(
    "add_sphere(HEAD,'NoseBridgeV69',(0,-.006,.1082),(.0071,.037,.0058),SKIN,30,20)\nadd_sphere(HEAD,'NoseTipV69',(0,-.043,.1218),(.0097,.0096,.0082),SKIN,32,20)",
    "add_section_mesh(HEAD,'NoseFormV70',[(.031,.0045,.0026,.0038,.1035),(.008,.0054,.0031,.0050,.1068),(-.016,.0068,.0036,.0065,.1103),(-.035,.0087,.0041,.0086,.1146),(-.046,.0100,.0045,.0094,.1165),(-.055,.0082,.0037,.0055,.1133)],SKIN,32)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'NoseWingV69_{side}',(side*.0064,-.049,.1138),(.0045,.0056,.0040),SKIN,22,14)",
    "add_sphere(HEAD,f'NoseWingV70_{side}',(side*.0063,-.050,.1148),(.0042,.0048,.0036),SKIN,22,14)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'NostrilV69_{side}',(side*.0039,-.0538,.1188),(.00034,.00025,.00021),FACE_DARK,10,7)",
    "add_sphere(HEAD,f'NostrilV70_{side}',(side*.0040,-.0535,.1190),(.00040,.00030,.00024),FACE_DARK,12,8)",
    1,
)

# Curved lip ribbons replace the two flat parallel almond strips.
lip_old="""add_almond_surface(HEAD,'UpperLipV69',0,-.0762,.1112,.0254,.0037,.00078,LIP,58,1,0.0)
add_almond_surface(HEAD,'LowerLipV69',0,-.0832,.1120,.0248,.0042,.00088,LIP,58,1,0.0)
add_strand(HEAD,'MouthSeamV69',[(-.0212,-.0799,.1125),(0,-.0806,.1129),(.0212,-.0799,.1125)],.000095,FACE_DARK)
"""
lip_new="""add_flow_ribbon(HEAD,'UpperLipV70_L',[(-.026,-.0810,.1132),(-.014,-.0762,.1143),(0,-.0792,.1150)],[.0020,.0052,.0028],.00100,LIP)
add_flow_ribbon(HEAD,'UpperLipV70_R',[(0,-.0792,.1150),(.014,-.0762,.1143),(.026,-.0810,.1132)],[.0028,.0052,.0020],.00100,LIP)
add_flow_ribbon(HEAD,'LowerLipV70',[(-.025,-.0820,.1134),(-.012,-.0860,.1144),(0,-.0874,.1152),(.012,-.0860,.1144),(.025,-.0820,.1134)],[.0020,.0048,.0062,.0048,.0020],.00118,LIP)
add_strand(HEAD,'MouthSeamV70',[(-.024,-.0814,.1152),(0,-.0819,.1158),(.024,-.0814,.1152)],.000105,FACE_DARK)
"""
if lip_old not in s:
    raise SystemExit('v6.9 lip block not found')
s=s.replace(lip_old,lip_new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V70: volumetric eyes, unified nose and curved natural lips')
