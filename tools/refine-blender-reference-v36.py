from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V36' in s:
    print('Blender heroine generator already carries REFERENCE_V36')
    raise SystemExit(0)
if '# REFERENCE_V35' not in s:
    raise SystemExit('REFERENCE_V35 generator required before v3.6')
s=s.replace('# REFERENCE_V35: asymmetric key-art fringe, stronger portrait cues and brighter couture balance.','# REFERENCE_V35: asymmetric key-art fringe, stronger portrait cues and brighter couture balance.\n# REFERENCE_V36: portrait anatomy rebuild, larger almond eyes and dark layered forehead locks.',1)

# Preserve pale skin while preventing the face from clipping to a flat white mask under the bright viewer sky.
s=s.replace("SKIN=material('Skin',(0.76,0.54,0.49),0,.56)","SKIN=material('Skin',(0.69,0.49,0.45),0,.62)",1)

# Replace the anatomical deformation helper. The skull remains one connected mesh;
# cheekbone, eye socket, brow, nose, muzzle and chin are all low-frequency surface deformations.
a=s.index('def add_anatomical_head(')
b=s.index('def add_lock_mesh(',a)
helper="""def add_anatomical_head(p,name,sections,mat,segments=64):
 verts=[]
 for yy,w,back,front,zoff in sections:
  for i in range(segments):
   ang=2*math.pi*i/segments
   cs=math.cos(ang);sn=math.sin(ang)
   depth=front if sn>=0 else back
   x=cs*w
   z=zoff+sn*depth
   if sn>0:
    fm=sn**1.72
    # Zygomatic support and a clear cheek break below the eye line.
    for side in(-1,1):
     cheek_x=side*head_w*.205
     z+=fm*.0160*math.exp(-((x-cheek_x)/(head_w*.110))**2-((yy+.008)/.050)**2)
     eye_x=side*head_w*.152
     # Deeper, wider socket; this makes the eye opening sit inside the face rather than on top of it.
     z-=fm*.0170*math.exp(-((x-eye_x)/(head_w*.126))**2-((yy-.026)/.026)**2)
     # Brow ridge and upper orbital plane catch light separately from the forehead.
     z+=fm*.0072*math.exp(-((x-eye_x)/(head_w*.132))**2-((yy-.073)/.027)**2)
     # Subtle lower-cheek hollow keeps the face from reading as one smooth egg.
     z-=fm*.0038*math.exp(-((x-side*head_w*.245)/(head_w*.110))**2-((yy+.060)/.045)**2)
    # Nose bridge grows continuously from the brow, with a stronger tip and soft columella.
    z+=fm*.0145*math.exp(-(x/(head_w*.060))**2-((yy-.020)/.086)**2)
    z+=fm*.0315*math.exp(-(x/(head_w*.076))**2-((yy+.041)/.025)**2)
    z+=fm*.0060*math.exp(-(x/(head_w*.052))**2-((yy+.058)/.017)**2)
    # Philtrum, mouth cushion and chin plane.
    z-=fm*.0028*math.exp(-(x/(head_w*.054))**2-((yy+.067)/.017)**2)
    z+=fm*.0070*math.exp(-(x/(head_w*.155))**2-((yy+.083)/.027)**2)
    z+=fm*.0078*math.exp(-(x/(head_w*.118))**2-((yy+.121)/.022)**2)
   verts.append(bpos((x,yy,z)))
 faces=[]
 for r in range(len(sections)-1):
  base=r*segments;nxt=(r+1)*segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((base+i,base+j,nxt+j,nxt+i))
 faces.append(tuple(range(segments-1,-1,-1)))
 last=(len(sections)-1)*segments;faces.append(tuple(last+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

"""
s=s[:a]+helper+s[b:]

# Narrow the lower face and preserve width high on the cheek/temple. This is the biggest
# silhouette correction versus the round v3.5 portrait.
a=s.index("add_anatomical_head(HEAD,'HeadShellV33',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_anatomical_head(HEAD,'HeadShellV36',[
 (-.142,head_w*.060,head_d*.145,head_d*.198,.053),
 (-.132,head_w*.140,head_d*.200,head_d*.260,.047),
 (-.119,head_w*.220,head_d*.258,head_d*.320,.039),
 (-.103,head_w*.292,head_d*.302,head_d*.366,.032),
 (-.084,head_w*.350,head_d*.342,head_d*.410,.024),
 (-.060,head_w*.405,head_d*.380,head_d*.452,.015),
 (-.033,head_w*.450,head_d*.414,head_d*.482,.007),
 (-.004,head_w*.480,head_d*.440,head_d*.500,-.001),
 (.026,head_w*.492,head_d*.460,head_d*.500,-.006),
 (.056,head_w*.482,head_d*.476,head_d*.482,-.011),
 (.084,head_w*.458,head_d*.482,head_d*.452,-.016),
 (.109,head_w*.420,head_d*.474,head_d*.410,-.021),
 (.131,head_w*.365,head_d*.454,head_d*.357,-.026),
 (.149,head_w*.296,head_d*.423,head_d*.296,-.030)
],SKIN,76)
"""
s=s[:a]+head+s[b:]

# Rebuild the visible portrait. Eyes are larger and more expressive, the iris/pupil sit forward,
# the nose gets a tiny integrated tip/wing reinforcement, and lips are shaped around a cupid bow.
a=s.index('# Anatomy v3.4:')
b=s.index('# Hair v3.5:',a)
face="""# Anatomy v3.6: single-shell portrait with deeper sockets, larger almond eyes and explicit nose/mouth cues.
face_front=head_d*.512
eye_y=.029
eye_x=head_w*.147
eye_rx=head_w*.126
eye_ry=.0192
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV36_{side}',(ex,eye_y,head_d*.423),(head_w*.102,.020,head_d*.074),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeOpeningV36_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0034,SCLERA,32)
 add_sphere(HEAD,f'IrisV36_{side}',(ex,eye_y,face_front+.0058),(head_w*.043,.0125,.0029),IRIS,28,18)
 add_sphere(HEAD,f'PupilV36_{side}',(ex,eye_y,face_front+.0084),(head_w*.016,.0062,.0019),PUPIL,20,12)
 add_sphere(HEAD,f'EyeLightV36_{side}',(ex-side*head_w*.011,eye_y+.0060,face_front+.0102),(head_w*.0075,.0032,.0013),SCLERA,12,8)
 inner=ex-side*eye_rx*.92;outer=ex+side*eye_rx*.98
 add_strand(HEAD,f'UpperLidV36_{side}',[(inner,eye_y+.001,face_front+.0025),(ex,eye_y+.019,face_front+.0058),(outer,eye_y+.002,face_front+.0025)],.00135,SKIN)
 add_strand(HEAD,f'LowerLidV36_{side}',[(inner,eye_y-.001,face_front+.0020),(ex,eye_y-.013,face_front+.0030),(outer,eye_y-.001,face_front+.0020)],.00085,SKIN)
 add_strand(HEAD,f'UpperLashV36_{side}',[(inner,eye_y+.004,face_front+.0065),(ex,eye_y+.020,face_front+.0082),(outer,eye_y+.004,face_front+.0065)],.00185,HAIR)
 add_strand(HEAD,f'LashWingV36_{side}',[(outer,eye_y+.004,face_front+.0067),(outer+side*head_w*.027,eye_y+.012,face_front+.0075)],.00145,HAIR)
 # Slightly lower, angled brows frame the eyes like the key art instead of floating high on the forehead.
 add_strand(HEAD,f'BrowV36_{side}',[(ex-side*eye_rx*.76,.073,head_d*.510),(ex,.083,head_d*.516),(ex+side*eye_rx*.94,.069,head_d*.510)],.00175,HAIR)

# The bridge/tip is already in HeadShellV36. Tiny skin volumes only reinforce the profile silhouette.
add_sphere(HEAD,'NoseTipSoftV36',(0,-.041,head_d*.525),(.0105,.0085,.0060),SKIN,20,12)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV36_{side}',(side*.0105,-.049,head_d*.520),(.0060,.0052,.0042),SKIN,16,10)
 add_sphere(HEAD,f'NostrilV36_{side}',(side*.0072,-.050,head_d*.526),(.0024,.0017,.0013),FACE_DARK,12,8)
add_strand(HEAD,'NoseUndersideV36',[(-.010,-.049,head_d*.524),(0,-.054,head_d*.527),(.010,-.049,head_d*.524)],.00092,FACE_DARK)

# Defined but compact lips. Splitting the upper lip creates a readable cupid bow without a decal card.
add_strand(HEAD,'UpperLipLeftV36',[(-.027,-.079,head_d*.519),(-.014,-.074,head_d*.522),(0,-.079,head_d*.523)],.00145,LIP)
add_strand(HEAD,'UpperLipRightV36',[(0,-.079,head_d*.523),(.014,-.074,head_d*.522),(.027,-.079,head_d*.519)],.00145,LIP)
add_strand(HEAD,'MouthLineV36',[(-.026,-.083,head_d*.521),(0,-.086,head_d*.523),(.026,-.083,head_d*.521)],.00095,FACE_DARK)
add_strand(HEAD,'LowerLipV36',[(-.022,-.087,head_d*.519),(0,-.092,head_d*.522),(.022,-.087,head_d*.519)],.00118,LIP)
for side in(-1,1):
 add_sphere(HEAD,f'MouthCornerV36_{side}',(side*.027,-.083,head_d*.521),(.0018,.0015,.0011),FACE_DARK,10,6)

"""
s=s[:a]+face+s[b:]

# Hair: the face view must read as dark hair, not bright blades. Five broad tapered locks cover
# the forehead from an asymmetric side part; secondary locks break the silhouette without clutter.
a=s.index('# Hair v3.5:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.6: dark scalp mass -> five broad forehead locks -> sparse crossing pieces -> separated ponytail.
add_sphere(HEAD,'HairBackV36',(0,.028,-head_d*.365),(head_w*.520,.132,head_d*.455),HAIR,46,32)
add_sphere(HEAD,'HairCrownV36',(-.016,.116,-head_d*.205),(head_w*.475,.060,head_d*.326),HAIR,44,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV36_{side}',(side*head_w*.414,.018,-.030),(head_w*.092,.080,head_d*.142),HAIR,30,20)

# Five primary locks overlap at the root. Use the dark material on all forehead locks so highlights
# come from lighting, not from pale geometry that can read as a white headband.
primary=[
 (-.112,-.090,-.064,.028,.153,.064,.014),
 (-.070,-.052,-.026,.008,.160,.058,.012),
 (-.028,-.010,.012,-.010,.163,.050,.010),
 (.022,.043,.067,.028,.156,.056,.012),
 (.070,.092,.111,.040,.149,.061,.014),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(primary):
 pts=[(rx,ry,-head_d*.010),(mx,ry-.020,head_d*.145),(tx,.098,head_d*.385),(tx,ty,head_d*.519)]
 add_lock_mesh(HEAD,f'ForeheadLockV36_{i}',pts,[w*.68,w,w*.72,tipw],[.010,.012,.010,.004],HAIR,6)
# Narrow diagonal layers add the key-art sweep and soften the transition between the five masses.
secondary=[(-.098,-.070,.047),(-.060,-.032,.030),(-.018,.004,.018),(.032,.057,.035),(.071,.100,.027)]
for i,(rx,tx,ty) in enumerate(secondary):
 pts=[(rx,.142,head_d*.014),((rx+tx)*.5,.118,head_d*.278),(tx,.082,head_d*.430),(tx,ty,head_d*.520)]
 add_lock_mesh(HEAD,f'FringeLayerV36_{i}',pts,[.020,.022,.015,.0048],[.0055,.0060,.0050,.0025],HAIR_HI if i in(0,4) else HAIR,6)
for i,(rx,tx,ty) in enumerate(((-.100,-.086,.024),(-.055,-.040,.016),(.014,.028,.014),(.060,.081,.030),(.100,.116,.021))):
 add_strand(HEAD,f'BangWispV36_{i}',[(rx,.134,head_d*.027),((rx+tx)*.5,.108,head_d*.302),(tx,ty,head_d*.522)],.0010,HAIR_HI if i in(0,4) else HAIR)

# Long face-framing locks stay close to the cheek silhouette and taper below the jaw.
for side in(-1,1):
 for j,(off,end_y) in enumerate(((0.00,-.36),(.024,-.48))):
  pts=[(side*(head_w*.350+off),.076,-.008),(side*(head_w*.420+off),-.014,head_d*.085),(side*(head_w*.438+off),-.170,head_d*.020),(side*(head_w*.385+off),end_y,-.026)]
  add_lock_mesh(HEAD,f'FaceLockV36_{side}_{j}',pts,[.032-j*.006,.036-j*.006,.024-j*.005,.0045],[.007,.008,.006,.0028],HAIR_HI if j else HAIR,6)

# Preserve the successful separated high ponytail silhouette, with slightly denser central locks.
add_sphere(HEAD,'PonyRootV36',(0,.152,-head_d*.420),(.083,.065,.068),HAIR,34,24)
add_box(HEAD,'HairTieV36',(0,.147,-head_d*.480),(.092,.023,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(19):
 lane=(i-9)/9
 sway=(-1 if i%2==0 else 1)*(.010+.005*abs(lane))
 zoff=((i%3)-1)*.011-.010*abs(lane)
 endx=lane*.250+sway
 pts=[(lane*.052,.150,-head_d*.510+zoff),(lane*.078,.032,-head_d*.748+zoff),(lane*.113+sway,-.245,-.490+zoff*.40),(lane*.160-sway,-.610,-.355),(lane*.212+sway,-1.000,-.228),(endx,-1.390,-.112),(endx*.96,-1.680-(i%4)*.018,-.028)]
 base_w=.052-.010*abs(lane)
 add_lock_mesh(PONY,f'PonyLockV36_{i}',pts,[base_w*.62,base_w,base_w*1.04,base_w*.94,base_w*.72,base_w*.36,.0050],[.013,.015,.016,.014,.011,.007,.003],HAIR_HI if i in(5,9,13) else HAIR,6)
for i in range(10):
 lane=(i-4.5)/4.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV36_{i}',[(lane*.046,.147,-head_d*.515),(lane*.080+sgn*.009,-.055,-head_d*.780),(lane*.140-sgn*.014,-.435,-.442),(lane*.210+sgn*.016,-.915,-.266),(lane*.278-sgn*.012,-1.320,-.125),(lane*.307,-1.675-(i%4)*.028,-.022)],.00120+(i%3)*.00017,HAIR_HI if i%4==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V36: portrait anatomy rebuild and dark layered key-art fringe')
