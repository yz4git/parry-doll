import bpy, json, os, math

ROOT_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
OUT=os.path.join(ROOT_DIR,'dist','assets','models','heroine-blender.glb')
REF_PATH=os.path.join(ROOT_DIR,'tools','heroine-reference-proportions.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
H=float(REF['derived_world_units']['nominal_height'])
FW=REF['front_width_over_height'];SD=REF['side_depth_over_height'];DW=REF['derived_world_units']
W=lambda key:float(FW[key])*H
D=lambda key:float(SD[key])*H

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def bpos(v):x,y,z=v;return(x,-z,y)
def bscale(v):x,y,z=v;return(x,z,y)
def material(name,color,metallic=0.0,roughness=.45):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metallic;b.inputs['Roughness'].default_value=roughness;return m
SKIN=material('Skin',(0.69,0.49,0.45),0,.62)
BLACK=material('Suit Black',(0.014,0.018,0.027),.08,.30)
BLACK_SOFT=material('Suit Soft',(0.030,0.035,0.048),.02,.44)
WHITE=material('Porcelain White',(0.86,0.88,0.88),.18,.28)
SILVER=material('Silver',(0.50,0.53,0.56),.78,.19)
HAIR=material('Hair',(0.007,0.006,0.010),0.0,.52)
HAIR_HI=material('Hair Highlight',(0.026,0.020,0.030),0.0,.46)
# Reduce Principled specular so dark hair does not blow out to a silver ribbon under bright sky lighting.
for _hair_mat,_spec in ((HAIR,.14),(HAIR_HI,.18)):
 _bsdf=_hair_mat.node_tree.nodes.get('Principled BSDF')
 if _bsdf:
  _ior=_bsdf.inputs.get('Specular IOR Level')
  _old=_bsdf.inputs.get('Specular')
  if _ior:_ior.default_value=_spec
  elif _old:_old.default_value=_spec
SCLERA=material('Sclera',(0.86,0.84,0.82),0,.42)
IRIS=material('Iris',(0.12,0.085,0.070),.02,.34)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.38,0.13,0.16),0,.52)
FACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)
GLOW=material('Cyan Accent',(0.20,0.56,0.61),.38,.18)

def parent(o,p):o.parent=p;return o
def empty(name,p=None):
 o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o)
 if p:o.parent=p
 return o
def smooth(o):
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def add_sphere(p,name,loc,scale,mat,segments=30,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=bpos(loc));o=bpy.context.object;o.name=name;o.scale=bscale(scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);smooth(o);return parent(o,p)
def add_box(p,name,loc,scale,mat,bevel=.020,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(size=1,location=bpos(loc));o=bpy.context.object;o.name=name;o.dimensions=bscale(scale);o.rotation_euler=(rot[0],rot[2],-rot[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('bevel','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 smooth(o);return parent(o,p)
def add_cylinder(p,name,loc,radius,length,mat,vertices=28):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=length,location=bpos(loc));o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return parent(o,p)
def add_taper(p,name,r1,r2,depth1,depth2,mat):
 # Four elliptical rings use both end widths/depths; this removes the old tube + ball-joint look.
 rings=[(-.50,r1,depth1),(-.18,r1*.97,depth1*.96),(.18,(r1+r2)*.51,(depth1+depth2)*.50),(.50,r2,depth2)]
 verts=[];seg=32
 for yy,w,d in rings:
  for i in range(seg):
   ang=2*math.pi*i/seg;verts.append(bpos((math.cos(ang)*w,yy,math.sin(ang)*d)))
 faces=[]
 for r in range(len(rings)-1):
  base=r*seg;nxt=(r+1)*seg
  for i in range(seg):j=(i+1)%seg;faces.append((base+i,base+j,nxt+j,nxt+i))
 faces.append(tuple(range(seg-1,-1,-1)));last=(len(rings)-1)*seg;faces.append(tuple(last+i for i in range(seg)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name+'_core',mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

def add_section_mesh(p,name,sections,mat,segments=36):
 # sections: (logical_y, half_width, back_depth, front_depth, z_offset)
 verts=[]
 for yy,w,back,front,zoff in sections:
  for i in range(segments):
   ang=2*math.pi*i/segments;sn=math.sin(ang);depth=front if sn>=0 else back
   verts.append(bpos((math.cos(ang)*w,yy,zoff+sn*depth)))
 faces=[]
 for r in range(len(sections)-1):
  base=r*segments;nxt=(r+1)*segments
  for i in range(segments):j=(i+1)%segments;faces.append((base+i,base+j,nxt+j,nxt+i))
 faces.append(tuple(range(segments-1,-1,-1)));last=(len(sections)-1)*segments;faces.append(tuple(last+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

def add_anatomical_head(p,name,sections,mat,segments=64):
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
    z+=fm*.0170*math.exp(-(x/(head_w*.060))**2-((yy-.020)/.086)**2)
    z+=fm*.0355*math.exp(-(x/(head_w*.076))**2-((yy+.041)/.025)**2)
    z+=fm*.0072*math.exp(-(x/(head_w*.052))**2-((yy+.058)/.017)**2)
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

def add_lock_mesh(p,name,pts,widths,depths,mat,ring_segments=10):
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

def add_almond_surface(p,name,cx,cy,cz,rx,ry,bulge,mat,segments=28,side=1,tilt=0.0):
 verts=[bpos((cx,cy,cz+bulge))]
 for i in range(segments):
  a=2*math.pi*i/segments
  ca=math.cos(a);sa=math.sin(a)
  x=cx+rx*ca
  # Pinched almond with a slight canthal tilt: the outer corner sits higher than the inner corner.
  yy=cy+ry*sa*(.68+.32*abs(ca))+tilt*side*ca
  verts.append(bpos((x,yy,cz)))
 faces=[]
 for i in range(segments):faces.append((0,1+i,1+((i+1)%segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

def add_ribbon(p,name,pts,widths,thickness,mat):
 verts=[]
 for (x,y,z),w in zip(pts,widths):
  h=w*.5;t=thickness*.5
  verts.extend([bpos((x-h,y,z+t)),bpos((x+h,y,z+t)),bpos((x-h,y,z-t)),bpos((x+h,y,z-t))])
 faces=[]
 for i in range(len(pts)-1):
  a=i*4;b=(i+1)*4
  faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,a+2,a+3,a+1),(b,b+1,b+3,b+2)])
 faces.extend([(0,2,3,1),((len(pts)-1)*4,(len(pts)-1)*4+1,(len(pts)-1)*4+3,(len(pts)-1)*4+2)])
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

def add_flow_ribbon(p,name,pts,widths,thickness,mat):
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

def add_panel(p,name,points,depth,mat):
 front=[(x,y,z+depth*.5) for x,y,z in points];back=[(x,y,z-depth*.5) for x,y,z in points];verts=[bpos(v) for v in front+back];n=len(points);faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);return parent(o,p)
def add_strand(p,name,pts,radius,mat):
 c=bpy.data.curves.new(name+'Curve','CURVE');c.dimensions='3D';c.resolution_u=3;c.bevel_depth=radius;c.bevel_resolution=2;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for bp,q in zip(s.bezier_points,pts):bp.co=bpos(q);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.parent=p;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return o

ROOT=empty('BLENDER_HEROINE');PELVIS=empty('BL_PELVIS',ROOT);TORSO=empty('BL_TORSO',ROOT);HEAD=empty('BL_HEAD',ROOT)
UA_L=empty('BL_UPPER_ARM_L',ROOT);FA_L=empty('BL_FOREARM_L',ROOT);HAND_L=empty('BL_HAND_L',ROOT);UA_R=empty('BL_UPPER_ARM_R',ROOT);FA_R=empty('BL_FOREARM_R',ROOT);HAND_R=empty('BL_HAND_R',ROOT)
TH_L=empty('BL_THIGH_L',ROOT);SH_L=empty('BL_SHIN_L',ROOT);FOOT_L=empty('BL_FOOT_L',ROOT);TH_R=empty('BL_THIGH_R',ROOT);SH_R=empty('BL_SHIN_R',ROOT);FOOT_R=empty('BL_FOOT_R',ROOT);SWORD=empty('BL_SWORD',ROOT)

# === REFERENCE-LOCKED BODY ENVELOPE ===
# Source sheet measured at H=961 px and normalized in heroine-reference-proportions.json.
# REFERENCE_V14: direct silhouette-driven Blender authoring pass.
# REFERENCE_V15: hair mass, portrait and layered couture polish.
# REFERENCE_V16: side-curve, face and pony-root polish.
# REFERENCE_V17: portrait readability, shoulder continuity and refined heels.
# REFERENCE_V18: natural hairline, clavicle bridge and stronger feminine torso curvature.
# REFERENCE_V19: continuous portrait shell and face-plane retarget.
# REFERENCE_V20: fuller bodice curve, longer fringe, deeper ponytail and broader front couture.
# REFERENCE_V21: solid scalp coverage and panel-based fringe.
# REFERENCE_V22: eye-clear tapered fringe proportions.
# REFERENCE_V23: projected portrait features for reliable front/profile readability.
# REFERENCE_V24: eyebrow-height fringe with open eye line.
# REFERENCE_V25: larger portrait eyes and strand-separated ponytail mass.
# REFERENCE_V26: strand-flow fringe, split pony cascade and couture micro-detail.
# REFERENCE_V27: asymmetric fringe, clean forehead and layered-volume ponytail.
# REFERENCE_V28: low-specular black hair and staggered fringe roots.
# REFERENCE_V29: anatomy-first head, embedded eyes, eyelids, connected nose and continuous ribcage.
# REFERENCE_V30: continuous facial surface and tangent-oriented hair ribbons.
# REFERENCE_V31: sculpted single-shell face and curve-based hair masses.
# REFERENCE_V32: stronger facial planes and tapered volumetric hair locks.
# REFERENCE_V33: portrait-first facial proportions and layered blade-like hair locks.
# REFERENCE_V34: almond eye surfaces, explicit facial cues and thin swept fringe blades.
# REFERENCE_V35: asymmetric key-art fringe, stronger portrait cues and brighter couture balance.
# REFERENCE_V36: portrait anatomy rebuild, larger almond eyes and dark layered forehead locks.
# REFERENCE_V37: separate skull width from hair span and retarget portrait features to the narrower face.
# REFERENCE_V38: tilted expressive almond eyes and stronger central portrait cues.
# REFERENCE_V39: portrait de-doll pass with slimmer eyes, stronger nose/lips and finer asymmetric fringe.
# REFERENCE_V40: narrower shoulder flow and split couture skirt that exposes the long-leg silhouette.
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope as a single continuous surface.
# Front depth peaks at the bust while the lower back eases toward the high waist, matching the side sheet.
add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.49,waist_d*.49,waist_d*.54,-.006),
 (-.285,waist_w*.47,waist_d*.47,waist_d*.54,-.004),
 (-.220,waist_w*.49,waist_d*.46,waist_d*.55,-.001),
 (-.150,bust_w*.37,bust_d*.40,bust_d*.47,.004),
 (-.075,bust_w*.43,bust_d*.41,bust_d*.54,.011),
 (.000,bust_w*.48,bust_d*.42,bust_d*.62,.021),
 (.075,bust_w*.515,bust_d*.44,bust_d*.675,.030),
 (.135,bust_w*.505,bust_d*.44,bust_d*.655,.030),
 (.195,bust_w*.465,bust_d*.42,bust_d*.57,.022),
 (.255,bust_w*.405,bust_d*.39,bust_d*.48,.012),
 (.315,bust_w*.340,bust_d*.34,bust_d*.385,.002)
],BLACK,48)
# Shallow soft-tissue support over a continuous ribcage. The outer envelope remains reference-locked.
for side in(-1,1):
 add_sphere(TORSO,f'BustSoft_{side}',(side*bust_w*.205,.105,bust_d*.330),(bust_w*.205,.082,bust_d*.180),BLACK,36,22)
add_box(TORSO,'UnderBustLine',(0,.020,bust_d*.505),(bust_w*.70,.014,.009),SILVER,.003)
for side in(-1,1):
 add_box(TORSO,f'WaistContour_{side}',(side*waist_w*.44,-.150,waist_d*.50),(.012,.175,.009),SILVER,.0035,rot=(0,0,-side*.15))
# Anatomical clavicle/deltoid bridge inside the measured shoulder envelope.
for side in(-1,1):
 add_sphere(TORSO,f'DeltoidBridge_{side}',(side*bust_w*.365,.238,.002),(bust_w*.108,.061,bust_d*.142),BLACK,30,20)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.285,.258,bust_d*.28),(side*bust_w*.392,.225,bust_d*.18),(side*bust_w*.275,.210,bust_d*.31)],.013,BLACK_SOFT)
 add_box(TORSO,f'ClavicleTrim_{side}',(side*bust_w*.225,.247,bust_d*.325),(bust_w*.250,.010,.008),SILVER,.0025,rot=(0,0,-side*.11))
# Reference-like harness: thin lines, no square robot chest plates.
add_box(TORSO,'Sternum',(0,.085,bust_d*.43),(.020,.355,.016),SILVER,.006)
add_box(TORSO,'Collar',(0,.305,.010),(W('neck')*1.15,.055,.105),BLACK,.014)
add_box(TORSO,'WaistBelt',(0,-.255,.005),(waist_w*1.12,.040,waist_d*1.10),SILVER,.008)
for side in(-1,1):
 add_box(TORSO,f'UpperHarness_{side}',(side*.095,.205,bust_d*.39),(.020,.255,.014),SILVER,.006,rot=(0,0,side*.40))
 add_box(TORSO,f'LowerHarness_{side}',(side*.072,-.080,bust_d*.37),(.018,.210,.014),SILVER,.006,rot=(0,0,-side*.28))
 add_panel(TORSO,f'WhiteSidePanel_{side}',[(side*waist_w*.53,-.23,.02),(side*bust_w*.48,.05,.01),(side*bust_w*.43,.24,.00),(side*waist_w*.56,-.08,.02)],.025,WHITE)
 if side<0:
  add_panel(TORSO,'FrontBodiceWhiteL',[(-bust_w*.47,.205,bust_d*.47),(-bust_w*.28,.185,bust_d*.54),(-waist_w*.32,-.205,waist_d*.63),(-waist_w*.58,-.235,waist_d*.52)],.014,WHITE)
  add_box(TORSO,'BustTrimL',(-bust_w*.31,.115,bust_d*.555),(.016,.190,.010),SILVER,.004,rot=(0,0,-.18))
 else:
  add_panel(TORSO,'FrontBodiceWhiteR',[(bust_w*.28,.185,bust_d*.54),(bust_w*.47,.205,bust_d*.47),(waist_w*.58,-.235,waist_d*.52),(waist_w*.32,-.205,waist_d*.63)],.014,WHITE)
  add_box(TORSO,'BustTrimR',(bust_w*.31,.115,bust_d*.555),(.016,.190,.010),SILVER,.004,rot=(0,0,.18))

# v3.5 brighter front couture: white side bodice layers over the existing black anatomical core.
add_panel(TORSO,'BodiceWhiteV35_L',[(-bust_w*.455,.218,bust_d*.515),(-bust_w*.255,.190,bust_d*.585),(-waist_w*.245,-.190,waist_d*.675),(-waist_w*.520,-.225,waist_d*.585)],.010,WHITE)
add_panel(TORSO,'BodiceWhiteV35_R',[(bust_w*.255,.190,bust_d*.585),(bust_w*.455,.218,bust_d*.515),(waist_w*.520,-.225,waist_d*.585),(waist_w*.245,-.190,waist_d*.675)],.010,WHITE)
for side in(-1,1):
 add_box(TORSO,f'BodiceEdgeV35_{side}',(side*bust_w*.275,.030,bust_d*.600),(.012,.330,.009),SILVER,.0035,rot=(0,0,side*.08))
 add_box(TORSO,f'UpperArmBandV35_{side}',(side*.205,.215,.000),(.040,.020,.072),BLACK,.004)

# Compact pelvis and high waist: measured 0.123H width and 0.089H depth.
add_section_mesh(PELVIS,'PelvisSuit',[
 (-.180,pelvis_w*.42,pelvis_d*.60,pelvis_d*.48,-.018),
 (-.080,pelvis_w*.50,pelvis_d*.58,pelvis_d*.52,-.012),
 (.040,pelvis_w*.49,pelvis_d*.52,pelvis_d*.51,-.005),
 (.155,waist_w*.57,waist_d*.56,waist_d*.59,0.000)
],BLACK,36)
add_box(PELVIS,'HighWaist',(0,.105,.012),(pelvis_w*.96,.070,pelvis_d*.88),BLACK,.018)
add_box(PELVIS,'HipBelt',(0,.145,.018),(pelvis_w*1.08,.028,pelvis_d*.94),SILVER,.008)
# Layered split skirt v4.0: short front petals keep the thigh line visible; long tails move behind/outside the legs.
add_panel(PELVIS,'FrontCenterV40_L',[(-.145,.124,.142),(-.010,.118,.152),(-.024,-.150,.160),(-.080,-.295,.142),(-.170,-.155,.108)],.016,WHITE)
add_panel(PELVIS,'FrontCenterV40_R',[(.010,.118,.152),(.145,.124,.142),(.170,-.155,.108),(.080,-.295,.142),(.024,-.150,.160)],.016,WHITE)
add_panel(PELVIS,'HipPetalV40_L',[(-.112,.120,.116),(-.226,.096,.092),(-.276,-.080,.070),(-.218,-.245,.090),(-.132,-.150,.122)],.015,BLACK)
add_panel(PELVIS,'HipPetalV40_R',[(.112,.120,.116),(.132,-.150,.122),(.218,-.245,.090),(.276,-.080,.070),(.226,.096,.092)],.015,BLACK)
# Bright outer split panels stop high on the thigh instead of becoming calf-length white stripes.
add_panel(PELVIS,'OuterPetalV40_L',[(-.180,.108,.104),(-.252,.072,.070),(-.300,-.135,.050),(-.250,-.335,.068),(-.174,-.190,.112)],.013,WHITE)
add_panel(PELVIS,'OuterPetalV40_R',[(.180,.108,.104),(.174,-.190,.112),(.250,-.335,.068),(.300,-.135,.050),(.252,.072,.070)],.013,WHITE)
# Black under-petals create a clean split silhouette and visually lengthen the legs.
add_panel(PELVIS,'SplitUnderV40_L',[(-.210,.095,.040),(-.278,.060,.010),(-.318,-.205,-.018),(-.276,-.455,.018),(-.218,-.250,.060)],.012,BLACK)
add_panel(PELVIS,'SplitUnderV40_R',[(.210,.095,.040),(.218,-.250,.060),(.276,-.455,.018),(.318,-.205,-.018),(.278,.060,.010)],.012,BLACK)
# Only two long couture tails remain, swept backward and outward so the front leg columns stay clear.
add_panel(PELVIS,'RearTailV40_L',[(-.250,.080,-.120),(-.158,.070,-.160),(-.205,-.420,-.205),(-.285,-.820,-.145),(-.350,-.470,-.090)],.014,BLACK)
add_panel(PELVIS,'RearTailV40_R',[(.158,.070,-.160),(.250,.080,-.120),(.350,-.470,-.090),(.285,-.820,-.145),(.205,-.420,-.205)],.014,BLACK)
add_panel(PELVIS,'RearTailInlayV40_L',[(-.270,.050,-.132),(-.190,.045,-.168),(-.226,-.405,-.188),(-.282,-.690,-.140),(-.326,-.445,-.104)],.009,WHITE)
add_panel(PELVIS,'RearTailInlayV40_R',[(.190,.045,-.168),(.270,.050,-.132),(.326,-.445,-.104),(.282,-.690,-.140),(.226,-.405,-.188)],.009,WHITE)

# === REFERENCE COUTURE MICRO DETAIL v2.6 ===
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

# === HEAD / FACE ===
# One continuous measured portrait shell instead of overlapping spheres.
add_anatomical_head(HEAD,'HeadShellV37',[
 (-.140,head_w*.052,head_d*.142,head_d*.192,.052),
 (-.130,head_w*.120,head_d*.194,head_d*.252,.046),
 (-.117,head_w*.195,head_d*.250,head_d*.310,.038),
 (-.101,head_w*.260,head_d*.294,head_d*.356,.031),
 (-.082,head_w*.315,head_d*.336,head_d*.400,.023),
 (-.058,head_w*.365,head_d*.374,head_d*.442,.014),
 (-.031,head_w*.410,head_d*.408,head_d*.474,.006),
 (-.003,head_w*.438,head_d*.436,head_d*.492,-.001),
 (.026,head_w*.450,head_d*.456,head_d*.492,-.006),
 (.055,head_w*.442,head_d*.472,head_d*.474,-.011),
 (.083,head_w*.420,head_d*.478,head_d*.444,-.016),
 (.108,head_w*.385,head_d*.470,head_d*.402,-.021),
 (.130,head_w*.335,head_d*.450,head_d*.350,-.026),
 (.148,head_w*.270,head_d*.420,head_d*.290,-.030)
],SKIN,76)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.445,-.018,-.014),(.010,.023,.009),SKIN,18,10)
# Anatomy v3.9: narrower cinematic eyes, clearer nose/lips, and a softer adult portrait read.
face_front=head_d*.512
eye_y=.031
eye_x=head_w*.137
eye_rx=head_w*.098
eye_ry=.0132
eye_tilt=.0032
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV39_{side}',(ex,eye_y,head_d*.425),(head_w*.082,.017,head_d*.064),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeOpeningV39_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0028,SCLERA,34,side,eye_tilt)
 # Darker/larger iris coverage keeps the eyes expressive without the white-heavy doll stare.
 add_sphere(HEAD,f'IrisV39_{side}',(ex,eye_y+.0008,face_front+.0057),(head_w*.040,.0106,.0030),IRIS,30,18)
 add_sphere(HEAD,f'PupilV39_{side}',(ex,eye_y+.0008,face_front+.0085),(head_w*.0148,.0055,.0020),PUPIL,22,12)
 add_sphere(HEAD,f'EyeLightV39_{side}',(ex-side*head_w*.0095,eye_y+.0054,face_front+.0105),(head_w*.0058,.0026,.0012),SCLERA,12,8)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.01
 inner_y=eye_y-eye_tilt
 outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV39_{side}',[(inner,inner_y+.0010,face_front+.0027),(ex,eye_y+.0134,face_front+.0058),(outer,outer_y+.0012,face_front+.0028)],.00120,SKIN)
 add_strand(HEAD,f'LowerLidV39_{side}',[(inner,inner_y-.0008,face_front+.0022),(ex,eye_y-.0080,face_front+.0032),(outer,outer_y-.0008,face_front+.0022)],.00068,SKIN)
 add_strand(HEAD,f'UpperLashV39_{side}',[(inner,inner_y+.0025,face_front+.0066),(ex,eye_y+.0146,face_front+.0082),(outer,outer_y+.0027,face_front+.0068)],.00175,HAIR)
 add_strand(HEAD,f'LashWingV39_{side}',[(outer,outer_y+.0027,face_front+.0068),(outer+side*head_w*.026,outer_y+.0090,face_front+.0074)],.00128,HAIR)
 add_strand(HEAD,f'LowerLashV39_{side}',[(inner,inner_y,face_front+.0048),(ex,eye_y-.0072,face_front+.0051),(outer,outer_y,face_front+.0048)],.00038,HAIR)
 # Lower, flatter brows improve the mature key-art expression and reduce forehead emptiness.
 add_strand(HEAD,f'BrowV39_{side}',[(ex-side*eye_rx*.86,.067,head_d*.511),(ex,.076,head_d*.517),(ex+side*eye_rx*1.06,.065,head_d*.511)],.00162,HAIR)

# Readable front/profile nose: preserve the connected shell but give bridge, tip and nostrils distinct planes.
add_strand(HEAD,'NoseBridgeCueV39',[(0,.035,head_d*.516),(-.001,-.005,head_d*.523),(-.002,-.033,head_d*.531)],.00055,FACE_DARK)
add_sphere(HEAD,'NoseTipSoftV39',(0,-.043,head_d*.536),(.0105,.0088,.0057),SKIN,22,14)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV39_{side}',(side*.0108,-.050,head_d*.530),(.0058,.0051,.0040),SKIN,18,10)
 add_sphere(HEAD,f'NostrilV39_{side}',(side*.0075,-.052,head_d*.536),(.0026,.0018,.0014),FACE_DARK,12,8)
add_strand(HEAD,'NoseUndersideV39',[(-.0105,-.050,head_d*.534),(0,-.055,head_d*.538),(.0105,-.050,head_d*.534)],.00088,FACE_DARK)

# Slightly fuller, lower lips survive normal gameplay distance without reading as a painted dot.
add_strand(HEAD,'UpperLipLeftV39',[(-.032,-.080,head_d*.534),(-.016,-.075,head_d*.538),(0,-.080,head_d*.539)],.00162,LIP)
add_strand(HEAD,'UpperLipRightV39',[(0,-.080,head_d*.539),(.016,-.075,head_d*.538),(.032,-.080,head_d*.534)],.00162,LIP)
add_strand(HEAD,'MouthLineV39',[(-.032,-.084,head_d*.537),(0,-.087,head_d*.540),(.032,-.084,head_d*.537)],.00115,FACE_DARK)
add_strand(HEAD,'LowerLipV39',[(-.025,-.088,head_d*.535),(0,-.094,head_d*.538),(.025,-.088,head_d*.535)],.00136,LIP)
for side in(-1,1):
 add_sphere(HEAD,f'MouthCornerV39_{side}',(side*.032,-.084,head_d*.537),(.0019,.0015,.0012),FACE_DARK,10,6)

# Hair v3.9: compact scalp mass, seven finer swept fringe locks, and slimmer cheek framing.
add_sphere(HEAD,'HairBackV39',(0,.030,-head_d*.365),(head_w*.508,.128,head_d*.452),HAIR,48,32)
add_sphere(HEAD,'HairCrownV39',(-.014,.118,-head_d*.208),(head_w*.468,.058,head_d*.320),HAIR,46,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV39_{side}',(side*head_w*.407,.020,-.031),(head_w*.082,.074,head_d*.132),HAIR,30,20)

# Fine layered fringe: most tips stop around brow height, leaving the eye line readable.
primary=[
 (-.118,-.100,-.072,.054,.150,.038,.0060),
 (-.088,-.069,-.039,.068,.157,.037,.0055),
 (-.054,-.033,-.004,.080,.162,.034,.0050),
 (-.020,.004,.030,.084,.164,.032,.0048),
 (.018,.039,.064,.076,.160,.034,.0052),
 (.054,.073,.096,.061,.154,.036,.0058),
 (.086,.101,.120,.045,.147,.032,.0055),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(primary):
 pts=[(rx,ry,-head_d*.014),(mx,ry-.022,head_d*.160),((mx+tx)*.5,.112,head_d*.365),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'ForeheadLockV39_{i}',pts,[w*.58,w,w*.60,tipw],[.0075,.0090,.0070,.0028],HAIR_HI if i in(0,6) else HAIR,6)

# Crossing ribbons create a continuous side-part sweep without restoring the chunky helmet fringe.
secondary=[(-.108,-.077,.072),(-.074,-.043,.083),(-.036,.000,.090),(.010,.048,.081),(.050,.088,.067),(.082,.114,.052)]
for i,(rx,tx,ty) in enumerate(secondary):
 pts=[(rx,.146,head_d*.008),((rx+tx)*.5,.121,head_d*.285),(tx,.096,head_d*.444),(tx,ty,head_d*.520)]
 add_lock_mesh(HEAD,f'FringeLayerV39_{i}',pts,[.015,.017,.011,.0038],[.0045,.0050,.0040,.0020],HAIR_HI if i in(0,5) else HAIR,6)
for i,(rx,tx,ty) in enumerate(((-.104,-.088,.061),(-.062,-.040,.074),(-.016,.010,.083),(.036,.064,.070),(.078,.108,.054))):
 add_strand(HEAD,f'BangWispV39_{i}',[(rx,.139,head_d*.020),((rx+tx)*.5,.112,head_d*.320),(tx,ty,head_d*.523)],.00082,HAIR_HI if i in(0,4) else HAIR)

# Face framing is deliberately slim and bowed away from the cheeks; the v3.8 audit showed dark vertical bars.
for side in(-1,1):
 pts=[(side*head_w*.344,.082,-.010),(side*head_w*.394,.010,head_d*.075),(side*head_w*.410,-.145,head_d*.010),(side*head_w*.372,-.335,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV39_{side}',pts,[.022,.025,.016,.0038],[.0055,.0060,.0045,.0022],HAIR,6)
 add_strand(HEAD,f'FaceWispV39_{side}',[(side*head_w*.380,.070,-.006),(side*head_w*.430,-.040,head_d*.040),(side*head_w*.420,-.235,-.004),(side*head_w*.395,-.455,-.030)],.00085,HAIR_HI)

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

# === LIMBS ===
# Diameters come directly from the front sheet; side depth comes from the side view.
ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.50;kn=W('knee_each')*.50;calf=W('calf_each')*.50;ank=W('ankle_each')*.50
ua_d=ua*.78;fa_d=fa*.80;th_d=D('thigh')*.50;calf_d=D('calf')*.50;ank_d=D('ankle')*.50
for group,name,r1,r2,d1,d2,mat in[
 (UA_L,'UpperArmL',ua*.98,ua*.78,ua_d,ua_d*.82,SKIN),(UA_R,'UpperArmR',ua*.98,ua*.78,ua_d,ua_d*.82,SKIN),
 (FA_L,'ForearmL',fa*.92,fa*.68,fa_d,fa_d*.72,BLACK),(FA_R,'ForearmR',fa*.92,fa*.68,fa_d,fa_d*.72,BLACK),
 (TH_L,'ThighL',th*1.08,kn*.90,th_d,th_d*.78,SKIN),(TH_R,'ThighR',th*1.08,kn*.90,th_d,th_d*.78,SKIN),
 (SH_L,'ShinL',calf*.93,ank*.90,calf_d,ank_d,BLACK),(SH_R,'ShinR',calf*.93,ank*.90,calf_d,ank_d,BLACK)]:add_taper(group,name,r1,r2,d1,d2,mat)
# Soft junction volumes remove the detached mannequin-arm/thigh look while staying inside measured widths.
for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_sphere(group,'DeltoidBlend'+name,(0,-.430,0),(ua*.94,.075,ua_d*.96),SKIN,24,16)
for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_sphere(group,'HipThighBlend'+name,(0,-.430,0),(th*1.02,.082,th_d*.98),SKIN,26,16)
# Upper-arm straps + forearm gauntlets; narrow armor follows the limb instead of becoming the limb.
for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_cylinder(group,'UpperArmBand'+name,(0,-.26,0),ua*1.07,.070,BLACK,24);add_cylinder(group,'UpperArmBand2'+name,(0,-.13,0),ua*1.04,.045,SILVER,24)
for group,name in[(FA_L,'L'),(FA_R,'R')]:
 add_box(group,'ForearmPlate'+name,(0,.06,fa_d*.78),(fa*1.35,.43,fa_d*.52),WHITE,.014);add_box(group,'ForearmRail'+name,(0,.05,fa_d*1.08),(.018,.35,.012),SILVER,.005)
# Thigh-high boot begins below the garter line, preserving measured leg diameter.
for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_cylinder(group,'Garter'+name,(0,-.245,0),th*1.06,.048,BLACK,24)
 add_box(group,'GarterBuckle'+name,(th*.72,-.245,th_d*.74),(.024,.038,.018),SILVER,.004)
 add_box(group,'GarterTab'+name,(th*.70,-.185,th_d*.70),(.014,.090,.014),BLACK_SOFT,.003)
 add_cylinder(group,'ThighBootTop'+name,(0,.105,0),th*.96,.70,BLACK,28)
for group,name in[(SH_L,'L'),(SH_R,'R')]:
 add_box(group,'ShinPlate'+name,(0,.03,calf_d*.78),(calf*1.30,.50,calf_d*.44),BLACK_SOFT,.012);add_box(group,'ShinAccent'+name,(0,.06,calf_d*1.02),(.018,.40,.012),SILVER,.005)
for group,name in[(HAND_L,'L'),(HAND_R,'R')]:
 add_sphere(group,'Hand'+name,(0,0,0),(fa*.73,.078,fa_d*.66),BLACK,22,14);add_box(group,'HandPlate'+name,(0,.010,fa_d*.58),(fa*1.02,.068,.018),WHITE,.006)
# Reference heel silhouette: tapered toe, narrow ankle and separated rear heel.
for group,name in[(FOOT_L,'L'),(FOOT_R,'R')]:
 add_box(group,'ShoeBase'+name,(0,-.040,.085),(ank*1.72,.070,.220),BLACK,.018)
 add_box(group,'ToeCap'+name,(0,-.052,.195),(ank*1.60,.052,.095),WHITE,.012)
 add_box(group,'AnkleCuff'+name,(0,.055,.005),(ank*1.82,.095,.090),SILVER,.010)
 add_box(group,'Instep'+name,(0,.008,.085),(ank*1.52,.105,.105),BLACK_SOFT,.014,rot=(.16,0,0))
 add_box(group,'HeelStem'+name,(0,-.120,-.030),(ank*.34,.180,.032),BLACK,.006)
 add_box(group,'HeelTip'+name,(0,-.205,-.030),(ank*.46,.026,.042),SILVER,.004)
# Slim sword retained as a gameplay-readable prop.
add_box(SWORD,'SwordBlade',(0,.63,0),(.043,1.26,.018),WHITE,.008);add_box(SWORD,'SwordEdge',(.020,.65,.013),(.010,1.22,.010),GLOW,.003);add_box(SWORD,'SwordGuard',(0,-.03,0),(.245,.040,.085),SILVER,.012);add_cylinder(SWORD,'SwordGrip',(0,-.17,0),.026,.23,BLACK,20);add_box(SWORD,'SwordPommel',(0,-.31,0),(.050,.050,.050),SILVER,.009)

for o in[ROOT,PELVIS,TORSO,HEAD,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)

bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0]+'.blend')
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
print('Reference ratios:',{'H':H,'shoulder_half':DW['shoulder_joint_half_width'],'hip_half':DW['hip_joint_half_width'],'bust_w':round(bust_w,4),'waist_w':round(waist_w,4),'pelvis_w':round(pelvis_w,4)})
print('Wrote',OUT,os.path.getsize(OUT),'bytes')
