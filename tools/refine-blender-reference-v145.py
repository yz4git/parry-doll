from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V145' in s:
    print('Blender heroine generator already carries REFERENCE_V145')
    raise SystemExit(0)
if '# REFERENCE_V144' not in s:
    raise SystemExit('REFERENCE_V144 generator required before v13.15')

marker="# REFERENCE_V144: ear-anatomy/layered-hair pass gives the exposed ear shallow 3D concha/tragus structure and overlays narrow swept crown/temple locks so the supplied profile reads as layered dark-brown hair instead of a smooth helmet mass."
if marker not in s:
    raise SystemExit('v13.15 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V145: portrait-eye/lip realism pass reduces the front/three-quarter doll-eye vertical aperture and iris dominance, while enlarging only the exact-profile eye aperture and adding restrained lip volume for the supplied elegant side portrait.",1)

# Three-quarter/front: retain eye width but reduce vertical roundness and iris dominance.
repls=[
 ("eye_ry=.01090*ASSEMBLY120['head']['eyeSize']","eye_ry=.00995*ASSEMBLY120['head']['eyeSize']"),
 ("iris_scale=ASSEMBLY120['head']['irisScale']*1.05","iris_scale=ASSEMBLY120['head']['irisScale']*.97"),
 (".00102*eye_contrast,HAIR)",".00110*eye_contrast,HAIR)"),
 (".00060*eye_contrast,HAIR)",".00066*eye_contrast,HAIR)"),
]
for old,new in repls:
    if old not in s:
        raise SystemExit(f'v13.15 eye anchor missing: {old}')
    s=s.replace(old,new,1)

# Exact profile: because these YZ planes are edge-on from front they can be larger without changing the
# established frontal identity. This makes the supplied-reference eye readable at a true 90-degree view.
old=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileScleraYZV140_{side}',ex+side*eye_rx*.846,eye_y+.0001,.1023,eye_ry*.73,.00570,SCLERA,38)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.858,eye_y+.0002,.1030,eye_ry*.50,.00370,IRIS_INNER,36)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.864,eye_y+.0001,.1034,eye_ry*.235,.00185,PUPIL,28)
"""
new=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileScleraYZV140_{side}',ex+side*eye_rx*.846,eye_y+.0001,.1023,eye_ry*.88,.00720,SCLERA,42)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.858,eye_y+.0002,.1032,eye_ry*.57,.00455,IRIS_INNER,40)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.864,eye_y+.0001,.1037,eye_ry*.265,.00215,PUPIL,30)
"""
if old not in s:
    raise SystemExit('v13.15 exact-profile eye anchor missing')
s=s.replace(old,new,1)

# Lip colour planes already follow the actual face shell. Increase only their shallow relief so the mouth
# catches a soft highlight like the supplied portrait instead of reading as a flat pink decal.
repls=[
 (".00034*FACE120['surface']['lipThickness'],LIP)",".00046*FACE120['surface']['lipThickness'],LIP)"),
 (".00039*FACE120['surface']['lipThickness'],LIP)",".00052*FACE120['surface']['lipThickness'],LIP)"),
 ("],.000075,FACE_DARK)","],.000095,FACE_DARK)"),
]
for old,new in repls:
    if old not in s:
        raise SystemExit(f'v13.15 lip anchor missing: {old}')
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.14';"
new="ROOT['character_revision']='v13.15';"
if old not in s:
    raise SystemExit('v13.15 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.14'","HEAD_ASSET['reference_profile_silhouette']='v13.15'",1)
s=s.replace("FACE_ASSET['profile_eye_volume_revision']='v13.10'","FACE_ASSET['profile_eye_volume_revision']='v13.15'",1)
s=s.replace("FACE_ASSET['profile_iris_volume_revision']='v13.10'","FACE_ASSET['profile_iris_volume_revision']='v13.15'",1)
s=s.replace("FACE_ASSET['profile_sclera_aperture_revision']='v13.10'","FACE_ASSET['profile_sclera_aperture_revision']='v13.15'",1)
needle="FACE_ASSET['portrait_material_revision']='v12.8-pbr';"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['almond_eye_revision']='v13.15';FACE_ASSET['lip_volume_revision']='v13.15';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V145: slimmer frontal eye, restrained iris, larger exact-profile aperture and fuller lip relief')
