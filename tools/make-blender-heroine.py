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
SKIN=material('Skin',(0.60,0.41,0.39),0,.56)
BLACK=material('Suit Black',(0.014,0.018,0.027),.08,.30)
BLACK_SOFT=material('Suit Soft',(0.030,0.035,0.048),.02,.44)
WHITE=material('Porcelain White',(0.86,0.88,0.88),.18,.28)
SILVER=material('Silver',(0.50,0.53,0.56),.78,.19)
HAIR=material('Hair',(0.020,0.014,0.019),0.0,.54)
HAIR_HI=material('Hair Highlight',(0.070,0.045,0.052),0.0,.48)
# Reduce Principled specular so dark hair does not blow out to a silver ribbon under bright sky lighting.
for _hair_mat,_spec in ((HAIR,.14),(HAIR_HI,.18)):
 _bsdf=_hair_mat.node_tree.nodes.get('Principled BSDF')
 if _bsdf:
  _ior=_bsdf.inputs.get('Specular IOR Level')
  _old=_bsdf.inputs.get('Specular')
  if _ior:_ior.default_value=_spec
  elif _old:_old.default_value=_spec
SCLERA=material('Sclera',(0.76,0.72,0.69),0,.46)
IRIS=material('Iris',(0.10,0.067,0.055),.02,.30)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.34,0.16,0.17),0,.56)
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

def add_portrait_head_v44(p,name,sections,mat,segments=96):
 verts=[]
 for yy,w,back,front,zoff in sections:
  for i in range(segments):
   ang=2*math.pi*i/segments
   cs=math.cos(ang);sn=math.sin(ang)
   depth=front if sn>=0 else back
   x=cs*w
   z=zoff+sn*depth
   if sn>0:
    fm=sn**1.45
    # Temples tuck in while the upper cheekbone projects; this removes the round mask silhouette.
    for side in(-1,1):
     temple_x=side*head_w*.345
     z-=fm*.0068*math.exp(-((x-temple_x)/(head_w*.105))**2-((yy-.055)/.050)**2)
     cheek_x=side*head_w*.225
     z+=fm*.0145*math.exp(-((x-cheek_x)/(head_w*.105))**2-((yy+.010)/.040)**2)
     # Deep orbital bowl with a softer lower lid shelf.
     eye_x=side*head_w*.148
     z-=fm*.0205*math.exp(-((x-eye_x)/(head_w*.118))**2-((yy-.031)/.025)**2)
     z+=fm*.0048*math.exp(-((x-eye_x)/(head_w*.120))**2-((yy-.068)/.024)**2)
     z+=fm*.0030*math.exp(-((x-eye_x)/(head_w*.115))**2-((yy+.002)/.020)**2)
     # Lower-cheek hollow and nasolabial transition form a readable adult mid-face plane.
     z-=fm*.0048*math.exp(-((x-side*head_w*.275)/(head_w*.095))**2-((yy+.052)/.038)**2)
     z-=fm*.0022*math.exp(-((x-side*head_w*.105)/(head_w*.070))**2-((yy+.065)/.028)**2)
    # Continuous nose bridge, dorsum, tip and columella.
    z+=fm*.0100*math.exp(-(x/(head_w*.070))**2-((yy-.036)/.080)**2)
    z+=fm*.0180*math.exp(-(x/(head_w*.060))**2-((yy+.005)/.058)**2)
    z+=fm*.0410*math.exp(-(x/(head_w*.070))**2-((yy+.043)/.023)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.047))**2-((yy+.059)/.016)**2)
    # Soft muzzle and lip cushion, then a separate chin plane.
    z+=fm*.0065*math.exp(-(x/(head_w*.150))**2-((yy+.082)/.024)**2)
    z-=fm*.0028*math.exp(-(x/(head_w*.055))**2-((yy+.066)/.014)**2)
    z+=fm*.0105*math.exp(-(x/(head_w*.120))**2-((yy+.124)/.020)**2)
   verts.append(bpos((x,yy,z)))
 faces=[]
 for r in range(len(sections)-1):
  base=r*segments;nxt=(r+1)*segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((base+i,base+j,nxt+j,nxt+i))
 faces.append(tuple(range(segments-1,-1,-1)))
 last=(len(sections)-1)*segments;faces.append(tuple(last+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 # One subdivision pass softens ring transitions without erasing the sculpted planes.
 mod=o.modifiers.new('portrait_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)

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
# REFERENCE_V41: sculptural face, swept fringe and consolidated ponytail for a less procedural silhouette.
# REFERENCE_V42: portrait depth pass with volumetric lips, softer orbital detail and an offset rear ponytail.
# REFERENCE_V43: softer adult portrait, blunt side-swept fringe and a true side-flow ponytail.
# REFERENCE_V44: rebuilt portrait head topology, larger inset eyes and sheet-like swept bangs.
# REFERENCE_V45: safe layered lock fringe, warmer portrait materials and stronger eyes/lips.
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
add_portrait_head_v44(HEAD,'HeadShellV44',[
 (-.148,head_w*.050,head_d*.145,head_d*.188,.052),
 (-.137,head_w*.105,head_d*.190,head_d*.238,.047),
 (-.123,head_w*.190,head_d*.248,head_d*.302,.038),
 (-.105,head_w*.270,head_d*.302,head_d*.360,.028),
 (-.083,head_w*.335,head_d*.350,head_d*.414,.018),
 (-.058,head_w*.382,head_d*.390,head_d*.454,.009),
 (-.030,head_w*.414,head_d*.420,head_d*.480,.002),
 (.000,head_w*.434,head_d*.438,head_d*.492,-.003),
 (.030,head_w*.444,head_d*.450,head_d*.494,-.007),
 (.060,head_w*.438,head_d*.458,head_d*.480,-.011),
 (.090,head_w*.414,head_d*.456,head_d*.446,-.016),
 (.117,head_w*.372,head_d*.444,head_d*.400,-.022),
 (.140,head_w*.312,head_d*.420,head_d*.344,-.027),
 (.158,head_w*.225,head_d*.390,head_d*.282,-.030)
],SKIN,96)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.445,-.018,-.014),(.010,.023,.009),SKIN,18,10)
# Anatomy v4.4: portrait proportions matched to the key-art close-up.
face_front=head_d*.514
eye_y=.0320
eye_x=head_w*.145
eye_rx=head_w*.105
eye_ry=.0142
eye_tilt=.0034
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV44_{side}',(ex,eye_y,head_d*.420),(head_w*.083,.0175,head_d*.062),SCLERA,40,24)
 add_almond_surface(HEAD,f'EyeOpeningV44_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0026,SCLERA,44,side,eye_tilt)
 add_sphere(HEAD,f'IrisV44_{side}',(ex,eye_y+.0003,face_front+.0059),(head_w*.0480,.0108,.0030),IRIS,34,20)
 add_sphere(HEAD,f'PupilV44_{side}',(ex,eye_y+.0002,face_front+.0086),(head_w*.0142,.0051,.0019),PUPIL,24,14)
 add_sphere(HEAD,f'EyeLightV44_{side}',(ex-side*head_w*.0092,eye_y+.0052,face_front+.0106),(head_w*.0052,.0023,.0011),SCLERA,12,8)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV44_{side}',[(inner,inner_y+.0011,face_front+.0035),(ex,eye_y+.0143,face_front+.0059),(outer,outer_y+.0012,face_front+.0035)],.00066,SKIN)
 add_strand(HEAD,f'UpperLashV44_{side}',[(inner,inner_y+.0018,face_front+.0064),(ex,eye_y+.0148,face_front+.0080),(outer,outer_y+.0020,face_front+.0065)],.00078,HAIR)
 add_strand(HEAD,f'LashWingV44_{side}',[(outer,outer_y+.0020,face_front+.0065),(outer+side*head_w*.016,outer_y+.0065,face_front+.0070)],.00056,HAIR)
 add_strand(HEAD,f'BrowV44_{side}',[(ex-side*eye_rx*.82,.0680,head_d*.510),(ex,.0785,head_d*.516),(ex+side*eye_rx*1.02,.0660,head_d*.511)],.00108,HAIR)

# Small explicit nose pieces finish the profile; the main bridge and cheeks now come from the shell itself.
add_sphere(HEAD,'NoseTipV44',(0,-.0445,head_d*.553),(.0108,.0091,.0068),SKIN,28,16)
add_sphere(HEAD,'ColumellaV44',(0,-.0540,head_d*.548),(.0031,.0047,.0030),SKIN,18,10)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV44_{side}',(side*.0104,-.0505,head_d*.545),(.0052,.0047,.0037),SKIN,20,12)
 add_sphere(HEAD,f'NostrilV44_{side}',(side*.0072,-.0526,head_d*.550),(.00145,.0010,.00085),FACE_DARK,12,8)

# Two continuous almond surfaces give the soft, slightly parted key-art mouth without red point artifacts.
add_almond_surface(HEAD,'UpperLipV45',0,-.0810,head_d*.550,.0340,.0052,.0020,LIP,44,1,0.0)
add_almond_surface(HEAD,'LowerLipV45',0,-.0893,head_d*.549,.0315,.0060,.0023,LIP,44,1,0.0)
add_strand(HEAD,'MouthSeamV45',[(-.0290,-.0852,head_d*.552),(0,-.0864,head_d*.553),(.0290,-.0852,head_d*.552)],.00036,FACE_DARK)

# Hair v4.5: overlapping curved lock fringe using the proven local-space lock helper.
add_sphere(HEAD,'HairBackV45',(0,.032,-head_d*.366),(head_w*.510,.130,head_d*.456),HAIR,56,36)
add_sphere(HEAD,'HairCrownV45',(-.020,.120,-head_d*.205),(head_w*.474,.061,head_d*.325),HAIR,52,32)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV45_{side}',(side*head_w*.407,.021,-.030),(head_w*.080,.074,head_d*.132),HAIR,32,22)

# Six broad, overlapping masses form one continuous side-swept fringe. The final width deliberately
# remains 25-35% of the root width so no strand ends as a spike.
fringe=[
 (-.123,-.105,-.072,-.048,.058,.154,.052,.017),
 (-.098,-.074,-.038,-.008,.071,.160,.054,.017),
 (-.068,-.038,.000,.034,.083,.165,.053,.016),
 (-.034,.000,.042,.074,.079,.164,.052,.016),
 (.004,.040,.080,.105,.066,.159,.050,.015),
 (.044,.078,.112,.130,.048,.151,.046,.014),
]
for i,(rx,mx,cx,tx,ty,ry,w,tipw) in enumerate(fringe):
 pts=[
  (rx,ry,-head_d*.016),
  (mx,ry-.020,head_d*.165),
  (cx,.112,head_d*.355),
  (tx,ty,head_d*.516),
 ]
 add_lock_mesh(HEAD,f'ForeheadLockV45_{i}',pts,[w*.62,w,w*.70,tipw],[.0085,.0100,.0075,.0038],HAIR_HI if i in(0,5) else HAIR,10)

# Three shallower crossing locks hide root gaps and establish the diagonal part without forming bars.
for i,(rx,mx,tx,ty) in enumerate(((-.112,-.072,-.020,.077),(-.068,-.018,.048,.082),(-.012,.045,.112,.056))):
 pts=[(rx,.148,head_d*.008),(mx,.126,head_d*.265),((mx+tx)*.5,.101,head_d*.430),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'FringeLayerV45_{i}',pts,[.026,.030,.021,.009],[.0058,.0064,.0048,.0028],HAIR_HI if i==2 else HAIR,8)

# Fine edge wisps are sparse and follow the same sweep.
for i,(rx,tx,ty) in enumerate(((-.104,-.056,.066),(-.050,.018,.081),(.018,.094,.058))):
 add_strand(HEAD,f'BangWispV45_{i}',[(rx,.141,head_d*.014),((rx+tx)*.5,.112,head_d*.320),(tx,ty,head_d*.523)],.00048,HAIR_HI if i!=1 else HAIR)

for side in(-1,1):
 pts=[(side*head_w*.350,.087,-.010),(side*head_w*.397,.018,head_d*.068),(side*head_w*.410,-.130,head_d*.005),(side*head_w*.372,-.310,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV45_{side}',pts,[.020,.023,.014,.0045],[.0050,.0054,.0040,.0022],HAIR,8)
 add_strand(HEAD,f'FaceWispV45_{side}',[(side*head_w*.382,.074,-.006),(side*head_w*.425,-.030,head_d*.035),(side*head_w*.414,-.205,-.006),(side*head_w*.394,-.405,-.030)],.00050,HAIR_HI)

# True side-flow ponytail v4.3: seven broad locks bend right while staying behind the body.
add_sphere(HEAD,'PonyRootV43',(.036,.152,-head_d*.425),(.082,.064,.069),HAIR,34,24)
add_box(HEAD,'HairTieV43',(.040,.147,-head_d*.486),(.090,.022,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(7):
 lane=(i-3)/3
 zoff=((i%3)-1)*.010-.008*abs(lane)
 endx=.300+lane*.165
 pts=[
  (lane*.036+.036,.150,-head_d*.520+zoff),
  (lane*.050+.080,.030,-head_d*.765+zoff),
  (lane*.070+.145,-.245,-.555+zoff*.40),
  (lane*.090+.205,-.610,-.455),
  (lane*.110+.250,-1.000,-.360),
  (endx,-1.390,-.270),
  (endx+.035,-1.660-(i%3)*.018,-.190)
 ]
 base_w=.088-.016*abs(lane)
 add_lock_mesh(PONY,f'PonyLockV43_{i}',pts,[base_w*.70,base_w,base_w*1.04,base_w*.94,base_w*.72,base_w*.40,.0080],[.017,.020,.021,.018,.014,.009,.0040],HAIR_HI if i in(1,5) else HAIR,10)
for i in range(3):
 lane=(i-1)
 add_strand(PONY,f'PonyFlyV43_{i}',[(lane*.028+.036,.148,-head_d*.522),(lane*.045+.085,-.060,-head_d*.792),(lane*.070+.150,-.440,-.515),(lane*.100+.235,-.930,-.370),(lane*.120+.320,-1.645-(i%2)*.025,-.180)],.00066+(i%2)*.00008,HAIR_HI if i!=1 else HAIR)

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
