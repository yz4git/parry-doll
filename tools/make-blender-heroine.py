import bpy, math, os
from mathutils import Vector

OUT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','dist','assets','models','heroine-blender.glb'))
os.makedirs(os.path.dirname(OUT),exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials):
    pass

def bpos(v):
    x,y,z=v
    return (x,-z,y)

def bscale(v):
    x,y,z=v
    return (x,z,y)

def material(name,color,metallic=0.0,roughness=.45):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Metallic'].default_value=metallic
    bsdf.inputs['Roughness'].default_value=roughness
    return m

SKIN=material('Skin',(0.78,0.50,0.43),0,.43)
BLACK=material('Suit Black',(0.025,0.035,0.055),.08,.28)
WHITE=material('Porcelain White',(0.82,0.86,0.88),.28,.23)
SILVER=material('Silver',(0.42,0.50,0.58),.76,.21)
HAIR=material('Hair',(0.035,0.025,0.045),.03,.30)
HAIR_HI=material('Hair Highlight',(0.12,0.07,0.13),.06,.26)
EYE=material('Eyes',(0.12,0.16,0.18),.05,.18)
IRIS=material('Iris',(0.16,0.30,0.34),.15,.16)
GLOW=material('Cyan Accent',(0.13,0.58,0.68),.42,.16)


def parent(obj,p):
    obj.parent=p
    return obj

def empty(name,parent_obj=None):
    o=bpy.data.objects.new(name,None)
    bpy.context.scene.collection.objects.link(o)
    if parent_obj:o.parent=parent_obj
    return o

def smooth(obj):
    if obj.type=='MESH':
        for poly in obj.data.polygons:poly.use_smooth=True
    return obj

def add_sphere(parent_obj,name,loc,scale,mat,segments=28,rings=18):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=bpos(loc))
    o=bpy.context.object;o.name=name;o.scale=bscale(scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);smooth(o);return parent(o,parent_obj)

def add_box(parent_obj,name,loc,scale,mat,bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=bpos(loc))
    o=bpy.context.object;o.name=name;o.dimensions=bscale(scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Soft bevel','BEVEL');mod.width=bevel;mod.segments=3
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    smooth(o);return parent(o,parent_obj)

def add_cylinder(parent_obj,name,loc,radius,length,mat,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=length,location=bpos(loc))
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return parent(o,parent_obj)

def add_segment(parent_obj,name,radius,mat,armor=False):
    add_cylinder(parent_obj,name+'_core',(0,0,0),radius,.72,mat,28)
    add_sphere(parent_obj,name+'_jointA',(0,-.36,0),(radius*1.03,radius*1.05,radius*1.03),mat,24,14)
    add_sphere(parent_obj,name+'_jointB',(0,.36,0),(radius*1.03,radius*1.05,radius*1.03),mat,24,14)
    if armor:
        add_box(parent_obj,name+'_armor',(0,.06,.105),(radius*1.55,.48,.075),WHITE,.025)
        add_box(parent_obj,name+'_rail',(0,.02,.155),(.035,.40,.025),SILVER,.012)

def add_panel(parent_obj,name,points,depth,mat):
    front=[(x,y,z+depth*.5) for x,y,z in points];back=[(x,y,z-depth*.5) for x,y,z in points]
    verts=[bpos(v) for v in front+back];n=len(points);faces=[]
    faces.append(tuple(range(n)));faces.append(tuple(range(2*n-1,n-1,-1)))
    for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,parent_obj)

def add_strand(parent_obj,name,pts,radius,mat):
    c=bpy.data.curves.new(name+'Curve','CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=radius;c.bevel_resolution=2;c.resolution_u=3
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for bp,p in zip(s.bezier_points,pts):bp.co=bpos(p);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.parent=parent_obj
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return o

ROOT=empty('BLENDER_HEROINE')
PELVIS=empty('BL_PELVIS',ROOT);TORSO=empty('BL_TORSO',ROOT);HEAD=empty('BL_HEAD',ROOT)
UA_L=empty('BL_UPPER_ARM_L',ROOT);FA_L=empty('BL_FOREARM_L',ROOT);HAND_L=empty('BL_HAND_L',ROOT)
UA_R=empty('BL_UPPER_ARM_R',ROOT);FA_R=empty('BL_FOREARM_R',ROOT);HAND_R=empty('BL_HAND_R',ROOT)
TH_L=empty('BL_THIGH_L',ROOT);SH_L=empty('BL_SHIN_L',ROOT);FOOT_L=empty('BL_FOOT_L',ROOT)
TH_R=empty('BL_THIGH_R',ROOT);SH_R=empty('BL_SHIN_R',ROOT);FOOT_R=empty('BL_FOOT_R',ROOT)
SWORD=empty('BL_SWORD',ROOT)

# Slender porcelain-mecha torso, deliberately narrow through shoulder/chest.
add_sphere(TORSO,'TorsoSuit',(0,.02,0),(.285,.34,.18),BLACK)
add_sphere(TORSO,'RibShape',(0,.16,.01),(.315,.23,.19),BLACK)
add_sphere(TORSO,'Waist',(0,-.23,0),(.205,.16,.15),BLACK)
add_box(TORSO,'ChestPlateL',(-.115,.12,.175),(.18,.23,.055),WHITE,.035)
add_box(TORSO,'ChestPlateR',(.115,.12,.175),(.18,.23,.055),WHITE,.035)
add_box(TORSO,'Sternum',(0,.08,.22),(.035,.31,.025),SILVER,.012)
add_box(TORSO,'BackSpine',(0,.02,-.19),(.055,.49,.035),SILVER,.014)
for side in (-1,1):
    add_box(TORSO,f'Clavicle_{side}',(side*.17,.28,.14),(.16,.045,.045),SILVER,.015)
    add_box(TORSO,f'SideHarness_{side}',(side*.245,-.01,-.02),(.035,.43,.055),BLACK,.012)

add_sphere(PELVIS,'PelvisSuit',(0,0,0),(.275,.18,.205),BLACK)
add_box(PELVIS,'HighWaist',(0,.13,.02),(.47,.085,.22),WHITE,.025)
add_box(PELVIS,'Belt',(0,.17,.04),(.52,.035,.24),SILVER,.012)
add_panel(PELVIS,'SkirtPanelL',[(-.22,.11,.02),(-.055,.11,.03),(-.075,-.62,.01),(-.31,-.48,-.02)],.035,WHITE)
add_panel(PELVIS,'SkirtPanelR',[(.055,.11,.03),(.22,.11,.02),(.31,-.48,-.02),(.075,-.62,.01)],.035,WHITE)
add_panel(PELVIS,'SkirtInsetL',[(-.20,.09,-.01),(-.08,.09,0),(-.095,-.52,-.01),(-.27,-.42,-.03)],.020,BLACK)
add_panel(PELVIS,'SkirtInsetR',[(.08,.09,0),(.20,.09,-.01),(.27,-.42,-.03),(.095,-.52,-.01)],.020,BLACK)

# Face and head.
add_sphere(HEAD,'HeadSkin',(0,0,0),(.195,.235,.185),SKIN,32,20)
add_sphere(HEAD,'FacePlane',(0,-.01,.145),(.168,.205,.067),SKIN,30,18)
for side in (-1,1):
    add_sphere(HEAD,f'EyeWhite_{side}',(side*.067,.035,.197),(.055,.029,.019),EYE,20,12)
    add_sphere(HEAD,f'Iris_{side}',(side*.067,.035,.214),(.022,.021,.011),IRIS,16,10)
    add_box(HEAD,f'Brow_{side}',(side*.066,.094,.195),(.075,.014,.012),HAIR,.008)
add_box(HEAD,'Mouth',(0,-.075,.211),(.075,.012,.010),material('Lip',(0.45,0.16,0.17),0,.38),.006)
# Hair shell sits behind the face; layered fringe restores a soft hairline.
add_sphere(HEAD,'HairBack',(0,.035,-.055),(.218,.255,.205),HAIR,32,20)
add_sphere(HEAD,'HairCrown',(0,.12,-.005),(.222,.165,.205),HAIR,32,18)
for i in range(9):
    lane=(i-4)/4
    add_strand(HEAD,f'Fringe_{i}',[(lane*.12,.19,.16),(lane*.10,.10,.205),(lane*.12-.035,.015,.215),(lane*.15-.055,-.07,.205)],.013+(i%2)*.003,HAIR_HI if i%3==0 else HAIR)
for side in (-1,1):
    for i in range(3):
        add_strand(HEAD,f'SideLock_{side}_{i}',[(side*(.13+i*.018),.11,.10),(side*(.19+i*.018),-.06,.14),(side*(.21+i*.02),-.27,.09)],.015,HAIR)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(15):
    lane=(i-7)/7
    add_strand(PONY,f'Pony_{i}',[(lane*.035,.16,-.18),(lane*.09,.02,-.31),(lane*.16,-.35,-.38),(lane*.24,-.82,-.30),(lane*.32,-1.28,-.14)],.018+(i%3)*.003,HAIR_HI if i%5==0 else HAIR)
add_box(HEAD,'HairTie',(0,.145,-.185),(.15,.055,.06),SILVER,.018)

# Arms and legs. Group Y is unit length and gets runtime segment scaling.
for group,name,radius,mat,armor in [(UA_L,'UpperArmL',.105,BLACK,False),(UA_R,'UpperArmR',.105,BLACK,False),(FA_L,'ForearmL',.095,BLACK,True),(FA_R,'ForearmR',.095,BLACK,True),(TH_L,'ThighL',.135,BLACK,False),(TH_R,'ThighR',.135,BLACK,False),(SH_L,'ShinL',.102,BLACK,True),(SH_R,'ShinR',.102,BLACK,True)]:
    add_segment(group,name,radius,mat,armor)
for group,name in [(UA_L,'L'),(UA_R,'R')]:
    add_box(group,'ShoulderPlate'+name,(0,.35,.10),(.18,.18,.09),WHITE,.04)
    add_box(group,'ShoulderTrim'+name,(0,.35,.155),(.06,.15,.025),SILVER,.012)
for group,name in [(TH_L,'L'),(TH_R,'R')]:
    add_box(group,'ThighStrap'+name,(0,.23,.12),(.18,.09,.035),SILVER,.015)
for group,name in [(HAND_L,'L'),(HAND_R,'R')]:
    add_sphere(group,'Hand'+name,(0,0,0),(.10,.13,.075),BLACK,22,14)
    add_box(group,'HandPlate'+name,(0,.02,.07),(.14,.12,.035),SILVER,.012)
for group,name in [(FOOT_L,'L'),(FOOT_R,'R')]:
    add_box(group,'Boot'+name,(0,-.035,.075),(.19,.22,.34),BLACK,.045)
    add_box(group,'BootPlate'+name,(0,.055,.19),(.15,.14,.11),WHITE,.025)

# Sword modeled in Blender, runtime-oriented to the existing gameplay blade pose.
add_box(SWORD,'SwordBlade',(0,.62,0),(.065,1.24,.028),WHITE,.015)
add_box(SWORD,'SwordEdge',(.028,.64,.018),(.018,1.20,.018),GLOW,.006)
add_box(SWORD,'SwordGuard',(0,-.035,0),(.34,.055,.14),SILVER,.02)
add_cylinder(SWORD,'SwordGrip',(0,-.18,0),.038,.24,BLACK,20)
add_box(SWORD,'SwordPommel',(0,-.32,0),(.075,.065,.075),SILVER,.015)

# Ensure all runtime groups remain identity transforms in the asset.
for o in [ROOT,PELVIS,TORSO,HEAD,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:
    o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)

bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0]+'.blend')
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
print('Wrote',OUT,os.path.getsize(OUT),'bytes')
