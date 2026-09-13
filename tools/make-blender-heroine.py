import bpy, json, os, math

ROOT_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
OUT=os.path.join(ROOT_DIR,'dist','assets','models','heroine-blender.glb')
REF_PATH=os.path.join(ROOT_DIR,'tools','heroine-reference-proportions.json')
FACE75_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v75.json')
CC0_FACE_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-template-v1.json')
CC0_STATS_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-stats.json')
FACE120_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v120.json')
ASSEMBLY120_PATH=os.path.join(ROOT_DIR,'tools','heroine-assembly-v120.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE75_PATH,'r',encoding='utf-8') as f:FACE75=json.load(f)
with open(CC0_FACE_PATH,'r',encoding='utf-8') as f:CC0_FACE=json.load(f)
with open(CC0_STATS_PATH,'r',encoding='utf-8') as f:CC0_STATS=json.load(f)
with open(FACE120_PATH,'r',encoding='utf-8') as f:FACE120=json.load(f)
with open(ASSEMBLY120_PATH,'r',encoding='utf-8') as f:ASSEMBLY120=json.load(f)
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

def tune_principled(mat,specular=None,coat=None,coat_roughness=None):
 b=mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
 if not b:return mat
 def set_any(names,value):
  if value is None:return
  for name in names:
   inp=b.inputs.get(name)
   if inp is not None:
    inp.default_value=value
    return
 set_any(('Specular IOR Level','Specular'),specular)
 set_any(('Coat Weight','Clearcoat'),coat)
 set_any(('Coat Roughness','Clearcoat Roughness'),coat_roughness)
 return mat
SKIN=material('Skin',(0.375,0.245,0.225),0,.68)
BLACK=material('Suit Black',(0.014,0.018,0.027),.08,.30)
BLACK_SOFT=material('Suit Soft',(0.030,0.035,0.048),.02,.44)
WHITE=material('Porcelain White',(0.86,0.88,0.88),.18,.28)
SILVER=material('Silver',(0.50,0.53,0.56),.78,.19)
HAIR=material('Hair',(0.028,0.019,0.022),0.0,.51)
HAIR_HI=material('Hair Highlight',(0.072,0.046,0.050),0.0,.50)
# Reduce Principled specular so dark hair does not blow out to a silver ribbon under bright sky lighting.
for _hair_mat,_spec in ((HAIR,.16),(HAIR_HI,.21)):
 _bsdf=_hair_mat.node_tree.nodes.get('Principled BSDF')
 if _bsdf:
  _ior=_bsdf.inputs.get('Specular IOR Level')
  _old=_bsdf.inputs.get('Specular')
  if _ior:_ior.default_value=_spec
  elif _old:_old.default_value=_spec
SCLERA=material('Sclera',(0.60,0.575,0.555),0,.42)
IRIS=material('Iris',(0.052,0.032,0.030),.01,.42)
IRIS_INNER=material('Iris Inner',(0.175,0.105,0.082),.01,.40)
IRIS_RAY_WARM=material('Iris Ray Warm',(0.205,0.118,0.078),.01,.40)
IRIS_RAY_DARK=material('Iris Ray Dark',(0.105,0.055,0.042),.01,.43)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.28)
LIP=material('Lip',(0.285,0.105,0.125),0,.42)
FACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)
EYE_WET=material('Eye Wetline',(0.34,0.155,0.145),0,.24)
EAR_SHADOW=material('Ear Inner',(0.255,0.145,0.135),0,.78)
GLOW=material('Cyan Accent',(0.20,0.56,0.61),.38,.18)
tune_principled(SKIN,specular=.32,coat=.035,coat_roughness=.70)
tune_principled(SCLERA,specular=.52,coat=.32,coat_roughness=.18)
tune_principled(IRIS,specular=.46,coat=.18,coat_roughness=.22)
tune_principled(IRIS_INNER,specular=.48,coat=.22,coat_roughness=.20)
tune_principled(IRIS_RAY_WARM,specular=.46,coat=.18,coat_roughness=.22)
tune_principled(IRIS_RAY_DARK,specular=.42,coat=.14,coat_roughness=.24)
tune_principled(PUPIL,specular=.34,coat=.12,coat_roughness=.20)
tune_principled(LIP,specular=.44,coat=.30,coat_roughness=.24)
tune_principled(EYE_WET,specular=.58,coat=.52,coat_roughness=.12)

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


def add_profile_ellipse_yz_v137(p,name,cx,cy,cz,ry,rz,mat,segments=32):
 verts=[bpos((cx,cy,cz))]
 for i in range(segments):
  a=2*math.pi*i/segments
  verts.append(bpos((cx,cy+ry*math.cos(a),cz+rz*math.sin(a))))
 faces=[(0,1+i,1+((i+1)%segments)) for i in range(segments)]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)


def add_iris_rays_v129(p,name,cx,cy,cz,rx,ry,inner_ratio,mats,segments=24):
 verts=[]
 for radius in (inner_ratio,1.0):
  for i in range(segments):
   a=2*math.pi*i/segments
   verts.append(bpos((cx+rx*radius*math.cos(a),cy+ry*radius*math.sin(a),cz)))
 faces=[]
 for i in range(segments):
  j=(i+1)%segments
  faces.append((i,j,segments+j,segments+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
 for mat in mats:o.data.materials.append(mat)
 for i,poly in enumerate(o.data.polygons):poly.material_index=0 if (i%5 in (0,2) or i%3==1) else 1
 smooth(o);return parent(o,p)


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
 verts=[];logical_ys=[]
 for vx,vy,vz in CC0_FACE['vertices']:
  yn=max(0.0,min(1.0,vy+.5))
  yy=-.145+yn*.305
  logical_ys.append(yy)
  # 0.245 total mapping gives a slim 0.1225 half-face; taper the lower third into the reference V jaw.
  jaw_t=max(0.0,min(1.0,(-.025-yy)/.120))
  x=vx*.238*(1.0-.175*jaw_t)
  # The open CC0 patch used to stay too wide below the mouth while HeadShellV60 narrows sharply.
  # Smoothly pull only the lower third inward so its boundary stays inside the jaw/under-chin silhouette.
  under_t=max(0.0,min(1.0,(-.078-yy)/.067))
  under_t=under_t*under_t*(3.0-2.0*under_t)
  x*=1.0-.52*under_t
  # v10.8 feathers only the lower outer CC0 perimeter. The centre chin keeps the measured profile;
  # outer seam vertices contract a little more so no isolated triangle can protrude past HeadShellV60.
  edge_t=max(0.0,min(1.0,(abs(vx)-.205)/.095))
  edge_t=edge_t*edge_t*(3.0-2.0*edge_t)
  edge_under=edge_t*under_t
  x*=1.0-.14*edge_under
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
  # Keep the expressive face patch proud through the cheeks, then settle its lower boundary into the backing shell.
  # At the lower outer perimeter suppress generic relief and pull the seam fractionally rearward;
  # centre-line chin/lip depth remains untouched because edge_under is zero there.
  local_relief*=1.0-.62*edge_under
  z=pz+local_relief*relief_gain+(.0016-.0012*under_t-.00085*edge_under)
  # The CC0 patch is an expression/topology overlay, not the final under-chin shell. Fade it behind
  # HeadShellV60 after the mouth so the closed UV head owns the chin silhouette continuously.
  chin_hide=max(0.0,min(1.0,(-.094-yy)/.051))
  chin_hide=chin_hide*chin_hide*(3.0-2.0*chin_hide)
  z-=.0190*chin_hide
  bridge_lat=math.exp(-(x/.030)**2)
  tip_lat=math.exp(-(x/.0215)**2)
  z+=.0024*bridge_lat*math.exp(-((yy+.006)/.052)**2)
  z+=.0022*tip_lat*math.exp(-((yy+.045)/.0195)**2)
  verts.append(bpos((x,yy,z)))
 # v11.0: v10.9 has already moved the lower overlay behind HeadShellV60. Drop faces that
 # touch the fully hidden under-chin zone so they cannot intersect back through the closed shell.
 # The cutoff remains below the mouth/labiomental work; the visible chin is owned by HeadShellV60.
 faces=[]
 for f in CC0_FACE['faces']:
  if min(logical_ys[i] for i in f) < -.118:
   continue
  faces.append(tuple(f))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)

def add_anime_head_v60(p,name,mat,segments=96,rings=48):
 # Smooth UV topology replaces row-profile rings that produced horizontal shading bands.
 verts=[]
 # v11.1 keeps the measured face untouched through the jaw, but shortens the purely structural
 # UV-sphere tail below it.  The mapped bottom remains overlapped by the neck, avoiding any gap.
 jaw_anchor=-.118
 under_chin_scale=.68
 bottom_y=jaw_anchor+(-.157-jaw_anchor)*under_chin_scale
 top=bpos((0,.179,0));bottom=bpos((0,bottom_y,0));verts.append(top)
 for r in range(1,rings):
  theta=math.pi*r/rings
  sy=math.cos(theta);rad=math.sin(theta)
  yy=.011+.168*sy
  render_y=yy if yy>=jaw_anchor else jaw_anchor+(yy-jaw_anchor)*under_chin_scale
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
   verts.append(bpos((x,render_y,z)))
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

def add_reference_head_v120(p,name,mat,segments=112):
 # Parameter grouping follows yz4git/model-editor: frontal metrics and side-depth metrics are
 # independent. This keeps profile edits from changing face width/jaw/eye spacing in front view.
 frontal=FACE120['frontal'];profile_ctrl=FACE120['profile'];surface=FACE120['surface']
 assembly_head=ASSEMBLY120['head']
 frontal={**frontal,'eyeSize':assembly_head['eyeSize'],'eyeSpacing':assembly_head['eyeSpacing'],'faceWidth':assembly_head['faceWidth'],'jaw':assembly_head['jaw'],'cheekVolume':assembly_head['cheekVolume'],'mouthWidth':assembly_head['mouthWidth']}
 profile_ctrl={**profile_ctrl,'noseProjection':assembly_head['noseProjection'],'noseWidth':assembly_head['noseWidth'],'foreheadDepth':assembly_head['foreheadDepth'],'mouthProjection':assembly_head['mouthProjection'],'chinProjection':assembly_head['chinProjection'],'chinLength':assembly_head['chinLength']}
 surface={**surface,'irisScale':assembly_head['irisScale'],'eyeContrast':assembly_head['eyeContrast']}
 fw=frontal['faceWidth']*1.025;jaw=frontal['jaw']*.975;cheek=frontal['cheekVolume']*1.045
 eye_spacing=frontal['eyeSpacing'];eye_size=frontal['eyeSize']
 nose_proj=profile_ctrl['noseProjection']*.76;nose_width=profile_ctrl['noseWidth']
 forehead_depth=profile_ctrl['foreheadDepth']*1.01;mouth_proj=profile_ctrl['mouthProjection']*1.08
 chin_proj=profile_ctrl['chinProjection']*1.02;chin_len=profile_ctrl['chinLength']*1.00
 orbital=surface['orbitalDepth'];malar=surface['malarSupport'];hollow=surface['lowerCheekHollow']
 alar=surface['alarVolume'];philtrum=surface['philtrumDepth'];corner=surface['mouthCornerDepth']
 labiomental=surface['labiomentalDepth'];lip_volume=surface['lipThickness']
 glabella=surface['glabellaRelief'];bridge_relief=surface['bridgeRelief'];tip_relief=surface['tipRelief']
 columella=surface['columellaRelief'];infraorbital=surface['infraorbitalSoftness'];nasolabial=surface['nasolabialDepth']

 base_sections=[
  (.164,.071,.078,.080,-.010),(.150,.101,.084,.086,-.008),(.132,.119,.089,.091,-.006),
  (.108,.128,.094,.095,-.003),(.082,.130,.098,.097,-.001),(.058,.128,.100,.098,.001),
  (.036,.124,.101,.099,.002),(.014,.126,.102,.099,.003),(-.008,.125,.102,.100,.003),
  (-.030,.120,.102,.101,.002),(-.052,.114,.101,.102,.001),(-.072,.105,.100,.103,.000),
  (-.089,.096,.098,.103,-.001),(-.103,.087,.096,.102,-.003),(-.115,.078,.094,.101,-.004),
  (-.126,.068,.091,.098,-.006),(-.135,.056,.087,.093,-.008),(-.141,.042,.081,.086,-.009),
  (-.145,.026,.072,.078,-.010)
 ]
 sections=[]
 for yy,w,back,front,zoff in base_sections:
  # Jaw control ramps in below the mouth; upper cranium responds only to faceWidth.
  jw=max(0.0,min(1.0,(-yy-.050)/.095))
  width_scale=fw*(1.0-jw)+jaw*jw
  # chinLength changes vertical lower-face extent only, matching model-editor's side-mode intent.
  y2=yy if yy>=-.105 else -.105+(yy+.105)*chin_len
  sections.append((y2,w*width_scale,back,front,zoff))

 base_profile=[
  (.090,.1005),(.060,.1020),(.035,.1010),(.015,.0995),(-.005,.1035),(-.025,.1125),
  (-.040,.1255),(-.048,.1315),(-.055,.1295),(-.062,.1185),(-.068,.1085),
  (-.077,.1105),(-.086,.1175),(-.094,.1205),(-.103,.1110),(-.111,.1030),
  (-.121,.1168),(-.131,.1150),(-.140,.1040),(-.148,.0870),(-.154,.0710)
 ]
 profile=[]
 for yy,z in base_profile:
  ref=.100
  scale=1.0
  if yy>.035: scale=forehead_depth
  elif yy>-.068: scale=nose_proj
  elif yy>-.108: scale=mouth_proj
  else: scale=chin_proj
  profile.append((yy,ref+(z-ref)*scale))
 def sample_profile(y):
  if y>=profile[0][0]:return profile[0][1]
  if y<=profile[-1][0]:return profile[-1][1]
  for j in range(len(profile)-1):
   y0,z0=profile[j];y1,z1=profile[j+1]
   if y0>=y>=y1:
    t=(y0-y)/(y0-y1);t=t*t*(3.0-2.0*t)
    return z0+(z1-z0)*t
  return .100

 verts=[]
 for yy,w,back,front,zoff in sections:
  pz=sample_profile(yy)
  for i in range(segments):
   phi=2*math.pi*i/segments;cp=math.cos(phi);sp=math.sin(phi)
   x=cp*w;depth=front if sp>=0 else back;z=zoff+sp*depth
   if sp>0:
    fm=sp**1.48
    face_band=math.exp(-((yy+.018)/.125)**4)
    face_lat=1.0/(1.0+(abs(x)/(.096*fw))**6)
    neutral=.1005+.0012*math.exp(-((yy+.008)/.070)**2)
    z+=fm*face_band*face_lat*(neutral-z)*.78

    # Profile deformation affects Z only. Nose width is independent from frontal jaw/face width.
    pw=(.030*nose_width) if yy>-.068 else (.043 if yy>-.108 else .039)
    profile_lat=1.0/(1.0+(abs(x)/pw)**6)
    profile_band=math.exp(-((yy+.032)/.148)**6)
    z+=fm*profile_lat*profile_band*(pz-z)*.985

    for side in (-1,1):
     ex=side*.0465*eye_spacing
     z-=fm*(.00315*orbital)*math.exp(-((x-ex)/(.0265*eye_size))**2-((yy-.033)/(.0195*eye_size))**2)
     z+=fm*.0025*math.exp(-((x-ex)/.031)**2-((yy-.061)/.022)**2)
     z+=fm*(.00670*malar*cheek)*math.exp(-((x-side*.057)/.034)**2-((yy+.004)/.036)**2)
     z-=fm*(.00300*hollow)*math.exp(-((x-side*.069)/.030)**2-((yy+.054)/.035)**2)
     z-=fm*.0016*math.exp(-((x-side*.087)/.025)**2-((yy-.040)/.041)**2)
     z+=fm*.0028*math.exp(-((x-side*.0105)/(.0110*nose_width))**2-((yy+.055)/.0135)**2)
     z-=fm*.0012*math.exp(-((x-side*.018)/.014)**2-((yy+.071)/.017)**2)
     z-=fm*.0022*math.exp(-((x-side*.065*jaw)/.029)**2-((yy+.108)/.027)**2)

    # v11.7 local RBF anatomy, adapted from model-editor's measured-base deformation strategy.
    # Each field is deliberately local so nose/mouth depth can change without widening the frontal jaw.
    for side in (-1,1):
     # Alar wings move slightly outward and forward around the nasal base.
     aw=math.exp(-((x-side*.0115)/(.0105*nose_width))**2-((yy+.0555)/.0115)**2)
     x+=side*.00155*alar*aw
     z+=fm*.0035*alar*aw
     # The nostril floor/alar crease sits just below and medial to the wing.
     nr=math.exp(-((x-side*.0075)/.0085)**2-((yy+.0630)/.0075)**2)
     z-=fm*.00175*surface['nostrilScale']*nr

    # Subnasal break and philtrum groove keep nose and upper lip from melting into one mound.
    z-=fm*.00155*math.exp(-(x/.0105)**2-((yy+.0665)/.0075)**2)
    z-=fm*.00145*philtrum*math.exp(-(x/.0070)**2-((yy+.0760)/.0105)**2)

    # Upper lip is two soft lobes with a shallow central Cupid notch; lower lip is one broad volume.
    mouth_w=frontal['mouthWidth']
    ul=(math.exp(-((x-.0105*mouth_w)/(.0120*mouth_w))**2-((yy+.0845)/.0080)**2)+
        math.exp(-((x+.0105*mouth_w)/(.0120*mouth_w))**2-((yy+.0845)/.0080)**2))
    z+=fm*.00322*lip_volume*ul
    z-=fm*.00075*lip_volume*math.exp(-(x/.0055)**2-((yy+.0847)/.0055)**2)
    ll=math.exp(-(x/(.0255*mouth_w))**2-((yy+.0940)/.0085)**2)
    z+=fm*.00378*lip_volume*ll
    # Mouth seam and corners recess into the muzzle rather than floating as a drawn line.
    z-=fm*.00080*math.exp(-(x/(.0280*mouth_w))**4-((yy+.0887)/.0032)**2)
    for side in (-1,1):
     mc=math.exp(-((x-side*.0285*mouth_w)/.0090)**2-((yy+.0890)/.0070)**2)
     z-=fm*.00135*corner*mc

    # Labiomental fold separates the lower lip from a more feminine, compact chin pad.
    z-=fm*.00135*labiomental*math.exp(-(x/.0245)**2-((yy+.1060)/.0082)**2)
    z+=fm*.00465*math.exp(-(x/.0305)**2-((yy+.121)/.0195)**2)

    # v11.8 adult facial planes. These are local depth fields, not detached feature meshes,
    # so the silhouette remains one continuous head surface from front through three-quarter views.
    z+=fm*.00215*glabella*math.exp(-(x/.0220)**2-((yy-.0470)/.0180)**2)
    z+=fm*.00345*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)
    z+=fm*.00470*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0115)**2)
    z+=fm*.00195*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0085)**2)

    # Soften the lower-orbit to malar transition but keep a readable cheek plane under cinematic light.
    for side in (-1,1):
     io=math.exp(-((x-side*.0445*eye_spacing)/(.0260*eye_size))**2-((yy-.0140)/.0185)**2)
     z+=fm*.00155*infraorbital*io
     nl=math.exp(-((x-side*.0300)/.0145)**2-((yy+.0690)/.0180)**2)
     z-=fm*.00085*nasolabial*nl
   render_y=yy
   if yy<-.112:
    under=max(0.0,min(1.0,(-yy-.112)/.042))
    frontness=max(0.0,sp)
    # Existing side/rear lift, reduced slightly now that the depth-aware term below owns the jaw angle.
    render_y+=.0075*under*(1.0-frontness**1.45)
    # z is logical front/back. As the surface travels rearward from the chin, raise it toward the jaw hinge/neck.
    backness=max(0.0,min(1.0,(.116-z)/.105))
    render_y+=.0200*under*(backness**1.18)
    # Only the very lowest centre-front samples receive a tiny lift; the visible chin tip remains low/rounded.
    throat=max(0.0,min(1.0,(-yy-.133)/.020))
    render_y+=.0022*throat*frontness
   verts.append(bpos((x,render_y,z)))

 top_idx=len(verts);verts.append(bpos((0,.176,-.006)))
 bottom_y=-.105+(-.147+.105)*chin_len*.58
 bottom_idx=len(verts);verts.append(bpos((0,bottom_y,-.011)))
 faces=[];rows=len(sections)
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 for i in range(segments):
  j=(i+1)%segments;faces.append((top_idx,j,i))
  a=(rows-1)*segments;faces.append((bottom_idx,a+i,a+j))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('reference_head_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)

ROOT=empty('BLENDER_HEROINE')
BODY_ASSET=empty('BL_BODY_ASSET',ROOT)
PELVIS=empty('BL_PELVIS',BODY_ASSET);TORSO=empty('BL_TORSO',BODY_ASSET);HEAD=empty('BL_HEAD',ROOT)
HEAD_ASSET=empty('BL_HEAD_ASSET',HEAD);HAIR_ASSET=empty('BL_HAIR_ASSET',HEAD);FACE_ASSET=empty('BL_FACE_ASSET',HEAD)
EYE_L=empty('BL_EYE_L',FACE_ASSET);EYE_R=empty('BL_EYE_R',FACE_ASSET);MOUTH_ASSET=empty('BL_MOUTH',FACE_ASSET)
UA_L=empty('BL_UPPER_ARM_L',BODY_ASSET);FA_L=empty('BL_FOREARM_L',BODY_ASSET);HAND_L=empty('BL_HAND_L',BODY_ASSET);UA_R=empty('BL_UPPER_ARM_R',BODY_ASSET);FA_R=empty('BL_FOREARM_R',BODY_ASSET);HAND_R=empty('BL_HAND_R',BODY_ASSET)
TH_L=empty('BL_THIGH_L',BODY_ASSET);SH_L=empty('BL_SHIN_L',BODY_ASSET);FOOT_L=empty('BL_FOOT_L',BODY_ASSET);TH_R=empty('BL_THIGH_R',BODY_ASSET);SH_R=empty('BL_SHIN_R',BODY_ASSET);FOOT_R=empty('BL_FOOT_R',BODY_ASSET);SWORD=empty('BL_SWORD',ROOT)

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
# REFERENCE_V103: adult visible ears sit outside a notched temporal undercap, restoring a natural hairline-to-ear transition in profile.
# REFERENCE_V104: the notched temporal undercap widens rearward into the rear-hair shell, covering the exposed side scalp without hiding the ears.
# REFERENCE_V105: visible rear-hair geometry expands around ear height while the buried v10.4 undercap returns to the compact v10.3 footprint.
# REFERENCE_V106: the CC0 face patch lower third tapers into the head shell, removing the collar-like under-chin boundary spikes without changing eyes, nose or cheeks.
# REFERENCE_V107: the remaining lower patch edge tightens further and settles into the head shell, eliminating the last under-chin sawtooth silhouette.
# REFERENCE_V108: only the lower CC0 patch perimeter is feathered into the backing head shell, removing residual chin-edge teeth while preserving the centre profile.
# REFERENCE_V109: the CC0 overlay fades behind the backing shell below the mouth; the continuous head shell owns chin and under-chin silhouette with no beard-like patch edge.
# REFERENCE_V110: fully hidden lower CC0 faces are trimmed after the fade so no intersecting overlay triangles can reappear as chin/neck scallops in three-quarter views.
# REFERENCE_V111: the closed head shell compresses only below the jaw anchor, replacing the long UV-sphere bottom cone with a compact under-chin transition while all facial landmarks stay fixed.
# REFERENCE_V112: public-model study reset; one independently generated continuous adult-anime head shell replaces HeadShellV60 plus the CC0 overlay patch.
# REFERENCE_V113: the new single shell gains an explicit adult S-profile and seated orbital surfaces after five-view validation exposed the v11.2 flat side silhouette.
# REFERENCE_V114: stronger public-basemesh-scale facial projection gives the clean shell a readable nose/lip/chin silhouette and retargets surface accents to it.
# REFERENCE_V115: the clean shell gains a tapered adult jaw, deeper orbital seating, stronger malar transition and a naturally wider mouth after five-view review.
# REFERENCE_V116: model-editor-inspired independent frontal/profile/surface controls drive the single-shell face so depth tuning no longer disturbs frontal proportions.
# REFERENCE_V117: model-editor-style local Gaussian/RBF fields sculpt alar wings, philtrum, volumetric lips, mouth corners and the labiomental fold directly into the single-shell face.
# REFERENCE_V118: reference-locked adult portrait pass narrows the lower face, strengthens brow/bridge/tip/columella profile planes and upgrades the cinematic almond-eye treatment.
# REFERENCE_V119: visual-audit portrait pass boosts iPhone-scale eye contrast, shortens the lower face, exaggerates the key-art profile and adds layered asymmetric brow-length bangs.
# REFERENCE_V120: Tripo/Astra-inspired modular assembly pass separates body/head/hair/face assets, adds expression pivots and rebalances the close-up eye/profile read without changing combat rig names.
# REFERENCE_V121: audit correction keeps visible eye/mouth meshes in the face asset, leaves expression pivots transform-neutral, and narrows the adult-anime eye aperture for clean profile/3q views.
# REFERENCE_V122: real skin eyelid meshes use a Blink morph target so eyes close over the globe instead of scaling the eyeball.
# REFERENCE_V123: TPS silhouette pass keeps measured rig endpoints while narrowing visual deltoid/clavicle armor and upper-chest shell bulk.
# REFERENCE_V124: layered crown and hero-ponytail masses break the helmet/flat-sheet silhouette while preserving the existing dynamic pony root.
# REFERENCE_V125: facial-depth and eye-material pass strengthens orbital/nasal/cheek planes and mobile-scale gaze without changing the modular expression pivots.
# REFERENCE_V126: compact adult-anime face pass shortens the lower face, opens the gaze slightly and broadens the cheek plane without changing combat/head pivots.
# REFERENCE_V127: profile-balance pass reduces excessive nasal projection and restores a cleaner nose-lip-chin S-curve while preserving the accepted v12.6 frontal mask.
# REFERENCE_V128: portrait PBR pass adds mobile-safe eye wetline geometry plus skin/sclera/iris/lip specular tuning without changing accepted v12.7 proportions.
# REFERENCE_V129: texture-like radial iris detail uses one tiny indexed mesh per eye, adding warm/dark spokes without image textures or extra draw-call-heavy strand objects.
# REFERENCE_V130: user-profile reference pass reshapes the nose/lip/chin silhouette toward a smaller rounded nose, flatter muzzle and longer elegant chin without changing the accepted frontal mask.
# REFERENCE_V131: profile-silhouette pass opens the eye through finer fringe, adds an orbital-to-bridge break and lengthens the tapered chin toward the supplied side-view reference.
# REFERENCE_V132: profile-eye/jaw pass strengthens the side-view lash silhouette, clears the near-eye fringe and extends the chin-underjaw flow toward the supplied portrait while preserving the accepted frontal mask.
# REFERENCE_V133: volumetric profile-eye pass embeds a shallow sclera globe and side-swept lash fin so the eye remains readable in exact profile instead of collapsing to an edge-on plane.
# REFERENCE_V134: profile-iris/underjaw pass embeds a mostly buried iris volume for side-view gaze and lifts the rear under-chin cap toward the neck for the supplied elegant jawline.
# REFERENCE_V135: supplied-reference silhouette pass refines the small nose/lip/chin S-curve, exposes more neck below the jaw and adds a near-side iris crescent for exact-profile readability.
# REFERENCE_V136: supplied-reference hair-profile pass warms the dark hair, reveals the ear, converts the cheek-side slab into fine layered locks and adds a restrained metallic pony ornament plus loose wisps.
# REFERENCE_V137: profile-anatomy correction rounds/recedes the chin, lifts the rear underjaw toward a rear-set neck and adds a true side-facing iris/pupil surface plus a small earring cue.
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
 add_sphere(TORSO,f'DeltoidBridgeV50_{side}',(side*bust_w*.385,.236,.002),(bust_w*.108,.056,bust_d*.128),BLACK,34,22)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.270,.258,bust_d*.28),(side*bust_w*.435,.226,bust_d*.18),(side*bust_w*.255,.211,bust_d*.31)],.012,BLACK_SOFT)
 add_box(TORSO,f'ClavicleTrim_{side}',(side*bust_w*.205,.247,bust_d*.325),(bust_w*.220,.009,.008),SILVER,.0025,rot=(0,0,-side*.10))
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
add_panel(TORSO,'ChestWingV67_L',[(-bust_w*.472,.248,bust_d*.455),(-bust_w*.245,.226,bust_d*.595),(-bust_w*.205,.080,bust_d*.790),(-bust_w*.438,.066,bust_d*.690)],.012,WHITE)
add_panel(TORSO,'ChestWingV67_R',[(bust_w*.245,.226,bust_d*.595),(bust_w*.472,.248,bust_d*.455),(bust_w*.438,.066,bust_d*.690),(bust_w*.205,.080,bust_d*.790)],.012,WHITE)
add_panel(TORSO,'WaistWingV67_L',[(-bust_w*.455,.060,bust_d*.675),(-bust_w*.205,.076,bust_d*.790),(-waist_w*.235,-.205,waist_d*.760),(-waist_w*.545,-.232,waist_d*.655)],.011,WHITE)
add_panel(TORSO,'WaistWingV67_R',[(bust_w*.205,.076,bust_d*.790),(bust_w*.455,.060,bust_d*.675),(waist_w*.545,-.232,waist_d*.655),(waist_w*.235,-.205,waist_d*.760)],.011,WHITE)
for side in(-1,1):
 add_box(TORSO,f'ChestSeamV67_{side}',(side*bust_w*.245,.120,bust_d*.785),(.010,.205,.010),SILVER,.0032,rot=(0,0,side*.11))

# v6.8 porcelain shell covers the old black capsule; a narrow black centre panel restores the reference couture contrast.
add_panel(TORSO,'PorcelainShellV68_L',[(-bust_w*.486,.250,bust_d*.485),(-bust_w*.115,.226,bust_d*.690),(-bust_w*.095,.072,bust_d*.875),(-waist_w*.105,-.188,waist_d*.905),(-waist_w*.535,-.238,waist_d*.735),(-bust_w*.462,.058,bust_d*.750)],.013,WHITE)
add_panel(TORSO,'PorcelainShellV68_R',[(bust_w*.115,.226,bust_d*.690),(bust_w*.486,.250,bust_d*.485),(bust_w*.462,.058,bust_d*.750),(waist_w*.535,-.238,waist_d*.735),(waist_w*.105,-.188,waist_d*.905),(bust_w*.095,.072,bust_d*.875)],.013,WHITE)
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
# v11.2 full rebuild: a single new independently generated shell owns the visible face.
# The legacy HeadShellV60 and FaceQuadPatchV77 remain as unused historical helpers only.
add_reference_head_v120(HEAD,'HeadShellV120',SKIN,128)
add_cylinder(HEAD,'Neck',(0,-.181,-.030),W('neck')*.292,.134,SKIN,30)
add_cylinder(HEAD,'Choker',(0,-.206,-.028),W('neck')*.425,.038,BLACK,30)
add_cylinder(HEAD,'ChokerTrim',(0,-.186,-.028),W('neck')*.435,.008,SILVER,30)
for side in(-1,1):
 add_sphere(HEAD,f'EarV103_{side}',(side*.1265,-.020,-.012),(.0122,.0350,.0170),SKIN,30,20)
 # A restrained helix/concha line is enough to read as an ear at iPhone portrait scale without becoming a dark decal.
 add_strand(HEAD,f'EarHelixV103_{side}',[
  (side*.1380,.004,-.021),
  (side*.1390,-.007,-.012),
  (side*.1393,-.021,-.010),
  (side*.1388,-.035,-.016),
  (side*.1376,-.044,-.025)
 ],.00028,EAR_SHADOW)
 add_strand(HEAD,f'EarConchaV103_{side}',[
  (side*.1385,-.010,-.018),
  (side*.1390,-.020,-.015),
  (side*.1384,-.030,-.020)
 ],.00022,EAR_SHADOW)
 add_strand(HEAD,f'EarringDropV137_{side}',[(side*.1390,-.043,-.010),(side*.1392,-.057,-.009),(side*.1390,-.071,-.010)],.00032,SILVER)
 add_box(HEAD,f'EarringTipV137_{side}',(side*.1390,-.075,-.010),(.0045,.010,.0045),SILVER,.0015)



def add_blink_lid_surface(p,name,ex,cy,rx,ry,mat):
 us=(-1.0,-.55,0.0,.55,1.0)
 opened=[];closed=[]
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10542+.00034*bow
  edge=cy+ry*(.10+.86*bow);top=edge+.00415+.00055*bow
  opened.append((x,top,z-.00008));closed.append((x,top,z-.00008))
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10550+.00042*bow
  edge=cy+ry*(.10+.86*bow);close_y=cy-.00030+ry*.075*bow-.00022
  opened.append((x,edge,z));closed.append((x,close_y,z+.00016))
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10544+.00038*bow
  edge=cy-ry*(.08+.60*bow);close_y=cy-.00030+ry*.075*bow+.00022
  opened.append((x,edge,z));closed.append((x,close_y,z+.00010))
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10531+.00028*bow
  edge=cy-ry*(.08+.60*bow);bottom=edge-.00330-.00038*bow
  opened.append((x,bottom,z-.00008));closed.append((x,bottom,z-.00008))
 verts=[bpos(v) for v in opened];faces=[]
 for i in range(4):
  faces.append((i,i+1,6+i,5+i))
  faces.append((10+i,11+i,16+i,15+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);parent(o,p)
 o.shape_key_add(name='Basis')
 blink=o.shape_key_add(name='Blink')
 for i,v in enumerate(closed):blink.data[i].co=bpos(v)
 o['expression']='blink';o['blink_morph']='Blink';smooth(o)
 return o

# v11.9 key-art eyes: the white aperture stays adult-shaped, but a dark complete contour and larger warm iris
# preserve the expressive anime-real portrait read at actual iPhone gameplay distance.
face_front=.0974
eye_y=.0295
eye_x=.0452*ASSEMBLY120['head']['eyeSpacing']
eye_rx=.02865*ASSEMBLY120['head']['eyeSize']
eye_ry=.01090*ASSEMBLY120['head']['eyeSize']
eye_tilt=.00285
iris_scale=ASSEMBLY120['head']['irisScale']*1.05
eye_contrast=ASSEMBLY120['head']['eyeContrast']*1.08
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeScleraGlobeV133_{side}',(ex,eye_y,.0936),(eye_rx*.82,eye_ry*.88,.0107),SCLERA,34,22)
 add_sphere(HEAD,f'EyeIrisVolumeV134_{side}',(ex,eye_y-.00010,.09915),(eye_rx*.285,eye_ry*.48,.00495),IRIS,28,18)
 add_sphere(HEAD,f'EyePupilVolumeV134_{side}',(ex,eye_y-.00025,.10055),(eye_rx*.105,eye_ry*.235,.00355),PUPIL,24,16)
 add_sphere(HEAD,f'EyeProfileIrisV135_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.10010),(eye_rx*.175,eye_ry*.34,.00325),IRIS_INNER,22,14)
 add_sphere(HEAD,f'EyeProfilePupilV135_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10105),(eye_rx*.060,eye_ry*.17,.00225),PUPIL,18,12)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.815,eye_y+.0003,.1025,eye_ry*.43,.00255,IRIS_INNER,30)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.822,eye_y+.0002,.1029,eye_ry*.205,.00125,PUPIL,24)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
 # Dark outer iris first, then a smaller warm inner iris and pupil; this gives a readable limbal ring.
 add_ellipse_surface(HEAD,f'IrisOuterV119_{side}',ex,eye_y-.00025,.10448,.01155*iris_scale,.00915*iris_scale,IRIS,52)
 add_ellipse_surface(HEAD,f'IrisInnerV119_{side}',ex,eye_y-.00005,.10472,.00875*iris_scale,.00670*iris_scale,IRIS_INNER,48)
 add_iris_rays_v129(HEAD,f'IrisRaysV129_{side}',ex,eye_y-.00005,.10484,.00795*iris_scale,.00605*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)
 add_ellipse_surface(HEAD,f'PupilV119_{side}',ex,eye_y-.00045,.10502,.00305*iris_scale,.00385*iris_scale,PUPIL,36)
 add_ellipse_surface(HEAD,f'EyeLightV119A_{side}',ex-side*.00355,eye_y+.00335,.10520,.00135,.00103,SCLERA,20)
 add_ellipse_surface(HEAD,f'EyeLightV119B_{side}',ex+side*.00205,eye_y+.00105,.10518,.00048,.00040,SCLERA,16)
 inner=ex-side*eye_rx*.965;outer=ex+side*eye_rx*1.035
 # Explicit dark eyelid silhouette. The previous skin-coloured rim disappeared against the face at mobile scale.
 add_strand(HEAD,f'UpperLashV119_{side}',[(inner,eye_y-eye_tilt+.0002,.10402),(ex-side*.0030,eye_y+.01165,.10484),(outer+side*.0012,eye_y+eye_tilt+.00045,.10413)],.00102*eye_contrast,HAIR)
 add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0036,eye_y+eye_tilt+.0017,.10417),(outer+side*.0058,eye_y+eye_tilt+.0052,.10422),(outer+side*.0108,eye_y+eye_tilt+.0037,.10408)],.00060*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashV133_{side}',[(outer-side*.0015,eye_y+eye_tilt+.0030,.10425),(outer+side*.0010,eye_y+eye_tilt+.0050,.1068),(outer+side*.0028,eye_y+eye_tilt+.0042,.1092)],.00024*eye_contrast,HAIR)
 add_strand(HEAD,f'LowerLidV119_{side}',[(inner+side*.0040,eye_y-eye_tilt-.00035,.10374),(ex,eye_y-.00870,.10403),(outer-side*.0024,eye_y+eye_tilt-.00015,.10383)],.000215*eye_contrast,FACE_DARK)
 add_strand(HEAD,f'UpperLidFoldV119_{side}',[(inner+side*.0050,eye_y-eye_tilt+.0038,.10340),(ex,eye_y+.0153,.10375),(outer-side*.0060,eye_y+eye_tilt+.0036,.10342)],.00017,FACE_DARK)
 # v12.8 glossy waterline follows only the inner two-thirds of the lower lid so it reads as moisture, not eyeliner.
 add_strand(HEAD,f'EyeWetlineV128_{side}',[(inner+side*.0050,eye_y-eye_tilt-.00005,.10404),(ex,eye_y-.00785,.10412),(outer-side*.0100,eye_y+eye_tilt-.00005,.10403)],.00011,EYE_WET)
 add_ellipse_surface(HEAD,f'InnerCanthusV128_{side}',inner+side*.0014,eye_y-eye_tilt+.00025,.10408,.00135,.00058,EYE_WET,18)
 # Lower, fuller brows match the key-art expression and visually reduce the oversized forehead.
 add_strand(HEAD,f'BrowV119_{side}',[(ex-side*.0240,.0580,.1030),(ex,.0634,.10355),(ex+side*.0265,.0560,.10305)],.00068,HAIR)
 add_blink_lid_surface(HEAD,'BL_EYELID_L' if side<0 else 'BL_EYELID_R',ex,eye_y,eye_rx,eye_ry,SKIN)

# v7.1 integrated portrait accents: head topology owns all nose/mouth depth.
# Only a shallow colour patch remains for the lips, following the actual mouth plane instead of floating in front of it.
# v11.4 surface accents follow the rebuilt shell instead of the retired v8 face depth.
add_panel(HEAD,'UpperLipV119_L',[(-.0294*FACE120['frontal']['mouthWidth'],-.0835,.1268),(-.0135,-.0796,.1284),(0,-.0827,.1302),(0,-.0867,.1305),(-.0115,-.0860,.1292),(-.0282*FACE120['frontal']['mouthWidth'],-.0878,.1273)],.00034*FACE120['surface']['lipThickness'],LIP)
add_panel(HEAD,'UpperLipV119_R',[(0,-.0827,.1302),(.0135,-.0796,.1284),(.0294*FACE120['frontal']['mouthWidth'],-.0835,.1268),(.0282*FACE120['frontal']['mouthWidth'],-.0878,.1273),(.0115,-.0860,.1292),(0,-.0867,.1305)],.00034*FACE120['surface']['lipThickness'],LIP)
add_panel(HEAD,'LowerLipV119',[(-.0282*FACE120['frontal']['mouthWidth'],-.0880,.1272),(0,-.0879,.1301),(.0282*FACE120['frontal']['mouthWidth'],-.0880,.1272),(.0238*FACE120['frontal']['mouthWidth'],-.0944,.1270),(0,-.0985,.1291),(-.0238*FACE120['frontal']['mouthWidth'],-.0944,.1270)],.00039*FACE120['surface']['lipThickness'],LIP)
add_strand(HEAD,'MouthSeamV119',[(-.0300,-.0868,.1272),(-.0135,-.0860,.1290),(0,-.0869,.1307),(.0135,-.0860,.1290),(.0300,-.0868,.1272)],.000075,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV119_{side}',side*.0065*FACE120['profile']['noseWidth'],-.0580,.1368,.00205*FACE120['surface']['nostrilScale'],.00088*FACE120['surface']['nostrilScale'],FACE_DARK,20)

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
add_rear_hair_shell(HEAD,'HairRearShellV105',[
 # The old shell collapsed to 0.30*head_w at ear height, exposing a large skin-colored side plane.
 # These first three sections stay outside the cranium and slightly behind EarV103, so the ear remains readable.
 (-.055,head_w*.410,head_d*.340,-head_d*.125),
 (-.025,head_w*.472,head_d*.455,-head_d*.102),
 (.012,head_w*.505,head_d*.535,-head_d*.078),
 (.052,head_w*.520,head_d*.565,-head_d*.058),
 (.096,head_w*.528,head_d*.562,-head_d*.042),
 (.138,head_w*.490,head_d*.517,-head_d*.033),
 (.170,head_w*.394,head_d*.422,-head_d*.024),
 (.194,head_w*.230,head_d*.270,-head_d*.013),
 (.206,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,48)

# v10.1: a scalp-tight undercap provides dark root coverage without becoming the visible silhouette.
# head_w is the full measured head width, so ~0.46*head_w tracks the actual cranium instead of floating far outside it.
for side in (-1,1):
 add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV105_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.442, head_d*.012,.032,.0012),
  (.098,head_w*.462, head_d*.000,.041,.0015),
  (.068,head_w*.465,-head_d*.014,.041,.0015),
  (.043,head_w*.446,-head_d*.031,.034,.0013),
  (.022,head_w*.421,-head_d*.049,.024,.0010),
  (.004,head_w*.402,-head_d*.067,.015,.0008),
  (-.014,head_w*.406,-head_d*.085,.010,.0007),
  (-.031,head_w*.424,-head_d*.101,.008,.0006),
  (-.045,head_w*.442,-head_d*.113,.003,.0003)
 ],HAIR,17)

 # Rounded swept locks sit above the undercap. Each covers only a narrow front/back band, so profile reads as layered hair.
 add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.026),
  (side*head_w*.420,.145, head_d*.018),
  (side*head_w*.468,.108, head_d*.006),
  (side*head_w*.486,.068,-head_d*.018),
  (side*head_w*.482,.028,-head_d*.052),
  (side*head_w*.468,.010,-head_d*.088),
  (side*head_w*.442,-.004,-head_d*.118)
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

# v12.4 hero crown breakup: large overlapping sweeps give the top silhouette direction and asymmetry.
_crown_v124=[
 ('L',[(-.010,.214,-.003),(-.032,.209,.008),(-.058,.198,.020),(-.084,.180,.025),(-.103,.158,.014),(-.111,.132,-.006)],[.008,.021,.037,.046,.039,.009],[.003,.007,.011,.014,.012,.003],HAIR),
 ('C',[(.006,.216,-.012),(.022,.210,.002),(.035,.198,.017),(.043,.181,.029),(.038,.160,.035),(.024,.138,.027)],[.007,.019,.034,.043,.036,.008],[.003,.006,.010,.013,.011,.003],HAIR_HI),
 ('R',[(.018,.213,-.006),(.044,.207,.005),(.070,.195,.018),(.091,.176,.022),(.105,.151,.008),(.108,.124,-.014)],[.008,.022,.039,.047,.037,.009],[.003,.007,.011,.014,.011,.003],HAIR)
]
for _name,_pts,_widths,_depths,_mat in _crown_v124:
 add_smooth_lock(HEAD,f'HeroCrownV124_{_name}',_pts,_widths,_depths,_mat,14,7)
# A pair of long direction lines makes the crown read as hair rather than a smooth helmet under mobile lighting.
add_strand(HEAD,'HeroCrownHiV124_L',[(-.026,.207,.010),(-.058,.191,.025),(-.092,.158,.016),(-.106,.132,-.004)],.000075,HAIR_HI)
add_strand(HEAD,'HeroCrownHiV124_R',[(.038,.205,.007),(.070,.189,.023),(.099,.154,.012),(.106,.126,-.010)],.000060,HAIR_HI)

# v9.0: the fringe is born inside the existing crown cap instead of being patched to it with blobs.
# The first two samples are narrow and hidden under the cap; width only opens after the path exits the crown.
add_fringe_surface_v85(HEAD,'FringeSurfaceV90_Main',[(-.008,.214,.004),(-.028,.207,.019),(-.050,.199,.036),(-.070,.188,.053),(-.076,.174,.070),(-.057,.157,.087),(-.025,.139,.101),(.012,.122,.108),(.052,.109,.110),(.090,.101,.106)],[.004,.010,.026,.052,.082,.101,.098,.078,.047,.014],[.0004,.0008,.0016,.0030,.0044,.0053,.0050,.0040,.0025,.0008],HAIR,.0027)
add_fringe_surface_v85(HEAD,'FringeSurfaceV90_Over',[(.004,.211,.006),(-.010,.204,.021),(-.028,.197,.039),(-.041,.186,.056),(-.028,.169,.075),(-.002,.151,.092),(.030,.135,.102),(.065,.121,.107),(.099,.112,.104)],[.003,.008,.019,.040,.060,.069,.060,.037,.010],[.0003,.0007,.0015,.0028,.0039,.0044,.0038,.0024,.0007],HAIR_HI,.0022)
# Direction lines start only after the root is already covered by the crown cap.
add_strand(HEAD,'FringeFineV90_A',[(-.067,.188,.054),(-.050,.159,.088),(.024,.122,.109)],.000034,HAIR_HI)
add_strand(HEAD,'FringeFineV90_B',[(-.039,.186,.057),(.000,.153,.092),(.078,.120,.106)],.000032,HAIR_HI)
# v11.9 asymmetric portrait bangs: narrower overlapping locks break up the old helmet-like sweep and
# lower the visual hairline to the brow/outer-eye zone, matching the current Parry Doll key art.
_bang_specs=[
 ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.100,.111),(-.059,.073,.111),(-.068,.047,.106)],[.0058,.0092,.0094,.0058,.00135]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.116,.113),(-.025,.090,.116),(-.036,.066,.111)],[.0060,.0100,.0104,.0062,.00145]),
 ('C',[(-.016,.199,.051),(-.003,.160,.091),(.012,.124,.112),(.018,.096,.117),(.010,.070,.114)],[.0065,.0115,.0120,.0080,.0018]),
 ('D',[(.017,.198,.050),(.028,.160,.088),(.040,.126,.109),(.050,.100,.114),(.056,.076,.110)],[.0065,.0110,.0120,.0080,.0018]),
 ('E',[(.047,.187,.066),(.061,.151,.094),(.073,.118,.107),(.081,.091,.108),(.087,.066,.103)],[.0070,.0115,.0120,.0075,.0017])
]
for _name,_pts,_widths in _bang_specs:
 add_smooth_lock(HEAD,f'KeyArtBangV119_{_name}',_pts,_widths,[.0045,.0060,.0062,.0046,.0012],HAIR,12,6)
# Fine warm highlights trace only three locks, keeping the mass dark while revealing strand direction.
for _name,_pts in (
 ('B',[(-.044,.181,.070),(-.029,.143,.102),(-.023,.094,.116),(-.038,.051,.112)]),
 ('C',[(-.013,.191,.054),(.001,.153,.095),(.016,.112,.115),(.011,.065,.114)]),
 ('D',[(.022,.190,.054),(.033,.151,.093),(.047,.112,.112),(.056,.073,.110)])):
 add_strand(HEAD,f'KeyArtBangHiV119_{_name}',_pts,.000055,HAIR_HI)
# v13.2 profile eye-frame strands: fine upper/lower guides around, not across, the near eye.
add_strand(HEAD,'ProfileEyeFrameV132_L_Upper',[(-.058,.110,.112),(-.064,.086,.114),(-.066,.064,.112),(-.062,.048,.108)],.000032,HAIR_HI)
add_strand(HEAD,'ProfileEyeFrameV132_L_Lower',[(-.074,.040,.106),(-.071,.016,.103),(-.064,-.012,.099),(-.058,-.040,.094)],.000030,HAIR)

# v13.1 reference-profile wisps: fine face framing without hiding the eye.
add_strand(HEAD,'ProfileWispV131_L',[(-.076,.122,.108),(-.083,.082,.107),(-.080,.045,.097),(-.068,-.006,.093),(-.058,-.060,.094)],.000040,HAIR)
add_strand(HEAD,'ProfileWispV131_R',[(.078,.126,.106),(.086,.086,.109),(.084,.042,.106),(.073,.004,.100),(.064,-.032,.095)],.000042,HAIR_HI)

# v13.6 supplied-reference loose profile wisps.
for _side in (-1,1):
 add_strand(HEAD,f'ReferenceWispV136_A_{_side}',[(_side*.080,.118,.103),(_side*.085,.072,.107),(_side*.078,.020,.103),(_side*.066,-.035,.095),(_side*.057,-.082,.086)],.000032,HAIR)
 add_strand(HEAD,f'ReferenceWispV136_B_{_side}',[(_side*.067,.145,.094),(_side*.073,.098,.102),(_side*.070,.052,.104),(_side*.058,.006,.098),(_side*.050,-.050,.091)],.000028,HAIR_HI)
 add_strand(HEAD,f'ReferenceWispV136_C_{_side}',[(_side*.095,.088,.080),(_side*.098,.040,.086),(_side*.090,-.010,.083),(_side*.078,-.055,.077)],.000026,HAIR)

# v12.0 modular hair-fit pass: broad temple layers bridge fringe to side/back mass.
for _side in (-1,1):
 _sw=ASSEMBLY120['hair']['templeLockWidth']*.62;_sd=ASSEMBLY120['hair']['templeLockDepth']*.56
 _pts=[(_side*.086,.170,.052),(_side*.098,.132,.075),(_side*.106,.090,.090),(_side*.108,.045,.084),(_side*.102,.000,.069),(_side*.094,-.036,.054)]
 _widths=[_sw*.70,_sw, _sw*1.04,_sw*.88,_sw*.62,_sw*.20]
 _depths=[_sd*.72,_sd,_sd*1.02,_sd*.88,_sd*.60,_sd*.18]
 add_smooth_lock(HEAD,f'TempleLayerV120_{_side}',_pts,_widths,_depths,HAIR,12,6)
 add_strand(HEAD,f'TempleLayerHiV120_{_side}',[(_side*.087,.165,.057),(_side*.099,.126,.081),(_side*.106,.080,.091),(_side*.101,.002,.070)],.000038,HAIR_HI)
# v8.2 deliberately omits isolated cheek wisps. At portrait scale even a physically thin curve
# reads as a detached black scratch in profile; the existing broad temple/face locks carry the hairstyle.

# v8.3: no isolated front temple locks; the rear shell/fringe own this silhouette continuously.

for _side in (-1,1):
 add_box(HEAD,f'ProfileHairOrnamentV136_{_side}',(_side*.105,.090,-head_d*.365),(.011,.145,.013),SILVER,.0025,rot=(0,0,-_side*.055))
 add_box(HEAD,f'ProfileHairOrnamentTipV136_{_side}',(_side*.106,.016,-head_d*.365),(.016,.026,.016),SILVER,.003)
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
# v12.4 asymmetric hero pony contour: wide near the shoulder blades, tapering cleanly below the hips.
_hero_pony_v124=[
 ('L',[( -.020,.145,-head_d*.548),(-.050,.035,-head_d*.618),(-.105,-.180,-.274),(-.205,-.430,-.222),(-.295,-.720,-.170),(-.310,-1.000,-.132),(-.245,-1.270,-.105),(-.150,-1.520,-.080)],[.045,.082,.112,.132,.140,.112,.068,.010],HAIR),
 ('M',[( .012,.146,-head_d*.552),(.020,.030,-head_d*.620),(.035,-.190,-.268),(.060,-.455,-.214),(.082,-.755,-.163),(.095,-1.055,-.125),(.082,-1.315,-.100),(.060,-1.535,-.078)],[.040,.076,.104,.124,.128,.102,.060,.009],HAIR_HI),
 ('R',[( .032,.143,-head_d*.546),(.058,.030,-head_d*.616),(.108,-.175,-.270),(.180,-.420,-.220),(.235,-.700,-.172),(.245,-.970,-.134),(.205,-1.230,-.107),(.130,-1.480,-.084)],[.043,.080,.108,.126,.132,.105,.064,.010],HAIR)
]
for _name,_pts,_widths,_mat in _hero_pony_v124:
 add_smooth_lock(PONY,f'HeroPonyV124_{_name}',_pts,_widths,[.026,.040,.050,.055,.052,.043,.029,.007],_mat,16,8)
add_strand(PONY,'HeroPonyHiV124_L',[(-.045,.030,-head_d*.620),(-.142,-.300,-.244),(-.280,-.720,-.168),(-.270,-1.120,-.118),(-.165,-1.470,-.086)],.00018,HAIR_HI)
add_strand(PONY,'HeroPonyHiV124_R',[(.052,.030,-head_d*.616),(.135,-.290,-.242),(.224,-.700,-.170),(.226,-1.080,-.121),(.142,-1.430,-.087)],.00014,HAIR_HI)

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
 add_sphere(group,'DeltoidBlendV59'+name,(0,-.430,0),(ua*1.03,.087,ua_d*1.02),SKIN,30,20)
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

# v12.0 modular assembly: Body is the scale reference; Head and Hair remain separately selectable/reviewable.
def _under(obj,ancestor):
 q=obj.parent
 while q:
  if q is ancestor:return True
  q=q.parent
 return False
def _reparent_keep_world(obj,target):
 mw=obj.matrix_world.copy();obj.parent=target;obj.matrix_world=mw
def _materials(obj):
 return {m.name for m in getattr(obj.data,'materials',[]) if m}

for o in[ROOT,BODY_ASSET,PELVIS,TORSO,HEAD,HEAD_ASSET,HAIR_ASSET,FACE_ASSET,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:
 o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
# Expression pivots use the same measured eye/mouth centers as the visible v12 geometry.
EYE_L.location=bpos((-.0452*ASSEMBLY120['head']['eyeSpacing'],.0295,.1040));EYE_R.location=bpos((.0452*ASSEMBLY120['head']['eyeSpacing'],.0295,.1040));MOUTH_ASSET.location=bpos((0,-.0880,.1290))
EYE_L.rotation_euler=EYE_R.rotation_euler=MOUTH_ASSET.rotation_euler=(0,0,0);EYE_L.scale=EYE_R.scale=MOUTH_ASSET.scale=(1,1,1)

_eye_tokens=('BL_EYELID','EyeSclera','IrisOuter','IrisInner','Pupil','EyeLight','UpperLash','OuterLash','LowerLid','UpperLid')
_mouth_tokens=('UpperLip','LowerLip','MouthSeam')
_face_tokens=('Brow','Nostril','Ear','Face','Philtrum','Chin','Nose')
for _o in list(bpy.data.objects):
 if _o.type!='MESH' or not _under(_o,HEAD) or _under(_o,PONY):continue
 _name=_o.name;_mats=_materials(_o);_target=None
 if any(t in _name for t in _eye_tokens):
  _target=FACE_ASSET
 elif any(t in _name for t in _mouth_tokens):_target=FACE_ASSET
 elif any(t in _name for t in _face_tokens):_target=FACE_ASSET
 elif 'Hair' in _mats or 'Hair Highlight' in _mats or 'HairTie' in _name or 'Fringe' in _name or 'Bang' in _name or 'TempleLayer' in _name:_target=HAIR_ASSET
 else:_target=HEAD_ASSET
 _reparent_keep_world(_o,_target)
# Keep the existing dynamic pony root working, but move the complete hair subsystem under its own asset root.
_reparent_keep_world(PONY,HAIR_ASSET)
ROOT['character_revision']='v13.7';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.7';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.6';HAIR_ASSET['reference_profile_hair_revision']='v13.6';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.7';FACE_ASSET['profile_iris_volume_revision']='v13.7';FACE_ASSET['profile_side_plane_revision']='v13.7';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'


bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0]+'.blend')
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
print('Reference ratios:',{'H':H,'shoulder_half':DW['shoulder_joint_half_width'],'hip_half':DW['hip_joint_half_width'],'bust_w':round(bust_w,4),'waist_w':round(waist_w,4),'pelvis_w':round(pelvis_w,4)})
print('Wrote',OUT,os.path.getsize(OUT),'bytes')
