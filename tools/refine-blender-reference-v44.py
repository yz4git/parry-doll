from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V44' in s:
    print('Blender heroine generator already carries REFERENCE_V44')
    raise SystemExit(0)
if '# REFERENCE_V43' not in s:
    raise SystemExit('REFERENCE_V43 generator required before v4.4')

s=s.replace(
    '# REFERENCE_V43: softer adult portrait, blunt side-swept fringe and a true side-flow ponytail.',
    '# REFERENCE_V43: softer adult portrait, blunt side-swept fringe and a true side-flow ponytail.\n# REFERENCE_V44: rebuilt portrait head topology, larger inset eyes and sheet-like swept bangs.',
    1,
)

# Reference key art uses soft pale skin, subtle lips and warm charcoal-brown hair rather than pure black.
s=s.replace("HAIR=material('Hair',(0.007,0.006,0.010),0.0,.52)", "HAIR=material('Hair',(0.020,0.014,0.019),0.0,.54)", 1)
s=s.replace("HAIR_HI=material('Hair Highlight',(0.026,0.020,0.030),0.0,.46)", "HAIR_HI=material('Hair Highlight',(0.070,0.045,0.052),0.0,.48)", 1)
s=s.replace("LIP=material('Lip',(0.38,0.13,0.16),0,.52)", "LIP=material('Lip',(0.38,0.22,0.22),0,.60)", 1)

# Add a dedicated portrait shell. Unlike the old generic anatomical head, this surface deliberately
# shapes the orbital rim, zygomatic plane, muzzle, jaw and chin in one continuous mesh.
anchor='def add_lock_mesh(p,name,pts,widths,depths,mat,ring_segments=10):'
if 'def add_portrait_head_v44' not in s:
    fn="""def add_portrait_head_v44(p,name,sections,mat,segments=96):
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
     z+=fm*.0145*math.exp(-((x-cheek_x)/(head_w*.105))**2-((yy+.010)/.040)**2)
     # Deep orbital bowl with a softer lower lid shelf.
     eye_x=side*head_w*.148
     z-=fm*.0205*math.exp(-((x-eye_x)/(head_w*.118))**2-((yy-.031)/.025)**2)
     z+=fm*.0048*math.exp(-((x-eye_x)/(head_w*.120))**2-((yy-.068)/.024)**2)
     z+=fm*.0030*math.exp(-((x-eye_x)/(head_w*.115))**2-((yy+.002)/.020)**2)
     # Lower-cheek hollow and nasolabial transition form a readable adult mid-face plane.
     z-=fm*.0048*math.exp(-((x-side*head_w*.275)/(head_w*.095))**2-((yy+.052)/.038)**2)
     z-=fm*.0022*math.exp(-((x-side*head_w*.105)/(head_w*.070))**2-((yy+.065)/.028)**2)
    # Continuous nose bridge, dorsum, tip and columella.
    z+=fm*.0100*math.exp(-(x/(head_w*.070))**2-((yy-.036)/.080)**2)
    z+=fm*.0180*math.exp(-(x/(head_w*.060))**2-((yy+.005)/.058)**2)
    z+=fm*.0410*math.exp(-(x/(head_w*.070))**2-((yy+.043)/.023)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.047))**2-((yy+.059)/.016)**2)
    # Soft muzzle and lip cushion, then a separate chin plane.
    z+=fm*.0065*math.exp(-(x/(head_w*.150))**2-((yy+.082)/.024)**2)
    z-=fm*.0028*math.exp(-(x/(head_w*.055))**2-((yy+.066)/.014)**2)
    z+=fm*.0105*math.exp(-(x/(head_w*.120))**2-((yy+.124)/.020)**2)
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

"""
    s=s.replace(anchor,fn+anchor,1)

# Replace the old measured shell with a narrower oval/jaw silhouette and denser portrait topology.
a=s.index("add_anatomical_head(HEAD,'HeadShellV37',[")
b=s.index('],SKIN,76)',a)+len('],SKIN,76)')
head="""add_portrait_head_v44(HEAD,'HeadShellV44',[
 (-.148,head_w*.050,head_d*.145,head_d*.188,.052),
 (-.137,head_w*.105,head_d*.190,head_d*.238,.047),
 (-.123,head_w*.190,head_d*.248,head_d*.302,.038),
 (-.105,head_w*.270,head_d*.302,head_d*.360,.028),
 (-.083,head_w*.335,head_d*.350,head_d*.414,.018),
 (-.058,head_w*.382,head_d*.390,head_d*.454,.009),
 (-.030,head_w*.414,head_d*.420,head_d*.480,.002),
 (.000,head_w*.434,head_d*.438,head_d*.492,-.003),
 (.030,head_w*.444,head_d*.450,head_d*.494,-.007),
 (.060,head_w*.438,head_d*.458,head_d*.480,-.011),
 (.090,head_w*.414,head_d*.456,head_d*.446,-.016),
 (.117,head_w*.372,head_d*.444,head_d*.400,-.022),
 (.140,head_w*.312,head_d*.420,head_d*.344,-.027),
 (.158,head_w*.225,head_d*.390,head_d*.282,-.030)
],SKIN,96)"""
s=s[:a]+head+s[b:]

# Rebuild facial placement around the new shell. Eyes are larger than v4.3 but remain inset in the orbit.
a=s.index('# Anatomy v4.3:')
b=s.index('# Hair v4.3:',a)
face="""# Anatomy v4.4: portrait proportions matched to the key-art close-up.
face_front=head_d*.514
eye_y=.0320
eye_x=head_w*.145
eye_rx=head_w*.105
eye_ry=.0142
eye_tilt=.0034
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV44_{side}',(ex,eye_y,head_d*.420),(head_w*.083,.0175,head_d*.062),SCLERA,40,24)
 add_almond_surface(HEAD,f'EyeOpeningV44_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0026,SCLERA,44,side,eye_tilt)
 add_sphere(HEAD,f'IrisV44_{side}',(ex,eye_y+.0003,face_front+.0059),(head_w*.0435,.0104,.0030),IRIS,34,20)
 add_sphere(HEAD,f'PupilV44_{side}',(ex,eye_y+.0002,face_front+.0086),(head_w*.0142,.0051,.0019),PUPIL,24,14)
 add_sphere(HEAD,f'EyeLightV44_{side}',(ex-side*head_w*.0092,eye_y+.0052,face_front+.0106),(head_w*.0052,.0023,.0011),SCLERA,12,8)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV44_{side}',[(inner,inner_y+.0011,face_front+.0035),(ex,eye_y+.0143,face_front+.0059),(outer,outer_y+.0012,face_front+.0035)],.00066,SKIN)
 add_strand(HEAD,f'UpperLashV44_{side}',[(inner,inner_y+.0018,face_front+.0064),(ex,eye_y+.0148,face_front+.0080),(outer,outer_y+.0020,face_front+.0065)],.00078,HAIR)
 add_strand(HEAD,f'LashWingV44_{side}',[(outer,outer_y+.0020,face_front+.0065),(outer+side*head_w*.016,outer_y+.0065,face_front+.0070)],.00056,HAIR)
 add_strand(HEAD,f'BrowV44_{side}',[(ex-side*eye_rx*.82,.0680,head_d*.510),(ex,.0785,head_d*.516),(ex+side*eye_rx*1.02,.0660,head_d*.511)],.00108,HAIR)

# Small explicit nose pieces finish the profile; the main bridge and cheeks now come from the shell itself.
add_sphere(HEAD,'NoseTipV44',(0,-.0445,head_d*.553),(.0108,.0091,.0068),SKIN,28,16)
add_sphere(HEAD,'ColumellaV44',(0,-.0540,head_d*.548),(.0031,.0047,.0030),SKIN,18,10)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV44_{side}',(side*.0104,-.0505,head_d*.545),(.0052,.0047,.0037),SKIN,20,12)
 add_sphere(HEAD,f'NostrilV44_{side}',(side*.0072,-.0526,head_d*.550),(.00145,.0010,.00085),FACE_DARK,12,8)

# Two continuous almond surfaces give the soft, slightly parted key-art mouth without red point artifacts.
add_almond_surface(HEAD,'UpperLipV44',0,-.0810,head_d*.550,.0300,.0045,.0018,LIP,40,1,0.0)
add_almond_surface(HEAD,'LowerLipV44',0,-.0890,head_d*.549,.0275,.0054,.0021,LIP,40,1,0.0)
add_strand(HEAD,'MouthSeamV44',[(-.0255,-.0850,head_d*.552),(0,-.0863,head_d*.553),(.0255,-.0850,head_d*.552)],.00034,FACE_DARK)

"""
s=s[:a]+face+s[b:]

# Replace the claw-like v4.3 fringe with thin overlapping hair sheets. Roots overlap under the crown,
# so the forehead reads as one hairstyle rather than three separate mesh objects.
a=s.index('# Hair v4.3:')
b=s.index('# True side-flow ponytail v4.3:',a)
hair="""# Hair v4.4: overlapping sheet-like side-swept fringe and soft face framing.
add_sphere(HEAD,'HairBackV44',(0,.032,-head_d*.366),(head_w*.510,.130,head_d*.456),HAIR,56,36)
add_sphere(HEAD,'HairCrownV44',(-.020,.120,-head_d*.205),(head_w*.472,.061,head_d*.324),HAIR,52,32)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV44_{side}',(side*head_w*.407,.021,-.030),(head_w*.080,.074,head_d*.132),HAIR,32,22)

# Broad flat ribbons sweep left-to-right and terminate with blunt tapered edges near the brows.
fringe=[
 ([(-.122,.153,-head_d*.005),(-.092,.132,head_d*.220),(-.060,.105,head_d*.430),(-.035,.064,head_d*.520)],[.070,.072,.054,.018]),
 ([(-.080,.158,-head_d*.010),(-.038,.135,head_d*.238),(.010,.108,head_d*.442),(.040,.078,head_d*.520)],[.074,.076,.056,.020]),
 ([(-.030,.158,-head_d*.012),(.018,.134,head_d*.230),(.070,.102,head_d*.438),(.103,.055,head_d*.516)],[.072,.074,.054,.019]),
]
for i,(pts,widths) in enumerate(fringe):
 add_flow_ribbon(HEAD,f'FringeSheetV44_{i}',pts,widths,.0068,HAIR_HI if i==2 else HAIR)

# A small crossing sheet hides gaps around the part while leaving one clean forehead opening.
add_flow_ribbon(HEAD,'FringeCrossV44',[(-.104,.148,head_d*.010),(-.055,.128,head_d*.285),(.010,.102,head_d*.455),(.068,.071,head_d*.518)],[.030,.032,.024,.009],.0048,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.350,.087,-.010),(side*head_w*.397,.018,head_d*.068),(side*head_w*.410,-.130,head_d*.005),(side*head_w*.372,-.310,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV44_{side}',pts,[.020,.023,.014,.0045],[.0050,.0054,.0040,.0022],HAIR,8)
 add_strand(HEAD,f'FaceWispV44_{side}',[(side*head_w*.382,.074,-.006),(side*head_w*.425,-.030,head_d*.035),(side*head_w*.414,-.205,-.006),(side*head_w*.394,-.405,-.030)],.00050,HAIR_HI)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V44: rebuilt portrait topology, larger inset eyes and sheet-like swept bangs')
