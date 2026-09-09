from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V20' in s:
    print('Blender heroine generator already carries REFERENCE_V20')
    raise SystemExit(0)
if '# REFERENCE_V19' not in s:
    raise SystemExit('REFERENCE_V19 generator required before v2.0')
s=s.replace('# REFERENCE_V19: continuous portrait shell and face-plane retarget.','# REFERENCE_V19: continuous portrait shell and face-plane retarget.\n# REFERENCE_V20: fuller bodice curve, longer fringe, deeper ponytail and broader front couture.',1)

# Stronger chest-to-waist curve while keeping the measured envelope and narrow shoulders.
a=s.index("add_section_mesh(TORSO,'TorsoSuit'")
b=s.index("# Front-biased contours define the bust",a)
torso="""add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.50,waist_d*.50,waist_d*.56,-.006),
 (-.255,waist_w*.46,waist_d*.48,waist_d*.57,-.002),
 (-.145,bust_w*.35,bust_d*.40,bust_d*.48,.006),
 (-.020,bust_w*.45,bust_d*.43,bust_d*.58,.017),
 (.095,bust_w*.51,bust_d*.45,bust_d*.70,.032),
 (.185,bust_w*.49,bust_d*.43,bust_d*.62,.025),
 (.260,bust_w*.43,bust_d*.39,bust_d*.50,.012),
 (.315,bust_w*.35,bust_d*.34,bust_d*.39,.002)
],BLACK,44)
"""
s=s[:a]+torso+s[b:]

# Refine bust volumes and bring the white side panels slightly forward so the hourglass reads in-game.
a=s.index("# Front-biased contours define the bust")
b=s.index("# Upper torso continuity",a)
bust="""# Front-biased contours define the bust from front/side while staying within the measured bust width.
for side in(-1,1):
 add_sphere(TORSO,f'BustContour_{side}',(side*bust_w*.205,.115,bust_d*.390),(bust_w*.220,.100,bust_d*.285),BLACK,34,22)
add_box(TORSO,'UnderBustLine',(0,.028,bust_d*.535),(bust_w*.74,.017,.011),SILVER,.004)
for side in(-1,1):
 add_box(TORSO,f'WaistContour_{side}',(side*waist_w*.44,-.145,waist_d*.54),(.014,.190,.010),SILVER,.004,rot=(0,0,-side*.17))
"""
s=s[:a]+bust+s[b:]

# Broader front couture: one readable white center field plus dark side petals, closer to the supplied sheet.
a=s.index("add_panel(PELVIS,'FrontCenterL'")
b=s.index("# Side tails stay narrow",a)
front_skirt="""add_panel(PELVIS,'FrontCenterL',[(-.150,.122,.138),(-.008,.116,.148),(-.020,-.205,.157),(-.082,-.335,.142),(-.178,-.185,.102)],.018,WHITE)
add_panel(PELVIS,'FrontCenterR',[(.008,.116,.148),(.150,.122,.138),(.178,-.185,.102),(.082,-.335,.142),(.020,-.205,.157)],.018,WHITE)
add_panel(PELVIS,'HipPetalL',[(-.115,.118,.120),(-.238,.094,.094),(-.292,-.100,.070),(-.220,-.275,.088),(-.126,-.160,.122)],.016,BLACK)
add_panel(PELVIS,'HipPetalR',[(.115,.118,.120),(.126,-.160,.122),(.220,-.275,.088),(.292,-.100,.070),(.238,.094,.094)],.016,BLACK)
add_panel(PELVIS,'WhitePetalL',[(-.188,.105,.106),(-.258,.070,.074),(-.304,-.185,.052),(-.238,-.365,.070),(-.170,-.195,.110)],.014,WHITE)
add_panel(PELVIS,'WhitePetalR',[(.188,.105,.106),(.170,-.195,.110),(.238,-.365,.070),(.304,-.185,.052),(.258,.070,.074)],.014,WHITE)
"""
s=s[:a]+front_skirt+s[b:]

# Replace the short fringe with longer overlapping layers that visibly cross the forehead.
a=s.index("# Layered bangs cover the upper forehead")
b=s.index("# Longer side fringe frames",a)
fringe="""# Layered bangs cross the forehead and taper around the eyes like the reference.
add_ribbon(HEAD,'CrownSweepL',[(-.012,.133,-.046),(-.050,.116,-.004),(-.086,.090,face_z*.42),(-.104,.048,face_z*.77)],[.080,.076,.058,.026],.0054,HAIR)
add_ribbon(HEAD,'CrownSweepR',[(.012,.133,-.046),(.044,.116,-.006),(.080,.090,face_z*.40),(.098,.050,face_z*.74)],[.076,.072,.054,.024],.0054,HAIR_HI)
fringe=[(-.120,-.106,-.095,.042,-.038),(-.096,-.080,-.071,.043,-.030),(-.071,-.055,-.049,.044,-.022),(-.045,-.031,-.028,.045,-.015),(-.020,-.010,-.010,.044,-.010),(.006,.012,.010,.043,-.012),(.032,.038,.033,.042,-.017),(.058,.065,.055,.040,-.023),(.084,.091,.076,.038,-.031),(.108,.114,.097,.035,-.040)]
for i,(sx,mx,ex,w0,ey) in enumerate(fringe):
 add_ribbon(HEAD,f'FringeSweep_{i}',[(sx,.122,-.025),(mx,.100,face_z*.34),(ex,.065,face_z*.69),(ex*.97,ey,face_z+.016)],[w0,w0*.96,w0*.62,w0*.15],.0048,HAIR_HI if i in(2,7) else HAIR)
"""
s=s[:a]+fringe+s[b:]

# Give the ponytail more side-view depth and a wider upper cascade while retaining the long taper.
a=s.index("add_section_mesh(PONY,'PonyCore'")
b=s.index("# === LIMBS ===",a)
pony="""add_section_mesh(PONY,'PonyCore',[
 (.150,.055,.040,.052,-head_d*.49),
 (.025,.095,.061,.076,-head_d*.76),
 (-.235,.142,.073,.090,-.465),
 (-.545,.168,.081,.102,-.375),
 (-.895,.162,.077,.096,-.282),
 (-1.225,.128,.061,.075,-.190),
 (-1.500,.078,.039,.050,-.102),
 (-1.665,.034,.019,.026,-.040)
],HAIR,40)
for i in range(11):
 lane=(i-5)/5
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.026,.143,-head_d*.50),(lane*.075,-.010,-head_d*.78),(lane*.150,-.325,-.470),(lane*.235,-.755,-.338),(lane*.318,-1.225,-.192),(lane*.365,-1.645,-.045)],[.047,.066,.080,.073,.048,.010],.0050,HAIR_HI if i in(2,8) else HAIR)
for i in range(12):
 lane=(i-5.5)/5.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.026,.138,-head_d*.51),(lane*.092,-.080,-head_d*.80),(lane*.175,-.505,-.438),(lane*.270,-1.035,-.250),(lane*.370,-1.685,-.030)],.0030+(i%2)*.0006,HAIR_HI if i%4==0 else HAIR)

"""
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V20: bodice curve, long fringe, deep ponytail and broader front couture')
