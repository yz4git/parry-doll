from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V77' in s:
    print('Blender heroine generator already carries REFERENCE_V77')
    raise SystemExit(0)
if '# REFERENCE_V76' not in s:
    raise SystemExit('REFERENCE_V76 generator required before v7.7')

s=s.replace(
    '# REFERENCE_V76: covered hairline, slimmer V-face, wider almond gaze and sculpted Cupid lips.',
    '# REFERENCE_V76: covered hairline, slimmer V-face, wider almond gaze and sculpted Cupid lips.\n# REFERENCE_V77: pinned-CC0 quad topology hybrid face retargeted to the PARRY DOLL multiview profile.',
    1,
)

old_load="""FACE75_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v75.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE75_PATH,'r',encoding='utf-8') as f:FACE75=json.load(f)
"""
new_load="""FACE75_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v75.json')
CC0_FACE_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-template-v1.json')
CC0_STATS_PATH=os.path.join(ROOT_DIR,'tools','cc0-face-topology-stats.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE75_PATH,'r',encoding='utf-8') as f:FACE75=json.load(f)
with open(CC0_FACE_PATH,'r',encoding='utf-8') as f:CC0_FACE=json.load(f)
with open(CC0_STATS_PATH,'r',encoding='utf-8') as f:CC0_STATS=json.load(f)
if CC0_FACE.get('version')!=2 or CC0_FACE.get('license')!='CC0-1.0':
 raise RuntimeError('v7.7 requires the local CC0 hm08 topology template v2')
"""
if old_load not in s:
    raise SystemExit('v7.5 load block not found')
s=s.replace(old_load,new_load,1)

anchor="""def add_anime_head_v60(p,name,mat,segments=96,rings=48):
"""
helper="""def sample_cc0_front_v77(yn):
 pts=CC0_STATS['patch']['profile_samples_normalized']
 if yn<=pts[0]['y']: return pts[0]['front_z']-.5
 if yn>=pts[-1]['y']: return pts[-1]['front_z']-.5
 for a,b in zip(pts,pts[1:]):
  if a['y']<=yn<=b['y']:
   t=(yn-a['y'])/max(b['y']-a['y'],1e-8)
   t=t*t*(3-2*t)
   return (a['front_z']*(1-t)+b['front_z']*t)-.5
 return 0.0

def add_cc0_face_patch_v77(p,name,mat):
 # CC0 supplies only topology/local relief. Heroine reference controls size, eye spacing and centre-line profile.
 verts=[]
 for vx,vy,vz in CC0_FACE['vertices']:
  yn=max(0.0,min(1.0,vy+.5))
  yy=-.145+yn*.305
  # 0.245 total mapping gives a slim 0.1225 half-face; taper the lower third into the reference V jaw.
  jaw_t=max(0.0,min(1.0,(-.025-yy)/.120))
  x=vx*.245*(1.0-.105*jaw_t)
  # Anime-reference eye spacing: spread the orbital band without widening cheeks/jaw globally.
  orbital=math.exp(-((yy-.031)/.035)**2)
  x+=math.copysign(.0060*orbital*max(0.0,1.0-abs(x)/.122),x) if abs(x)>1e-8 else 0.0
  # Lock the foremost profile at every height to v7.5+, then transfer only CC0's local rearward relief.
  pz,_=sample_face_profile_v75(yy)
  generic_front=sample_cc0_front_v77(yn)
  local_relief=(vz-generic_front)*.050
  # Reduce generic relief near the outer seam so it blends gently into the recessed UV cranium.
  seam=max(0.0,min(1.0,(.126-abs(x))/.040))
  relief_gain=.62+.38*seam
  z=pz+local_relief*relief_gain+.0016
  verts.append(bpos((x,yy,z)))
 faces=[tuple(f) for f in CC0_FACE['faces']]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)

def add_anime_head_v60(p,name,mat,segments=96,rings=48):
"""
if anchor not in s:
    raise SystemExit('anime head helper anchor missing')
s=s.replace(anchor,helper,1)

# Recess only the old UV-sphere facial front so the CC0 quad patch owns shading and eye/mouth openings.
old_tail="""    z+=fm*(pz-depth)*lateral
   verts.append(bpos((x,yy,z)))
"""
new_tail="""    z+=fm*(pz-depth)*lateral
    # v7.7 hybrid: keep this surface as cranium/backing but place it safely behind the local quad face patch.
    patch_y=1.0-max(0.0,min(1.0,abs(yy-.005)/.170))
    patch_x=max(0.0,min(1.0,(.132-abs(x))/.030))
    z-=fm*.0135*patch_y*patch_x
   verts.append(bpos((x,yy,z)))
"""
if old_tail not in s:
    raise SystemExit('v7.5 absolute profile tail not found')
s=s.replace(old_tail,new_tail,1)

old_head="""add_anime_head_v60(HEAD,'HeadShellV60',SKIN,96,48)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
"""
new_head="""add_anime_head_v60(HEAD,'HeadShellV60',SKIN,96,48)
add_cc0_face_patch_v77(HEAD,'FaceQuadPatchV77',SKIN)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
"""
if old_head not in s:
    raise SystemExit('head creation block missing')
s=s.replace(old_head,new_head,1)

# The structural scalp cap now reaches the advanced forehead; remove the two crossing v7.6 filler ribbons.
old_underlay="""# v7.6 front hairline underlay follows the advanced forehead and prevents skin wedges between fringe ribbons.
add_flow_ribbon(HEAD,'HairlineUnderlayV76',[(0,.188,.034),(0,.166,.060),(0,.143,.082),(0,.120,.099),(0,.101,.106)],[.118,.205,.232,.216,.176],.00125,HAIR)
add_flow_ribbon(HEAD,'HairlineSoftEdgeV76',[(-.020,.177,.050),(-.008,.153,.075),(.010,.130,.095),(.026,.111,.106)],[.150,.168,.150,.096],.00095,HAIR_HI)

"""
new_underlay="""# v7.7 single continuous front-scalp veil replaces crossed filler ribbons and closes the last forehead opening.
add_flow_ribbon(HEAD,'HairlineVeilV77',[(0,.194,.052),(0,.177,.073),(0,.158,.091),(0,.138,.103),(0,.118,.109)],[.090,.174,.220,.226,.198],.00110,HAIR)

"""
if old_underlay not in s:
    raise SystemExit('v7.6 hair underlay block missing')
s=s.replace(old_underlay,new_underlay,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V77: CC0 quad face topology fitted to heroine multiview profile')
