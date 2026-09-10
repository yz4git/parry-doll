from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V67' in s:
    print('Blender heroine generator already carries REFERENCE_V67')
    raise SystemExit(0)
if '# REFERENCE_V66' not in s:
    raise SystemExit('REFERENCE_V66 generator required before v6.7')

s=s.replace(
    '# REFERENCE_V66: surfaced bust contour, visible white bodice couture and fanned pony flow.',
    '# REFERENCE_V66: surfaced bust contour, visible white bodice couture and fanned pony flow.\n# REFERENCE_V67: integrated bust contour, upper-chest couture wings, almond gaze and wide high-pony silhouette.',
    1,
)

# Integrate the bust into the ribcage instead of reading as two round black capsules.
s=s.replace(
    "add_sphere(TORSO,f'BustContourV66_{side}',(side*bust_w*.205,.100,bust_d*.655),(bust_w*.245,.092,bust_d*.160),BLACK,44,28)",
    "add_sphere(TORSO,f'BustContourV67_{side}',(side*bust_w*.182,.102,bust_d*.670),(bust_w*.205,.074,bust_d*.112),BLACK_SOFT,44,28)",
    1,
)

# Broader porcelain chest wings frame the black centre and make the fitted white/black couture readable from gameplay distance.
anchor="""for side in(-1,1):
 add_box(TORSO,f'BodiceEdgeV66_{side}',(side*bust_w*.275,.030,bust_d*.670),(.012,.330,.009),SILVER,.0035,rot=(0,0,side*.08))
 add_box(TORSO,f'UpperArmBandV35_{side}',(side*.205,.215,.000),(.040,.020,.072),BLACK,.004)
"""
insert=anchor+"""
# v6.7 upper-chest panels sit on the true front envelope and taper into the narrow waist.
add_panel(TORSO,'ChestWingV67_L',[(-bust_w*.505,.248,bust_d*.455),(-bust_w*.245,.226,bust_d*.595),(-bust_w*.205,.080,bust_d*.790),(-bust_w*.465,.066,bust_d*.690)],.012,WHITE)
add_panel(TORSO,'ChestWingV67_R',[(bust_w*.245,.226,bust_d*.595),(bust_w*.505,.248,bust_d*.455),(bust_w*.465,.066,bust_d*.690),(bust_w*.205,.080,bust_d*.790)],.012,WHITE)
add_panel(TORSO,'WaistWingV67_L',[(-bust_w*.455,.060,bust_d*.675),(-bust_w*.205,.076,bust_d*.790),(-waist_w*.235,-.205,waist_d*.760),(-waist_w*.545,-.232,waist_d*.655)],.011,WHITE)
add_panel(TORSO,'WaistWingV67_R',[(bust_w*.205,.076,bust_d*.790),(bust_w*.455,.060,bust_d*.675),(waist_w*.545,-.232,waist_d*.655),(waist_w*.235,-.205,waist_d*.760)],.011,WHITE)
for side in(-1,1):
 add_box(TORSO,f'ChestSeamV67_{side}',(side*bust_w*.245,.120,bust_d*.785),(.010,.205,.010),SILVER,.0032,rot=(0,0,side*.11))
"""
if anchor not in s:
    raise SystemExit('v6.6 bodice anchor not found')
s=s.replace(anchor,insert,1)

# Slightly more horizontal eyes reduce the round doll-eye read without reducing iris presence.
s=s.replace('eye_ry=.0154','eye_ry=.0144',1)
s=s.replace('.0262,.0138,IRIS','.0262,.0129,IRIS',1)
s=s.replace('.0208,.0109,IRIS_INNER','.0208,.0101,IRIS_INNER',1)
s=s.replace('.0038,.0047,PUPIL','.0038,.0044,PUPIL',1)
s=s.replace('eye_y+.0160','eye_y+.0151',1)
s=s.replace('eye_y-.0094','eye_y-.0088',1)

# Large upper-half pony foundations make the high pony fan outward before the long cascade narrows again.
pony_anchor='# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry.'
pony_insert="""# v6.7 broad high-pony wings: overlapping masses, not isolated strings.
for i,(target,drop) in enumerate(((-.300,-1.34),(-.205,-1.52),(.195,-1.48),(.295,-1.30))):
 sign=-1 if target<0 else 1
 pts=[
  (sign*.018,.143,-head_d*.550),
  (sign*.034,.035,-head_d*.620),
  (sign*.075,-.165,-.270),
  (target*.48,-.390,-.225),
  (target*.73,-.650,-.178),
  (target,-.930,-.135),
  (target*.90,-1.155,-.108),
  (target*.72,drop,-.086)
 ]
 widths=[.050,.090,.120,.132,.122,.102,.066,.010]
 depths=[.027,.043,.052,.056,.051,.043,.030,.007]
 add_smooth_lock(PONY,f'PonyWingV67_{i}',pts,widths,depths,HAIR if i in (0,3) else HAIR_HI,16,8)
# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry."""
if pony_anchor not in s:
    raise SystemExit('pony anchor not found')
s=s.replace(pony_anchor,pony_insert,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V67: integrated couture torso, almond gaze and wide high pony')
