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
SCLERA=material('Sclera',(0.58,0.565,0.550),0,.64)
IRIS=material('Iris',(0.050,0.038,0.040),.01,.52)
IRIS_INNER=material('Iris Inner',(0.205,0.150,0.136),.01,.54)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.30,0.105,0.120),0,.68)
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


def add_anime_head_v60(p,name,mat,segments=96,rings=48):
 # Smooth UV topology replaces row-profile rings that produced horizontal shading bands.
 verts=[]
 top=bpos((0,.179,0));bottom=bpos((0,-.151,0));verts.append(top)
 for r in range(1,rings):
  theta=math.pi*r/rings
  sy=math.cos(theta);rad=math.sin(theta)
  yy=.014+.165*sy
  # Adult/anime silhouette: broad cranium, tapered lower cheek and compact chin.
  lower=max(0.0,min(1.0,(-.030-yy)/.120))
  cheek=math.exp(-((yy+.010)/.060)**2)
  width=.132*(1.0-.300*lower+.030*cheek)
  for i in range(segments):
   phi=2*math.pi*i/segments
   cp=math.cos(phi);sp=math.sin(phi)
   x=width*rad*cp
   depth=(.103 if sp<0 else .0975)*rad
   z=depth*sp
   if sp>0:
    fm=sp**2.0
    # Recess the eye sockets while supporting the zygomatic plane.
    for side in (-1,1):
     ex=side*.0415
     z-=fm*.0058*math.exp(-((x-ex)/.026)**2-((yy-.033)/.022)**2)
     z+=fm*.0044*math.exp(-((x-side*.054)/.035)**2-((yy+.004)/.040)**2)
    # Restrained central profile: bridge, small tip, philtrum break and chin support.
    z+=fm*.0054*math.exp(-(x/.019)**2-((yy+.002)/.052)**2)
    z+=fm*.0140*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)
    z-=fm*.0036*math.exp(-(x/.018)**2-((yy+.061)/.012)**2)
    z+=fm*.0046*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)
    z+=fm*.0060*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)
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
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'EarV60_{side}',(side*.126,-.018,-.012),(.009,.021,.008),SKIN,20,12)

# Large but adult almond eyes seated directly on the smooth shell.
face_front=.0974
eye_y=.0308
eye_x=.0450
eye_rx=.0425
eye_ry=.0129
eye_tilt=.0030
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV60_{side}',(ex,eye_y,.0835),(.0205,.0160,.0122),SCLERA,46,28)
 add_almond_surface(HEAD,f'EyeOpeningV60_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00115,SCLERA,64,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV60_{side}',ex,eye_y,face_front+.0014,.0223,.0117,IRIS,48)
 add_ellipse_surface(HEAD,f'IrisInnerV60_{side}',ex,eye_y-.0002,face_front+.0020,.0165,.0088,IRIS_INNER,42)
 add_ellipse_surface(HEAD,f'PupilV60_{side}',ex,eye_y-.0002,face_front+.0026,.0033,.0040,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV60_{side}',ex-side*.0052,eye_y+.0052,face_front+.0032,.0016,.0014,SCLERA,18)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 add_strand(HEAD,f'UpperLashV60_{side}',[(inner,eye_y-eye_tilt+.0012,face_front+.0025),(ex,eye_y+.0137,face_front+.0030),(outer,eye_y+eye_tilt+.0011,face_front+.0026)],.00042,HAIR)
 add_strand(HEAD,f'LowerLidV60_{side}',[(inner+side*.004,eye_y-eye_tilt-.0003,face_front+.0018),(ex,eye_y-.0081,face_front+.0021),(outer-side*.004,eye_y+eye_tilt-.0003,face_front+.0018)],.00012,FACE_DARK)
 add_strand(HEAD,f'BrowV60_{side}',[(ex-side*.027,.067,.101),(ex,.075,.103),(ex+side*.032,.064,.1015)],.00052,HAIR)

# v6.1 explicit portrait accents remain shallow; they only make the profile readable.
add_sphere(HEAD,'NoseBridgeV69',(0,-.006,.1082),(.0071,.037,.0058),SKIN,30,20)
add_sphere(HEAD,'NoseTipV69',(0,-.043,.1218),(.0097,.0096,.0082),SKIN,32,20)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV69_{side}',(side*.0064,-.049,.1138),(.0045,.0056,.0040),SKIN,22,14)
 add_sphere(HEAD,f'NostrilV69_{side}',(side*.0039,-.0538,.1188),(.00034,.00025,.00021),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV69',0,-.0762,.1112,.0254,.0037,.00078,LIP,58,1,0.0)
add_almond_surface(HEAD,'LowerLipV69',0,-.0832,.1120,.0248,.0042,.00088,LIP,58,1,0.0)
add_strand(HEAD,'MouthSeamV69',[(-.0212,-.0799,.1125),(0,-.0806,.1129),(.0212,-.0799,.1125)],.000095,FACE_DARK)

# Hair v5.9: broad layered side sweep with an open eye line, plus a much fuller high pony cascade.
add_section_mesh(HEAD,'HairTopCapV59',[
 (.064,head_w*.452,head_d*.442,head_d*.492,-.018),
 (.098,head_w*.446,head_d*.434,head_d*.482,-.020),
 (.133,head_w*.402,head_d*.392,head_d*.438,-.021),
 (.164,head_w*.312,head_d*.302,head_d*.344,-.018),
 (.189,head_w*.187,head_d*.181,head_d*.209,-.010),
 (.204,head_w*.070,head_d*.070,head_d*.080,-.002)
],HAIR,56)
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

# Two wide dark planes establish a natural side-swept fringe instead of repeated finger-like locks.
add_flow_ribbon(HEAD,'FringeSweepV59_A',[(-.112,.182,.012),(-.096,.160,.045),(-.066,.134,.074),(-.027,.107,.096),(.018,.085,.106),(.060,.071,.110)],[.086,.088,.080,.064,.046,.028],.00145,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV59_B',[(-.047,.184,.012),(-.025,.160,.047),(.010,.133,.077),(.048,.106,.099),(.085,.083,.108),(.114,.069,.110)],[.072,.071,.064,.050,.035,.021],.00140,HAIR)
# Short overlapping strips break the broad masses without covering the eyes.
add_flow_ribbon(HEAD,'FringeLayerV59_C',[(-.083,.177,.014),(-.059,.153,.049),(-.026,.126,.078),(.012,.101,.100),(.043,.085,.108)],[.035,.037,.033,.024,.012],.00115,HAIR_HI)
add_flow_ribbon(HEAD,'FringeLayerV59_D',[(-.015,.179,.013),(.010,.153,.049),(.043,.125,.079),(.078,.099,.101),(.105,.082,.108)],[.032,.034,.030,.022,.011],.00112,HAIR)
add_strand(HEAD,'FringeFineV59_A',[(-.096,.173,.018),(-.057,.137,.074),(.012,.092,.109)],.000085,HAIR_HI)
add_strand(HEAD,'FringeFineV59_B',[(-.036,.176,.018),(.014,.135,.077),(.091,.087,.108)],.000080,HAIR_HI)
add_strand(HEAD,'FringeFineV63_C',[(-.116,.170,.017),(-.085,.142,.061),(-.032,.105,.101)],.000070,HAIR_HI)
add_strand(HEAD,'FringeFineV63_D',[(-.068,.181,.016),(-.026,.143,.063),(.038,.096,.106)],.000072,HAIR_HI)
add_strand(HEAD,'FringeFineV63_E',[(-.005,.180,.016),(.034,.143,.064),(.095,.087,.107)],.000068,HAIR_HI)
for side in(-1,1):
 add_strand(HEAD,f'FaceWispV63_{side}',[(side*.105,.124,.094),(side*.116,.072,.101),(side*.120,.010,.099),(side*.112,-.052,.094)],.00010,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.394,.112,-head_d*.038),(side*head_w*.423,.050,-.013),(side*head_w*.428,-.028,-.016),(side*head_w*.416,-.103,-.044),(side*head_w*.401,-.178,-.064)]
 add_smooth_lock(HEAD,f'FaceLockV59_{side}',pts,[.010,.013,.0105,.0060,.0026],[.008,.009,.007,.0045,.0022],HAIR,10,5)

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
