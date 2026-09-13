from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V140' in s:
    print('Blender heroine generator already carries REFERENCE_V140')
    raise SystemExit(0)
if '# REFERENCE_V139' not in s:
    raise SystemExit('REFERENCE_V139 generator required before v13.10')

marker="# REFERENCE_V139: eye-reveal fringe pass lifts the thick brow-level bang volumes away from the profile eye and replaces their lower continuation with fine face-framing strands, preserving crown coverage and the accepted v13.8 face."
if marker not in s:
    raise SystemExit('v13.10 REFERENCE_V139 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V140: exact-profile eye-aperture pass adds a small side-facing sclera aperture with iris/pupil and lid rims so the supplied-reference eye remains readable from 90 degrees while staying nearly edge-on in front view.",1)

# v13.7/13.8 supplied side-facing iris planes, but without a side-facing sclera aperture the eye still
# collapsed to a dark dot in exact profile. Add a restrained outer sclera ellipse, then layer iris/pupil
# slightly farther outward in X so depth testing is stable from both left and right profile cameras.
old=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.850,eye_y+.0003,.1027,eye_ry*.54,.00335,IRIS_INNER,34)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.858,eye_y+.0002,.1031,eye_ry*.255,.00165,PUPIL,26)
"""
new=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileScleraYZV140_{side}',ex+side*eye_rx*.846,eye_y+.0001,.1023,eye_ry*.73,.00570,SCLERA,38)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.858,eye_y+.0002,.1030,eye_ry*.50,.00370,IRIS_INNER,36)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.864,eye_y+.0001,.1034,eye_ry*.235,.00185,PUPIL,28)
"""
if old not in s:
    raise SystemExit('v13.10 side eye plane anchor missing')
s=s.replace(old,new,1)

# Frame the new aperture with actual side-plane eyelid rims. These curves are almost invisible from front,
# but from exact profile they turn the white oval into an eye rather than a detached highlight.
old=""" add_strand(HEAD,f'ProfileLashV133_{side}',[(outer-side*.0015,eye_y+eye_tilt+.0030,.10425),(outer+side*.0010,eye_y+eye_tilt+.0050,.1068),(outer+side*.0028,eye_y+eye_tilt+.0042,.1092)],.00031*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashFanV138_A_{side}',[(outer-side*.0008,eye_y+eye_tilt+.0035,.10435),(outer+side*.0018,eye_y+eye_tilt+.0072,.1072),(outer+side*.0035,eye_y+eye_tilt+.0078,.1104)],.00020*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashFanV138_B_{side}',[(outer-side*.0005,eye_y+eye_tilt+.0026,.10430),(outer+side*.0020,eye_y+eye_tilt+.0038,.1078),(outer+side*.0040,eye_y+eye_tilt+.0028,.1100)],.00018*eye_contrast,HAIR)
"""
new=""" add_strand(HEAD,f'ProfileLashV133_{side}',[(outer-side*.0015,eye_y+eye_tilt+.0030,.10425),(outer+side*.0010,eye_y+eye_tilt+.0050,.1068),(outer+side*.0028,eye_y+eye_tilt+.0042,.1092)],.00031*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileUpperLidV140_{side}',[(ex+side*eye_rx*.870,eye_y+eye_ry*.66,.1018),(ex+side*eye_rx*.872,eye_y+eye_ry*.30,.1067),(ex+side*eye_rx*.872,eye_y-.0002,.1082)],.00020*eye_contrast,FACE_DARK)
 add_strand(HEAD,f'ProfileLowerLidV140_{side}',[(ex+side*eye_rx*.870,eye_y-eye_ry*.63,.1019),(ex+side*eye_rx*.872,eye_y-eye_ry*.31,.1061),(ex+side*eye_rx*.872,eye_y-.0002,.1080)],.00013*eye_contrast,EYE_WET)
 add_strand(HEAD,f'ProfileLashFanV138_A_{side}',[(outer-side*.0008,eye_y+eye_tilt+.0035,.10435),(outer+side*.0018,eye_y+eye_tilt+.0072,.1072),(outer+side*.0035,eye_y+eye_tilt+.0078,.1104)],.00023*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashFanV138_B_{side}',[(outer-side*.0005,eye_y+eye_tilt+.0026,.10430),(outer+side*.0020,eye_y+eye_tilt+.0038,.1078),(outer+side*.0040,eye_y+eye_tilt+.0028,.1100)],.00020*eye_contrast,HAIR)
"""
if old not in s:
    raise SystemExit('v13.10 profile lid anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.9';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.9';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.9';HAIR_ASSET['reference_profile_hair_revision']='v13.9';HAIR_ASSET['eye_reveal_fringe_revision']='v13.9';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.8';FACE_ASSET['profile_iris_volume_revision']='v13.8';FACE_ASSET['profile_side_plane_revision']='v13.8';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.10';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.10';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.9';HAIR_ASSET['reference_profile_hair_revision']='v13.9';HAIR_ASSET['eye_reveal_fringe_revision']='v13.9';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.10';FACE_ASSET['profile_iris_volume_revision']='v13.10';FACE_ASSET['profile_side_plane_revision']='v13.10';FACE_ASSET['profile_sclera_aperture_revision']='v13.10';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.10 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V140: exact-profile sclera aperture, stronger iris/pupil and side eyelid rims')
