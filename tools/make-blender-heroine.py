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
HAIR=material('Hair',(0.007,0.006,0.010),0.0,.52)
HAIR_HI=material('Hair Highlight',(0.026,0.020,0.030),0.0,.46)
# Reduce Principled specular so dark hair does not blow out to a silver ribbon under bright sky lighting.
for _hair_mat,_spec in ((HAIR,.14),(HAIR_HI,.18)):
 _bsdf=_hair_mat.node_tree.nodes.get('Principled BSDF')
 if _bsdf:
  _ior=_bsdf.inputs.get('Specular IOR Level')
  _old=_bsdf.inputs.get('Specular')
  if _ior:_ior.default_value=_spec
  elif _old:_old.default_value=_spec
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
bust_w=W('bust');waist_w=W('waist');pelvis_w=W('pelvis');bust_d=D('bust');waist_d=D('waist');pelvis_d=D('pelvis');head_w=W('head');head_d=D('head')
# Torso follows the measured hourglass envelope as a single continuous surface.
# Front depth peaks at the bust while the lower back eases toward the high waist, matching the side sheet.
add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.49,waist_d*.49,waist_d*.54,-.006),
 (-.285,waist_w*.47,waist_d*.47,waist_d*.54,-.004),
 (-.220,waist_w*.49,waist_d*.46,waist_d*.55,-.001),
 (-.150,bust_w*.37,bust_d*.40,bust_d*.47,.004),
 (-.075,bust_w*.43,bust_d*.41,bust_d*.54,.011),
 (.000,bust_w*.48,bust_d*.42,bust_d*.62,.021),
 (.075,bust_w*.515,bust_d*.44,bust_d*.675,.030),
 (.135,bust_w*.505,bust_d*.44,bust_d*.655,.030),
 (.195,bust_w*.465,bust_d*.42,bust_d*.57,.022),
 (.255,bust_w*.405,bust_d*.39,bust_d*.48,.012),
 (.315,bust_w*.340,bust_d*.34,bust_d*.385,.002)
],BLACK,48)
# Shallow soft-tissue support over a continuous ribcage. The outer envelope remains reference-locked.
for side in(-1,1):
 add_sphere(TORSO,f'BustSoft_{side}',(side*bust_w*.205,.105,bust_d*.330),(bust_w*.205,.082,bust_d*.180),BLACK,36,22)
add_box(TORSO,'UnderBustLine',(0,.020,bust_d*.505),(bust_w*.70,.014,.009),SILVER,.003)
for side in(-1,1):
 add_box(TORSO,f'WaistContour_{side}',(side*waist_w*.44,-.150,waist_d*.50),(.012,.175,.009),SILVER,.0035,rot=(0,0,-side*.15))
# Anatomical clavicle/deltoid bridge inside the measured shoulder envelope.
for side in(-1,1):
 add_sphere(TORSO,f'DeltoidBridge_{side}',(side*bust_w*.405,.238,.002),(bust_w*.125,.064,bust_d*.150),BLACK,30,20)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.285,.258,bust_d*.28),(side*bust_w*.430,.225,bust_d*.18),(side*bust_w*.275,.210,bust_d*.31)],.013,BLACK_SOFT)
 add_box(TORSO,f'ClavicleTrim_{side}',(side*bust_w*.225,.247,bust_d*.325),(bust_w*.285,.010,.008),SILVER,.0025,rot=(0,0,-side*.11))
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
add_panel(PELVIS,'FrontCenterL',[(-.150,.122,.138),(-.008,.116,.148),(-.020,-.205,.157),(-.082,-.335,.142),(-.178,-.185,.102)],.018,WHITE)
add_panel(PELVIS,'FrontCenterR',[(.008,.116,.148),(.150,.122,.138),(.178,-.185,.102),(.082,-.335,.142),(.020,-.205,.157)],.018,WHITE)
add_panel(PELVIS,'HipPetalL',[(-.115,.118,.120),(-.238,.094,.094),(-.292,-.100,.070),(-.220,-.275,.088),(-.126,-.160,.122)],.016,BLACK)
add_panel(PELVIS,'HipPetalR',[(.115,.118,.120),(.126,-.160,.122),(.220,-.275,.088),(.292,-.100,.070),(.238,.094,.094)],.016,BLACK)
add_panel(PELVIS,'WhitePetalL',[(-.188,.105,.106),(-.258,.070,.074),(-.304,-.185,.052),(-.238,-.365,.070),(-.170,-.195,.110)],.014,WHITE)
add_panel(PELVIS,'WhitePetalR',[(.188,.105,.106),(.170,-.195,.110),(.238,-.365,.070),(.304,-.185,.052),(.258,.070,.074)],.014,WHITE)
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
add_section_mesh(HEAD,'HeadShell',[
 (-.145,head_w*.120,head_d*.170,head_d*.235,.052),  # chin tip
 (-.126,head_w*.235,head_d*.235,head_d*.305,.045),  # chin body
 (-.105,head_w*.315,head_d*.300,head_d*.360,.036),  # jaw
 (-.078,head_w*.385,head_d*.350,head_d*.410,.026),  # mouth / lower cheek
 (-.045,head_w*.445,head_d*.390,head_d*.455,.015),  # cheek lower
 (-.010,head_w*.490,head_d*.425,head_d*.500,.004),  # cheekbone / eye socket
 (.025,head_w*.505,head_d*.450,head_d*.515,-.004),  # eye level
 (.058,head_w*.490,head_d*.472,head_d*.490,-.010),  # brow / temple
 (.092,head_w*.455,head_d*.482,head_d*.445,-.017),  # forehead
 (.120,head_w*.395,head_d*.468,head_d*.385,-.024),  # upper forehead
 (.145,head_w*.310,head_d*.435,head_d*.315,-.030)   # crown transition
],SKIN,52)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'Ear_{side}',(side*head_w*.485,-.018,-.014),(.010,.023,.009),SKIN,18,10)
# Anatomy-first portrait: embedded eyeballs, eyelids and a connected central face form.
face_z=head_d*.515
eye_y=.018
eye_z=face_z-.010
eye_x=head_w*.160
eye_rx=head_w*.090
eye_ry=.028
eye_rz=head_d*.100
for side in(-1,1):
 ex=side*eye_x
 # Eyeball first; the lids are built around its visible front surface.
 add_sphere(HEAD,f'Eyeball_{side}',(ex,eye_y,eye_z),(eye_rx,eye_ry,eye_rz),SCLERA,32,20)
 eye_front=eye_z+eye_rz*.96
 add_sphere(HEAD,f'Iris_{side}',(ex,eye_y-.001,eye_front+.003),(head_w*.048,.012,.0046),IRIS,26,16)
 add_sphere(HEAD,f'Pupil_{side}',(ex,eye_y-.001,eye_front+.0065),(head_w*.018,.0070,.0030),PUPIL,20,12)
 add_sphere(HEAD,f'EyeLight_{side}',(ex-side*head_w*.012,eye_y+.008,eye_front+.0095),(head_w*.010,.0040,.0018),SCLERA,12,8)
 # Upper and lower eyelid skin wraps the sphere rather than floating as a rectangular plate.
 lid_outer=ex+side*eye_rx*.95
 lid_inner=ex-side*eye_rx*.90
 add_panel(HEAD,f'UpperLid_{side}',[(lid_inner,.030,eye_front+.001),(ex,.043,eye_front+.004),(lid_outer,.028,eye_front+.001),(lid_outer,.018,eye_front+.004),(ex,.028,eye_front+.008),(lid_inner,.019,eye_front+.004)],.0023,SKIN)
 add_panel(HEAD,f'LowerLid_{side}',[(lid_inner,.008,eye_front+.003),(ex,-.004,eye_front+.004),(lid_outer,.009,eye_front+.003),(lid_outer,.015,eye_front+.005),(ex,.008,eye_front+.006),(lid_inner,.015,eye_front+.005)],.0020,SKIN)
 # Lashes/brows follow the eye arc and retain the stylized key-art readability.
 add_panel(HEAD,f'UpperLash_{side}',[(lid_inner,.032,eye_front+.008),(ex,.045,eye_front+.010),(lid_outer,.030,eye_front+.008),(lid_outer,.026,eye_front+.009),(ex,.040,eye_front+.011),(lid_inner,.027,eye_front+.009)],.0015,HAIR)
 add_panel(HEAD,f'Brow_{side}',[(ex-side*eye_rx*.82,.078,face_z+.007),(ex,.086,face_z+.010),(ex+side*eye_rx*.96,.073,face_z+.007),(ex+side*eye_rx*.90,.067,face_z+.008),(ex,.079,face_z+.011),(ex-side*eye_rx*.78,.071,face_z+.008)],.0015,HAIR)

# Nose bridge, tip and alar wings form one connected volume growing out of the face plane.
add_section_mesh(HEAD,'NoseForm',[
 (.073,.0045,.0035,.0050,face_z-.012),
 (.045,.0055,.0038,.0075,face_z-.009),
 (.015,.0070,.0040,.0105,face_z-.006),
 (-.012,.0085,.0042,.0140,face_z-.003),
 (-.034,.0110,.0045,.0180,face_z+.000),
 (-.050,.0135,.0048,.0195,face_z+.002)
],SKIN,24)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWing_{side}',(side*.0125,-.050,face_z+.010),(.0085,.0080,.0060),SKIN,18,10)

# Mouth stays embedded in the lower-face plane with a soft cupid bow and restrained projection.
add_panel(HEAD,'UpperLip',[(-.029,-.076,face_z+.004),(-.014,-.071,face_z+.005),(0,-.075,face_z+.006),(.014,-.071,face_z+.005),(.029,-.076,face_z+.004),(.020,-.081,face_z+.005),(0,-.080,face_z+.006),(-.020,-.081,face_z+.005)],.0018,LIP)
add_panel(HEAD,'LowerLip',[(-.024,-.082,face_z+.004),(0,-.087,face_z+.006),(.024,-.082,face_z+.004),(.017,-.091,face_z+.004),(0,-.094,face_z+.005),(-.017,-.091,face_z+.004)],.0017,LIP)
# Tiny philtrum/chin cues improve front/profile readability without adding hard mechanical lines.
add_box(HEAD,'Philtrum',(0,-.063,face_z+.002),(.006,.014,.003),SKIN,.001)
add_sphere(HEAD,'ChinPlane',(0,-.118,face_z-.010),(head_w*.115,.020,head_d*.055),SKIN,24,14)
# Rear scalp never crosses the forehead; frontal hair is entirely layered geometry.
add_sphere(HEAD,'HairBack',(0,.022,-head_d*.370),(head_w*.515,.128,head_d*.450),HAIR,44,30)
add_sphere(HEAD,'HairCrown',(0,.093,-head_d*.380),(head_w*.450,.047,head_d*.270),HAIR,40,24)
for side in(-1,1):add_sphere(HEAD,f'HairTemple_{side}',(side*head_w*.414,.006,-.030),(head_w*.093,.080,head_d*.150),HAIR,28,18)
add_sphere(HEAD,'HairTopCap',(0,.082,-head_d*.145),(head_w*.495,.069,head_d*.350),HAIR,42,24)
# Asymmetric five-lock fringe with staggered roots; no continuous root band across the forehead.
bang_z=face_z+.019
fringe_data=[
 (-.118,-.100,-.095,.030,.054,.132),
 (-.072,-.056,-.046,.050,.050,.124),
 (-.018,-.008,-.004,-.012,.043,.141),
 (.036,.046,.040,.040,.048,.128),
 (.092,.102,.100,.052,.053,.136)
]
for i,(rootx,midx,tipx,tipy,w,rooty) in enumerate(fringe_data):
 add_ribbon(HEAD,f'FringeMajorV28_{i}',[(rootx,rooty,head_d*.02),(midx,rooty-.016,head_d*.28),(tipx,.086,face_z*.75),(tipx*.98,tipy,bang_z)],[w*.48,w,w*.70,w*.16],.0038,HAIR_HI if i in(1,3) else HAIR)
# Irregular wisps cross the major locks at different heights, producing a soft broken lower edge.
for i,(sx,tx,ty,sy) in enumerate(((-.104,-.088,.042,.116),(-.058,-.038,.025,.108),(.004,.010,.012,.121),(.054,.070,.044,.110),(.110,.120,.034,.118))):
 add_ribbon(HEAD,f'FringeWispV28_{i}',[(sx,sy,head_d*.30),((sx+tx)*.5,sy-.025,face_z*.70),(tx,ty,bang_z+.001)],[.018,.013,.0035],.0025,HAIR_HI if i in(0,4) else HAIR)
# Narrow crown flows bridge scalp to the staggered roots without forming a visible rim.
for i,(lane,sy) in enumerate(((-.28,.143),(-.13,.136),(.015,.146),(.16,.138),(.30,.142))):
 add_ribbon(HEAD,f'CrownFlowV28_{i}',[(lane*head_w,sy,-head_d*.23),(lane*head_w*.95,sy-.009,-head_d*.04),(lane*head_w*.88,sy-.020,head_d*.15),(lane*head_w*.80,sy-.032,face_z*.42)],[.019,.023,.019,.0065],.0024,HAIR_HI if i in(1,3) else HAIR)
add_ribbon(HEAD,'TempleWispV28L',[(-.120,.084,bang_z),(-.132,.046,bang_z),(-.138,-.010,bang_z-.004)],[.016,.010,.0035],.0025,HAIR)
add_ribbon(HEAD,'TempleWispV28R',[(.120,.084,bang_z),(.132,.046,bang_z),(.138,-.010,bang_z-.004)],[.016,.010,.0035],.0025,HAIR)
# Longer side fringe frames the jaw like the supplied sheet.
for side in(-1,1):
 add_ribbon(HEAD,f'FaceFrame_{side}',[(side*head_w*.365,.070,-.006),(side*head_w*.445,-.012,head_d*.115),(side*head_w*.458,-.178,head_d*.044),(side*head_w*.395,-.415,-.020)],[.042,.038,.026,.010],.0052,HAIR)
 add_ribbon(HEAD,f'FaceFrameFine_{side}',[(side*head_w*.408,.046,-.016),(side*head_w*.478,-.078,head_d*.060),(side*head_w*.486,-.270,.000),(side*head_w*.425,-.495,-.042)],[.020,.018,.013,.006],.0038,HAIR_HI)
# High ponytail with backward launch, broad upper mass and fine taper.
add_sphere(HEAD,'PonyRootMass',(0,.148,-head_d*.410),(.076,.061,.064),HAIR,32,22)
add_box(HEAD,'HairTie',(0,.143,-head_d*.470),(.090,.023,.034),SILVER,.007)
for side in(-1,1):add_box(HEAD,f'HairTieFin_{side}',(side*.055,.147,-head_d*.475),(.009,.086,.018),SILVER,.003,rot=(0,0,side*.18))
PONY=empty('BL_PONY_DYNAMIC',HEAD)
pony_specs=[
 (-.090,-.126,-.185,1.50,.050,-.010),
 (-.068,-.098,-.150,1.58,.053,.008),
 (-.046,-.070,-.112,1.66,.056,-.006),
 (-.024,-.038,-.062,1.71,.057,.010),
 (0.000,.006,.012,1.74,.059,-.008),
 (.024,.038,.062,1.70,.057,.009),
 (.046,.070,.112,1.65,.056,-.007),
 (.068,.098,.150,1.57,.053,.008),
 (.090,.126,.185,1.49,.050,-.010)
]
for i,(rx,mx,ex,endy,w,zoff) in enumerate(pony_specs):
 sway=(-1 if i%2==0 else 1)*.016
 root_y=.146-(i%3)*.010
 add_ribbon(PONY,f'PonyBundleV28_{i}',[(rx,root_y,-head_d*.50+zoff),(rx*.92,.020-(i%2)*.008,-head_d*.78+zoff),(mx+sway,-.300,-.474+zoff),(mx-sway,-.665,-.350+zoff),(ex+sway,-1.035,-.240+zoff),(ex,-1.365,-.123+zoff),(ex*.94,-endy,-.038+zoff)],[w*.68,w,w*1.06,w*.98,w*.76,w*.44,.008],.0045,HAIR_HI if i in(2,6) else HAIR)
# Three recessed under-layers restore healthy hair mass while preserving clear gaps between the front bundles.
for i,(lane,w) in enumerate(((-.060,.050),(0,.055),(.060,.050))):
 add_ribbon(PONY,f'PonyUnderV27_{i}',[(lane,.130,-head_d*.56),(lane*1.10,-.030,-head_d*.82),(lane*1.35,-.390,-.505),(lane*1.55,-.790,-.365),(lane*1.70,-1.180,-.215),(lane*1.78,-1.520,-.075)],[w*.72,w,w*.94,w*.82,w*.56,.010],.0040,HAIR)
# Root feathers blend the tie into both depth layers.
for i,lane in enumerate((-.070,-.035,0,.035,.070)):
 add_ribbon(PONY,f'PonyRootV27_{i}',[(lane,.151,-head_d*.49),(lane*1.12,.078,-head_d*.66),(lane*1.25,-.055,-head_d*.78)],[.030,.038,.014],.0034,HAIR_HI if i in(1,3) else HAIR)
# Fine irregular edge strands avoid a cut-paper silhouette.
for i in range(16):
 lane=(i-7.5)/7.5
 side=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV27_{i}',[(lane*.056,.138,-head_d*.53),(lane*.095+side*.009,-.085,-head_d*.80),(lane*.148-side*.014,-.455,-.455),(lane*.214+side*.015,-.875,-.292),(lane*.278-side*.010,-1.285,-.148),(lane*.318,-1.600-(i%4)*.028,-.030)],.0018+(i%3)*.00032,HAIR_HI if i%5==0 else HAIR)

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
