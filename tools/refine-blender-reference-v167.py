from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V167' in s and face.get('revision')=='v14.7':
    print('Blender heroine generator already carries REFERENCE_V167 / v14.7')
    raise SystemExit(0)
if '# REFERENCE_V166' not in s:
    raise SystemExit('REFERENCE_V166 generator required before v14.7')

marker="# REFERENCE_V166: v14.6 cuts true orbital apertures into the v14 head cage and replaces flat/profile eye helper plates with one embedded spherical sclera and shallow curved iris stack, so front, 3/4 and profile share the same physical eye."
if marker not in s:
    raise SystemExit('v14.7 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V167: v14.7 targets the actual HeadShellV140 face loop for the orbital openings, wraps the outer canthus aperture around the side plane, and restores visible iris/pupil discs on the physical sclera surface.",1)

face['revision']='v14.7'
face['reference_intent']='adult realistic-anime heroine; actual HeadShellV140 orbital holes; outer canthus wraps into side plane; one shared embedded globe per eye; visible warm iris and pupil restored on globe surface; compact v14.5 nose/lips/jaw retained'
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# v14.6 accidentally matched an earlier historical helper with the same generic face-loop text.
# This anchor includes the unique v14.0 bottom pole, so only the live HeadShellV140 topology is changed.
old=""" bottom_idx=len(verts);verts.append(bpos((0,-.146,-.011)))
 faces=[];rows=len(sections)
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 for i in range(segments):
"""
new=""" bottom_idx=len(verts);verts.append(bpos((0,-.146,-.011)))
 faces=[];rows=len(sections)
 hole_rx=FACE140['eye_target']['aperture_rx']*.96
 hole_ry=FACE140['eye_target']['aperture_ry']*1.08
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments
   ids=(a+i,a+j,b+j,b+i)
   cx=sum(logical[k][0] for k in ids)*.25
   cy=sum(logical[k][1] for k in ids)*.25
   cz=sum(logical[k][2] for k in ids)*.25
   orbital_open=False
   for side in (-1,1):
    ex=side*lm['eye_center_x']
    nx=(cx-ex)/max(hole_rx,1e-6)
    ny=(cy-lm['eye_center_y'])/max(hole_ry,1e-6)
    primary=(nx*nx+ny*ny < .90 and cz>.086)
    # A smaller outer-canthus tunnel turns the opening around the lateral face so the same globe
    # remains visible in three-quarter and exact profile without introducing a second side eye.
    outer_ex=ex+side*hole_rx*.70
    onx=(cx-outer_ex)/max(hole_rx*.44,1e-6)
    ony=(cy-lm['eye_center_y'])/max(hole_ry*.76,1e-6)
    lateral=(onx*onx+ony*ony < 1.0 and cz>.072)
    if primary or lateral:
     orbital_open=True;break
   if not orbital_open:
    faces.append(ids)
 for i in range(segments):
"""
if old not in s:
    raise SystemExit('v14.7 live HeadShellV140 loop anchor missing')
s=s.replace(old,new,1)

# Replace the buried shallow sphere iris stack with visible surface discs that sit just in front of the
# sclera sphere. A tiny outward offset gives the profile a real iris edge without changing gaze materially.
repls=(
 ("add_sphere(HEAD,f'IrisOuterV166_{side}',(ex,eye_y-.00018,.09955),(.01115*iris_scale,.00855*iris_scale,.00220),IRIS,36,24)",
  "add_ellipse_surface(HEAD,f'IrisOuterV167_{side}',ex+side*eye_rx*.055,eye_y-.00018,.10208,.01110*iris_scale,.00850*iris_scale,IRIS,60)"),
 ("add_sphere(HEAD,f'IrisInnerV166_{side}',(ex,eye_y-.00004,.10005),(.00835*iris_scale,.00620*iris_scale,.00178),IRIS_INNER,34,22)",
  "add_ellipse_surface(HEAD,f'IrisInnerV167_{side}',ex+side*eye_rx*.055,eye_y-.00004,.10224,.00830*iris_scale,.00615*iris_scale,IRIS_INNER,56)"),
 ("add_iris_rays_v129(HEAD,f'IrisRaysV166_{side}',ex,eye_y-.00005,.10192,.00745*iris_scale,.00552*iris_scale,.31,(IRIS_RAY_WARM,IRIS_RAY_DARK),28)",
  "add_iris_rays_v129(HEAD,f'IrisRaysV167_{side}',ex+side*eye_rx*.055,eye_y-.00005,.10234,.00742*iris_scale,.00548*iris_scale,.31,(IRIS_RAY_WARM,IRIS_RAY_DARK),28)"),
 ("add_sphere(HEAD,f'PupilV166_{side}',(ex,eye_y-.00038,.10062),(.00282*iris_scale,.00342*iris_scale,.00142),PUPIL,30,20)",
  "add_ellipse_surface(HEAD,f'PupilV167_{side}',ex+side*eye_rx*.055,eye_y-.00038,.10246,.00280*iris_scale,.00340*iris_scale,PUPIL,40)"),
 ("add_ellipse_surface(HEAD,f'EyeLightV166A_{side}',ex-side*.00355,eye_y+.00335,.10208,.00128,.00096,SCLERA,20)",
  "add_ellipse_surface(HEAD,f'EyeLightV167A_{side}',ex-side*.00315,eye_y+.00310,.10262,.00122,.00092,SCLERA,20)"),
 ("add_ellipse_surface(HEAD,f'EyeLightV166B_{side}',ex+side*.00205,eye_y+.00105,.10204,.00044,.00036,SCLERA,16)",
  "add_ellipse_surface(HEAD,f'EyeLightV167B_{side}',ex+side*.00220,eye_y+.00100,.10258,.00042,.00034,SCLERA,16)"),
)
for old,new in repls:
    if old not in s: raise SystemExit('v14.7 iris surface anchor missing: '+old[:72])
    s=s.replace(old,new,1)

# Move the skin rim slightly outward to cover the actual open edge after Catmull smoothing.
for old,new in (
 ("add_strand(HEAD,f'UpperSkinRimV166_{side}',[(inner+side*.0020,eye_y-eye_tilt+.0001,.10055),(ex,eye_y+.00925,.10105),(outer-side*.0015,eye_y+eye_tilt+.0002,.10062)],.00058,SKIN)",
  "add_strand(HEAD,f'UpperSkinRimV167_{side}',[(inner+side*.0015,eye_y-eye_tilt+.0001,.10100),(ex,eye_y+.00935,.10148),(outer-side*.0008,eye_y+eye_tilt+.0002,.10108)],.00062,SKIN)"),
 ("add_strand(HEAD,f'LowerSkinRimV166_{side}',[(inner+side*.0030,eye_y-eye_tilt-.0002,.10048),(ex,eye_y-.00725,.10078),(outer-side*.0030,eye_y+eye_tilt-.0001,.10052)],.00042,SKIN)",
  "add_strand(HEAD,f'LowerSkinRimV167_{side}',[(inner+side*.0025,eye_y-eye_tilt-.0002,.10094),(ex,eye_y-.00735,.10120),(outer-side*.0020,eye_y+eye_tilt-.0001,.10098)],.00046,SKIN)"),
):
    if old not in s: raise SystemExit('v14.7 rim anchor missing')
    s=s.replace(old,new,1)

old="o['face_rebuild']='v14.0';o['topology']='continuous_multiview_quad_cage';o['reference']='supplied_profile_plus_existing_front_audits'"
new="o['face_rebuild']='v14.7';o['topology']='multiview_quad_cage_with_true_orbital_openings';o['reference']='supplied_profile_plus_existing_front_audits'"
if old not in s: raise SystemExit('v14.7 topology metadata anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v14.6';"
new="ROOT['character_revision']='v14.7';"
if old not in s: raise SystemExit('v14.7 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.6';"
if needle in s: s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.7';",1)
needle="FACE_ASSET['profile_ocular_revision']='v14.6-shared-physical-globe';"
if needle in s: s=s.replace(needle,"FACE_ASSET['profile_ocular_revision']='v14.7-shared-globe-lateral-canthus';",1)
needle="FACE_ASSET['midface_plane_revision']='v14.6';"
if needle in s: s=s.replace(needle,"FACE_ASSET['midface_plane_revision']='v14.7';",1)
needle="FACE_ASSET['orbital_topology']='open-physical-eye-v14.6';"
if needle in s: s=s.replace(needle,"FACE_ASSET['orbital_topology']='open-physical-eye-v14.7-live-head';",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V167: live head orbital openings, lateral canthus wrap and visible iris/pupil surface stack')
