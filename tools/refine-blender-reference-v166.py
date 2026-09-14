from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V166' in s and face.get('revision')=='v14.6':
    print('Blender heroine generator already carries REFERENCE_V166 / v14.6')
    raise SystemExit(0)
if '# REFERENCE_V165' not in s:
    raise SystemExit('REFERENCE_V165 generator required before v14.6')

marker="# REFERENCE_V165: v14.5 rebuilds portrait readability around a larger but deeper-set almond aperture, clearer alar/nostril anatomy and fuller integrated lips while keeping the compact v14 jaw and single wrapped profile eye."
if marker not in s:
    raise SystemExit('v14.6 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V166: v14.6 cuts true orbital apertures into the v14 head cage and replaces flat/profile eye helper plates with one embedded spherical sclera and shallow curved iris stack, so front, 3/4 and profile share the same physical eye.",1)

face['revision']='v14.6'
face['reference_intent']='adult realistic-anime heroine; true open orbital apertures in unified head shell; one embedded spherical eye per side shared by front/3q/profile; curved iris and pupil stack; compact soft jaw and v14.5 nose/lips retained'
# Slightly calmer aperture because the actual opening now exposes a full globe instead of a painted sclera card.
face['eye_target']['aperture_rx']=0.0298
face['eye_target']['aperture_ry']=0.00945
face['eye_target']['iris_scale_multiplier']=0.865
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# Cut two almond-ish orbital holes directly into the unified head cage.  The head stays one mesh;
# only front-facing quads whose centres fall inside the aperture are omitted.
old=""" faces=[];rows=len(sections)
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
"""
new=""" faces=[];rows=len(sections)
 hole_rx=FACE140['eye_target']['aperture_rx']*.97
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
   if cz>.087:
    for side in (-1,1):
     ex=side*lm['eye_center_x']
     nx=(cx-ex)/max(hole_rx,1e-6)
     ny=(cy-lm['eye_center_y'])/max(hole_ry,1e-6)
     # Wider at the centre, slightly tighter toward canthi for an adult almond opening.
     if nx*nx+ny*ny < .93:
      orbital_open=True;break
   if not orbital_open:
    faces.append(ids)
"""
if old not in s:
    raise SystemExit('v14.6 face-loop anchor missing')
s=s.replace(old,new,1)

# The blink shell had been authored far in front of the face because it used to cover a painted eye card.
# Move it back to the physical orbit before building the v14.6 eye.
for old,new in (
 ("z=.10550+.00042*bow","z=.10228+.00036*bow"),
 ("z=.10544+.00038*bow","z=.10220+.00034*bow"),
 ("z=.10531+.00028*bow","z=.10208+.00025*bow"),
):
    if old not in s: raise SystemExit('v14.6 blink shell anchor missing')
    s=s.replace(old,new,1)

# Replace the flattened front/profile hybrid with one actual eyeball.  Front-most sclera lands near .1015,
# matching the new orbital rim; the same sphere now naturally reads from 3/4 and profile.
old="add_sphere(HEAD,f'EyeScleraGlobeV165_{side}',(ex,eye_y,.0917),(eye_rx*.79,eye_ry*.81,.00895),SCLERA,36,24)"
new="add_sphere(HEAD,f'EyeScleraGlobeV166_{side}',(ex,eye_y,.0832),(eye_rx*.620,eye_rx*.620,eye_rx*.620),SCLERA,48,32)"
if old not in s: raise SystemExit('v14.6 sclera globe anchor missing')
s=s.replace(old,new,1)

# Retire duplicate helper volumes/side plates.  Profile visibility now comes from the same physical globe.
remove_lines=(
 " add_sphere(HEAD,f'EyeIrisVolumeV165_{side}',(ex,eye_y-.00010,.09750),(eye_rx*.258,eye_ry*.412,.00385),IRIS,30,20)",
 " add_sphere(HEAD,f'EyePupilVolumeV165_{side}',(ex,eye_y-.00025,.09882),(eye_rx*.094,eye_ry*.198,.00270),PUPIL,24,16)",
 " add_sphere(HEAD,f'EyeProfileIrisV164_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.09915),(eye_rx*.165,eye_ry*.31,.00285),IRIS_INNER,22,14)",
 " add_sphere(HEAD,f'EyeProfilePupilV164_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10005),(eye_rx*.056,eye_ry*.155,.00195),PUPIL,18,12)",
 " add_profile_ellipse_yz_v137(HEAD,f'EyeProfileScleraYZV140_{side}',ex+side*eye_rx*1.095,eye_y+.0001,.10055,eye_ry*.72,.00860,SCLERA,48)",
 " add_profile_ellipse_yz_v137(HEAD,f'EyeProfileIrisYZV137_{side}',ex+side*eye_rx*1.102,eye_y+.0002,.10125,eye_ry*.43,.00465,IRIS_INNER,42)",
 " add_profile_ellipse_yz_v137(HEAD,f'EyeProfilePupilYZV137_{side}',ex+side*eye_rx*1.106,eye_y+.0001,.10152,eye_ry*.18,.00205,PUPIL,30)",
 " add_almond_surface(HEAD,f'EyeScleraV165_{side}',ex,eye_y,.10028,eye_rx,eye_ry,.00092,SCLERA,112,side,eye_tilt*.72)",
)
for line in remove_lines:
    if line not in s: raise SystemExit('v14.6 obsolete eye helper missing: '+line[:72])
    s=s.replace(line," # v14.6 removed: sclera/profile helper replaced by shared embedded globe",1)

# Curved iris stack: shallow ellipsoids follow the spherical sclera instead of floating flat cards.
repls=(
 ("add_ellipse_surface(HEAD,f'IrisOuterV165_{side}',ex,eye_y-.00025,.10142,.01120*iris_scale,.00865*iris_scale,IRIS,56)",
  "add_sphere(HEAD,f'IrisOuterV166_{side}',(ex,eye_y-.00018,.09955),(.01115*iris_scale,.00855*iris_scale,.00220),IRIS,36,24)"),
 ("add_ellipse_surface(HEAD,f'IrisInnerV165_{side}',ex,eye_y-.00005,.10165,.00840*iris_scale,.00628*iris_scale,IRIS_INNER,52)",
  "add_sphere(HEAD,f'IrisInnerV166_{side}',(ex,eye_y-.00004,.10005),(.00835*iris_scale,.00620*iris_scale,.00178),IRIS_INNER,34,22)"),
 ("add_iris_rays_v129(HEAD,f'IrisRaysV165_{side}',ex,eye_y-.00005,.10178,.00755*iris_scale,.00562*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),26)",
  "add_iris_rays_v129(HEAD,f'IrisRaysV166_{side}',ex,eye_y-.00005,.10192,.00745*iris_scale,.00552*iris_scale,.31,(IRIS_RAY_WARM,IRIS_RAY_DARK),28)"),
 ("add_ellipse_surface(HEAD,f'PupilV165_{side}',ex,eye_y-.00045,.10192,.00288*iris_scale,.00352*iris_scale,PUPIL,38)",
  "add_sphere(HEAD,f'PupilV166_{side}',(ex,eye_y-.00038,.10062),(.00282*iris_scale,.00342*iris_scale,.00142),PUPIL,30,20)"),
 ("add_ellipse_surface(HEAD,f'EyeLightV119A_{side}',ex-side*.00355,eye_y+.00335,.10520,.00135,.00103,SCLERA,20)",
  "add_ellipse_surface(HEAD,f'EyeLightV166A_{side}',ex-side*.00355,eye_y+.00335,.10208,.00128,.00096,SCLERA,20)"),
 ("add_ellipse_surface(HEAD,f'EyeLightV119B_{side}',ex+side*.00205,eye_y+.00105,.10518,.00048,.00040,SCLERA,16)",
  "add_ellipse_surface(HEAD,f'EyeLightV166B_{side}',ex+side*.00205,eye_y+.00105,.10204,.00044,.00036,SCLERA,16)"),
)
for old,new in repls:
    if old not in s: raise SystemExit('v14.6 iris/highlight anchor missing: '+old[:72])
    s=s.replace(old,new,1)

# Give the orbital hole a soft skin rim so the open head mesh reads as eyelid thickness rather than a cut edge.
anchor=" add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0036,eye_y+eye_tilt+.0017,.10325),(outer+side*.0058,eye_y+eye_tilt+.0052,.10330),(outer+side*.0108,eye_y+eye_tilt+.0037,.10318)],.00066*eye_contrast,HAIR)"
if anchor not in s: raise SystemExit('v14.6 lid rim insertion anchor missing')
extra="\n add_strand(HEAD,f'UpperSkinRimV166_{side}',[(inner+side*.0020,eye_y-eye_tilt+.0001,.10055),(ex,eye_y+.00925,.10105),(outer-side*.0015,eye_y+eye_tilt+.0002,.10062)],.00058,SKIN)\n add_strand(HEAD,f'LowerSkinRimV166_{side}',[(inner+side*.0030,eye_y-eye_tilt-.0002,.10048),(ex,eye_y-.00725,.10078),(outer-side*.0030,eye_y+eye_tilt-.0001,.10052)],.00042,SKIN)"
s=s.replace(anchor,anchor+extra,1)

old="ROOT['character_revision']='v14.5';"
new="ROOT['character_revision']='v14.6';"
if old not in s: raise SystemExit('v14.6 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.5';"
if needle in s: s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.6';",1)
needle="FACE_ASSET['profile_ocular_revision']='v14.5-deeper-almond-canthus';"
if needle in s: s=s.replace(needle,"FACE_ASSET['profile_ocular_revision']='v14.6-shared-physical-globe';",1)
needle="FACE_ASSET['midface_plane_revision']='v14.5';"
if needle in s: s=s.replace(needle,"FACE_ASSET['midface_plane_revision']='v14.6';",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s: s=s.replace(needle,"FACE_ASSET['orbital_topology']='open-physical-eye-v14.6';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V166: true orbital openings with shared spherical eyes and curved iris stack')
