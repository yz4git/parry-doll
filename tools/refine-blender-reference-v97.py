from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V97' in s:
    print('Blender heroine generator already carries REFERENCE_V97')
    raise SystemExit(0)
if '# REFERENCE_V96' not in s:
    raise SystemExit('REFERENCE_V96 generator required before v9.7')

marker='# REFERENCE_V96: anatomically readable ears and unified temporal-hair tone make the remaining exposed side skin intentional rather than bald.'
if marker not in s:
    raise SystemExit('v9.7 REFERENCE_V96 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V97: rear hair shell wraps forward around both temples; duplicate v9.6 ears are removed while the original EarV78 anatomy remains.',1)

# v9.6 accidentally added a second ear set even though EarV78 already exists at the measured side-head position.
# Remove only that duplicate block and keep the original ears plus the unified dark temporal leaves.
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

"""
if ear_block not in s:
    raise SystemExit('v9.7 duplicate ear block missing')
s=s.replace(ear_block,"""# v9.7: EarV78 is the single canonical ear set; no duplicate side anatomy is added here.\n\n""",1)

# The real remaining gap is the open temple seam of the rear shell.  Wrap that shell ~20 degrees
# forward on both sides.  It stays at the outer skull radius, so it does not cross the eye/nose plane,
# while the three v9.5 leaves remain visible as foreground strand structure.
old="angles=[math.pi+.055+(math.pi-.110)*i/segments for i in range(segments+1)]"
new="angles=[math.pi-.34+(math.pi+.68)*i/segments for i in range(segments+1)]"
if old not in s:
    raise SystemExit('v9.7 rear-shell angle anchor missing')
s=s.replace(old,new,1)

# The old comment described an intentionally open temple seam; update it to match the wrapped shell.
old_comment="# Close the two temple seams and the small top/bottom openings, while leaving the face fully open."
new_comment="# Close the wrapped temple boundaries and top/bottom openings; the expanded arc covers side scalp while leaving the central face open."
if old_comment in s:
    s=s.replace(old_comment,new_comment,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V97: forward-wrapped rear hair shell, canonical single EarV78 set')
