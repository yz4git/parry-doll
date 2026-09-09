from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V32' in s:
    print('Blender heroine generator already carries REFERENCE_V32')
    raise SystemExit(0)
if '# REFERENCE_V31' not in s:
    raise SystemExit('REFERENCE_V31 generator required before v3.2')
s=s.replace('# REFERENCE_V31: sculpted single-shell face and curve-based hair masses.','# REFERENCE_V31: sculpted single-shell face and curve-based hair masses.\n# REFERENCE_V32: stronger facial planes and tapered volumetric hair locks.',1)

# Strengthen the continuous face very slightly. These are still low-frequency
# deformations of the single head shell, never a second face patch.
a=s.index('def add_anatomical_head(')
b=s.index('def add_ribbon(',a)
helper=s[a:b]
helper=helper.replace("z+=fm*.0080*math.exp(-((x-cheek_x)/(head_w*.120))**2-((yy+.008)/.050)**2)","z+=fm*.0105*math.exp(-((x-cheek_x)/(head_w*.118))**2-((yy+.006)/.050)**2)")
helper=helper.replace("z-=fm*.0088*math.exp(-((x-eye_x)/(head_w*.105))**2-((yy-.024)/.029)**2)","z-=fm*.0115*math.exp(-((x-eye_x)/(head_w*.105))**2-((yy-.024)/.030)**2)")
helper=helper.replace("z+=fm*.0038*math.exp(-((x-eye_x)/(head_w*.125))**2-((yy-.070)/.028)**2)","z+=fm*.0050*math.exp(-((x-eye_x)/(head_w*.125))**2-((yy-.070)/.029)**2)")
helper=helper.replace("z+=fm*.0065*math.exp(-(x/(head_w*.060))**2-((yy-.025)/.075)**2)","z+=fm*.0095*math.exp(-(x/(head_w*.062))**2-((yy-.022)/.078)**2)")
helper=helper.replace("z+=fm*.0165*math.exp(-(x/(head_w*.075))**2-((yy+.041)/.024)**2)","z+=fm*.0210*math.exp(-(x/(head_w*.078))**2-((yy+.041)/.025)**2)")
helper=helper.replace("z+=fm*.0032*math.exp(-(x/(head_w*.180))**2-((yy+.083)/.028)**2)","z+=fm*.0044*math.exp(-(x/(head_w*.180))**2-((yy+.082)/.029)**2)")
helper=helper.replace("z+=fm*.0030*math.exp(-(x/(head_w*.145))**2-((yy+.116)/.023)**2)","z+=fm*.0040*math.exp(-(x/(head_w*.145))**2-((yy+.116)/.024)**2)")
# Add a solid swept-lock helper after the anatomical head helper. Each section
# has an elliptical cross-section perpendicular to the local path tangent.
lock_helper="""def add_lock_mesh(p,name,pts,widths,depths,mat,ring_segments=10):
 def sub(a,b):return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
 def dot(a,b):return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
 def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
 def norm(v):
  l=max((v[0]*v[0]+v[1]*v[1]+v[2]*v[2])**.5,1e-8)
  return (v[0]/l,v[1]/l,v[2]/l)
 verts=[];n=len(pts)
 for i,c in enumerate(pts):
  if i==0:t=norm(sub(pts[1],c))
  elif i==n-1:t=norm(sub(c,pts[i-1]))
  else:t=norm(sub(pts[i+1],pts[i-1]))
  # Keep the broad axis close to logical X while remaining perpendicular to the path.
  wx=(1.0,0.0,0.0);proj=dot(wx,t);u=(wx[0]-proj*t[0],wx[1]-proj*t[1],wx[2]-proj*t[2])
  if dot(u,u)<1e-5:
   wz=(0.0,0.0,1.0);proj=dot(wz,t);u=(wz[0]-proj*t[0],wz[1]-proj*t[1],wz[2]-proj*t[2])
  u=norm(u);v=norm(cross(t,u))
  rw=max(widths[i]*.5,.0006);rd=max(depths[i]*.5,.0006)
  for k in range(ring_segments):
   ang=2*math.pi*k/ring_segments;ca=math.cos(ang);sa=math.sin(ang)
   q=(c[0]+u[0]*rw*ca+v[0]*rd*sa,c[1]+u[1]*rw*ca+v[1]*rd*sa,c[2]+u[2]*rw*ca+v[2]*rd*sa)
   verts.append(bpos(q))
 faces=[]
 for r in range(n-1):
  base=r*ring_segments;nxt=(r+1)*ring_segments
  for k in range(ring_segments):
   j=(k+1)%ring_segments;faces.append((base+k,base+j,nxt+j,nxt+k))
 faces.append(tuple(range(ring_segments-1,-1,-1)))
 last=(n-1)*ring_segments;faces.append(tuple(last+k for k in range(ring_segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

"""
s=s[:a]+helper+lock_helper+s[b:]

# Improve portrait readability while retaining the embedded-eye construction.
a=s.index('# Anatomy v3.1:')
b=s.index('# Hair v3.1:',a)
face=s[a:b]
face=face.replace('eye_rx=head_w*.098','eye_rx=head_w*.105')
face=face.replace('eye_ry=.0255','eye_ry=.0270')
face=face.replace('eye_rz=head_d*.075','eye_rz=head_d*.078')
face=face.replace("(head_w*.052,.0118,.0042)","(head_w*.057,.0128,.0044)")
face=face.replace("(head_w*.019,.0066,.0026)","(head_w*.021,.0072,.0028)")
face=face.replace(".00165,LIP)",".00185,LIP)")
face=face.replace(".00155,LIP)",".00172,LIP)")
s=s[:a]+face+s[b:]

# Replace the wire-like v3.1 hair with a small number of solid tapered locks.
a=s.index('# Hair v3.1:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.2: scalp mass -> broad volumetric locks -> sparse flyaways.
# The frontal cap is deliberately kept behind the hairline so it cannot read as a helmet/headband.
add_sphere(HEAD,'HairBackV32',(0,.028,-head_d*.365),(head_w*.520,.132,head_d*.455),HAIR,46,32)
add_sphere(HEAD,'HairCrownV32',(0,.112,-head_d*.210),(head_w*.480,.060,head_d*.325),HAIR,44,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV32_{side}',(side*head_w*.425,.018,-.030),(head_w*.095,.082,head_d*.145),HAIR,30,20)

# Seven main bangs. Their widths overlap slightly at the root but taper into broken, asymmetric tips.
bang_specs=[
 (-.116,-.102,-.091,.031,.140,.052),
 (-.081,-.067,-.054,.048,.131,.050),
 (-.047,-.036,-.025,.034,.143,.046),
 (-.013,-.005,.001,-.006,.149,.041),
 (.029,.039,.033,.029,.135,.046),
 (.064,.076,.069,.045,.145,.050),
 (.101,.112,.105,.030,.138,.052),
]
for i,(rx,mx,tx,ty,ry,w) in enumerate(bang_specs):
 pts=[(rx,ry,-head_d*.020),(mx,ry-.022,head_d*.145),(tx,.092,head_d*.390),(tx*.98,ty,head_d*.510)]
 widths=[w*.62,w,w*.72,.0065]
 depths=[.020,.022,.018,.0040]
 add_lock_mesh(HEAD,f'BangLockV32_{i}',pts,widths,depths,HAIR_HI if i in(1,5) else HAIR,10)
# A few tiny wisps break the silhouette without turning the forehead into wire curtains.
for i,(rx,tx,ty) in enumerate(((-.102,-.084,.020),(-.055,-.040,.012),(.015,.025,.014),(.061,.080,.031),(.104,.116,.017))):
 add_strand(HEAD,f'BangWispV32_{i}',[(rx,.128,head_d*.010),((rx+tx)*.5,.106,head_d*.260),(tx,ty,head_d*.512)],.0015,HAIR_HI if i in(0,4) else HAIR)

# Two layered face-framing locks per side, each with actual cross-section.
for side in(-1,1):
 for j,(off,end_y) in enumerate(((0.00,-.34),(.025,-.46))):
  pts=[(side*(head_w*.360+off),.075,-.010),(side*(head_w*.430+off),-.012,head_d*.090),(side*(head_w*.450+off),-.165,head_d*.025),(side*(head_w*.392+off),end_y,-.025)]
  add_lock_mesh(HEAD,f'FaceLockV32_{side}_{j}',pts,[.038-j*.009,.043-j*.009,.031-j*.007,.006],[.018,.020,.016,.004],HAIR_HI if j else HAIR,10)

# High ponytail root. The cascade is 15 solid locks rather than dozens of tubes or one cape.
add_sphere(HEAD,'PonyRootV32',(0,.152,-head_d*.420),(.080,.063,.065),HAIR,34,24)
add_box(HEAD,'HairTieV32',(0,.147,-head_d*.480),(.092,.023,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(15):
 lane=(i-7)/7
 sway=(-1 if i%2==0 else 1)*(.012+.006*abs(lane))
 zoff=((i%3)-1)*.015-.012*abs(lane)
 endx=lane*.245+sway
 pts=[
  (lane*.050,.150,-head_d*.510+zoff),
  (lane*.075,.030,-head_d*.750+zoff),
  (lane*.108+sway,-.245,-.490+zoff*.45),
  (lane*.155-sway,-.610,-.355),
  (lane*.205+sway,-1.000,-.230),
  (endx,-1.390,-.115),
  (endx*.96,-1.675-(i%4)*.020,-.030),
 ]
 base_w=.050-.012*abs(lane)
 widths=[base_w*.62,base_w,base_w*1.06,base_w*.96,base_w*.74,base_w*.40,.006]
 depths=[.026,.030,.032,.029,.023,.015,.004]
 add_lock_mesh(PONY,f'PonyLockV32_{i}',pts,widths,depths,HAIR_HI if i in(3,7,11) else HAIR,10)
# Sparse flyaways restore fine motion/detail around the broad silhouette.
for i in range(12):
 lane=(i-5.5)/5.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV32_{i}',[(lane*.046,.147,-head_d*.515),(lane*.080+sgn*.009,-.055,-head_d*.780),(lane*.140-sgn*.014,-.435,-.442),(lane*.210+sgn*.016,-.915,-.266),(lane*.275-sgn*.012,-1.320,-.125),(lane*.305,-1.675-(i%4)*.028,-.022)],.00145+(i%3)*.00022,HAIR_HI if i%5==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V32: stronger single-shell face and volumetric tapered hair locks')
