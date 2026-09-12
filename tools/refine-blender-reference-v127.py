from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V127' in s:
    print('Blender heroine generator already carries REFERENCE_V127')
    raise SystemExit(0)
if '# REFERENCE_V126' not in s:
    raise SystemExit('REFERENCE_V126 generator required before v12.7')

marker="# REFERENCE_V126: compact adult-anime face pass shortens the lower face, opens the gaze slightly and broadens the cheek plane without changing combat/head pivots."
if marker not in s:
    raise SystemExit('v12.7 REFERENCE_V126 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V127: profile-balance pass reduces excessive nasal projection and restores a cleaner nose-lip-chin S-curve while preserving the accepted v12.6 frontal mask.",1)

# Preserve frontal x/y proportions from v12.6 and alter only profile-depth multipliers.
old="nose_proj=profile_ctrl['noseProjection'];nose_width=profile_ctrl['noseWidth']\n forehead_depth=profile_ctrl['foreheadDepth'];mouth_proj=profile_ctrl['mouthProjection']\n chin_proj=profile_ctrl['chinProjection'];chin_len=profile_ctrl['chinLength']*.82"
new="nose_proj=profile_ctrl['noseProjection']*.88;nose_width=profile_ctrl['noseWidth']\n forehead_depth=profile_ctrl['foreheadDepth']*1.01;mouth_proj=profile_ctrl['mouthProjection']*1.02\n chin_proj=profile_ctrl['chinProjection']*1.05;chin_len=profile_ctrl['chinLength']*.82"
if old not in s:
    raise SystemExit('v12.7 profile control anchor missing')
s=s.replace(old,new,1)

# v12.5 increased local nasal relief for frontal readability. With the profile cage now balanced,
# reduce only the centreline bridge/tip relief slightly so the exact profile does not double-count it.
repls=(
("z+=fm*.00415*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)",
 "z+=fm*.00380*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)"),
("z+=fm*.00670*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0105)**2)",
 "z+=fm*.00585*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0105)**2)"),
("z+=fm*.00245*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0080)**2)",
 "z+=fm*.00225*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0080)**2)")
)
for old,new in repls:
    if old not in s:
        raise SystemExit('v12.7 nasal relief anchor missing')
    s=s.replace(old,new,1)

# Keep the nostril colour cue seated on the reduced nose base instead of hovering in front.
old="side*.0065*FACE120['profile']['noseWidth'],-.0580,.1485,.00215*FACE120['surface']['nostrilScale']"
new="side*.0065*FACE120['profile']['noseWidth'],-.0580,.1432,.00215*FACE120['surface']['nostrilScale']"
if old not in s:
    raise SystemExit('v12.7 nostril depth anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v12.6';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v12.7';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v12.7 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V127: balanced nose/lip/chin profile while preserving v12.6 frontal proportions')
