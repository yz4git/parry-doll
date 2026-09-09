from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V34' in s:
    print('Blender heroine generator already carries REFERENCE_V34')
    raise SystemExit(0)
if '# REFERENCE_V33' not in s:
    raise SystemExit('REFERENCE_V33 generator required before v3.4')
s=s.replace('# REFERENCE_V33: portrait-first facial proportions and layered blade-like hair locks.','# REFERENCE_V33: portrait-first facial proportions and layered blade-like hair locks.\n# REFERENCE_V34: almond eye surfaces, explicit facial cues and thin swept fringe blades.',1)

# Add a shallow convex almond surface for the visible sclera. This prevents a
# full eyeball sphere from reading as a large round toy eye in the game camera.
anchor='def add_ribbon(p,name,pts,widths,thickness,mat):\n'
helper="""def add_almond_surface(p,name,cx,cy,cz,rx,ry,bulge,mat,segments=28):
 verts=[bpos((cx,cy,cz+bulge))]
 for i in range(segments):
  a=2*math.pi*i/segments
  ca=math.cos(a);sa=math.sin(a)
  # Pinch toward the inner/outer corners while retaining a soft upper/lower arc.
  yy=cy+ry*sa*(.72+.28*abs(ca))
  x=cx+rx*ca
  verts.append(bpos((x,yy,cz)))
 faces=[]
 for i in range(segments):faces.append((0,1+i,1+((i+1)%segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

"""
if anchor not in s: raise SystemExit('add_ribbon anchor missing')
s=s.replace(anchor,helper+anchor,1)

# A low-contrast face-detail material lets nostril/mouth cues survive bright sky
# lighting without becoming heavy makeup.
if "FACE_DARK=material('Face Detail'" not in s:
 s=s.replace("LIP=material('Lip',(0.42,0.17,0.18),0,.46)","LIP=material('Lip',(0.38,0.13,0.16),0,.52)\nFACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)",1)

# Replace the visible portrait assembly. The skull remains the same connected
# HeadShellV33; only the visible eye opening and secondary facial cues change.
a=s.index('# Anatomy v3.1:')
b=s.index('# Hair v3.3:',a)
face="""# Anatomy v3.4: single-shell skull with controlled almond eye openings.
face_front=head_d*.507
eye_y=.024
eye_x=head_w*.150
eye_rx=head_w*.112
eye_ry=.0126
# Hidden eyeballs preserve the correct socket volume/profile but stay behind the visible opening.
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV34_{side}',(ex,eye_y,head_d*.425),(head_w*.098,.018,head_d*.070),SCLERA,32,20)
 add_almond_surface(HEAD,f'EyeOpeningV34_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0028,SCLERA,30)
 # Iris is intentionally modest and slightly taller than wide in the opening.
 add_sphere(HEAD,f'IrisV34_{side}',(ex,eye_y,face_front+.0050),(head_w*.032,.0090,.0026),IRIS,26,16)
 add_sphere(HEAD,f'PupilV34_{side}',(ex,eye_y,face_front+.0073),(head_w*.012,.0048,.0018),PUPIL,18,10)
 add_sphere(HEAD,f'EyeLightV34_{side}',(ex-side*head_w*.010,eye_y+.0050,face_front+.0090),(head_w*.0065,.0030,.0012),SCLERA,12,8)
 inner=ex-side*eye_rx*.93;outer=ex+side*eye_rx*.96
 # Thin skin/lash arcs define the almond without covering it with geometry cards.
 add_strand(HEAD,f'UpperLidV34_{side}',[(inner,eye_y+.001,face_front+.002),(ex,eye_y+.015,face_front+.005),(outer,eye_y+.001,face_front+.002)],.00145,SKIN)
 add_strand(HEAD,f'LowerLidV34_{side}',[(inner,eye_y-.001,face_front+.002),(ex,eye_y-.010,face_front+.003),(outer,eye_y-.001,face_front+.002)],.00095,SKIN)
 add_strand(HEAD,f'UpperLashV34_{side}',[(inner,eye_y+.003,face_front+.006),(ex,eye_y+.016,face_front+.007),(outer,eye_y+.003,face_front+.006)],.00120,HAIR)
 add_strand(HEAD,f'BrowV34_{side}',[(ex-side*eye_rx*.77,.071,head_d*.505),(ex,.079,head_d*.510),(ex+side*eye_rx*.92,.069,head_d*.505)],.00135,HAIR)
# Nose bridge/tip remain sculpted into HeadShellV33. These tiny underside cues make it readable front-on.
add_strand(HEAD,'NoseUndersideV34',[(-.010,-.049,head_d*.520),(0,-.053,head_d*.523),(.010,-.049,head_d*.520)],.00090,FACE_DARK)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV34_{side}',(side*.0075,-.049,head_d*.522),(.0025,.0018,.0014),FACE_DARK,12,8)
# Compact lips and mouth line stay close to the muzzle; no rectangular decal geometry.
add_strand(HEAD,'UpperLipV34',[(-.025,-.079,head_d*.512),(-.012,-.075,head_d*.515),(0,-.078,head_d*.517),(.012,-.075,head_d*.515),(.025,-.079,head_d*.512)],.00128,LIP)
add_strand(HEAD,'MouthLineV34',[(-.023,-.083,head_d*.514),(0,-.085,head_d*.516),(.023,-.083,head_d*.514)],.00078,FACE_DARK)
add_strand(HEAD,'LowerLipV34',[(-.020,-.086,head_d*.512),(0,-.090,head_d*.514),(.020,-.086,head_d*.512)],.00100,LIP)

"""
s=s[:a]+face+s[b:]

# Replace only the hair section. Broad fringe pieces now use the stable fixed-X
# swept ribbon primitive: thin in depth, overlapping in width, tapering to tips.
a=s.index('# Hair v3.3:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.4: crown mass -> thin swept fringe blades -> separated pony locks.
add_sphere(HEAD,'HairBackV34',(0,.028,-head_d*.365),(head_w*.520,.132,head_d*.455),HAIR,46,32)
add_sphere(HEAD,'HairCrownV34',(0,.112,-head_d*.210),(head_w*.472,.057,head_d*.318),HAIR,44,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV34_{side}',(side*head_w*.416,.018,-.030),(head_w*.090,.078,head_d*.140),HAIR,30,20)

# Six overlapping primary fringe blades with staggered roots and long tapered tips.
fringe=[
 (-.112,-.091,-.081,.027,.145,.050),
 (-.078,-.059,-.047,.018,.151,.048),
 (-.041,-.021,-.010,.005,.157,.046),
 (.004,.020,.030,-.009,.154,.044),
 (.047,.063,.069,.020,.149,.048),
 (.088,.106,.101,.033,.143,.050),
]
for i,(rx,mx,tx,ty,ry,w) in enumerate(fringe):
 add_ribbon(HEAD,f'FringeBladeV34_{i}',[(rx,ry,-head_d*.006),(mx,ry-.020,head_d*.155),(tx,.095,head_d*.390),(tx*.98,ty,head_d*.514)],[w*.50,w,w*.64,.0038],.0040,HAIR_HI if i in(1,4) else HAIR)
# Small crossing blades create the swept, layered key-art hairline.
for i,(rx,tx,ty) in enumerate(((-.101,-.077,.042),(-.067,-.043,.028),(-.031,-.009,.014),(.018,.037,.013),(.057,.082,.030),(.095,.113,.020))):
 add_ribbon(HEAD,f'FringeCrossV34_{i}',[(rx,.137,head_d*.018),((rx+tx)*.5,.113,head_d*.285),(tx,ty,head_d*.516)],[.018,.020,.0028],.0028,HAIR_HI if i in(0,5) else HAIR)
for i,(rx,tx,ty) in enumerate(((-.098,-.084,.023),(-.052,-.038,.015),(.016,.028,.013),(.061,.081,.028),(.098,.114,.018))):
 add_strand(HEAD,f'BangWispV34_{i}',[(rx,.131,head_d*.025),((rx+tx)*.5,.105,head_d*.300),(tx,ty,head_d*.518)],.00110,HAIR_HI if i in(0,4) else HAIR)

# Two thin face-framing blades per side.
for side in(-1,1):
 for j,(off,end_y) in enumerate(((0.00,-.35),(.024,-.47))):
  add_ribbon(HEAD,f'FaceBladeV34_{side}_{j}',[(side*(head_w*.350+off),.076,-.008),(side*(head_w*.420+off),-.014,head_d*.085),(side*(head_w*.438+off),-.170,head_d*.020),(side*(head_w*.385+off),end_y,-.026)],[.030-j*.006,.034-j*.006,.022-j*.005,.0038],.0038 if j==0 else .0030,HAIR_HI if j else HAIR)

# Keep the successful dense separated v3.3 ponytail silhouette.
add_sphere(HEAD,'PonyRootV34',(0,.152,-head_d*.420),(.082,.064,.067),HAIR,34,24)
add_box(HEAD,'HairTieV34',(0,.147,-head_d*.480),(.092,.023,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(17):
 lane=(i-8)/8
 sway=(-1 if i%2==0 else 1)*(.011+.005*abs(lane))
 zoff=((i%3)-1)*.012-.010*abs(lane)
 endx=lane*.250+sway
 pts=[(lane*.052,.150,-head_d*.510+zoff),(lane*.077,.032,-head_d*.748+zoff),(lane*.112+sway,-.245,-.490+zoff*.40),(lane*.158-sway,-.610,-.355),(lane*.210+sway,-1.000,-.228),(endx,-1.390,-.112),(endx*.96,-1.680-(i%4)*.018,-.028)]
 base_w=.054-.011*abs(lane)
 add_lock_mesh(PONY,f'PonyBladeV34_{i}',pts,[base_w*.60,base_w,base_w*1.04,base_w*.94,base_w*.72,base_w*.36,.0055],[.014,.016,.017,.015,.012,.008,.003],HAIR_HI if i in(4,8,12) else HAIR,6)
for i in range(10):
 lane=(i-4.5)/4.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV34_{i}',[(lane*.046,.147,-head_d*.515),(lane*.080+sgn*.009,-.055,-head_d*.780),(lane*.140-sgn*.014,-.435,-.442),(lane*.210+sgn*.016,-.915,-.266),(lane*.278-sgn*.012,-1.320,-.125),(lane*.307,-1.675-(i%4)*.028,-.022)],.00125+(i%3)*.00017,HAIR_HI if i%4==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V34: almond eyes, explicit facial cues and thin swept fringe blades')
