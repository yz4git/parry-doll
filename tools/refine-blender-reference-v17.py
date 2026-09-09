from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V17' in s:
    print('Blender heroine generator already carries REFERENCE_V17')
    raise SystemExit(0)
if '# REFERENCE_V16' not in s:
    raise SystemExit('REFERENCE_V16 generator required before v1.7')
s=s.replace('# REFERENCE_V16: side-curve, face and pony-root polish.','# REFERENCE_V16: side-curve, face and pony-root polish.\n# REFERENCE_V17: portrait readability, shoulder continuity and refined heels.',1)

# Portrait v1.7: reduce the visor-like forehead band, enlarge/read the eyes, shorten visible neck,
# and make the ponytail root flow into a layered high ponytail instead of a hard cap + vertical sheet.
a=s.index('# === HEAD / FACE ===')
b=s.index('# === LIMBS ===',a)
head='''# === HEAD / FACE ===
# Reference-locked compact skull with tapered lower face.
add_sphere(HEAD,'Cranium',(0,.012,-.024),(head_w*.482,.112,head_d*.470),SKIN,44,30)
add_sphere(HEAD,'Cheek',(0,-.036,.036),(head_w*.385,.061,head_d*.385),SKIN,40,24)
add_sphere(HEAD,'Jaw',(0,-.077,.046),(head_w*.315,.042,head_d*.320),SKIN,36,22)
add_sphere(HEAD,'Chin',(0,-.116,.066),(head_w*.165,.020,head_d*.185),SKIN,28,16)
add_cylinder(HEAD,'Neck',(0,-.154,-.006),W('neck')*.34,.088,SKIN,24)
add_cylinder(HEAD,'Choker',(0,-.137,-.004),W('neck')*.46,.035,BLACK,26)
add_cylinder(HEAD,'ChokerTrim',(0,-.123,-.004),W('neck')*.47,.010,SILVER,26)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.462,-.018,-.006),(.011,.023,.010),SKIN,18,10)
face_z=head_d*.500
for side in(-1,1):
 # Larger almond-like layered eyes remain readable at the model-viewer distance.
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.158,.012,face_z),(head_w*.086,.010,.0058),SCLERA,26,14)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.158,.010,face_z+.0065),(head_w*.036,.0082,.0041),IRIS,20,12)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.158,.010,face_z+.0092),(head_w*.013,.0052,.0025),PUPIL,16,10)
 add_box(HEAD,f'UpperLash_{side}',(side*head_w*.158,.028,face_z+.0090),(head_w*.101,.0045,.0030),HAIR,.0012,rot=(0,0,-side*.085))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.158,.061,face_z+.001),(head_w*.100,.0042,.0030),HAIR,.0012,rot=(0,0,-side*.095))
add_sphere(HEAD,'NoseBridge',(0,.004,face_z+.002),(.008,.029,.0065),SKIN,18,10)
add_sphere(HEAD,'NoseTip',(0,-.025,face_z+.009),(.009,.014,.0085),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.071,face_z+.003),(.042,.0045,.0030),LIP,.0010)
# Back/crown masses stay behind the facial plane. No broad sheet is allowed to cross the forehead.
add_sphere(HEAD,'HairBack',(0,.020,-head_d*.315),(head_w*.515,.126,head_d*.530),HAIR,42,28)
add_sphere(HEAD,'HairCrown',(0,.080,-head_d*.225),(head_w*.475,.056,head_d*.390),HAIR,40,26)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.405,.004,-.018),(head_w*.100,.082,head_d*.175),HAIR,28,18)
# Narrow swept crown strands replace the v1.6 visor-like top ribbons.
sweeps=[(-.102,-.070,-.040,.030),(-.064,-.040,-.018,.032),(-.028,-.010,.004,.034),(.016,.020,.020,.033),(.054,.052,.042,.031),(.090,.084,.060,.028)]
for i,(sx,mx,ex,w0) in enumerate(sweeps):
 add_ribbon(HEAD,f'CrownSweep_{i}',[(sx,.112,-.025),(mx,.088,face_z*.34),(ex,.055,face_z*.63),(ex*.90,.028,face_z*.79)],[w0,w0*.92,w0*.66,w0*.24],.0054,HAIR_HI if i in(1,4) else HAIR)
# Asymmetric tapered bangs, leaving a visible forehead gap and eye line.
bangs=[(-.090,-.018,-.066,.040),(-.055,.000,-.036,.043),(-.019,.020,-.006,.042),(.020,.010,.020,.040),(.054,-.008,.049,.039),(.088,-.030,.075,.036)]
for i,(sx,ey,ex,w0) in enumerate(bangs):
 add_ribbon(HEAD,f'BangSheet_{i}',[(sx,.090,.012),(sx*.82,.068,face_z*.52),(ex*.90,.038,face_z-.002),(ex,ey,face_z+.003)],[w0,w0*.88,w0*.54,w0*.15],.0053,HAIR_HI if i in(1,4) else HAIR)
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.370,.060,-.004),(side*head_w*.445,-.020,head_d*.12),(side*head_w*.455,-.185,head_d*.050),(side*head_w*.390,-.405,-.016)],[.042,.038,.027,.011],.0055,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.410,.038,-.012),(side*head_w*.480,-.085,head_d*.070),(side*head_w*.485,-.270,.008),(side*head_w*.425,-.475,-.038)],[.022,.020,.015,.007],.0040,HAIR_HI)
# Gathered high root flows backward before falling, matching the reference side silhouette.
add_sphere(HEAD,'PonyRootMass',(0,.142,-head_d*.39),(.078,.062,.066),HAIR,32,22)
add_box(HEAD,'HairTie',(0,.138,-head_d*.45),(.092,.024,.036),SILVER,.007)
for side in(-1,1):add_box(HEAD,f'HairTieFin_{side}',(side*.058,.142,-head_d*.455),(.010,.090,.020),SILVER,.003,rot=(0,0,side*.18))
PONY=empty('BL_PONY_DYNAMIC',HEAD)
add_section_mesh(PONY,'PonyCore',[
 (.140,.043,.027,.034,-head_d*.45),
 (.020,.078,.040,.052,-head_d*.70),
 (-.250,.120,.052,.068,-.430),
 (-.560,.148,.062,.078,-.350),
 (-.900,.145,.060,.074,-.270),
 (-1.230,.112,.046,.058,-.190),
 (-1.490,.067,.028,.038,-.105),
 (-1.650,.030,.016,.021,-.045)
],HAIR,36)
for i in range(9):
 lane=(i-4)/4
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.020,.135,-head_d*.47),(lane*.064,-.015,-head_d*.71),(lane*.130,-.330,-.435),(lane*.205,-.760,-.315),(lane*.285,-1.225,-.185),(lane*.330,-1.625,-.050)],[.045,.058,.070,.066,.045,.010],.0054,HAIR_HI if i in(2,6) else HAIR)
for i in range(10):
 lane=(i-4.5)/4.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.024,.130,-head_d*.47),(lane*.082,-.080,-head_d*.73),(lane*.155,-.500,-.405),(lane*.245,-1.030,-.240),(lane*.340,-1.665,-.035)],.0032+(i%2)*.0006,HAIR_HI if i%3==0 else HAIR)

'''
s=s[:a]+head+s[b:]

# Humanize limb junctions without widening the measured outer silhouette.
anchor=s.index('# Upper-arm straps + forearm gauntlets;')
blend='''# Soft junction volumes remove the detached mannequin-arm/thigh look while staying inside measured widths.
for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_sphere(group,'DeltoidBlend'+name,(0,-.430,0),(ua*.94,.075,ua_d*.96),SKIN,24,16)
for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_sphere(group,'HipThighBlend'+name,(0,-.430,0),(th*1.02,.082,th_d*.98),SKIN,26,16)
'''
s=s[:anchor]+blend+s[anchor:]

# Replace blocky footwear with a shorter tapered toe, ankle shell and a narrow heel.
a=s.index('# Reference heel silhouette:')
b=s.index('# Slim sword retained',a)
shoe='''# Reference heel silhouette: tapered toe, narrow ankle and separated rear heel.
for group,name in[(FOOT_L,'L'),(FOOT_R,'R')]:
 add_box(group,'ShoeBase'+name,(0,-.040,.085),(ank*1.72,.070,.220),BLACK,.018)
 add_box(group,'ToeCap'+name,(0,-.052,.195),(ank*1.60,.052,.095),WHITE,.012)
 add_box(group,'AnkleCuff'+name,(0,.055,.005),(ank*1.82,.095,.090),SILVER,.010)
 add_box(group,'Instep'+name,(0,.008,.085),(ank*1.52,.105,.105),BLACK_SOFT,.014,rot=(.16,0,0))
 add_box(group,'HeelStem'+name,(0,-.120,-.030),(ank*.34,.180,.032),BLACK,.006)
 add_box(group,'HeelTip'+name,(0,-.205,-.030),(ank*.46,.026,.042),SILVER,.004)
'''
s=s[:a]+shoe+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V17: portrait readability, shoulder continuity, layered ponytail and refined heels')
