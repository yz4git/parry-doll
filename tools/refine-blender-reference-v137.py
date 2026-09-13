from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V137' in s:
    print('Blender heroine generator already carries REFERENCE_V137')
    raise SystemExit(0)
if '# REFERENCE_V136' not in s:
    raise SystemExit('REFERENCE_V136 generator required before v13.7')

marker="# REFERENCE_V136: supplied-reference hair-profile pass warms the dark hair, reveals the ear, converts the cheek-side slab into fine layered locks and adds a restrained metallic pony ornament plus loose wisps."
if marker not in s:
    raise SystemExit('v13.7 REFERENCE_V136 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V137: profile-anatomy correction rounds/recedes the chin, lifts the rear underjaw toward a rear-set neck and adds a true side-facing iris/pupil surface plus a small earring cue.",1)

# Bring the chin back from the over-pointed v13.5 silhouette and keep lower-face length closer to the supplied portrait.
old="chin_proj=profile_ctrl['chinProjection']*1.13;chin_len=profile_ctrl['chinLength']*1.06"
new="chin_proj=profile_ctrl['chinProjection']*1.02;chin_len=profile_ctrl['chinLength']*1.00"
if old not in s:
    raise SystemExit('v13.7 chin control anchor missing')
s=s.replace(old,new,1)

# Round and slightly recess the chin while preserving the accepted nose/lip portion of the centre-line profile.
old="""  (-.077,.1105),(-.086,.1175),(-.094,.1205),(-.103,.1110),(-.111,.1030),
  (-.123,.1200),(-.135,.1155),(-.146,.0975),(-.155,.0755)
"""
new="""  (-.077,.1105),(-.086,.1175),(-.094,.1205),(-.103,.1110),(-.111,.1030),
  (-.121,.1168),(-.131,.1150),(-.140,.1040),(-.148,.0870),(-.154,.0710)
"""
if old not in s:
    raise SystemExit('v13.7 chin spline anchor missing')
s=s.replace(old,new,1)

# Directly shape the lower silhouette using actual front/back depth. Rear underjaw vertices rise much more
# strongly than the chin tip, giving the reference-like diagonal chin -> jaw hinge line instead of a shelf.
old="""   render_y=yy
   if yy<-.112:
    under=max(0.0,min(1.0,(-yy-.112)/.045))
    frontness=max(0.0,sp)
    render_y+=.0105*under*(1.0-frontness**1.55)
    # Keep the chin tip low, but lift the throat-side continuation after it so the underside rises toward the neck.
    throat=max(0.0,min(1.0,(-yy-.132)/.023))
    render_y+=.0038*throat*frontness
   verts.append(bpos((x,render_y,z)))
"""
new="""   render_y=yy
   if yy<-.112:
    under=max(0.0,min(1.0,(-yy-.112)/.042))
    frontness=max(0.0,sp)
    # Existing side/rear lift, reduced slightly now that the depth-aware term below owns the jaw angle.
    render_y+=.0075*under*(1.0-frontness**1.45)
    # z is logical front/back. As the surface travels rearward from the chin, raise it toward the jaw hinge/neck.
    backness=max(0.0,min(1.0,(.116-z)/.105))
    render_y+=.0200*under*(backness**1.18)
    # Only the very lowest centre-front samples receive a tiny lift; the visible chin tip remains low/rounded.
    throat=max(0.0,min(1.0,(-yy-.133)/.020))
    render_y+=.0022*throat*frontness
   verts.append(bpos((x,render_y,z)))
"""
if old not in s:
    raise SystemExit('v13.7 underjaw depth-shape anchor missing')
s=s.replace(old,new,1)

# Move the neck rearward under the ear instead of directly under the chin; keep the longer visible neck from v13.5.
old="""add_cylinder(HEAD,'Neck',(0,-.181,-.010),W('neck')*.305,.132,SKIN,28)
add_cylinder(HEAD,'Choker',(0,-.204,-.009),W('neck')*.44,.038,BLACK,30)
add_cylinder(HEAD,'ChokerTrim',(0,-.184,-.009),W('neck')*.45,.008,SILVER,30)
"""
new="""add_cylinder(HEAD,'Neck',(0,-.181,-.030),W('neck')*.292,.134,SKIN,30)
add_cylinder(HEAD,'Choker',(0,-.206,-.028),W('neck')*.425,.038,BLACK,30)
add_cylinder(HEAD,'ChokerTrim',(0,-.186,-.028),W('neck')*.435,.008,SILVER,30)
"""
if old not in s:
    raise SystemExit('v13.7 rear-set neck anchor missing')
s=s.replace(old,new,1)

# True profile-facing ellipse helper. The accepted front eye layers live in XY at constant Z; this YZ plane
# is nearly edge-on from front and therefore changes exact profile without turning the frontal iris into a blob.
anchor="def add_iris_rays_v129(p,name,cx,cy,cz,rx,ry,inner_ratio,mats,segments=24):"
if anchor not in s:
    raise SystemExit('v13.7 profile ellipse helper anchor missing')
helper="""def add_profile_ellipse_yz_v137(p,name,cx,cy,cz,ry,rz,mat,segments=32):
 verts=[bpos((cx,cy,cz))]
 for i in range(segments):
  a=2*math.pi*i/segments
  verts.append(bpos((cx,cy+ry*math.cos(a),cz+rz*math.sin(a))))
 faces=[(0,1+i,1+((i+1)%segments)) for i in range(segments)]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)


"""
s=s.replace(anchor,helper+anchor,1)

# Add a side-facing iris and pupil at the outer surface of each sclera globe. From front they are almost edge-on;
# from profile they produce the readable brown/black vertical eye sliver visible in the supplied portrait.
old=""" add_sphere(HEAD,f'EyeProfileIrisV135_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.10010),(eye_rx*.175,eye_ry*.34,.00325),IRIS_INNER,22,14)
 add_sphere(HEAD,f'EyeProfilePupilV135_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10105),(eye_rx*.060,eye_ry*.17,.00225),PUPIL,18,12)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
new=""" add_sphere(HEAD,f'EyeProfileIrisV135_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.10010),(eye_rx*.175,eye_ry*.34,.00325),IRIS_INNER,22,14)
 add_sphere(HEAD,f'EyeProfilePupilV135_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10105),(eye_rx*.060,eye_ry*.17,.00225),PUPIL,18,12)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*.815,eye_y+.0003,.1025,eye_ry*.43,.00255,IRIS_INNER,30)
 add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*.822,eye_y+.0002,.1029,eye_ry*.205,.00125,PUPIL,24)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
if old not in s:
    raise SystemExit('v13.7 side-facing iris anchor missing')
s=s.replace(old,new,1)

# A tiny dangling earring is a useful side-profile landmark from the supplied design and helps break the ear/hair mass.
anchor2=" add_strand(HEAD,f'EarConchaV103_{side}',[\n  (side*.1385,-.010,-.018),\n  (side*.1390,-.020,-.015),\n  (side*.1384,-.030,-.020)\n ],.00022,EAR_SHADOW)"
if anchor2 not in s:
    raise SystemExit('v13.7 earring anchor missing')
earring=anchor2+"""
 add_strand(HEAD,f'EarringDropV137_{side}',[(side*.1390,-.043,-.010),(side*.1392,-.057,-.009),(side*.1390,-.071,-.010)],.00032,SILVER)
 add_box(HEAD,f'EarringTipV137_{side}',(side*.1390,-.075,-.010),(.0045,.010,.0045),SILVER,.0015)
"""
s=s.replace(anchor2,earring,1)

old="ROOT['character_revision']='v13.6';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.6';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.5';HEAD_ASSET['reference_neck_revision']='v13.5';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.6';HAIR_ASSET['reference_profile_hair_revision']='v13.6';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.5';FACE_ASSET['profile_iris_volume_revision']='v13.5';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.7';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.7';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.7';HEAD_ASSET['reference_neck_revision']='v13.7';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.6';HAIR_ASSET['reference_profile_hair_revision']='v13.6';HAIR_ASSET['metal_ornament_revision']='v13.6';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.7';FACE_ASSET['profile_iris_volume_revision']='v13.7';FACE_ASSET['profile_side_plane_revision']='v13.7';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.7 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V137: rounded chin, diagonal underjaw, rear-set neck and true side-facing iris/pupil surfaces')
