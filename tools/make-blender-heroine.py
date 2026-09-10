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
SKIN=material('Skin',(0.54,0.36,0.34),0,.68)
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
SCLERA=material('Sclera',(0.82,0.78,0.75),0,.50)
IRIS=material('Iris',(0.17,0.075,0.048),.01,.36)
IRIS_INNER=material('Iris Inner',(0.30,0.135,0.065),.01,.38)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.42,0.18,0.18),0,.60)
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
     z+=fm*.0180*math.exp(-((x-cheek_x)/(head_w*.110))**2-((yy+.010)/.043)**2)
     # Deep orbital bowl with a softer lower lid shelf.
     eye_x=side*head_w*.148
     z-=fm*.0165*math.exp(-((x-eye_x)/(head_w*.124))**2-((yy-.030)/.027)**2)
     z+=fm*.0048*math.exp(-((x-eye_x)/(head_w*.120))**2-((yy-.068)/.024)**2)
     z+=fm*.0030*math.exp(-((x-eye_x)/(head_w*.115))**2-((yy+.002)/.020)**2)
     # Lower-cheek hollow and nasolabial transition form a readable adult mid-face plane.
     z-=fm*.0048*math.exp(-((x-side*head_w*.275)/(head_w*.095))**2-((yy+.052)/.038)**2)
     z-=fm*.0022*math.exp(-((x-side*head_w*.105)/(head_w*.070))**2-((yy+.065)/.028)**2)
    # Continuous nose bridge, dorsum, tip and columella.
    z+=fm*.0100*math.exp(-(x/(head_w*.070))**2-((yy-.036)/.080)**2)
    z+=fm*.0300*math.exp(-(x/(head_w*.066))**2-((yy+.005)/.062)**2)
    z+=fm*.0530*math.exp(-(x/(head_w*.078))**2-((yy+.043)/.026)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.047))**2-((yy+.059)/.016)**2)
    # Soft muzzle and lip cushion, then a separate chin plane.
    z+=fm*.0220*math.exp(-(x/(head_w*.164))**2-((yy+.082)/.028)**2)
    z-=fm*.0028*math.exp(-(x/(head_w*.055))**2-((yy+.066)/.014)**2)
    z+=fm*.0240*math.exp(-(x/(head_w*.128))**2-((yy+.116)/.024)**2)
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


def add_rear_hair_shell(p,name,sections,mat,segments=36):
 verts=[]
 # Logical Z is front/back; only sample the rear half of each horizontal section.
 angles=[math.pi+.055+(math.pi-.110)*i/segments for i in range(segments+1)]
 for yy,w,depth,zoff in sections:
  for ang in angles:
   verts.append(bpos((math.cos(ang)*w,yy,zoff+math.sin(ang)*depth)))
 row=len(angles);faces=[]
 for r in range(len(sections)-1):
  base=r*row;nxt=(r+1)*row
  for i in range(row-1):faces.append((base+i,base+i+1,nxt+i+1,nxt+i))
 # Close the two temple seams and the small top/bottom openings, while leaving the face fully open.
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
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope as a single continuous surface.
# Front depth peaks at the bust while the lower back eases toward the high waist, matching the side sheet.
add_section_mesh(TORSO,'TorsoSuitV47',[
 (-.340,waist_w*.455,waist_d*.47,waist_d*.54,-.006),
 (-.285,waist_w*.440,waist_d*.46,waist_d*.55,-.004),
 (-.220,waist_w*.470,waist_d*.45,waist_d*.58,-.001),
 (-.150,bust_w*.355,bust_d*.40,bust_d*.51,.005),
 (-.075,bust_w*.430,bust_d*.41,bust_d*.59,.014),
 (.000,bust_w*.490,bust_d*.43,bust_d*.675,.027),
 (.075,bust_w*.525,bust_d*.45,bust_d*.735,.039),
 (.135,bust_w*.515,bust_d*.45,bust_d*.705,.037),
 (.195,bust_w*.455,bust_d*.42,bust_d*.585,.023),
 (.255,bust_w*.375,bust_d*.37,bust_d*.455,.010),
 (.315,bust_w*.300,bust_d*.31,bust_d*.350,.000)
],BLACK,56)
# Shallow soft-tissue support over a continuous ribcage. The outer envelope remains reference-locked.
for side in(-1,1):
 add_sphere(TORSO,f'BustSoft_{side}',(side*bust_w*.205,.105,bust_d*.330),(bust_w*.205,.082,bust_d*.180),BLACK,36,22)
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
add_panel(TORSO,'BodiceWhiteV35_L',[(-bust_w*.455,.218,bust_d*.515),(-bust_w*.255,.190,bust_d*.585),(-waist_w*.245,-.190,waist_d*.675),(-waist_w*.520,-.225,waist_d*.585)],.010,WHITE)
add_panel(TORSO,'BodiceWhiteV35_R',[(bust_w*.255,.190,bust_d*.585),(bust_w*.455,.218,bust_d*.515),(waist_w*.520,-.225,waist_d*.585),(waist_w*.245,-.190,waist_d*.675)],.010,WHITE)
for side in(-1,1):
 add_box(TORSO,f'BodiceEdgeV35_{side}',(side*bust_w*.275,.030,bust_d*.600),(.012,.330,.009),SILVER,.0035,rot=(0,0,side*.08))
 add_box(TORSO,f'UpperArmBandV35_{side}',(side*.205,.215,.000),(.040,.020,.072),BLACK,.004)

# Compact pelvis and high waist: measured 0.123H width and 0.089H depth.
add_section_mesh(PELVIS,'PelvisSuitV47',[
 (-.180,pelvis_w*.445,pelvis_d*.62,pelvis_d*.51,-.018),
 (-.080,pelvis_w*.525,pelvis_d*.60,pelvis_d*.56,-.011),
 (.040,pelvis_w*.510,pelvis_d*.54,pelvis_d*.55,-.004),
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
# One continuous measured portrait shell instead of overlapping spheres.
add_portrait_head_v44(HEAD,'HeadShellV48',[
 (-.136,head_w*.072,head_d*.154,head_d*.214,.047),
 (-.127,head_w*.148,head_d*.203,head_d*.270,.041),
 (-.113,head_w*.242,head_d*.263,head_d*.332,.032),
 (-.096,head_w*.322,head_d*.318,head_d*.388,.022),
 (-.076,head_w*.378,head_d*.364,head_d*.437,.012),
 (-.053,head_w*.414,head_d*.402,head_d*.472,.004),
 (-.028,head_w*.438,head_d*.430,head_d*.493,-.003),
 (.000,head_w*.452,head_d*.447,head_d*.503,-.008),
 (.030,head_w*.457,head_d*.458,head_d*.503,-.012),
 (.060,head_w*.449,head_d*.464,head_d*.488,-.016),
 (.090,head_w*.426,head_d*.460,head_d*.453,-.021),
 (.117,head_w*.384,head_d*.448,head_d*.407,-.026),
 (.141,head_w*.322,head_d*.424,head_d*.351,-.031),
 (.160,head_w*.236,head_d*.393,head_d*.287,-.034)
],SKIN,96)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.445,-.018,-.014),(.010,.023,.009),SKIN,18,10)
# Anatomy v5.2: larger dark-brown irises occupy the eye opening while preserving a slim almond sclera.
face_front=head_d*.531
eye_y=.0305
eye_x=head_w*.144
eye_rx=head_w*.145
eye_ry=.0180
eye_tilt=.0038
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV52_{side}',(ex,eye_y,head_d*.425),(head_w*.105,.0220,head_d*.068),SCLERA,48,30)
 add_almond_surface(HEAD,f'EyeOpeningV52_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0022,SCLERA,60,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV52_{side}',ex,eye_y,face_front+.0028,head_w*.115,.0146,IRIS,48)
 add_ellipse_surface(HEAD,f'IrisInnerV52_{side}',ex,eye_y-.0002,face_front+.0037,head_w*.074,.0107,IRIS_INNER,44)
 add_ellipse_surface(HEAD,f'PupilV52_{side}',ex,eye_y-.0003,face_front+.0045,head_w*.031,.0059,PUPIL,38)
 add_ellipse_surface(HEAD,f'EyeLightV52A_{side}',ex-side*head_w*.022,eye_y+.0058,face_front+.0052,head_w*.0066,.0028,SCLERA,20)
 add_ellipse_surface(HEAD,f'EyeLightV52B_{side}',ex+side*head_w*.012,eye_y+.0018,face_front+.0053,head_w*.0024,.0013,SCLERA,16)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLashV52_{side}',[(inner,inner_y+.0015,face_front+.0049),(ex,eye_y+.0187,face_front+.0060),(outer,outer_y+.0018,face_front+.0050)],.00062,HAIR)
 add_strand(HEAD,f'LashWingV52_{side}',[(outer,outer_y+.0018,face_front+.0050),(outer+side*head_w*.018,outer_y+.0068,face_front+.0053)],.00040,HAIR)
 add_strand(HEAD,f'BrowV52_{side}',[(ex-side*eye_rx*.75,.0700,head_d*.524),(ex,.0802,head_d*.528),(ex+side*eye_rx*.95,.0668,head_d*.524)],.00076,HAIR)

add_sphere(HEAD,'NoseTipSoftV52',(0,-.0430,head_d*.688),(.0061,.0056,.0034),SKIN,30,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV52_{side}',(side*.0056,-.0510,head_d*.670),(.00082,.00058,.00052),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV52',0,-.0768,head_d*.678,.0390,.0060,.0023,LIP,56,1,0.0)
add_almond_surface(HEAD,'LowerLipV52',0,-.0860,head_d*.674,.0375,.0070,.0026,LIP,56,1,0.0)
add_strand(HEAD,'MouthSeamV52',[(-.0330,-.0816,head_d*.685),(0,-.0830,head_d*.688),(.0330,-.0816,head_d*.685)],.00022,FACE_DARK)

# Hair v5.2: broad diagonal fringe over the open rear shell, plus spline-smoothed pony locks.
add_rear_hair_shell(HEAD,'HairRearShellV52',[
 (-.030,head_w*.300,head_d*.410,-head_d*.064),
 (.005,head_w*.425,head_d*.495,-head_d*.057),
 (.045,head_w*.497,head_d*.542,-head_d*.050),
 (.090,head_w*.520,head_d*.554,-head_d*.042),
 (.132,head_w*.482,head_d*.510,-head_d*.033),
 (.166,head_w*.390,head_d*.420,-head_d*.024),
 (.192,head_w*.230,head_d*.270,-head_d*.013),
 (.205,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,44)

# Three broad swept sheets replace the repeated pointed-lock rhythm.
swept=[
 ((-.132,.181,head_d*.005),(-.105,.151,head_d*.285),(-.045,.104,head_d*.492),(.041,.050,head_d*.556),.076,.026),
 ((-.073,.184,head_d*.004),(-.040,.151,head_d*.312),(.025,.098,head_d*.507),(.091,.034,head_d*.551),.073,.024),
 ((-.010,.179,head_d*.003),(.026,.143,head_d*.300),(.086,.087,head_d*.480),(.132,.020,head_d*.538),.062,.020),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(swept):
 add_flow_ribbon(HEAD,f'BangSweepV52_{i}',[p0,p1,p2,p3],[w0,w0*.90,w0*.63,w1],.00215,HAIR)

# Two irregular wisps break the silhouette without recreating a comb.
for i,(pts,w) in enumerate((
 ([(-.105,.174,head_d*.011),(-.052,.124,head_d*.365),(.030,.059,head_d*.555)],.00018),
 ([(-.035,.176,head_d*.009),(.026,.121,head_d*.382),(.112,.037,head_d*.544)],.00015),
)):
 add_strand(HEAD,f'BangWispV52_{i}',pts,w,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.394,.105,-head_d*.035),(side*head_w*.424,.038,-.010),(side*head_w*.428,-.043,-.012),(side*head_w*.414,-.115,-.042),(side*head_w*.400,-.190,-.063)]
 add_smooth_lock(HEAD,f'FaceLockV52_{side}',pts,[.010,.013,.011,.0065,.0028],[.0085,.0095,.0075,.0048,.0024],HAIR,10,4)

add_box(HEAD,'HairTieV52',(.014,.134,-head_d*.528),(.070,.017,.027),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(7):
 lane=(i-3)/3
 dz=lane*.019+((i%2)-.5)*.012
 # Fewer design bends, then Catmull interpolation generates the smooth cascade between them.
 pts=[
  (lane*.022+.014,.134,-head_d*.540+dz*.2),
  (lane*.032+.018,.010,-head_d*.610+dz),
  (lane*.046+.022,-.250,-.238+dz*1.15),
  (lane*.060+.027,-.560,-.190+dz*1.30),
  (lane*.072+.032,-.900,-.145+dz*1.35),
  (lane*.082+.037,-1.225,-.112+dz*1.30),
  (lane*.090+.042,-1.455-(i%3)*.020,-.092+dz*1.18)
 ]
 base=.057-.009*abs(lane)
 widths=[base*.68,base,base*.92,base*.78,base*.58,base*.32,.0050]
 depths=[.028,.038,.037,.032,.025,.015,.0042]
 add_smooth_lock(PONY,f'PonyMassV52_{i}',pts,widths,depths,HAIR_HI if i in(1,5) else HAIR,12,5)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV52_{i}',[(lane*.024+.014,.132,-head_d*.545),(lane*.034+.019,-.040,-head_d*.605),(lane*.048+.025,-.350,-.218),(lane*.065+.033,-.820,-.150),(lane*.082+.044,-1.455-(i%2)*.024,-.086)],.00026+(i%2)*.00004,HAIR_HI if i%2==0 else HAIR)

# === LIMBS ===
# Diameters come directly from the front sheet; side depth comes from the side view.
ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.58;kn=W('knee_each')*.54;calf=W('calf_each')*.53;ank=W('ankle_each')*.48
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
