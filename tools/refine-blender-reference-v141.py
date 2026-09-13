from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V141' in s:
    print('Blender heroine generator already carries REFERENCE_V141')
    raise SystemExit(0)
if '# REFERENCE_V140' not in s:
    raise SystemExit('REFERENCE_V140 generator required before v13.11')

marker="# REFERENCE_V140: exact-profile eye-aperture pass adds a small side-facing sclera aperture with iris/pupil and lid rims so the supplied-reference eye remains readable from 90 degrees while staying nearly edge-on in front view."
if marker not in s:
    raise SystemExit('v13.11 REFERENCE_V140 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V141: swept-temple/ear-exposure pass recesses the side undercap, pulls the front temporal lock behind the ear and adds fine rearward flow strands to match the supplied ponytail profile.",1)

# The scalp undercap previously sat almost flush with the ear's outer X, which made profile hair read as one
# dark plate and hid the ear. Keep crown/root coverage, then tuck the lower half inside the ear silhouette and
# send it rearward in Z. The ear itself remains unchanged.
old=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV105_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.442, head_d*.012,.032,.0012),
  (.098,head_w*.462, head_d*.000,.041,.0015),
  (.068,head_w*.465,-head_d*.014,.041,.0015),
  (.043,head_w*.446,-head_d*.031,.034,.0013),
  (.022,head_w*.421,-head_d*.049,.024,.0010),
  (.004,head_w*.402,-head_d*.067,.015,.0008),
  (-.014,head_w*.406,-head_d*.085,.010,.0007),
  (-.031,head_w*.424,-head_d*.101,.008,.0006),
  (-.045,head_w*.442,-head_d*.113,.003,.0003)
 ],HAIR,17)
"""
new=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV105_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.434, head_d*.008,.030,.0011),
  (.098,head_w*.444,-head_d*.006,.035,.0013),
  (.068,head_w*.436,-head_d*.030,.033,.0012),
  (.043,head_w*.420,-head_d*.052,.028,.0011),
  (.022,head_w*.399,-head_d*.074,.020,.0009),
  (.004,head_w*.384,-head_d*.092,.013,.0007),
  (-.014,head_w*.388,-head_d*.108,.009,.0006),
  (-.031,head_w*.402,-head_d*.122,.006,.0005),
  (-.045,head_w*.416,-head_d*.132,.0025,.0003)
 ],HAIR,17)
"""
if old not in s:
    raise SystemExit('v13.11 temporal undercap anchor missing')
s=s.replace(old,new,1)

# Re-route the visible front temple lock around/behind the ear instead of dropping down as a broad side plate.
old=""" add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.026),
  (side*head_w*.420,.145, head_d*.018),
  (side*head_w*.468,.108, head_d*.006),
  (side*head_w*.486,.068,-head_d*.018),
  (side*head_w*.482,.028,-head_d*.052),
  (side*head_w*.468,.010,-head_d*.088),
  (side*head_w*.442,-.004,-head_d*.118)
 ],[.003,.006,.009,.010,.0085,.005,.0012],[.007,.012,.016,.019,.015,.009,.0028],HAIR,14,6)
"""
new=""" add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.018),
  (side*head_w*.410,.145, head_d*.006),
  (side*head_w*.450,.108,-head_d*.018),
  (side*head_w*.462,.068,-head_d*.052),
  (side*head_w*.452,.030,-head_d*.094),
  (side*head_w*.432,.010,-head_d*.128),
  (side*head_w*.402,-.006,-head_d*.150)
 ],[.0028,.0055,.0072,.0074,.0058,.0036,.0009],[.006,.010,.012,.0125,.0095,.0058,.0020],HAIR,14,6)
"""
if old not in s:
    raise SystemExit('v13.11 front temporal lock anchor missing')
s=s.replace(old,new,1)

# Fine sweep lines carry strand direction across the exposed ear without recreating a solid slab.
anchor="# v13.6 supplied-reference loose profile wisps."
if anchor not in s:
    raise SystemExit('v13.11 temple strand insertion anchor missing')
insert="""# v13.11 supplied-reference swept temple flow around the exposed ear.
for _side in (-1,1):
 add_strand(HEAD,f'TempleSweepV141_A_{_side}',[(_side*head_w*.365,.161,head_d*.018),(_side*head_w*.410,.128,-head_d*.010),(_side*head_w*.438,.086,-head_d*.050),(_side*head_w*.445,.041,-head_d*.091),(_side*head_w*.425,-.004,-head_d*.126)],.000030,HAIR_HI)
 add_strand(HEAD,f'TempleSweepV141_B_{_side}',[(_side*head_w*.350,.150,head_d*.000),(_side*head_w*.397,.113,-head_d*.032),(_side*head_w*.425,.072,-head_d*.067),(_side*head_w*.430,.028,-head_d*.104),(_side*head_w*.408,-.017,-head_d*.136)],.000024,HAIR)
 add_strand(HEAD,f'TempleSweepV141_C_{_side}',[(_side*head_w*.380,.137,-head_d*.018),(_side*head_w*.420,.099,-head_d*.046),(_side*head_w*.444,.055,-head_d*.080),(_side*head_w*.438,.010,-head_d*.116)],.000020,HAIR_HI)

"""
s=s.replace(anchor,insert+anchor,1)

old="ROOT['character_revision']='v13.10';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.10';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.9';HAIR_ASSET['reference_profile_hair_revision']='v13.9';HAIR_ASSET['eye_reveal_fringe_revision']='v13.9';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.10';FACE_ASSET['profile_iris_volume_revision']='v13.10';FACE_ASSET['profile_side_plane_revision']='v13.10';FACE_ASSET['profile_sclera_aperture_revision']='v13.10';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.11';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.11';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.9';HAIR_ASSET['reference_profile_hair_revision']='v13.11';HAIR_ASSET['eye_reveal_fringe_revision']='v13.9';HAIR_ASSET['ear_exposure_revision']='v13.11';HAIR_ASSET['temple_sweep_revision']='v13.11';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.10';FACE_ASSET['profile_iris_volume_revision']='v13.10';FACE_ASSET['profile_side_plane_revision']='v13.10';FACE_ASSET['profile_sclera_aperture_revision']='v13.10';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.11 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V141: recessed temple undercap, rear-swept visible lock and exposed-ear strand flow')
