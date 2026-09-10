from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V61' in s:
    print('Blender heroine generator already carries REFERENCE_V61')
    raise SystemExit(0)
if '# REFERENCE_V60' not in s:
    raise SystemExit('REFERENCE_V60 generator required before v6.1')

s=s.replace(
    '# REFERENCE_V60: stable UV portrait head, continuous facial planes and restrained adult profile.',
    '# REFERENCE_V60: stable UV portrait head, continuous facial planes and restrained adult profile.\n# REFERENCE_V61: expressive larger eyes, tapered jaw and restrained explicit nose/lip profile.',
    1,
)

# Sharpen the lower-face silhouette without disturbing the smooth UV topology.
s=s.replace("width=.132*(1.0-.205*lower+.025*cheek)","width=.132*(1.0-.245*lower+.025*cheek)",1)

# Bring the eyes closer to the reference portrait while keeping adult horizontal proportions.
s=s.replace('face_front=.0964','face_front=.0974',1)
s=s.replace('eye_rx=.0368','eye_rx=.0420',1)
s=s.replace('eye_ry=.0168','eye_ry=.0200',1)
s=s.replace(".0184,.0122,IRIS",".0214,.0148,IRIS",1)
s=s.replace(".0116,.0077,IRIS_INNER",".0136,.0095,IRIS_INNER",1)
s=s.replace(".0044,.0049,PUPIL",".0050,.0060,PUPIL",1)
s=s.replace("eye_y+.0173","eye_y+.0202",1)
s=s.replace("eye_y-.0102","eye_y-.0120",1)

# Add a deliberately small explicit nose over the already restrained mesh profile.
needle="""# Only tiny surface accents are separate; the head mesh owns the actual nose/chin profile.\nfor side in(-1,1):add_sphere(HEAD,f'NostrilV60_{side}',(side*.0042,-.0535,.1055),(.00042,.00030,.00026),FACE_DARK,10,7)"""
replacement="""# v6.1 explicit portrait accents remain shallow; they only make the profile readable.\nadd_sphere(HEAD,'NoseBridgeV61',(0,-.006,.1008),(.0085,.038,.0060),SKIN,28,18)\nadd_sphere(HEAD,'NoseTipV61',(0,-.043,.1065),(.0125,.0115,.0090),SKIN,28,18)\nfor side in(-1,1):\n add_sphere(HEAD,f'NoseWingV61_{side}',(side*.0072,-.049,.1038),(.0055,.0065,.0048),SKIN,22,14)\n add_sphere(HEAD,f'NostrilV61_{side}',(side*.0045,-.0540,.1082),(.00040,.00030,.00025),FACE_DARK,10,7)"""
if needle not in s:
    raise SystemExit('v6.0 nose anchor not found')
s=s.replace(needle,replacement,1)

s=s.replace("add_almond_surface(HEAD,'UpperLipV60',0,-.0770,.1012,.0265,.0038,.00075,LIP,54,1,0.0)","add_almond_surface(HEAD,'UpperLipV61',0,-.0765,.1030,.0275,.0042,.00090,LIP,58,1,0.0)",1)
s=s.replace("add_almond_surface(HEAD,'LowerLipV60',0,-.0840,.1018,.0255,.0042,.00085,LIP,54,1,0.0)","add_almond_surface(HEAD,'LowerLipV61',0,-.0838,.1036,.0265,.0048,.00100,LIP,58,1,0.0)",1)
s=s.replace("add_strand(HEAD,'MouthSeamV60',[(-.0225,-.0805,.1024),(0,-.0812,.1028),(.0225,-.0805,.1024)],.00011,FACE_DARK)","add_strand(HEAD,'MouthSeamV61',[(-.0230,-.0802,.1042),(0,-.0810,.1046),(.0230,-.0802,.1042)],.00011,FACE_DARK)",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V61: expressive stable portrait with tapered jaw and restrained nose')
