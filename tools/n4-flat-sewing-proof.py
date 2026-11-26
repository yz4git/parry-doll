"""N4 flat-pattern sewing proof. Collision surrogate uses measured AF2 torso section bounds.
No character asset or reference photograph is committed. NOT the finished N4 outfit.
"""
import bpy, math, json, sys, os
variant=os.environ.get('N4_SEW_VARIANT','guided')
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=100;scene.render.fps=24
def material(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);return m
navy=material('Navy fabric',(.035,.065,.115));blue=material('Front panel',(.065,.12,.23));back=material('Back panel',(.11,.18,.28));bodymat=material('Neutral fit mannequin',(.40,.42,.43))
# (height, half-width, front depth, rear depth) measured AF2 bounds; ellipse approximation.
profile=[(1.00,.1454,.0926,.0861),(1.025,.1348,.1005,.0825),(1.05,.1296,.1115,.0757),(1.075,.1179,.112,.0639),(1.10,.1103,.112,.0401),(1.125,.0951,.117,.028),(1.15,.0887,.1173,.0174),(1.175,.0914,.1153,.0173),(1.20,.096,.1171,.0274),(1.225,.0994,.1296,.033),(1.25,.1166,.143,.0418),(1.275,.1193,.1434,.0518),(1.30,.1172,.1417,.056),(1.325,.1347,.1293,.0602),(1.35,.1495,.1046,.0619),(1.375,.1436,.0752,.0619),(1.40,.1494,.062,.0517),(1.425,.1232,.0254,.0489),(1.45,.0429,.0353,.0431),(1.49,.042,.033,.039)]
def mesh(name,v,e,f):
 m=bpy.data.meshes.new(name);m.from_pydata(v,e,f);m.update();o=bpy.data.objects.new(name,m);scene.collection.objects.link(o);return o
v=[];f=[];n=64
for z,w,front,rear in profile:
 for i in range(n):
  a=i*2*math.pi/n;v.append((w*math.cos(a),(.5*(front-rear))+.5*(front+rear)*math.sin(a),z))
for j in range(len(profile)-1):
 for i in range(n):
  a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
f += [tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]
man=mesh('AF2 measured section surrogate',v,[],f);man.data.materials.append(bodymat)
for p in man.data.polygons:p.use_smooth=True
man.modifiers.new('Torso collision','COLLISION');man.collision.thickness_outer=.002
# independently drafted planar front/back halves: (height, inner, outer) in metres
draftF=[(1.055,0,.157),(1.095,0,.155),(1.15,0,.143),(1.20,0,.15),(1.25,0,.168),(1.285,.017,.181),(1.32,.042,.157),(1.36,.055,.135),(1.40,.050,.135),(1.445,.048,.13)]
draftB=[(1.055,0,.146),(1.095,0,.143),(1.15,0,.129),(1.20,0,.133),(1.25,0,.174),(1.285,0,.176),(1.32,0,.155),(1.36,.014,.138),(1.40,.032,.135),(1.445,.048,.13)]
def interp(table,z):
 for (a,b,c),(d,e,f) in zip(table,table[1:]):
  if z<=d+1e-8:
   t=(z-a)/(d-a);return b+(e-b)*t,c+(f-c)*t
 return table[-1][1:]
# Draft width from quarter-ellipse arc length of each measured section.
def section(z):
 for a,b in zip(profile,profile[1:]):
  if z<=b[0]:
   t=max(0,min(1,(z-a[0])/(b[0]-a[0])))
   return tuple(a[i]+(b[i]-a[i])*t for i in (1,2,3))
 return profile[-1][1:]
def arc(z):
 w,fr,rr=section(z);d=(fr+rr)/2
 return sum(math.hypot(w*math.sin((i+.5)*math.pi/128),d*math.cos((i+.5)*math.pi/128)) for i in range(64))*math.pi/128
def drafted(table,z):
 a,b=interp(table,z)
 t=max(0,min(1,(1.325-z)/.04))
 return a,b*(1-t)+(arc(z)+.012)*t
R,C=27,13;v=[];faces=[];seams=[];panels={};uvs=[];rows=[]
for front in (True,False):
 for side in (-1,1):
  key=('front' if front else 'back')+('_L' if side<0 else '_R')
  ids=[];coords=[];table=draftF if front else draftB
  for j in range(R):
   z=1.055+.390*j/(R-1);a,b=drafted(table,z);row=[]
   for i in range(C):
    x=side*(a+(b-a)*i/(C-1));row.append(len(v));v.append((x,.172 if front else -.103,z));coords.append([x,z]);uvs.append((i/(C-1),j/(R-1)))
   ids.append(row)
  start=len(faces)
  for j in range(R-1):
   for i in range(C-1):
    q=(ids[j][i],ids[j][i+1],ids[j+1][i+1],ids[j+1][i])
    if (side==1)==front:q=q[::-1]
    faces.append(q)
  rows.append((start,len(faces),front));panels[key]={'ids':ids,'flat_xz_m':coords}
seam_groups={}
def sew(a,b,group):
 assert a!=b;seams.append((a,b));seam_groups.setdefault(group,[]).append((a,b))
for side in ('L','R'):
 a=panels['front_'+side]['ids'];b=panels['back_'+side]['ids']
 for j in range(R):
  z=1.055+.390*j/(R-1)
  if z<=1.285:sew(a[j][-1],b[j][-1],'side_'+side)
 for i in range(C):sew(a[-1][i],b[-1][i],'shoulder_'+side)
for where in ('front','back'):
 a=panels[where+'_L']['ids'];b=panels[where+'_R']['ids']
 # back center and closed lower front center. Coincident endpoints deliberately separated by 1 mm.
 for j in range(R):
  z=1.055+.390*j/(R-1)
  if (where=='front' and z<=1.25) or (where=='back' and z<=1.32):
   ia,ib=a[j][0],b[j][0];pa=list(v[ia]);pb=list(v[ib]);pa[0]-=.0005;pb[0]+=.0005;v[ia]=tuple(pa);v[ib]=tuple(pb);sew(ia,ib,where+'_center')
cloth=mesh('Four planar panels with loose sewing springs',v,seams,faces)
cloth.data.materials.append(blue);cloth.data.materials.append(back)
for a,b,fr in rows:
 for p in list(cloth.data.polygons)[a:b]:p.material_index=0 if fr else 1
uv=cloth.data.uv_layers.new(name='Pattern UV')
for p in cloth.data.polygons:
 for l in p.loop_indices:uv.data[l].uv=uvs[cloth.data.loops[l].vertex_index]

# V2: shoulder support through animated pin targets; the input pattern remains flat at frame 1.
pin=cloth.vertex_groups.new(name='Shoulder support')
basis=cloth.shape_key_add(name='Basis')
target=cloth.shape_key_add(name='Shoulder seam placement')
for where in ('front','back'):
 for side in ('L','R'):
  row=panels[where+'_'+side]['ids'][-1]
  for i in range(0,C,2):
   idx=row[i];pin.add([idx],1.0,'REPLACE')
   target.data[idx].co.y=.003 if where=='front' else -.003
   target.data[idx].co.z=1.45
# Sparse side-seam guides are an explicit fitting constraint, not free simulation.
if variant=='guided':
 for side in ('L','R'):
  sign=-1 if side=='L' else 1
  for j in (0,5,10,15):
   z=1.055+.390*j/(R-1);w,fr,rr=section(z)
   for where in ('front','back'):
    idx=panels[where+'_'+side]['ids'][j][-1]
    pin.add([idx],1.0,'REPLACE')
    target.data[idx].co=(sign*(w+.009),(fr-rr)/2+(.002 if where=='front' else -.002),z)
target.value=0;target.keyframe_insert(data_path='value',frame=1)
target.value=1;target.keyframe_insert(data_path='value',frame=45)
target.value=0
scene.frame_set(1)

mod=cloth.modifiers.new('Actual Blender Cloth sewing','CLOTH');s=mod.settings;s.quality=14;s.mass=.22;s.tension_stiffness=35;s.compression_stiffness=35;s.shear_stiffness=20;s.bending_stiffness=1.2;s.use_sewing_springs=True;s.sewing_force_max=14;s.effector_weights.gravity=.18;s.vertex_group_mass=pin.name;s.pin_stiffness=1.0
col=mod.collision_settings;col.use_collision=True;col.distance_min=.004;col.use_self_collision=True;col.self_distance_min=.002;col.collision_quality=8
mod.point_cache.frame_start=1;mod.point_cache.frame_end=100
(out/'patterns.json').write_text(json.dumps({'units':'m','panels':panels,'seam_pairs':seams,'seam_groups':seam_groups,'variant':variant,'profile':profile,'note':'elliptical surrogate not original body mesh'},indent=2))
# layout actual flat pattern polygons, not projection of 3D cloth
colors=['#7088b0','#526b99','#8697af','#63768f'];svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560"><rect width="1000" height="560" fill="#f5f5f5"/>']
for k,(name,p) in enumerate(panels.items()):
 ids=p['ids'];points=p['flat_xz_m'];boundary=[0]+[j*C+C-1 for j in range(R)]+[R*C-C]+[j*C for j in range(R-2,0,-1)];cx=120+250*k
 coords=lambda idx:(cx+points[idx][0]*950,455-(points[idx][1]-1.055)*950)
 poly=' '.join('%.1f,%.1f'%coords(i) for i in boundary)
 svg.append(f'<polygon points="{poly}" fill="{colors[k]}" stroke="#29364b" stroke-width="2"/>')
 for j in range(R):
  x,y=coords(j*C);xx,yy=coords(j*C+C-1);svg.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="#ffffff" opacity=".28"/>')
 svg.append(f'<text x="{cx}" y="495" text-anchor="middle" font-family="sans-serif" font-size="19">{name}</text>')
svg.append('</svg>');(out/'patterns.svg').write_text(''.join(svg))
def positions():
 dg=bpy.context.evaluated_depsgraph_get();ob=cloth.evaluated_get(dg);me=ob.to_mesh();p=[vv.co.copy() for vv in me.vertices];ob.to_mesh_clear();return p
def gap(p):
 d=sorted((p[a]-p[b]).length for a,b in seams);return {'median_mm':1000*d[len(d)//2],'max_mm':1000*max(d),'mean_mm':1000*sum(d)/len(d)}
def inside(p):
 count=0;worst=0.
 for q in p:
  if q.z<profile[0][0] or q.z>profile[-1][0]:continue
  for a,b in zip(profile,profile[1:]):
   if q.z<=b[0]:
    t=(q.z-a[0])/(b[0]-a[0]);w,fr,rr=[a[i]+(b[i]-a[i])*t for i in (1,2,3)];break
  r=math.sqrt((q.x/w)**2+((q.y-(fr-rr)/2)/((fr+rr)/2))**2)
  if r<.97:count+=1;worst=max(worst,1-r)
 return {'inside_proxy_vertices':count,'max_normalized_penetration':worst}
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=700;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.world.color=(.22,.22,.22)
cam=bpy.data.objects.new('Review',bpy.data.cameras.new('Review'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.68
for i,(x,y,z,p) in enumerate([(-.65,1.0,1.9,55),(.7,.7,1.4,35),(0,-.7,1.8,40)]):
 l=bpy.data.lights.new('Area'+str(i),'AREA');l.energy=p;l.size=.7;o=bpy.data.objects.new(l.name,l);scene.collection.objects.link(o);o.location=(x,y,z);aim(o,(0,0,1.25))
def render(name,ang):
 a=math.radians(ang);cam.location=(math.sin(a)*1.8,math.cos(a)*1.8,1.34);aim(cam,(0,0,1.25));scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.frame_set(1);initial=positions();history={'1':{**gap(initial),**inside(initial)}};bpy.ops.wm.save_as_mainfile(filepath=str(out/'sewing_setup.blend'))
render('before_45',45)
for frame in range(2,101):
 scene.frame_set(frame);bpy.context.view_layer.update()
 if frame in (10,25,50,75,100):
  q=positions();history[str(frame)]={**gap(q),**inside(q)};print('CLOTH_FRAME',frame,history[str(frame)],flush=True)
p=positions();assert all(math.isfinite(k) for q in p for k in q)
group_report={}
for k,pairs in seam_groups.items():
 ds=sorted((p[a]-p[b]).length*1000 for a,b in pairs)
 group_report[k]={'count':len(ds),'median_mm':ds[len(ds)//2],'max_mm':max(ds),'over_10mm':sum(d>10 for d in ds)}
report={'variant':variant,'seam_groups_final':group_report,'blender':bpy.app.version_string,'flat_panels':len(panels),'vertices':len(v),'faces':len(faces),'loose_sewing_edges':len(seams),'history':history,'max_vertex_motion_mm':1000*max((a-b).length for a,b in zip(initial,p)),'proxy_only':True,'solver':'Blender Cloth','finished_garment':False,'shoulder_pin_count':28,'side_guide_count':16 if variant=='guided' else 0,'animated_shoulder_targets':True}
(out/'report.json').write_text(json.dumps(report,indent=2));print('CLOTH_RESULT',json.dumps(report),flush=True)
# freeze evaluated simulation into editable separate mesh for inspection/export
final=mesh('Simulated cloth frame 100',p,[],faces);final.data.materials.append(navy)
uv=final.data.uv_layers.new(name='Pattern UV')
for poly in final.data.polygons:
 poly.use_smooth=True
 for l in poly.loop_indices:uv.data[l].uv=uvs[final.data.loops[l].vertex_index]
cloth.hide_render=True;cloth.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'sewing_result.blend'))
for name,ang in [('after_front',0),('after_45',45),('after_side',90),('after_back',180)]:render(name,ang)
bpy.ops.object.select_all(action='DESELECT');final.select_set(True);bpy.context.view_layer.objects.active=final
bpy.ops.export_scene.gltf(filepath=str(out/'cloth_proof.glb'),export_format='GLB',use_selection=True)
