from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V126' in s:
    print('Blender heroine generator already carries REFERENCE_V126')
    raise SystemExit(0)
if '# REFERENCE_V125' not in s:
    raise SystemExit('REFERENCE_V125 generator required before v12.6')

marker="# REFERENCE_V125: facial-depth and eye-material pass strengthens orbital/nasal/cheek planes and mobile-scale gaze without changing the modular expression pivots."
s=s.replace(marker,marker+"\n# REFERENCE_V126: compact adult-anime face pass shortens the lower face, opens the gaze slightly and broadens the cheek plane without changing combat/head pivots.",1)

# The portrait still reads slightly long and narrow in the v12.5 front audit.  Keep the reference
# profile and expression pivots, but make the visible facial mask a little broader while compressing
# only the lower-chin segment below the mouth.
old="fw=frontal['faceWidth'];jaw=frontal['jaw'];cheek=frontal['cheekVolume']"
new="fw=frontal['faceWidth']*1.025;jaw=frontal['jaw']*.975;cheek=frontal['cheekVolume']*1.045"
if old not in s: raise SystemExit('v12.6 face width anchor missing')
s=s.replace(old,new,1)
old="chin_proj=profile_ctrl['chinProjection'];chin_len=profile_ctrl['chinLength']"
new="chin_proj=profile_ctrl['chinProjection'];chin_len=profile_ctrl['chinLength']*.82"
if old not in s: raise SystemExit('v12.6 chin length anchor missing')
s=s.replace(old,new,1)

# Mobile-scale eye aperture: enlarge the actual almond surface modestly rather than only making the
# iris bigger.  This keeps the adult gaze while preventing the eyes from collapsing to tiny dots.
old="eye_rx=.0277*ASSEMBLY120['head']['eyeSize']\neye_ry=.01015*ASSEMBLY120['head']['eyeSize']"
new="eye_rx=.02865*ASSEMBLY120['head']['eyeSize']\neye_ry=.01090*ASSEMBLY120['head']['eyeSize']"
if old not in s: raise SystemExit('v12.6 eye aperture anchor missing')
s=s.replace(old,new,1)

# Bring the visible lip planes fractionally upward and widen their outer corners.  The geometry below
# already contains volumetric lips; this is only the color/readability layer.
repls=(
("(-.0280*FACE120['frontal']['mouthWidth'],-.0845,.1268)","(-.0294*FACE120['frontal']['mouthWidth'],-.0835,.1268)"),
("(.0280*FACE120['frontal']['mouthWidth'],-.0845,.1268)","(.0294*FACE120['frontal']['mouthWidth'],-.0835,.1268)"),
("(-.0268*FACE120['frontal']['mouthWidth'],-.0884,.1273)","(-.0282*FACE120['frontal']['mouthWidth'],-.0878,.1273)"),
("(.0268*FACE120['frontal']['mouthWidth'],-.0884,.1273)","(.0282*FACE120['frontal']['mouthWidth'],-.0878,.1273)"),
("(-.0268*FACE120['frontal']['mouthWidth'],-.0886,.1272)","(-.0282*FACE120['frontal']['mouthWidth'],-.0880,.1272)"),
("(.0268*FACE120['frontal']['mouthWidth'],-.0886,.1272)","(.0282*FACE120['frontal']['mouthWidth'],-.0880,.1272)"),
("(-.0228*FACE120['frontal']['mouthWidth'],-.0952,.1270)","(-.0238*FACE120['frontal']['mouthWidth'],-.0944,.1270)"),
("(.0228*FACE120['frontal']['mouthWidth'],-.0952,.1270)","(.0238*FACE120['frontal']['mouthWidth'],-.0944,.1270)")
)
for old,new in repls:
    if old not in s: raise SystemExit('v12.6 lip anchor missing: '+old)
    s=s.replace(old,new,1)

# Match the mouth seam to the wider lip tint.
old="[(-.0282,-.0871,.1272),(-.0128,-.0863,.1290),(0,-.0872,.1307),(.0128,-.0863,.1290),(.0282,-.0871,.1272)]"
new="[(-.0300,-.0868,.1272),(-.0135,-.0860,.1290),(0,-.0869,.1307),(.0135,-.0860,.1290),(.0300,-.0868,.1272)]"
if old not in s: raise SystemExit('v12.6 mouth seam anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v12.5';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v12.6';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s: raise SystemExit('v12.6 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V126: compact lower face, slightly broader cheeks, larger almond gaze and refined mouth read')
