from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V23' in s:
    print('Blender heroine generator already carries REFERENCE_V23')
    raise SystemExit(0)
if '# REFERENCE_V22' not in s:
    raise SystemExit('REFERENCE_V22 generator required before v2.3')
s=s.replace('# REFERENCE_V22: eye-clear tapered fringe proportions.','# REFERENCE_V22: eye-clear tapered fringe proportions.\n# REFERENCE_V23: projected portrait features for reliable front/profile readability.',1)

# Replace the barely-tangent facial primitives with a deliberately projected portrait layer.
# The previous features sat almost exactly on the head shell and disappeared through depth precision / interpolation.
a=s.index('# Facial plane is tied to the front depth of the eye/cheek rings.')
b=s.index('# Rear scalp never crosses the forehead;',a)
face='''# Portrait feature plane is projected slightly beyond the continuous head shell.
# This keeps the eyes/brows/mouth visible in WebGL without changing the measured skull silhouette.
face_z=head_d*.585
for side in(-1,1):
 ex=side*head_w*.158
 # Almond-like eye plate: compact vertically, wider horizontally, with dark upper lash.
 add_panel(HEAD,f'EyePlate_{side}',[(ex-head_w*.088,.031,face_z),(ex+head_w*.088,.031,face_z),(ex+head_w*.072,-.003,face_z),(ex-head_w*.072,-.003,face_z)],.0040,SCLERA)
 add_sphere(HEAD,f'Iris_{side}',(ex,.013,face_z+.0065),(head_w*.039,.0100,.0042),IRIS,22,12)
 add_sphere(HEAD,f'Pupil_{side}',(ex,.013,face_z+.0100),(head_w*.014,.0060,.0028),PUPIL,16,10)
 add_box(HEAD,f'UpperLash_{side}',(ex,.032,face_z+.0090),(head_w*.190,.0062,.0034),HAIR,.0012,rot=(0,0,-side*.080))
 add_box(HEAD,f'Brow_{side}',(ex,.071,face_z+.0040),(head_w*.172,.0050,.0030),HAIR,.0012,rot=(0,0,-side*.095))
 # Tiny catchlight prevents the iris from reading as a dead black dot at game distance.
 add_sphere(HEAD,f'EyeLight_{side}',(ex-side*head_w*.010,.019,face_z+.0135),(head_w*.010,.0038,.0018),SCLERA,12,8)
# Slim nose bridge and tip, pushed only enough to read in profile.
add_sphere(HEAD,'NoseBridge',(0,.010,face_z+.001),(.0065,.030,.0055),SKIN,18,10)
add_sphere(HEAD,'NoseTip',(0,-.028,face_z+.008),(.0082,.012,.0070),SKIN,18,10)
# Soft two-part lip line rather than one thick rectangular bar.
add_panel(HEAD,'UpperLip',[(-.037,-.067,face_z+.006),(.037,-.067,face_z+.006),(.026,-.075,face_z+.007),(-.026,-.075,face_z+.007)],.0025,LIP)
add_panel(HEAD,'LowerLip',[(-.027,-.076,face_z+.006),(.027,-.076,face_z+.006),(.018,-.083,face_z+.005),(-.018,-.083,face_z+.005)],.0020,LIP)
'''
s=s[:a]+face+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V23: projected portrait features for reliable front/profile readability')
