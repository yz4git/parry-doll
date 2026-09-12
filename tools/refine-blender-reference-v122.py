from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V122' in s:
    print('Blender heroine generator already carries REFERENCE_V122')
    raise SystemExit(0)
if '# REFERENCE_V121' not in s:
    raise SystemExit('REFERENCE_V121 generator required before v12.2')

marker="# REFERENCE_V121: audit correction keeps visible eye/mouth meshes in the face asset, leaves expression pivots transform-neutral, and narrows the adult-anime eye aperture for clean profile/3q views."
if marker not in s:
    raise SystemExit('v12.2 REFERENCE_V121 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V122: real skin eyelid meshes use a Blink morph target so eyes close over the globe instead of scaling the eyeball.",1)

# Add a compact two-strip eyelid mesh.  Its Basis is open; the Blink shape brings the upper
# lid most of the way down and the lower lid slightly upward, meeting over the convex eyeball.
anchor="# v11.9 key-art eyes: the white aperture stays adult-shaped, but a dark complete contour and larger warm iris\n"
if anchor not in s:
    raise SystemExit('v12.2 eye section anchor missing')
helper="""def add_blink_lid_surface(p,name,ex,cy,rx,ry,mat):
 us=(-1.0,-.55,0.0,.55,1.0)
 opened=[];closed=[]
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10542+.00034*bow
  edge=cy+ry*(.10+.86*bow);top=edge+.00415+.00055*bow
  opened.append((x,top,z-.00008));closed.append((x,top,z-.00008))
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10550+.00042*bow
  edge=cy+ry*(.10+.86*bow);close_y=cy-.00030+ry*.075*bow-.00022
  opened.append((x,edge,z));closed.append((x,close_y,z+.00016))
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10544+.00038*bow
  edge=cy-ry*(.08+.60*bow);close_y=cy-.00030+ry*.075*bow+.00022
  opened.append((x,edge,z));closed.append((x,close_y,z+.00010))
 for u in us:
  bow=max(0.0,1.0-u*u);x=ex+u*rx*.985;z=.10531+.00028*bow
  edge=cy-ry*(.08+.60*bow);bottom=edge-.00330-.00038*bow
  opened.append((x,bottom,z-.00008));closed.append((x,bottom,z-.00008))
 verts=[bpos(v) for v in opened];faces=[]
 for i in range(4):
  faces.append((i,i+1,6+i,5+i))
  faces.append((10+i,11+i,16+i,15+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);parent(o,p)
 o.shape_key_add(name='Basis')
 blink=o.shape_key_add(name='Blink')
 for i,v in enumerate(closed):blink.data[i].co=bpos(v)
 o['expression']='blink';o['blink_morph']='Blink';smooth(o)
 return o

"""
s=s.replace(anchor,helper+anchor,1)

# Add the eyelid morph mesh after each eye's brow is created, while ex/side still refer to that eye.
old=""" add_strand(HEAD,f'BrowV119_{side}',[(ex-side*.0240,.0580,.1030),(ex,.0634,.10355),(ex+side*.0265,.0560,.10305)],.00062,HAIR)
"""
new=old+""" add_blink_lid_surface(HEAD,'BL_EYELID_L' if side<0 else 'BL_EYELID_R',ex,eye_y,eye_rx,eye_ry,SKIN)
"""
if old not in s:
    raise SystemExit('v12.2 brow/eyelid insertion anchor missing')
s=s.replace(old,new,1)

# Sort the new eyelid meshes into the face asset without changing legacy eye pivots.
old="_eye_tokens=('EyeSclera','IrisOuter','IrisInner','Pupil','EyeLight','UpperLash','OuterLash','LowerLid','UpperLid')"
new="_eye_tokens=('BL_EYELID','EyeSclera','IrisOuter','IrisInner','Pupil','EyeLight','UpperLash','OuterLash','LowerLid','UpperLid')"
if old not in s:
    raise SystemExit('v12.2 eye token anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v12.1';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v12.2';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v12.2 assembly property anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V122: morph-target skin eyelids for natural globe-covering blink')
