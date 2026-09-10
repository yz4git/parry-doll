from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V110' in s:
    print('Blender heroine generator already carries REFERENCE_V110')
    raise SystemExit(0)
if '# REFERENCE_V109' not in s:
    raise SystemExit('REFERENCE_V109 generator required before v11.0')

marker='# REFERENCE_V109: the CC0 overlay fades behind the backing shell below the mouth; the continuous head shell owns chin and under-chin silhouette with no beard-like patch edge.'
if marker not in s:
    raise SystemExit('v11.0 REFERENCE_V109 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V110: fully hidden lower CC0 faces are trimmed after the fade so no intersecting overlay triangles can reappear as chin/neck scallops in three-quarter views.',1)

old="""def add_cc0_face_patch_v77(p,name,mat):
 # CC0 supplies only topology/local relief. Heroine reference controls size, eye spacing and centre-line profile.
 verts=[]
 for vx,vy,vz in CC0_FACE['vertices']:
  yn=max(0.0,min(1.0,vy+.5))
  yy=-.145+yn*.305
"""
new="""def add_cc0_face_patch_v77(p,name,mat):
 # CC0 supplies only topology/local relief. Heroine reference controls size, eye spacing and centre-line profile.
 verts=[];logical_ys=[]
 for vx,vy,vz in CC0_FACE['vertices']:
  yn=max(0.0,min(1.0,vy+.5))
  yy=-.145+yn*.305
  logical_ys.append(yy)
"""
if old not in s:
    raise SystemExit('v11.0 CC0 vertex loop anchor missing')
s=s.replace(old,new,1)

old_faces=""" faces=[tuple(f) for f in CC0_FACE['faces']]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
"""
new_faces=""" # v11.0: v10.9 has already moved the lower overlay behind HeadShellV60. Drop faces that
 # touch the fully hidden under-chin zone so they cannot intersect back through the closed shell.
 # The cutoff remains below the mouth/labiomental work; the visible chin is owned by HeadShellV60.
 faces=[]
 for f in CC0_FACE['faces']:
  if min(logical_ys[i] for i in f) < -.118:
   continue
  faces.append(tuple(f))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
"""
if old_faces not in s:
    raise SystemExit('v11.0 CC0 face-list anchor missing')
s=s.replace(old_faces,new_faces,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V110: hidden under-chin CC0 faces trimmed to prevent shell intersection scallops')
