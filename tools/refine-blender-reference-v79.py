from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V79' in s:
    print('Blender heroine generator already carries REFERENCE_V79')
    raise SystemExit(0)
if '# REFERENCE_V78' not in s:
    raise SystemExit('REFERENCE_V78 generator required before v7.9')

s=s.replace(
    '# REFERENCE_V78: narrower mature face, wider almond gaze, fuller sculpted lips and cleaner swept hairline.',
    '# REFERENCE_V78: narrower mature face, wider almond gaze, fuller sculpted lips and cleaner swept hairline.\n# REFERENCE_V79: embedded eyes, stronger adult nose bridge, integrated lips and an open asymmetric fringe.',
    1,
)

# Give the hybrid quad patch a genuine centre-line nose volume instead of letting the profile
# exist only as a shallow row target. The lateral Gaussian keeps cheeks unchanged.
old="""  z=pz+local_relief*relief_gain+.0016
  verts.append(bpos((x,yy,z)))
"""
new="""  z=pz+local_relief*relief_gain+.0016
  bridge_lat=math.exp(-(x/.030)**2)
  tip_lat=math.exp(-(x/.0215)**2)
  z+=.0034*bridge_lat*math.exp(-((yy+.006)/.050)**2)
  z+=.0048*tip_lat*math.exp(-((yy+.045)/.0175)**2)
  verts.append(bpos((x,yy,z)))
"""
if old not in s: raise SystemExit('v7.9 face-patch z anchor missing')
s=s.replace(old,new,1)

# Seat the almond surface into the socket. Keep the front silhouette but remove the contact-lens bulge
# that becomes obvious in three-quarter view.
repls=[
("add_almond_lens(HEAD,f'EyeScleraV78_{side}',ex,eye_y,.1038,.0392,.0129,.00410,SCLERA,8,80,side,eye_tilt*.72)",
 "add_almond_lens(HEAD,f'EyeScleraV79_{side}',ex,eye_y,.1022,.0392,.0129,.00265,SCLERA,8,80,side,eye_tilt*.72)"),
("add_sphere(HEAD,f'IrisV78_{side}',(ex,eye_y,.1087),(.0137,.0104,.00142),IRIS_INNER,52,30)",
 "add_sphere(HEAD,f'IrisV79_{side}',(ex,eye_y,.1050),(.0134,.0102,.00118),IRIS_INNER,52,30)"),
("add_sphere(HEAD,f'PupilV78_{side}',(ex,eye_y-.0002,.1098),(.00275,.00335,.00098),PUPIL,32,22)",
 "add_sphere(HEAD,f'PupilV79_{side}',(ex,eye_y-.0002,.1061),(.00270,.00325,.00078),PUPIL,32,22)"),
("add_ellipse_surface(HEAD,f'EyeLightV78_{side}',ex-side*.0044,eye_y+.0041,.1104,.00128,.00102,SCLERA,18)",
 "add_ellipse_surface(HEAD,f'EyeLightV79_{side}',ex-side*.0043,eye_y+.0040,.1068,.00118,.00094,SCLERA,18)"),
("add_strand(HEAD,f'UpperLashV76_{side}',[(inner,eye_y-eye_tilt+.0010,.1072),(ex,eye_y+.0138,.1085),(outer,eye_y+eye_tilt+.0010,.1073)],.00088,HAIR)",
 "add_strand(HEAD,f'UpperLashV79_{side}',[(inner,eye_y-eye_tilt+.0010,.1045),(ex,eye_y+.0138,.1057),(outer,eye_y+eye_tilt+.0010,.1046)],.00082,HAIR)"),
("add_strand(HEAD,f'UpperLidFoldV76_{side}',[(inner+side*.0042,eye_y-eye_tilt+.0032,.1060),(ex,eye_y+.0160,.1068),(outer-side*.0042,eye_y+eye_tilt+.0032,.1060)],.00021,FACE_DARK)",
 "add_strand(HEAD,f'UpperLidFoldV79_{side}',[(inner+side*.0042,eye_y-eye_tilt+.0032,.1039),(ex,eye_y+.0160,.1047),(outer-side*.0042,eye_y+eye_tilt+.0032,.1039)],.00019,FACE_DARK)"),
("add_strand(HEAD,f'LowerLidV76_{side}',[(inner+side*.0042,eye_y-eye_tilt-.0002,.1054),(ex,eye_y-.0095,.1059),(outer-side*.0042,eye_y+eye_tilt-.0002,.1054)],.000075,FACE_DARK)",
 "add_strand(HEAD,f'LowerLidV79_{side}',[(inner+side*.0042,eye_y-eye_tilt-.0002,.1036),(ex,eye_y-.0095,.1041),(outer-side*.0042,eye_y+eye_tilt-.0002,.1036)],.000070,FACE_DARK)"),
]
for old,new in repls:
    if old not in s: raise SystemExit(f'v7.9 eye anchor missing: {old[:52]}')
    s=s.replace(old,new,1)

old_lips="""add_panel(HEAD,'UpperLipV78_L',[(-.0260,-.0850,.1102),(-.0128,-.0797,.1118),(0,-.0828,.1129),(0,-.0870,.1132),(-.0110,-.0860,.1125),(-.0242,-.0883,.1109)],.00066,LIP)
add_panel(HEAD,'UpperLipV78_R',[(0,-.0828,.1129),(.0128,-.0797,.1118),(.0260,-.0850,.1102),(.0242,-.0883,.1109),(.0110,-.0860,.1125),(0,-.0870,.1132)],.00066,LIP)
add_panel(HEAD,'LowerLipV78',[(-.0242,-.0884,.1112),(0,-.0874,.1129),(.0242,-.0884,.1112),(.0208,-.0954,.1110),(0,-.0990,.1115),(-.0208,-.0954,.1110)],.00072,LIP)
add_strand(HEAD,'MouthSeamV78',[(-.0248,-.0868,.1111),(-.0115,-.0862,.1123),(0,-.0872,.1133),(.0115,-.0862,.1123),(.0248,-.0868,.1111)],.000050,FACE_DARK)
"""
new_lips="""add_panel(HEAD,'UpperLipV79_L',[(-.0255,-.0850,.1098),(-.0125,-.0798,.1105),(0,-.0829,.1112),(0,-.0870,.1114),(-.0108,-.0860,.1110),(-.0238,-.0883,.1102)],.00050,LIP)
add_panel(HEAD,'UpperLipV79_R',[(0,-.0829,.1112),(.0125,-.0798,.1105),(.0255,-.0850,.1098),(.0238,-.0883,.1102),(.0108,-.0860,.1110),(0,-.0870,.1114)],.00050,LIP)
add_panel(HEAD,'LowerLipV79',[(-.0238,-.0884,.1105),(0,-.0875,.1115),(.0238,-.0884,.1105),(.0202,-.0952,.1104),(0,-.0983,.1109),(-.0202,-.0952,.1104)],.00054,LIP)
add_strand(HEAD,'MouthSeamV79',[(-.0242,-.0868,.1103),(-.0112,-.0862,.1110),(0,-.0871,.1116),(.0112,-.0862,.1110),(.0242,-.0868,.1103)],.000045,FACE_DARK)
"""
if old_lips not in s: raise SystemExit('v7.9 lip block missing')
s=s.replace(old_lips,new_lips,1)

# Open the centre of the forehead and sweep the broad masses toward the heroine's right temple.
hair_repls=[
("add_flow_ribbon(HEAD,'FringeSweepV59_A',[(-.112,.182,.012),(-.096,.160,.045),(-.066,.134,.074),(-.027,.107,.096),(.018,.085,.106),(.060,.071,.110)],[.086,.088,.080,.064,.046,.028],.00145,HAIR)",
 "add_flow_ribbon(HEAD,'FringeSweepV79_A',[(-.112,.182,.012),(-.095,.161,.045),(-.062,.139,.074),(-.018,.120,.095),(.030,.105,.105),(.078,.096,.108)],[.072,.074,.065,.050,.033,.018],.00130,HAIR)"),
("add_flow_ribbon(HEAD,'FringeSweepV59_B',[(-.047,.184,.012),(-.025,.160,.047),(.010,.133,.077),(.048,.106,.099),(.085,.083,.108),(.114,.069,.110)],[.072,.071,.064,.050,.035,.021],.00140,HAIR)",
 "add_flow_ribbon(HEAD,'FringeSweepV79_B',[(-.048,.184,.012),(-.022,.163,.047),(.018,.142,.077),(.061,.121,.098),(.096,.106,.106),(.121,.098,.108)],[.058,.060,.052,.039,.026,.014],.00126,HAIR)"),
("add_flow_ribbon(HEAD,'FringeLayerV59_C',[(-.083,.177,.014),(-.059,.153,.049),(-.026,.126,.078),(.012,.101,.100),(.043,.085,.108)],[.035,.037,.033,.024,.012],.00115,HAIR_HI)",
 "add_flow_ribbon(HEAD,'FringeLayerV79_C',[(-.083,.177,.014),(-.056,.156,.049),(-.020,.137,.078),(.020,.119,.099),(.060,.108,.106)],[.030,.031,.027,.019,.009],.00102,HAIR_HI)"),
("add_flow_ribbon(HEAD,'FringeLayerV59_D',[(-.015,.179,.013),(.010,.153,.049),(.043,.125,.079),(.078,.099,.101),(.105,.082,.108)],[.032,.034,.030,.022,.011],.00112,HAIR)",
 "add_flow_ribbon(HEAD,'FringeLayerV79_D',[(-.014,.179,.013),(.014,.157,.049),(.052,.138,.079),(.087,.119,.100),(.112,.106,.106)],[.026,.028,.024,.017,.008],.00100,HAIR)"),
]
for old,new in hair_repls:
    if old not in s: raise SystemExit(f'v7.9 fringe anchor missing: {old[:48]}')
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V79: embedded gaze, stronger nose, integrated mouth, open side-swept fringe')
