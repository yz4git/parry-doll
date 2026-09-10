from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V72' in s:
    print('Blender heroine generator already carries REFERENCE_V72')
    raise SystemExit(0)
if '# REFERENCE_V71' not in s:
    raise SystemExit('REFERENCE_V71 generator required before v7.2')

s=s.replace(
    '# REFERENCE_V71: multiview-constrained integrated face surface, embedded eyes and surface-following lip tint.',
    '# REFERENCE_V71: multiview-constrained integrated face surface, embedded eyes and surface-following lip tint.\n# REFERENCE_V72: smooth 3D almond sclera lens, stronger integrated S-profile and three-quarter-safe portrait proportions.',
    1,
)

# A shallow multi-ring almond lens is curved in depth. Unlike the old fan-triangulated eye sticker,
# it is smooth under profile/three-quarter views and gives the lids a stable canthal silhouette.
anchor='\ndef add_ribbon(p,name,pts,widths,thickness,mat):\n'
helper="""
def add_almond_lens(p,name,cx,cy,cz,rx,ry,bulge,mat,rings=7,segments=48,side=1,tilt=0.0):
 verts=[bpos((cx,cy,cz+bulge))]
 for r in range(1,rings+1):
  f=r/rings
  z=cz+bulge*(1.0-f*f)
  for i in range(segments):
   a=2*math.pi*i/segments;ca=math.cos(a);sa=math.sin(a)
   x=cx+f*rx*ca
   yy=cy+f*ry*sa*(.68+.32*abs(ca))+f*tilt*side*ca
   verts.append(bpos((x,yy,z)))
 faces=[]
 for i in range(segments):faces.append((0,1+i,1+((i+1)%segments)))
 for r in range(rings-1):
  a=1+r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)

def add_ribbon(p,name,pts,widths,thickness,mat):
"""
if anchor not in s:
    raise SystemExit('add_ribbon anchor not found')
s=s.replace(anchor,'\n'+helper,1)

# Strengthen the integrated profile without reintroducing detached geometry. The target is an S-curve
# visible in profile while remaining narrow from the front.
old_profile="""    # Multiview landmark profile: one continuous surface owns bridge -> tip -> philtrum -> lips -> chin.
    z+=fm*.0058*math.exp(-(x/.021)**2-((yy+.004)/.060)**2)   # glabella / bridge
    z+=fm*.0065*math.exp(-(x/.018)**2-((yy+.025)/.034)**2)   # dorsum
    z+=fm*.0105*math.exp(-(x/.020)**2-((yy+.045)/.018)**2)   # restrained tip
    z+=fm*.0045*math.exp(-(x/.014)**2-((yy+.058)/.014)**2)   # columella
    z-=fm*.0020*math.exp(-(x/.020)**2-((yy+.068)/.012)**2)   # philtrum break
    z+=fm*.0075*math.exp(-(x/.036)**2-((yy+.080)/.012)**2)   # upper lip volume
    z+=fm*.0080*math.exp(-(x/.038)**2-((yy+.090)/.013)**2)   # lower lip volume
    z-=fm*.0035*math.exp(-(x/.034)**2-((yy+.104)/.013)**2)   # labiomental crease
    z+=fm*.0170*math.exp(-(x/.042)**2-((yy+.122)/.025)**2)   # chin support
"""
new_profile="""    # Multiview landmark profile: explicit but continuous forehead -> nose -> lips -> chin S-curve.
    z+=fm*.0065*math.exp(-(x/.020)**2-((yy+.004)/.060)**2)   # glabella / bridge
    z+=fm*.0090*math.exp(-(x/.016)**2-((yy+.025)/.034)**2)   # narrow dorsum
    z+=fm*.0180*math.exp(-(x/.017)**2-((yy+.045)/.018)**2)   # small projected tip
    z+=fm*.0070*math.exp(-(x/.012)**2-((yy+.058)/.014)**2)   # columella
    z-=fm*.0028*math.exp(-(x/.018)**2-((yy+.068)/.012)**2)   # philtrum break
    z+=fm*.0100*math.exp(-(x/.034)**2-((yy+.080)/.012)**2)   # upper lip volume
    z+=fm*.0110*math.exp(-(x/.036)**2-((yy+.090)/.013)**2)   # lower lip volume
    z-=fm*.0040*math.exp(-(x/.032)**2-((yy+.104)/.013)**2)   # labiomental crease
    z+=fm*.0240*math.exp(-(x/.040)**2-((yy+.122)/.025)**2)   # chin support
"""
if old_profile not in s:
    raise SystemExit('v7.1 profile block not found')
s=s.replace(old_profile,new_profile,1)

# Softer iris contrast removes the concentric target/ring look while retaining a dark gaze.
s=s.replace("IRIS=material('Iris',(0.036,0.028,0.031),.01,.56)","IRIS=material('Iris',(0.072,0.050,0.047),.01,.58)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.165,0.118,0.108),.01,.58)","IRIS_INNER=material('Iris Inner',(0.125,0.086,0.078),.01,.60)",1)

# Replace the exposed ellipse eyeball with a pinched, shallow 3D almond lens.
s=s.replace(
    "add_sphere(HEAD,f'EyeballV71_{side}',(ex,eye_y,.0962),(.0258,.0118,.0062),SCLERA,48,28)",
    "add_almond_lens(HEAD,f'EyeScleraV72_{side}',ex,eye_y,.0920,.0280,.0106,.0072,SCLERA,7,56,side,eye_tilt*.55)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisV71_{side}',(ex,eye_y,.1016),(.0098,.0092,.00175),IRIS,40,24)",
    "add_sphere(HEAD,f'IrisV72_{side}',(ex,eye_y,.0998),(.0092,.0088,.00155),IRIS,40,24)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisInnerV71_{side}',(ex,eye_y-.0001,.1025),(.0067,.0065,.00145),IRIS_INNER,36,22)",
    "add_sphere(HEAD,f'IrisInnerV72_{side}',(ex,eye_y-.0001,.1006),(.0067,.0064,.00135),IRIS_INNER,36,22)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'PupilV71_{side}',(ex,eye_y-.0001,.1032),(.0028,.0032,.00120),PUPIL,28,18)",
    "add_sphere(HEAD,f'PupilV72_{side}',(ex,eye_y-.0001,.1013),(.0025,.0030,.00110),PUPIL,28,18)",
    1,
)
s=s.replace("ex-side*.0035,eye_y+.0040,.1038,.0012,.0010","ex-side*.0031,eye_y+.0038,.1019,.0011,.0009",1)

# Stronger upper lid and a lower brow position reproduce the reference's soft but defined gaze.
old_lash=""" add_strand(HEAD,f'UpperLashV60_{side}',[(inner,eye_y-eye_tilt+.0012,face_front+.0025),(ex,eye_y+.0122,face_front+.0030),(outer,eye_y+eye_tilt+.0011,face_front+.0026)],.00042,HAIR)
 add_strand(HEAD,f'LowerLidV60_{side}',[(inner+side*.004,eye_y-eye_tilt-.0003,face_front+.0018),(ex,eye_y-.0084,face_front+.0021),(outer-side*.004,eye_y+eye_tilt-.0003,face_front+.0018)],.00012,FACE_DARK)
 add_strand(HEAD,f'BrowV60_{side}',[(ex-side*.027,.067,.101),(ex,.075,.103),(ex+side*.032,.064,.1015)],.00052,HAIR)
"""
new_lash=""" add_strand(HEAD,f'UpperLashV72_{side}',[(inner,eye_y-eye_tilt+.0010,.1000),(ex,eye_y+.0119,.1010),(outer,eye_y+eye_tilt+.0010,.1001)],.00062,HAIR)
 add_strand(HEAD,f'LowerLidV72_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0003,.0988),(ex,eye_y-.0081,.0992),(outer-side*.0035,eye_y+eye_tilt-.0003,.0988)],.00010,FACE_DARK)
 add_strand(HEAD,f'BrowV72_{side}',[(ex-side*.025,.064,.0995),(ex,.071,.1010),(ex+side*.029,.061,.1000)],.00062,HAIR)
"""
if old_lash not in s:
    raise SystemExit('v7.1 lash/brow block not found')
s=s.replace(old_lash,new_lash,1)

# Move the colour patch onto the now-more-projected integrated lip volume and give it readable area.
s=s.replace(
    "add_almond_surface(HEAD,'LipTintV71',0,-.0840,.0966,.0208,.0053,.00035,LIP,58,1,0.0)",
    "add_almond_surface(HEAD,'LipTintV72',0,-.0845,.1017,.0228,.0060,.00045,LIP,64,1,0.0)",
    1,
)
s=s.replace(
    "add_strand(HEAD,'MouthSeamV71',[(-.0185,-.0832,.0972),(0,-.0840,.0975),(.0185,-.0832,.0972)],.000080,FACE_DARK)",
    "add_strand(HEAD,'MouthSeamV72',[(-.0195,-.0837,.1023),(0,-.0845,.1027),(.0195,-.0837,.1023)],.000075,FACE_DARK)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V72: 3D almond eye lens and stronger integrated multiview profile')
