from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V95' in s:
    print('Blender heroine generator already carries REFERENCE_V95')
    raise SystemExit(0)
if '# REFERENCE_V94' not in s:
    raise SystemExit('REFERENCE_V94 generator required before v9.5')

marker='# REFERENCE_V94: smooth elliptical side locks replace the rectangular temporal sheets and cover the ear-zone scalp naturally.'
if marker not in s:
    raise SystemExit('v9.5 REFERENCE_V94 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V95: three tapered convex scalp leaves per side replace the detached ear-pad lock with a continuous swept temple-to-rear flow.',1)

anchor="def add_panel(p,name,points,depth,mat):\n"
helper="""def add_temporal_leaf_v95(p,name,side,rows,mat,cols=7):
 # rows: (logical_y, scalp_x, center_z, half_depth, crown).  A tapered convex leaf follows
 # the side of the skull.  Its pointed ends and overlapping neighbors read as swept hair locks,
 # not a rectangular shell or a detached vertical sausage.
 fs=[-1.0+2.0*i/(cols-1) for i in range(cols)]
 verts=[]
 for yy,xbase,zc,half_depth,crown in rows:
  for f in fs:
   dome=max(0.0,1.0-f*f)
   x=side*(xbase+crown*dome)
   z=zc+half_depth*f
   verts.append(bpos((x,yy,z)))
 row=cols;faces=[]
 for r in range(len(rows)-1):
  a=r*row;b=(r+1)*row
  for i in range(row-1):faces.append((a+i,a+i+1,b+i+1,b+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 solid=o.modifiers.new('temporal_leaf_thickness','SOLIDIFY');solid.thickness=.0016;solid.offset=-.45
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
 sub=o.modifiers.new('temporal_leaf_smooth','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=1;sub.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 return parent(o,p)

"""+anchor
if anchor not in s:
    raise SystemExit('v9.5 helper insertion anchor missing')
s=s.replace(anchor,helper,1)

old="""# v9.4 replaces the sheet-like side patch with a volumetric, vertically flowing lock.
# Its radial X thickness stays thin while the logical-Z depth is broad enough to bridge temple to rear hair.
# The front edge stops well behind the cheek/nose plane, so the face silhouette remains clean.
for side in (-1,1):
 add_smooth_lock(HEAD,f'SideScalpLockV94_{side}',[
  (side*head_w*.455,.176,-head_d*.025),
  (side*head_w*.495,.145,-head_d*.030),
  (side*head_w*.520,.108,-head_d*.040),
  (side*head_w*.530,.068,-head_d*.050),
  (side*head_w*.522,.026,-head_d*.066),
  (side*head_w*.505,-.014,-head_d*.082),
  (side*head_w*.478,-.047,-head_d*.098),
  (side*head_w*.435,-.069,-head_d*.112)
 ],[.008,.013,.017,.019,.019,.017,.012,.0045],[.020,.036,.050,.058,.060,.056,.044,.014],HAIR,16,6)
 # A restrained rear-biased highlight breaks up the mass without creating a second hanging panel.
 add_smooth_lock(HEAD,f'SideScalpAccentV94_{side}',[
  (side*head_w*.482,.158,-head_d*.105),
  (side*head_w*.510,.115,-head_d*.125),
  (side*head_w*.518,.066,-head_d*.142),
  (side*head_w*.505,.018,-head_d*.155),
  (side*head_w*.472,-.030,-head_d*.162)
 ],[.004,.006,.007,.006,.002],[.010,.015,.018,.016,.006],HAIR_HI,12,5)
"""
new="""# v9.5: three overlapping tapered scalp leaves carry the side sweep from crown to rear hair.
# They span the exposed temple/ear zone in depth while remaining thin radially, so profile reads as
# layered hair rather than a vertical ear-pad.  The face plane itself stays completely untouched.
for side in (-1,1):
 add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Front_{side}',side,[
  (.188,head_w*.365, head_d*.030,.003,.0010),
  (.163,head_w*.430, head_d*.022,.015,.0020),
  (.132,head_w*.485, head_d*.012,.027,.0030),
  (.095,head_w*.515, head_d*.000,.036,.0035),
  (.056,head_w*.520,-head_d*.018,.035,.0032),
  (.020,head_w*.505,-head_d*.035,.026,.0024),
  (-.012,head_w*.470,-head_d*.050,.013,.0014),
  (-.030,head_w*.435,-head_d*.058,.003,.0006)
 ],HAIR,9)
 add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Mid_{side}',side,[
  (.186,head_w*.350,-head_d*.030,.003,.0009),
  (.158,head_w*.425,-head_d*.040,.016,.0018),
  (.124,head_w*.485,-head_d*.052,.030,.0029),
  (.084,head_w*.520,-head_d*.066,.039,.0035),
  (.042,head_w*.525,-head_d*.082,.039,.0033),
  (.004,head_w*.510,-head_d*.098,.030,.0025),
  (-.030,head_w*.480,-head_d*.112,.016,.0015),
  (-.050,head_w*.445,-head_d*.120,.003,.0006)
 ],HAIR_HI,9)
 add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Rear_{side}',side,[
  (.178,head_w*.330,-head_d*.090,.003,.0008),
  (.150,head_w*.405,-head_d*.105,.014,.0017),
  (.116,head_w*.468,-head_d*.122,.027,.0027),
  (.076,head_w*.505,-head_d*.140,.035,.0032),
  (.034,head_w*.515,-head_d*.158,.034,.0030),
  (-.004,head_w*.500,-head_d*.174,.025,.0022),
  (-.034,head_w*.468,-head_d*.187,.012,.0012),
  (-.052,head_w*.435,-head_d*.194,.003,.0005)
 ],HAIR,9)
"""
if old not in s:
    raise SystemExit('v9.5 v9.4 side-lock block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V95: layered tapered temporal leaves replace detached side locks')
