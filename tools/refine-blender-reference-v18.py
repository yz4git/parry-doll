from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V18' in s:
    print('Blender heroine generator already carries REFERENCE_V18')
    raise SystemExit(0)
if '# REFERENCE_V17' not in s:
    raise SystemExit('REFERENCE_V17 generator required before v1.8')
s=s.replace('# REFERENCE_V17: portrait readability, shoulder continuity and refined heels.','# REFERENCE_V17: portrait readability, shoulder continuity and refined heels.\n# REFERENCE_V18: natural hairline, clavicle bridge and stronger feminine torso curvature.',1)

# Strengthen the upper torso without changing the locked shoulder width.
anchor=s.index('# Reference-like harness:')
upper='''# Upper torso continuity: clavicle/shoulder bridge stays inside the measured shoulder envelope.
for side in(-1,1):
 add_sphere(TORSO,f'ClavicleBlend_{side}',(side*bust_w*.390,.245,.006),(bust_w*.145,.060,bust_d*.175),BLACK,28,18)
 add_panel(TORSO,f'ShoulderStrap_{side}',[(side*bust_w*.265,.285,bust_d*.30),(side*bust_w*.445,.245,bust_d*.18),(side*bust_w*.450,.185,bust_d*.24),(side*bust_w*.285,.205,bust_d*.36)],.018,BLACK)
'''
s=s[:anchor]+upper+s[anchor:]

# Replace the small chest contour with a more continuous feminine front curve.
a=s.index('# Small front-biased contours carry the chest highlight')
b=s.index('# Upper torso continuity:',a)
bust='''# Front-biased contours define the bust from front/side while staying within the measured bust width.
for side in(-1,1):
 add_sphere(TORSO,f'BustContour_{side}',(side*bust_w*.205,.125,bust_d*.350),(bust_w*.205,.086,bust_d*.245),BLACK,32,20)
add_box(TORSO,'UnderBustLine',(0,.045,bust_d*.485),(bust_w*.72,.018,.012),SILVER,.004)
'''
s=s[:a]+bust+s[b:]

# Portrait v1.8: push all solid scalp masses behind the forehead and let many tapered strands form the hairline.
a=s.index('# === HEAD / FACE ===')
b=s.index('# === LIMBS ===',a)
head='''# === HEAD / FACE ===
add_sphere(HEAD,'Cranium',(0,.012,-.026),(head_w*.480,.111,head_d*.468),SKIN,44,30)
add_sphere(HEAD,'Cheek',(0,-.036,.038),(head_w*.382,.060,head_d*.382),SKIN,40,24)
add_sphere(HEAD,'Jaw',(0,-.078,.049),(head_w*.310,.041,head_d*.315),SKIN,36,22)
add_sphere(HEAD,'Chin',(0,-.118,.069),(head_w*.160,.019,head_d*.180),SKIN,28,16)
add_cylinder(HEAD,'Neck',(0,-.154,-.006),W('neck')*.34,.086,SKIN,24)
add_cylinder(HEAD,'Choker',(0,-.137,-.004),W('neck')*.46,.034,BLACK,26)
add_cylinder(HEAD,'ChokerTrim',(0,-.123,-.004),W('neck')*.47,.009,SILVER,26)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.460,-.018,-.006),(.011,.023,.010),SKIN,18,10)
face_z=head_d*.500
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.158,.013,face_z),(head_w*.090,.0105,.0060),SCLERA,28,14)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.158,.011,face_z+.0068),(head_w*.040,.0085,.0043),IRIS,22,12)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.158,.011,face_z+.0095),(head_w*.014,.0054,.0026),PUPIL,16,10)
 add_box(HEAD,f'UpperLash_{side}',(side*head_w*.158,.029,face_z+.0092),(head_w*.104,.0044,.0030),HAIR,.0012,rot=(0,0,-side*.090))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.158,.062,face_z+.001),(head_w*.100,.0042,.0030),HAIR,.0012,rot=(0,0,-side*.095))
add_sphere(HEAD,'NoseBridge',(0,.004,face_z+.002),(.008,.029,.0065),SKIN,18,10)
add_sphere(HEAD,'NoseTip',(0,-.026,face_z+.009),(.009,.014,.0085),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.071,face_z+.0035),(.044,.0048,.0032),LIP,.0010)
# Solid scalp is entirely rearward; it must never create a horizontal forehead band.
add_sphere(HEAD,'HairBack',(0,.022,-head_d*.355),(head_w*.515,.127,head_d*.465),HAIR,42,28)
add_sphere(HEAD,'HairCrown',(0,.088,-head_d*.365),(head_w*.455,.050,head_d*.285),HAIR,40,24)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.410,.004,-.025),(head_w*.095,.082,head_d*.160),HAIR,28,18)
# Nine narrow crown-to-fringe ribbons form a broken, natural hairline rather than a visor.
fringe=[(-.112,-.090,-.078,.030),(-.084,-.060,-.055,.032),(-.058,-.036,-.032,.034),(-.030,-.014,-.012,.035),(-.004,.006,.008,.034),(.024,.028,.030,.033),(.052,.050,.050,.032),(.080,.074,.070,.030),(.106,.098,.087,.027)]
for i,(sx,mx,ex,w0) in enumerate(fringe):
 ey=.006-.010*abs((i-4)/4)
 add_ribbon(HEAD,f'FringeSweep_{i}',[(sx,.112,-.018),(mx,.086,face_z*.30),(ex,.056,face_z*.61),(ex*.96,ey,face_z+.002)],[w0,w0*.88,w0*.54,w0*.12],.0048,HAIR_HI if i in(2,6) else HAIR)
# Fine face framing strands break the side silhouette around cheeks/ears.
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.365,.065,-.006),(side*head_w*.440,-.018,head_d*.115),(side*head_w*.455,-.185,head_d*.045),(side*head_w*.390,-.410,-.018)],[.040,.036,.025,.010],.0052,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.405,.042,-.014),(side*head_w*.475,-.082,head_d*.065),(side*head_w*.485,-.270,.004),(side*head_w*.425,-.485,-.040)],[.020,.018,.013,.006],.0038,HAIR_HI)
# High ponytail root and layered mass.
add_sphere(HEAD,'PonyRootMass',(0,.145,-head_d*.405),(.076,.061,.064),HAIR,32,22)
add_box(HEAD,'HairTie',(0,.141,-head_d*.465),(.090,.023,.034),SILVER,.007)
for side in(-1,1):add_box(HEAD,f'HairTieFin_{side}',(side*.055,.145,-head_d*.470),(.009,.086,.018),SILVER,.003,rot=(0,0,side*.18))
PONY=empty('BL_PONY_DYNAMIC',HEAD)
add_section_mesh(PONY,'PonyCore',[
 (.142,.042,.026,.033,-head_d*.46),
 (.020,.078,.040,.052,-head_d*.71),
 (-.250,.120,.052,.068,-.435),
 (-.560,.148,.062,.078,-.350),
 (-.900,.145,.060,.074,-.268),
 (-1.230,.112,.046,.058,-.185),
 (-1.490,.067,.028,.038,-.100),
 (-1.650,.030,.016,.021,-.042)
],HAIR,36)
for i in range(9):
 lane=(i-4)/4
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.020,.138,-head_d*.48),(lane*.064,-.015,-head_d*.72),(lane*.130,-.330,-.440),(lane*.205,-.760,-.318),(lane*.285,-1.225,-.185),(lane*.330,-1.625,-.046)],[.044,.058,.070,.066,.045,.010],.0052,HAIR_HI if i in(2,6) else HAIR)
for i in range(10):
 lane=(i-4.5)/4.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.024,.132,-head_d*.48),(lane*.082,-.080,-head_d*.74),(lane*.155,-.500,-.410),(lane*.245,-1.030,-.240),(lane*.340,-1.665,-.032)],.0031+(i%2)*.0006,HAIR_HI if i%3==0 else HAIR)

'''
s=s[:a]+head+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V18: natural broken hairline, stronger bust curve and clavicle bridge')
