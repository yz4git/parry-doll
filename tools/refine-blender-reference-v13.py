from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

old_skirt="""# Layered split panels preserve the long-leg read while matching the reference skirt envelope.
add_panel(PELVIS,'FrontPanelL',[(-.145,.115,.115),(-.020,.105,.120),(-.045,-.66,.135),(-.225,-.49,.075)],.024,WHITE)
add_panel(PELVIS,'FrontPanelR',[(.020,.105,.120),(.145,.115,.115),(.225,-.49,.075),(.045,-.66,.135)],.024,WHITE)
add_panel(PELVIS,'SidePanelL',[(-.145,.105,.035),(-.225,.065,.010),(-.330,-.53,-.015),(-.245,-.70,.025)],.020,BLACK)
add_panel(PELVIS,'SidePanelR',[(.145,.105,.035),(.225,.065,.010),(.245,-.70,.025),(.330,-.53,-.015)],.020,BLACK)
add_panel(PELVIS,'RearPanelL',[(-.155,.095,-.100),(-.020,.090,-.115),(-.055,-.71,-.145),(-.245,-.54,-.075)],.020,WHITE)
add_panel(PELVIS,'RearPanelR',[(.020,.090,-.115),(.155,.095,-.100),(.245,-.54,-.075),(.055,-.71,-.145)],.020,WHITE)
"""
new_skirt="""# Layered pointed skirt measured from the reference silhouette. Avoid long rectangular slabs.
add_panel(PELVIS,'FrontPanelL',[(-.150,.115,.118),(-.026,.105,.126),(-.052,-.42,.142),(-.112,-.60,.132),(-.222,-.40,.082)],.022,WHITE)
add_panel(PELVIS,'FrontPanelR',[(.026,.105,.126),(.150,.115,.118),(.222,-.40,.082),(.112,-.60,.132),(.052,-.42,.142)],.022,WHITE)
add_panel(PELVIS,'FrontBladeL',[(-.180,.090,.095),(-.120,.075,.110),(-.170,-.49,.108),(-.258,-.66,.055),(-.246,-.29,.050)],.018,BLACK)
add_panel(PELVIS,'FrontBladeR',[(.120,.075,.110),(.180,.090,.095),(.246,-.29,.050),(.258,-.66,.055),(.170,-.49,.108)],.018,BLACK)
add_panel(PELVIS,'SidePanelL',[(-.175,.105,.022),(-.232,.070,-.005),(-.315,-.37,-.035),(-.286,-.76,.010),(-.220,-.53,.040)],.018,WHITE)
add_panel(PELVIS,'SidePanelR',[(.175,.105,.022),(.232,.070,-.005),(.220,-.53,.040),(.286,-.76,.010),(.315,-.37,-.035)],.018,WHITE)
add_panel(PELVIS,'SideBladeL',[(-.214,.080,-.035),(-.267,.045,-.060),(-.338,-.44,-.082),(-.285,-.68,-.045)],.015,BLACK)
add_panel(PELVIS,'SideBladeR',[(.214,.080,-.035),(.285,-.68,-.045),(.338,-.44,-.082),(.267,.045,-.060)],.015,BLACK)
add_panel(PELVIS,'RearPanelL',[(-.155,.095,-.105),(-.025,.090,-.120),(-.060,-.50,-.150),(-.138,-.80,-.128),(-.252,-.52,-.080)],.018,WHITE)
add_panel(PELVIS,'RearPanelR',[(.025,.090,-.120),(.155,.095,-.105),(.252,-.52,-.080),(.138,-.80,-.128),(.060,-.50,-.150)],.018,WHITE)
"""
if old_skirt not in s:raise SystemExit('skirt block not found')
s=s.replace(old_skirt,new_skirt)

old_head="""# === HEAD / FACE ===
# 0.128H front width, 0.114H side depth. Jaw is narrower than the cranium to avoid the old mask/ball look.
add_sphere(HEAD,'Cranium',(0,.025,-.018),(head_w*.49,.180,head_d*.46),SKIN,40,28)
add_sphere(HEAD,'Jaw',(0,-.075,.025),(head_w*.405,.120,head_d*.405),SKIN,38,24)
add_cylinder(HEAD,'Neck',(0,-.235,-.006),W('neck')*.38,.125,SKIN,24)
# Eyes/nose/mouth are deliberately forward of the skin surface so they remain readable in the game camera.
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.185,.025,head_d*.438),(head_w*.105,.020,.010),SCLERA,24,14)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.185,.025,head_d*.450),(head_w*.037,.015,.006),IRIS,18,12)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.185,.025,head_d*.456),(head_w*.015,.009,.004),PUPIL,14,10)
 add_box(HEAD,f'Brow_{side}',(side*head_w*.185,.075,head_d*.440),(head_w*.135,.009,.008),HAIR,.003,rot=(0,0,-side*.08))
add_sphere(HEAD,'Nose',(0,-.020,head_d*.454),(.014,.032,.014),SKIN,18,12)
add_box(HEAD,'Mouth',(0,-.090,head_d*.440),(.052,.008,.006),LIP,.002)
# Hair shell stays behind the face; long dense ponytail matches the side/back sheet.
add_sphere(HEAD,'HairBack',(0,.045,-head_d*.17),(head_w*.54,.205,head_d*.53),HAIR,38,26)
add_sphere(HEAD,'HairCrown',(0,.150,-.015),(head_w*.53,.130,head_d*.50),HAIR,38,24)
for i in range(11):
 lane=(i-5)/5
 # Centre fringe stops above the eye line; outer lanes become longer face-framing bangs.
 end_y=-.010-.075*abs(lane);end_x=lane*head_w*.42
 add_strand(HEAD,f'Fringe_{i}',[(lane*head_w*.34,.175,head_d*.18),(lane*head_w*.30,.112,head_d*.38),(lane*head_w*.34,.052,head_d*.46),(end_x,end_y,head_d*.43)],.0075+(i%2)*.0012,HAIR_HI if i%4==0 else HAIR)
"""
new_head="""# === HEAD / FACE ===
# 0.128H front width, 0.114H side depth. Vertical envelope is reduced to the sheet's ~0.15H head region.
add_sphere(HEAD,'Cranium',(0,.018,-.020),(head_w*.485,.145,head_d*.455),SKIN,36,24)
add_sphere(HEAD,'Jaw',(0,-.066,.030),(head_w*.390,.092,head_d*.390),SKIN,34,22)
add_cylinder(HEAD,'Neck',(0,-.190,-.006),W('neck')*.36,.110,SKIN,22)
# Project features beyond the facial surface; v1.2 placed them behind the jaw and they disappeared.
face_z=.154
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.178,.020,face_z),(head_w*.102,.018,.009),SCLERA,20,12)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.178,.020,face_z+.011),(head_w*.036,.014,.005),IRIS,16,10)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.178,.020,face_z+.016),(head_w*.014,.008,.003),PUPIL,12,8)
 add_box(HEAD,f'Eyeliner_{side}',(side*head_w*.178,.040,face_z+.014),(head_w*.116,.008,.004),HAIR,.002,rot=(0,0,-side*.06))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.178,.070,face_z+.005),(head_w*.130,.008,.005),HAIR,.002,rot=(0,0,-side*.08))
add_sphere(HEAD,'Nose',(0,-.015,face_z+.010),(.012,.027,.011),SKIN,16,10)
add_box(HEAD,'Mouth',(0,-.075,face_z+.004),(.050,.007,.004),LIP,.0015)
# Hair shell stays compact around the skull. Bangs leave the eye line visible.
add_sphere(HEAD,'HairBack',(0,.035,-head_d*.18),(head_w*.535,.165,head_d*.515),HAIR,34,22)
add_sphere(HEAD,'HairCrown',(0,.108,-.018),(head_w*.525,.095,head_d*.490),HAIR,34,22)
for i in range(11):
 lane=(i-5)/5
 end_y=.018-.058*abs(lane);end_x=lane*head_w*.42
 add_strand(HEAD,f'Fringe_{i}',[(lane*head_w*.33,.142,head_d*.18),(lane*head_w*.30,.098,head_d*.40),(lane*head_w*.33,.060,face_z-.003),(end_x,end_y,face_z+.002)],.0068+(i%2)*.0010,HAIR_HI if i%4==0 else HAIR)
"""
if old_head not in s:raise SystemExit('head block not found')
s=s.replace(old_head,new_head)

# Ponytail root follows the smaller crown while keeping the reference's long back silhouette.
s=s.replace("[(side*(head_w*.35+i*.010),.120,head_d*.16),(side*(head_w*.47+i*.012),-.04,head_d*.28),(side*(head_w*.50+i*.012),-.33,head_d*.12),(side*(head_w*.43+i*.010),-.55,-.015)]","[(side*(head_w*.35+i*.010),.095,head_d*.16),(side*(head_w*.47+i*.012),-.04,head_d*.28),(side*(head_w*.50+i*.012),-.30,head_d*.12),(side*(head_w*.43+i*.010),-.52,-.015)]")
s=s.replace("[(lane*.020,.145,-head_d*.46),(lane*.065,.015,-head_d*.70),(lane*.115,-.37,-.38),(lane*.19,-.88,-.31),(lane*.28,-1.48,-.12)]","[(lane*.020,.105,-head_d*.46),(lane*.065,-.005,-head_d*.70),(lane*.115,-.36,-.38),(lane*.19,-.88,-.31),(lane*.28,-1.48,-.12)]")
s=s.replace("add_box(HEAD,'HairTie',(0,.135,-head_d*.47),(.105,.036,.042),SILVER,.010)","add_box(HEAD,'HairTie',(0,.100,-head_d*.47),(.100,.032,.040),SILVER,.009)")

p.write_text(s,encoding='utf-8')
print('Applied reference v1.3 face/head/skirt refinement')
