from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V130' in s:
    print('Blender heroine generator already carries REFERENCE_V130')
    raise SystemExit(0)
if '# REFERENCE_V129' not in s:
    raise SystemExit('REFERENCE_V129 generator required before v13.0')

marker="# REFERENCE_V129: texture-like radial iris detail uses one tiny indexed mesh per eye, adding warm/dark spokes without image textures or extra draw-call-heavy strand objects."
if marker not in s:
    raise SystemExit('v13.0 REFERENCE_V129 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V130: user-profile reference pass reshapes the nose/lip/chin silhouette toward a smaller rounded nose, flatter muzzle and longer elegant chin without changing the accepted frontal mask.",1)

# Keep the frontal proportions from v12.9. Profile controls move only depth/vertical lower-face shape.
old="nose_proj=profile_ctrl['noseProjection']*.88;nose_width=profile_ctrl['noseWidth']\n forehead_depth=profile_ctrl['foreheadDepth']*1.01;mouth_proj=profile_ctrl['mouthProjection']*1.02\n chin_proj=profile_ctrl['chinProjection']*1.05;chin_len=profile_ctrl['chinLength']*.82"
new="nose_proj=profile_ctrl['noseProjection']*.80;nose_width=profile_ctrl['noseWidth']\n forehead_depth=profile_ctrl['foreheadDepth']*1.01;mouth_proj=profile_ctrl['mouthProjection']*1.00\n chin_proj=profile_ctrl['chinProjection']*1.08;chin_len=profile_ctrl['chinLength']*.86"
if old not in s:
    raise SystemExit('v13.0 profile control anchor missing')
s=s.replace(old,new,1)

# Replace the sharp triangular nasal peak with a smoother compact bridge-tip-base arc. The mouth plane
# stays restrained while the chin recovers a clean forward/downward finish like the supplied side reference.
old=""" base_profile=[
  (.090,.0990),(.060,.1000),(.035,.1030),(.015,.1080),(-.005,.1140),(-.025,.1240),
  (-.044,.1450),(-.054,.1320),(-.063,.1190),(-.069,.1080),(-.077,.1145),(-.086,.1200),
  (-.094,.1215),(-.103,.1130),(-.110,.1050),(-.119,.1160),(-.128,.1120),(-.137,.1000),(-.145,.0860)
 ]
"""
new=""" base_profile=[
  (.090,.0990),(.060,.1000),(.035,.1025),(.015,.1065),(-.005,.1115),(-.025,.1195),
  (-.040,.1300),(-.048,.1350),(-.055,.1325),(-.062,.1220),(-.068,.1110),
  (-.077,.1135),(-.086,.1195),(-.094,.1215),(-.103,.1130),(-.110,.1055),
  (-.119,.1165),(-.128,.1135),(-.137,.1025),(-.145,.0890)
 ]
"""
if old not in s:
    raise SystemExit('v13.0 base profile anchor missing')
s=s.replace(old,new,1)

# Make the visible nose read as one refined rounded form instead of stacking too much local relief on top
# of the new profile cage.
repls=(
("z+=fm*.00380*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)",
 "z+=fm*.00345*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)"),
("z+=fm*.00585*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0105)**2)",
 "z+=fm*.00470*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0115)**2)"),
("z+=fm*.00225*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0080)**2)",
 "z+=fm*.00195*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0085)**2)"),
("z-=fm*.00165*labiomental*math.exp(-(x/.0245)**2-((yy+.1060)/.0075)**2)",
 "z-=fm*.00135*labiomental*math.exp(-(x/.0245)**2-((yy+.1060)/.0082)**2)"),
("z+=fm*.00495*math.exp(-(x/.0315)**2-((yy+.119)/.0180)**2)",
 "z+=fm*.00465*math.exp(-(x/.0305)**2-((yy+.121)/.0195)**2)")
)
for old,new in repls:
    if old not in s:
        raise SystemExit('v13.0 local profile relief anchor missing')
    s=s.replace(old,new,1)

# Keep lip definition after flattening the surrounding muzzle. This is local lip volume only, so the face
# does not gain a protruding muzzle in exact profile.
old="z+=fm*.00265*lip_volume*ul"
new="z+=fm*.00282*lip_volume*ul"
if old not in s: raise SystemExit('v13.0 upper lip anchor missing')
s=s.replace(old,new,1)
old="z+=fm*.00310*lip_volume*ll"
new="z+=fm*.00330*lip_volume*ll"
if old not in s: raise SystemExit('v13.0 lower lip anchor missing')
s=s.replace(old,new,1)

# The nostril tint is only a colour/depth cue; move it back onto the new smaller nose base.
old="side*.0065*FACE120['profile']['noseWidth'],-.0580,.1432,.00215*FACE120['surface']['nostrilScale']"
new="side*.0065*FACE120['profile']['noseWidth'],-.0580,.1368,.00205*FACE120['surface']['nostrilScale']"
if old not in s:
    raise SystemExit('v13.0 nostril cue anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v12.9';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.0';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.0 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V130: smaller rounded reference nose, flatter muzzle, fuller lips and elegant chin profile')
