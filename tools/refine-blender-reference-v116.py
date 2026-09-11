from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V116' in s:
    print('Blender heroine generator already carries REFERENCE_V116')
    raise SystemExit(0)
if '# REFERENCE_V115' not in s:
    raise SystemExit('REFERENCE_V115 generator required before v11.6')

marker='# REFERENCE_V115: the clean shell gains a tapered adult jaw, deeper orbital seating, stronger malar transition and a naturally wider mouth after five-view review.'
if marker not in s:
    raise SystemExit('v11.6 REFERENCE_V115 marker anchor missing')
s=s.replace(marker,marker+'\n# REFERENCE_V116: model-editor-inspired independent frontal/profile/surface controls drive the single-shell face so depth tuning no longer disturbs frontal proportions.',1)

# Load authored face controls next to the existing reference datasets.
anchor="CC0_STATS_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-stats.json')"
if anchor not in s:
    raise SystemExit('v11.6 path anchor missing')
s=s.replace(anchor,anchor+"\nFACE116_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v116.json')",1)
anchor="with open(CC0_STATS_PATH,'r',encoding='utf-8') as f:CC0_STATS=json.load(f)"
if anchor not in s:
    raise SystemExit('v11.6 load anchor missing')
s=s.replace(anchor,anchor+"\nwith open(FACE116_PATH,'r',encoding='utf-8') as f:FACE116=json.load(f)",1)

start=s.find('def add_reference_head_v113(')
end=s.find("ROOT=empty('BLENDER_HEROINE')",start)
if start<0 or end<0:
    raise SystemExit('v11.6 current single-shell builder missing')

builder=r'''def add_reference_head_v116(p,name,mat,segments=112):
 # Parameter grouping follows yz4git/model-editor: frontal metrics and side-depth metrics are
 # independent. This keeps profile edits from changing face width/jaw/eye spacing in front view.
 frontal=FACE116['frontal'];profile_ctrl=FACE116['profile'];surface=FACE116['surface']
 fw=frontal['faceWidth'];jaw=frontal['jaw'];cheek=frontal['cheekVolume']
 eye_spacing=frontal['eyeSpacing'];eye_size=frontal['eyeSize']
 nose_proj=profile_ctrl['noseProjection'];nose_width=profile_ctrl['noseWidth']
 forehead_depth=profile_ctrl['foreheadDepth'];mouth_proj=profile_ctrl['mouthProjection']
 chin_proj=profile_ctrl['chinProjection'];chin_len=profile_ctrl['chinLength']
 orbital=surface['orbitalDepth'];malar=surface['malarSupport'];hollow=surface['lowerCheekHollow']

 base_sections=[
  (.164,.071,.078,.080,-.010),(.150,.101,.084,.086,-.008),(.132,.119,.089,.091,-.006),
  (.108,.128,.094,.095,-.003),(.082,.130,.098,.097,-.001),(.058,.128,.100,.098,.001),
  (.036,.124,.101,.099,.002),(.014,.126,.102,.099,.003),(-.008,.125,.102,.100,.003),
  (-.030,.120,.102,.101,.002),(-.052,.114,.101,.102,.001),(-.072,.105,.100,.103,.000),
  (-.089,.096,.098,.103,-.001),(-.103,.087,.096,.102,-.003),(-.115,.078,.094,.101,-.004),
  (-.126,.068,.091,.098,-.006),(-.135,.056,.087,.093,-.008),(-.141,.042,.081,.086,-.009),
  (-.145,.026,.072,.078,-.010)
 ]
 sections=[]
 for yy,w,back,front,zoff in base_sections:
  # Jaw control ramps in below the mouth; upper cranium responds only to faceWidth.
  jw=max(0.0,min(1.0,(-yy-.050)/.095))
  width_scale=fw*(1.0-jw)+jaw*jw
  # chinLength changes vertical lower-face extent only, matching model-editor's side-mode intent.
  y2=yy if yy>=-.105 else -.105+(yy+.105)*chin_len
  sections.append((y2,w*width_scale,back,front,zoff))

 base_profile=[
  (.090,.0990),(.060,.1000),(.035,.1030),(.015,.1080),(-.005,.1140),(-.025,.1240),
  (-.044,.1450),(-.054,.1320),(-.063,.1190),(-.069,.1080),(-.077,.1145),(-.086,.1200),
  (-.094,.1215),(-.103,.1130),(-.110,.1050),(-.119,.1160),(-.128,.1120),(-.137,.1000),(-.145,.0860)
 ]
 profile=[]
 for yy,z in base_profile:
  ref=.100
  scale=1.0
  if yy>.035: scale=forehead_depth
  elif yy>-.068: scale=nose_proj
  elif yy>-.108: scale=mouth_proj
  else: scale=chin_proj
  profile.append((yy,ref+(z-ref)*scale))
 def sample_profile(y):
  if y>=profile[0][0]:return profile[0][1]
  if y<=profile[-1][0]:return profile[-1][1]
  for j in range(len(profile)-1):
   y0,z0=profile[j];y1,z1=profile[j+1]
   if y0>=y>=y1:
    t=(y0-y)/(y0-y1);t=t*t*(3.0-2.0*t)
    return z0+(z1-z0)*t
  return .100

 verts=[]
 for yy,w,back,front,zoff in sections:
  pz=sample_profile(yy)
  for i in range(segments):
   phi=2*math.pi*i/segments;cp=math.cos(phi);sp=math.sin(phi)
   x=cp*w;depth=front if sp>=0 else back;z=zoff+sp*depth
   if sp>0:
    fm=sp**1.48
    face_band=math.exp(-((yy+.018)/.125)**4)
    face_lat=1.0/(1.0+(abs(x)/(.096*fw))**6)
    neutral=.1005+.0012*math.exp(-((yy+.008)/.070)**2)
    z+=fm*face_band*face_lat*(neutral-z)*.78

    # Profile deformation affects Z only. Nose width is independent from frontal jaw/face width.
    pw=(.030*nose_width) if yy>-.068 else (.043 if yy>-.108 else .039)
    profile_lat=1.0/(1.0+(abs(x)/pw)**6)
    profile_band=math.exp(-((yy+.032)/.148)**6)
    z+=fm*profile_lat*profile_band*(pz-z)*.985

    for side in (-1,1):
     ex=side*.0465*eye_spacing
     z-=fm*(.0027*orbital)*math.exp(-((x-ex)/(.0265*eye_size))**2-((yy-.033)/(.0195*eye_size))**2)
     z+=fm*.0025*math.exp(-((x-ex)/.031)**2-((yy-.061)/.022)**2)
     z+=fm*(.0062*malar*cheek)*math.exp(-((x-side*.057)/.034)**2-((yy+.004)/.036)**2)
     z-=fm*(.0027*hollow)*math.exp(-((x-side*.069)/.030)**2-((yy+.054)/.035)**2)
     z-=fm*.0016*math.exp(-((x-side*.087)/.025)**2-((yy-.040)/.041)**2)
     z+=fm*.0028*math.exp(-((x-side*.0105)/(.0110*nose_width))**2-((yy+.055)/.0135)**2)
     z-=fm*.0012*math.exp(-((x-side*.018)/.014)**2-((yy+.071)/.017)**2)
     z-=fm*.0022*math.exp(-((x-side*.065*jaw)/.029)**2-((yy+.108)/.027)**2)

    z+=fm*.0044*math.exp(-(x/.052)**2-((yy+.086)/.023)**2)
    z+=fm*.0060*math.exp(-(x/.038)**2-((yy+.119)/.019)**2)
   verts.append(bpos((x,yy,z)))

 top_idx=len(verts);verts.append(bpos((0,.176,-.006)))
 bottom_y=-.105+(-.147+.105)*chin_len
 bottom_idx=len(verts);verts.append(bpos((0,bottom_y,-.011)))
 faces=[];rows=len(sections)
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 for i in range(segments):
  j=(i+1)%segments;faces.append((top_idx,j,i))
  a=(rows-1)*segments;faces.append((bottom_idx,a+i,a+j))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('reference_head_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)

'''
s=s[:start]+builder+s[end:]

if "add_reference_head_v113(HEAD,'HeadShellV113',SKIN,112)" not in s:
    raise SystemExit('v11.6 head call anchor missing')
s=s.replace("add_reference_head_v113(HEAD,'HeadShellV113',SKIN,112)","add_reference_head_v116(HEAD,'HeadShellV116',SKIN,112)",1)

# Derive eye spacing/size from the same independent frontal control group.
s=s.replace("eye_x=.0465\neye_rx=.0262\neye_ry=.0099", "eye_x=.0465*FACE116['frontal']['eyeSpacing']\neye_rx=.0262*FACE116['frontal']['eyeSize']\neye_ry=.0099*FACE116['frontal']['eyeSize']",1)

# A skin-coloured upper-lid rim adds physical thickness around the seated eye without changing aperture.
needle=" add_strand(HEAD,f'UpperLashV115_{side}',[(inner,eye_y-eye_tilt+.0006,.10255),(ex,eye_y+.0101,.10305),(outer,eye_y+eye_tilt+.0006,.10260)],.00048,HAIR)"
if needle not in s:
    raise SystemExit('v11.6 upper-lash anchor missing')
replacement=" add_strand(HEAD,f'UpperLidRimV116_{side}',[(inner+side*.0018,eye_y-eye_tilt+.0010,.10205),(ex,eye_y+.0095,.10252),(outer-side*.0018,eye_y+eye_tilt+.0010,.10210)],.00030*FACE116['surface']['upperLidThickness'],SKIN)\n"+needle
s=s.replace(needle,replacement,1)

# Mouth width and lip thickness become explicit frontal/surface controls, mirroring model-editor's separation.
s=s.replace("(-.0265,-.0849,.1189)","(-.0265*FACE116['frontal']['mouthWidth'],-.0849,.1189)")
s=s.replace("(.0265,-.0849,.1189)","(.0265*FACE116['frontal']['mouthWidth'],-.0849,.1189)")
s=s.replace("(-.0250,-.0882,.1195)","(-.0250*FACE116['frontal']['mouthWidth'],-.0882,.1195)")
s=s.replace("(.0250,-.0882,.1195)","(.0250*FACE116['frontal']['mouthWidth'],-.0882,.1195)")
s=s.replace("(-.0250,-.0884,.1196)","(-.0250*FACE116['frontal']['mouthWidth'],-.0884,.1196)")
s=s.replace("(.0250,-.0884,.1196)","(.0250*FACE116['frontal']['mouthWidth'],-.0884,.1196)")
s=s.replace("(-.0210,-.0945,.1194)","(-.0210*FACE116['frontal']['mouthWidth'],-.0945,.1194)")
s=s.replace("(.0210,-.0945,.1194)","(.0210*FACE116['frontal']['mouthWidth'],-.0945,.1194)")
s=s.replace(".00027,LIP)",".00027*FACE116['surface']['lipThickness'],LIP)")
s=s.replace(".00031,LIP)",".00031*FACE116['surface']['lipThickness'],LIP)")

# Slightly larger nostril tint follows the independently controlled nasal base.
s=s.replace("side*.0062,-.0570,.1250,.00165,.00058,FACE_DARK,18", "side*.0062*FACE116['profile']['noseWidth'],-.0570,.1250,.00165*FACE116['surface']['nostrilScale'],.00058*FACE116['surface']['nostrilScale'],FACE_DARK,18",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V116: model-editor-informed independent frontal/profile/surface controls, physical upper-lid rim and explicit lip/nose controls')
