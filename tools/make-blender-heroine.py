import bpy, json, os

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
SKIN=material('Skin',(0.84,0.61,0.54),0,.48)
BLACK=material('Suit Black',(0.014,0.018,0.027),.08,.30)
BLACK_SOFT=material('Suit Soft',(0.030,0.035,0.048),.02,.44)
WHITE=material('Porcelain White',(0.86,0.88,0.88),.18,.28)
SILVER=material('Silver',(0.50,0.53,0.56),.78,.19)
HAIR=material('Hair',(0.027,0.020,0.022),.02,.40)
HAIR_HI=material('Hair Highlight',(0.075,0.048,0.050),.02,.35)
SCLERA=material('Sclera',(0.86,0.84,0.82),0,.42)
IRIS=material('Iris',(0.18,0.24,0.25),.04,.24)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.42,0.17,0.18),0,.46)
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
 # Elliptical tapered segment. The reference sheet supplies front width and side depth separately.
 bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=1,radius2=1,depth=1,location=(0,0,0));o=bpy.context.object;o.name=name+'_core';o.scale=(r1,depth1,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);smooth(o);parent(o,p)
 # Narrow overlap caps remove the old ball-joint silhouette without creating visible gaps.
 add_sphere(p,name+'_jointA',(0,-.485,0),(r1*.72,r1*.76,depth1*.72),mat,22,14);add_sphere(p,name+'_jointB',(0,.485,0),(r2*.72,r2*.76,depth2*.72),mat,22,14)
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
# Source sheet measured at H=920 px and normalized in heroine-reference-proportions.json.
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope instead of the previous armor-block proportions.
add_sphere(TORSO,'TorsoCore',(0,.00,0),(bust_w*.43,.305,bust_d*.38),BLACK_SOFT,36,24)
add_sphere(TORSO,'RibCage',(0,.145,.015),(bust_w*.50,.185,bust_d*.46),BLACK,36,24)
add_sphere(TORSO,'Waist',(0,-.225,0),(waist_w*.50,.145,waist_d*.50),BLACK,32,20)
# Subtle bust shaping is front-biased but does not widen the measured front silhouette.
for side in(-1,1):add_sphere(TORSO,f'Bust_{side}',(side*bust_w*.205,.135,bust_d*.27),(bust_w*.26,.115,bust_d*.29),BLACK,30,18)
# Reference-like harness: thin lines, no square robot chest plates.
add_box(TORSO,'Sternum',(0,.085,bust_d*.43),(.020,.355,.016),SILVER,.006)
add_box(TORSO,'Collar',(0,.305,.010),(W('neck')*1.15,.055,.105),BLACK,.014)
add_box(TORSO,'WaistBelt',(0,-.255,.005),(waist_w*1.12,.040,waist_d*1.10),SILVER,.008)
for side in(-1,1):
 add_box(TORSO,f'UpperHarness_{side}',(side*.095,.205,bust_d*.39),(.020,.255,.014),SILVER,.006,rot=(0,0,side*.40))
 add_box(TORSO,f'LowerHarness_{side}',(side*.072,-.080,bust_d*.37),(.018,.210,.014),SILVER,.006,rot=(0,0,-side*.28))
 add_panel(TORSO,f'WhiteSidePanel_{side}',[(side*waist_w*.53,-.23,.02),(side*bust_w*.48,.05,.01),(side*bust_w*.43,.24,.00),(side*waist_w*.56,-.08,.02)],.025,WHITE)

# Compact pelvis and high waist: measured 0.123H width and 0.089H depth.
add_sphere(PELVIS,'PelvisSuit',(0,0,0),(pelvis_w*.50,.135,pelvis_d*.50),BLACK,34,22)
add_box(PELVIS,'HighWaist',(0,.105,.012),(pelvis_w*.96,.070,pelvis_d*.88),BLACK,.018)
add_box(PELVIS,'HipBelt',(0,.145,.018),(pelvis_w*1.08,.028,pelvis_d*.94),SILVER,.008)
# Layered pointed skirt measured from the reference silhouette. Avoid long rectangular slabs.
add_panel(PELVIS,'FrontPanelL',[(-.150,.115,.118),(-.026,.105,.126),(-.052,-.42,.142),(-.112,-.60,.132),(-.222,-.40,.082)],.022,WHITE)
add_panel(PELVIS,'FrontPanelR',[(.026,.105,.126),(.150,.115,.118),(.222,-.40,.082),(.112,-.60,.132),(.052,-.42,.142)],.022,WHITE)
add_panel(PELVIS,'FrontBladeL',[(-.180,.090,.095),(-.120,.075,.110),(-.170,-.49,.108),(-.258,-.66,.055),(-.246,-.29,.050)],.018,BLACK)
add_panel(PELVIS,'FrontBladeR',[(.120,.075,.110),(.180,.090,.095),(.246,-.29,.050),(.258,-.66,.055),(.170,-.49,.108)],.018,BLACK)
add_panel(PELVIS,'SidePanelL',[(-.175,.105,.022),(-.232,.070,-.005),(-.315,-.37,-.035),(-.286,-.76,.010),(-.220,-.53,.040)],.018,WHITE)
add_panel(PELVIS,'SidePanelR',[(.175,.105,.022),(.232,.070,-.005),(.220,-.53,.040),(.286,-.76,.010),(.315,-.37,-.035)],.018,WHITE)
add_panel(PELVIS,'SideBladeL',[(-.214,.080,-.035),(-.267,.045,-.060),(-.338,-.44,-.082),(-.285,-.68,-.045)],.015,BLACK)
add_panel(PELVIS,'SideBladeR',[(.214,.080,-.035),(.285,-.68,-.045),(.338,-.44,-.082),(.267,.045,-.060)],.015,BLACK)
add_panel(PELVIS,'RearPanelL',[(-.155,.095,-.105),(-.025,.090,-.120),(-.060,-.50,-.150),(-.138,-.80,-.128),(-.252,-.52,-.080)],.018,WHITE)
add_panel(PELVIS,'RearPanelR',[(.025,.090,-.120),(.155,.095,-.105),(.252,-.52,-.080),(.138,-.80,-.128),(.060,-.50,-.150)],.018,WHITE)

# === HEAD / FACE ===
# 0.128H front width, 0.114H side depth. Vertical envelope is reduced to the sheet's ~0.15H head region.
add_sphere(HEAD,'Cranium',(0,.018,-.020),(head_w*.485,.145,head_d*.455),SKIN,36,24)
add_sphere(HEAD,'Jaw',(0,-.066,.030),(head_w*.390,.092,head_d*.390),SKIN,34,22)
add_cylinder(HEAD,'Neck',(0,-.190,-.006),W('neck')*.36,.110,SKIN,22)
# Project features beyond the facial surface; v1.2 placed them behind the jaw and they disappeared.
face_z=.154
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.178,.020,face_z),(head_w*.102,.018,.009),SCLERA,20,12)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.178,.020,face_z+.011),(head_w*.036,.014,.005),IRIS,16,10)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.178,.020,face_z+.016),(head_w*.014,.008,.003),PUPIL,12,8)
 add_box(HEAD,f'Eyeliner_{side}',(side*head_w*.178,.040,face_z+.014),(head_w*.116,.008,.004),HAIR,.002,rot=(0,0,-side*.06))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.178,.070,face_z+.005),(head_w*.130,.008,.005),HAIR,.002,rot=(0,0,-side*.08))
add_sphere(HEAD,'Nose',(0,-.015,face_z+.010),(.012,.027,.011),SKIN,16,10)
add_box(HEAD,'Mouth',(0,-.075,face_z+.004),(.050,.007,.004),LIP,.0015)
# Hair shell stays compact around the skull. Bangs leave the eye line visible.
add_sphere(HEAD,'HairBack',(0,.035,-head_d*.18),(head_w*.535,.165,head_d*.515),HAIR,34,22)
add_sphere(HEAD,'HairCrown',(0,.108,-.018),(head_w*.525,.095,head_d*.490),HAIR,34,22)
for i in range(11):
 lane=(i-5)/5
 end_y=.018-.058*abs(lane);end_x=lane*head_w*.42
 add_strand(HEAD,f'Fringe_{i}',[(lane*head_w*.33,.142,head_d*.18),(lane*head_w*.30,.098,head_d*.40),(lane*head_w*.33,.060,face_z-.003),(end_x,end_y,face_z+.002)],.0068+(i%2)*.0010,HAIR_HI if i%4==0 else HAIR)
for side in(-1,1):
 for i in range(5):
  add_strand(HEAD,f'SideLock_{side}_{i}',[(side*(head_w*.35+i*.010),.095,head_d*.16),(side*(head_w*.47+i*.012),-.04,head_d*.28),(side*(head_w*.50+i*.012),-.30,head_d*.12),(side*(head_w*.43+i*.010),-.52,-.015)],.009,HAIR_HI if i==0 else HAIR)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(27):
 lane=(i-13)/13;spread=.030+.035*abs(lane)
 add_strand(PONY,f'Pony_{i}',[(lane*.020,.105,-head_d*.46),(lane*.065,-.005,-head_d*.70),(lane*.115,-.36,-.38),(lane*.19,-.88,-.31),(lane*.28,-1.48,-.12)],.0095+(i%5)*.0011,HAIR_HI if i%7==0 else HAIR)
add_box(HEAD,'HairTie',(0,.100,-head_d*.47),(.100,.032,.040),SILVER,.009)

# === LIMBS ===
# Diameters come directly from the front sheet; side depth comes from the side view.
ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.50;kn=W('knee_each')*.50;calf=W('calf_each')*.50;ank=W('ankle_each')*.50
ua_d=ua*.78;fa_d=fa*.80;th_d=D('thigh')*.50;calf_d=D('calf')*.50;ank_d=D('ankle')*.50
for group,name,r1,r2,d1,d2,mat in[
 (UA_L,'UpperArmL',ua*.98,ua*.78,ua_d,ua_d*.82,SKIN),(UA_R,'UpperArmR',ua*.98,ua*.78,ua_d,ua_d*.82,SKIN),
 (FA_L,'ForearmL',fa*.92,fa*.68,fa_d,fa_d*.72,BLACK),(FA_R,'ForearmR',fa*.92,fa*.68,fa_d,fa_d*.72,BLACK),
 (TH_L,'ThighL',th*1.08,kn*.90,th_d,th_d*.78,SKIN),(TH_R,'ThighR',th*1.08,kn*.90,th_d,th_d*.78,SKIN),
 (SH_L,'ShinL',calf*.93,ank*.90,calf_d,ank_d,BLACK),(SH_R,'ShinR',calf*.93,ank*.90,calf_d,ank_d,BLACK)]:add_taper(group,name,r1,r2,d1,d2,mat)
# Upper-arm straps + forearm gauntlets; narrow armor follows the limb instead of becoming the limb.
for group,name in[(UA_L,'L'),(UA_R,'R')]:
 add_cylinder(group,'UpperArmBand'+name,(0,-.26,0),ua*1.07,.070,BLACK,24);add_cylinder(group,'UpperArmBand2'+name,(0,-.13,0),ua*1.04,.045,SILVER,24)
for group,name in[(FA_L,'L'),(FA_R,'R')]:
 add_box(group,'ForearmPlate'+name,(0,.06,fa_d*.78),(fa*1.35,.43,fa_d*.52),WHITE,.014);add_box(group,'ForearmRail'+name,(0,.05,fa_d*1.08),(.018,.35,.012),SILVER,.005)
# Thigh-high boot begins below the garter line, preserving measured leg diameter.
for group,name in[(TH_L,'L'),(TH_R,'R')]:
 add_cylinder(group,'Garter'+name,(0,-.21,0),th*1.08,.055,BLACK,24);add_cylinder(group,'ThighBootTop'+name,(0,.235,0),th*.97,.47,BLACK,28)
for group,name in[(SH_L,'L'),(SH_R,'R')]:
 add_box(group,'ShinPlate'+name,(0,.03,calf_d*.78),(calf*1.30,.50,calf_d*.44),BLACK_SOFT,.012);add_box(group,'ShinAccent'+name,(0,.06,calf_d*1.02),(.018,.40,.012),SILVER,.005)
for group,name in[(HAND_L,'L'),(HAND_R,'R')]:
 add_sphere(group,'Hand'+name,(0,0,0),(fa*.73,.078,fa_d*.66),BLACK,22,14);add_box(group,'HandPlate'+name,(0,.010,fa_d*.58),(fa*1.02,.068,.018),WHITE,.006)
# Reference heel silhouette: compact toe, ankle cuff, narrow rear heel.
for group,name in[(FOOT_L,'L'),(FOOT_R,'R')]:
 add_box(group,'Shoe'+name,(0,-.030,.105),(ank*2.10,.115,.285),BLACK,.025)
 add_box(group,'ToeCap'+name,(0,-.045,.235),(ank*1.95,.075,.120),WHITE,.015)
 add_box(group,'AnkleCuff'+name,(0,.075,.020),(ank*2.25,.115,.105),SILVER,.012)
 add_box(group,'Heel'+name,(0,-.110,-.035),(ank*.52,.205,.045),BLACK,.008)

# Slim sword retained as a gameplay-readable prop.
add_box(SWORD,'SwordBlade',(0,.63,0),(.043,1.26,.018),WHITE,.008);add_box(SWORD,'SwordEdge',(.020,.65,.013),(.010,1.22,.010),GLOW,.003);add_box(SWORD,'SwordGuard',(0,-.03,0),(.245,.040,.085),SILVER,.012);add_cylinder(SWORD,'SwordGrip',(0,-.17,0),.026,.23,BLACK,20);add_box(SWORD,'SwordPommel',(0,-.31,0),(.050,.050,.050),SILVER,.009)

for o in[ROOT,PELVIS,TORSO,HEAD,UA_L,FA_L,HAND_L,UA_R,FA_R,HAND_R,TH_L,SH_L,FOOT_L,TH_R,SH_R,FOOT_R,SWORD,PONY]:o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)

bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0]+'.blend')
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
print('Reference ratios:',{'H':H,'shoulder_half':DW['shoulder_joint_half_width'],'hip_half':DW['hip_joint_half_width'],'bust_w':round(bust_w,4),'waist_w':round(waist_w,4),'pelvis_w':round(pelvis_w,4)})
print('Wrote',OUT,os.path.getsize(OUT),'bytes')
