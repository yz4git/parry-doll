from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V64' in s:
    print('Blender heroine generator already carries REFERENCE_V64')
    raise SystemExit(0)
if '# REFERENCE_V63' not in s:
    raise SystemExit('REFERENCE_V63 generator required before v6.4')

s=s.replace(
    '# REFERENCE_V63: layered grey-brown irises, smaller pupils and fine separated portrait fringe.',
    '# REFERENCE_V63: layered grey-brown irises, smaller pupils and fine separated portrait fringe.\n# REFERENCE_V64: readable soft grey-brown gaze and continuous restrained nose-lip-chin profile.',
    1,
)

# Keep a dark limbal ring but make the inner iris visibly grey-brown under the bright audit sky.
s=s.replace("IRIS=material('Iris',(0.030,0.023,0.024),.01,.48)","IRIS=material('Iris',(0.042,0.031,0.033),.01,.50)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.115,0.078,0.070),.01,.50)","IRIS_INNER=material('Iris Inner',(0.180,0.125,0.112),.01,.52)",1)
s=s.replace("SCLERA=material('Sclera',(0.72,0.69,0.67),0,.60)","SCLERA=material('Sclera',(0.66,0.635,0.615),0,.62)",1)

# A calmer horizontal almond: slightly less vertical white, large iris, small pupil.
s=s.replace('eye_y=.0315','eye_y=.0308',1)
s=s.replace('eye_rx=.0455','eye_rx=.0460',1)
s=s.replace('eye_ry=.0161','eye_ry=.0154',1)
s=s.replace(".0260,.0146,IRIS",".0262,.0138,IRIS",1)
s=s.replace(".0200,.0115,IRIS_INNER",".0208,.0109,IRIS_INNER",1)
s=s.replace(".0048,.0058,PUPIL",".0038,.0047,PUPIL",1)
s=s.replace("eye_y+.0168","eye_y+.0160",1)
s=s.replace("eye_y-.0100","eye_y-.0094",1)

# Strengthen only the centre-line depth on the smooth UV head. This preserves the stable topology.
s=s.replace("z+=fm*.0080*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)","z+=fm*.0105*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)",1)
s=s.replace("z+=fm*.0018*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)","z+=fm*.0032*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)",1)
s=s.replace("z+=fm*.0028*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)","z+=fm*.0042*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)",1)

# Explicit accents stay narrow in front, but sit far enough forward to read from profile.
s=s.replace("add_sphere(HEAD,'NoseBridgeV63',(0,-.006,.1040),(.0078,.038,.0061),SKIN,30,20)","add_sphere(HEAD,'NoseBridgeV64',(0,-.006,.1065),(.0075,.038,.0062),SKIN,30,20)",1)
s=s.replace("add_sphere(HEAD,'NoseTipV63',(0,-.043,.1122),(.0114,.0110,.0090),SKIN,30,20)","add_sphere(HEAD,'NoseTipV64',(0,-.043,.1180),(.0105,.0102,.0087),SKIN,32,20)",1)
s=s.replace("add_sphere(HEAD,f'NoseWingV62_{side}',(side*.0070,-.049,.1060),(.0052,.0062,.0046),SKIN,22,14)","add_sphere(HEAD,f'NoseWingV64_{side}',(side*.0068,-.049,.1110),(.0049,.0060,.0043),SKIN,22,14)",1)
s=s.replace("add_sphere(HEAD,f'NostrilV62_{side}',(side*.0043,-.0540,.1110),(.00038,.00028,.00023),FACE_DARK,10,7)","add_sphere(HEAD,f'NostrilV64_{side}',(side*.0041,-.0540,.1160),(.00036,.00027,.00022),FACE_DARK,10,7)",1)
s=s.replace("add_almond_surface(HEAD,'UpperLipV62',0,-.0765,.1038,.0270,.0039,.00082,LIP,58,1,0.0)","add_almond_surface(HEAD,'UpperLipV64',0,-.0765,.1080,.0262,.0038,.00082,LIP,58,1,0.0)",1)
s=s.replace("add_almond_surface(HEAD,'LowerLipV62',0,-.0838,.1043,.0260,.0045,.00092,LIP,58,1,0.0)","add_almond_surface(HEAD,'LowerLipV64',0,-.0838,.1086,.0255,.0044,.00092,LIP,58,1,0.0)",1)
s=s.replace("add_strand(HEAD,'MouthSeamV62',[(-.0225,-.0802,.1049),(0,-.0810,.1052),(.0225,-.0802,.1049)],.00010,FACE_DARK)","add_strand(HEAD,'MouthSeamV64',[(-.0220,-.0802,.1092),(0,-.0810,.1096),(.0220,-.0802,.1092)],.00010,FACE_DARK)",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V64: readable soft gaze and restrained continuous profile')
