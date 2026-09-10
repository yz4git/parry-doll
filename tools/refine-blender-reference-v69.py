from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V69' in s:
    print('Blender heroine generator already carries REFERENCE_V69')
    raise SystemExit(0)
if '# REFERENCE_V68' not in s:
    raise SystemExit('REFERENCE_V68 generator required before v6.9')

s=s.replace(
    '# REFERENCE_V68: layered porcelain torso shell, narrow black corset centre and natural portrait eye spacing.',
    '# REFERENCE_V68: layered porcelain torso shell, narrow black corset centre and natural portrait eye spacing.\n# REFERENCE_V69: sculpted adult-anime portrait planes, tapered jaw and restrained continuous profile.',
    1,
)

# Keep the stable UV topology, but taper the lower face and give the cheek/orbit planes clearer separation.
s=s.replace("width=.132*(1.0-.245*lower+.025*cheek)","width=.132*(1.0-.300*lower+.030*cheek)",1)
s=s.replace("z-=fm*.0042*math.exp(-((x-ex)/.026)**2-((yy-.033)/.022)**2)","z-=fm*.0058*math.exp(-((x-ex)/.026)**2-((yy-.033)/.022)**2)",1)
s=s.replace("z+=fm*.0034*math.exp(-((x-side*.054)/.035)**2-((yy+.004)/.040)**2)","z+=fm*.0044*math.exp(-((x-side*.054)/.035)**2-((yy+.004)/.040)**2)",1)

# Continuous centre-line relief: still far below the old v5.x projection, but enough to read from true profile.
s=s.replace("z+=fm*.0038*math.exp(-(x/.019)**2-((yy+.002)/.052)**2)","z+=fm*.0054*math.exp(-(x/.019)**2-((yy+.002)/.052)**2)",1)
s=s.replace("z+=fm*.0105*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)","z+=fm*.0140*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)",1)
s=s.replace("z-=fm*.0025*math.exp(-(x/.018)**2-((yy+.061)/.012)**2)","z-=fm*.0036*math.exp(-(x/.018)**2-((yy+.061)/.012)**2)",1)
s=s.replace("z+=fm*.0032*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)","z+=fm*.0046*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)",1)
s=s.replace("z+=fm*.0042*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)","z+=fm*.0060*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)",1)

# Softer grey-brown iris that remains legible in the bright WebGL audit scene.
s=s.replace("IRIS=material('Iris',(0.042,0.031,0.033),.01,.50)","IRIS=material('Iris',(0.050,0.038,0.040),.01,.52)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.180,0.125,0.112),.01,.52)","IRIS_INNER=material('Iris Inner',(0.205,0.150,0.136),.01,.54)",1)

# Calm adult-anime almond: a little wider, clearly less round, with an iris large enough to avoid a startled sclera-heavy look.
s=s.replace('eye_x=.0435','eye_x=.0450',1)
s=s.replace('eye_rx=.0415','eye_rx=.0425',1)
s=s.replace('eye_ry=.0142','eye_ry=.0129',1)
s=s.replace('.0210,.0122,IRIS','.0223,.0117,IRIS',1)
s=s.replace('.0154,.0091,IRIS_INNER','.0165,.0088,IRIS_INNER',1)
s=s.replace('.0035,.0042,PUPIL','.0033,.0040,PUPIL',1)
s=s.replace('eye_y+.0148','eye_y+.0137',1)
s=s.replace('eye_y-.0086','eye_y-.0081',1)

# Explicit accents now sit on the strengthened continuous surface rather than doing all of the profile work themselves.
s=s.replace("add_sphere(HEAD,'NoseBridgeV64',(0,-.006,.1065),(.0075,.038,.0062),SKIN,30,20)","add_sphere(HEAD,'NoseBridgeV69',(0,-.006,.1082),(.0071,.037,.0058),SKIN,30,20)",1)
s=s.replace("add_sphere(HEAD,'NoseTipV64',(0,-.043,.1180),(.0105,.0102,.0087),SKIN,32,20)","add_sphere(HEAD,'NoseTipV69',(0,-.043,.1218),(.0097,.0096,.0082),SKIN,32,20)",1)
s=s.replace("add_sphere(HEAD,f'NoseWingV64_{side}',(side*.0068,-.049,.1110),(.0049,.0060,.0043),SKIN,22,14)","add_sphere(HEAD,f'NoseWingV69_{side}',(side*.0064,-.049,.1138),(.0045,.0056,.0040),SKIN,22,14)",1)
s=s.replace("add_sphere(HEAD,f'NostrilV64_{side}',(side*.0041,-.0540,.1160),(.00036,.00027,.00022),FACE_DARK,10,7)","add_sphere(HEAD,f'NostrilV69_{side}',(side*.0039,-.0538,.1188),(.00034,.00025,.00021),FACE_DARK,10,7)",1)
s=s.replace("add_almond_surface(HEAD,'UpperLipV64',0,-.0765,.1080,.0262,.0038,.00082,LIP,58,1,0.0)","add_almond_surface(HEAD,'UpperLipV69',0,-.0762,.1112,.0254,.0037,.00078,LIP,58,1,0.0)",1)
s=s.replace("add_almond_surface(HEAD,'LowerLipV64',0,-.0838,.1086,.0255,.0044,.00092,LIP,58,1,0.0)","add_almond_surface(HEAD,'LowerLipV69',0,-.0832,.1120,.0248,.0042,.00088,LIP,58,1,0.0)",1)
s=s.replace("add_strand(HEAD,'MouthSeamV64',[(-.0220,-.0802,.1092),(0,-.0810,.1096),(.0220,-.0802,.1092)],.00010,FACE_DARK)","add_strand(HEAD,'MouthSeamV69',[(-.0212,-.0799,.1125),(0,-.0806,.1129),(.0212,-.0799,.1125)],.000095,FACE_DARK)",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V69: sculpted portrait anatomy and tapered adult-anime gaze')
