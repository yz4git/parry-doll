from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V161' in s and face.get('revision')=='v14.1':
    print('Blender heroine generator already carries REFERENCE_V161 / v14.1 cage')
    raise SystemExit(0)
if '# REFERENCE_V160' not in s:
    raise SystemExit('REFERENCE_V160 generator required before v14.1')

marker="# REFERENCE_V160: v14.0 root face rebuild replaces the accumulated v13 centre-profile/RBF shell with one new multiview landmark cage: recessed orbit, continuous narrow nose, embedded lips, soft chin and rising under-jaw while preserving BL_HEAD, neck and blink runtime contracts."
if marker not in s:
    raise SystemExit('v14.1 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V161: v14.1 base-cage correction strengthens the nasion-to-tip S profile, raises the rear under-jaw and seats larger exact-profile eyes deeper inside the rebuilt sockets; no return to v13 local silhouette patches.",1)

# The v14 data file remains the single source of truth for large face forms.
face['revision']='v14.1'
face['reference_intent']='adult realistic-anime heroine; supplied side reference: deeper orbit, visible almond eye in true profile, narrow nasion, smooth projected bridge, small rounded tip, embedded full lips, soft chin, steep rising jaw-to-ear plane'
face['profile']=[
 [0.096,0.1000],[0.070,0.1008],[0.050,0.1005],[0.034,0.0990],
 [0.022,0.0965],[0.010,0.0968],[-0.004,0.1025],[-0.018,0.1115],
 [-0.032,0.1215],[-0.044,0.1290],[-0.052,0.1330],[-0.058,0.1320],
 [-0.064,0.1260],[-0.071,0.1145],[-0.077,0.1122],[-0.083,0.1188],
 [-0.089,0.1220],[-0.095,0.1235],[-0.101,0.1192],[-0.108,0.1115],
 [-0.116,0.1070],[-0.123,0.1188],[-0.131,0.1195],[-0.139,0.1110],
 [-0.147,0.0950],[-0.154,0.0750]
]
face['surface_strength']['orbit_recess']=0.00715
face['surface_strength']['brow_support']=0.00275
face['surface_strength']['malar_projection']=0.00595
face['surface_strength']['buccal_hollow']=0.00295
face['surface_strength']['philtrum_recess']=0.00205
face['surface_strength']['upper_lip']=0.00395
face['surface_strength']['lower_lip']=0.00455
face['surface_strength']['labiomental_recess']=0.00185
face['surface_strength']['chin_pad']=0.00420
face['eye_target']['aperture_rx']=0.02835
face['eye_target']['aperture_ry']=0.00920
face['eye_target']['tilt']=0.00355
face['eye_target']['iris_scale_multiplier']=0.845
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# Make the rear under-jaw rise visibly toward the ear/neck. This edits the v14 cage deformation itself.
old="render_y+=.0130*under*sideback+.0255*under*(backness**1.08)"
new="render_y+=.0175*under*sideback+.0350*under*(backness**1.06)"
if old not in s:
    raise SystemExit('v14.1 under-jaw anchor missing')
s=s.replace(old,new,1)

# Seat the front/3Q eye slightly deeper into the new orbital surface. The blink lid remains the outer skin layer.
for old,new in (
    ("add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)",
     "add_almond_surface(HEAD,f'EyeScleraV140_{side}',ex,eye_y,.10235,eye_rx,eye_ry,.00118,SCLERA,96,side,eye_tilt*.74)"),
    ("add_ellipse_surface(HEAD,f'IrisOuterV119_{side}',ex,eye_y-.00025,.10448,.01155*iris_scale,.00915*iris_scale,IRIS,52)",
     "add_ellipse_surface(HEAD,f'IrisOuterV140_{side}',ex,eye_y-.00025,.10362,.01145*iris_scale,.00895*iris_scale,IRIS,52)"),
    ("add_ellipse_surface(HEAD,f'IrisInnerV119_{side}',ex,eye_y-.00005,.10472,.00875*iris_scale,.00670*iris_scale,IRIS_INNER,48)",
     "add_ellipse_surface(HEAD,f'IrisInnerV140_{side}',ex,eye_y-.00005,.10384,.00865*iris_scale,.00655*iris_scale,IRIS_INNER,48)"),
    ("add_iris_rays_v129(HEAD,f'IrisRaysV129_{side}',ex,eye_y-.00005,.10484,.00795*iris_scale,.00605*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)",
     "add_iris_rays_v129(HEAD,f'IrisRaysV140_{side}',ex,eye_y-.00005,.10396,.00785*iris_scale,.00590*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)"),
    ("add_ellipse_surface(HEAD,f'PupilV119_{side}',ex,eye_y-.00045,.10502,.00305*iris_scale,.00385*iris_scale,PUPIL,36)",
     "add_ellipse_surface(HEAD,f'PupilV140_{side}',ex,eye_y-.00045,.10410,.00300*iris_scale,.00375*iris_scale,PUPIL,36)"),
):
    if old not in s:
        raise SystemExit('v14.1 eye seating anchor missing: '+old[:54])
    s=s.replace(old,new,1)

# True profile eye must read as an eye, not a dot. These helper surfaces remain almost edge-on in front view.
for old,new in (
    ("eye_ry*1.180,.00900,SCLERA,48","eye_ry*1.420,.01080,SCLERA,52"),
    ("eye_ry*.760,.00570,IRIS_INNER,44","eye_ry*.900,.00665,IRIS_INNER,48"),
    ("eye_ry*.340,.00265,PUPIL,34","eye_ry*.390,.00305,PUPIL,36"),
    ("eye_y+eye_ry*.82,.1020","eye_y+eye_ry*.96,.1020"),
    ("eye_y-eye_ry*.78,.1021","eye_y-eye_ry*.92,.1021"),
):
    if old not in s:
        raise SystemExit('v14.1 exact-profile eye anchor missing: '+old)
    s=s.replace(old,new,1)

# A stronger but still thin profile lash fan supplies the reference's long upper-lash silhouette.
for old,new in (
    (".00031*eye_contrast,HAIR)\n add_strand(HEAD,f'ProfileLashFanV138_B_{side}'", ".00036*eye_contrast,HAIR)\n add_strand(HEAD,f'ProfileLashFanV138_B_{side}'"),
    (".00027*eye_contrast,HAIR)\n add_strand(HEAD,f'LowerLidV119_{side}'", ".00031*eye_contrast,HAIR)\n add_strand(HEAD,f'LowerLidV119_{side}'"),
):
    if old not in s:
        raise SystemExit('v14.1 lash anchor missing')
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v14.0';"
new="ROOT['character_revision']='v14.1';"
if old not in s:
    raise SystemExit('v14.1 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.0';"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.1';",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['v14_eye_seating_revision']='v14.1';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V161: v14.1 cage profile, jaw plane and integrated eye seating correction')
