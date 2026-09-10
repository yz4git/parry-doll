from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V96' in s:
    print('Blender heroine generator already carries REFERENCE_V96')
    raise SystemExit(0)
if '# REFERENCE_V95' not in s:
    raise SystemExit('REFERENCE_V95 generator required before v9.6')

marker='# REFERENCE_V95: three tapered convex scalp leaves per side replace the detached ear-pad lock with a continuous swept temple-to-rear flow.'
if marker not in s:
    raise SystemExit('v9.6 REFERENCE_V95 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V96: anatomically readable ears and unified temporal-hair tone make the remaining exposed side skin intentional rather than bald.',1)

mat_anchor="FACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)\n"
if mat_anchor not in s:
    raise SystemExit('v9.6 ear material anchor missing')
s=s.replace(mat_anchor,mat_anchor+"EAR_SHADOW=material('Ear Inner',(0.255,0.145,0.135),0,.78)\n",1)

hair_anchor="# Hair v5.9: broad layered side sweep with an open eye line, plus a much fuller high pony cascade.\n"
ear_block="""# v9.6: low-profile ears turn the remaining side-head skin into intentional anatomy.
# They sit under the temporal leaves; the helix/concha lines are restrained enough for portrait scale.
for side in (-1,1):
 ear_x=side*head_w*.482
 ear_z=-head_d*.010
 add_sphere(HEAD,f'EarMassV96_{side}',(ear_x,-.022,ear_z),(.0092,.034,.0125),SKIN,24,16)
 rim_x=side*head_w*.511
 add_strand(HEAD,f'EarHelixV96_{side}',[
  (rim_x,.006,ear_z+.0075),(rim_x,.019,ear_z+.0025),(rim_x,.013,ear_z-.0055),
  (rim_x,-.010,ear_z-.0090),(rim_x,-.035,ear_z-.0060),(rim_x,-.048,ear_z+.0015)
 ],.00105,EAR_SHADOW)
 add_strand(HEAD,f'EarConchaV96_{side}',[
  (rim_x,-.002,ear_z+.0025),(rim_x,-.013,ear_z-.0025),(rim_x,-.027,ear_z-.0010),
  (rim_x,-.034,ear_z+.0035)
 ],.00078,EAR_SHADOW)

"""+hair_anchor
if hair_anchor not in s:
    raise SystemExit('v9.6 hair insertion anchor missing')
s=s.replace(hair_anchor,ear_block,1)

# Remove the brown petal read: all three structural temple leaves use the same dark hair material.
old=""" ],HAIR_HI,9)
 add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Rear_{side}',side,[
"""
new=""" ],HAIR,9)
 # A hairline-thin direction accent supplies variation without turning a whole leaf brown.
 add_strand(HEAD,f'TemporalFlowV96_{side}',[
  (side*head_w*.486,.142,-head_d*.052),
  (side*head_w*.526,.078,-head_d*.078),
  (side*head_w*.510,.010,-head_d*.108),
  (side*head_w*.474,-.030,-head_d*.124)
 ],.000040,HAIR_HI)
 add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Rear_{side}',side,[
"""
if old not in s:
    raise SystemExit('v9.6 mid-leaf material anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V96: subtle ears plus unified temporal leaf tone')
