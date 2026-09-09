from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V16' in s:
    print('Blender heroine generator already carries REFERENCE_V16')
    raise SystemExit(0)
if '# REFERENCE_V15' not in s:
    raise SystemExit('REFERENCE_V15 generator required before v1.6')
s=s.replace('# REFERENCE_V15: hair mass, portrait and layered couture polish.','# REFERENCE_V15: hair mass, portrait and layered couture polish.\n# REFERENCE_V16: side-curve, face and pony-root polish.',1)

# Give the bodice the reference's chest/waist depth transition instead of a straight dark slab.
a=s.index('# Torso follows the measured hourglass envelope as a single continuous surface.')
b=s.index('# Small front-biased bust volumes',a)
torso='''# Torso follows the measured hourglass envelope as a single continuous surface.
# Front depth peaks at the bust while the lower back eases toward the high waist, matching the side sheet.
add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.53,waist_d*.52,waist_d*.58,-.004),
 (-.245,waist_w*.49,waist_d*.50,waist_d*.58,0.000),
 (-.115,bust_w*.39,bust_d*.42,bust_d*.49,0.007),
 (.010,bust_w*.46,bust_d*.44,bust_d*.58,0.018),
 (.130,bust_w*.50,bust_d*.45,bust_d*.66,0.028),
 (.225,bust_w*.47,bust_d*.41,bust_d*.53,0.016),
 (.315,bust_w*.38,bust_d*.35,bust_d*.40,0.003)
],BLACK,40)
'''
s=s[:a]+torso+s[b:]

# Make the bust contour part of the bodice read from profile without returning to two spherical pods.
a=s.index('# Small front-biased bust volumes')
b=s.index('# Reference-like harness:',a)
bust='''# Small front-biased contours carry the chest highlight from oblique/profile views.
for side in(-1,1):
 add_sphere(TORSO,f'BustContour_{side}',(side*bust_w*.205,.125,bust_d*.330),(bust_w*.190,.082,bust_d*.215),BLACK,30,18)
'''
s=s[:a]+bust+s[b:]

# Add a single continuous back curve to the pelvis rather than separate butt primitives.
a=s.index("add_section_mesh(PELVIS,'PelvisSuit'")
b=s.index("add_box(PELVIS,'HighWaist'",a)
pelvis='''add_section_mesh(PELVIS,'PelvisSuit',[
 (-.180,pelvis_w*.42,pelvis_d*.60,pelvis_d*.48,-.018),
 (-.080,pelvis_w*.50,pelvis_d*.58,pelvis_d*.52,-.012),
 (.040,pelvis_w*.49,pelvis_d*.52,pelvis_d*.51,-.005),
 (.155,waist_w*.57,waist_d*.56,waist_d*.59,0.000)
],BLACK,36)
'''
s=s[:a]+pelvis+s[b:]

# Portrait v1.6: narrower jaw, exposed forehead, swept top hair and a clearly high ponytail root.
a=s.index('# === HEAD / FACE ===')
b=s.index('# === LIMBS ===',a)
head='''# === HEAD / FACE ===
# Compact skull with a narrower jaw/chin; dimensions remain tied to the measured head width/depth.
add_sphere(HEAD,'Cranium',(0,.010,-.020),(head_w*.488,.114,head_d*.475),SKIN,42,28)
add_sphere(HEAD,'Jaw',(0,-.058,.034),(head_w*.365,.069,head_d*.375),SKIN,38,22)
add_sphere(HEAD,'Chin',(0,-.108,.061),(head_w*.195,.025,head_d*.220),SKIN,28,16)
add_cylinder(HEAD,'Neck',(0,-.158,-.004),W('neck')*.36,.098,SKIN,24)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.475,-.012,-.005),(.012,.025,.010),SKIN,18,10)
face_z=head_d*.495
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.160,.006,face_z),(head_w*.074,.009,.0055),SCLERA,24,12)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.160,.006,face_z+.006),(head_w*.029,.0075,.0037),IRIS,18,10)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.160,.006,face_z+.0085),(head_w*.0105,.0048,.0023),PUPIL,14,8)
 add_box(HEAD,f'Eyeliner_{side}',(side*head_w*.160,.022,face_z+.008),(head_w*.091,.0045,.0030),HAIR,.0013,rot=(0,0,-side*.095))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.160,.052,face_z+.001),(head_w*.098,.0045,.0032),HAIR,.0013,rot=(0,0,-side*.095))
add_sphere(HEAD,'Nose',(0,-.013,face_z+.006),(.0085,.020,.0075),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.064,face_z+.003),(.038,.0045,.0032),LIP,.0011)
# Move the solid scalp behind the hairline; forehead silhouette now comes from swept layers, not a helmet rim.
add_sphere(HEAD,'HairBack',(0,.022,-head_d*.31),(head_w*.515,.126,head_d*.535),HAIR,40,26)
add_sphere(HEAD,'HairCrown',(0,.074,-head_d*.18),(head_w*.475,.061,head_d*.425),HAIR,38,24)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.405,.002,-.010),(head_w*.105,.086,head_d*.190),HAIR,26,18)
# Broad crown sweeps give the parting visible in the reference before the bangs fall over the forehead.
add_ribbon(HEAD,'TopSweepL',[(-.015,.122,-.035),(-.055,.102,.020),(-.095,.070,face_z*.50),(-.105,.020,face_z*.80)],[.074,.072,.058,.025],.0065,HAIR)
add_ribbon(HEAD,'TopSweepR',[(.015,.122,-.035),(.050,.102,.018),(.090,.070,face_z*.48),(.102,.018,face_z*.78)],[.070,.068,.054,.024],.0065,HAIR_HI)
# Five overlapping asymmetric bangs, all tapered before they reach eye level.
bangs=[(-.086,-.032,-.070,.056),(-.048,-.004,-.033,.061),(-.008,.014,.012,.064),(.038,-.008,.043,.058),(.080,-.038,.073,.052)]
for i,(sx,ey,ex,w0) in enumerate(bangs):
 add_ribbon(HEAD,f'BangSheet_{i}',[(sx,.096,.012),(sx*.80,.073,face_z*.58),(ex*.84,.038,face_z-.004),(ex,ey,face_z+.003)],[w0,w0*.94,w0*.60,w0*.20],.006,HAIR_HI if i in(1,3) else HAIR)
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.370,.060,.005),(side*head_w*.445,-.025,head_d*.13),(side*head_w*.455,-.190,head_d*.055),(side*head_w*.395,-.410,-.012)],[.046,.042,.030,.012],.006,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.410,.040,-.005),(side*head_w*.480,-.090,head_d*.08),(side*head_w*.490,-.275,.015),(side*head_w*.435,-.490,-.032)],[.024,.023,.017,.008],.0045,HAIR_HI)
# High gathered root is visible above/behind the crown like the supplied four-view sheet.
add_sphere(HEAD,'PonyRootMass',(0,.142,-head_d*.36),(.085,.070,.068),HAIR,30,20)
add_box(HEAD,'HairTie',(0,.142,-head_d*.43),(.098,.026,.038),SILVER,.008)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
add_section_mesh(PONY,'PonyCore',[
 (.145,.048,.030,.038,-head_d*.43),
 (.020,.080,.042,.054,-head_d*.66),
 (-.285,.122,.054,.070,-.395),
 (-.640,.145,.061,.076,-.325),
 (-1.000,.130,.053,.065,-.232),
 (-1.305,.090,.037,.047,-.150),
 (-1.505,.043,.021,.027,-.075)
],HAIR,34)
for i in range(7):
 lane=(i-3)/3
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.025,.138,-head_d*.45),(lane*.072,-.020,-head_d*.69),(lane*.140,-.400,-.405),(lane*.210,-.900,-.285),(lane*.278,-1.485,-.085)],[.054,.062,.067,.050,.013],.006,HAIR_HI if i in(1,5) else HAIR)
for i in range(8):
 lane=(i-3.5)/3.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.030,.135,-head_d*.46),(lane*.088,-.060,-head_d*.71),(lane*.165,-.505,-.385),(lane*.250,-1.025,-.235),(lane*.335,-1.550,-.055)],.0036+(i%2)*.0007,HAIR_HI if i%3==0 else HAIR)

'''
s=s[:a]+head+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V16: chest/hip side curve, narrower portrait and high ponytail root')
