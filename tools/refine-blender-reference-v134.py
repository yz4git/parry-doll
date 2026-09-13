from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V134' in s:
    print('Blender heroine generator already carries REFERENCE_V134')
    raise SystemExit(0)
if '# REFERENCE_V133' not in s:
    raise SystemExit('REFERENCE_V133 generator required before v13.4')

marker="# REFERENCE_V133: volumetric profile-eye pass embeds a shallow sclera globe and side-swept lash fin so the eye remains readable in exact profile instead of collapsing to an edge-on plane."
if marker not in s:
    raise SystemExit('v13.4 REFERENCE_V133 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V134: profile-iris/underjaw pass embeds a mostly buried iris volume for side-view gaze and lifts the rear under-chin cap toward the neck for the supplied elegant jawline.",1)

# The sclera volume fixed exact-profile visibility. Add a smaller iris ellipsoid whose front stays just behind
# the accepted flat iris layers; from front it is hidden, from profile it supplies the dark eye core seen in reference.
old=""" add_sphere(HEAD,f'EyeScleraGlobeV133_{side}',(ex,eye_y,.0936),(eye_rx*.82,eye_ry*.88,.0107),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
new=""" add_sphere(HEAD,f'EyeScleraGlobeV133_{side}',(ex,eye_y,.0936),(eye_rx*.82,eye_ry*.88,.0107),SCLERA,34,22)
 add_sphere(HEAD,f'EyeIrisVolumeV134_{side}',(ex,eye_y-.00010,.09915),(eye_rx*.285,eye_ry*.48,.00495),IRIS,28,18)
 add_sphere(HEAD,f'EyePupilVolumeV134_{side}',(ex,eye_y-.00025,.10055),(eye_rx*.105,eye_ry*.235,.00355),PUPIL,24,16)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
if old not in s:
    raise SystemExit('v13.4 iris volume anchor missing')
s=s.replace(old,new,1)

# The old bottom cap ended at nearly the same vertical level as the front chin, producing a horizontal shelf.
# Lift only the rear/central under-chin pole. The visible centre-front chin section remains v13.3.
old="bottom_y=-.105+(-.147+.105)*chin_len"
new="bottom_y=-.105+(-.147+.105)*chin_len*.58"
if old not in s:
    raise SystemExit('v13.4 underchin pole anchor missing')
s=s.replace(old,new,1)

# Strengthen the v13.3 side/rear lift a little so the section rings meet the raised cap as one smooth slope.
old="render_y+=.0075*under*(1.0-frontness**1.5)"
new="render_y+=.0105*under*(1.0-frontness**1.55)"
if old not in s:
    raise SystemExit('v13.4 underjaw lift anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.3';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.3';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.3';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.3';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.3';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.4';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.4';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.4';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.3';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.4';FACE_ASSET['profile_iris_volume_revision']='v13.4';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.4 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V134: buried iris/pupil volumes and raised rear under-chin pole for reference profile')
