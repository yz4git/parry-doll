from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V30' in s:
    print('Blender heroine generator already carries REFERENCE_V30')
    raise SystemExit(0)
if '# REFERENCE_V29' not in s:
    raise SystemExit('REFERENCE_V29 generator required before v3.0')
s=s.replace('# REFERENCE_V29: anatomy-first head, embedded eyes, eyelids, connected nose and continuous ribcage.','# REFERENCE_V29: anatomy-first head, embedded eyes, eyelids, connected nose and continuous ribcage.\n# REFERENCE_V30: continuous facial surface and tangent-oriented hair ribbons.',1)

# Add a ribbon helper whose width follows the local tangent instead of always
# expanding along global X. This removes the triangular/cardboard hair artifacts.
anchor='def add_panel(p,name,points,depth,mat):\n'
helper="""def add_flow_ribbon(p,name,pts,widths,thickness,mat):
 verts=[];n=len(pts)
 for i,((x,y,z),w) in enumerate(zip(pts,widths)):
  if i==0: tx,ty=pts[1][0]-x,pts[1][1]-y
  elif i==n-1: tx,ty=x-pts[i-1][0],y-pts[i-1][1]
  else: tx,ty=pts[i+1][0]-pts[i-1][0],pts[i+1][1]-pts[i-1][1]
  ln=max((tx*tx+ty*ty)**.5,1e-6);px,py=-ty/ln,tx/ln;h=w*.5;t=thickness*.5
  verts.extend([bpos((x+px*h,y+py*h,z+t)),bpos((x-px*h,y-py*h,z+t)),bpos((x+px*h,y+py*h,z-t)),bpos((x-px*h,y-py*h,z-t))])
 faces=[]
 for i in range(n-1):
  a=i*4;b=(i+1)*4
  faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,a+2,a+3,a+1),(b,b+1,b+3,b+2)])
 faces.extend([(0,2,3,1),((n-1)*4,(n-1)*4+1,(n-1)*4+3,(n-1)*4+2)])
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

"""
if anchor not in s: raise SystemExit('add_panel anchor missing')
s=s.replace(anchor,helper+anchor,1)

# Slightly shorten the lower face and give the cheek/jaw transition more readable planes.
a=s.index("add_section_mesh(HEAD,'HeadShell',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_section_mesh(HEAD,'HeadShell',[
 (-.132,head_w*.120,head_d*.175,head_d*.230,.048),
 (-.116,head_w*.235,head_d*.240,head_d*.300,.041),
 (-.096,head_w*.325,head_d*.305,head_d*.355,.033),
 (-.070,head_w*.395,head_d*.350,head_d*.405,.024),
 (-.040,head_w*.455,head_d*.390,head_d*.450,.014),
 (-.006,head_w*.495,head_d*.425,head_d*.492,.003),
 (.026,head_w*.505,head_d*.450,head_d*.505,-.004),
 (.058,head_w*.490,head_d*.472,head_d*.482,-.010),
 (.090,head_w*.455,head_d*.482,head_d*.440,-.017),
 (.118,head_w*.400,head_d*.468,head_d*.382,-.024),
 (.145,head_w*.315,head_d*.435,head_d*.310,-.030)
],SKIN,52)
"""
s=s[:a]+head+s[b:]

# Replace the v2.9 feature assembly with one continuous mid-face patch. The patch
# encodes cheekbones, eye sockets, nose bridge/tip and muzzle in a single surface.
a=s.index('# Anatomy-first portrait: embedded eyeballs, eyelids and a connected central face form.')
b=s.index('# Rear scalp never crosses the forehead;',a)
face="""# Continuous facial surface: broad planes first, features second.
face_z=head_d*.505
xmax=head_w*.430
ymin,ymax=-.114,.108
nx,ny=17,17
verts=[]
for j in range(ny):
 y=ymin+(ymax-ymin)*j/(ny-1)
 for i in range(nx):
  x=-xmax+2*xmax*i/(nx-1)
  xn=x/max(xmax,1e-6)
  # Base curvature follows the front of the head while rolling away at the cheeks/jaw edges.
  z=face_z-.026*(xn*xn)-.007*((y-.004)/.125)**2
  # Zygomatic / cheek volume.
  for side in(-1,1):
   cx=side*head_w*.205
   z+=.0075*math.exp(-((x-cx)/(head_w*.115))**2-((y+.006)/.052)**2)
   # Eye socket sits behind the cheek/brow plane.
   ex=side*head_w*.160
   z-=.0065*math.exp(-((x-ex)/(head_w*.105))**2-((y-.025)/.030)**2)
  # Nose grows continuously out of the brow and mid-face.
  z+=.0075*math.exp(-(x/(head_w*.065))**2-((y-.020)/.078)**2)
  z+=.0125*math.exp(-(x/(head_w*.085))**2-((y+.035)/.026)**2)
  # Muzzle / mouth cushion and a subtle chin plane.
  z+=.0030*math.exp(-(x/(head_w*.190))**2-((y+.077)/.030)**2)
  z+=.0025*math.exp(-(x/(head_w*.150))**2-((y+.108)/.025)**2)
  verts.append(bpos((x,y,z)))
faces=[]
for j in range(ny-1):
 for i in range(nx-1):
  a0=j*nx+i;b0=a0+1;c0=a0+nx+1;d0=a0+nx;faces.append((a0,b0,c0,d0))
mesh=bpy.data.meshes.new('FaceSurfaceMesh');mesh.from_pydata(verts,[],faces);mesh.update();face_obj=bpy.data.objects.new('FaceSurface',mesh);bpy.context.scene.collection.objects.link(face_obj);face_obj.data.materials.append(SKIN);smooth(face_obj);parent(face_obj,HEAD)

# Eyeballs are established first and the eyelids hug their visible surface.
eye_y=.022
eye_x=head_w*.160
eye_z=face_z-.010
eye_rx=head_w*.092
eye_ry=.027
eye_rz=head_d*.088
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballV30_{side}',(ex,eye_y,eye_z),(eye_rx,eye_ry,eye_rz),SCLERA,34,22)
 front=eye_z+eye_rz*.98
 add_sphere(HEAD,f'IrisV30_{side}',(ex,eye_y-.001,front+.003),(head_w*.051,.0125,.0045),IRIS,26,16)
 add_sphere(HEAD,f'PupilV30_{side}',(ex,eye_y-.001,front+.0062),(head_w*.019,.0072,.0028),PUPIL,20,12)
 add_sphere(HEAD,f'EyeLightV30_{side}',(ex-side*head_w*.012,eye_y+.008,front+.009),(head_w*.010,.004,.0017),SCLERA,12,8)
 inner=ex-side*eye_rx*.92;outer=ex+side*eye_rx*.98
 add_flow_ribbon(HEAD,f'UpperLidV30_{side}',[(inner,.026,front+.003),(ex,.040,front+.006),(outer,.027,front+.003)],[.010,.012,.009],.0023,SKIN)
 add_flow_ribbon(HEAD,f'LowerLidV30_{side}',[(inner,.011,front+.003),(ex,.000,front+.004),(outer,.012,front+.003)],[.007,.009,.007],.0020,SKIN)
 add_flow_ribbon(HEAD,f'UpperLashV30_{side}',[(inner,.030,front+.008),(ex,.043,front+.010),(outer,.030,front+.008)],[.0035,.0042,.0032],.0014,HAIR)
 add_flow_ribbon(HEAD,f'BrowV30_{side}',[(ex-side*eye_rx*.80,.075,face_z+.005),(ex,.084,face_z+.008),(ex+side*eye_rx*.98,.071,face_z+.005)],[.006,.007,.005],.0014,HAIR)

# The nose tip/wings only add secondary volume; the bridge is already in FaceSurface.
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV30_{side}',(side*.012,-.047,face_z+.010),(.0075,.0070,.0050),SKIN,18,10)
# Soft lips follow the mouth arc rather than rectangular decal plates.
add_flow_ribbon(HEAD,'UpperLipV30',[(-.028,-.077,face_z+.004),(0,-.073,face_z+.006),(.028,-.077,face_z+.004)],[.007,.009,.007],.0017,LIP)
add_flow_ribbon(HEAD,'LowerLipV30',[(-.024,-.084,face_z+.004),(0,-.089,face_z+.006),(.024,-.084,face_z+.004)],[.006,.009,.006],.0016,LIP)
"""
s=s[:a]+face+s[b:]

# Rebuild the complete hair layer with tangent-oriented locks. Remove the old
# plate/ribbon cascade between the scalp marker and the limb section.
a=s.index('# Rear scalp never crosses the forehead;')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.0: scalp mass, directional locks, then secondary strands.
add_sphere(HEAD,'HairBackV30',(0,.024,-head_d*.365),(head_w*.515,.130,head_d*.455),HAIR,44,30)
add_sphere(HEAD,'HairTopV30',(0,.103,-head_d*.205),(head_w*.475,.065,head_d*.330),HAIR,42,26)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV30_{side}',(side*head_w*.420,.012,-.030),(head_w*.090,.085,head_d*.145),HAIR,28,18)

# Seven major fringe locks start at different crown positions and sweep around the eyes.
fringe=[
 (-.120,-.104,-.092,.036,.050,.136),
 (-.082,-.068,-.056,.048,.047,.128),
 (-.045,-.034,-.026,.038,.043,.140),
 (-.012,-.004,.000,-.004,.038,.146),
 (.030,.040,.032,.030,.043,.132),
 (.068,.080,.070,.047,.047,.141),
 (.108,.118,.108,.034,.050,.134),
]
for i,(rx,mx,tx,ty,w,ry) in enumerate(fringe):
 add_flow_ribbon(HEAD,f'FringeV30_{i}',[(rx,ry,-head_d*.035),(mx,ry-.022,head_d*.18),(tx,.092,face_z*.76),(tx*.98,ty,face_z+.018)],[w*.58,w,w*.72,w*.14],.0034,HAIR_HI if i in(1,5) else HAIR)
# Fine crossover locks break symmetry and hide the scalp/lock seam.
for i,(rx,tx,ty) in enumerate(((-.102,-.078,.025),(-.058,-.038,.018),(.014,.020,.012),(.057,.074,.035),(.100,.118,.020))):
 add_flow_ribbon(HEAD,f'FringeFineV30_{i}',[(rx,.126,-head_d*.015),((rx+tx)*.5,.105,head_d*.30),(tx,ty,face_z+.019)],[.019,.014,.0035],.0023,HAIR_HI if i in(0,4) else HAIR)
# Face-framing locks are long but narrow, like the supplied four-view reference.
for side in(-1,1):
 for j,(off,end_y) in enumerate(((0.00,-.34),(.030,-.46))):
  add_flow_ribbon(HEAD,f'FaceFrameV30_{side}_{j}',[(side*(head_w*.365+off),.074,-.010),(side*(head_w*.435+off),-.010,head_d*.10),(side*(head_w*.450+off),-.155,head_d*.035),(side*(head_w*.390+off),end_y,-.020)],[.040-j*.012,.035-j*.010,.022-j*.006,.007-j*.002],.0037 if j==0 else .0027,HAIR_HI if j else HAIR)

# High ponytail: overlapping broad flow ribbons, no opaque cape core.
add_sphere(HEAD,'PonyRootV30',(0,.150,-head_d*.420),(.076,.060,.062),HAIR,32,22)
add_box(HEAD,'HairTieV30',(0,.145,-head_d*.475),(.088,.022,.032),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(13):
 lane=(i-6)/6
 sway=(-1 if i%2==0 else 1)*(.014+.004*(abs(lane)))
 zoff=-.020*abs(lane)+(.008 if i%3==0 else 0)
 endx=lane*.245+sway
 add_flow_ribbon(PONY,f'PonyFlowV30_{i}',[(lane*.050,.145,-head_d*.50+zoff),(lane*.075,.030,-head_d*.74+zoff),(lane*.105+sway,-.250,-.485),(lane*.155-sway,-.610,-.360),(lane*.205+sway,-1.000,-.235),(endx,-1.390,-.120),(endx*.96,-1.690-(i%3)*.025,-.035)],[.032,.048,.060,.058,.047,.028,.0065],.0038,HAIR_HI if i in(2,6,10) else HAIR)
# Dark under-layer keeps rear density without returning to one solid sheet.
for i,lane in enumerate((-.50,-.25,0,.25,.50)):
 add_flow_ribbon(PONY,f'PonyUnderV30_{i}',[(lane*.040,.136,-head_d*.54),(lane*.075,-.010,-head_d*.80),(lane*.120,-.420,-.455),(lane*.170,-.900,-.275),(lane*.215,-1.420,-.090)],[.035,.050,.060,.045,.010],.0032,HAIR)
for i in range(16):
 lane=(i-7.5)/7.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV30_{i}',[(lane*.045,.142,-head_d*.52),(lane*.080+sgn*.008,-.060,-head_d*.78),(lane*.135-sgn*.012,-.440,-.445),(lane*.200+sgn*.015,-.920,-.270),(lane*.265-sgn*.010,-1.330,-.130),(lane*.300,-1.690-(i%4)*.020,-.025)],.0018+(i%3)*.00028,HAIR_HI if i%5==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V30: continuous facial surface and tangent-oriented hair ribbons')
