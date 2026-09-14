from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V162' in s and face.get('revision')=='v14.2':
    print('Blender heroine generator already carries REFERENCE_V162 / v14.2 cage')
    raise SystemExit(0)
if '# REFERENCE_V161' not in s:
    raise SystemExit('REFERENCE_V161 generator required before v14.2')

marker="# REFERENCE_V161: v14.1 base-cage correction strengthens the nasion-to-tip S profile, raises the rear under-jaw and seats larger exact-profile eyes deeper inside the rebuilt sockets; no return to v13 local silhouette patches."
if marker not in s:
    raise SystemExit('v14.2 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V162: v14.2 compacts the lower-face cage, preserves a softer adult jaw instead of a long V, and places a true side-facing ocular layer on the lateral head surface so profile audits read an eye rather than a dot.",1)

face['revision']='v14.2'
face['reference_intent']='adult realistic-anime heroine; compact lower face, soft but readable jaw angle, narrow nasion and small projected tip, embedded lips, visible almond eye in exact profile with the eye seated on the lateral orbital surface'
# Keep the accepted cranium/orbital rows. Compact only the mouth-to-chin envelope and retain enough width for an adult jaw.
face['sections']=[
 [0.168,0.068,0.078,0.079,-0.010],[0.154,0.097,0.085,0.085,-0.008],[0.138,0.116,0.091,0.091,-0.006],
 [0.120,0.126,0.096,0.095,-0.003],[0.100,0.130,0.100,0.098,-0.001],[0.080,0.128,0.102,0.099,0.000],
 [0.060,0.125,0.103,0.100,0.001],[0.040,0.121,0.104,0.100,0.002],[0.020,0.119,0.104,0.101,0.002],
 [0.000,0.116,0.104,0.101,0.002],[-0.020,0.113,0.103,0.102,0.002],[-0.040,0.108,0.102,0.102,0.001],
 [-0.060,0.102,0.101,0.102,0.000],[-0.075,0.097,0.100,0.103,-0.001],[-0.088,0.092,0.099,0.103,-0.002],
 [-0.099,0.087,0.098,0.102,-0.003],[-0.109,0.081,0.096,0.100,-0.004],[-0.118,0.074,0.093,0.097,-0.006],
 [-0.127,0.064,0.088,0.092,-0.008],[-0.134,0.050,0.082,0.086,-0.010]
]
# Stronger but still feminine side silhouette. The bridge grows continuously from a deeper nasion,
# then falls quickly into a small tip; the lower face is shorter and the chin stays rounded.
face['profile']=[
 [0.096,0.1000],[0.070,0.1008],[0.050,0.1002],[0.034,0.0982],[0.022,0.0952],[0.010,0.0958],
 [-0.004,0.1030],[-0.018,0.1132],[-0.032,0.1240],[-0.044,0.1330],[-0.051,0.1370],[-0.057,0.1350],
 [-0.064,0.1270],[-0.071,0.1140],[-0.077,0.1120],[-0.083,0.1190],[-0.089,0.1230],[-0.095,0.1242],
 [-0.101,0.1195],[-0.108,0.1115],[-0.114,0.1080],[-0.120,0.1185],[-0.126,0.1190],[-0.132,0.1100],
 [-0.138,0.0940],[-0.144,0.0750]
]
face['feature_landmarks']['chin_y']=-0.118
face['feature_landmarks']['jaw_hinge_y']=-0.076
face['surface_strength']['chin_pad']=0.00395
face['surface_strength']['buccal_hollow']=0.00270
face['eye_target']['aperture_rx']=0.02855
face['eye_target']['aperture_ry']=0.00935
face['eye_target']['iris_scale_multiplier']=0.875
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# Make the rear under-jaw angle clearly rise toward the ear while keeping the centre-front chin rounded.
old="render_y+=.0175*under*sideback+.0350*under*(backness**1.06)"
new="render_y+=.0225*under*sideback+.0460*under*(backness**1.04)"
if old not in s:
    raise SystemExit('v14.2 under-jaw anchor missing')
s=s.replace(old,new,1)

# v14.1's profile helper lived too close to the face centre (x ~= 0.075) and was occluded by the closed head shell.
# Leave that helper as an internal continuity layer and add a thin YZ ocular surface at the actual lateral orbital skin.
blink_line=" add_blink_lid_surface(HEAD,'BL_EYELID_L' if side<0 else 'BL_EYELID_R',ex,eye_y,eye_rx,eye_ry,SKIN)"
if blink_line not in s:
    raise SystemExit('v14.2 blink insertion anchor missing')
profile_eye="""
 # v14.2 exact-profile ocular layer. Constant-X YZ geometry is edge-on from the front but fully readable in true profile.
 _px=side*.1218;_pz=.0685
 add_profile_ellipse_yz_v137(HEAD,f'ProfileHeroScleraV142_{side}',_px,eye_y,_pz,eye_ry*.82,.0162,SCLERA,56)
 add_profile_ellipse_yz_v137(HEAD,f'ProfileHeroIrisV142_{side}',_px+side*.00035,eye_y+.0001,_pz+.0040,eye_ry*.54,.0091,IRIS_INNER,48)
 add_profile_ellipse_yz_v137(HEAD,f'ProfileHeroPupilV142_{side}',_px+side*.00055,eye_y-.0001,_pz+.0055,eye_ry*.235,.0037,PUPIL,36)
 add_strand(HEAD,f'ProfileHeroUpperLidV142_{side}',[(_px+side*.0007,eye_y-.0008,_pz-.0160),(_px+side*.0010,eye_y+.0078,_pz-.0040),(_px+side*.0010,eye_y+.0086,_pz+.0070),(_px+side*.0007,eye_y+.0030,_pz+.0160)],.00030*eye_contrast,FACE_DARK)
 add_strand(HEAD,f'ProfileHeroLowerLidV142_{side}',[(_px+side*.00065,eye_y-.0005,_pz-.0152),(_px+side*.0009,eye_y-.0063,_pz-.0030),(_px+side*.0009,eye_y-.0059,_pz+.0080),(_px+side*.00065,eye_y-.0006,_pz+.0150)],.00017*eye_contrast,EYE_WET)
 add_strand(HEAD,f'ProfileHeroLashV142_{side}',[(_px+side*.0011,eye_y+.0068,_pz+.0070),(_px+side*.0018,eye_y+.0105,_pz+.0145),(_px+side*.0027,eye_y+.0110,_pz+.0220)],.00031*eye_contrast,HAIR)
"""
s=s.replace(blink_line,blink_line+profile_eye,1)

# Keep the exported revision explicit for runtime/debug and visual audits.
old="ROOT['character_revision']='v14.1';"
new="ROOT['character_revision']='v14.2';"
if old not in s:
    raise SystemExit('v14.2 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.1';"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.2';",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['profile_ocular_revision']='v14.2';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V162: compact jaw cage plus lateral profile ocular layer')
