from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V25' in s:
    print('Blender heroine generator already carries REFERENCE_V25')
    raise SystemExit(0)
if '# REFERENCE_V24' not in s:
    raise SystemExit('REFERENCE_V24 generator required before v2.5')
s=s.replace('# REFERENCE_V24: eyebrow-height fringe with open eye line.','# REFERENCE_V24: eyebrow-height fringe with open eye line.\n# REFERENCE_V25: larger portrait eyes and strand-separated ponytail mass.',1)

# Enlarge the visible eyes slightly and reduce the lip width for a closer key-art portrait balance.
a=s.index('# Portrait feature plane is projected slightly beyond the continuous head shell.')
b=s.index('# Rear scalp never crosses the forehead;',a)
face='''# Portrait feature plane is projected slightly beyond the continuous head shell.
face_z=head_d*.585
for side in(-1,1):
 ex=side*head_w*.158
 add_panel(HEAD,f'EyePlate_{side}',[(ex-head_w*.102,.033,face_z),(ex+head_w*.102,.033,face_z),(ex+head_w*.082,-.006,face_z),(ex-head_w*.082,-.006,face_z)],.0040,SCLERA)
 add_sphere(HEAD,f'Iris_{side}',(ex,.013,face_z+.0067),(head_w*.050,.0115,.0045),IRIS,24,14)
 add_sphere(HEAD,f'Pupil_{side}',(ex,.013,face_z+.0102),(head_w*.018,.0066,.0029),PUPIL,18,10)
 add_box(HEAD,f'UpperLash_{side}',(ex,.034,face_z+.0092),(head_w*.205,.0064,.0035),HAIR,.0012,rot=(0,0,-side*.080))
 add_box(HEAD,f'Brow_{side}',(ex,.073,face_z+.0040),(head_w*.170,.0048,.0030),HAIR,.0012,rot=(0,0,-side*.095))
 add_sphere(HEAD,f'EyeLight_{side}',(ex-side*head_w*.012,.020,face_z+.0138),(head_w*.011,.0040,.0018),SCLERA,12,8)
add_sphere(HEAD,'NoseBridge',(0,.010,face_z+.001),(.0062,.029,.0053),SKIN,18,10)
add_sphere(HEAD,'NoseTip',(0,-.028,face_z+.008),(.0080,.0115,.0068),SKIN,18,10)
add_panel(HEAD,'UpperLip',[(-.030,-.068,face_z+.006),(.030,-.068,face_z+.006),(.021,-.075,face_z+.007),(-.021,-.075,face_z+.007)],.0024,LIP)
add_panel(HEAD,'LowerLip',[(-.022,-.076,face_z+.006),(.022,-.076,face_z+.006),(.015,-.082,face_z+.005),(-.015,-.082,face_z+.005)],.0020,LIP)
'''
s=s[:a]+face+s[b:]

# Slim the opaque pony core and let the outer ribbons/strands define the silhouette.
a=s.index("add_section_mesh(PONY,'PonyCore'")
b=s.index('# === LIMBS ===',a)
pony="""add_section_mesh(PONY,'PonyCore',[
 (.150,.046,.038,.050,-head_d*.49),
 (.025,.076,.057,.071,-head_d*.76),
 (-.235,.108,.067,.083,-.465),
 (-.545,.126,.073,.090,-.375),
 (-.895,.120,.068,.084,-.282),
 (-1.225,.092,.054,.066,-.190),
 (-1.500,.055,.034,.043,-.102),
 (-1.665,.025,.017,.023,-.040)
],HAIR,40)
for i in range(11):
 lane=(i-5)/5
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.022,.143,-head_d*.50),(lane*.058,-.010,-head_d*.78),(lane*.112,-.325,-.470),(lane*.176,-.755,-.338),(lane*.240,-1.225,-.192),(lane*.276,-1.645,-.045)],[.040,.054,.064,.058,.038,.008],.0046,HAIR_HI if i in(2,8) else HAIR)
for i in range(14):
 lane=(i-6.5)/6.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.024,.138,-head_d*.51),(lane*.072,-.080,-head_d*.80),(lane*.136,-.505,-.438),(lane*.208,-1.035,-.250),(lane*.286,-1.685,-.030)],.0027+(i%2)*.0005,HAIR_HI if i%4==0 else HAIR)

"""
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V25: larger portrait eyes and strand-separated ponytail mass')
