from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V121' in s:
    print('Blender heroine generator already carries REFERENCE_V121')
    raise SystemExit(0)
if '# REFERENCE_V120' not in s:
    raise SystemExit('REFERENCE_V120 generator required before v12.1')

marker="# REFERENCE_V120: Tripo/Astra-inspired modular assembly pass separates body/head/hair/face assets, adds expression pivots and rebalances the close-up eye/profile read without changing combat rig names."
if marker not in s:
    raise SystemExit('v12.1 REFERENCE_V120 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V121: audit correction keeps visible eye/mouth meshes in the face asset, leaves expression pivots transform-neutral, and narrows the adult-anime eye aperture for clean profile/3q views.",1)

# The first v12 assembly pass parented visible eye/mouth meshes below offset expression pivots.
# GLB export preserved the extra parent translation in profile.  Keep visible geometry on BL_FACE_ASSET;
# the named eye/mouth nodes remain available as neutral future expression-control anchors.
old="""if any(t in _name for t in _eye_tokens):
  _target=EYE_L if _name.endswith('_-1') else EYE_R if _name.endswith('_1') else FACE_ASSET
 elif any(t in _name for t in _mouth_tokens):_target=MOUTH_ASSET
 elif any(t in _name for t in _face_tokens):_target=FACE_ASSET"""
new="""if any(t in _name for t in _eye_tokens):
  _target=FACE_ASSET
 elif any(t in _name for t in _mouth_tokens):_target=FACE_ASSET
 elif any(t in _name for t in _face_tokens):_target=FACE_ASSET"""
if old not in s:
    raise SystemExit('v12.1 modular face parenting anchor missing')
s=s.replace(old,new,1)

# v12.1 adult-anime aperture: retain the readable dark contour while reducing the horizontal doll-eye read.
old="""eye_x=.0452*ASSEMBLY120['head']['eyeSpacing']
eye_rx=.0302*ASSEMBLY120['head']['eyeSize']
eye_ry=.01055*ASSEMBLY120['head']['eyeSize']
eye_tilt=.00300"""
new="""eye_x=.0452*ASSEMBLY120['head']['eyeSpacing']
eye_rx=.0277*ASSEMBLY120['head']['eyeSize']
eye_ry=.01015*ASSEMBLY120['head']['eyeSize']
eye_tilt=.00285"""
if old not in s:
    raise SystemExit('v12.1 eye aperture anchor missing')
s=s.replace(old,new,1)

s=s.replace("SCLERA=material('Sclera',(0.50,0.485,0.475),0,.68)","SCLERA=material('Sclera',(0.43,0.415,0.405),0,.72)",1)
s=s.replace(".01095*iris_scale,.00905*iris_scale,IRIS,52", ".01155*iris_scale,.00915*iris_scale,IRIS,52",1)
s=s.replace(".00825*iris_scale,.00655*iris_scale,IRIS_INNER,48", ".00875*iris_scale,.00670*iris_scale,IRIS_INNER,48",1)

props="ROOT['character_revision']='v12.0';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True"
if props not in s:
    raise SystemExit('v12.1 assembly property anchor missing')
s=s.replace(props,"ROOT['character_revision']='v12.1';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V121: fixed GLB face parenting, neutral expression pivots, narrower eye aperture and calmer sclera contrast')
