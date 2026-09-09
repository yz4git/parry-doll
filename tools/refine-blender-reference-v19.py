from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V19' in s:
    print('Blender heroine generator already carries REFERENCE_V19')
    raise SystemExit(0)
if '# REFERENCE_V18' not in s:
    raise SystemExit('REFERENCE_V18 generator required before v1.9')
s=s.replace('# REFERENCE_V18: natural hairline, clavicle bridge and stronger feminine torso curvature.','# REFERENCE_V18: natural hairline, clavicle bridge and stronger feminine torso curvature.\n# REFERENCE_V19: continuous portrait shell and face-plane retarget.',1)

# Replace the multi-sphere portrait with one continuous section mesh. This removes visible primitive seams
# and gives explicit widths/depths at chin, jaw, cheek, eye, temple and crown heights.
a=s.index('# === HEAD / FACE ===')
b=s.index('# === LIMBS ===',a)
head='''# === HEAD / FACE ===
# One continuous measured portrait shell instead of overlapping spheres.
add_section_mesh(HEAD,'HeadShell',[
 (-.128,head_w*.155,head_d*.225,head_d*.300,.050),
 (-.105,head_w*.250,head_d*.285,head_d*.355,.042),
 (-.078,head_w*.340,head_d*.345,head_d*.410,.030),
 (-.038,head_w*.415,head_d*.390,head_d*.455,.016),
 (.012,head_w*.485,head_d*.435,head_d*.505,.002),
 (.060,head_w*.500,head_d*.465,head_d*.490,-.008),
 (.103,head_w*.455,head_d*.480,head_d*.430,-.018),
 (.135,head_w*.340,head_d*.445,head_d*.330,-.030)
],SKIN,48)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.485,-.018,-.014),(.010,.023,.009),SKIN,18,10)
# Facial plane is tied to the front depth of the eye/cheek rings.
face_z=head_d*.505
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.158,.014,face_z),(head_w*.091,.0105,.0060),SCLERA,30,16)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.158,.012,face_z+.0068),(head_w*.041,.0087,.0043),IRIS,22,12)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.158,.012,face_z+.0096),(head_w*.014,.0054,.0026),PUPIL,16,10)
 add_box(HEAD,f'UpperLash_{side}',(side*head_w*.158,.030,face_z+.0092),(head_w*.105,.0044,.0030),HAIR,.0012,rot=(0,0,-side*.090))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.158,.064,face_z+.001),(head_w*.101,.0042,.0030),HAIR,.0012,rot=(0,0,-side*.095))
# A slim bridge + tip reads in profile without becoming a toy nose.
add_sphere(HEAD,'NoseBridge',(0,.004,face_z+.004),(.0075,.031,.0060),SKIN,20,12)
add_sphere(HEAD,'NoseTip',(0,-.027,face_z+.011),(.0085,.013,.0080),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.073,face_z+.0040),(.044,.0048,.0032),LIP,.0010)
# Rear scalp never crosses the forehead; frontal hair is entirely layered geometry.
add_sphere(HEAD,'HairBack',(0,.022,-head_d*.370),(head_w*.515,.128,head_d*.450),HAIR,44,30)
add_sphere(HEAD,'HairCrown',(0,.093,-head_d*.380),(head_w*.450,.047,head_d*.270),HAIR,40,24)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.414,.006,-.030),(head_w*.093,.080,head_d*.150),HAIR,28,18)
# Layered bangs cover the upper forehead while keeping an irregular, broken hairline.
fringe=[(-.116,-.094,-.082,.033),(-.090,-.070,-.061,.034),(-.064,-.047,-.041,.035),(-.038,-.026,-.022,.036),(-.014,-.006,-.004,.035),(.012,.016,.015,.034),(.038,.040,.036,.033),(.065,.064,.057,.032),(.092,.088,.078,.030),(.114,.106,.096,.027)]
for i,(sx,mx,ex,w0) in enumerate(fringe):
 ey=-.004-.014*abs((i-4.5)/4.5)
 add_ribbon(HEAD,f'FringeSweep_{i}',[(sx,.116,-.020),(mx,.090,face_z*.27),(ex,.055,face_z*.60),(ex*.96,ey,face_z+.003)],[w0,w0*.92,w0*.58,w0*.13],.0047,HAIR_HI if i in(2,7) else HAIR)
# Longer side fringe frames the jaw like the supplied sheet.
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.365,.070,-.006),(side*head_w*.445,-.012,head_d*.115),(side*head_w*.458,-.178,head_d*.044),(side*head_w*.395,-.415,-.020)],[.042,.038,.026,.010],.0052,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.408,.046,-.016),(side*head_w*.478,-.078,head_d*.060),(side*head_w*.486,-.270,.000),(side*head_w*.425,-.495,-.042)],[.020,.018,.013,.006],.0038,HAIR_HI)
# High ponytail with backward launch, broad upper mass and fine taper.
add_sphere(HEAD,'PonyRootMass',(0,.148,-head_d*.410),(.076,.061,.064),HAIR,32,22)
add_box(HEAD,'HairTie',(0,.143,-head_d*.470),(.090,.023,.034),SILVER,.007)
for side in(-1,1):add_box(HEAD,f'HairTieFin_{side}',(side*.055,.147,-head_d*.475),(.009,.086,.018),SILVER,.003,rot=(0,0,side*.18))
PONY=empty('BL_PONY_DYNAMIC',HEAD)
add_section_mesh(PONY,'PonyCore',[
 (.145,.042,.026,.033,-head_d*.47),
 (.025,.080,.041,.053,-head_d*.73),
 (-.240,.122,.053,.069,-.450),
 (-.550,.150,.063,.079,-.360),
 (-.900,.146,.060,.074,-.272),
 (-1.230,.113,.046,.058,-.185),
 (-1.495,.067,.028,.038,-.100),
 (-1.660,.030,.016,.021,-.040)
],HAIR,38)
for i in range(9):
 lane=(i-4)/4
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.020,.140,-head_d*.49),(lane*.064,-.010,-head_d*.74),(lane*.132,-.330,-.455),(lane*.208,-.760,-.325),(lane*.288,-1.230,-.185),(lane*.334,-1.640,-.044)],[.044,.058,.071,.067,.045,.010],.0052,HAIR_HI if i in(2,6) else HAIR)
for i in range(10):
 lane=(i-4.5)/4.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.024,.134,-head_d*.49),(lane*.082,-.080,-head_d*.76),(lane*.158,-.500,-.420),(lane*.248,-1.035,-.242),(lane*.342,-1.680,-.030)],.0031+(i%2)*.0006,HAIR_HI if i%3==0 else HAIR)

'''
s=s[:a]+head+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V19: continuous portrait shell and face-plane retarget')
