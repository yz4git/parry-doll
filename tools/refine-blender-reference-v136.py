from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V136' in s:
    print('Blender heroine generator already carries REFERENCE_V136')
    raise SystemExit(0)
if '# REFERENCE_V135' not in s:
    raise SystemExit('REFERENCE_V135 generator required before v13.6')

marker="# REFERENCE_V135: supplied-reference silhouette pass refines the small nose/lip/chin S-curve, exposes more neck below the jaw and adds a near-side iris crescent for exact-profile readability."
if marker not in s:
    raise SystemExit('v13.6 REFERENCE_V135 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V136: supplied-reference hair-profile pass warms the dark hair, reveals the ear, converts the cheek-side slab into fine layered locks and adds a restrained metallic pony ornament plus loose wisps.",1)

# Reference hair is near-black brown rather than absolute black; keep it dark while allowing strand direction to read.
s=s.replace("HAIR=material('Hair',(0.020,0.014,0.019),0.0,.54)","HAIR=material('Hair',(0.028,0.019,0.022),0.0,.51)",1)
s=s.replace("HAIR_HI=material('Hair Highlight',(0.045,0.029,0.036),0.0,.54)","HAIR_HI=material('Hair Highlight',(0.072,0.046,0.050),0.0,.50)",1)
s=s.replace("for _hair_mat,_spec in ((HAIR,.14),(HAIR_HI,.18)):","for _hair_mat,_spec in ((HAIR,.16),(HAIR_HI,.21)):",1)

# Make the visible ear closer to the supplied profile: slightly taller, a little farther forward and less buried.
old="add_sphere(HEAD,f'EarV103_{side}',(side*.1265,-.020,-.020),(.0120,.0305,.0145),SKIN,28,18)"
new="add_sphere(HEAD,f'EarV103_{side}',(side*.1265,-.020,-.012),(.0122,.0350,.0170),SKIN,30,20)"
if old not in s:
    raise SystemExit('v13.6 ear anchor missing')
s=s.replace(old,new,1)

# The broad v12 temple bridge reads as a single black cheek slab in profile. Preserve scalp coverage at the root,
# but narrow/deepen the visible lock and sweep its lower half rearward so the eye/ear/jaw remain readable.
old="""for _side in (-1,1):
 _sw=ASSEMBLY120['hair']['templeLockWidth'];_sd=ASSEMBLY120['hair']['templeLockDepth']
 _pts=[(_side*.086,.170,.055),(_side*.098,.132,.083),(_side*.106,.090,.100),(_side*.108,.045,.103),(_side*.102,.000,.097),(_side*.094,-.036,.086)]
 _widths=[_sw*.70,_sw, _sw*1.04,_sw*.88,_sw*.62,_sw*.24]
 _depths=[_sd*.72,_sd,_sd*1.02,_sd*.88,_sd*.60,_sd*.20]
 add_smooth_lock(HEAD,f'TempleLayerV120_{_side}',_pts,_widths,_depths,HAIR,12,6)
 add_strand(HEAD,f'TempleLayerHiV120_{_side}',[(_side*.087,.165,.060),(_side*.099,.126,.089),(_side*.106,.080,.102),(_side*.101,.002,.098)],.000050,HAIR_HI)
"""
new="""for _side in (-1,1):
 _sw=ASSEMBLY120['hair']['templeLockWidth']*.62;_sd=ASSEMBLY120['hair']['templeLockDepth']*.56
 _pts=[(_side*.086,.170,.052),(_side*.098,.132,.075),(_side*.106,.090,.090),(_side*.108,.045,.084),(_side*.102,.000,.069),(_side*.094,-.036,.054)]
 _widths=[_sw*.70,_sw, _sw*1.04,_sw*.88,_sw*.62,_sw*.20]
 _depths=[_sd*.72,_sd,_sd*1.02,_sd*.88,_sd*.60,_sd*.18]
 add_smooth_lock(HEAD,f'TempleLayerV120_{_side}',_pts,_widths,_depths,HAIR,12,6)
 add_strand(HEAD,f'TempleLayerHiV120_{_side}',[(_side*.087,.165,.057),(_side*.099,.126,.081),(_side*.106,.080,.091),(_side*.101,.002,.070)],.000038,HAIR_HI)
"""
if old not in s:
    raise SystemExit('v13.6 temple layer anchor missing')
s=s.replace(old,new,1)

# Sweep the lowest front temporal lock behind the ear instead of letting it sit directly over the ear silhouette.
old="""  (side*head_w*.486,.068,-head_d*.010),
  (side*head_w*.482,.028,-head_d*.027),
  (side*head_w*.468,.010,-head_d*.050),
  (side*head_w*.442,-.004,-head_d*.075)
"""
new="""  (side*head_w*.486,.068,-head_d*.018),
  (side*head_w*.482,.028,-head_d*.052),
  (side*head_w*.468,.010,-head_d*.088),
  (side*head_w*.442,-.004,-head_d*.118)
"""
if old not in s:
    raise SystemExit('v13.6 temporal sweep anchor missing')
s=s.replace(old,new,1)

# Add fine, deliberately separated face-framing hairs like the supplied image. These are hairline-thin curves,
# not broad sheets, so they enrich the side silhouette without hiding the eye.
anchor="# v12.0 modular hair-fit pass: broad temple layers bridge fringe to side/back mass."
if anchor not in s:
    raise SystemExit('v13.6 face-wisp insertion anchor missing')
insert="""# v13.6 supplied-reference loose profile wisps.
for _side in (-1,1):
 add_strand(HEAD,f'ReferenceWispV136_A_{_side}',[(_side*.080,.118,.103),(_side*.085,.072,.107),(_side*.078,.020,.103),(_side*.066,-.035,.095),(_side*.057,-.082,.086)],.000032,HAIR)
 add_strand(HEAD,f'ReferenceWispV136_B_{_side}',[(_side*.067,.145,.094),(_side*.073,.098,.102),(_side*.070,.052,.104),(_side*.058,.006,.098),(_side*.050,-.050,.091)],.000028,HAIR_HI)
 add_strand(HEAD,f'ReferenceWispV136_C_{_side}',[(_side*.095,.088,.080),(_side*.098,.040,.086),(_side*.090,-.010,.083),(_side*.078,-.055,.077)],.000026,HAIR)

"""
s=s.replace(anchor,insert+anchor,1)

# A restrained metallic vertical ornament beside the pony root echoes the supplied futuristic hair hardware.
anchor2="add_box(HEAD,'HairTieV59',(.014,.138,-head_d*.530),(.072,.017,.027),SILVER,.003)"
if anchor2 not in s:
    raise SystemExit('v13.6 hair ornament anchor missing')
ornament="""for _side in (-1,1):
 add_box(HEAD,f'ProfileHairOrnamentV136_{_side}',(_side*.105,.090,-head_d*.365),(.011,.145,.013),SILVER,.0025,rot=(0,0,-_side*.055))
 add_box(HEAD,f'ProfileHairOrnamentTipV136_{_side}',(_side*.106,.016,-head_d*.365),(.016,.026,.016),SILVER,.003)
"""
s=s.replace(anchor2,ornament+anchor2,1)

old="ROOT['character_revision']='v13.5';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.5';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.5';HEAD_ASSET['reference_neck_revision']='v13.5';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.3';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.5';FACE_ASSET['profile_iris_volume_revision']='v13.5';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.6';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.6';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.5';HEAD_ASSET['reference_neck_revision']='v13.5';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.6';HAIR_ASSET['reference_profile_hair_revision']='v13.6';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.5';FACE_ASSET['profile_iris_volume_revision']='v13.5';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.6 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V136: warmer layered hair, exposed ear, fine profile wisps and metallic pony ornament')
