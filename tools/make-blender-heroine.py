import bpy, json, os, math

ROOT_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
OUT=os.path.join(ROOT_DIR,'dist','assets','models','heroine-blender.glb')
REF_PATH=os.path.join(ROOT_DIR,'tools','heroine-reference-proportions.json')
FACE75_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v75.json')
CC0_FACE_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-template-v1.json')
CC0_STATS_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-stats.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE75_PATH,'r',encoding='utf-8') as f:FACE75=json.load(f)
with open(CC0_FACE_PATH,'r',encoding='utf-8') as f:CC0_FACE=json.load(f)
with open(CC0_STATS_PATH,'r',encoding='utf-8') as f:CC0_STATS=json.load(f)
if CC0_FACE.get('version')!=2 or CC0_FACE.get('license')!='CC0-1.0':
 raise RuntimeError('v7.7 requires the local CC0 hm08 topology template v2')
H=float(REF['derived_world_units']['nominal_height'])
FW=REF['front_width_over_height'];SD=REF['side_depth_over_height'];DW=REF['derived_world_units']
W=lambda key:float(FW[key])*H
D=lambda key:float(SD[key])*H

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def bpos(v):x,y,z=v;return(x,-z,y)
def bscale(v):x,y,z=v;return(x,z,y)
def material(name,color,metallic=0.0,roughness=.45):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metallic;b.inputs['Roughness'].default_value=roughness;return m
SKIN=material('Skin',(0.36,0.235,0.215),0,.76)
BLACK=material('Suit Black',(0.014,0.018,0.027),.08,.30)
BLACK_SOFT=material('Suit Soft',(0.030,0.035,0.048),.02,.44)
WHITE=material('Porcelain White',(0.86,0.88,0.88),.18,.28)
SILVER=material('Silver',(0.50,0.53,0.56),.78,.19)
HAIR=material('Hair',(0.020,0.014,0.019),0.0,.54)
HAIR_HI=material('Hair Highlight',(0.045,0.029,0.036),0.0,.54)
# Reduce Principled specular so dark hair does not blow out to a silver ribbon under bright sky lighting.
for _hair_mat,_spec in ((HAIR,.14),(HAIR_HI,.18)):
 _bsdf=_hair_mat.node_tree.nodes.get('Principled BSDF')
 if _bsdf:
  _ior=_bsdf.inputs.get('Specular IOR Level')
  _old=_bsdf.inputs.get('Specular')
  if _ior:_ior.default_value=_spec
  elif _old:_old.default_value=_spec
SCLERA=material('Sclera',(0.50,0.485,0.475),0,.68)
IRIS=material('Iris',(0.072,0.050,0.047),.01,.58)
IRIS_INNER=material('Iris Inner',(0.125,0.086,0.078),.01,.60)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.34,0.120,0.140),0,.62)
FACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)
EAR_SHADOW=material('Ear Inner',(0.255,0.145,0.135),0,.78)
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
     z+=fm*.0125*math.exp(-((x-cheek_x)/(head_w*.112))**2-((yy+.010)/.045)**2)
     # Deep orbital bowl with a softer lower lid shelf.
     eye_x=side*head_w*.148
     z-=fm*.0165*math.exp(-((x-eye_x)/(head_w*.124))**2-((yy-.030)/.027)**2)
     z+=fm*.0048*math.exp(-((x-eye_x)/(head_w*.120))**2-((yy-.068)/.024)**2)
     z+=fm*.0030*math.exp(-((x-eye_x)/(head_w*.115))**2-((yy+.002)/.020)**2)
     # Lower-cheek hollow and nasolabial transition form a readable adult mid-face plane.
     z-=fm*.0048*math.exp(-((x-side*head_w*.275)/(head_w*.095))**2-((yy+.052)/.038)**2)
     z-=fm*.0022*math.exp(-((x-side*head_w*.105)/(head_w*.070))**2-((yy+.065)/.028)**2)
    # Continuous nose bridge, dorsum, tip and columella.
    z+=fm*.0065*math.exp(-(x/(head_w*.072))**2-((yy-.036)/.082)**2)
    z+=fm*.0105*math.exp(-(x/(head_w*.070))**2-((yy+.005)/.066)**2)
    z+=fm*.0165*math.exp(-(x/(head_w*.082))**2-((yy+.043)/.028)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.047))**2-((yy+.059)/.016)**2)
    # Soft muzzle and lip cushion, then a separate chin plane.
    z+=fm*.0075*math.exp(-(x/(head_w*.170))**2-((yy+.082)/.032)**2)
    z-=fm*.0028*math.exp(-(x/(head_w*.055))**2-((yy+.066)/.014)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.136))**2-((yy+.116)/.028)**2)
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


def add_almond_lens(p,name,cx,cy,cz,rx,ry,bulge,mat,rings=7,segments=48,side=1,tilt=0.0):
 verts=[bpos((cx,cy,cz+bulge))]
 for r in range(1,rings+1):
  f=r/rings
  z=cz+bulge*(1.0-f*f)
  for i in range(segments):
   a=2*math.pi*i/segments;ca=math.cos(a);sa=math.sin(a)
   x=cx+f*rx*ca
   yy=cy+f*ry*sa*(.68+.32*abs(ca))+f*tilt*side*ca
   verts.append(bpos((x,yy,z)))
 faces=[]
 for i in range(segments):faces.append((0,1+i,1+((i+1)%segments)))
 for r in range(rings-1):
  a=1+r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)

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

def add_fringe_surface_v85(p,name,pts,widths,lifts,mat,thickness=.0032):
 cols=9;fs=(-1.0,-.75,-.5,-.25,0.0,.25,.5,.75,1.0);verts=[];n=len(pts)
 for layer in (-.5,.5):
  for i,((x,y,z),w,lift) in enumerate(zip(pts,widths,lifts)):
   if i==0:tx,ty=pts[1][0]-x,pts[1][1]-y
   elif i==n-1:tx,ty=x-pts[i-1][0],y-pts[i-1][1]
   else:tx,ty=pts[i+1][0]-pts[i-1][0],pts[i+1][1]-pts[i-1][1]
   ln=max((tx*tx+ty*ty)**.5,1e-7);px,py=-ty/ln,tx/ln
   for f in fs:
    crown=max(0.0,1.0-abs(f)**1.55)
    edge_sink=.0012*(abs(f)**2)
    q=(x+px*w*.5*f,y+py*w*.5*f,z+lift*crown-edge_sink+layer*thickness)
    verts.append(bpos(q))
 faces=[];layer_count=n*cols
 # front/back grids
 for layer in range(2):
  off=layer*layer_count
  for r in range(n-1):
   a=off+r*cols;b=a+cols
   for c in range(cols-1):
    if layer==1:faces.append((a+c,a+c+1,b+c+1,b+c))
    else:faces.append((a+c,b+c,b+c+1,a+c+1))
 # close both long edges and both tips
 for r in range(n-1):
  a=r*cols;b=(r+1)*cols;aa=layer_count+a;bb=layer_count+b
  faces.append((a,b,bb,aa));a+=cols-1;b+=cols-1;aa+=cols-1;bb+=cols-1;faces.append((a,aa,bb,b))
 for c in range(cols-1):
  faces.append((c,layer_count+c,layer_count+c+1,c+1))
  a=(n-1)*cols+c;faces.append((a,a+1,layer_count+a+1,layer_count+a))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 # One Catmull-Clark pass converts the low-poly folded sheet into a continuous hair mass while
 # preserving enough edge definition for the side-swept silhouette. The denser cross-section above
 # prevents the broad triangular facets seen in the v8.5 five-view portrait audit.
 subd=o.modifiers.new('fringe_surface_smooth','SUBSURF');subd.subdivision_type='CATMULL_CLARK';subd.levels=1;subd.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=subd.name)
 bevel=o.modifiers.new('fringe_edge_soften','BEVEL');bevel.width=.0011;bevel.segments=2
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 return parent(o,p)

def add_temporal_shell_v92(p,name,side,rows,mat,arc_segments=16):
 # rows: (logical_y, half_width, depth, z_offset).  The shell spans only the side scalp:
 # front-temple -> true side -> rear-temple, never crossing the cheek or eye region.
 angles=[-1.12+1.28*i/arc_segments for i in range(arc_segments+1)]
 verts=[]
 for yy,w,d,zoff in rows:
  for a in angles:
   x=side*math.cos(a)*w
   z=zoff+math.sin(a)*d
   verts.append(bpos((x,yy,z)))
 row=len(angles);faces=[]
 for r in range(len(rows)-1):
  base=r*row;nxt=(r+1)*row
  for i in range(row-1):faces.append((base+i,base+i+1,nxt+i+1,nxt+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 # Give the scalp patch just enough physical thickness to render consistently from all audit views.
 solid=o.modifiers.new('temporal_shell_thickness','SOLIDIFY');solid.thickness=.0022;solid.offset=-.35
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
 sub=o.modifiers.new('temporal_shell_smooth','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=1;sub.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 return parent(o,p)

def add_temporal_leaf_v95(p,name,side,rows,mat,cols=7):
 # rows: (logical_y, scalp_x, center_z, half_depth, crown).  A tapered convex leaf follows
 # the side of the skull.  Its pointed ends and overlapping neighbors read as swept hair locks,
 # not a rectangular shell or a detached vertical sausage.
 fs=[-1.0+2.0*i/(cols-1) for i in range(cols)]
 verts=[]
 for yy,xbase,zc,half_depth,crown in rows:
  for f in fs:
   dome=max(0.0,1.0-f*f)
   x=side*(xbase+crown*dome)
   z=zc+half_depth*f
   verts.append(bpos((x,yy,z)))
 row=cols;faces=[]
 for r in range(len(rows)-1):
  a=r*row;b=(r+1)*row
  for i in range(row-1):faces.append((a+i,a+i+1,b+i+1,b+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 solid=o.modifiers.new('temporal_leaf_thickness','SOLIDIFY');solid.thickness=.0016;solid.offset=-.45
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
 sub=o.modifiers.new('temporal_leaf_smooth','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=1;sub.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 return parent(o,p)

def add_panel(p,name,points,depth,mat):
 front=[(x,y,z+depth*.5) for x,y,z in points];back=[(x,y,z-depth*.5) for x,y,z in points];verts=[bpos(v) for v in front+back];n=len(points);faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);return parent(o,p)
def add_strand(p,name,pts,radius,mat):
 c=bpy.data.curves.new(name+'Curve','CURVE');c.dimensions='3D';c.resolution_u=3;c.bevel_depth=radius;c.bevel_resolution=2;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for bp,q in zip(s.bezier_points,pts):bp.co=bpos(q);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.parent=p;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return o


def add_rear_hair_shell(p,name,sections,mat,segments=36):
 verts=[]
 # Logical Z is front/back; only sample the rear half of each horizontal section.
 angles=[math.pi-.34+(math.pi+.68)*i/segments for i in range(segments+1)]
 for yy,w,depth,zoff in sections:
  for ang in angles:
   verts.append(bpos((math.cos(ang)*w,yy,zoff+math.sin(ang)*depth)))
 row=len(angles);faces=[]
 for r in range(len(sections)-1):
  base=r*row;nxt=(r+1)*row
  for i in range(row-1):faces.append((base+i,base+i+1,nxt+i+1,nxt+i))
 # Close the wrapped temple boundaries and top/bottom openings; the expanded arc covers side scalp while leaving the central face open.
 left=[r*row for r in range(len(sections))];right=[r*row+row-1 for r in range(len(sections))]
 faces.append(tuple(left));faces.append(tuple(reversed(right)))
 faces.append(tuple(range(row-1,-1,-1)));last=(len(sections)-1)*row;faces.append(tuple(last+i for i in range(row)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('rear_hair_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)


def add_ellipse_surface(p,name,cx,cy,cz,rx,ry,mat,segments=40):
 verts=[bpos((cx,cy,cz))]
 for i in range(segments):
  a=2*math.pi*i/segments
  verts.append(bpos((cx+rx*math.cos(a),cy+ry*math.sin(a),cz)))
 faces=[(0,1+i,1+((i+1)%segments)) for i in range(segments)]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)


def add_smooth_lock(p,name,pts,widths,depths,mat,ring_segments=12,samples=5):
 out=[];ow=[];od=[];n=len(pts)
 for i in range(n-1):
  p0=pts[max(0,i-1)];p1=pts[i];p2=pts[i+1];p3=pts[min(n-1,i+2)]
  for j in range(samples):
   t=j/samples;t2=t*t;t3=t2*t
   q=[]
   for k in range(3):
    q.append(.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t3))
   out.append(tuple(q));ow.append(widths[i]*(1-t)+widths[i+1]*t);od.append(depths[i]*(1-t)+depths[i+1]*t)
 out.append(pts[-1]);ow.append(widths[-1]);od.append(depths[-1])
 return add_lock_mesh(p,name,out,ow,od,mat,ring_segments)


def add_face_patch_v54(p,name,rows,mat,cols=40):
 verts=[]
 for yy,half_w,front_z,edge_z in rows:
  for j in range(cols+1):
   u=-1.0+2.0*j/cols
   x=u*half_w
   blend=max(0.0,1.0-u*u)**0.62
   z=edge_z+(front_z-edge_z)*blend+.0012
   # Adult facial planes: cheekbone, orbital bowl and lower-cheek break.
   for side in (-1,1):
    ex=side*head_w*.147
    z-=.0066*math.exp(-((x-ex)/(head_w*.086))**2-((yy-.030)/.021)**2)
    cx=side*head_w*.205
    z+=.0058*math.exp(-((x-cx)/(head_w*.105))**2-((yy+.004)/.040)**2)
    z-=.0026*math.exp(-((x-side*head_w*.255)/(head_w*.105))**2-((yy+.058)/.038)**2)
   # Central profile is intentionally narrow; the row profile supplies most of the depth.
   z+=.0060*math.exp(-(x/(head_w*.062))**2-((yy-.006)/.055)**2)
   z+=.0170*math.exp(-(x/(head_w*.065))**2-((yy+.043)/.019)**2)
   z-=.0030*math.exp(-(x/(head_w*.055))**2-((yy+.061)/.013)**2)
   z+=.0035*math.exp(-(x/(head_w*.145))**2-((yy+.081)/.018)**2)
   z+=.0038*math.exp(-(x/(head_w*.118))**2-((yy+.116)/.020)**2)
   verts.append(bpos((x,yy,z)))
 row=cols+1;faces=[]
 for r in range(len(rows)-1):
  a=r*row;b=(r+1)*row
  for j in range(cols):
   faces.append((a+j,a+j+1,b+j+1,b+j))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('face_patch_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)


def add_profile_head_v55(p,name,rows,mat,segments=96):
 # rows: logical_y, half_width, back_depth, front_depth. A single closed surface owns the entire head.
 verts=[]
 for yy,w,back,front in rows:
  for i in range(segments):
   ang=2*math.pi*i/segments;cs=math.cos(ang);sn=math.sin(ang)
   x=cs*w
   z=sn*(front if sn>=0 else back)
   if sn>0:
    fm=sn**1.55
    # Orbital recess, brow plane and cheekbone support.
    for side in (-1,1):
     ex=side*head_w*.147
     z-=fm*.0078*math.exp(-((x-ex)/(head_w*.082))**2-((yy-.030)/.021)**2)
     z+=fm*.0030*math.exp(-((x-ex)/(head_w*.105))**2-((yy-.063)/.024)**2)
     cx=side*head_w*.205
     z+=fm*.0052*math.exp(-((x-cx)/(head_w*.105))**2-((yy+.004)/.040)**2)
     z-=fm*.0022*math.exp(-((x-side*head_w*.255)/(head_w*.105))**2-((yy+.058)/.038)**2)
    # Narrow bridge and tip reinforce the explicit centre-line profile without inflating the whole muzzle.
    z+=fm*.0042*math.exp(-(x/(head_w*.062))**2-((yy-.002)/.052)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.062))**2-((yy+.043)/.018)**2)
    z-=fm*.0028*math.exp(-(x/(head_w*.052))**2-((yy+.061)/.012)**2)
    z+=fm*.0024*math.exp(-(x/(head_w*.142))**2-((yy+.082)/.018)**2)
    z+=fm*.0030*math.exp(-(x/(head_w*.118))**2-((yy+.116)/.019)**2)
   verts.append(bpos((x,yy,z)))
 faces=[]
 for r in range(len(rows)-1):
  a=r*segments;b=(r+1)*segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 faces.append(tuple(range(segments-1,-1,-1)))
 last=(len(rows)-1)*segments;faces.append(tuple(last+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('profile_head_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)


def sample_face_profile_v75(yy):
 pts=FACE75['profile_curve']
 if yy>=pts[0]['y']:
  return pts[0]['front_z'],pts[0]['half_width']
 if yy<=pts[-1]['y']:
  return pts[-1]['front_z'],pts[-1]['half_width']
 for a,b in zip(pts,pts[1:]):
  if a['y']>=yy>=b['y']:
   t=(a['y']-yy)/max(a['y']-b['y'],1e-8)
   t=t*t*(3.0-2.0*t)
   z=a['front_z']*(1-t)+b['front_z']*t
   w=a['half_width']*(1-t)+b['half_width']*t
   return z,w
 return .097,.04

def sample_cc0_front_v77(yn):
 pts=CC0_STATS['patch']['profile_samples_normalized']
 if yn<=pts[0]['y']: return pts[0]['front_z']-.5
 if yn>=pts[-1]['y']: return pts[-1]['front_z']-.5
 for a,b in zip(pts,pts[1:]):
  if a['y']<=yn<=b['y']:
   t=(yn-a['y'])/max(b['y']-a['y'],1e-8)
   t=t*t*(3-2*t)
   return (a['front_z']*(1-t)+b['front_z']*t)-.5
 return 0.0

def add_cc0_face_patch_v77(p,name,mat):
 # CC0 supplies only topology/local relief. Heroine reference controls size, eye spacing and centre-line profile.
 verts=[]
 for vx,vy,vz in CC0_FACE['vertices']:
  yn=max(0.0,min(1.0,vy+.5))
  yy=-.145+yn*.305
  # 0.245 total mapping gives a slim 0.1225 half-face; taper the lower third into the reference V jaw.
  jaw_t=max(0.0,min(1.0,(-.025-yy)/.120))
  x=vx*.238*(1.0-.175*jaw_t)
  # Anime-reference eye spacing: spread the orbital band without widening cheeks/jaw globally.
  orbital=math.exp(-((yy-.031)/.035)**2)
  x+=math.copysign(.0076*orbital*max(0.0,1.0-abs(x)/.119),x) if abs(x)>1e-8 else 0.0
  # Lock the foremost profile at every height to v7.5+, then transfer only CC0's local rearward relief.
  pz,_=sample_face_profile_v75(yy)
  generic_front=sample_cc0_front_v77(yn)
  local_relief=(vz-generic_front)*.050
  # Reduce generic relief near the outer seam so it blends gently into the recessed UV cranium.
  seam=max(0.0,min(1.0,(.126-abs(x))/.040))
  relief_gain=.62+.38*seam
  z=pz+local_relief*relief_gain+.0016
  bridge_lat=math.exp(-(x/.030)**2)
  tip_lat=math.exp(-(x/.0215)**2)
  z+=.0024*bridge_lat*math.exp(-((yy+.006)/.052)**2)
  z+=.0022*tip_lat*math.exp(-((yy+.045)/.0195)**2)
  verts.append(bpos((x,yy,z)))
 faces=[tuple(f) for f in CC0_FACE['faces']]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)

def add_anime_head_v60(p,name,mat,segments=96,rings=48):
 # Smooth UV topology replaces row-profile rings that produced horizontal shading bands.
 verts=[]
 top=bpos((0,.179,0));bottom=bpos((0,-.157,0));verts.append(top)
 for r in range(1,rings):
  theta=math.pi*r/rings
  sy=math.cos(theta);rad=math.sin(theta)
  yy=.011+.168*sy
  # Adult/anime silhouette: broad cranium, tapered lower cheek and compact chin.
  lower=max(0.0,min(1.0,(-.030-yy)/.120))
  cheek=math.exp(-((yy+.010)/.060)**2)
  width=.1285*(1.0-.385*lower+.034*cheek)
  for i in range(segments):
   phi=2*math.pi*i/segments
   cp=math.cos(phi);sp=math.sin(phi)
   x=width*rad*cp
   depth=(.103 if sp<0 else .0975)*rad
   z=depth*sp
   if sp>0:
    fm=sp**2.0
    # CC0-informed facial plane: distribute the front surface through neighboring vertices instead of
    # leaving the cheeks on a spherical dome. This stabilizes the same silhouette in front, 3/4 and profile.
    face_band=math.exp(-((yy+.030)/.125)**4)
    plane_lat=1.0/(1.0+(abs(x)/.095)**6)
    front_plane=depth*.985
    z+=fm*face_band*plane_lat*(front_plane-z)*.62
    # Recess the eye sockets while supporting the zygomatic plane.
    for side in (-1,1):
     ex=side*.0470
     z-=fm*.0058*math.exp(-((x-ex)/.026)**2-((yy-.033)/.022)**2)
     z+=fm*.0044*math.exp(-((x-side*.054)/.035)**2-((yy+.004)/.040)**2)
    # v7.5: absolute centre-line target plus a broad CC0-like lateral falloff.
    # Using an absolute front Z compensates the UV sphere's severe lower-face recession at the chin.
    pz,pw=sample_face_profile_v75(yy)
    lateral=1.0/(1.0+(abs(x)/max(pw,1e-5))**4)
    z+=fm*(pz-depth)*lateral
    # v7.7 hybrid: keep this surface as cranium/backing but place it safely behind the local quad face patch.
    patch_y=1.0-max(0.0,min(1.0,abs(yy-.005)/.170))
    patch_x=max(0.0,min(1.0,(.132-abs(x))/.030))
    z-=fm*.0135*patch_y*patch_x
   verts.append(bpos((x,yy,z)))
 bottom_idx=len(verts);verts.append(bottom)
 faces=[]
 first=1
 for i in range(segments):faces.append((0,first+i,first+(i+1)%segments))
 for r in range(rings-2):
  a=1+r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 last=1+(rings-2)*segments
 for i in range(segments):faces.append((last+i,bottom_idx,last+(i+1)%segments))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)

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
# REFERENCE_V46: cinematic almond eyes, readable nasal bridge and fuller natural mouth.
# REFERENCE_V47: reference-silhouette face, softer hourglass torso and fuller layered hair.
# REFERENCE_V48: unified hair cap, sheet fringe, iris-dominant eyes and rebuilt side-profile depth.
# REFERENCE_V49: skull-hugging hair, vertical pony cascade, readable warm irises and stronger profile.
# REFERENCE_V50: open rear hair shell, readable portrait eyes, softer profile and connected shoulders.
# REFERENCE_V51: explicit iris discs, asymmetric fringe and smoother pony flow.
# REFERENCE_V52: Catmull-smoothed pony, broad swept fringe and larger dark-brown eyes.
# REFERENCE_V53: embedded portrait features, realistic iris scale, unified fringe and soft profile.
# REFERENCE_V54: dedicated facial surface patch, explicit profile landmarks and unified fringe mass.
# REFERENCE_V55: single closed profile head, recessed orbits and scalp-covered swept hair.
# REFERENCE_V56: cleaner adult profile, visible almond eyes and eyebrow-clear swept fringe.
# REFERENCE_V57: expressive realistic-anime eyes, tapered lower face and filled side-swept hairline.
# REFERENCE_V58: reference body volume, layered rounded fringe and larger portrait eyes.
# REFERENCE_V59: broad swept fringe, full high pony cascade and softer human limb volume.
# REFERENCE_V60: stable UV portrait head, continuous facial planes and restrained adult profile.
# REFERENCE_V61: expressive larger eyes, tapered jaw and restrained explicit nose/lip profile.
# REFERENCE_V62: cinematic almond gaze, warm skin response and subtle readable side-profile nose.
# REFERENCE_V63: layered grey-brown irises, smaller pupils and fine separated portrait fringe.
# REFERENCE_V64: readable soft grey-brown gaze and continuous restrained nose-lip-chin profile.
# REFERENCE_V65: reference silhouette limb volume, readable warm skin and overlapping pony foundation mass.
# REFERENCE_V66: surfaced bust contour, visible white bodice couture and fanned pony flow.
# REFERENCE_V67: integrated bust contour, upper-chest couture wings, almond gaze and wide high-pony silhouette.
# REFERENCE_V68: layered porcelain torso shell, narrow black corset centre and natural portrait eye spacing.
# REFERENCE_V69: sculpted adult-anime portrait planes, tapered jaw and restrained continuous profile.
# REFERENCE_V70: volumetric portrait eyes, unified nose form and curved natural lips.
# REFERENCE_V71: multiview-constrained integrated face surface, embedded eyes and surface-following lip tint.
# REFERENCE_V72: smooth 3D almond sclera lens, stronger integrated S-profile and three-quarter-safe portrait proportions.
# REFERENCE_V73: CC0-topology-informed continuous profile depth and fully exposed almond eye aperture.
# REFERENCE_V74: data-driven single profile spline, flush mouth tint and five-view consistency.
# REFERENCE_V75: CC0-informed facial plane, absolute profile cage, single iris and flush two-volume lips.
# REFERENCE_V76: covered hairline, slimmer V-face, wider almond gaze and sculpted Cupid lips.
# REFERENCE_V77: pinned-CC0 quad topology hybrid face retargeted to the PARRY DOLL multiview profile.
# REFERENCE_V78: narrower mature face, wider almond gaze, fuller sculpted lips and cleaner swept hairline.
# REFERENCE_V79: embedded eyes, stronger adult nose bridge, integrated lips and an open asymmetric fringe.
# REFERENCE_V80: mature flush almond eyes, softened centre profile and rounded side-swept hair masses.
# REFERENCE_V81: clean cheek silhouette, lifted side wisps and sealed crown root for production portrait readability.
# REFERENCE_V82: artifact-free cheeks, no detached side strands and a front-visible overlapping crown seal.
# REFERENCE_V83: +10% mature almond aperture, lower side-swept fringe and clean temple silhouette.
# REFERENCE_V84: overlap-closed front fringe with the v8.3 face and eye proportions frozen.
# REFERENCE_V85: scalp-hugging convex fringe surfaces replace the braided/tubular front locks.
# REFERENCE_V86: high-sample Catmull-Clark fringe surfaces for smooth production hair silhouette.
# REFERENCE_V87: unified two-layer side sweep; crown root folded into the main fringe instead of a third fin.
# REFERENCE_V88: tapered-root side sweep over a scalp-tight undercap, eliminating the v8.7 crown fin and skin notch.
# REFERENCE_V89: zero-width fringe roots plus rounded scalp blends remove closed-end fins and the last hairline notch.
# REFERENCE_V90: crown-buried zero-width roots replace filler blobs and create continuous hair-cap/fringe overlap.
# REFERENCE_V91: fuller upper crown cap wraps the buried roots and removes the remaining 3/4 scalp stripe.
# REFERENCE_V92: dedicated scalp-hugging temporal shells bridge fringe to rear hair above the ears without cheek wisps.
# REFERENCE_V93: rear-biased lower temporal shells cover the ear-zone scalp while preserving the cheek and eye silhouette.
# REFERENCE_V94: smooth elliptical side locks replace the rectangular temporal sheets and cover the ear-zone scalp naturally.
# REFERENCE_V95: three tapered convex scalp leaves per side replace the detached ear-pad lock with a continuous swept temple-to-rear flow.
# REFERENCE_V96: anatomically readable ears and unified temporal-hair tone make the remaining exposed side skin intentional rather than bald.
# REFERENCE_V97: rear hair shell wraps forward around both temples; duplicate v9.6 ears are removed while the original EarV78 anatomy remains.
# REFERENCE_V98: a hidden convex temporal root underlay fills the fringe-to-side-lock scalp gap while preserving the canonical ears.
# REFERENCE_V99: side-hair roots stay substantial through the ear line, then taper behind the jaw instead of opening a large bare temporal patch.
# REFERENCE_V100: adult portrait reset reduces oversized doll eyes and tightens the lower-face silhouette while preserving the established profile and hair.
# REFERENCE_V101: side hair becomes a scalp-tight undercap plus several rounded swept locks, replacing the large profile-facing leaf plate.
# REFERENCE_V102: temporal lock tips sweep rearward around the ear instead of dropping into straight claw-like prongs.
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope as a single continuous surface.
# Front depth peaks at the bust while the lower back eases toward the high waist, matching the side sheet.
add_section_mesh(TORSO,'TorsoSuitV58',[
 (-.340,waist_w*.430,waist_d*.46,waist_d*.54,-.006),
 (-.285,waist_w*.415,waist_d*.45,waist_d*.55,-.004),
 (-.220,waist_w*.455,waist_d*.45,waist_d*.58,-.001),
 (-.150,bust_w*.350,bust_d*.40,bust_d*.52,.005),
 (-.075,bust_w*.445,bust_d*.41,bust_d*.61,.015),
 (.000,bust_w*.535,bust_d*.43,bust_d*.705,.030),
 (.075,bust_w*.580,bust_d*.45,bust_d*.770,.044),
 (.135,bust_w*.565,bust_d*.45,bust_d*.735,.041),
 (.195,bust_w*.480,bust_d*.42,bust_d*.610,.026),
 (.255,bust_w*.392,bust_d*.37,bust_d*.470,.011),
 (.315,bust_w*.300,bust_d*.31,bust_d*.350,.000)
],BLACK,56)
# Shallow soft-tissue support over a continuous ribcage. The outer envelope remains reference-locked.
for side in(-1,1):
 add_sphere(TORSO,f'BustContourV68_{side}',(side*bust_w*.175,.102,bust_d*.676),(bust_w*.155,.058,bust_d*.072),BLACK_SOFT,44,28)
add_box(TORSO,'UnderBustLine',(0,.020,bust_d*.505),(bust_w*.70,.014,.009),SILVER,.003)
for side in(-1,1):
 add_box(TORSO,f'WaistContour_{side}',(side*waist_w*.44,-.150,waist_d*.50),(.012,.175,.009),SILVER,.0035,rot=(0,0,-side*.15))
# Anatomical clavicle/deltoid bridge inside the measured shoulder envelope.
for side in(-1,1):
 add_sphere(TORSO,f'DeltoidBridgeV50_{side}',(side*bust_w*.415,.238,.002),(bust_w*.126,.062,bust_d*.142),BLACK,34,22)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.285,.258,bust_d*.28),(side*bust_w*.475,.225,bust_d*.18),(side*bust_w*.275,.210,bust_d*.31)],.013,BLACK_SOFT)
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
add_panel(TORSO,'BodiceWhiteV66_L',[(-bust_w*.455,.218,bust_d*.600),(-bust_w*.255,.190,bust_d*.640),(-waist_w*.245,-.190,waist_d*.720),(-waist_w*.520,-.225,waist_d*.640)],.010,WHITE)
add_panel(TORSO,'BodiceWhiteV66_R',[(bust_w*.255,.190,bust_d*.640),(bust_w*.455,.218,bust_d*.600),(waist_w*.520,-.225,waist_d*.640),(waist_w*.245,-.190,waist_d*.720)],.010,WHITE)
for side in(-1,1):
 add_box(TORSO,f'BodiceEdgeV66_{side}',(side*bust_w*.275,.030,bust_d*.670),(.012,.330,.009),SILVER,.0035,rot=(0,0,side*.08))
 add_box(TORSO,f'UpperArmBandV35_{side}',(side*.205,.215,.000),(.040,.020,.072),BLACK,.004)

# v6.7 upper-chest panels sit on the true front envelope and taper into the narrow waist.
add_panel(TORSO,'ChestWingV67_L',[(-bust_w*.505,.248,bust_d*.455),(-bust_w*.245,.226,bust_d*.595),(-bust_w*.205,.080,bust_d*.790),(-bust_w*.465,.066,bust_d*.690)],.012,WHITE)
add_panel(TORSO,'ChestWingV67_R',[(bust_w*.245,.226,bust_d*.595),(bust_w*.505,.248,bust_d*.455),(bust_w*.465,.066,bust_d*.690),(bust_w*.205,.080,bust_d*.790)],.012,WHITE)
add_panel(TORSO,'WaistWingV67_L',[(-bust_w*.455,.060,bust_d*.675),(-bust_w*.205,.076,bust_d*.790),(-waist_w*.235,-.205,waist_d*.760),(-waist_w*.545,-.232,waist_d*.655)],.011,WHITE)
add_panel(TORSO,'WaistWingV67_R',[(bust_w*.205,.076,bust_d*.790),(bust_w*.455,.060,bust_d*.675),(waist_w*.545,-.232,waist_d*.655),(waist_w*.235,-.205,waist_d*.760)],.011,WHITE)
for side in(-1,1):
 add_box(TORSO,f'ChestSeamV67_{side}',(side*bust_w*.245,.120,bust_d*.785),(.010,.205,.010),SILVER,.0032,rot=(0,0,side*.11))

# v6.8 porcelain shell covers the old black capsule; a narrow black centre panel restores the reference couture contrast.
add_panel(TORSO,'PorcelainShellV68_L',[(-bust_w*.520,.250,bust_d*.485),(-bust_w*.115,.226,bust_d*.690),(-bust_w*.095,.072,bust_d*.875),(-waist_w*.105,-.188,waist_d*.905),(-waist_w*.535,-.238,waist_d*.735),(-bust_w*.500,.058,bust_d*.750)],.013,WHITE)
add_panel(TORSO,'PorcelainShellV68_R',[(bust_w*.115,.226,bust_d*.690),(bust_w*.520,.250,bust_d*.485),(bust_w*.500,.058,bust_d*.750),(waist_w*.535,-.238,waist_d*.735),(waist_w*.105,-.188,waist_d*.905),(bust_w*.095,.072,bust_d*.875)],.013,WHITE)
add_panel(TORSO,'CenterCorsetV68',[(-bust_w*.135,.235,bust_d*.730),(bust_w*.135,.235,bust_d*.730),(bust_w*.205,.070,bust_d*.915),(waist_w*.125,-.205,waist_d*.970),(-waist_w*.125,-.205,waist_d*.970),(-bust_w*.205,.070,bust_d*.915)],.014,BLACK)
add_panel(TORSO,'CenterCorsetInlayV68',[(-bust_w*.045,.215,bust_d*.748),(bust_w*.045,.215,bust_d*.748),(bust_w*.060,.050,bust_d*.935),(waist_w*.038,-.185,waist_d*.990),(-waist_w*.038,-.185,waist_d*.990),(-bust_w*.060,.050,bust_d*.935)],.008,BLACK_SOFT)
for side in(-1,1):
 add_box(TORSO,f'CorsetTrimV68_{side}',(side*bust_w*.150,.035,bust_d*.920),(.008,.330,.008),SILVER,.0028,rot=(0,0,side*.055))

# Compact pelvis and high waist: measured 0.123H width and 0.089H depth.
add_section_mesh(PELVIS,'PelvisSuitV47',[
 (-.180,pelvis_w*.445,pelvis_d*.62,pelvis_d*.51,-.018),
 (-.080,pelvis_w*.555,pelvis_d*.60,pelvis_d*.56,-.011),
 (.040,pelvis_w*.540,pelvis_d*.54,pelvis_d*.55,-.004),
 (.155,waist_w*.545,waist_d*.55,waist_d*.60,0.000)
],BLACK,44)
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
# v6.0 uses one dense UV surface. Facial depth is deliberately restrained to avoid the v5.x muzzle/nose blowout.
add_anime_head_v60(HEAD,'HeadShellV60',SKIN,96,48)
add_cc0_face_patch_v77(HEAD,'FaceQuadPatchV77',SKIN)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'EarV78_{side}',(side*.121,-.018,-.012),(.0085,.0205,.0078),SKIN,20,12)

# v10.0 adult-scale almond eyes: narrower apertures, lower iris coverage and subtler lids remove the child/doll read.
face_front=.0974
eye_y=.0330
eye_x=.0465
eye_rx=.0262
eye_ry=.0099
eye_tilt=.0018
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV100_{side}',ex,eye_y,.1030,.0288,.0097,.00115,SCLERA,72,side,eye_tilt*.70)
 add_ellipse_surface(HEAD,f'IrisV100_{side}',ex,eye_y,.10430,.0094,.0078,IRIS_INNER,40)
 add_ellipse_surface(HEAD,f'PupilV100_{side}',ex,eye_y-.00015,.10466,.00285,.00345,PUPIL,30)
 add_ellipse_surface(HEAD,f'EyeLightV100_{side}',ex-side*.0030,eye_y+.0028,.10488,.00090,.00072,SCLERA,16)
 inner=ex-side*eye_rx*.96;outer=ex+side*eye_rx*1.03
 add_strand(HEAD,f'UpperLashV100_{side}',[(inner,eye_y-eye_tilt+.0006,.10395),(ex,eye_y+.0101,.10450),(outer,eye_y+eye_tilt+.0006,.10400)],.00054,HAIR)
 add_strand(HEAD,f'UpperLidFoldV100_{side}',[(inner+side*.0035,eye_y-eye_tilt+.0025,.10350),(ex,eye_y+.0124,.10392),(outer-side*.0035,eye_y+eye_tilt+.0025,.10350)],.00014,FACE_DARK)
 add_strand(HEAD,f'LowerLidV100_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0001,.10342),(ex,eye_y-.0072,.10368),(outer-side*.0035,eye_y+eye_tilt-.0001,.10342)],.000052,FACE_DARK)
 add_strand(HEAD,f'BrowV100_{side}',[(ex-side*.0235,.0645,.1018),(ex,.0698,.1023),(ex+side*.0255,.0630,.1019)],.00038,HAIR)

# v7.1 integrated portrait accents: head topology owns all nose/mouth depth.
# Only a shallow colour patch remains for the lips, following the actual mouth plane instead of floating in front of it.
add_panel(HEAD,'UpperLipV80_L',[(-.0225,-.0848,.1095),(-.0110,-.0802,.1101),(0,-.0833,.1107),(0,-.0867,.1108),(-.0095,-.0859,.1105),(-.0210,-.0880,.1099)],.00030,LIP)
add_panel(HEAD,'UpperLipV80_R',[(0,-.0833,.1107),(.0110,-.0802,.1101),(.0225,-.0848,.1095),(.0210,-.0880,.1099),(.0095,-.0859,.1105),(0,-.0867,.1108)],.00030,LIP)
add_panel(HEAD,'LowerLipV80',[(-.0210,-.0882,.1100),(0,-.0876,.1108),(.0210,-.0882,.1100),(.0178,-.0942,.1099),(0,-.0969,.1103),(-.0178,-.0942,.1099)],.00034,LIP)
add_strand(HEAD,'MouthSeamV80',[(-.0215,-.0867,.1099),(-.0100,-.0862,.1105),(0,-.0870,.1109),(.0100,-.0862,.1105),(.0215,-.0867,.1099)],.000038,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV76_{side}',side*.0056,-.0570,.1157,.00145,.00052,FACE_DARK,16)

# v9.7: EarV78 is the single canonical ear set; no duplicate side anatomy is added here.

# Hair v5.9: broad layered side sweep with an open eye line, plus a much fuller high pony cascade.
add_section_mesh(HEAD,'HairTopCapV91',[
 (.064,head_w*.452,head_d*.442,head_d*.492,-.018),
 (.098,head_w*.448,head_d*.436,head_d*.486,-.020),
 (.133,head_w*.414,head_d*.404,head_d*.452,-.021),
 # v9.1 keeps crown width longer instead of collapsing into a narrow cone above the forehead.
 (.164,head_w*.356,head_d*.342,head_d*.390,-.018),
 (.189,head_w*.258,head_d*.242,head_d*.286,-.010),
 (.204,head_w*.142,head_d*.126,head_d*.158,-.002),
 (.213,head_w*.052,head_d*.048,head_d*.060,.002)
],HAIR,64)
add_rear_hair_shell(HEAD,'HairRearShellV59',[
 (-.025,head_w*.300,head_d*.410,-head_d*.066),
 (.012,head_w*.430,head_d*.500,-head_d*.058),
 (.052,head_w*.505,head_d*.550,-head_d*.050),
 (.096,head_w*.528,head_d*.562,-head_d*.042),
 (.138,head_w*.490,head_d*.517,-head_d*.033),
 (.170,head_w*.394,head_d*.422,-head_d*.024),
 (.194,head_w*.230,head_d*.270,-head_d*.013),
 (.206,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,44)

# v10.1: a scalp-tight undercap provides dark root coverage without becoming the visible silhouette.
# head_w is the full measured head width, so ~0.46*head_w tracks the actual cranium instead of floating far outside it.
for side in (-1,1):
 add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV101_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.442, head_d*.012,.032,.0012),
  (.098,head_w*.462, head_d*.000,.041,.0015),
  (.068,head_w*.468,-head_d*.014,.043,.0016),
  (.039,head_w*.465,-head_d*.028,.038,.0014),
  (.014,head_w*.455,-head_d*.041,.028,.0011),
  (-.004,head_w*.442,-head_d*.050,.016,.0008),
  (-.014,head_w*.430,-head_d*.055,.004,.0003)
 ],HAIR,15)

 # Rounded swept locks sit above the undercap. Each covers only a narrow front/back band, so profile reads as layered hair.
 add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.026),
  (side*head_w*.420,.145, head_d*.018),
  (side*head_w*.468,.108, head_d*.006),
  (side*head_w*.486,.068,-head_d*.010),
  (side*head_w*.482,.028,-head_d*.027),
  (side*head_w*.468,.010,-head_d*.050),
  (side*head_w*.442,-.004,-head_d*.075)
 ],[.003,.006,.009,.010,.0085,.005,.0012],[.007,.012,.016,.019,.015,.009,.0028],HAIR,14,6)

 add_smooth_lock(HEAD,f'TemporalLockV101_Mid_{side}',[
  (side*head_w*.344,.170,-head_d*.030),
  (side*head_w*.410,.139,-head_d*.041),
  (side*head_w*.462,.101,-head_d*.056),
  (side*head_w*.490,.059,-head_d*.073),
  (side*head_w*.489,.016,-head_d*.091),
  (side*head_w*.474,.002,-head_d*.122),
  (side*head_w*.446,-.010,-head_d*.151)
 ],[.003,.006,.009,.011,.009,.0055,.0012],[.008,.014,.019,.022,.018,.011,.0032],HAIR,14,6)

 add_smooth_lock(HEAD,f'TemporalLockV101_Rear_{side}',[
  (side*head_w*.332,.164,-head_d*.082),
  (side*head_w*.392,.132,-head_d*.096),
  (side*head_w*.448,.094,-head_d*.113),
  (side*head_w*.480,.051,-head_d*.132),
  (side*head_w*.482,.008,-head_d*.151),
  (side*head_w*.466,-.004,-head_d*.184),
  (side*head_w*.438,-.016,-head_d*.211)
 ],[.003,.006,.009,.011,.009,.0055,.0012],[.008,.014,.020,.023,.018,.011,.0032],HAIR,14,6)

 # One very fine highlight follows the flow; no whole lock is tinted brown.
 add_strand(HEAD,f'TemporalFlowV101_{side}',[
  (side*head_w*.445,.142,-head_d*.055),
  (side*head_w*.482,.090,-head_d*.078),
  (side*head_w*.488,.036,-head_d*.101),
  (side*head_w*.472,.004,-head_d*.128),
  (side*head_w*.443,-.012,-head_d*.156)
 ],.000032,HAIR_HI)

# v9.0: the fringe is born inside the existing crown cap instead of being patched to it with blobs.
# The first two samples are narrow and hidden under the cap; width only opens after the path exits the crown.
add_fringe_surface_v85(HEAD,'FringeSurfaceV90_Main',[(-.008,.214,.004),(-.028,.207,.019),(-.050,.199,.036),(-.070,.188,.053),(-.076,.174,.070),(-.057,.157,.087),(-.025,.139,.101),(.012,.122,.108),(.052,.109,.110),(.090,.101,.106)],[.004,.010,.026,.052,.082,.101,.098,.078,.047,.014],[.0004,.0008,.0016,.0030,.0044,.0053,.0050,.0040,.0025,.0008],HAIR,.0027)
add_fringe_surface_v85(HEAD,'FringeSurfaceV90_Over',[(.004,.211,.006),(-.010,.204,.021),(-.028,.197,.039),(-.041,.186,.056),(-.028,.169,.075),(-.002,.151,.092),(.030,.135,.102),(.065,.121,.107),(.099,.112,.104)],[.003,.008,.019,.040,.060,.069,.060,.037,.010],[.0003,.0007,.0015,.0028,.0039,.0044,.0038,.0024,.0007],HAIR_HI,.0022)
# Direction lines start only after the root is already covered by the crown cap.
add_strand(HEAD,'FringeFineV90_A',[(-.067,.188,.054),(-.050,.159,.088),(.024,.122,.109)],.000034,HAIR_HI)
add_strand(HEAD,'FringeFineV90_B',[(-.039,.186,.057),(.000,.153,.092),(.078,.120,.106)],.000032,HAIR_HI)
# v8.2 deliberately omits isolated cheek wisps. At portrait scale even a physically thin curve
# reads as a detached black scratch in profile; the existing broad temple/face locks carry the hairstyle.

# v8.3: no isolated front temple locks; the rear shell/fringe own this silhouette continuously.

add_box(HEAD,'HairTieV59',(.014,.138,-head_d*.530),(.072,.017,.027),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# v6.5 overlapping foundation: broad spline locks eliminate the separated vertical-string silhouette.
for i in range(5):
 lane=(i-2)/2
 sideflow=.055*lane
 pts=[
  (lane*.018+.014,.138,-head_d*.540),
  (lane*.030+.018,.025,-head_d*.615),
  (lane*.046+.030,-.220,-.255),
  (lane*.060+.055+sideflow*.25,-.500,-.210),
  (lane*.075+.085+sideflow*.55,-.820,-.162),
  (lane*.090+.110+sideflow*.75,-1.150,-.120),
  (lane*.105+.125+sideflow,-1.485,-.085)
 ]
 widths=[.052,.095,.118,.122,.104,.070,.014]
 depths=[.026,.040,.047,.048,.041,.029,.008]
 add_smooth_lock(PONY,f'PonyFoundationV65_{i}',pts,widths,depths,HAIR_HI if i in(1,3) else HAIR,14,7)
# v6.6 fanned secondary mass: broad curves give the pony a graceful lateral silhouette.
for i,target in enumerate((-.120,.145,.265)):
 lane=(i-1)*.030
 pts=[
  (lane+.014,.137,-head_d*.548),
  (lane+.022,.025,-head_d*.620),
  (lane+target*.16,-.205,-.258),
  (lane+target*.34,-.455,-.218),
  (lane+target*.55,-.720,-.175),
  (lane+target*.74,-.995,-.137),
  (lane+target*.90,-1.285,-.105),
  (target,-1.505,-.082)
 ]
 widths=[.038,.070,.090,.098,.094,.078,.048,.008]
 depths=[.024,.038,.045,.046,.042,.034,.022,.006]
 add_smooth_lock(PONY,f'PonyFanV66_{i}',pts,widths,depths,HAIR_HI if i==1 else HAIR,14,7)
# v6.7 broad high-pony wings: overlapping masses, not isolated strings.
for i,(target,drop) in enumerate(((-.300,-1.34),(-.205,-1.52),(.195,-1.48),(.295,-1.30))):
 sign=-1 if target<0 else 1
 pts=[
  (sign*.018,.143,-head_d*.550),
  (sign*.034,.035,-head_d*.620),
  (sign*.075,-.165,-.270),
  (target*.48,-.390,-.225),
  (target*.73,-.650,-.178),
  (target,-.930,-.135),
  (target*.90,-1.155,-.108),
  (target*.72,drop,-.086)
 ]
 widths=[.050,.090,.120,.132,.122,.102,.066,.010]
 depths=[.027,.043,.052,.056,.051,.043,.030,.007]
 add_smooth_lock(PONY,f'PonyWingV67_{i}',pts,widths,depths,HAIR if i in (0,3) else HAIR_HI,16,8)
# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry.
for i in range(11):
 lane=(i-5)/5
 dz=lane*.046+((i%3)-1)*.012
 sway=.055*math.sin((i+1)*1.37)
 flare=lane*.070
 pts=[
  (lane*.025+.014,.138,-head_d*.540+dz*.18),
  (lane*.042+.020+sway*.12,.030,-head_d*.615+dz*.55),
  (lane*.068+.026+sway*.45,-.220,-.250+dz*.80),
  (lane*.095+.032+sway+flare*.35,-.520,-.205+dz),
  (lane*.125+.040+sway*.78+flare*.60,-.850,-.158+dz*1.10),
  (lane*.145+.048+sway*.44+flare*.80,-1.170,-.120+dz*1.05),
  (lane*.158+.054+flare,-1.500-(i%3)*.025,-.092+dz*.88)
 ]
 base=.064-.009*abs(lane)
 widths=[base*.72,base,base*.98,base*.90,base*.72,base*.43,.0060]
 depths=[.030,.043,.044,.040,.032,.020,.0050]
 add_smooth_lock(PONY,f'PonyMassV59_{i}',pts,widths,depths,HAIR_HI if i in(2,8) else HAIR,12,6)
for i in range(7):
 lane=(i-3)/3
 sway=.040*math.sin((i+2)*1.41)
 add_strand(PONY,f'PonyWispV59_{i}',[(lane*.028+.014,.136,-head_d*.548),(lane*.046+.020,-.020,-head_d*.616),(lane*.075+.026+sway*.4,-.330,-.235),(lane*.115+.036+sway,-.805,-.158),(lane*.155+.050,-1.515-(i%2)*.030,-.086)],.00022+(i%2)*.000035,HAIR_HI if i%2==0 else HAIR)

# === LIMBS ===
# Diameters come directly from the front sheet; side depth comes from the side view.
ua=W('upper_arm')*.74;fa=W('forearm')*.69;th=W('thigh_each')*.82;kn=W('knee_each')*.70;calf=W('calf_each')*.72;ank=W('ankle_each')*.56
ua_d=ua*.78;fa_d=fa*.80;th_d=D('thigh')*.50;calf_d=D('calf')*.50;ank_d=D('ankle')*.50
for group,name,r1,r2,d1,d2,mat in[
 (UA_L,'UpperArmL',ua*1.04,ua*.82,ua_d*1.05,ua_d*.86,SKIN),(UA_R,'UpperArmR',ua*1.04,ua*.82,ua_d*1.05,ua_d*.86,SKIN),
 (FA_L,'ForearmL',fa*.96,fa*.72,fa_d*1.02,fa_d*.75,BLACK),(FA_R,'ForearmR',fa*.96,fa*.72,fa_d*1.02,fa_d*.75,BLACK),
 (TH_L,'ThighL',th*1.12,kn*.94,th_d*1.06,th_d*.82,SKIN),(TH_R,'ThighR',th*1.12,kn*.94,th_d*1.06,th_d*.82,SKIN),
 (SH_L,'ShinL',calf*.93,ank*.90,calf_d,ank_d,BLACK),(SH_R,'ShinR',calf*.93,ank*.90,calf_d,ank_d,BLACK)]:add_taper(group,name,r1,r2,d1,d2,mat)
# Soft junction volumes remove the detached mannequin-arm/thigh look while staying inside measured widths.
for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_sphere(group,'DeltoidBlendV59'+name,(0,-.430,0),(ua*1.10,.095,ua_d*1.08),SKIN,30,20)
for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_sphere(group,'HipThighBlendV58'+name,(0,-.430,0),(th*1.08,.092,th_d*1.04),SKIN,28,18)
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
