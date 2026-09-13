from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V133' in s:
    print('Blender heroine generator already carries REFERENCE_V133')
    raise SystemExit(0)
if '# REFERENCE_V132' not in s:
    raise SystemExit('REFERENCE_V132 generator required before v13.3')

marker="# REFERENCE_V132: profile-eye/jaw pass strengthens the side-view lash silhouette, clears the near-eye fringe and extends the chin-underjaw flow toward the supplied portrait while preserving the accepted frontal mask."
if marker not in s:
    raise SystemExit('v13.3 REFERENCE_V132 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V133: volumetric profile-eye pass embeds a shallow sclera globe and side-swept lash fin so the eye remains readable in exact profile instead of collapsing to an edge-on plane.",1)

# The existing almond sclera/iris layers are excellent from front/3q but almost edge-on from exact profile.
# Add a mostly buried ellipsoid behind each eye. Only the front crescent reaches the facial surface, so the
# accepted frontal aperture stays the same while profile gets real corneal/scleral thickness.
old="""for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
new="""for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeScleraGlobeV133_{side}',(ex,eye_y,.0936),(eye_rx*.82,eye_ry*.88,.0107),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
"""
if old not in s:
    raise SystemExit('v13.3 eye globe anchor missing')
s=s.replace(old,new,1)

# Add a very small y/z lash fin. Because it has actual profile-plane extent, it reads in side view while
# remaining nearly invisible as extra geometry in the frontal portrait.
old=""" add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0036,eye_y+eye_tilt+.0017,.10417),(outer+side*.0058,eye_y+eye_tilt+.0052,.10422),(outer+side*.0108,eye_y+eye_tilt+.0037,.10408)],.00060*eye_contrast,HAIR)
 add_strand(HEAD,f'LowerLidV119_{side}',[(inner+side*.0040,eye_y-eye_tilt-.00035,.10374),(ex,eye_y-.00870,.10403),(outer-side*.0024,eye_y+eye_tilt-.00015,.10383)],.000215*eye_contrast,FACE_DARK)
"""
new=""" add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0036,eye_y+eye_tilt+.0017,.10417),(outer+side*.0058,eye_y+eye_tilt+.0052,.10422),(outer+side*.0108,eye_y+eye_tilt+.0037,.10408)],.00060*eye_contrast,HAIR)
 add_strand(HEAD,f'ProfileLashV133_{side}',[(outer-side*.0015,eye_y+eye_tilt+.0030,.10425),(outer+side*.0010,eye_y+eye_tilt+.0050,.1068),(outer+side*.0028,eye_y+eye_tilt+.0042,.1092)],.00024*eye_contrast,HAIR)
 add_strand(HEAD,f'LowerLidV119_{side}',[(inner+side*.0040,eye_y-eye_tilt-.00035,.10374),(ex,eye_y-.00870,.10403),(outer-side*.0024,eye_y+eye_tilt-.00015,.10383)],.000215*eye_contrast,FACE_DARK)
"""
if old not in s:
    raise SystemExit('v13.3 profile lash anchor missing')
s=s.replace(old,new,1)

# v13.1's near-side wisp still crossed the exact-profile eye centre. Keep the same strand and silhouette,
# but route the eye-height samples rearward over the temple so the globe/lashes have a visible window.
old="add_strand(HEAD,'ProfileWispV131_L',[(-.076,.122,.108),(-.083,.078,.111),(-.080,.028,.108),(-.068,-.020,.101),(-.058,-.060,.094)],.000045,HAIR)"
new="add_strand(HEAD,'ProfileWispV131_L',[(-.076,.122,.108),(-.083,.082,.107),(-.080,.045,.097),(-.068,-.006,.093),(-.058,-.060,.094)],.000040,HAIR)"
if old not in s:
    raise SystemExit('v13.3 near-eye wisp anchor missing')
s=s.replace(old,new,1)

# Shape the underjaw as a slope rather than a horizontal shelf. The centre-front chin remains at the
# accepted v13.2 height; side/rear vertices below the mouth lift progressively toward the jaw hinge.
old="""     nl=math.exp(-((x-side*.0300)/.0145)**2-((yy+.0690)/.0180)**2)
     z-=fm*.00085*nasolabial*nl
   verts.append(bpos((x,yy,z)))
"""
new="""     nl=math.exp(-((x-side*.0300)/.0145)**2-((yy+.0690)/.0180)**2)
     z-=fm*.00085*nasolabial*nl
   render_y=yy
   if yy<-.112:
    under=max(0.0,min(1.0,(-yy-.112)/.045))
    frontness=max(0.0,sp)
    render_y+=.0075*under*(1.0-frontness**1.5)
   verts.append(bpos((x,render_y,z)))
"""
if old not in s:
    raise SystemExit('v13.3 underjaw slope anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.2';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.2';HEAD_ASSET['chin_underjaw_flow_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.2';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v13.3';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HEAD_ASSET['user_reference_profile_review']=True;HEAD_ASSET['reference_profile_silhouette']='v13.3';HEAD_ASSET['chin_underjaw_flow_review']=True;HEAD_ASSET['underjaw_slope_revision']='v13.3';HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;HAIR_ASSET['profile_eye_clearance_review']=True;HAIR_ASSET['profile_eye_frame_revision']='v13.3';FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['profile_eye_review']=True;FACE_ASSET['profile_eye_volume_revision']='v13.3';FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v13.3 revision anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V133: shallow eye globes, profile lash fins, eye-clear wisp and sloped underjaw')
