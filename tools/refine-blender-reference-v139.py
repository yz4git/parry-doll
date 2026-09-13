from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V139' in s:
    print('Blender heroine generator already carries REFERENCE_V139')
    raise SystemExit(0)
if '# REFERENCE_V138' not in s:
    raise SystemExit('REFERENCE_V138 generator required before v13.9')

marker="# REFERENCE_V138: supplied-reference portrait pass softens the nose-tip S-curve, gives the lips a cleaner profile break and strengthens the exact-profile iris/lash silhouette without changing frontal face width."
if marker not in s:
    raise SystemExit('v13.9 REFERENCE_V138 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V139: eye-reveal fringe pass lifts the thick brow-level bang volumes away from the profile eye and replaces their lower continuation with fine face-framing strands, preserving crown coverage and the accepted v13.8 face.",1)

# The v11.9 locks are intentionally volumetric, but in exact profile A/B/C formed a single opaque slab over
# the eye. Keep their roots and crown overlap, then taper/retreat the lower samples before the eyelid line.
old="""_bang_specs=[
 ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.100,.111),(-.059,.073,.111),(-.068,.047,.106)],[.0058,.0092,.0094,.0058,.00135]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.116,.113),(-.025,.090,.116),(-.036,.066,.111)],[.0060,.0100,.0104,.0062,.00145]),
 ('C',[(-.016,.199,.051),(-.003,.160,.091),(.012,.124,.112),(.018,.096,.117),(.010,.070,.114)],[.0065,.0115,.0120,.0080,.0018]),
 ('D',[(.017,.198,.050),(.028,.160,.088),(.040,.126,.109),(.050,.100,.114),(.056,.076,.110)],[.0065,.0110,.0120,.0080,.0018]),
 ('E',[(.047,.187,.066),(.061,.151,.094),(.073,.118,.107),(.081,.091,.108),(.087,.066,.103)],[.0070,.0115,.0120,.0075,.0017])
]
for _name,_pts,_widths in _bang_specs:
 add_smooth_lock(HEAD,f'KeyArtBangV119_{_name}',_pts,_widths,[.0045,.0060,.0062,.0046,.0012],HAIR,12,6)
"""
new="""_bang_specs=[
 ('A',[(-.072,.172,.081),(-.061,.139,.098),(-.052,.108,.104),(-.060,.088,.101),(-.070,.073,.095)],[.0048,.0075,.0068,.0035,.00070]),
 ('B',[(-.046,.188,.064),(-.032,.153,.093),(-.020,.124,.105),(-.027,.103,.105),(-.039,.084,.099)],[.0050,.0080,.0072,.0038,.00075]),
 ('C',[(-.016,.199,.050),(-.003,.162,.088),(.012,.130,.104),(.018,.108,.107),(.010,.088,.103)],[.0054,.0088,.0078,.0042,.00085]),
 ('D',[(.017,.198,.049),(.028,.162,.086),(.040,.132,.102),(.050,.111,.105),(.056,.091,.101)],[.0054,.0086,.0078,.0042,.00085]),
 ('E',[(.047,.187,.063),(.061,.153,.090),(.073,.124,.100),(.081,.104,.101),(.087,.086,.096)],[.0058,.0090,.0080,.0040,.00080])
]
for _name,_pts,_widths in _bang_specs:
 add_smooth_lock(HEAD,f'KeyArtBangV119_{_name}',_pts,_widths,[.0034,.0045,.0042,.0026,.00065],HAIR,12,6)
"""
if old not in s:
    raise SystemExit('v13.9 key-art bang volume anchor missing')
s=s.replace(old,new,1)

# Thin lower continuations now cross the face as individual hairs rather than a single solid volume.
# They arc around the eye centre so the sclera/iris/lash work from v13.7/13.8 remains visible in profile.
anchor="# Fine warm highlights trace only three locks, keeping the mass dark while revealing strand direction."
if anchor not in s:
    raise SystemExit('v13.9 fringe strand insertion anchor missing')
insert="""# v13.9 reference-like eye-reveal fringe continuations.
for _side in (-1,1):
 add_strand(HEAD,f'EyeRevealFringeV139_A_{_side}',[(_side*.055,.111,.105),(_side*.062,.083,.104),(_side*.064,.057,.101),(_side*.058,.030,.097),(_side*.052,-.004,.093)],.000022,HAIR)
 add_strand(HEAD,f'EyeRevealFringeV139_B_{_side}',[(_side*.037,.124,.106),(_side*.044,.094,.108),(_side*.047,.067,.106),(_side*.043,.041,.102),(_side*.037,.012,.098)],.000018,HAIR_HI)
 add_strand(HEAD,f'EyeRevealFringeV139_C_{_side}',[(_side*.078,.101,.097),(_side*.081,.074,.099),(_side*.078,.047,.097),(_side*.070,.018,.092),(_side*.063,-.020,.087)],.000019,HAIR)

"""
s=s.replace(anchor,insert+anchor,1)

# Pull the old left/right profile wisps a few millimetres farther from the eye centre; keep their lower cheek
# framing because it matches the supplied image well.
old="add_strand(HEAD,'ProfileWispV131_L',[(-.076,.122,.108),(-.083,.082,.107),(-.080,.045,.097),(-.068,-.006,.093),(-.058,-.060,.094)],.000040,HAIR)"
new="add_strand(HEAD,'ProfileWispV131_L',[(-.076,.122,.106),(-.084,.086,.102),(-.082,.052,.092),(-.070,-.002,.089),(-.058,-.060,.094)],.000032,HAIR)"
if old not in s:
    raise SystemExit('v13.9 left profile wisp anchor missing')
s=s.replace(old,new,1)
old="add_strand(HEAD,'ProfileWispV131_R',[(.078,.126,.106),(.086,.086,.109),(.084,.042,.106),(.073,.004,.100),(.064,-.032,.095)],.000042,HAIR_HI)"
new="add_strand(HEAD,'ProfileWispV131_R',[(.078,.126,.104),(.087,.090,.103),(.086,.054,.096),(.075,.008,.093),(.064,-.032,.095)],.000034,HAIR_HI)"
if old not in s:
    raise SystemExit('v13.9 right profile wisp anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.8';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.8';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.8';HAIR_ASSET['reference_profile_hair_revision']='v13.8';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.8';FACE_ASSET['profile_iris_volume_revision']='v13.8';FACE_ASSET['profile_side_plane_revision']='v13.8';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.9';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.9';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.9';HAIR_ASSET['reference_profile_hair_revision']='v13.9';HAIR_ASSET['eye_reveal_fringe_revision']='v13.9';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.8';FACE_ASSET['profile_iris_volume_revision']='v13.8';FACE_ASSET['profile_side_plane_revision']='v13.8';FACE_ASSET['reference_nose_lip_revision']='v13.8';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.9 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V139: tapered eye-reveal bang volumes with fine layered face-framing fringe')
