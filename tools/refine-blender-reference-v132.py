from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V132' in s:
    print('Blender heroine generator already carries REFERENCE_V132')
    raise SystemExit(0)
if '# REFERENCE_V131' not in s:
    raise SystemExit('REFERENCE_V131 generator required before v13.2')

marker="# REFERENCE_V131: profile-silhouette pass opens the eye through finer fringe, adds an orbital-to-bridge break and lengthens the tapered chin toward the supplied side-view reference."
if marker not in s:
    raise SystemExit('v13.2 REFERENCE_V131 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V132: profile-eye/jaw pass strengthens the side-view lash silhouette, clears the near-eye fringe and extends the chin-underjaw flow toward the supplied portrait while preserving the accepted frontal mask.",1)

# Preserve v13.1 upper-face/nose/mouth depth. Extend only the lower face enough to move the chin-to-neck
# transition away from the short horizontal shelf seen in the audit, without widening the frontal jaw.
old="chin_proj=profile_ctrl['chinProjection']*1.10;chin_len=profile_ctrl['chinLength']*.98"
new="chin_proj=profile_ctrl['chinProjection']*1.115;chin_len=profile_ctrl['chinLength']*1.045"
if old not in s:
    raise SystemExit('v13.2 chin control anchor missing')
s=s.replace(old,new,1)

old="""  (-.120,.1175),(-.130,.1140),(-.140,.1010),(-.149,.0845)
 ]
"""
new="""  (-.121,.1182),(-.132,.1148),(-.143,.1000),(-.153,.0815)
 ]
"""
if old not in s:
    raise SystemExit('v13.2 lower profile anchor missing')
s=s.replace(old,new,1)

# Make the near-side eye survive exact profile: slightly stronger upper lid, a longer swept outer lash,
# and a clearer lower-lid edge. Eye aperture/iris size remain unchanged, so the frontal identity is stable.
old="add_strand(HEAD,f'UpperLashV119_{side}',[(inner,eye_y-eye_tilt+.0002,.10402),(ex-side*.0030,eye_y+.01145,.10478),(outer,eye_y+eye_tilt+.0002,.10410)],.00094*eye_contrast,HAIR)"
new="add_strand(HEAD,f'UpperLashV119_{side}',[(inner,eye_y-eye_tilt+.0002,.10402),(ex-side*.0030,eye_y+.01165,.10484),(outer+side*.0012,eye_y+eye_tilt+.00045,.10413)],.00102*eye_contrast,HAIR)"
if old not in s:
    raise SystemExit('v13.2 upper lash anchor missing')
s=s.replace(old,new,1)

old="add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0040,eye_y+eye_tilt+.0015,.10416),(outer+side*.0048,eye_y+eye_tilt+.0042,.10418),(outer+side*.0080,eye_y+eye_tilt+.0030,.10405)],.00048*eye_contrast,HAIR)"
new="add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0036,eye_y+eye_tilt+.0017,.10417),(outer+side*.0058,eye_y+eye_tilt+.0052,.10422),(outer+side*.0108,eye_y+eye_tilt+.0037,.10408)],.00060*eye_contrast,HAIR)"
if old not in s:
    raise SystemExit('v13.2 outer lash anchor missing')
s=s.replace(old,new,1)

old="add_strand(HEAD,f'LowerLidV119_{side}',[(inner+side*.0040,eye_y-eye_tilt-.0004,.10372),(ex,eye_y-.00855,.10400),(outer-side*.0030,eye_y+eye_tilt-.0003,.10380)],.00019*eye_contrast,FACE_DARK)"
new="add_strand(HEAD,f'LowerLidV119_{side}',[(inner+side*.0040,eye_y-eye_tilt-.00035,.10374),(ex,eye_y-.00870,.10403),(outer-side*.0024,eye_y+eye_tilt-.00015,.10383)],.000215*eye_contrast,FACE_DARK)"
if old not in s:
    raise SystemExit('v13.2 lower lid anchor missing')
s=s.replace(old,new,1)

# The supplied reference keeps dense bangs, but the eye sits in a deliberate window. On the near/left
# profile side, thin the two locks that cross the orbital silhouette and lift their terminal tips slightly.
old=""" ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.098,.111),(-.060,.066,.111),(-.070,.036,.106)],[.0070,.0110,.0115,.0075,.0018]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.114,.113),(-.025,.084,.116),(-.037,.056,.111)],[.0070,.0120,.0125,.0082,.0019]),
"""
new=""" ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.100,.111),(-.059,.073,.111),(-.068,.047,.106)],[.0058,.0092,.0094,.0058,.00135]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.116,.113),(-.025,.090,.116),(-.036,.066,.111)],[.0060,.0100,.0104,.0062,.00145]),
"""
if old not in s:
    raise SystemExit('v13.2 near-eye bang anchor missing')
s=s.replace(old,new,1)

# Add two extremely fine side-profile strands outside the eye window. They retain the supplied-reference
# wispy look without recreating the previous black curtain across the eye.
anchor="# v13.1 reference-profile wisps: fine face framing without hiding the eye."
if anchor not in s:
    raise SystemExit('v13.2 wisp anchor missing')
insert="""# v13.2 profile eye-frame strands: fine upper/lower guides around, not across, the near eye.
add_strand(HEAD,'ProfileEyeFrameV132_L_Upper',[(-.058,.110,.112),(-.064,.086,.114),(-.066,.064,.112),(-.062,.048,.108)],.000032,HAIR_HI)
add_strand(HEAD,'ProfileEyeFrameV132_L_Lower',[(-.074,.040,.106),(-.071,.016,.103),(-.064,-.012,.099),(-.058,-.040,.094)],.000030,HAIR)

"""
s=s.replace(anchor,insert+anchor,1)

old="ROOT['character_revision']='v13.1';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.1';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.2';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.2';HEAD_ASSET['chin_underjaw_flow_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.2';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.2 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V132: stronger profile lashes, eye-clear near fringe and longer tapered chin-underjaw flow')
