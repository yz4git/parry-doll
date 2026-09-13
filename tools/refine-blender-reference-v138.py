from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V138' in s:
    print('Blender heroine generator already carries REFERENCE_V138')
    raise SystemExit(0)
if '# REFERENCE_V137' not in s:
    raise SystemExit('REFERENCE_V137 generator required before v13.8')

marker="# REFERENCE_V137: profile-anatomy correction rounds/recedes the chin, lifts the rear underjaw toward a rear-set neck and adds a true side-facing iris/pupil surface plus a small earring cue."
if marker not in s:
    raise SystemExit('v13.8 REFERENCE_V137 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V138: supplied-reference portrait pass softens the nose-tip S-curve, gives the lips a cleaner profile break and strengthens the exact-profile iris/lash silhouette without changing frontal face width.",1)

# Reduce only nose depth; frontal face/jaw/eye spacing stay frozen.
old="nose_proj=profile_ctrl['noseProjection']*.76;nose_width=profile_ctrl['noseWidth']"
new="nose_proj=profile_ctrl['noseProjection']*.73;nose_width=profile_ctrl['noseWidth']"
if old not in s:
    raise SystemExit('v13.8 nose projection anchor missing')
s=s.replace(old,new,1)

# Refine the accepted v13.7 centre-line into a slightly smaller, smoother nose with a cleaner lip S-curve.
old=""" base_profile=[
  (.090,.1005),(.060,.1020),(.035,.1010),(.015,.0995),(-.005,.1035),(-.025,.1125),
  (-.040,.1255),(-.048,.1315),(-.055,.1295),(-.062,.1185),(-.068,.1085),
  (-.077,.1105),(-.086,.1175),(-.094,.1205),(-.103,.1110),(-.111,.1030),
  (-.121,.1168),(-.131,.1150),(-.140,.1040),(-.148,.0870),(-.154,.0710)
 ]
"""
new=""" base_profile=[
  (.090,.1005),(.060,.1017),(.035,.1007),(.015,.0988),(-.005,.1020),(-.025,.1105),
  (-.040,.1235),(-.048,.1287),(-.055,.1272),(-.062,.1168),(-.068,.1078),
  (-.077,.1115),(-.086,.1190),(-.094,.1216),(-.103,.1113),(-.111,.1030),
  (-.121,.1168),(-.131,.1150),(-.140,.1040),(-.148,.0870),(-.154,.0710)
 ]
"""
if old not in s:
    raise SystemExit('v13.8 profile spline anchor missing')
s=s.replace(old,new,1)

# Slightly stronger but still integrated lip volumes. This affects depth, not frontal mouth width.
s=s.replace("z+=fm*.00322*lip_volume*ul","z+=fm*.00340*lip_volume*ul",1)
s=s.replace("z+=fm*.00378*lip_volume*ll","z+=fm*.00398*lip_volume*ll",1)

# Make the true side-facing iris/pupil readable from exact profile. They remain edge-on from front.
old=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.815,eye_y+.0003,.1025,eye_ry*.43,.00255,IRIS_INNER,30)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.822,eye_y+.0002,.1029,eye_ry*.205,.00125,PUPIL,24)
"""
new=""" add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.850,eye_y+.0003,.1027,eye_ry*.54,.00335,IRIS_INNER,34)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.858,eye_y+.0002,.1031,eye_ry*.255,.00165,PUPIL,26)
"""
if old not in s:
    raise SystemExit('v13.8 profile iris plane anchor missing')
s=s.replace(old,new,1)

# The reference eye has a strong fan of upper lashes visible in profile. Keep the frontal lash unchanged and
# add two tiny side-view strands behind the accepted v13.3 profile lash.
old=""" add_strand(HEAD,f'ProfileLashV133_{side}',[(outer-side*.0015,eye_y+eye_tilt+.0030,.10425),(outer+side*.0010,eye_y+eye_tilt+.0050,.1068),(outer+side*.0028,eye_y+eye_tilt+.0042,.1092)],.00024*eye_contrast,HAIR)
"""
new=""" add_strand(HEAD,f'ProfileLashV133_{side}',[(outer-side*.0015,eye_y+eye_tilt+.0030,.10425),(outer+side*.0010,eye_y+eye_tilt+.0050,.1068),(outer+side*.0028,eye_y+eye_tilt+.0042,.1092)],.00031*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashFanV138_A_{side}',[(outer-side*.0008,eye_y+eye_tilt+.0035,.10435),(outer+side*.0018,eye_y+eye_tilt+.0072,.1072),(outer+side*.0035,eye_y+eye_tilt+.0078,.1104)],.00020*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashFanV138_B_{side}',[(outer-side*.0005,eye_y+eye_tilt+.0026,.10430),(outer+side*.0020,eye_y+eye_tilt+.0038,.1078),(outer+side*.0040,eye_y+eye_tilt+.0028,.1100)],.00018*eye_contrast,HAIR)
"""
if old not in s:
    raise SystemExit('v13.8 profile lash anchor missing')
s=s.replace(old,new,1)

# Add two ultra-fine face-framing hairs around the eye/ear transition. They are deliberately thin enough not
# to recreate the old black temple slab.
anchor="# v12.0 modular hair-fit pass: broad temple layers bridge fringe to side/back mass."
if anchor not in s:
    raise SystemExit('v13.8 wisp insertion anchor missing')
insert="""# v13.8 reference eye/ear framing wisps.
for _side in (-1,1):
 add_strand(HEAD,f'ReferenceWispV138_D_{_side}',[(_side*.073,.132,.100),(_side*.079,.090,.105),(_side*.075,.047,.103),(_side*.064,.005,.097),(_side*.056,-.040,.089)],.000022,HAIR_HI)
 add_strand(HEAD,f'ReferenceWispV138_E_{_side}',[(_side*.103,.078,.071),(_side*.105,.038,.077),(_side*.099,-.005,.075),(_side*.088,-.046,.070)],.000020,HAIR)

"""
s=s.replace(anchor,insert+anchor,1)

old="ROOT['character_revision']='v13.7';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.7';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.6';HAIR_ASSET['reference_profile_hair_revision']='v13.6';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.7';FACE_ASSET['profile_iris_volume_revision']='v13.7';FACE_ASSET['profile_side_plane_revision']='v13.7';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.8';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.8';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.8';HAIR_ASSET['reference_profile_hair_revision']='v13.8';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.8';FACE_ASSET['profile_iris_volume_revision']='v13.8';FACE_ASSET['profile_side_plane_revision']='v13.8';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.8 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V138: softer nose/lip S-curve, stronger side iris, profile lash fan and fine eye-ear wisps')
