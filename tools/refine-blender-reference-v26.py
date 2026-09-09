from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V26' in s:
    print('Blender heroine generator already carries REFERENCE_V26')
    raise SystemExit(0)
if '# REFERENCE_V25' not in s:
    raise SystemExit('REFERENCE_V25 generator required before v2.6')
s=s.replace('# REFERENCE_V25: larger portrait eyes and strand-separated ponytail mass.','# REFERENCE_V25: larger portrait eyes and strand-separated ponytail mass.\n# REFERENCE_V26: strand-flow fringe, split pony cascade and couture micro-detail.',1)

# Darker, less brown hair with a tighter specular response.
s=s.replace("HAIR=material('Hair',(0.027,0.020,0.022),.02,.40)","HAIR=material('Hair',(0.012,0.010,0.014),.03,.30)",1)
s=s.replace("HAIR_HI=material('Hair Highlight',(0.075,0.048,0.050),.02,.35)","HAIR_HI=material('Hair Highlight',(0.050,0.036,0.046),.03,.27)",1)

# Replace flat forehead plates with overlapping curved ribbons flowing from the crown.
a=s.index('# Broad fringe now terminates above the eye line;')
b=s.index('# Longer side fringe frames',a)
fringe="""# Layered curved fringe: roots sit on the crown and sweep forward, avoiding flat plate/teeth silhouettes.
bang_z=face_z+.019
fringe_data=[
 (-.120,-.111,-.104,.050,.050),
 (-.086,-.078,-.068,.047,.046),
 (-.054,-.044,-.034,.044,.043),
 (-.022,-.012,-.006,.006,.039),
 (.022,.012,.006,.018,.039),
 (.054,.044,.034,.044,.043),
 (.086,.078,.068,.047,.046),
 (.120,.111,.104,.050,.050)
]
for i,(rootx,midx,tipx,tipy,w) in enumerate(fringe_data):
 add_ribbon(HEAD,f'FringeFlow_{i}',[(rootx,.132,head_d*.10),(midx,.116,head_d*.34),(tipx,.086,face_z*.78),(tipx*.98,tipy,bang_z)],[w*.72,w,w*.76,w*.20],.0042,HAIR_HI if i in(1,6) else HAIR)
# Fine surface locks break up the crown cap without exposing scalp.
for i,lane in enumerate((-.34,-.17,0,.17,.34)):
 add_ribbon(HEAD,f'CrownVeil_{i}',[(lane*head_w,.140,-head_d*.20),(lane*head_w*.96,.132,head_d*.02),(lane*head_w*.90,.118,head_d*.24),(lane*head_w*.78,.102,face_z*.50)],[.026,.030,.026,.010],.0028,HAIR_HI if i in(1,3) else HAIR)
# Two light temple wisps soften the hard hairline corners.
add_ribbon(HEAD,'TempleWispL',[(-.118,.086,bang_z),(-.126,.055,bang_z+.002),(-.132,.016,bang_z-.002)],[.018,.012,.004],.0028,HAIR)
add_ribbon(HEAD,'TempleWispR',[(.118,.086,bang_z),(.126,.055,bang_z+.002),(.132,.016,bang_z-.002)],[.018,.012,.004],.0028,HAIR)
"""
s=s[:a]+fringe+s[b:]

# Add reference-like harness and waist hardware so gaps between hair strands reveal designed detail, not a plain black torso.
anchor='# === HEAD / FACE ==='
if anchor not in s: raise SystemExit('head anchor not found')
couture="""# === REFERENCE COUTURE MICRO DETAIL v2.6 ===
add_box(TORSO,'BackSpineRail',(0,.040,-bust_d*.505),(.018,.390,.014),SILVER,.004)
add_panel(TORSO,'BackHarnessKite',[(-.072,.235,-bust_d*.50),(.072,.235,-bust_d*.50),(.110,.060,-bust_d*.54),(0,-.095,-bust_d*.57),(-.110,.060,-bust_d*.54)],.012,BLACK_SOFT)
for side in(-1,1):
 add_box(TORSO,f'BackHarnessUpper_{side}',(side*.076,.185,-bust_d*.535),(.016,.250,.012),SILVER,.004,rot=(0,0,-side*.36))
 add_box(TORSO,f'BackHarnessLower_{side}',(side*.060,-.070,-bust_d*.555),(.015,.210,.011),SILVER,.004,rot=(0,0,side*.28))
 add_box(PELVIS,f'HipBuckle_{side}',(side*.206,.068,.108),(.042,.046,.026),SILVER,.006)
 add_box(PELVIS,f'HipStrap_{side}',(side*.205,-.015,.090),(.028,.190,.018),BLACK_SOFT,.005,rot=(0,0,-side*.10))
add_panel(PELVIS,'WaistChevronL',[(-.155,.142,.145),(-.018,.150,.165),(-.042,.070,.176),(-.168,.088,.148)],.010,WHITE)
add_panel(PELVIS,'WaistChevronR',[(.018,.150,.165),(.155,.142,.145),(.168,.088,.148),(.042,.070,.176)],.010,WHITE)
add_box(PELVIS,'WaistCenterGem',(0,.102,.184),(.026,.050,.018),SILVER,.005)

"""
s=s.replace(anchor,couture+anchor,1)

# Eliminate the opaque cape-like pony core. Seven ribbon bundles and fine flyaway strands form separated hair masses with visible gaps.
a=s.index("add_section_mesh(PONY,'PonyCore'")
b=s.index('# === LIMBS ===',a)
pony="""pony_specs=[
 (-.074,-.110,-.168,1.55,.046),
 (-.052,-.078,-.120,1.64,.048),
 (-.030,-.046,-.072,1.70,.047),
 (0.000,.006,.012,1.73,.050),
 (.030,.046,.072,1.69,.047),
 (.052,.078,.120,1.62,.048),
 (.074,.110,.168,1.53,.046)
]
for i,(rx,mx,ex,endy,w) in enumerate(pony_specs):
 sway=(-1 if i%2==0 else 1)*.020
 add_ribbon(PONY,f'PonyBundle_{i}',[(rx,.145,-head_d*.50),(rx*.92,.012,-head_d*.78),(mx+sway,-.315,-.470),(mx-sway,-.690,-.345),(ex+sway,-1.070,-.235),(ex,-1.390,-.120),(ex*.94,-endy,-.038)],[w*.64,w,w*1.02,w*.94,w*.72,w*.40,.007],.0044,HAIR_HI if i in(1,5) else HAIR)
# Root feathers bridge the tie into the separated cascade.
for i,lane in enumerate((-.060,-.030,0,.030,.060)):
 add_ribbon(PONY,f'PonyRootFeather_{i}',[(lane,.150,-head_d*.49),(lane*1.15,.070,-head_d*.67),(lane*1.28,-.060,-head_d*.76)],[.030,.036,.014],.0036,HAIR_HI if i in(1,3) else HAIR)
# Long flyaways give the silhouette the fine layered tails visible in the reference sheet.
for i in range(18):
 lane=(i-8.5)/8.5
 side=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFly_{i}',[(lane*.052,.138,-head_d*.52),(lane*.090+side*.010,-.080,-head_d*.78),(lane*.140-side*.016,-.470,-.445),(lane*.205+side*.018,-.900,-.285),(lane*.270-side*.012,-1.300,-.145),(lane*.310,-1.620-(i%3)*.035,-.030)],.0019+(i%3)*.00035,HAIR_HI if i%5==0 else HAIR)

"""
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V26: strand-flow fringe, split pony cascade and couture micro-detail')
