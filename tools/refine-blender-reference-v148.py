from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V148' in s:
    print('Blender heroine generator already carries REFERENCE_V148')
    raise SystemExit(0)
if '# REFERENCE_V147' not in s:
    raise SystemExit('REFERENCE_V147 generator required before v13.18')

marker="# REFERENCE_V147: continuous-profile silhouette pass rebuilds the centre-line forehead/nasal-root/nose/lip/chin S-curve from the supplied side portrait while leaving frontal widths, eye spacing, jaw width and the accepted neck/hair systems unchanged."
if marker not in s:
    raise SystemExit('v13.18 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V148: exact-profile eye-readability pass enlarges only the YZ side-facing sclera/iris/pupil aperture and moves the profile lids/lashes slightly outward, matching the supplied portrait without changing frontal eye spacing or width.",1)

old=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileScleraYZV140_{side}',ex+side*eye_rx*.846,eye_y+.0001,.1023,eye_ry*.88,.00720,SCLERA,42)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.858,eye_y+.0002,.1032,eye_ry*.57,.00455,IRIS_INNER,40)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.864,eye_y+.0001,.1037,eye_ry*.265,.00215,PUPIL,30)
"""
new=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileScleraYZV140_{side}',ex+side*eye_rx*.870,eye_y+.0001,.1025,eye_ry*.985,.00810,SCLERA,46)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.880,eye_y+.0002,.10345,eye_ry*.625,.00505,IRIS_INNER,42)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.886,eye_y+.0001,.10390,eye_ry*.292,.00242,PUPIL,32)
"""
if old not in s:
    raise SystemExit('v13.18 profile eye-plane anchor missing')
s=s.replace(old,new,1)

old=""" add_strand(HEAD,f'ProfileUpperLidV140_{side}',[(ex+side*eye_rx*.870,eye_y+eye_ry*.66,.1018),(ex+side*eye_rx*.872,eye_y+eye_ry*.30,.1067),(ex+side*eye_rx*.872,eye_y-.0002,.1082)],.00020*eye_contrast,FACE_DARK)
 add_strand(HEAD,f'ProfileLowerLidV140_{side}',[(ex+side*eye_rx*.870,eye_y-eye_ry*.63,.1019),(ex+side*eye_rx*.872,eye_y-eye_ry*.31,.1061),(ex+side*eye_rx*.872,eye_y-.0002,.1080)],.00013*eye_contrast,EYE_WET)
"""
new=""" add_strand(HEAD,f'ProfileUpperLidV140_{side}',[(ex+side*eye_rx*.894,eye_y+eye_ry*.74,.1019),(ex+side*eye_rx*.896,eye_y+eye_ry*.33,.10715),(ex+side*eye_rx*.896,eye_y-.0001,.10865)],.00024*eye_contrast,FACE_DARK)
 add_strand(HEAD,f'ProfileLowerLidV140_{side}',[(ex+side*eye_rx*.894,eye_y-eye_ry*.70,.1020),(ex+side*eye_rx*.896,eye_y-eye_ry*.34,.10655),(ex+side*eye_rx*.896,eye_y-.0001,.10835)],.00015*eye_contrast,EYE_WET)
"""
if old not in s:
    raise SystemExit('v13.18 profile lid anchor missing')
s=s.replace(old,new,1)

# Strengthen only the true side-view lash fan. Frontal upper/outer lashes remain untouched.
s=s.replace(".00023*eye_contrast,HAIR)\n add_strand(HEAD,f'ProfileLashFanV138_B_{side}'",".00027*eye_contrast,HAIR)\n add_strand(HEAD,f'ProfileLashFanV138_B_{side}'",1)
s=s.replace(".00020*eye_contrast,HAIR)\n add_strand(HEAD,f'LowerLidV119_{side}'",".00023*eye_contrast,HAIR)\n add_strand(HEAD,f'LowerLidV119_{side}'",1)

old="ROOT['character_revision']='v13.17';"
new="ROOT['character_revision']='v13.18';"
if old not in s:
    raise SystemExit('v13.18 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.17'","HEAD_ASSET['reference_profile_silhouette']='v13.18'",1)
s=s.replace("FACE_ASSET['profile_eye_volume_revision']='v13.15'","FACE_ASSET['profile_eye_volume_revision']='v13.18'",1)
s=s.replace("FACE_ASSET['profile_iris_volume_revision']='v13.15'","FACE_ASSET['profile_iris_volume_revision']='v13.18'",1)
s=s.replace("FACE_ASSET['profile_sclera_aperture_revision']='v13.15'","FACE_ASSET['profile_sclera_aperture_revision']='v13.18'",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['profile_lid_readability_revision']='v13.18';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V148: larger exact-profile sclera/iris/pupil aperture with outward profile lids and stronger side lashes')
