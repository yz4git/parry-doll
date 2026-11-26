"""B12 controlled sewing test: B11 pattern coordinates quantized to 0.25 mm.
B09 torso section surrogate (26 x 48); not full body, no dynamic pose.
"""
import bpy,sys,math,json,zlib,base64,struct,statistics,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
n=int(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);out.mkdir(parents=True,exist_ok=True)
assert n in (4,8)
d=json.loads(Path(__file__).with_name('n4-b12-pattern-data.json').read_text())
def decode(k,R,C):
 raw=zlib.decompress(base64.b64decode(d[k],validate=True))
 assert len(raw)==R*C*4,(k,len(raw),R*C*4)
 a=struct.unpack('<'+'h'*(R*C*2),raw)
 grid=[[[0,0] for i in range(C)] for j in range(R)]
 for j in range(R):
  for i in range(C):
   for h in range(2):
    grid[j][i][h]=a[(j*C+i)*2+h]+(grid[j-1][i][h] if j else 0)+(grid[j][i-1][h] if i else 0)-(grid[j-1][i-1][h] if j and i else 0)
 return [[[x*.00025 for x in pt] for pt in row] for row in grid]
R=21;C=48//n+1
q=decode('flat'+str(n),R,n*C);target=decode('target',21,48);body=decode('body',26,48)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=140;scene.render.fps=24
def mesh(name,v,e,f):
 m=bpy.data.meshes.new(name);m.from_pydata(v,e,f);m.update();ob=bpy.data.objects.new(name,m);scene.collection.objects.link(ob);return ob
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.75;return m
navy=mat('Navy toile',(.055,.10,.20));slate=mat('Alternate panel',(.10,.18,.30));gray=mat('Neutral collision surface',(.38,.40,.43))
v=[Vector((x,y,1.025+j*.015)) for j,row in enumerate(body) for x,y in row];f=[]
for j in range(25):
 for i in range(48):
  a=j*48+i;b=j*48+(i+1)%48;f.append((a,b,b+48,a+48))
f += [tuple(reversed(range(48))),tuple(range(25*48,26*48))]
man=mesh('B09 section surrogate 26x48',v,[],f);man.data.materials.append(gray)
for poly in man.data.polygons:poly.use_smooth=True
man.modifiers.new('Body collision','COLLISION');man.collision.thickness_outer=.0025
tree=BVHTree.FromPolygons(v,f,all_triangles=False)
p=[];flat=[];faces=[];seams=[];rows=[];uv=[]
for k in range(n):
 row=[];ids=[];fl=[]
 for j in range(R):
  r=[]
  for i in range(C):
   a=k*(C-1)+i;x,y=target[j][a%48];r.append(len(p));p.append(Vector((x,y,1.055+j*.015)));fl.append(q[j][k*C+i])
  row.append(r);ids.extend(r)
 rows.append(row)
 c=sum((p[i] for i in ids),Vector())/len(ids);normal=Vector((c.x,c.y-.035,0)).normalized();t=Vector((-normal.y,normal.x,0));ux=statistics.mean(x[0] for x in fl);uy=min(x[1] for x in fl);base=Vector((c.x,c.y,1.055))+normal*.10
 for x,y in fl:flat.append(base+t*(x-ux)+Vector((0,0,y-uy)));uv.append((x,y))
 for j in range(R-1):
  for i in range(C-1):
   a,b=row[j][i:i+2];c,e=row[j+1][i:i+2];faces.extend([(a,b,e),(a,e,c)])
for k in range(n):
 for j in range(R):seams.append((rows[k][j][-1],rows[(k+1)%n][j][0]))
assert len(p)==len(flat)==n*R*C and len(seams)==n*R
cloth=mesh('Flat B11 patterns',flat,seams,faces);cloth.data.materials.append(navy);cloth.data.materials.append(slate)
for poly in cloth.data.polygons:poly.material_index=(poly.index//((R-1)*(C-1)*2))%2
pin=cloth.vertex_groups.new(name='Supported top edge');cloth.shape_key_add(name='Basis');key=cloth.shape_key_add(name='Top edge fit target')
for row in rows:
 for i in row[-1]:pin.add([i],1,'REPLACE');key.data[i].co=p[i]
key.value=0;key.keyframe_insert(data_path='value',frame=1);key.value=1;key.keyframe_insert(data_path='value',frame=50);key.value=0;scene.frame_set(1)
mod=cloth.modifiers.new('Cloth physical sewing','CLOTH');s=mod.settings;s.quality=16;s.mass=.22;s.tension_stiffness=45;s.compression_stiffness=45;s.shear_stiffness=30;s.bending_stiffness=1.5;s.use_sewing_springs=True;s.sewing_force_max=18;s.vertex_group_mass=pin.name;s.pin_stiffness=1;s.effector_weights.gravity=.15
col=mod.collision_settings;col.use_collision=True;col.distance_min=.003;col.use_self_collision=True;col.self_distance_min=.002;col.collision_quality=8;mod.point_cache.frame_start=1;mod.point_cache.frame_end=140
edges=sorted({tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces for i in range(len(f))});rest=[(flat[a]-flat[b]).length for a,b in edges]
def positions():
 e=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();r=[v.co.copy() for v in m.vertices];e.to_mesh_clear();return r
def pct(a,q):
 a=sorted(a);return a[min(len(a)-1,int(q*(len(a)-1)))]
def measure(r):
 gaps=[(r[a]-r[b]).length*1000 for a,b in seams];stretch=[(r[a]-r[b]).length/max(l,1e-8) for (a,b),l in zip(edges,rest)];inside=0;worst=0;fc=0
 for x in r:
  c,no,i,dist=tree.find_nearest(x)
  if c is not None and (x-c).dot(no)<-.001:inside+=1;worst=max(worst,-(x-c).dot(no)*1000)
 for a,b,c in faces:
  x=(r[a]+r[b]+r[c])/3;co,no,i,dist=tree.find_nearest(x)
  if co is not None and (x-co).dot(no)<-.001:fc+=1
 return dict(seam_median_mm=statistics.median(gaps),seam_max_mm=max(gaps),seams_over_10mm=sum(x>10 for x in gaps),seams_over_5mm=sum(x>5 for x in gaps),edge_stretch_p95=pct(stretch,.95),absolute_edge_strain_p95_pct=pct([abs(x-1)*100 for x in stretch],.95),inside_vertices_approx=inside,inside_face_centroids_approx=fc,max_penetration_mm_approx=worst,target_distance_mean_mm=statistics.mean((a-b).length*1000 for a,b in zip(r,p)))
def aim(ob,t):ob.rotation_euler=(Vector(t)-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world.color=(.22,.22,.22)
cam=bpy.data.objects.new('Review',bpy.data.cameras.new('Review'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.76
for i,(x,y,z,power) in enumerate([(-.6,1,1.9,55),(.7,.7,1.4,35),(0,-.7,1.8,40)]):
 l=bpy.data.lights.new('Area'+str(i),'AREA');l.energy=power;l.size=.7;o=bpy.data.objects.new(l.name,l);scene.collection.objects.link(o);o.location=(x,y,z);aim(o,(0,0,1.22))
def render(name,ang):
 a=math.radians(ang);cam.location=(math.sin(a)*1.8,math.cos(a)*1.8,1.32);aim(cam,(0,0,1.22));scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.frame_set(1);history={'1':measure(positions())}
bpy.ops.wm.save_as_mainfile(filepath=str(out/'setup.blend'));render('before_45',45)
for frame in range(2,141):
 scene.frame_set(frame);bpy.context.view_layer.update()
 if frame in (25,50,75,100,140):
  history[str(frame)]=measure(positions());print('B12_FRAME',frame,json.dumps(history[str(frame)]),flush=True)
r=positions();assert all(math.isfinite(x) for v in r for x in v)
report={'panels':n,'vertices':len(p),'faces':len(faces),'seams':len(seams),'quantization_mm':.25,'body':'B09 actual section samples, 26x48, clipped upper arms, not exact body','history':history,'limitations':'top edge pinned; approximate penetration test; no shoulder/armholes; not finished vest'}
(out/'report.json').write_text(json.dumps(report,indent=2));print('B12_RESULT',json.dumps(report),flush=True)
final=mesh('Simulated torso toile',r,[],faces);final.data.materials.append(navy);final.data.materials.append(slate)
uvlayer=final.data.uv_layers.new(name='Flat pattern UV')
for poly in final.data.polygons:
 poly.use_smooth=True;poly.material_index=(poly.index//((R-1)*(C-1)*2))%2
 for l in poly.loop_indices:uvlayer.data[l].uv=uv[final.data.loops[l].vertex_index]
cloth.hide_render=True;cloth.hide_set(True);bpy.ops.wm.save_as_mainfile(filepath=str(out/'result.blend'))
for name,ang in [('after_front',0),('after_45',45),('after_side',90),('after_back',180)]:render(name,ang)
bpy.ops.object.select_all(action='DESELECT');final.select_set(True);bpy.context.view_layer.objects.active=final;bpy.ops.export_scene.gltf(filepath=str(out/'result.glb'),export_format='GLB',use_selection=True)
