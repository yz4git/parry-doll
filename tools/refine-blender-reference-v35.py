from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V35' in s:
    print('Blender heroine generator already carries REFERENCE_V35')
    raise SystemExit(0)
if '# REFERENCE_V34' not in s:
    raise SystemExit('REFERENCE_V34 generator required before v3.5')
s=s.replace('# REFERENCE_V34: almond eye surfaces, explicit facial cues and thin swept fringe blades.','# REFERENCE_V34: almond eye surfaces, explicit facial cues and thin swept fringe blades.\n# REFERENCE_V35: asymmetric key-art fringe, stronger portrait cues and brighter couture balance.',1)

# Reference portrait uses a warm dark iris rather than a cool mechanical teal.
s=s.replace("IRIS=material('Iris',(0.18,0.24,0.25),.04,.24)","IRIS=material('Iris',(0.12,0.085,0.070),.02,.34)",1)

# Portrait readability: retain almond surfaces, but make the opening slightly
# taller and the lash/brow/mouth cues strong enough to survive the game camera.
a=s.index('# Anatomy v3.4:')
b=s.index('# Hair v3.4:',a)
face=s[a:b]
face=face.replace('eye_y=.024','eye_y=.026')
face=face.replace('eye_ry=.0126','eye_ry=.0142')
face=face.replace("(head_w*.032,.0090,.0026)","(head_w*.035,.0100,.0026)")
face=face.replace("(head_w*.012,.0048,.0018)","(head_w*.013,.0053,.0018)")
face=face.replace(".00120,HAIR)",".00155,HAIR)")
face=face.replace(".00135,HAIR)",".00165,HAIR)")
face=face.replace(".00090,FACE_DARK)",".00105,FACE_DARK)")
face=face.replace(".00128,LIP)",".00145,LIP)")
face=face.replace(".00078,FACE_DARK)",".00092,FACE_DARK)")
face=face.replace(".00100,LIP)",".00112,LIP)")
# Add short outer lash wings after each upper lash arc.
needle=" add_strand(HEAD,f'UpperLashV34_{side}',[(inner,eye_y+.003,face_front+.006),(ex,eye_y+.016,face_front+.007),(outer,eye_y+.003,face_front+.006)],.00155,HAIR)\n"
wing=needle+" add_strand(HEAD,f'LashWingV35_{side}',[(outer,eye_y+.004,face_front+.006),(outer+side*head_w*.020,eye_y+.009,face_front+.0065)],.00125,HAIR)\n"
if needle not in face: raise SystemExit('v35 lash anchor missing')
face=face.replace(needle,wing,1)
s=s[:a]+face+s[b:]

# Replace the symmetrical six-fang fringe with a five-lock asymmetric side part.
a=s.index('# Hair v3.4:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.5: asymmetric side-part fringe inspired by the supplied front reference.
add_sphere(HEAD,'HairBackV35',(0,.028,-head_d*.365),(head_w*.520,.132,head_d*.455),HAIR,46,32)
add_sphere(HEAD,'HairCrownV35',(-.012,.113,-head_d*.210),(head_w*.472,.057,head_d*.318),HAIR,44,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV35_{side}',(side*head_w*.416,.018,-.030),(head_w*.090,.078,head_d*.140),HAIR,30,20)

# Heavy left sweep + lighter right pieces. Tips remain broad enough to read as hair, not teeth.
fringe=[
 (-.112,-.090,-.060,.020,.148,.050,.0110),
 (-.072,-.055,-.028,.006,.155,.043,.0090),
 (-.030,-.015,.004,-.012,.160,.034,.0070),
 (.020,.040,.061,.032,.151,.038,.0090),
 (.066,.086,.102,.041,.145,.042,.0100),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(fringe):
 add_ribbon(HEAD,f'FringeSweepV35_{i}',[(rx,ry,-head_d*.004),(mx,ry-.018,head_d*.150),(tx,.094,head_d*.390),(tx,ty,head_d*.515)],[w*.48,w,w*.66,tipw],.0042,HAIR_HI if i in(0,3) else HAIR)
# Diagonal crossover locks create the characteristic layered bangs around the part.
cross=[(-.094,-.058,.050),(-.060,-.026,.034),(-.022,.010,.024),(.026,.052,.039),(.064,.094,.031)]
for i,(rx,tx,ty) in enumerate(cross):
 add_ribbon(HEAD,f'FringeLayerV35_{i}',[(rx,.139,head_d*.022),((rx+tx)*.5,.114,head_d*.292),(tx,ty,head_d*.518)],[.016,.019,.0055],.0030,HAIR_HI if i in(0,4) else HAIR)
for i,(rx,tx,ty) in enumerate(((-.101,-.085,.024),(-.054,-.039,.016),(.014,.028,.015),(.059,.080,.030),(.098,.115,.021))):
 add_strand(HEAD,f'BangWispV35_{i}',[(rx,.132,head_d*.028),((rx+tx)*.5,.106,head_d*.305),(tx,ty,head_d*.520)],.00105,HAIR_HI if i in(0,4) else HAIR)

# Long face-framing pieces echo the reference's loose cheek strands.
for side in(-1,1):
 for j,(off,end_y) in enumerate(((0.00,-.36),(.024,-.48))):
  add_ribbon(HEAD,f'FaceBladeV35_{side}_{j}',[(side*(head_w*.350+off),.076,-.008),(side*(head_w*.420+off),-.014,head_d*.085),(side*(head_w*.438+off),-.170,head_d*.020),(side*(head_w*.385+off),end_y,-.026)],[.030-j*.006,.034-j*.006,.022-j*.005,.0042],.0038 if j==0 else .0030,HAIR_HI if j else HAIR)

# Preserve the separated high ponytail silhouette from v3.4.
add_sphere(HEAD,'PonyRootV35',(0,.152,-head_d*.420),(.082,.064,.067),HAIR,34,24)
add_box(HEAD,'HairTieV35',(0,.147,-head_d*.480),(.092,.023,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(17):
 lane=(i-8)/8
 sway=(-1 if i%2==0 else 1)*(.011+.005*abs(lane))
 zoff=((i%3)-1)*.012-.010*abs(lane)
 endx=lane*.250+sway
 pts=[(lane*.052,.150,-head_d*.510+zoff),(lane*.077,.032,-head_d*.748+zoff),(lane*.112+sway,-.245,-.490+zoff*.40),(lane*.158-sway,-.610,-.355),(lane*.210+sway,-1.000,-.228),(endx,-1.390,-.112),(endx*.96,-1.680-(i%4)*.018,-.028)]
 base_w=.054-.011*abs(lane)
 add_lock_mesh(PONY,f'PonyBladeV35_{i}',pts,[base_w*.60,base_w,base_w*1.04,base_w*.94,base_w*.72,base_w*.36,.0055],[.014,.016,.017,.015,.012,.008,.003],HAIR_HI if i in(4,8,12) else HAIR,6)
for i in range(10):
 lane=(i-4.5)/4.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV35_{i}',[(lane*.046,.147,-head_d*.515),(lane*.080+sgn*.009,-.055,-head_d*.780),(lane*.140-sgn*.014,-.435,-.442),(lane*.210+sgn*.016,-.915,-.266),(lane*.278-sgn*.012,-1.320,-.125),(lane*.307,-1.675-(i%4)*.028,-.022)],.00125+(i%3)*.00017,HAIR_HI if i%4==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

# Couture balance: the current front reads too black compared with the reference.
# Add thin white bodice overlays without changing shoulder width or core anatomy.
anchor="# Compact pelvis and high waist: measured 0.123H width and 0.089H depth.\n"
couture="""# v3.5 brighter front couture: white side bodice layers over the existing black anatomical core.
add_panel(TORSO,'BodiceWhiteV35_L',[(-bust_w*.455,.218,bust_d*.515),(-bust_w*.255,.190,bust_d*.585),(-waist_w*.245,-.190,waist_d*.675),(-waist_w*.520,-.225,waist_d*.585)],.010,WHITE)
add_panel(TORSO,'BodiceWhiteV35_R',[(bust_w*.255,.190,bust_d*.585),(bust_w*.455,.218,bust_d*.515),(waist_w*.520,-.225,waist_d*.585),(waist_w*.245,-.190,waist_d*.675)],.010,WHITE)
for side in(-1,1):
 add_box(TORSO,f'BodiceEdgeV35_{side}',(side*bust_w*.275,.030,bust_d*.600),(.012,.330,.009),SILVER,.0035,rot=(0,0,side*.08))
 add_box(TORSO,f'UpperArmBandV35_{side}',(side*.205,.215,.000),(.040,.020,.072),BLACK,.004)

"""
if anchor not in s: raise SystemExit('v35 couture anchor missing')
s=s.replace(anchor,couture+anchor,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V35: asymmetric key-art fringe, stronger portrait and brighter couture')
