from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V62' in s:
    print('Blender heroine generator already carries REFERENCE_V62')
    raise SystemExit(0)
if '# REFERENCE_V61' not in s:
    raise SystemExit('REFERENCE_V61 generator required before v6.2')

s=s.replace(
    '# REFERENCE_V61: expressive larger eyes, tapered jaw and restrained explicit nose/lip profile.',
    '# REFERENCE_V61: expressive larger eyes, tapered jaw and restrained explicit nose/lip profile.\n# REFERENCE_V62: cinematic almond gaze, warm skin response and subtle readable side-profile nose.',
    1,
)

# Reduce bright-sky washout and remove the amber button-eye look.
s=s.replace("SKIN=material('Skin',(0.58,0.405,0.390),0,.66)","SKIN=material('Skin',(0.50,0.335,0.320),0,.72)",1)
s=s.replace("SCLERA=material('Sclera',(0.86,0.83,0.81),0,.54)","SCLERA=material('Sclera',(0.72,0.69,0.67),0,.60)",1)
s=s.replace("IRIS=material('Iris',(0.075,0.036,0.024),.01,.40)","IRIS=material('Iris',(0.050,0.032,0.030),.01,.46)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.28,0.115,0.052),.01,.44)","IRIS_INNER=material('Iris Inner',(0.115,0.066,0.055),.01,.48)",1)
s=s.replace("LIP=material('Lip',(0.36,0.135,0.150),0,.62)","LIP=material('Lip',(0.30,0.105,0.120),0,.68)",1)

# More horizontal almond; iris fills the vertical opening so the sclera becomes a thin frame.
s=s.replace('eye_rx=.0420','eye_rx=.0445',1)
s=s.replace('eye_ry=.0200','eye_ry=.0166',1)
s=s.replace(".0214,.0148,IRIS",".0228,.0141,IRIS",1)
s=s.replace(".0136,.0095,IRIS_INNER",".0147,.0096,IRIS_INNER",1)
s=s.replace(".0050,.0060,PUPIL",".0058,.0068,PUPIL",1)
s=s.replace("eye_y+.0202","eye_y+.0172",1)
s=s.replace("eye_y-.0120","eye_y-.0100",1)

# Slightly stronger but still compact nose profile; no return to the v5.x muzzle.
s=s.replace("add_sphere(HEAD,'NoseBridgeV61',(0,-.006,.1008),(.0085,.038,.0060),SKIN,28,18)","add_sphere(HEAD,'NoseBridgeV62',(0,-.006,.1030),(.0080,.038,.0062),SKIN,30,20)",1)
s=s.replace("add_sphere(HEAD,'NoseTipV61',(0,-.043,.1065),(.0125,.0115,.0090),SKIN,28,18)","add_sphere(HEAD,'NoseTipV62',(0,-.043,.1103),(.0118,.0112,.0092),SKIN,30,20)",1)
s=s.replace("add_sphere(HEAD,f'NoseWingV61_{side}',(side*.0072,-.049,.1038),(.0055,.0065,.0048),SKIN,22,14)","add_sphere(HEAD,f'NoseWingV62_{side}',(side*.0070,-.049,.1060),(.0052,.0062,.0046),SKIN,22,14)",1)
s=s.replace("add_sphere(HEAD,f'NostrilV61_{side}',(side*.0045,-.0540,.1082),(.00040,.00030,.00025),FACE_DARK,10,7)","add_sphere(HEAD,f'NostrilV62_{side}',(side*.0043,-.0540,.1110),(.00038,.00028,.00023),FACE_DARK,10,7)",1)

# Keep the mouth compact and closer to the facial shell than the nose tip.
s=s.replace("add_almond_surface(HEAD,'UpperLipV61',0,-.0765,.1030,.0275,.0042,.00090,LIP,58,1,0.0)","add_almond_surface(HEAD,'UpperLipV62',0,-.0765,.1038,.0270,.0039,.00082,LIP,58,1,0.0)",1)
s=s.replace("add_almond_surface(HEAD,'LowerLipV61',0,-.0838,.1036,.0265,.0048,.00100,LIP,58,1,0.0)","add_almond_surface(HEAD,'LowerLipV62',0,-.0838,.1043,.0260,.0045,.00092,LIP,58,1,0.0)",1)
s=s.replace("add_strand(HEAD,'MouthSeamV61',[(-.0230,-.0802,.1042),(0,-.0810,.1046),(.0230,-.0802,.1042)],.00011,FACE_DARK)","add_strand(HEAD,'MouthSeamV62',[(-.0225,-.0802,.1049),(0,-.0810,.1052),(.0225,-.0802,.1049)],.00010,FACE_DARK)",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V62: cinematic almond gaze, warmer skin and readable restrained profile')
