from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V160' in s:
    print('Blender heroine generator already carries REFERENCE_V160')
    raise SystemExit(0)
if '# REFERENCE_V154' not in s:
    raise SystemExit('REFERENCE_V154 generator required before v14.0 rebuild')

marker="# REFERENCE_V154: exact-profile eye hero pass enlarges and slightly externalizes only the side-facing sclera/iris/pupil aperture, matching lids and lashes to that silhouette while preserving the accepted frontal/three-quarter almond eye."
if marker not in s:
    raise SystemExit('v14.0 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V160: v14.0 root face rebuild replaces the accumulated v13 centre-profile/RBF shell with one new multiview landmark cage: recessed orbit, continuous narrow nose, embedded lips, soft chin and rising under-jaw while preserving BL_HEAD, neck and blink runtime contracts.",1)

# Load the dedicated v14.0 face cage alongside the legacy controls.  The old controls remain available
# for body/hair compatibility, but the new head surface no longer depends on their accumulated profile multipliers.
old="ASSEMBLY120_PATH=os.path.join(ROOT_DIR,'tools','heroine-assembly-v120.json')"
new="ASSEMBLY120_PATH=os.path.join(ROOT_DIR,'tools','heroine-assembly-v120.json')\nFACE140_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-rebuild-v140.json')"
if old not in s:
    raise SystemExit('v14.0 face data path anchor missing')
s=s.replace(old,new,1)
old="with open(ASSEMBLY120_PATH,'r',encoding='utf-8') as f:ASSEMBLY120=json.load(f)"
new="with open(ASSEMBLY120_PATH,'r',encoding='utf-8') as f:ASSEMBLY120=json.load(f)\nwith open(FACE140_PATH,'r',encoding='utf-8') as f:FACE140=json.load(f)\nif FACE140.get('version')!=1: raise RuntimeError('v14.0 face cage version mismatch')"
if old not in s:
    raise SystemExit('v14.0 face data load anchor missing')
s=s.replace(old,new,1)

insert_anchor="\nROOT=empty('BLENDER_HEROINE')\n"
if insert_anchor not in s:
    raise SystemExit('v14.0 function insertion anchor missing')

new_function=r'''

def add_reference_head_v140(p,name,mat,segments=128):
 # v14.0 is a clean face-base pass, not another multiplier on the v11-v13 shell.
 # A single closed quad cage owns skull, face, jaw and under-jaw silhouette.  Large forms come from
 # explicit multiview rows/profile landmarks; local fields only describe anatomical planes.
 cfg=FACE140
 sections=[tuple(v) for v in cfg['sections']]
 profile=[tuple(v) for v in cfg['profile']]
 lm=cfg['feature_landmarks'];st=cfg['surface_strength']

 def sample_profile(y):
  if y>=profile[0][0]:return profile[0][1]
  if y<=profile[-1][0]:return profile[-1][1]
  for a,b in zip(profile,profile[1:]):
   if a[0]>=y>=b[0]:
    t=(a[0]-y)/max(a[0]-b[0],1e-8);t=t*t*(3.0-2.0*t)
    return a[1]*(1.0-t)+b[1]*t
  return .100

 verts=[]
 logical=[]
 for yy,w,back,front,zoff in sections:
  pz=sample_profile(yy)
  for i in range(segments):
   phi=2.0*math.pi*i/segments;cp=math.cos(phi);sp=math.sin(phi)
   x=cp*w;depth=front if sp>=0 else back;z=zoff+sp*depth
   if sp>0:
    fm=sp**1.34
    # Replace the spherical mask with a calm front facial plane before adding anatomy.
    face_band=math.exp(-((yy+.015)/.132)**4)
    plane_lat=1.0/(1.0+(abs(x)/.101)**6)
    neutral=.1002+.0010*math.exp(-((yy+.010)/.074)**2)
    z+=fm*face_band*plane_lat*(neutral-z)*.72

    # Centre-line silhouette has separate influence widths: broad forehead, narrow nose,
    # wider muzzle and chin.  This prevents the nose edit from inflating the 3/4 cheeks.
    if yy>.045:pw=.052
    elif yy>-.073:pw=.0245
    elif yy>-.111:pw=.0395
    else:pw=.0435
    centre=1.0/(1.0+(abs(x)/pw)**6)
    z+=fm*centre*(pz-z)*.992

    # Primary anatomy: orbit -> brow -> malar -> cheek hollow.  These are broad planes,
    # not engraved creases, so the face stays young and clean under gameplay lighting.
    for side in (-1,1):
     ex=side*lm['eye_center_x']
     orbit=math.exp(-((x-ex)/lm['orbit_width'])**2-((yy-lm['eye_center_y'])/lm['orbit_height'])**2)
     z-=fm*st['orbit_recess']*orbit
     brow=math.exp(-((x-ex)/.031)**2-((yy-.058)/.020)**2)
     z+=fm*st['brow_support']*brow
     malar=math.exp(-((x-side*lm['malar_x'])/.034)**2-((yy-lm['malar_y'])/.036)**2)
     z+=fm*st['malar_projection']*malar
     hollow=math.exp(-((x-side*.069)/.030)**2-((yy+.055)/.035)**2)
     z-=fm*st['buccal_hollow']*hollow
     temple=math.exp(-((x-side*.090)/.026)**2-((yy-.035)/.044)**2)
     z-=fm*st['temple_tuck']*temple
     infra=math.exp(-((x-ex)/.027)**2-((yy+.004)/.020)**2)
     z+=fm*.00125*infra

    # Nasal base is part of the continuous shell.  A tiny lateral alar shift and crease are enough;
    # the supplied-reference side profile comes from the centre-line cage rather than a detached nose.
    for side in (-1,1):
     alar=math.exp(-((x-side*.0100)/.0086)**2-((yy+.058)/.0105)**2)
     x+=side*.00072*alar
     z+=fm*st['alar_projection']*alar
     crease=math.exp(-((x-side*.0148)/.0095)**2-((yy+.066)/.0100)**2)
     z-=fm*.00105*crease

    # Subnasal break and philtrum: a real valley between nose and lip, not a painted line.
    z-=fm*.00155*math.exp(-(x/.0102)**2-((yy+.0690)/.0065)**2)
    z-=fm*st['philtrum_recess']*math.exp(-(x/.0066)**2-((yy+.0785)/.0085)**2)

    # Embedded lips: two upper lobes with Cupid notch, broad lower volume, recessed mouth corners.
    ul=(math.exp(-((x-.0094)/.0112)**2-((yy+.0862)/.0067)**2)+
        math.exp(-((x+.0094)/.0112)**2-((yy+.0862)/.0067)**2))
    z+=fm*st['upper_lip']*ul
    z-=fm*.00095*math.exp(-(x/.0048)**2-((yy+.0860)/.0048)**2)
    ll=math.exp(-(x/.0245)**2-((yy+.0950)/.0076)**2)
    z+=fm*st['lower_lip']*ll
    z-=fm*.00080*math.exp(-(x/.0300)**4-((yy+.0905)/.0027)**2)
    for side in (-1,1):
     corner=math.exp(-((x-side*lm['mouth_half_width'])/.0080)**2-((yy-lm['mouth_center_y'])/.0065)**2)
     z-=fm*st['mouth_corner']*corner

    # Lower lip/chin separation and soft chin pad.
    z-=fm*st['labiomental_recess']*math.exp(-(x/.0230)**2-((yy+.1085)/.0076)**2)
    z+=fm*st['chin_pad']*math.exp(-(x/.0290)**2-((yy-lm['chin_y'])/.0180)**2)
    for side in (-1,1):
     jaw_taper=math.exp(-((x-side*.071)/.029)**2-((yy+.119)/.025)**2)
     z-=fm*.00165*jaw_taper

   render_y=yy
   # Under-jaw is authored as a rising plane to the ear/neck rather than a horizontal cylinder cut.
   if yy<-.110:
    under=max(0.0,min(1.0,(-yy-.110)/.040));under=under*under*(3.0-2.0*under)
    frontness=max(0.0,sp)
    sideback=max(0.0,1.0-frontness**1.45)
    backness=max(0.0,min(1.0,(.112-z)/.100))
    render_y+=.0130*under*sideback+.0255*under*(backness**1.08)
    throat=max(0.0,min(1.0,(-yy-.134)/.016))
    render_y+=.0014*throat*frontness
   verts.append(bpos((x,render_y,z)));logical.append((x,render_y,z))

 top_idx=len(verts);verts.append(bpos((0,.178,-.006)))
 bottom_idx=len(verts);verts.append(bpos((0,-.146,-.011)))
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
 # One subdivision level is the runtime low/high compromise. The authored base remains a clean quad cage.
 sub=o.modifiers.new('v140_face_subdivision','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=1;sub.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 o['face_rebuild']='v14.0';o['topology']='continuous_multiview_quad_cage';o['reference']='supplied_profile_plus_existing_front_audits'
 return parent(o,p)
'''
s=s.replace(insert_anchor,new_function+insert_anchor,1)

# Swap the entire visible face shell.  Runtime hierarchy stays BL_HEAD and the old helper remains available
# only as history/fallback in source, so this is reversible without touching gameplay code.
old="add_reference_head_v120(HEAD,'HeadShellV120',SKIN,128)"
new="add_reference_head_v140(HEAD,'HeadShellV140',SKIN,128)"
if old not in s:
    raise SystemExit('v14.0 head call anchor missing')
s=s.replace(old,new,1)

# Retarget the modular eyes to the new sockets.  Exact-profile helper surfaces from v13.24 remain,
# but front/3Q aperture is rebuilt around the new head instead of inheriting the v13 proportions.
for old,new in (
    ("eye_y=.0295","eye_y=FACE140['eye_target']['center_y']"),
    ("eye_x=.0452*ASSEMBLY120['head']['eyeSpacing']","eye_x=FACE140['feature_landmarks']['eye_center_x']*ASSEMBLY120['head']['eyeSpacing']"),
    ("eye_rx=.02865*ASSEMBLY120['head']['eyeSize']","eye_rx=FACE140['eye_target']['aperture_rx']*ASSEMBLY120['head']['eyeSize']"),
    ("eye_ry=.00932*ASSEMBLY120['head']['eyeSize']","eye_ry=FACE140['eye_target']['aperture_ry']*ASSEMBLY120['head']['eyeSize']"),
    ("eye_tilt=.00312","eye_tilt=FACE140['eye_target']['tilt']"),
    ("iris_scale=ASSEMBLY120['head']['irisScale']*.915","iris_scale=ASSEMBLY120['head']['irisScale']*FACE140['eye_target']['iris_scale_multiplier']"),
):
    if old not in s:
        raise SystemExit('v14.0 eye retarget anchor missing: '+old)
    s=s.replace(old,new,1)

# Re-seat lip tint on the new embedded volumes. These remain shallow colour surfaces; geometry is owned by HeadShellV140.
old="add_panel(HEAD,'UpperLipV119_L',[(-.0288*FACE120['frontal']['mouthWidth'],-.0834,.1271),(-.0129,-.0799,.1290),(0,-.0824,.1308),(0,-.0866,.1310),(-.0112,-.0858,.1297),(-.0277*FACE120['frontal']['mouthWidth'],-.0877,.1276)],.00046*FACE120['surface']['lipThickness'],LIP)"
new="add_panel(HEAD,'UpperLipV140_L',[(-.0285,-.0844,.1248),(-.0125,-.0820,.1276),(0,-.0844,.1292),(0,-.0878,.1294),(-.0110,-.0872,.1280),(-.0273,-.0888,.1253)],.00038*FACE120['surface']['lipThickness'],LIP)"
if old not in s: raise SystemExit('v14.0 upper lip L anchor missing')
s=s.replace(old,new,1)
old="add_panel(HEAD,'UpperLipV119_R',[(0,-.0827,.1302),(.0129,-.0799,.1290),(.0288*FACE120['frontal']['mouthWidth'],-.0834,.1271),(.0277*FACE120['frontal']['mouthWidth'],-.0877,.1276),(.0112,-.0858,.1297),(0,-.0867,.1305)],.00034*FACE120['surface']['lipThickness'],LIP)"
new="add_panel(HEAD,'UpperLipV140_R',[(0,-.0844,.1292),(.0125,-.0820,.1276),(.0285,-.0844,.1248),(.0273,-.0888,.1253),(.0110,-.0872,.1280),(0,-.0878,.1294)],.00038*FACE120['surface']['lipThickness'],LIP)"
if old not in s: raise SystemExit('v14.0 upper lip R anchor missing')
s=s.replace(old,new,1)
old="add_panel(HEAD,'LowerLipV119',[(-.0277*FACE120['frontal']['mouthWidth'],-.0880,.1275),(0,-.0878,.1308),(.0277*FACE120['frontal']['mouthWidth'],-.0880,.1275),(.0233*FACE120['frontal']['mouthWidth'],-.0941,.1274),(0,-.0980,.1298),(-.0233*FACE120['frontal']['mouthWidth'],-.0941,.1274)],.00052*FACE120['surface']['lipThickness'],LIP)"
new="add_panel(HEAD,'LowerLipV140',[(-.0272,-.0901,.1254),(0,-.0897,.1293),(.0272,-.0901,.1254),(.0228,-.0950,.1252),(0,-.0990,.1282),(-.0228,-.0950,.1252)],.00046*FACE120['surface']['lipThickness'],LIP)"
if old not in s: raise SystemExit('v14.0 lower lip anchor missing')
s=s.replace(old,new,1)
old="add_strand(HEAD,'MouthSeamV119',[(-.0292,-.0867,.1275),(-.0130,-.0859,.1295),(0,-.0868,.1312),(.0130,-.0859,.1295),(.0292,-.0867,.1275)],.000095,FACE_DARK)"
new="add_strand(HEAD,'MouthSeamV140',[(-.0290,-.0890,.1254),(-.0130,-.0885,.1280),(0,-.0891,.1297),(.0130,-.0885,.1280),(.0290,-.0890,.1254)],.000085,FACE_DARK)"
if old not in s: raise SystemExit('v14.0 mouth seam anchor missing')
s=s.replace(old,new,1)

# Keep small nostril tint, aligned to the tucked v14 alar base.
old="add_ellipse_surface(HEAD,f'NostrilTintV119_{side}',side*.0062*FACE120['profile']['noseWidth'],-.0588,.1361,.00190*FACE120['surface']['nostrilScale'],.00078*FACE120['surface']['nostrilScale'],FACE_DARK,20)"
new="add_ellipse_surface(HEAD,f'NostrilTintV140_{side}',side*.0059,-.0615,.1267,.00162*FACE120['surface']['nostrilScale'],.00064*FACE120['surface']['nostrilScale'],FACE_DARK,20)"
if old not in s: raise SystemExit('v14.0 nostril tint anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.24';"
new="ROOT['character_revision']='v14.0';"
if old not in s:
    raise SystemExit('v14.0 revision anchor missing')
s=s.replace(old,new,1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.0';HEAD_ASSET['face_topology']='continuous_multiview_quad_cage';FACE_ASSET['v14_socket_retarget']=True;"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V160: new v14.0 continuous multiview head base, retargeted sockets and embedded mouth accents')
