from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V92' in s:
    print('Blender heroine generator already carries REFERENCE_V92')
    raise SystemExit(0)
if '# REFERENCE_V91' not in s:
    raise SystemExit('REFERENCE_V91 generator required before v9.2')

s=s.replace(
    '# REFERENCE_V91: widened upper crown cap wraps the v9.0 buried fringe roots from both 3/4 views.',
    '# REFERENCE_V91: widened upper crown cap wraps the v9.0 buried fringe roots from both 3/4 views.\n# REFERENCE_V92: dedicated scalp-hugging temporal shells bridge fringe to rear hair above the ears without cheek wisps.',
    1,
)

anchor="def add_panel(p,name,points,depth,mat):\n"
helper="""def add_temporal_shell_v92(p,name,side,rows,mat,arc_segments=16):
 # rows: (logical_y, half_width, depth, z_offset).  The shell spans only the side scalp:
 # front-temple -> true side -> rear-temple, never crossing the cheek or eye region.
 angles=[-.72+1.46*i/arc_segments for i in range(arc_segments+1)]
 verts=[]
 for yy,w,d,zoff in rows:
  for a in angles:
   x=side*math.cos(a)*w
   z=zoff+math.sin(a)*d
   verts.append(bpos((x,yy,z)))
 row=len(angles);faces=[]
 for r in range(len(rows)-1):
  base=r*row;nxt=(r+1)*row
  for i in range(row-1):faces.append((base+i,base+i+1,nxt+i+1,nxt+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 # Give the scalp patch just enough physical thickness to render consistently from all audit views.
 solid=o.modifiers.new('temporal_shell_thickness','SOLIDIFY');solid.thickness=.0022;solid.offset=-.35
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=solid.name)
 sub=o.modifiers.new('temporal_shell_smooth','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=1;sub.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 return parent(o,p)

""" + anchor
if anchor not in s:
    raise SystemExit('v9.2 helper insertion anchor missing')
s=s.replace(anchor,helper,1)

insert_after="""add_rear_hair_shell(HEAD,'HairRearShellV59',[
 (-.025,head_w*.300,head_d*.410,-head_d*.066),
 (.012,head_w*.430,head_d*.500,-head_d*.058),
 (.052,head_w*.505,head_d*.550,-head_d*.050),
 (.096,head_w*.528,head_d*.562,-head_d*.042),
 (.138,head_w*.490,head_d*.517,-head_d*.033),
 (.170,head_w*.394,head_d*.422,-head_d*.024),
 (.194,head_w*.230,head_d*.270,-head_d*.013),
 (.206,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,44)

"""
addition=insert_after+"""# v9.2 fills the true remaining gap: side scalp between the side-swept fringe and rear shell.
# It stops above the ears and remains outside the facial plane, avoiding the old on-cheek wisp artifacts.
for side in (-1,1):
 add_temporal_shell_v92(HEAD,f'TemporalHairShellV92_{side}',side,[
  (.176,head_w*.390,head_d*.338,-head_d*.018),
  (.151,head_w*.455,head_d*.405,-head_d*.024),
  (.121,head_w*.492,head_d*.455,-head_d*.030),
  (.090,head_w*.505,head_d*.470,-head_d*.036),
  (.062,head_w*.474,head_d*.438,-head_d*.041),
  (.044,head_w*.425,head_d*.392,-head_d*.044)
 ],HAIR,18)

"""
if insert_after not in s:
    raise SystemExit('v9.2 rear-shell insertion anchor missing')
s=s.replace(insert_after,addition,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V92: scalp-hugging temporal shells bridge fringe to rear hair above ears')
