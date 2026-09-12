from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V125' in s:
    print('Blender heroine generator already carries REFERENCE_V125')
    raise SystemExit(0)
if '# REFERENCE_V124' not in s:
    raise SystemExit('REFERENCE_V124 generator required before v12.5')

marker="# REFERENCE_V124: layered crown and hero-ponytail masses break the helmet/flat-sheet silhouette while preserving the existing dynamic pony root."
if marker not in s:
    raise SystemExit('v12.5 REFERENCE_V124 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V125: facial-depth and eye-material pass strengthens orbital/nasal/cheek planes and mobile-scale gaze without changing the modular expression pivots.",1)

# Softer skin response and clearer eye materials.  The previous sclera/iris palette collapsed into
# a small dark dot in the bright outdoor viewer; keep the limbal ring dark but give the inner iris
# and sclera enough value separation to survive iPhone-scale rendering.
replacements=(
("SKIN=material('Skin',(0.36,0.235,0.215),0,.76)","SKIN=material('Skin',(0.375,0.245,0.225),0,.68)"),
("SCLERA=material('Sclera',(0.43,0.415,0.405),0,.72)","SCLERA=material('Sclera',(0.60,0.575,0.555),0,.66)"),
("IRIS=material('Iris',(0.072,0.050,0.047),.01,.58)","IRIS=material('Iris',(0.052,0.032,0.030),.01,.56)"),
("IRIS_INNER=material('Iris Inner',(0.125,0.086,0.078),.01,.60)","IRIS_INNER=material('Iris Inner',(0.175,0.105,0.082),.01,.58)"),
("LIP=material('Lip',(0.34,0.120,0.140),0,.62)","LIP=material('Lip',(0.285,0.105,0.125),0,.67)")
)
for old,new in replacements:
    if old not in s:
        raise SystemExit('v12.5 material anchor missing: '+old)
    s=s.replace(old,new,1)

# Increase actual continuous-surface relief rather than layering detached feature meshes.  These
# small gains create readable light/shadow at the orbit, malar plane, nasal bridge/tip and chin.
replacements=(
("z-=fm*(.0027*orbital)*math.exp(-((x-ex)/(.0265*eye_size))**2-((yy-.033)/(.0195*eye_size))**2)",
 "z-=fm*(.00315*orbital)*math.exp(-((x-ex)/(.0265*eye_size))**2-((yy-.033)/(.0195*eye_size))**2)"),
("z+=fm*(.0062*malar*cheek)*math.exp(-((x-side*.057)/.034)**2-((yy+.004)/.036)**2)",
 "z+=fm*(.00670*malar*cheek)*math.exp(-((x-side*.057)/.034)**2-((yy+.004)/.036)**2)"),
("z-=fm*(.0027*hollow)*math.exp(-((x-side*.069)/.030)**2-((yy+.054)/.035)**2)",
 "z-=fm*(.00300*hollow)*math.exp(-((x-side*.069)/.030)**2-((yy+.054)/.035)**2)"),
("z+=fm*.00355*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)",
 "z+=fm*.00415*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)"),
("z+=fm*.00610*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0105)**2)",
 "z+=fm*.00670*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0105)**2)"),
("z+=fm*.00215*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0080)**2)",
 "z+=fm*.00245*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0080)**2)"),
("z+=fm*.00535*math.exp(-(x/.0315)**2-((yy+.119)/.0180)**2)",
 "z+=fm*.00495*math.exp(-(x/.0315)**2-((yy+.119)/.0180)**2)")
)
for old,new in replacements:
    if old not in s:
        raise SystemExit('v12.5 facial relief anchor missing')
    s=s.replace(old,new,1)

old="iris_scale=ASSEMBLY120['head']['irisScale']\neye_contrast=ASSEMBLY120['head']['eyeContrast']"
new="iris_scale=ASSEMBLY120['head']['irisScale']*1.05\neye_contrast=ASSEMBLY120['head']['eyeContrast']*1.08"
if old not in s:
    raise SystemExit('v12.5 eye read anchor missing')
s=s.replace(old,new,1)

# Slightly stronger eyelid/brow linework makes the eye socket readable without enlarging the sclera aperture.
replacements=(
("],.00088*eye_contrast,HAIR)","],.00094*eye_contrast,HAIR)"),
("],.00044*eye_contrast,HAIR)","],.00048*eye_contrast,HAIR)"),
("],.00016*eye_contrast,FACE_DARK)","],.00019*eye_contrast,FACE_DARK)"),
("],.00013,FACE_DARK)","],.00017,FACE_DARK)"),
("],.00062,HAIR)\n add_blink_lid_surface","],.00068,HAIR)\n add_blink_lid_surface")
)
for old,new in replacements:
    if old not in s:
        raise SystemExit('v12.5 eye line anchor missing')
    s=s.replace(old,new,1)

# Strengthen the nostril tint just enough to separate the nose base from the upper lip in frontal lighting.
old=".00195*FACE120['surface']['nostrilScale'],.00072*FACE120['surface']['nostrilScale'],FACE_DARK,20)"
new=".00215*FACE120['surface']['nostrilScale'],.00088*FACE120['surface']['nostrilScale'],FACE_DARK,20)"
if old not in s:
    raise SystemExit('v12.5 nostril tint anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v12.4';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v12.5';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v12.5 assembly property anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V125: stronger facial planes, clearer adult-anime gaze and softer portrait materials')
