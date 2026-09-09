from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V15' in s:
    print('Blender heroine generator already carries REFERENCE_V15')
    raise SystemExit(0)
if '# REFERENCE_V14' not in s:
    raise SystemExit('REFERENCE_V14 generator required before v1.5')

s=s.replace('# REFERENCE_V14: direct silhouette-driven Blender authoring pass.','# REFERENCE_V14: direct silhouette-driven Blender authoring pass.\n# REFERENCE_V15: hair mass, portrait and layered couture polish.',1)

# Add visible porcelain side bodice pieces; the v1.4 white side panels were too edge-on in the front view.
needle=''' for side in(-1,1):
 add_box(TORSO,f'UpperHarness_{side}',(side*.095,.205,bust_d*.39),(.020,.255,.014),SILVER,.006,rot=(0,0,side*.40))
 add_box(TORSO,f'LowerHarness_{side}',(side*.072,-.080,bust_d*.37),(.018,.210,.014),SILVER,.006,rot=(0,0,-side*.28))
 add_panel(TORSO,f'WhiteSidePanel_{side}',[(side*waist_w*.53,-.23,.02),(side*bust_w*.48,.05,.01),(side*bust_w*.43,.24,.00),(side*waist_w*.56,-.08,.02)],.025,WHITE)
'''
replacement='''for side in(-1,1):
 add_box(TORSO,f'UpperHarness_{side}',(side*.095,.205,bust_d*.39),(.020,.255,.014),SILVER,.006,rot=(0,0,side*.40))
 add_box(TORSO,f'LowerHarness_{side}',(side*.072,-.080,bust_d*.37),(.018,.210,.014),SILVER,.006,rot=(0,0,-side*.28))
 add_panel(TORSO,f'WhiteSidePanel_{side}',[(side*waist_w*.53,-.23,.02),(side*bust_w*.48,.05,.01),(side*bust_w*.43,.24,.00),(side*waist_w*.56,-.08,.02)],.025,WHITE)
 if side<0:
  add_panel(TORSO,'FrontBodiceWhiteL',[(-bust_w*.47,.205,bust_d*.47),(-bust_w*.28,.185,bust_d*.54),(-waist_w*.32,-.205,waist_d*.63),(-waist_w*.58,-.235,waist_d*.52)],.014,WHITE)
  add_box(TORSO,'BustTrimL',(-bust_w*.31,.115,bust_d*.555),(.016,.190,.010),SILVER,.004,rot=(0,0,-.18))
 else:
  add_panel(TORSO,'FrontBodiceWhiteR',[(bust_w*.28,.185,bust_d*.54),(bust_w*.47,.205,bust_d*.47),(waist_w*.58,-.235,waist_d*.52),(waist_w*.32,-.205,waist_d*.63)],.014,WHITE)
  add_box(TORSO,'BustTrimR',(bust_w*.31,.115,bust_d*.555),(.016,.190,.010),SILVER,.004,rot=(0,0,.18))
'''
# tolerate current indentation exactly as committed
if needle not in s:
    needle=needle.replace(' for side','for side')
if needle not in s:raise SystemExit('torso harness block not found')
s=s.replace(needle,replacement,1)

# Recompose the skirt: short fan at the front, long tails pushed outward/back so they no longer read as central curtains.
a=s.index('# Layered pointed skirt measured from the reference silhouette.')
b=s.index('# === HEAD / FACE ===',a)
skirt='''# Layered pointed skirt measured from the reference silhouette.
# A short radial mini-skirt carries the front silhouette; long tails are deliberately outside the leg columns.
add_panel(PELVIS,'FrontCenterL',[(-.125,.120,.132),(-.012,.112,.140),(-.030,-.185,.150),(-.088,-.280,.132),(-.165,-.175,.100)],.018,WHITE)
add_panel(PELVIS,'FrontCenterR',[(.012,.112,.140),(.125,.120,.132),(.165,-.175,.100),(.088,-.280,.132),(.030,-.185,.150)],.018,WHITE)
add_panel(PELVIS,'HipPetalL',[(-.105,.115,.118),(-.225,.092,.092),(-.268,-.090,.070),(-.205,-.235,.088),(-.120,-.145,.120)],.016,BLACK)
add_panel(PELVIS,'HipPetalR',[(.105,.115,.118),(.120,-.145,.120),(.205,-.235,.088),(.268,-.090,.070),(.225,.092,.092)],.016,BLACK)
add_panel(PELVIS,'WhitePetalL',[(-.175,.100,.104),(-.245,.070,.072),(-.282,-.165,.052),(-.225,-.315,.072),(-.165,-.180,.108)],.014,WHITE)
add_panel(PELVIS,'WhitePetalR',[(.175,.100,.104),(.165,-.180,.108),(.225,-.315,.072),(.282,-.165,.052),(.245,.070,.072)],.014,WHITE)
# Side tails stay narrow from the front but become broad, layered shapes in profile.
add_panel(PELVIS,'SideTailWhiteL',[(-.235,.085,.000),(-.285,.055,-.030),(-.338,-.370,-.062),(-.305,-.690,-.022),(-.255,-.455,.028)],.016,WHITE)
add_panel(PELVIS,'SideTailWhiteR',[(.235,.085,.000),(.255,-.455,.028),(.305,-.690,-.022),(.338,-.370,-.062),(.285,.055,-.030)],.016,WHITE)
add_panel(PELVIS,'SideTailBlackL',[(-.265,.070,-.055),(-.305,.040,-.085),(-.355,-.430,-.112),(-.318,-.780,-.068),(-.285,-.510,-.038)],.013,BLACK)
add_panel(PELVIS,'SideTailBlackR',[(.265,.070,-.055),(.285,-.510,-.038),(.318,-.780,-.068),(.355,-.430,-.112),(.305,.040,-.085)],.013,BLACK)
# Rear panels start away from the center line; from the front they sit behind/outside the thighs instead of making white vertical stripes.
add_panel(PELVIS,'RearTailWhiteL',[(-.205,.090,-.120),(-.105,.082,-.145),(-.120,-.450,-.178),(-.178,-.790,-.152),(-.275,-.500,-.095)],.016,WHITE)
add_panel(PELVIS,'RearTailWhiteR',[(.105,.082,-.145),(.205,.090,-.120),(.275,-.500,-.095),(.178,-.790,-.152),(.120,-.450,-.178)],.016,WHITE)
add_panel(PELVIS,'RearTailBlackL',[(-.250,.070,-.145),(-.165,.062,-.165),(-.185,-.520,-.195),(-.245,-.875,-.132),(-.315,-.485,-.105)],.012,BLACK)
add_panel(PELVIS,'RearTailBlackR',[(.165,.062,-.165),(.250,.070,-.145),(.315,-.485,-.105),(.245,-.875,-.132),(.185,-.520,-.195)],.012,BLACK)

'''
s=s[:a]+skirt+s[b:]

# Portrait/hair v1.5: reduce helmet/comb impression and make ponytail one coherent volume with layered breakup.
a=s.index('# === HEAD / FACE ===')
b=s.index('# === LIMBS ===',a)
head='''# === HEAD / FACE ===
# The sheet reads as a compact ~7-head stylized adult: keep the skull wide enough but reduce vertical helmet height.
add_sphere(HEAD,'Cranium',(0,.012,-.018),(head_w*.490,.116,head_d*.480),SKIN,40,26)
add_sphere(HEAD,'Jaw',(0,-.058,.030),(head_w*.400,.070,head_d*.400),SKIN,38,22)
add_sphere(HEAD,'Chin',(0,-.108,.058),(head_w*.230,.027,head_d*.235),SKIN,28,16)
add_cylinder(HEAD,'Neck',(0,-.160,-.004),W('neck')*.37,.100,SKIN,24)
face_z=head_d*.500
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.170,.010,face_z),(head_w*.080,.0105,.006),SCLERA,22,12)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.170,.010,face_z+.0065),(head_w*.032,.0085,.004),IRIS,18,10)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.170,.010,face_z+.009),(head_w*.012,.0055,.0025),PUPIL,14,8)
 add_box(HEAD,f'Eyeliner_{side}',(side*head_w*.170,.027,face_z+.0085),(head_w*.096,.005,.0032),HAIR,.0014,rot=(0,0,-side*.085))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.170,.058,face_z+.001),(head_w*.105,.005,.0035),HAIR,.0014,rot=(0,0,-side*.09))
add_sphere(HEAD,'Nose',(0,-.012,face_z+.006),(.009,.021,.008),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.066,face_z+.003),(.040,.005,.0035),LIP,.0012)
# Scalp volumes stay behind the face; temple fills prevent bald-looking gaps without forming a spherical helmet.
add_sphere(HEAD,'HairBack',(0,.026,-head_d*.24),(head_w*.530,.136,head_d*.565),HAIR,38,24)
add_sphere(HEAD,'HairCrown',(0,.080,-.035),(head_w*.510,.070,head_d*.500),HAIR,36,22)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.405,.012,.000),(head_w*.120,.095,head_d*.210),HAIR,26,18)
# Five broad overlapping swept bang sheets replace the picket-fence fringe.
bangs=[
 (-.090,-.045,-.072,.060),(-.052,-.012,-.038,.067),(-.010,.012,.010,.070),(.040,-.006,.043,.064),(.085,-.050,.078,.057)
]
for i,(sx,ey,ex,w0) in enumerate(bangs):
 add_ribbon(HEAD,f'BangSheet_{i}',[(sx,.104,.010),(sx*.80,.082,face_z*.62),(ex*.84,.043,face_z-.003),(ex,ey,face_z+.004)],[w0,w0*.96,w0*.68,w0*.28],.0065,HAIR_HI if i in(1,3) else HAIR)
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.365,.070,.015),(side*head_w*.445,-.010,head_d*.16),(side*head_w*.465,-.180,head_d*.08),(side*head_w*.405,-.420,-.005)],[.050,.046,.034,.014],.0065,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.410,.050,.000),(side*head_w*.485,-.075,head_d*.11),(side*head_w*.500,-.270,.035),(side*head_w*.445,-.500,-.025)],[.028,.026,.020,.010],.005,HAIR_HI)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# Continuous ponytail core: this is the dark hair mass seen in the side/back reference.
add_section_mesh(PONY,'PonyCore',[
 (.100,.050,.030,.038,-head_d*.47),
 (-.030,.078,.040,.052,-head_d*.67),
 (-.300,.118,.052,.068,-.390),
 (-.650,.142,.060,.074,-.325),
 (-1.000,.128,.052,.064,-.235),
 (-1.300,.092,.038,.048,-.155),
 (-1.500,.045,.022,.028,-.080)
],HAIR,32)
# Wide ribbons sit over the core, with fine strands only at the outside edge.
for i in range(7):
 lane=(i-3)/3
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.025,.095,-head_d*.49),(lane*.070,-.055,-head_d*.70),(lane*.135,-.410,-.405),(lane*.205,-.900,-.285),(lane*.270,-1.470,-.090)],[.055,.062,.066,.050,.014],.006,HAIR_HI if i in(1,5) else HAIR)
for i in range(8):
 lane=(i-3.5)/3.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.030,.090,-head_d*.50),(lane*.085,-.090,-head_d*.72),(lane*.160,-.500,-.390),(lane*.245,-1.020,-.245),(lane*.330,-1.535,-.060)],.0038+(i%2)*.0007,HAIR_HI if i%3==0 else HAIR)
add_box(HEAD,'HairTie',(0,.086,-head_d*.49),(.102,.028,.040),SILVER,.008)

'''
s=s[:a]+head+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V15: cohesive ponytail, swept bangs, radial skirt and front bodice layers')
