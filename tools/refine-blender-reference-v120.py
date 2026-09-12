from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V120' in s:
    print('Blender heroine generator already carries REFERENCE_V120')
    raise SystemExit(0)
if '# REFERENCE_V119' not in s:
    raise SystemExit('REFERENCE_V119 generator required before v12.0')

marker="# REFERENCE_V119: visual-audit portrait pass boosts iPhone-scale eye contrast, shortens the lower face, exaggerates the key-art profile and adds layered asymmetric brow-length bangs."
if marker not in s:
    raise SystemExit('v12.0 REFERENCE_V119 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V120: Tripo/Astra-inspired modular assembly pass separates body/head/hair/face assets, adds expression pivots and rebalances the close-up eye/profile read without changing combat rig names.",1)

old="FACE119_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v119.json')"
new="FACE120_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v120.json')\nASSEMBLY120_PATH=os.path.join(ROOT_DIR,'tools','heroine-assembly-v120.json')"
if old not in s: raise SystemExit('v12.0 face path anchor missing')
s=s.replace(old,new,1)
old="with open(FACE119_PATH,'r',encoding='utf-8') as f:FACE119=json.load(f)"
new="with open(FACE120_PATH,'r',encoding='utf-8') as f:FACE120=json.load(f)\nwith open(ASSEMBLY120_PATH,'r',encoding='utf-8') as f:ASSEMBLY120=json.load(f)"
if old not in s: raise SystemExit('v12.0 face load anchor missing')
s=s.replace(old,new,1)
s=s.replace('FACE119','FACE120')
s=s.replace('def add_reference_head_v119(','def add_reference_head_v120(',1)
s=s.replace("add_reference_head_v119(HEAD,'HeadShellV119',SKIN,128)","add_reference_head_v120(HEAD,'HeadShellV120',SKIN,128)",1)

# Use the v12 assembly controls as the single source for the identity-preserving face rebalance.
head_anchor="frontal=FACE120['frontal'];profile_ctrl=FACE120['profile'];surface=FACE120['surface']"
if head_anchor not in s: raise SystemExit('v12.0 head control anchor missing')
s=s.replace(head_anchor,head_anchor+"\n assembly_head=ASSEMBLY120['head']\n frontal={**frontal,'eyeSize':assembly_head['eyeSize'],'eyeSpacing':assembly_head['eyeSpacing'],'faceWidth':assembly_head['faceWidth'],'jaw':assembly_head['jaw'],'cheekVolume':assembly_head['cheekVolume'],'mouthWidth':assembly_head['mouthWidth']}\n profile_ctrl={**profile_ctrl,'noseProjection':assembly_head['noseProjection'],'noseWidth':assembly_head['noseWidth'],'foreheadDepth':assembly_head['foreheadDepth'],'mouthProjection':assembly_head['mouthProjection'],'chinProjection':assembly_head['chinProjection'],'chinLength':assembly_head['chinLength']}\n surface={**surface,'irisScale':assembly_head['irisScale'],'eyeContrast':assembly_head['eyeContrast']}",1)

# Slightly reduce the mobile close-up aperture while retaining the strong limbal ring and key-art outline.
s=s.replace("eye_x=.0450*FACE120['frontal']['eyeSpacing']\neye_rx=.0308*FACE120['frontal']['eyeSize']\neye_ry=.0109*FACE120['frontal']['eyeSize']\neye_tilt=.00315", "eye_x=.0452*ASSEMBLY120['head']['eyeSpacing']\neye_rx=.0302*ASSEMBLY120['head']['eyeSize']\neye_ry=.01055*ASSEMBLY120['head']['eyeSize']\neye_tilt=.00300",1)
s=s.replace("iris_scale=FACE120['surface']['irisScale']\neye_contrast=FACE120['surface']['eyeContrast']", "iris_scale=ASSEMBLY120['head']['irisScale']\neye_contrast=ASSEMBLY120['head']['eyeContrast']",1)

# Add broad scalp-connected temple layers; unlike old isolated wisps these read as continuous hair mass in profile.
anchor=" add_strand(HEAD,f'KeyArtBangHiV119_{_name}',_pts,.000055,HAIR_HI)\n"
if anchor not in s: raise SystemExit('v12.0 hair anchor missing')
hair_block=anchor+"""# v12.0 modular hair-fit pass: broad temple layers bridge fringe to side/back mass.
for _side in (-1,1):
 _sw=ASSEMBLY120['hair']['templeLockWidth'];_sd=ASSEMBLY120['hair']['templeLockDepth']
 _pts=[(_side*.086,.170,.055),(_side*.098,.132,.083),(_side*.106,.090,.100),(_side*.108,.045,.103),(_side*.102,.000,.097),(_side*.094,-.036,.086)]
 _widths=[_sw*.70,_sw, _sw*1.04,_sw*.88,_sw*.62,_sw*.24]
 _depths=[_sd*.72,_sd,_sd*1.02,_sd*.88,_sd*.60,_sd*.20]
 add_smooth_lock(HEAD,f'TempleLayerV120_{_side}',_pts,_widths,_depths,HAIR,12,6)
 add_strand(HEAD,f'TempleLayerHiV120_{_side}',[(_side*.087,.165,.060),(_side*.099,.126,.089),(_side*.106,.080,.102),(_side*.101,.002,.098)],.000050,HAIR_HI)
"""
s=s.replace(anchor,hair_block,1)

# Replace the flat build hierarchy with modular assembly roots while preserving all runtime node names.
old="ROOT=empty('BLENDER_HEROINE');PELVIS=empty('BL_PELVIS',ROOT);TORSO=empty('BL_TORSO',ROOT);HEAD=empty('BL_HEAD',ROOT)\nUA_L=empty('BL_UPPER_ARM_L',ROOT);FA_L=empty('BL_FOREARM_L',ROOT);HAND_L=empty('BL_HAND_L',ROOT);UA_R=empty('BL_UPPER_ARM_R',ROOT);FA_R=empty('BL_FOREARM_R',ROOT);HAND_R=empty('BL_HAND_R',ROOT)\nTH_L=empty('BL_THIGH_L',ROOT);SH_L=empty('BL_SHIN_L',ROOT);FOOT_L=empty('BL_FOOT_L',ROOT);TH_R=empty('BL_THIGH_R',ROOT);SH_R=empty('BL_SHIN_R',ROOT);FOOT_R=empty('BL_FOOT_R',ROOT);SWORD=empty('BL_SWORD',ROOT)"
new="""ROOT=empty('BLENDER_HEROINE')
BODY_ASSET=empty('BL_BODY_ASSET',ROOT)
PELVIS=empty('BL_PELVIS',BODY_ASSET);TORSO=empty('BL_TORSO',BODY_ASSET);HEAD=empty('BL_HEAD',ROOT)
HEAD_ASSET=empty('BL_HEAD_ASSET',HEAD);HAIR_ASSET=empty('BL_HAIR_ASSET',HEAD);FACE_ASSET=empty('BL_FACE_ASSET',HEAD)
EYE_L=empty('BL_EYE_L',FACE_ASSET);EYE_R=empty('BL_EYE_R',FACE_ASSET);MOUTH_ASSET=empty('BL_MOUTH',FACE_ASSET)
UA_L=empty('BL_UPPER_ARM_L',BODY_ASSET);FA_L=empty('BL_FOREARM_L',BODY_ASSET);HAND_L=empty('BL_HAND_L',BODY_ASSET);UA_R=empty('BL_UPPER_ARM_R',BODY_ASSET);FA_R=empty('BL_FOREARM_R',BODY_ASSET);HAND_R=empty('BL_HAND_R',BODY_ASSET)
TH_L=empty('BL_THIGH_L',BODY_ASSET);SH_L=empty('BL_SHIN_L',BODY_ASSET);FOOT_L=empty('BL_FOOT_L',BODY_ASSET);TH_R=empty('BL_THIGH_R',BODY_ASSET);SH_R=empty('BL_SHIN_R',BODY_ASSET);FOOT_R=empty('BL_FOOT_R',BODY_ASSET);SWORD=empty('BL_SWORD',ROOT)"""
if old not in s: raise SystemExit('v12.0 root hierarchy anchor missing')
s=s.replace(old,new,1)

# Before export, sort existing head meshes into Head / Hair / Face sub-assets and create eye/mouth pivots.
old="for o in[ROOT,PELVIS,TORSO,HEAD,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)"
if old not in s: raise SystemExit('v12.0 export reset anchor missing')
new="""# v12.0 modular assembly: Body is the scale reference; Head and Hair remain separately selectable/reviewable.
def _under(obj,ancestor):
 q=obj.parent
 while q:
  if q is ancestor:return True
  q=q.parent
 return False
def _reparent_keep_world(obj,target):
 mw=obj.matrix_world.copy();obj.parent=target;obj.matrix_world=mw
def _materials(obj):
 return {m.name for m in getattr(obj.data,'materials',[]) if m}

for o in[ROOT,BODY_ASSET,PELVIS,TORSO,HEAD,HEAD_ASSET,HAIR_ASSET,FACE_ASSET,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:
 o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
# Expression pivots use the same measured eye/mouth centers as the visible v12 geometry.
EYE_L.location=bpos((-.0452*ASSEMBLY120['head']['eyeSpacing'],.0295,.1040));EYE_R.location=bpos((.0452*ASSEMBLY120['head']['eyeSpacing'],.0295,.1040));MOUTH_ASSET.location=bpos((0,-.0880,.1290))
EYE_L.rotation_euler=EYE_R.rotation_euler=MOUTH_ASSET.rotation_euler=(0,0,0);EYE_L.scale=EYE_R.scale=MOUTH_ASSET.scale=(1,1,1)

_eye_tokens=('EyeSclera','IrisOuter','IrisInner','Pupil','EyeLight','UpperLash','OuterLash','LowerLid','UpperLid')
_mouth_tokens=('UpperLip','LowerLip','MouthSeam')
_face_tokens=('Brow','Nostril','Ear','Face','Philtrum','Chin','Nose')
for _o in list(bpy.data.objects):
 if _o.type!='MESH' or not _under(_o,HEAD) or _under(_o,PONY):continue
 _name=_o.name;_mats=_materials(_o);_target=None
 if any(t in _name for t in _eye_tokens):
  _target=EYE_L if _name.endswith('_-1') else EYE_R if _name.endswith('_1') else FACE_ASSET
 elif any(t in _name for t in _mouth_tokens):_target=MOUTH_ASSET
 elif any(t in _name for t in _face_tokens):_target=FACE_ASSET
 elif 'Hair' in _mats or 'Hair Highlight' in _mats or 'HairTie' in _name or 'Fringe' in _name or 'Bang' in _name or 'TempleLayer' in _name:_target=HAIR_ASSET
 else:_target=HEAD_ASSET
 _reparent_keep_world(_o,_target)
# Keep the existing dynamic pony root working, but move the complete hair subsystem under its own asset root.
_reparent_keep_world(PONY,HAIR_ASSET)
ROOT['character_revision']='v12.0';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True
"""
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V120: modular Body/Head/Hair assembly, expression pivots, profile-aware face rebalance and scalp-connected temple layers')
