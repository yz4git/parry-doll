from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V14' in s:
    print('Blender heroine generator already carries REFERENCE_V14')
    raise SystemExit(0)

s=s.replace('import bpy, json, os','import bpy, json, os, math',1)
s=s.replace('# Source sheet measured at H=920 px and normalized in heroine-reference-proportions.json.','# Source sheet measured at H=961 px and normalized in heroine-reference-proportions.json.\n# REFERENCE_V14: direct silhouette-driven Blender authoring pass.',1)

# Replace the old cylinder-like limb helper with a true elliptical taper, and add reusable section/ribbon builders.
a=s.index('def add_taper(')
b=s.index('def add_panel(',a)
helpers='''def add_taper(p,name,r1,r2,depth1,depth2,mat):
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

'''
s=s[:a]+helpers+s[b:]

# Sculpt the torso as one continuous measured envelope instead of overlapping spheres.
a=s.index('# Torso follows the measured hourglass envelope')
b=s.index('# Reference-like harness:',a)
torso='''# Torso follows the measured hourglass envelope as a single continuous surface.
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
'''
s=s[:a]+torso+s[b:]

# Replace pelvis primitive with a smooth high-waist transition.
old="add_sphere(PELVIS,'PelvisSuit',(0,0,0),(pelvis_w*.50,.135,pelvis_d*.50),BLACK,34,22)"
new="""add_section_mesh(PELVIS,'PelvisSuit',[
 (-.170,pelvis_w*.43,pelvis_d*.43,pelvis_d*.47,0.000),
 (-.070,pelvis_w*.50,pelvis_d*.48,pelvis_d*.52,0.004),
 (.055,pelvis_w*.49,pelvis_d*.47,pelvis_d*.50,0.004),
 (.155,waist_w*.57,waist_d*.54,waist_d*.58,0.000)
],BLACK,36)"""
if old not in s:raise SystemExit('pelvis primitive block not found')
s=s.replace(old,new,1)

# Front skirt must stop around upper thigh/crotch; only side/back tails reach toward the knee/calf like the sheet.
a=s.index('# Layered pointed skirt measured from the reference silhouette.')
b=s.index('# === HEAD / FACE ===',a)
skirt='''# Layered pointed skirt measured from the reference silhouette.
# Short front petals expose the long-leg line; long movement tails live at the sides/back.
add_panel(PELVIS,'FrontPanelL',[(-.142,.118,.125),(-.018,.108,.132),(-.035,-.205,.145),(-.092,-.305,.132),(-.185,-.205,.090)],.020,WHITE)
add_panel(PELVIS,'FrontPanelR',[(.018,.108,.132),(.142,.118,.125),(.185,-.205,.090),(.092,-.305,.132),(.035,-.205,.145)],.020,WHITE)
add_panel(PELVIS,'FrontBladeL',[(-.176,.098,.095),(-.112,.082,.112),(-.145,-.245,.118),(-.224,-.375,.070),(-.245,-.185,.052)],.016,BLACK)
add_panel(PELVIS,'FrontBladeR',[(.112,.082,.112),(.176,.098,.095),(.245,-.185,.052),(.224,-.375,.070),(.145,-.245,.118)],.016,BLACK)
add_panel(PELVIS,'SideWhiteL',[(-.172,.106,.030),(-.228,.068,-.002),(-.286,-.350,-.026),(-.258,-.650,.008),(-.215,-.470,.038)],.017,WHITE)
add_panel(PELVIS,'SideWhiteR',[(.172,.106,.030),(.228,.068,-.002),(.215,-.470,.038),(.258,-.650,.008),(.286,-.350,-.026)],.017,WHITE)
add_panel(PELVIS,'SideBladeL',[(-.215,.082,-.030),(-.262,.046,-.058),(-.320,-.405,-.078),(-.282,-.735,-.040),(-.244,-.500,-.020)],.014,BLACK)
add_panel(PELVIS,'SideBladeR',[(.215,.082,-.030),(.244,-.500,-.020),(.282,-.735,-.040),(.320,-.405,-.078),(.262,.046,-.058)],.014,BLACK)
add_panel(PELVIS,'RearWhiteL',[(-.150,.095,-.105),(-.020,.090,-.120),(-.046,-.430,-.148),(-.115,-.760,-.132),(-.238,-.505,-.082)],.017,WHITE)
add_panel(PELVIS,'RearWhiteR',[(.020,.090,-.120),(.150,.095,-.105),(.238,-.505,-.082),(.115,-.760,-.132),(.046,-.430,-.148)],.017,WHITE)
add_panel(PELVIS,'RearBladeL',[(-.205,.075,-.112),(-.142,.070,-.130),(-.176,-.500,-.165),(-.232,-.840,-.110),(-.276,-.470,-.086)],.013,BLACK)
add_panel(PELVIS,'RearBladeR',[(.142,.070,-.130),(.205,.075,-.112),(.276,-.470,-.086),(.232,-.840,-.110),(.176,-.500,-.165)],.013,BLACK)

'''
s=s[:a]+skirt+s[b:]

# Rebuild portrait: smaller jaw/eyes, swept ribbon bangs, denser ponytail mass.
a=s.index('# === HEAD / FACE ===')
b=s.index('# === LIMBS ===',a)
head='''# === HEAD / FACE ===
# v1.4 uses the remeasured 0.118H head width and 0.086H side depth.
add_sphere(HEAD,'Cranium',(0,.020,-.018),(head_w*.490,.142,head_d*.485),SKIN,40,28)
add_sphere(HEAD,'Jaw',(0,-.067,.026),(head_w*.405,.088,head_d*.405),SKIN,38,24)
add_sphere(HEAD,'Chin',(0,-.128,.055),(head_w*.245,.040,head_d*.255),SKIN,28,18)
add_cylinder(HEAD,'Neck',(0,-.188,-.004),W('neck')*.37,.108,SKIN,24)
face_z=head_d*.505
for side in(-1,1):
 add_sphere(HEAD,f'EyeWhite_{side}',(side*head_w*.172,.018,face_z),(head_w*.078,.013,.0065),SCLERA,22,12)
 add_sphere(HEAD,f'Iris_{side}',(side*head_w*.172,.018,face_z+.007),(head_w*.031,.010,.0042),IRIS,18,10)
 add_sphere(HEAD,f'Pupil_{side}',(side*head_w*.172,.018,face_z+.010),(head_w*.012,.0065,.0028),PUPIL,14,8)
 add_box(HEAD,f'Eyeliner_{side}',(side*head_w*.172,.035,face_z+.009),(head_w*.090,.006,.0035),HAIR,.0015,rot=(0,0,-side*.075))
 add_box(HEAD,f'Brow_{side}',(side*head_w*.172,.070,face_z+.002),(head_w*.108,.006,.004),HAIR,.0015,rot=(0,0,-side*.085))
add_sphere(HEAD,'Nose',(0,-.014,face_z+.007),(.010,.025,.009),SKIN,18,10)
add_box(HEAD,'Mouth',(0,-.078,face_z+.003),(.044,.006,.004),LIP,.0013)
# Hair shell is kept behind the face and sized from the skull instead of a large dome.
add_sphere(HEAD,'HairBack',(0,.035,-head_d*.22),(head_w*.535,.160,head_d*.555),HAIR,38,26)
add_sphere(HEAD,'HairCrown',(0,.112,-.020),(head_w*.525,.090,head_d*.515),HAIR,38,24)
# Seven swept ribbon bangs replace the comb-like vertical tubes.
bang_specs=[
 (-.092,-.050,-.080,.030),(-.062,-.018,-.052,.034),(-.032,.008,-.024,.037),
 ( .000,.020,.008,.038),( .032,.004,.035,.036),( .064,-.022,.064,.033),( .094,-.055,.088,.028)
]
for i,(sx,ey,ex,w0) in enumerate(bang_specs):
 add_ribbon(HEAD,f'Bang_{i}',[(sx,.142,.015),(sx*.86,.108,face_z*.66),(ex*.92,.060,face_z-.002),(ex,ey,face_z+.004)],[w0,w0*.95,w0*.72,w0*.42],.006,HAIR_HI if i in(1,5) else HAIR)
for side in(-1,1):
 for i in range(3):
  x0=side*(head_w*.38+i*.012)
  add_ribbon(HEAD,f'SideRibbon_{side}_{i}',[(x0,.095,head_d*.10),(side*(head_w*.48+i*.010),-.025,head_d*.20),(side*(head_w*.50+i*.012),-.255,head_d*.08),(side*(head_w*.43+i*.010),-.500,-.012)],[.033-i*.003,.030-i*.003,.024-i*.002,.014],.006,HAIR_HI if i==0 else HAIR)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# Broad overlapping ribbons provide the main ponytail volume; fine strands break the silhouette at the edge.
for i in range(13):
 lane=(i-6)/6;root_x=lane*.030
 add_ribbon(PONY,f'PonyRibbon_{i}',[(root_x,.104,-head_d*.47),(lane*.065,-.015,-head_d*.70),(lane*.120,-.365,-.39),(lane*.185,-.860,-.30),(lane*.245,-1.470,-.10)],[.040,.047,.052,.043,.015],.007,HAIR_HI if i%5==0 else HAIR)
for i in range(12):
 lane=(i-5.5)/5.5
 add_strand(PONY,f'PonyFine_{i}',[(lane*.018,.105,-head_d*.49),(lane*.074,-.050,-head_d*.72),(lane*.145,-.440,-.38),(lane*.230,-.980,-.25),(lane*.315,-1.520,-.075)],.0048+(i%3)*.0008,HAIR_HI if i%4==0 else HAIR)
add_box(HEAD,'HairTie',(0,.100,-head_d*.48),(.096,.030,.038),SILVER,.008)

'''
s=s[:a]+head+s[b:]

# Reference boots begin roughly one quarter down the thigh, not at the midpoint.
old="add_cylinder(group,'Garter'+name,(0,-.21,0),th*1.08,.055,BLACK,24);add_cylinder(group,'ThighBootTop'+name,(0,.235,0),th*.97,.47,BLACK,28)"
new="add_cylinder(group,'Garter'+name,(0,-.245,0),th*1.06,.048,BLACK,24);add_cylinder(group,'ThighBootTop'+name,(0,.105,0),th*.96,.70,BLACK,28)"
if old not in s:raise SystemExit('thigh boot block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V14: continuous torso, true limb taper, ribbon hair, reference skirt and face')
