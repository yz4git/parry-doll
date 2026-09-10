from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V112' in s:
    print('Blender heroine generator already carries REFERENCE_V112')
    raise SystemExit(0)
if '# REFERENCE_V111' not in s:
    raise SystemExit('REFERENCE_V111 generator required before v11.2')

marker='# REFERENCE_V111: the closed head shell compresses only below the jaw anchor, replacing the long UV-sphere bottom cone with a compact under-chin transition while all facial landmarks stay fixed.'
if marker not in s:
    raise SystemExit('v11.2 REFERENCE_V111 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V112: public-model study reset; one independently generated continuous adult-anime head shell replaces HeadShellV60 plus the CC0 overlay patch.',1)

root_anchor="ROOT=empty('BLENDER_HEROINE');PELVIS=empty('BL_PELVIS',ROOT);TORSO=empty('BL_TORSO',ROOT);HEAD=empty('BL_HEAD',ROOT)"
if root_anchor not in s:
    raise SystemExit('v11.2 ROOT anchor missing')

builder=r'''def add_reference_head_v112(p,name,mat,segments=112):
 # v11.2 is a clean face rebuild.  It does not reuse the old CC0 overlay topology or the v6.0 UV-sphere face sculpt.
 # The design follows production observations from public MakeHuman/MPFB and anime-base workflows:
 # one coherent cranium/orbit/cheek/jaw surface, compact adult lower face and an embedded nose/muzzle.
 sections=[
  (.164,.071,.078,.080,-.010),
  (.150,.101,.084,.086,-.008),
  (.132,.119,.089,.091,-.006),
  (.108,.128,.094,.095,-.003),
  (.082,.131,.098,.097,-.001),
  (.058,.129,.100,.097,.001),
  (.036,.125,.101,.096,.002),
  (.014,.128,.102,.096,.003),
  (-.008,.128,.102,.096,.003),
  (-.030,.124,.102,.097,.002),
  (-.052,.119,.101,.098,.001),
  (-.072,.113,.100,.099,.000),
  (-.089,.106,.098,.099,-.001),
  (-.103,.099,.096,.098,-.003),
  (-.115,.091,.094,.097,-.004),
  (-.126,.081,.091,.094,-.006),
  (-.135,.068,.087,.090,-.008),
  (-.141,.052,.081,.084,-.009),
  (-.145,.034,.072,.076,-.010)
 ]
 verts=[]
 for yy,w,back,front,zoff in sections:
  for i in range(segments):
   phi=2*math.pi*i/segments
   cp=math.cos(phi);sp=math.sin(phi)
   x=cp*w
   depth=front if sp>=0 else back
   z=zoff+sp*depth
   if sp>0:
    fm=sp**1.55
    # Broad central facial plane: public production basemeshes avoid a spherical mask and let
    # the orbit, cheek, nose and muzzle emerge from one continuous front surface.
    face_band=math.exp(-((yy+.020)/.122)**4)
    face_lat=1.0/(1.0+(abs(x)/.094)**6)
    target_front=.0995 + .0015*math.exp(-((yy+.010)/.070)**2)
    z+=fm*face_band*face_lat*(target_front-z)*.78

    # Adult orbital bowls and upper-cheek support.  Recess the eyeball seat, then project the
    # zygomatic plane below/outside it so three-quarter views keep depth instead of a flat cheek.
    for side in (-1,1):
     ex=side*.0465
     z-=fm*.0033*math.exp(-((x-ex)/.0260)**2-((yy-.033)/.0185)**2)
     z+=fm*.0045*math.exp(-((x-side*.056)/.032)**2-((yy+.004)/.034)**2)
     z-=fm*.0018*math.exp(-((x-side*.066)/.028)**2-((yy+.052)/.033)**2)
     # Temple tuck separates the cranium from the cheekbone without carving a visible groove.
     z-=fm*.0014*math.exp(-((x-side*.086)/.025)**2-((yy-.040)/.040)**2)

    # Continuous nasal pyramid.  These are surface displacements, not separate nose pieces.
    z+=fm*.0048*math.exp(-(x/.026)**2-((yy-.030)/.058)**2)      # bridge
    z+=fm*.0080*math.exp(-(x/.023)**2-((yy+.005)/.044)**2)      # dorsum
    z+=fm*.0200*math.exp(-(x/.0215)**2-((yy+.044)/.0185)**2)    # tip
    z+=fm*.0090*math.exp(-(x/.0155)**2-((yy+.059)/.0130)**2)    # columella
    # Small alar support keeps nostrils on a real nasal base rather than floating dots.
    for side in (-1,1):
     z+=fm*.0030*math.exp(-((x-side*.0100)/.0105)**2-((yy+.055)/.0135)**2)

    # Human/anime hybrid lower face: short philtrum, restrained muzzle, volumetric lips supplied
    # by the existing tint meshes, and a compact chin pad that turns under before the neck.
    z-=fm*.0018*math.exp(-(x/.017)**2-((yy+.071)/.0125)**2)
    z+=fm*.0063*math.exp(-(x/.051)**2-((yy+.085)/.0240)**2)
    z+=fm*.0098*math.exp(-(x/.036)**2-((yy+.119)/.0195)**2)
    # Jaw-angle plane: slightly recess the lateral lower face so the silhouette becomes a soft V,
    # not a flat slab and not the previous long UV-sphere cone.
    for side in (-1,1):
     z-=fm*.0018*math.exp(-((x-side*.067)/.030)**2-((yy+.105)/.028)**2)
   verts.append(bpos((x,yy,z)))

 # Close the shell with compact poles hidden by crown hair / neck overlap.
 top_idx=len(verts);verts.append(bpos((0,.176,-.006)))
 bottom_idx=len(verts);verts.append(bpos((0,-.147,-.011)))
 faces=[]
 rows=len(sections)
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 for i in range(segments):
  j=(i+1)%segments
  faces.append((top_idx,j,i))
  a=(rows-1)*segments
  faces.append((bottom_idx,a+i,a+j))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 # One subdivision pass gives the public-basemesh-like continuous surface while preserving the
 # deliberately modeled orbital / cheek / nasal planes.
 mod=o.modifiers.new('reference_head_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)

'''
s=s.replace(root_anchor,builder+root_anchor,1)

old="""# === HEAD / FACE ===
# v6.0 uses one dense UV surface. Facial depth is deliberately restrained to avoid the v5.x muzzle/nose blowout.
add_anime_head_v60(HEAD,'HeadShellV60',SKIN,96,48)
add_cc0_face_patch_v77(HEAD,'FaceQuadPatchV77',SKIN)
"""
new="""# === HEAD / FACE ===
# v11.2 full rebuild: a single new independently generated shell owns the visible face.
# The legacy HeadShellV60 and FaceQuadPatchV77 remain as unused historical helpers only.
add_reference_head_v112(HEAD,'HeadShellV112',SKIN,112)
"""
if old not in s:
    raise SystemExit('v11.2 legacy head-call anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V112: clean single-shell adult-anime face rebuild; legacy CC0 overlay disabled')
