from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V27' in s:
    print('Blender heroine generator already carries REFERENCE_V27')
    raise SystemExit(0)
if '# REFERENCE_V26' not in s:
    raise SystemExit('REFERENCE_V26 generator required before v2.7')
s=s.replace('# REFERENCE_V26: strand-flow fringe, split pony cascade and couture micro-detail.','# REFERENCE_V26: strand-flow fringe, split pony cascade and couture micro-detail.\n# REFERENCE_V27: asymmetric fringe, clean forehead and layered-volume ponytail.',1)

# Calm the hair highlight and remove the front-crown sphere that reads as a hard horizontal forehead band.
s=s.replace("HAIR=material('Hair',(0.012,0.010,0.014),.03,.30)","HAIR=material('Hair',(0.010,0.009,0.013),.02,.40)",1)
s=s.replace("HAIR_HI=material('Hair Highlight',(0.050,0.036,0.046),.03,.27)","HAIR_HI=material('Hair Highlight',(0.040,0.030,0.040),.02,.34)",1)
s=s.replace("add_sphere(HEAD,'HairTopCap',(0,.078,-head_d*.105),(head_w*.500,.071,head_d*.405),HAIR,42,24)","add_sphere(HEAD,'HairTopCap',(0,.082,-head_d*.145),(head_w*.495,.069,head_d*.350),HAIR,42,24)",1)
s=s.replace("add_sphere(HEAD,'HairFrontCrown',(0,.082,head_d*.105),(head_w*.455,.046,head_d*.235),HAIR,38,22)\n","",1)

# Replace the evenly spaced fringe with five major asymmetric locks plus small wisps.
a=s.index('# Layered curved fringe: roots sit on the crown')
b=s.index('# Longer side fringe frames',a)
fringe="""# Asymmetric five-lock fringe: fewer, broader flows read as hair instead of comb teeth.
bang_z=face_z+.019
fringe_data=[
 (-.118,-.100,-.095,.030,.058),
 (-.072,-.056,-.046,.050,.054),
 (-.020,-.010,-.006,-.010,.047),
 (.036,.046,.040,.040,.052),
 (.092,.102,.100,.052,.057)
]
for i,(rootx,midx,tipx,tipy,w) in enumerate(fringe_data):
 add_ribbon(HEAD,f'FringeMajor_{i}',[(rootx,.136,head_d*.04),(midx,.120,head_d*.30),(tipx,.088,face_z*.76),(tipx*.98,tipy,bang_z)],[w*.66,w,w*.74,w*.18],.0040,HAIR_HI if i in(1,3) else HAIR)
# Fine overlapping wisps break the lower edge and make the parting less geometric.
for i,(sx,tx,ty) in enumerate(((-.096,-.082,.044),(-.050,-.032,.028),(.008,.014,.018),(.060,.074,.048),(.108,.118,.038))):
 add_ribbon(HEAD,f'FringeWisp_{i}',[(sx,.116,head_d*.34),((sx+tx)*.5,.090,face_z*.72),(tx,ty,bang_z+.002)],[.021,.015,.0038],.0028,HAIR_HI if i in(0,4) else HAIR)
# Crown surface flows overlap the cap but stop before forming a forehead rim.
for i,lane in enumerate((-.30,-.15,0,.16,.31)):
 add_ribbon(HEAD,f'CrownFlowV27_{i}',[(lane*head_w,.143,-head_d*.22),(lane*head_w*.96,.134,-head_d*.02),(lane*head_w*.90,.120,head_d*.18),(lane*head_w*.82,.108,face_z*.46)],[.024,.028,.024,.008],.0026,HAIR_HI if i in(1,3) else HAIR)
add_ribbon(HEAD,'TempleWispV27L',[(-.120,.086,bang_z),(-.130,.048,bang_z+.001),(-.136,-.005,bang_z-.003)],[.018,.012,.004],.0027,HAIR)
add_ribbon(HEAD,'TempleWispV27R',[(.120,.086,bang_z),(.130,.048,bang_z+.001),(.136,-.005,bang_z-.003)],[.018,.012,.004],.0027,HAIR)
"""
s=s[:a]+fringe+s[b:]

# Rebuild the cascade with nine visible bundles plus three darker under-layers.
a=s.index('pony_specs=[')
b=s.index('# === LIMBS ===',a)
pony="""pony_specs=[
 (-.090,-.126,-.185,1.50,.050,-.010),
 (-.068,-.098,-.150,1.58,.053,.008),
 (-.046,-.070,-.112,1.66,.056,-.006),
 (-.024,-.038,-.062,1.71,.057,.010),
 (0.000,.006,.012,1.74,.059,-.008),
 (.024,.038,.062,1.70,.057,.009),
 (.046,.070,.112,1.65,.056,-.007),
 (.068,.098,.150,1.57,.053,.008),
 (.090,.126,.185,1.49,.050,-.010)
]
for i,(rx,mx,ex,endy,w,zoff) in enumerate(pony_specs):
 sway=(-1 if i%2==0 else 1)*.016
 add_ribbon(PONY,f'PonyBundleV27_{i}',[(rx,.146,-head_d*.50+zoff),(rx*.92,.020,-head_d*.78+zoff),(mx+sway,-.300,-.474+zoff),(mx-sway,-.665,-.350+zoff),(ex+sway,-1.035,-.240+zoff),(ex,-1.365,-.123+zoff),(ex*.94,-endy,-.038+zoff)],[w*.68,w,w*1.06,w*.98,w*.76,w*.44,.008],.0045,HAIR_HI if i in(2,6) else HAIR)
# Three recessed under-layers restore healthy hair mass while preserving clear gaps between the front bundles.
for i,(lane,w) in enumerate(((-.060,.050),(0,.055),(.060,.050))):
 add_ribbon(PONY,f'PonyUnderV27_{i}',[(lane,.130,-head_d*.56),(lane*1.10,-.030,-head_d*.82),(lane*1.35,-.390,-.505),(lane*1.55,-.790,-.365),(lane*1.70,-1.180,-.215),(lane*1.78,-1.520,-.075)],[w*.72,w,w*.94,w*.82,w*.56,.010],.0040,HAIR)
# Root feathers blend the tie into both depth layers.
for i,lane in enumerate((-.070,-.035,0,.035,.070)):
 add_ribbon(PONY,f'PonyRootV27_{i}',[(lane,.151,-head_d*.49),(lane*1.12,.078,-head_d*.66),(lane*1.25,-.055,-head_d*.78)],[.030,.038,.014],.0034,HAIR_HI if i in(1,3) else HAIR)
# Fine irregular edge strands avoid a cut-paper silhouette.
for i in range(16):
 lane=(i-7.5)/7.5
 side=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV27_{i}',[(lane*.056,.138,-head_d*.53),(lane*.095+side*.009,-.085,-head_d*.80),(lane*.148-side*.014,-.455,-.455),(lane*.214+side*.015,-.875,-.292),(lane*.278-side*.010,-1.285,-.148),(lane*.318,-1.600-(i%4)*.028,-.030)],.0018+(i%3)*.00032,HAIR_HI if i%5==0 else HAIR)

"""
s=s[:a]+pony+s[b:]

# Small garter hardware adds the missing reference-sheet costume rhythm on the long leg silhouette.
old="""for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_cylinder(group,'Garter'+name,(0,-.245,0),th*1.06,.048,BLACK,24);add_cylinder(group,'ThighBootTop'+name,(0,.105,0),th*.96,.70,BLACK,28)
"""
new="""for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_cylinder(group,'Garter'+name,(0,-.245,0),th*1.06,.048,BLACK,24)
 add_box(group,'GarterBuckle'+name,(th*.72,-.245,th_d*.74),(.024,.038,.018),SILVER,.004)
 add_box(group,'GarterTab'+name,(th*.70,-.185,th_d*.70),(.014,.090,.014),BLACK_SOFT,.003)
 add_cylinder(group,'ThighBootTop'+name,(0,.105,0),th*.96,.70,BLACK,28)
"""
if old not in s: raise SystemExit('garter block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V27: asymmetric fringe, clean forehead and layered-volume ponytail')
