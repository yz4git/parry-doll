from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V131' in s:
    print('Blender heroine generator already carries REFERENCE_V131')
    raise SystemExit(0)
if '# REFERENCE_V130' not in s:
    raise SystemExit('REFERENCE_V130 generator required before v13.1')

marker="# REFERENCE_V130: user-profile reference pass reshapes the nose/lip/chin silhouette toward a smaller rounded nose, flatter muzzle and longer elegant chin without changing the accepted frontal mask."
if marker not in s:
    raise SystemExit('v13.1 REFERENCE_V130 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V131: profile-silhouette pass opens the eye through finer fringe, adds an orbital-to-bridge break and lengthens the tapered chin toward the supplied side-view reference.",1)

# Keep the v13.0 nose/mouth depth, but recover a slightly longer, cleaner lower-face finish.
old="chin_proj=profile_ctrl['chinProjection']*1.08;chin_len=profile_ctrl['chinLength']*.86"
new="chin_proj=profile_ctrl['chinProjection']*1.10;chin_len=profile_ctrl['chinLength']*.98"
if old not in s:
    raise SystemExit('v13.1 chin control anchor missing')
s=s.replace(old,new,1)

# Create the reference-like forehead -> orbital recess -> slim bridge -> rounded tip progression.
old=""" base_profile=[
  (.090,.0990),(.060,.1000),(.035,.1025),(.015,.1065),(-.005,.1115),(-.025,.1195),
  (-.040,.1300),(-.048,.1350),(-.055,.1325),(-.062,.1220),(-.068,.1110),
  (-.077,.1135),(-.086,.1195),(-.094,.1215),(-.103,.1130),(-.110,.1055),
  (-.119,.1165),(-.128,.1135),(-.137,.1025),(-.145,.0890)
 ]
"""
new=""" base_profile=[
  (.090,.0990),(.060,.0995),(.035,.0985),(.015,.1020),(-.005,.1070),(-.025,.1150),
  (-.040,.1275),(-.048,.1345),(-.055,.1320),(-.062,.1220),(-.068,.1110),
  (-.077,.1130),(-.086,.1190),(-.094,.1215),(-.103,.1125),(-.110,.1045),
  (-.120,.1175),(-.130,.1140),(-.140,.1010),(-.149,.0845)
 ]
"""
if old not in s:
    raise SystemExit('v13.1 base profile anchor missing')
s=s.replace(old,new,1)

# The reference hairstyle has dense bangs but the near eye remains readable in exact profile. Reduce
# the five chunky face locks into narrower layered blades while preserving the overall dark fringe mass.
old="""_bang_specs=[
 ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.096,.111),(-.061,.055,.111),(-.073,.022,.106)],[.010,.016,.017,.013,.0028]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.112,.113),(-.026,.077,.116),(-.039,.047,.111)],[.010,.018,.019,.014,.0030]),
 ('C',[(-.016,.199,.051),(-.003,.160,.091),(.012,.122,.112),(.018,.091,.117),(.010,.061,.114)],[.009,.017,.018,.013,.0028]),
 ('D',[(.017,.198,.050),(.028,.160,.088),(.040,.124,.109),(.050,.095,.114),(.056,.069,.110)],[.009,.016,.018,.013,.0028]),
 ('E',[(.047,.187,.066),(.061,.151,.094),(.073,.116,.107),(.081,.084,.108),(.087,.056,.103)],[.010,.017,.018,.012,.0025])
]
"""
new="""_bang_specs=[
 ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.098,.111),(-.060,.066,.111),(-.070,.036,.106)],[.0070,.0110,.0115,.0075,.0018]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.114,.113),(-.025,.084,.116),(-.037,.056,.111)],[.0070,.0120,.0125,.0082,.0019]),
 ('C',[(-.016,.199,.051),(-.003,.160,.091),(.012,.124,.112),(.018,.096,.117),(.010,.070,.114)],[.0065,.0115,.0120,.0080,.0018]),
 ('D',[(.017,.198,.050),(.028,.160,.088),(.040,.126,.109),(.050,.100,.114),(.056,.076,.110)],[.0065,.0110,.0120,.0080,.0018]),
 ('E',[(.047,.187,.066),(.061,.151,.094),(.073,.118,.107),(.081,.091,.108),(.087,.066,.103)],[.0070,.0115,.0120,.0075,.0017])
]
"""
if old not in s:
    raise SystemExit('v13.1 bang silhouette anchor missing')
s=s.replace(old,new,1)

# Add two hairline-fine profile wisps like the supplied reference; unlike the old thick cheek lock these
# do not cover the eye or change the mobile silhouette into a black bar.
anchor="# v12.0 modular hair-fit pass: broad temple layers bridge fringe to side/back mass."
if anchor not in s:
    raise SystemExit('v13.1 profile wisp anchor missing')
insert="""# v13.1 reference-profile wisps: fine face framing without hiding the eye.
add_strand(HEAD,'ProfileWispV131_L',[(-.076,.122,.108),(-.083,.078,.111),(-.080,.028,.108),(-.068,-.020,.101),(-.058,-.060,.094)],.000045,HAIR)
add_strand(HEAD,'ProfileWispV131_R',[(.078,.126,.106),(.086,.086,.109),(.084,.042,.106),(.073,.004,.100),(.064,-.032,.095)],.000042,HAIR_HI)

"""
s=s.replace(anchor,insert+anchor,1)

old="ROOT['character_revision']='v13.0';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.1';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.1';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.1 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V131: eye-clear layered fringe, orbital bridge break and longer tapered chin profile')
