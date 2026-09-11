from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V114' in s:
    print('Blender heroine generator already carries REFERENCE_V114')
    raise SystemExit(0)
if '# REFERENCE_V113' not in s:
    raise SystemExit('REFERENCE_V113 generator required before v11.4')
marker='# REFERENCE_V113: the new single shell gains an explicit adult S-profile and seated orbital surfaces after five-view validation exposed the v11.2 flat side silhouette.'
s=s.replace(marker,marker+'\n# REFERENCE_V114: stronger public-basemesh-scale facial projection gives the clean shell a readable nose/lip/chin silhouette and retargets surface accents to it.',1)

old_profile=""" profile=[
  (.090,.0970),(.060,.0985),(.035,.1010),(.015,.1040),(-.005,.1080),(-.025,.1145),
  (-.044,.1265),(-.055,.1180),(-.066,.1040),(-.076,.1085),(-.086,.1113),(-.095,.1110),
  (-.105,.0990),(-.118,.1050),(-.128,.1020),(-.137,.0940),(-.145,.0820)
 ]
"""
new_profile=""" profile=[
  (.090,.0990),(.060,.1000),(.035,.1030),(.015,.1080),(-.005,.1140),(-.025,.1240),
  (-.044,.1450),(-.054,.1320),(-.063,.1190),(-.069,.1080),(-.077,.1145),(-.086,.1200),
  (-.094,.1215),(-.103,.1130),(-.110,.1050),(-.119,.1160),(-.128,.1120),(-.137,.1000),(-.145,.0860)
 ]
"""
if old_profile not in s:raise SystemExit('v11.4 profile block missing')
s=s.replace(old_profile,new_profile,1)

old_lat="""    profile_lat=1.0/(1.0+(abs(x)/.034)**6)
    profile_band=math.exp(-((yy+.032)/.148)**6)
    z+=fm*profile_lat*profile_band*(pz-z)*.96
"""
new_lat="""    # The nose uses a narrower pyramid; muzzle/chin projection spreads more broadly into the cheeks.
    profile_width=.030 if yy>-.068 else (.043 if yy>-.108 else .039)
    profile_lat=1.0/(1.0+(abs(x)/profile_width)**6)
    profile_band=math.exp(-((yy+.032)/.148)**6)
    z+=fm*profile_lat*profile_band*(pz-z)*.985
"""
if old_lat not in s:raise SystemExit('v11.4 profile lateral block missing')
s=s.replace(old_lat,new_lat,1)

# Existing lip meshes are only colour/detail, but their old v8.0 Z positions are behind the rebuilt muzzle.
old_lips="""add_panel(HEAD,'UpperLipV80_L',[(-.0225,-.0848,.1095),(-.0110,-.0802,.1101),(0,-.0833,.1107),(0,-.0867,.1108),(-.0095,-.0859,.1105),(-.0210,-.0880,.1099)],.00030,LIP)
add_panel(HEAD,'UpperLipV80_R',[(0,-.0833,.1107),(.0110,-.0802,.1101),(.0225,-.0848,.1095),(.0210,-.0880,.1099),(.0095,-.0859,.1105),(0,-.0867,.1108)],.00030,LIP)
add_panel(HEAD,'LowerLipV80',[(-.0210,-.0882,.1100),(0,-.0876,.1108),(.0210,-.0882,.1100),(.0178,-.0942,.1099),(0,-.0969,.1103),(-.0178,-.0942,.1099)],.00034,LIP)
add_strand(HEAD,'MouthSeamV80',[(-.0215,-.0867,.1099),(-.0100,-.0862,.1105),(0,-.0870,.1109),(.0100,-.0862,.1105),(.0215,-.0867,.1099)],.000038,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV76_{side}',side*.0056,-.0570,.1157,.00145,.00052,FACE_DARK,16)
"""
new_lips="""# v11.4 surface accents follow the rebuilt shell instead of the retired v8 face depth.
add_panel(HEAD,'UpperLipV114_L',[(-.0230,-.0848,.1195),(-.0112,-.0802,.1206),(0,-.0832,.1221),(0,-.0867,.1224),(-.0098,-.0860,.1213),(-.0215,-.0880,.1200)],.00028,LIP)
add_panel(HEAD,'UpperLipV114_R',[(0,-.0832,.1221),(.0112,-.0802,.1206),(.0230,-.0848,.1195),(.0215,-.0880,.1200),(.0098,-.0860,.1213),(0,-.0867,.1224)],.00028,LIP)
add_panel(HEAD,'LowerLipV114',[(-.0215,-.0883,.1201),(0,-.0877,.1222),(.0215,-.0883,.1201),(.0180,-.0944,.1198),(0,-.0970,.1208),(-.0180,-.0944,.1198)],.00032,LIP)
add_strand(HEAD,'MouthSeamV114',[(-.0218,-.0868,.1200),(-.0102,-.0863,.1212),(0,-.0871,.1225),(.0102,-.0863,.1212),(.0218,-.0868,.1200)],.000040,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV114_{side}',side*.0062,-.0570,.1250,.00165,.00058,FACE_DARK,18)
"""
if old_lips not in s:raise SystemExit('v11.4 lip/nostril block missing')
s=s.replace(old_lips,new_lips,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V114: stronger single-shell profile and rebuilt-surface lip/nostril accents')
