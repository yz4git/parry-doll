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
# REFERENCE_V16: side-curve, face and pony-root polish.
# REFERENCE_V17: portrait readability, shoulder continuity and refined heels.
# REFERENCE_V18: natural hairline, clavicle bridge and stronger feminine torso curvature.
# REFERENCE_V19: continuous portrait shell and face-plane retarget.
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope as a single continuous surface.
# Front depth peaks at the bust while the lower back eases toward the high waist, matching the side sheet.
add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.53,waist_d*.52,waist_d*.58,-.004),
 (-.245,waist_w*.49,waist_d*.50,waist_d*.58,0.000),
 (-.115,bust_w*.39,bust_d*.42,bust_d*.49,0.007),
 (.010,bust_w*.46,bust_d*.44,bust_d*.58,0.018),
 (.130,bust_w*.50,bust_d*.45,bust_d*.66,0.028),
 (.225,bust_w*.47,bust_d*.41,bust_d*.53,0.016),
 (.315,bust_w*.38,bust_d*.35,bust_d*.40,0.003)
],BLACK,40)
# Front-biased contours define the bust from front/side while staying within the measured bust width.
for side in(-1,1):
 add_sphere(TORSO,f'BustContour_{side}',(side*bust_w*.205,.125,bust_d*.350),(bust_w*.205,.086,bust_d*.245),BLACK,32,20)
add_box(TORSO,'UnderBustLine',(0,.045,bust_d*.485),(bust_w*.72,.018,.012),SILVER,.004)
# Upper torso continuity: clavicle/shoulder bridge stays inside the measured shoulder envelope.
for side in(-1,1):
 add_sphere(TORSO,f'ClavicleBlend_{side}',(side*bust_w*.390,.245,.006),(bust_w*.145,.060,bust_d*.175),BLACK,28,18)
 add_panel(TORSO,f'ShoulderStrap_{side}',[(side*bust_w*.265,.285,bust_d*.30),(side*bust_w*.445,.245,bust_d*.18),(side*bust_w*.450,.185,bust_d*.24),(side*bust_w*.285,.205,bust_d*.36)],.018,BLACK)
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
 (-.180,pelvis_w*.42,pelvis_d*.60,pelvis_d*.48,-.018),
 (-.080,pelvis_w*.50,pelvis_d*.58,pelvis_d*.52,-.012),
 (.040,pelvis_w*.49,pelvis_d*.52,pelvis_d*.51,-.005),
 (.155,waist_w*.57,waist_d*.56,waist_d*.59,0.000)
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
# One continuous measured portrait shell instead of overlapping spheres.
add_section_mesh(HEAD,'HeadShell',[
 (-.128,head_w*.155,head_d*.225,head_d*.300,.050),
 (-.105,head_w*.250,head_d*.285,head_d*.355,.042),
 (-.078,head_w*.340,head_d*.345,head_d*.410,.030),
 (-.038,head_w*.415,head_d*.390,head_d*.455,.016),
 (.012,head_w*.485,head_d*.435,head_d*.505,.002),
 (.060,head_w*.500,head_d*.465,head_d*.490,-.008),
 (.103,head_w*.455,head_d*.480,head_d*.430,-.018),
 (.135,head_w*.340,head_d*.445,head_d*.330,-.030)
],SKIN,48)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.485,-.018,-.014),(.010,.023,.009),SKIN,18,10)
# Facial plane is tied to the front depth of the eye/cheek rings.
face_z=head_d*.505
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.158,.014,face_z),(head_w*.091,.0105,.0060),SCLERA,30,16)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.158,.012,face_z+.0068),(head_w*.041,.0087,.0043),IRIS,22,12)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.158,.012,face_z+.0096),(head_w*.014,.0054,.0026),PUPIL,16,10)
 add_box(HEAD,f'UpperLash_{side}',(side*head_w*.158,.030,face_z+.0092),(head_w*.105,.0044,.0030),HAIR,.0012,rot=(0,0,-side*.090))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.158,.064,face_z+.001),(head_w*.101,.0042,.0030),HAIR,.0012,rot=(0,0,-side*.095))
# A slim bridge + tip reads in profile without becoming a toy nose.
add_sphere(HEAD,'NoseBridge',(0,.004,face_z+.004),(.0075,.031,.0060),SKIN,20,12)
add_sphere(HEAD,'NoseTip',(0,-.027,face_z+.011),(.0085,.013,.0080),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.073,face_z+.0040),(.044,.0048,.0032),LIP,.0010)
# Rear scalp never crosses the forehead; frontal hair is entirely layered geometry.
add_sphere(HEAD,'HairBack',(0,.022,-head_d*.370),(head_w*.515,.128,head_d*.450),HAIR,44,30)
add_sphere(HEAD,'HairCrown',(0,.093,-head_d*.380),(head_w*.450,.047,head_d*.270),HAIR,40,24)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.414,.006,-.030),(head_w*.093,.080,head_d*.150),HAIR,28,18)
# Layered bangs cover the upper forehead while keeping an irregular, broken hairline.
fringe=[(-.116,-.094,-.082,.033),(-.090,-.070,-.061,.034),(-.064,-.047,-.041,.035),(-.038,-.026,-.022,.036),(-.014,-.006,-.004,.035),(.012,.016,.015,.034),(.038,.040,.036,.033),(.065,.064,.057,.032),(.092,.088,.078,.030),(.114,.106,.096,.027)]
for i,(sx,mx,ex,w0) in enumerate(fringe):
 ey=-.004-.014*abs((i-4.5)/4.5)
 add_ribbon(HEAD,f'FringeSweep_{i}',[(sx,.116,-.020),(mx,.090,face_z*.27),(ex,.055,face_z*.60),(ex*.96,ey,face_z+.003)],[w0,w0*.92,w0*.58,w0*.13],.0047,HAIR_HI if i in(2,7) else HAIR)
# Longer side fringe frames the jaw like the supplied sheet.
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.365,.070,-.006),(side*head_w*.445,-.012,head_d*.115),(side*head_w*.458,-.178,head_d*.044),(side*head_w*.395,-.415,-.020)],[.042,.038,.026,.010],.0052,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.408,.046,-.016),(side*head_w*.478,-.078,head_d*.060),(side*head_w*.486,-.270,.000),(side*head_w*.425,-.495,-.042)],[.020,.018,.013,.006],.0038,HAIR_HI)
# High ponytail with backward launch, broad upper mass and fine taper.
add_sphere(HEAD,'PonyRootMass',(0,.148,-head_d*.410),(.076,.061,.064),HAIR,32,22)
add_box(HEAD,'HairTie',(0,.143,-head_d*.470),(.090,.023,.034),SILVER,.007)
for side in(-1,1):add_box(HEAD,f'HairTieFin_{side}',(side*.055,.147,-head_d*.475),(.009,.086,.018),SILVER,.003,rot=(0,0,side*.18))
PONY=empty('BL_PONY_DYNAMIC',HEAD)
add_section_mesh(PONY,'PonyCore',[
 (.145,.042,.026,.033,-head_d*.47),
 (.025,.080,.041,.053,-head_d*.73),
 (-.240,.122,.053,.069,-.450),
 (-.550,.150,.063,.079,-.360),
 (-.900,.146,.060,.074,-.272),
 (-1.230,.113,.046,.058,-.185),
 (-1.495,.067,.028,.038,-.100),
 (-1.660,.030,.016,.021,-.040)
],HAIR,38)
for i in range(9):
 lane=(i-4)/4
 add_ribbon(PONY,f'PonyLayer_{i}',[(lane*.020,.140,-head_d*.49),(lane*.064,-.010,-head_d*.74),(lane*.132,-.330,-.455),(lane*.208,-.760,-.325),(lane*.288,-1.230,-.185),(lane*.334,-1.640,-.044)],[.044,.058,.071,.067,.045,.010],.0052,HAIR_HI if i in(2,6) else HAIR)
for i in range(10):
 lane=(i-4.5)/4.5
 add_strand(PONY,f'PonyEdge_{i}',[(lane*.024,.134,-head_d*.49),(lane*.082,-.080,-head_d*.76),(lane*.158,-.500,-.420),(lane*.248,-1.035,-.242),(lane*.342,-1.680,-.030)],.0031+(i%2)*.0006,HAIR_HI if i%3==0 else HAIR)

# === LIMBS ===
# Diameters come directly from the front sheet; side depth comes from the side view.
ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.50;kn=W('knee_each')*.50;calf=W('calf_each')*.50;ank=W('ankle_each')*.50
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
 add_cylinder(group,'Garter'+name,(0,-.245,0),th*1.06,.048,BLACK,24);add_cylinder(group,'ThighBootTop'+name,(0,.105,0),th*.96,.70,BLACK,28)
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
