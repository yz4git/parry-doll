from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V46' in s:
    print('Blender heroine generator already carries REFERENCE_V46')
    raise SystemExit(0)
if '# REFERENCE_V45' not in s:
    raise SystemExit('REFERENCE_V45 generator required before v4.6')

s=s.replace(
    '# REFERENCE_V45: safe layered lock fringe, warmer portrait materials and stronger eyes/lips.',
    '# REFERENCE_V45: safe layered lock fringe, warmer portrait materials and stronger eyes/lips.\n# REFERENCE_V46: cinematic almond eyes, readable nasal bridge and fuller natural mouth.',
    1,
)

# Brown irises need enough luminance to separate from the pupils at the iPhone face-preset size.
s=s.replace("IRIS=material('Iris',(0.10,0.067,0.055),.02,.30)", "IRIS=material('Iris',(0.18,0.105,0.080),.02,.28)", 1)
s=s.replace("SKIN=material('Skin',(0.60,0.41,0.39),0,.56)", "SKIN=material('Skin',(0.57,0.39,0.37),0,.60)", 1)

a=s.index('# Anatomy v4.4:')
b=s.index('# Hair v4.5:',a)
face="""# Anatomy v4.6: wider almond eyes, visible iris separation and a readable central face plane.
face_front=head_d*.514
eye_y=.0325
eye_x=head_w*.146
eye_rx=head_w*.112
eye_ry=.0123
eye_tilt=.0037
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV46_{side}',(ex,eye_y,head_d*.418),(head_w*.086,.0170,head_d*.064),SCLERA,42,24)
 add_almond_surface(HEAD,f'EyeOpeningV46_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0027,SCLERA,48,side,eye_tilt)
 # Larger warm-brown iris and smaller pupil recreate the reference's glossy dark eye without a black-dot stare.
 add_sphere(HEAD,f'IrisV46_{side}',(ex,eye_y+.0002,face_front+.0060),(head_w*.0525,.0108,.0031),IRIS,36,20)
 add_sphere(HEAD,f'PupilV46_{side}',(ex,eye_y+.0001,face_front+.0088),(head_w*.0105,.0048,.0019),PUPIL,24,14)
 add_sphere(HEAD,f'EyeLightV46_{side}',(ex-side*head_w*.0100,eye_y+.0053,face_front+.0108),(head_w*.0055,.0024,.0011),SCLERA,12,8)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 # The upper lid carries most of the graphic weight; the lower lid is skin-toned and much finer.
 add_strand(HEAD,f'UpperLidV46_{side}',[(inner,inner_y+.0010,face_front+.0035),(ex,eye_y+.0128,face_front+.0059),(outer,outer_y+.0011,face_front+.0035)],.00070,SKIN)
 add_strand(HEAD,f'LowerLidV46_{side}',[(inner,inner_y-.0004,face_front+.0025),(ex,eye_y-.0071,face_front+.0032),(outer,outer_y-.0004,face_front+.0025)],.00042,SKIN)
 add_strand(HEAD,f'UpperLashV46_{side}',[(inner,inner_y+.0017,face_front+.0064),(ex,eye_y+.0137,face_front+.0081),(outer,outer_y+.0019,face_front+.0066)],.00082,HAIR)
 add_strand(HEAD,f'LashWingV46_{side}',[(outer,outer_y+.0019,face_front+.0066),(outer+side*head_w*.017,outer_y+.0068,face_front+.0071)],.00058,HAIR)
 add_strand(HEAD,f'BrowV46_{side}',[(ex-side*eye_rx*.80,.0690,head_d*.510),(ex,.0790,head_d*.516),(ex+side*eye_rx*.99,.0665,head_d*.511)],.00113,HAIR)

# A skin-volume bridge catches the side light; the shell still supplies the broad nose planes.
add_sphere(HEAD,'NoseBridgeV46',(0,-.0040,head_d*.535),(.0062,.041,.0064),SKIN,28,16)
add_sphere(HEAD,'NoseTipV46',(0,-.0450,head_d*.554),(.0105,.0090,.0067),SKIN,28,16)
add_sphere(HEAD,'ColumellaV46',(0,-.0540,head_d*.549),(.0030,.0046,.0030),SKIN,18,10)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV46_{side}',(side*.0102,-.0508,head_d*.546),(.0050,.0046,.0036),SKIN,20,12)
 add_sphere(HEAD,f'NostrilV46_{side}',(side*.0070,-.0528,head_d*.551),(.00135,.00095,.00080),FACE_DARK,12,8)

# Slightly wider, softer lips replace the tiny-point read visible in earlier audits.
add_almond_surface(HEAD,'UpperLipV46',0,-.0813,head_d*.551,.0370,.0055,.0021,LIP,48,1,0.0)
add_almond_surface(HEAD,'LowerLipV46',0,-.0896,head_d*.550,.0340,.0063,.0024,LIP,48,1,0.0)
add_strand(HEAD,'MouthSeamV46',[(-.0315,-.0855,head_d*.553),(0,-.0867,head_d*.554),(.0315,-.0855,head_d*.553)],.00034,FACE_DARK)

"""
s=s[:a]+face+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V46: cinematic eyes, nose bridge and fuller natural mouth')
