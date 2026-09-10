from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V85' in s:
    print('Blender heroine generator already carries REFERENCE_V85')
    raise SystemExit(0)
if '# REFERENCE_V84' not in s:
    raise SystemExit('REFERENCE_V84 generator required before v8.5')

s=s.replace(
    '# REFERENCE_V84: overlap-closed front fringe with the v8.3 face and eye proportions frozen.',
    '# REFERENCE_V84: overlap-closed front fringe with the v8.3 face and eye proportions frozen.\n# REFERENCE_V85: scalp-hugging convex fringe surfaces replace the braided/tubular front locks.',
    1,
)

# A thin closed convex strip reads as a sheet of hair with real volume rather than either a flat card
# or a round rope. Width follows the XY scalp tangent while centre lift adds a gentle Z crown.
anchor="""def add_panel(p,name,points,depth,mat):
"""
helper="""def add_fringe_surface_v85(p,name,pts,widths,lifts,mat,thickness=.0032):
 cols=5;fs=(-1.0,-.5,0.0,.5,1.0);verts=[];n=len(pts)
 for layer in (-.5,.5):
  for i,((x,y,z),w,lift) in enumerate(zip(pts,widths,lifts)):
   if i==0:tx,ty=pts[1][0]-x,pts[1][1]-y
   elif i==n-1:tx,ty=x-pts[i-1][0],y-pts[i-1][1]
   else:tx,ty=pts[i+1][0]-pts[i-1][0],pts[i+1][1]-pts[i-1][1]
   ln=max((tx*tx+ty*ty)**.5,1e-7);px,py=-ty/ln,tx/ln
   for f in fs:
    crown=max(0.0,1.0-abs(f)**1.55)
    edge_sink=.0012*(abs(f)**2)
    q=(x+px*w*.5*f,y+py*w*.5*f,z+lift*crown-edge_sink+layer*thickness)
    verts.append(bpos(q))
 faces=[];layer_count=n*cols
 # front/back grids
 for layer in range(2):
  off=layer*layer_count
  for r in range(n-1):
   a=off+r*cols;b=a+cols
   for c in range(cols-1):
    if layer==1:faces.append((a+c,a+c+1,b+c+1,b+c))
    else:faces.append((a+c,b+c,b+c+1,a+c+1))
 # close both long edges and both tips
 for r in range(n-1):
  a=r*cols;b=(r+1)*cols;aa=layer_count+a;bb=layer_count+b
  faces.append((a,b,bb,aa));a+=cols-1;b+=cols-1;aa+=cols-1;bb+=cols-1;faces.append((a,aa,bb,b))
 for c in range(cols-1):
  faces.append((c,layer_count+c,layer_count+c+1,c+1))
  a=(n-1)*cols+c;faces.append((a,a+1,layer_count+a+1,layer_count+a))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 bevel=o.modifiers.new('fringe_edge_soften','BEVEL');bevel.width=.0015;bevel.segments=2
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 return parent(o,p)

"""+anchor
if anchor not in s:
    raise SystemExit('v8.5 helper insertion anchor missing')
s=s.replace(anchor,helper,1)

old="""# v8.0 rounded scalp-following fringe. Broad geometry lives above the forehead, not as flat face cards.
add_smooth_lock(HEAD,'FringeMassV84_A',[(-.098,.190,.030),(-.084,.173,.056),(-.060,.151,.080),(-.026,.127,.101),(.018,.108,.108),(.066,.094,.107)],[.056,.061,.059,.058,.040,.012],[.020,.021,.020,.016,.011,.004],HAIR,14,6)
add_smooth_lock(HEAD,'FringeMassV84_B',[(-.040,.194,.026),(-.020,.178,.053),(.010,.156,.080),(.044,.132,.102),(.084,.111,.107),(.118,.098,.104)],[.048,.051,.048,.050,.030,.009],[.018,.019,.018,.015,.009,.003],HAIR,14,6)
add_smooth_lock(HEAD,'FringeAccentV84',[(-.116,.185,.025),(-.098,.166,.052),(-.072,.145,.079),(-.036,.124,.101),(.006,.110,.106)],[.030,.033,.032,.029,.009],[.012,.012,.011,.009,.003],HAIR_HI,12,5)
# v8.2 overlaps the exact front crown gap visible in the five-view audit. Two small rounded
# masses sit on the scalp/front transition; neither extends down across the forehead like a card.
add_smooth_lock(HEAD,'CrownRootSealV82_A',[(-.030,.187,.078),(-.016,.180,.092),(0,.172,.101),(.020,.164,.104)],[.033,.038,.032,.009],[.011,.012,.010,.003],HAIR,14,6)
add_smooth_lock(HEAD,'CrownRootSealV82_B',[(.000,.190,.074),(.014,.181,.091),(.032,.170,.101),(.050,.160,.103)],[.028,.031,.024,.007],[.010,.010,.008,.003],HAIR_HI,12,5)
"""
new="""# v8.5: two overlapping convex surfaces form a coherent side-swept fringe instead of rope-like locks.
add_fringe_surface_v85(HEAD,'FringeSurfaceV85_Main',[(-.108,.194,.034),(-.092,.177,.060),(-.064,.154,.083),(-.026,.130,.099),(.020,.110,.105),(.072,.096,.106)],[.094,.100,.096,.082,.060,.025],[.0060,.0075,.0080,.0065,.0045,.0020],HAIR,.0036)
add_fringe_surface_v85(HEAD,'FringeSurfaceV85_Over',[(-.040,.199,.030),(-.022,.181,.055),(.006,.158,.079),(.042,.135,.097),(.082,.115,.103),(.116,.102,.103)],[.070,.076,.072,.060,.040,.017],[.0050,.0065,.0070,.0060,.0040,.0015],HAIR_HI,.0033)
# A compact root overlap seals the crown/front junction while remaining visibly part of the same hair sheet.
add_fringe_surface_v85(HEAD,'FringeSurfaceV85_Root',[(-.066,.202,.036),(-.048,.190,.061),(-.025,.176,.082),(.003,.163,.097)],[.070,.076,.066,.030],[.0055,.0065,.0060,.0030],HAIR,.0034)
"""
if old not in s:
    raise SystemExit('v8.5 v8.4 fringe block missing')
s=s.replace(old,new,1)

# Fine strand lines are useful only when they sit on a coherent mass. Reduce to three subtle accents
# so the front never reads as a comb or braid at iPhone portrait scale.
old_fine="""add_strand(HEAD,'FringeFineV80_A',[(-.098,.177,.028),(-.058,.155,.076),(.030,.132,.101)],.000070,HAIR_HI)
add_strand(HEAD,'FringeFineV80_B',[(-.040,.181,.027),(.018,.158,.077),(.098,.133,.099)],.000066,HAIR_HI)
add_strand(HEAD,'FringeFineV80_C',[(-.116,.176,.026),(-.082,.158,.062),(-.012,.137,.095)],.000060,HAIR_HI)
add_strand(HEAD,'FringeFineV80_D',[(-.070,.184,.025),(-.024,.162,.065),(.058,.137,.098)],.000060,HAIR_HI)
add_strand(HEAD,'FringeFineV80_E',[(-.008,.184,.025),(.038,.163,.066),(.108,.136,.097)],.000058,HAIR_HI)
"""
new_fine="""add_strand(HEAD,'FringeFineV85_A',[(-.102,.187,.043),(-.062,.157,.084),(.026,.112,.108)],.000050,HAIR_HI)
add_strand(HEAD,'FringeFineV85_B',[(-.052,.194,.040),(.002,.160,.081),(.090,.113,.105)],.000048,HAIR_HI)
add_strand(HEAD,'FringeFineV85_C',[(-.090,.194,.040),(-.042,.172,.074),(.046,.129,.103)],.000044,HAIR_HI)
"""
if old_fine not in s:
    raise SystemExit('v8.5 fine fringe block missing')
s=s.replace(old_fine,new_fine,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V85: convex scalp-hugging fringe surfaces replace braided front locks')
