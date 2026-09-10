from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V86' in s:
    print('Blender heroine generator already carries REFERENCE_V86')
    raise SystemExit(0)
if '# REFERENCE_V85' not in s:
    raise SystemExit('REFERENCE_V85 generator required before v8.6')

s=s.replace(
    '# REFERENCE_V85: scalp-hugging convex fringe surfaces replace the braided/tubular front locks.',
    '# REFERENCE_V85: scalp-hugging convex fringe surfaces replace the braided/tubular front locks.\n# REFERENCE_V86: high-sample Catmull-Clark fringe surfaces for smooth production hair silhouette.',
    1,
)

old=""" cols=5;fs=(-1.0,-.5,0.0,.5,1.0);verts=[];n=len(pts)
"""
new=""" cols=9;fs=(-1.0,-.75,-.5,-.25,0.0,.25,.5,.75,1.0);verts=[];n=len(pts)
"""
if old not in s:
    raise SystemExit('v8.6 fringe sampling anchor missing')
s=s.replace(old,new,1)

old_mod=""" o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 bevel=o.modifiers.new('fringe_edge_soften','BEVEL');bevel.width=.0015;bevel.segments=2
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 return parent(o,p)
"""
new_mod=""" o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 # One Catmull-Clark pass converts the low-poly folded sheet into a continuous hair mass while
 # preserving enough edge definition for the side-swept silhouette. The denser cross-section above
 # prevents the broad triangular facets seen in the v8.5 five-view portrait audit.
 subd=o.modifiers.new('fringe_surface_smooth','SUBSURF');subd.subdivision_type='CATMULL_CLARK';subd.levels=1;subd.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=subd.name)
 bevel=o.modifiers.new('fringe_edge_soften','BEVEL');bevel.width=.0011;bevel.segments=2
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 return parent(o,p)
"""
if old_mod not in s:
    raise SystemExit('v8.6 fringe modifier anchor missing')
s=s.replace(old_mod,new_mod,1)

# v8.5 already has the correct overall placement. Slightly lower the centre lift so smoothing does
# not balloon the surface away from the forehead after subdivision.
s=s.replace(
    "[.0060,.0075,.0080,.0065,.0045,.0020],HAIR,.0036)",
    "[.0050,.0062,.0068,.0056,.0038,.0017],HAIR,.0034)",
    1,
)
s=s.replace(
    "[.0050,.0065,.0070,.0060,.0040,.0015],HAIR_HI,.0033)",
    "[.0042,.0054,.0059,.0050,.0034,.0013],HAIR_HI,.0031)",
    1,
)
s=s.replace(
    "[.0055,.0065,.0060,.0030],HAIR,.0034)",
    "[.0046,.0054,.0050,.0025],HAIR,.0032)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V86: dense Catmull-Clark fringe surfaces with reduced crown lift')
