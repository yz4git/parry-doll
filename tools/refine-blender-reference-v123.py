from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V123' in s:
    print('Blender heroine generator already carries REFERENCE_V123')
    raise SystemExit(0)
if '# REFERENCE_V122' not in s:
    raise SystemExit('REFERENCE_V122 generator required before v12.3')

marker="# REFERENCE_V122: real skin eyelid meshes use a Blink morph target so eyes close over the globe instead of scaling the eyeball."
if marker not in s:
    raise SystemExit('v12.3 REFERENCE_V122 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V123: TPS silhouette pass keeps measured rig endpoints while narrowing visual deltoid/clavicle armor and upper-chest shell bulk.",1)

# Keep the reference-locked torso and runtime shoulder endpoints untouched.  Only the visible
# shoulder bridge is reduced so the heroine reads longer-necked and more elegant from the low TPS camera.
old="""for side in(-1,1):
 add_sphere(TORSO,f'DeltoidBridgeV50_{side}',(side*bust_w*.415,.238,.002),(bust_w*.126,.062,bust_d*.142),BLACK,34,22)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.285,.258,bust_d*.28),(side*bust_w*.475,.225,bust_d*.18),(side*bust_w*.275,.210,bust_d*.31)],.013,BLACK_SOFT)
 add_box(TORSO,f'ClavicleTrim_{side}',(side*bust_w*.225,.247,bust_d*.325),(bust_w*.250,.010,.008),SILVER,.0025,rot=(0,0,-side*.11))
"""
new="""for side in(-1,1):
 add_sphere(TORSO,f'DeltoidBridgeV50_{side}',(side*bust_w*.385,.236,.002),(bust_w*.108,.056,bust_d*.128),BLACK,34,22)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.270,.258,bust_d*.28),(side*bust_w*.435,.226,bust_d*.18),(side*bust_w*.255,.211,bust_d*.31)],.012,BLACK_SOFT)
 add_box(TORSO,f'ClavicleTrim_{side}',(side*bust_w*.205,.247,bust_d*.325),(bust_w*.220,.009,.008),SILVER,.0025,rot=(0,0,-side*.10))
"""
if old not in s:
    raise SystemExit('v12.3 shoulder bridge anchor missing')
s=s.replace(old,new,1)

# Pull the porcelain chest wings inward.  Their old outer corners visually extended the shoulder
# line even though the underlying body envelope was already reference-locked.
replacements=(
("""add_panel(TORSO,'ChestWingV67_L',[(-bust_w*.505,.248,bust_d*.455),(-bust_w*.245,.226,bust_d*.595),(-bust_w*.205,.080,bust_d*.790),(-bust_w*.465,.066,bust_d*.690)],.012,WHITE)""",
 """add_panel(TORSO,'ChestWingV67_L',[(-bust_w*.472,.248,bust_d*.455),(-bust_w*.245,.226,bust_d*.595),(-bust_w*.205,.080,bust_d*.790),(-bust_w*.438,.066,bust_d*.690)],.012,WHITE)"""),
("""add_panel(TORSO,'ChestWingV67_R',[(bust_w*.245,.226,bust_d*.595),(bust_w*.505,.248,bust_d*.455),(bust_w*.465,.066,bust_d*.690),(bust_w*.205,.080,bust_d*.790)],.012,WHITE)""",
 """add_panel(TORSO,'ChestWingV67_R',[(bust_w*.245,.226,bust_d*.595),(bust_w*.472,.248,bust_d*.455),(bust_w*.438,.066,bust_d*.690),(bust_w*.205,.080,bust_d*.790)],.012,WHITE)"""),
("""add_panel(TORSO,'PorcelainShellV68_L',[(-bust_w*.520,.250,bust_d*.485),(-bust_w*.115,.226,bust_d*.690),(-bust_w*.095,.072,bust_d*.875),(-waist_w*.105,-.188,waist_d*.905),(-waist_w*.535,-.238,waist_d*.735),(-bust_w*.500,.058,bust_d*.750)],.013,WHITE)""",
 """add_panel(TORSO,'PorcelainShellV68_L',[(-bust_w*.486,.250,bust_d*.485),(-bust_w*.115,.226,bust_d*.690),(-bust_w*.095,.072,bust_d*.875),(-waist_w*.105,-.188,waist_d*.905),(-waist_w*.535,-.238,waist_d*.735),(-bust_w*.462,.058,bust_d*.750)],.013,WHITE)"""),
("""add_panel(TORSO,'PorcelainShellV68_R',[(bust_w*.115,.226,bust_d*.690),(bust_w*.520,.250,bust_d*.485),(bust_w*.500,.058,bust_d*.750),(waist_w*.535,-.238,waist_d*.735),(waist_w*.105,-.188,waist_d*.905),(bust_w*.095,.072,bust_d*.875)],.013,WHITE)""",
 """add_panel(TORSO,'PorcelainShellV68_R',[(bust_w*.115,.226,bust_d*.690),(bust_w*.486,.250,bust_d*.485),(bust_w*.462,.058,bust_d*.750),(waist_w*.535,-.238,waist_d*.735),(waist_w*.105,-.188,waist_d*.905),(bust_w*.095,.072,bust_d*.875)],.013,WHITE)""")
)
for old,new in replacements:
    if old not in s:
        raise SystemExit('v12.3 upper-chest shell anchor missing')
    s=s.replace(old,new,1)

# The spherical junction under the upper arm was another source of apparent shoulder width.
old="""for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_sphere(group,'DeltoidBlendV59'+name,(0,-.430,0),(ua*1.10,.095,ua_d*1.08),SKIN,30,20)
"""
new="""for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_sphere(group,'DeltoidBlendV59'+name,(0,-.430,0),(ua*1.03,.087,ua_d*1.02),SKIN,30,20)
"""
if old not in s:
    raise SystemExit('v12.3 upper-arm blend anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v12.2';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v12.3';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v12.3 assembly property anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V123: TPS shoulder/upper-chest silhouette refinement without moving rig endpoints')
