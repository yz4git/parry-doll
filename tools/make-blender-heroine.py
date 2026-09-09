import bpy, os

OUT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','dist','assets','models','heroine-blender.glb'))
os.makedirs(os.path.dirname(OUT),exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def bpos(v):x,y,z=v;return(x,-z,y)
def bscale(v):x,y,z=v;return(x,z,y)
def material(name,color,metallic=0.0,roughness=.45):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metallic;b.inputs['Roughness'].default_value=roughness;return m
SKIN=material('Skin',(0.88,0.68,0.61),0,.46);BLACK=material('Suit Black',(0.018,0.026,0.042),.06,.32);WHITE=material('Porcelain White',(0.88,0.91,0.92),.22,.24);SILVER=material('Silver',(0.48,0.56,0.63),.78,.20);HAIR=material('Hair',(0.028,0.020,0.038),.02,.35);HAIR_HI=material('Hair Highlight',(0.11,0.055,0.13),.03,.31);SCLERA=material('Sclera',(0.82,0.81,0.78),0,.38);IRIS=material('Iris',(0.12,0.31,0.36),.08,.20);PUPIL=material('Pupil',(0.006,0.008,0.012),0,.28);LIP=material('Lip',(0.48,0.20,0.20),0,.42);GLOW=material('Cyan Accent',(0.14,0.64,0.72),.45,.15)
def parent(o,p):o.parent=p;return o
def empty(name,p=None):
 o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o)
 if p:o.parent=p
 return o
def smooth(o):
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def add_sphere(p,name,loc,scale,mat,segments=28,rings=18):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=bpos(loc));o=bpy.context.object;o.name=name;o.scale=bscale(scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);smooth(o);return parent(o,p)
def add_box(p,name,loc,scale,mat,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=bpos(loc));o=bpy.context.object;o.name=name;o.dimensions=bscale(scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('bevel','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 smooth(o);return parent(o,p)
def add_cylinder(p,name,loc,radius,length,mat,vertices=28):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=length,location=bpos(loc));o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return parent(o,p)
def add_taper(p,name,r1,r2,mat,armor=False):
 bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=r1,radius2=r2,depth=1,location=(0,0,0));o=bpy.context.object;o.name=name+'_core';o.data.materials.append(mat);smooth(o);parent(o,p)
 add_sphere(p,name+'_jointA',(0,-.49,0),(r1*.82,r1*.88,r1*.82),mat,20,12);add_sphere(p,name+'_jointB',(0,.49,0),(r2*.82,r2*.88,r2*.82),mat,20,12)
 if armor:
  add_box(p,name+'_armor',(0,.06,.082),(max(r1,r2)*1.38,.42,.050),WHITE,.018);add_box(p,name+'_rail',(0,.04,.113),(.026,.35,.018),SILVER,.008)
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
# Narrow, vertically biased torso. Armor is thin and does not widen the shoulder line.
add_sphere(TORSO,'TorsoSuit',(0,.015,0),(.235,.335,.145),BLACK,32,20);add_sphere(TORSO,'RibShape',(0,.145,.01),(.258,.205,.155),BLACK,32,20);add_sphere(TORSO,'Waist',(0,-.225,0),(.158,.155,.120),BLACK,28,18)
add_box(TORSO,'ChestPlateL',(-.092,.12,.151),(.132,.195,.038),WHITE,.022);add_box(TORSO,'ChestPlateR',(.092,.12,.151),(.132,.195,.038),WHITE,.022);add_box(TORSO,'Sternum',(0,.075,.178),(.026,.285,.018),SILVER,.007);add_box(TORSO,'BackSpine',(0,.015,-.155),(.035,.43,.024),SILVER,.009)
for side in(-1,1):add_box(TORSO,f'Clavicle_{side}',(side*.135,.268,.126),(.115,.032,.028),SILVER,.009);add_box(TORSO,f'SideHarness_{side}',(side*.202,-.02,-.015),(.025,.38,.035),BLACK,.008)
# High waist / compact pelvis makes the legs read longer.
add_sphere(PELVIS,'PelvisSuit',(0,0,0),(.215,.145,.172),BLACK,30,18);add_box(PELVIS,'HighWaist',(0,.115,.018),(.365,.065,.175),WHITE,.019);add_box(PELVIS,'Belt',(0,.145,.035),(.405,.025,.19),SILVER,.008)
add_panel(PELVIS,'SkirtPanelL',[(-.175,.09,.01),(-.035,.09,.02),(-.055,-.57,.00),(-.245,-.46,-.02)],.025,WHITE);add_panel(PELVIS,'SkirtPanelR',[(.035,.09,.02),(.175,.09,.01),(.245,-.46,-.02),(.055,-.57,.00)],.025,WHITE)
add_panel(PELVIS,'SkirtInsetL',[(-.158,.075,-.01),(-.058,.075,0),(-.075,-.48,-.01),(-.215,-.39,-.025)],.014,BLACK);add_panel(PELVIS,'SkirtInsetR',[(.058,.075,0),(.158,.075,-.01),(.215,-.39,-.025),(.075,-.48,-.01)],.014,BLACK)
# Smaller head and readable features placed clearly in front of the face surface.
add_sphere(HEAD,'HeadSkin',(0,0,0),(.165,.205,.153),SKIN,36,24);add_sphere(HEAD,'FacePlane',(0,-.012,.123),(.143,.178,.052),SKIN,34,22);add_cylinder(HEAD,'Neck',(0,-.232,-.005),.060,.12,SKIN,24)
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*.057,.032,.184),(.043,.024,.012),SCLERA,24,14);add_sphere(HEAD,f'Iris_{side}',(side*.057,.032,.197),(.018,.018,.007),IRIS,18,12);add_sphere(HEAD,f'Pupil_{side}',(side*.057,.032,.204),(.007,.010,.004),PUPIL,14,10);add_box(HEAD,f'Brow_{side}',(side*.057,.082,.184),(.060,.010,.008),HAIR,.004)
add_sphere(HEAD,'Nose',(0,-.015,.193),(.018,.040,.018),SKIN,18,12);add_box(HEAD,'Mouth',(0,-.083,.190),(.060,.009,.007),LIP,.003)
# Hair: smaller opaque mass plus many thin front/side strands and a long layered ponytail.
add_sphere(HEAD,'HairBack',(0,.035,-.040),(.187,.222,.176),HAIR,34,22);add_sphere(HEAD,'HairCrown',(0,.112,-.002),(.190,.143,.174),HAIR,34,20)
for i in range(13):
 lane=(i-6)/6;add_strand(HEAD,f'Fringe_{i}',[(lane*.105,.175,.135),(lane*.095,.105,.174),(lane*.105-.025,.020,.191),(lane*.125-.040,-.070,.186)],.009+(i%3)*.0015,HAIR_HI if i%4==0 else HAIR)
for side in(-1,1):
 for i in range(4):add_strand(HEAD,f'SideLock_{side}_{i}',[(side*(.105+i*.014),.105,.085),(side*(.158+i*.015),-.04,.125),(side*(.178+i*.017),-.31,.075)],.0105,HAIR_HI if i==0 else HAIR)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(21):
 lane=(i-10)/10;add_strand(PONY,f'Pony_{i}',[(lane*.028,.145,-.166),(lane*.075,.01,-.275),(lane*.13,-.38,-.335),(lane*.21,-.88,-.26),(lane*.30,-1.42,-.105)],.011+(i%4)*.0015,HAIR_HI if i%6==0 else HAIR)
add_box(HEAD,'HairTie',(0,.135,-.170),(.115,.038,.044),SILVER,.011)
# Slender tapered limbs, normalized to unit Y so runtime scaling reaches joint endpoints.
for group,name,r1,r2,armor in[(UA_L,'UpperArmL',.071,.058,False),(UA_R,'UpperArmR',.071,.058,False),(FA_L,'ForearmL',.063,.050,True),(FA_R,'ForearmR',.063,.050,True),(TH_L,'ThighL',.100,.071,False),(TH_R,'ThighR',.100,.071,False),(SH_L,'ShinL',.074,.058,True),(SH_R,'ShinR',.074,.058,True)]:add_taper(group,name,r1,r2,BLACK,armor)
for group,name in[(UA_L,'L'),(UA_R,'R')]:add_box(group,'ShoulderPlate'+name,(0,.42,.070),(.115,.125,.050),WHITE,.021);add_box(group,'ShoulderTrim'+name,(0,.42,.102),(.035,.105,.016),SILVER,.006)
for group,name in[(TH_L,'L'),(TH_R,'R')]:add_box(group,'ThighStrap'+name,(0,.25,.086),(.130,.055,.023),SILVER,.009)
for group,name in[(HAND_L,'L'),(HAND_R,'R')]:add_sphere(group,'Hand'+name,(0,0,0),(.071,.095,.052),BLACK,22,14);add_box(group,'HandPlate'+name,(0,.012,.050),(.098,.082,.023),SILVER,.007)
for group,name in[(FOOT_L,'L'),(FOOT_R,'R')]:add_box(group,'Boot'+name,(0,-.025,.068),(.135,.175,.265),BLACK,.033);add_box(group,'BootPlate'+name,(0,.045,.145),(.105,.105,.070),WHITE,.017)
# Slim Blender-authored sword.
add_box(SWORD,'SwordBlade',(0,.63,0),(.045,1.26,.020),WHITE,.009);add_box(SWORD,'SwordEdge',(.021,.65,.014),(.012,1.22,.012),GLOW,.004);add_box(SWORD,'SwordGuard',(0,-.03,0),(.25,.042,.090),SILVER,.013);add_cylinder(SWORD,'SwordGrip',(0,-.17,0),.027,.23,BLACK,20);add_box(SWORD,'SwordPommel',(0,-.31,0),(.052,.052,.052),SILVER,.010)
for o in[ROOT,PELVIS,TORSO,HEAD,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
bpy.context.scene.render.engine='BLENDER_EEVEE';bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0]+'.blend');bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False);print('Wrote',OUT,os.path.getsize(OUT),'bytes')
