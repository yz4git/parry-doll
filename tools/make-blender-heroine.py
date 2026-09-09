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
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope as a single continuous surface.
add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.54,waist_d*.48,waist_d*.52,0.000),
 (-.245,waist_w*.50,waist_d*.48,waist_d*.54,0.004),
 (-.120,bust_w*.40,bust_d*.39,bust_d*.45,0.010),
 (.020,bust_w*.47,bust_d*.42,bust_d*.51,0.014),
 (.145,bust_w*.50,bust_d*.43,bust_d*.55,0.016),
 (.255,bust_w*.45,bust_d*.39,bust_d*.45,0.008),
 (.330,bust_w*.37,bust_d*.34,bust_d*.37,0.000)
],BLACK_SOFT,40)
# Small front-biased bust volumes blend into the suit rather than becoming two spherical armor pods.
for side in(-1,1):
 add_sphere(TORSO,f'BustContour_{side}',(side*bust_w*.205,.135,bust_d*.235),(bust_w*.185,.078,bust_d*.205),BLACK,28,18)
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

# Compact pelvis and high waist: measured 0.123H width and 0.089H depth.
add_section_mesh(PELVIS,'PelvisSuit',[
 (-.170,pelvis_w*.43,pelvis_d*.43,pelvis_d*.47,0.000),
 (-.070,pelvis_w*.50,pelvis_d*.48,pelvis_d*.52,0.004),
 (.055,pelvis_w*.49,pelvis_d*.47,pelvis_d*.50,0.004),
 (.155,waist_w*.57,waist_d*.54,waist_d*.58,0.000)
],BLACK,36)
add_box(PELVIS,'HighWaist',(0,.105,.012),(pelvis_w*.96,.070,pelvis_d*.88),BLACK,.018)
add_box(PELVIS,'HipBelt',(0,.145,.018),(pelvis_w*1.08,.028,pelvis_d*.94),SILVER,.008)
# Layered pointed skirt measured from the reference silhouette.
# A short radial mini-skirt carries the front silhouette; long tails are deliberately outside the leg columns.
add_panel(PELVIS,'FrontCenterL',[(-.125,.120,.132),(-.012,.112,.140),(-.030,-.185,.150),(-.088,-.280,.132),(-.165,-.175,.100)],.018,WHITE)
add_panel(PELVIS,'FrontCenterR',[(.012,.112,.140),(.125,.120,.132),(.165,-.175,.100),(.088,-.280,.132),(.030,-.185,.150)],.018,WHITE)
add_panel(PELVIS,'HipPetalL',[(-.105,.115,.118),(-.225,.092,.092),(-.268,-.090,.070),(-.205,-.235,.088),(-.120,-.145,.120)],.016,BLACK)
add_panel(PELVIS,'HipPetalR',[(.105,.115,.118),(.120,-.145,.120),(.205,-.235,.088),(.268,-.090,.070),(.225,.092,.092)],.016,BLACK)
add_panel(PELVIS,'WhitePetalL',[(-.175,.100,.104),(-.245,.070,.072),(-.282,-.165,.052),(-.225,-.315,.072),(-.165,-.180,.108)],.014,WHITE)
add_panel(PELVIS,'WhitePetalR',[(.175,.100,.104),(.165,-.180,.108),(.225,-.315,.072),(.282,-.165,.052),(.245,.070,.072)],.014,WHITE)
# Side tails stay narrow from the front but become broad, layered shapes in profile.
add_panel(PELVIS,'SideTailWhiteL',[(-.235,.085,.000),(-.285,.055,-.030),(-.338,-.370,-.062),(-.305,-.690,-.022),(-.255,-.455,.028)],.016,WHITE)
add_panel(PELVIS,'SideTailWhiteR',[(.235,.085,.000),(.255,-.455,.028),(.305,-.690,-.022),(.338,-.370,-.062),(.285,.055,-.030)],.016,WHITE)
add_panel(PELVIS,'SideTailBlackL',[(-.265,.070,-.055),(-.305,.040,-.085),(-.355,-.430,-.112),(-.318,-.780,-.068),(-.285,-.510,-.038)],.013,BLACK)
add_panel(PELVIS,'SideTailBlackR',[(.265,.070,-.055),(.285,-.510,-.038),(.318,-.780,-.068),(.355,-.430,-.112),(.305,.040,-.085)],.013,BLACK)
# Rear panels start away from the center line; from the front they sit behind/outside the thighs instead of making white vertical stripes.
add_panel(PELVIS,'RearTailWhiteL',[(-.205,.090,-.120),(-.105,.082,-.145),(-.120,-.450,-.178),(-.178,-.790,-.152),(-.275,-.500,-.095)],.016,WHITE)
add_panel(PELVIS,'RearTailWhiteR',[(.105,.082,-.145),(.205,.090,-.120),(.275,-.500,-.095),(.178,-.790,-.152),(.120,-.450,-.178)],.016,WHITE)
add_panel(PELVIS,'RearTailBlackL',[(-.250,.070,-.145),(-.165,.062,-.165),(-.185,-.520,-.195),(-.245,-.875,-.132),(-.315,-.485,-.105)],.012,BLACK)
add_panel(PELVIS,'RearTailBlackR',[(.165,.062,-.165),(.250,.070,-.145),(.315,-.485,-.105),(.245,-.875,-.132),(.185,-.520,-.195)],.012,BLACK)

# === HEAD / FACE ===
# The sheet reads as a compact ~7-head stylized adult: keep the skull wide enough but reduce vertical helmet height.
add_sphere(HEAD,'Cranium',(0,.012,-.018),(head_w*.490,.116,head_d*.480),SKIN,40,26)
add_sphere(HEAD,'Jaw',(0,-.058,.030),(head_w*.400,.070,head_d*.400),SKIN,38,22)
add_sphere(HEAD,'Chin',(0,-.108,.058),(head_w*.230,.027,head_d*.235),SKIN,28,16)
add_cylinder(HEAD,'Neck',(0,-.160,-.004),W('neck')*.37,.100,SKIN,24)
face_z=head_d*.500
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.170,.010,face_z),(head_w*.080,.0105,.006),SCLERA,22,12)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.170,.010,face_z+.0065),(head_w*.032,.0085,.004),IRIS,18,10)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.170,.010,face_z+.009),(head_w*.012,.0055,.0025),PUPIL,14,8)
 add_box(HEAD,f'Eyeliner_{side}',(side*head_w*.170,.027,face_z+.0085),(head_w*.096,.005,.0032),HAIR,.0014,rot=(0,0,-side*.085))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.170,.058,face_z+.001),(head_w*.105,.005,.0035),HAIR,.0014,rot=(0,0,-side*.09))
add_sphere(HEAD,'Nose',(0,-.012,face_z+.006),(.009,.021,.008),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.066,face_z+.003),(.040,.005,.0035),LIP,.0012)
# Scalp volumes stay behind the face; temple fills prevent bald-looking gaps without forming a spherical helmet.
add_sphere(HEAD,'HairBack',(0,.026,-head_d*.24),(head_w*.530,.136,head_d*.565),HAIR,38,24)
add_sphere(HEAD,'HairCrown',(0,.080,-.035),(head_w*.510,.070,head_d*.500),HAIR,36,22)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.405,.012,.000),(head_w*.120,.095,head_d*.210),HAIR,26,18)
# Five broad overlapping swept bang sheets replace the picket-fence fringe.
bangs=[
 (-.090,-.045,-.072,.060),(-.052,-.012,-.038,.067),(-.010,.012,.010,.070),(.040,-.006,.043,.064),(.085,-.050,.078,.057)
]
for i,(sx,ey,ex,w0) in enumerate(bangs):
 add_ribbon(HEAD,f'BangSheet_{i}',[(sx,.104,.010),(sx*.80,.082,face_z*.62),(ex*.84,.043,face_z-.003),(ex,ey,face_z+.004)],[w0,w0*.96,w0*.68,w0*.28],.0065,HAIR_HI if i in(1,3) else HAIR)
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.365,.070,.015),(side*head_w*.445,-.010,head_d*.16),(side*head_w*.465,-.180,head_d*.08),(side*head_w*.405,-.420,-.005)],[.050,.046,.034,.014],.0065,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.410,.050,.000),(side*head_w*.485,-.075,head_d*.11),(side*head_w*.500,-.270,.035),(side*head_w*.445,-.500,-.025)],[.028,.026,.020,.010],.005,HAIR_HI)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# Continuous ponytail core: this is the dark hair mass seen in the side/back reference.
add_section_mesh(PONY,'PonyCore',[
 (.100,.050,.030,.038,-head_d*.47),
 (-.030,.078,.040,.052,-head_d*.67),
 (-.300,.118,.052,.068,-.390),
 (-.650,.142,.060,.074,-.325),
 (-1.000,.128,.052,.064,-.235),
 (-1.300,.092,.038,.048,-.155),
 (-1.500,.045,.022,.028,-.080)
],HAIR,32)
# Wide ribbons sit over the core, with fine strands only at the outside edge.
for i in range(7):
 lane=(i-3)/3
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.025,.095,-head_d*.49),(lane*.070,-.055,-head_d*.70),(lane*.135,-.410,-.405),(lane*.205,-.900,-.285),(lane*.270,-1.470,-.090)],[.055,.062,.066,.050,.014],.006,HAIR_HI if i in(1,5) else HAIR)
for i in range(8):
 lane=(i-3.5)/3.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.030,.090,-head_d*.50),(lane*.085,-.090,-head_d*.72),(lane*.160,-.500,-.390),(lane*.245,-1.020,-.245),(lane*.330,-1.535,-.060)],.0038+(i%2)*.0007,HAIR_HI if i%3==0 else HAIR)
add_box(HEAD,'HairTie',(0,.086,-head_d*.49),(.102,.028,.040),SILVER,.008)

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
 add_cylinder(group,'Garter'+name,(0,-.245,0),th*1.06,.048,BLACK,24);add_cylinder(group,'ThighBootTop'+name,(0,.105,0),th*.96,.70,BLACK,28)
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
