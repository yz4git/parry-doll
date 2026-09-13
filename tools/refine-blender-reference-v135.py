from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V135' in s:
    print('Blender heroine generator already carries REFERENCE_V135')
    raise SystemExit(0)
if '# REFERENCE_V134' not in s:
    raise SystemExit('REFERENCE_V134 generator required before v13.5')

marker="# REFERENCE_V134: profile-iris/underjaw pass embeds a mostly buried iris volume for side-view gaze and lifts the rear under-chin cap toward the neck for the supplied elegant jawline."
if marker not in s:
    raise SystemExit('v13.5 REFERENCE_V134 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V135: supplied-reference silhouette pass refines the small nose/lip/chin S-curve, exposes more neck below the jaw and adds a near-side iris crescent for exact-profile readability.",1)

# Push the lower-face proportions toward the supplied elegant side-view without widening the accepted frontal mask.
old="nose_proj=profile_ctrl['noseProjection']*.80;nose_width=profile_ctrl['noseWidth']\n forehead_depth=profile_ctrl['foreheadDepth']*1.01;mouth_proj=profile_ctrl['mouthProjection']*1.00\n chin_proj=profile_ctrl['chinProjection']*1.115;chin_len=profile_ctrl['chinLength']*1.045"
new="nose_proj=profile_ctrl['noseProjection']*.76;nose_width=profile_ctrl['noseWidth']\n forehead_depth=profile_ctrl['foreheadDepth']*1.01;mouth_proj=profile_ctrl['mouthProjection']*1.08\n chin_proj=profile_ctrl['chinProjection']*1.13;chin_len=profile_ctrl['chinLength']*1.06"
if old not in s:
    raise SystemExit('v13.5 profile controls anchor missing')
s=s.replace(old,new,1)

# A more reference-like centre-line: shallow orbital root, restrained rounded tip, readable lips and a soft pointed chin.
old=""" base_profile=[
  (.090,.0990),(.060,.0995),(.035,.0985),(.015,.1020),(-.005,.1070),(-.025,.1150),
  (-.040,.1275),(-.048,.1345),(-.055,.1320),(-.062,.1220),(-.068,.1110),
  (-.077,.1130),(-.086,.1190),(-.094,.1215),(-.103,.1125),(-.110,.1045),
  (-.121,.1182),(-.132,.1148),(-.143,.1000),(-.153,.0815)
 ]
"""
new=""" base_profile=[
  (.090,.1005),(.060,.1020),(.035,.1010),(.015,.0995),(-.005,.1035),(-.025,.1125),
  (-.040,.1255),(-.048,.1315),(-.055,.1295),(-.062,.1185),(-.068,.1085),
  (-.077,.1105),(-.086,.1175),(-.094,.1205),(-.103,.1110),(-.111,.1030),
  (-.123,.1200),(-.135,.1155),(-.146,.0975),(-.155,.0755)
 ]
"""
if old not in s:
    raise SystemExit('v13.5 base profile anchor missing')
s=s.replace(old,new,1)

# The reference has soft but clearly readable lips in profile. Increase integrated lip volume only; no floating lip mesh.
s=s.replace("z+=fm*.00282*lip_volume*ul","z+=fm*.00322*lip_volume*ul",1)
s=s.replace("z+=fm*.00330*lip_volume*ll","z+=fm*.00378*lip_volume*ll",1)

# Lift only the lowest front-centre samples slightly so chin -> underjaw -> neck forms an oblique line rather than a shelf.
old="""   render_y=yy
   if yy<-.112:
    under=max(0.0,min(1.0,(-yy-.112)/.045))
    frontness=max(0.0,sp)
    render_y+=.0105*under*(1.0-frontness**1.55)
   verts.append(bpos((x,render_y,z)))
"""
new="""   render_y=yy
   if yy<-.112:
    under=max(0.0,min(1.0,(-yy-.112)/.045))
    frontness=max(0.0,sp)
    render_y+=.0105*under*(1.0-frontness**1.55)
    # Keep the chin tip low, but lift the throat-side continuation after it so the underside rises toward the neck.
    throat=max(0.0,min(1.0,(-yy-.132)/.023))
    render_y+=.0038*throat*frontness
   verts.append(bpos((x,render_y,z)))
"""
if old not in s:
    raise SystemExit('v13.5 jaw slope anchor missing')
s=s.replace(old,new,1)

# The buried central iris volume is still hidden from exact profile by the wider sclera globe. Add a tiny
# near-side limbal/iris crescent that reaches the visible globe surface. It is small enough to read as
# natural outer-eye shading from front, but produces the dark iris sliver present in the supplied profile.
old=""" add_sphere(HEAD,f'EyeIrisVolumeV134_{side}',(ex,eye_y-.00010,.09915),(eye_rx*.285,eye_ry*.48,.00495),IRIS,28,18)
 add_sphere(HEAD,f'EyePupilVolumeV134_{side}',(ex,eye_y-.00025,.10055),(eye_rx*.105,eye_ry*.235,.00355),PUPIL,24,16)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
new=""" add_sphere(HEAD,f'EyeIrisVolumeV134_{side}',(ex,eye_y-.00010,.09915),(eye_rx*.285,eye_ry*.48,.00495),IRIS,28,18)
 add_sphere(HEAD,f'EyePupilVolumeV134_{side}',(ex,eye_y-.00025,.10055),(eye_rx*.105,eye_ry*.235,.00355),PUPIL,24,16)
 add_sphere(HEAD,f'EyeProfileIrisV135_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.10010),(eye_rx*.175,eye_ry*.34,.00325),IRIS_INNER,22,14)
 add_sphere(HEAD,f'EyeProfilePupilV135_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10105),(eye_rx*.060,eye_ry*.17,.00225),PUPIL,18,12)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
if old not in s:
    raise SystemExit('v13.5 profile iris anchor missing')
s=s.replace(old,new,1)

# Expose a longer, slimmer skin neck before the black collar, matching the supplied portrait silhouette.
old="""add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
"""
new="""add_cylinder(HEAD,'Neck',(0,-.181,-.010),W('neck')*.305,.132,SKIN,28)
add_cylinder(HEAD,'Choker',(0,-.204,-.009),W('neck')*.44,.038,BLACK,30)
add_cylinder(HEAD,'ChokerTrim',(0,-.184,-.009),W('neck')*.45,.008,SILVER,30)
"""
if old not in s:
    raise SystemExit('v13.5 neck/choker anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.4';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.4';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.4';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.3';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.4';FACE_ASSET['profile_iris_volume_revision']='v13.4';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.5';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.5';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.5';HEAD_ASSET['reference_neck_revision']='v13.5';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.3';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.5';FACE_ASSET['profile_iris_volume_revision']='v13.5';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.5 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V135: refined reference S-profile, readable lips, profile iris crescent and longer exposed neck')
