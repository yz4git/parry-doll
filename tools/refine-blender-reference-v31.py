from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V31' in s:
    print('Blender heroine generator already carries REFERENCE_V31')
    raise SystemExit(0)
if '# REFERENCE_V30' not in s:
    raise SystemExit('REFERENCE_V30 generator required before v3.1')
s=s.replace('# REFERENCE_V30: continuous facial surface and tangent-oriented hair ribbons.','# REFERENCE_V30: continuous facial surface and tangent-oriented hair ribbons.\n# REFERENCE_V31: sculpted single-shell face and curve-based hair masses.',1)

# One connected head mesh. Facial anatomy is displaced directly on the front
# hemisphere so there is no separate mask/patch floating above the skull.
anchor='def add_ribbon(p,name,pts,widths,thickness,mat):\n'
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
    fm=sn**1.75
    # Broad cheekbone support.
    for side in(-1,1):
     cheek_x=side*head_w*.205
     z+=fm*.0080*math.exp(-((x-cheek_x)/(head_w*.120))**2-((yy+.008)/.050)**2)
     # Eye sockets recede into the skull instead of sitting on a flat face plate.
     eye_x=side*head_w*.160
     z-=fm*.0088*math.exp(-((x-eye_x)/(head_w*.105))**2-((yy-.024)/.029)**2)
     # Brow/temple transition catches light above each socket.
     z+=fm*.0038*math.exp(-((x-eye_x)/(head_w*.125))**2-((yy-.070)/.028)**2)
    # Continuous nose bridge and tip.
    z+=fm*.0065*math.exp(-(x/(head_w*.060))**2-((yy-.025)/.075)**2)
    z+=fm*.0165*math.exp(-(x/(head_w*.075))**2-((yy+.041)/.024)**2)
    # Philtrum, mouth cushion and chin are subtle surface changes, not decals.
    z-=fm*.0018*math.exp(-(x/(head_w*.055))**2-((yy+.064)/.018)**2)
    z+=fm*.0032*math.exp(-(x/(head_w*.180))**2-((yy+.083)/.028)**2)
    z+=fm*.0030*math.exp(-(x/(head_w*.145))**2-((yy+.116)/.023)**2)
   verts.append(bpos((x,yy,z)))
 faces=[]
 for r in range(len(sections)-1):
  base=r*segments;nxt=(r+1)*segments
  for i in range(segments):
   j=(i+1)%segments
   faces.append((base+i,base+j,nxt+j,nxt+i))
 faces.append(tuple(range(segments-1,-1,-1)))
 last=(len(sections)-1)*segments
 faces.append(tuple(last+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

"""
if anchor not in s: raise SystemExit('add_ribbon anchor missing')
s=s.replace(anchor,helper+anchor,1)

# Replace the old section-only head with the anatomical single shell.
a=s.index("add_section_mesh(HEAD,'HeadShell',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_anatomical_head(HEAD,'HeadShellV31',[
 (-.136,head_w*.105,head_d*.160,head_d*.215,.050),
 (-.124,head_w*.215,head_d*.225,head_d*.285,.044),
 (-.108,head_w*.300,head_d*.285,head_d*.345,.036),
 (-.090,head_w*.350,head_d*.325,head_d*.385,.030),
 (-.068,head_w*.405,head_d*.355,head_d*.420,.023),
 (-.044,head_w*.452,head_d*.390,head_d*.455,.014),
 (-.018,head_w*.485,head_d*.420,head_d*.485,.006),
 (.010,head_w*.502,head_d*.442,head_d*.500,-.001),
 (.036,head_w*.500,head_d*.460,head_d*.492,-.006),
 (.062,head_w*.485,head_d*.476,head_d*.470,-.011),
 (.086,head_w*.458,head_d*.480,head_d*.440,-.016),
 (.108,head_w*.420,head_d*.472,head_d*.402,-.021),
 (.128,head_w*.368,head_d*.455,head_d*.355,-.026),
 (.145,head_w*.300,head_d*.425,head_d*.295,-.030)
],SKIN,64)
"""
s=s[:a]+head+s[b:]

# Remove the v3.0 FaceSurface completely. Eyeballs are embedded into the single
# shell; eyelids, lashes, brows and lips use smooth Blender curves.
a=s.index('# Continuous facial surface: broad planes first, features second.')
b=s.index('# Hair v3.0:',a)
face="""# Anatomy v3.1: the HeadShellV31 itself carries cheek, socket, nose, muzzle and chin form.
face_z=head_d*.492
eye_y=.022
eye_x=head_w*.160
eye_z=head_d*.432
eye_rx=head_w*.098
eye_ry=.0255
eye_rz=head_d*.075
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballV31_{side}',(ex,eye_y,eye_z),(eye_rx,eye_ry,eye_rz),SCLERA,36,24)
 front=eye_z+eye_rz*.985
 add_sphere(HEAD,f'IrisV31_{side}',(ex,eye_y-.001,front+.0025),(head_w*.052,.0118,.0042),IRIS,28,18)
 add_sphere(HEAD,f'PupilV31_{side}',(ex,eye_y-.001,front+.0055),(head_w*.019,.0066,.0026),PUPIL,20,12)
 add_sphere(HEAD,f'EyeLightV31_{side}',(ex-side*head_w*.013,eye_y+.007,front+.0082),(head_w*.010,.0038,.0015),SCLERA,12,8)
 inner=ex-side*eye_rx*.84;outer=ex+side*eye_rx*.92
 # Skin-coloured lid ridges follow the eyeball arc and stay very thin.
 add_strand(HEAD,f'UpperLidV31_{side}',[(inner,.024,front-.001),(ex,.038,front+.0015),(outer,.025,front-.001)],.0021,SKIN)
 add_strand(HEAD,f'LowerLidV31_{side}',[(inner,.010,front-.001),(ex,.001,front+.0005),(outer,.011,front-.001)],.00145,SKIN)
 add_strand(HEAD,f'UpperLashV31_{side}',[(inner,.028,front+.005),(ex,.041,front+.0065),(outer,.028,front+.005)],.00155,HAIR)
 add_strand(HEAD,f'BrowV31_{side}',[(ex-side*eye_rx*.78,.072,face_z+.002),(ex,.082,face_z+.004),(ex+side*eye_rx*.96,.070,face_z+.002)],.0017,HAIR)
# Small alar cues only; the bridge and nose tip are part of the head mesh.
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV31_{side}',(side*.0115,-.047,head_d*.505),(.0063,.0062,.0042),SKIN,16,10)
# Curved lips sit almost flush with the muzzle.
add_strand(HEAD,'UpperLipV31',[(-.027,-.078,head_d*.505),(-.013,-.073,head_d*.508),(0,-.077,head_d*.510),(.013,-.073,head_d*.508),(.027,-.078,head_d*.505)],.00165,LIP)
add_strand(HEAD,'LowerLipV31',[(-.023,-.084,head_d*.504),(0,-.090,head_d*.508),(.023,-.084,head_d*.504)],.00155,LIP)

"""
s=s[:a]+face+s[b:]

# Replace every broad v3.0 hair ribbon with curve bundles. This follows the
# production layering order: scalp/crown mass -> major locks -> secondary hairs.
a=s.index('# Hair v3.0:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.1: solid scalp mass plus rounded curve locks; no face-sized cards or ribbon triangles.
add_sphere(HEAD,'HairBackV31',(0,.025,-head_d*.365),(head_w*.520,.132,head_d*.455),HAIR,46,32)
add_sphere(HEAD,'HairCrownV31',(0,.105,-head_d*.205),(head_w*.480,.066,head_d*.335),HAIR,44,28)
add_sphere(HEAD,'HairFrontCapV31',(0,.104,head_d*.020),(head_w*.445,.044,head_d*.205),HAIR,40,24)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV31_{side}',(side*head_w*.420,.012,-.025),(head_w*.095,.086,head_d*.150),HAIR,30,20)

# Major bangs are bundles of 3 rounded curves, giving volume without a flat plate.
bang_specs=[
 (-.112,-.098,-.086,.030,.137),
 (-.078,-.064,-.052,.043,.130),
 (-.047,-.036,-.026,.032,.141),
 (-.015,-.006,.000,-.004,.147),
 (.028,.038,.032,.028,.134),
 (.062,.074,.068,.042,.143),
 (.098,.110,.104,.028,.136),
]
for i,(rx,mx,tx,ty,ry) in enumerate(bang_specs):
 for j,off in enumerate((-.0055,0,.0055)):
  mat=HAIR_HI if (j==0 and i in(1,5)) else HAIR
  add_strand(HEAD,f'BangV31_{i}_{j}',[(rx+off,ry,-head_d*.015),(mx+off*.7,ry-.020,head_d*.155),(tx+off*.35,.090,head_d*.405),(tx+off*.15,ty,head_d*.505)],.00315 if j==1 else .00255,mat)
# Fine crossover hairs make the hairline irregular rather than ruler-straight.
for i,(rx,tx,ty) in enumerate(((-.105,-.083,.020),(-.066,-.045,.013),(-.028,-.010,.005),(.018,.030,.014),(.058,.078,.030),(.100,.115,.017))):
 add_strand(HEAD,f'BangFineV31_{i}',[(rx,.127,head_d*.020),((rx+tx)*.5,.105,head_d*.260),(tx,ty,head_d*.510)],.00165,HAIR_HI if i in(0,5) else HAIR)
# Long side framing locks use multiple parallel curves to create a tapered lock mass.
for side in(-1,1):
 for k in range(5):
  off=(k-2)*.0048
  add_strand(HEAD,f'FaceFrameV31_{side}_{k}',[(side*(head_w*.355+off),.073,-.008),(side*(head_w*.425+off),-.010,head_d*.085),(side*(head_w*.445+off),-.165,head_d*.025),(side*(head_w*.392+off),-.405,-.025)],.00245-(abs(k-2)*.00022),HAIR_HI if k==1 else HAIR)

# High ponytail root and tie.
add_sphere(HEAD,'PonyRootV31',(0,.151,-head_d*.420),(.078,.061,.064),HAIR,34,24)
add_box(HEAD,'HairTieV31',(0,.146,-head_d*.478),(.090,.023,.033),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# Dense central cascade: 27 curved locks with varying root depth and end sway.
for i in range(27):
 lane=(i-13)/13
 ring=(i%3)-1
 sway=(-1 if i%2==0 else 1)*(.010+.007*abs(lane))
 zoff=ring*.012-.014*abs(lane)
 endx=lane*.235+sway
 radius=.0036-.0009*abs(lane)+(.00035 if i%5==0 else 0)
 pts=[
  (lane*.052,.148,-head_d*.505+zoff),
  (lane*.072,.035,-head_d*.745+zoff),
  (lane*.105+sway,-.245,-.485+zoff*.5),
  (lane*.150-sway,-.605,-.355),
  (lane*.195+sway,-.995,-.230),
  (endx,-1.385,-.115),
  (endx*.96,-1.675-(i%4)*.018,-.030),
 ]
 add_strand(PONY,f'PonyLockV31_{i}',pts,max(radius,.0019),HAIR_HI if i in(4,13,22) else HAIR)
# Secondary flyaways keep the outer contour light and reference-like.
for i in range(18):
 lane=(i-8.5)/8.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV31_{i}',[(lane*.044,.145,-head_d*.515),(lane*.078+sgn*.008,-.055,-head_d*.780),(lane*.132-sgn*.014,-.435,-.440),(lane*.205+sgn*.016,-.915,-.265),(lane*.274-sgn*.012,-1.320,-.125),(lane*.305,-1.675-(i%4)*.026,-.022)],.00155+(i%3)*.00025,HAIR_HI if i%6==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V31: single-shell facial anatomy and curve-based layered hair')
