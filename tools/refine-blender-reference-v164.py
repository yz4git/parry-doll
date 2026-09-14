from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V164' in s and face.get('revision')=='v14.4':
    print('Blender heroine generator already carries REFERENCE_V164 / v14.4')
    raise SystemExit(0)
if '# REFERENCE_V163' not in s:
    raise SystemExit('REFERENCE_V163 generator required before v14.4')

marker="# REFERENCE_V163: v14.3 removes the detached lateral profile-eye plate after 3/4 audit exposed a duplicate-eye artifact; profile readability now comes from the original eye canthus wrapping farther around the orbital rim."
if marker not in s:
    raise SystemExit('v14.4 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V164: v14.4 seats the real eye deeper, turns the side helper into a restrained canthus glint, and strengthens orbital, nasal, malar and mouth planes for a less mannequin-like close portrait.",1)

# Keep the v14.2 compact jaw, but give the mid-face more anatomical separation.
face['revision']='v14.4'
face['reference_intent']='adult realistic-anime heroine; compact soft lower face retained; eyes seated inside stronger sockets; nose root, cheekbone, philtrum and lips must read as continuous facial planes in front and 3/4 without detached helper geometry'
face['surface_strength']['orbit_recess']=0.00810
face['surface_strength']['brow_support']=0.00315
face['surface_strength']['malar_projection']=0.00665
face['surface_strength']['buccal_hollow']=0.00310
face['surface_strength']['philtrum_recess']=0.00225
face['surface_strength']['upper_lip']=0.00430
face['surface_strength']['lower_lip']=0.00495
face['surface_strength']['mouth_corner']=0.00172
face['surface_strength']['labiomental_recess']=0.00205
face['surface_strength']['chin_pad']=0.00385
# Do not enlarge the anime aperture. A slightly calmer vertical opening helps the eye sit in the orbit.
face['eye_target']['aperture_rx']=0.02855
face['eye_target']['aperture_ry']=0.00905
face['eye_target']['iris_scale_multiplier']=0.865
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# Strengthen the lower orbital shelf so the eye is framed by skin instead of floating on a flat mask.
old="     z+=fm*.00125*infra"
new="     z+=fm*.00170*infra"
if old not in s:
    raise SystemExit('v14.4 infraorbital anchor missing')
s=s.replace(old,new,1)

# Add a narrow pair of nasal sidewall planes. The centre spline still owns the silhouette; these only catch 3/4 light.
old="     crease=math.exp(-((x-side*.0148)/.0095)**2-((yy+.066)/.0100)**2)\n     z-=fm*.00105*crease"
new="     crease=math.exp(-((x-side*.0148)/.0095)**2-((yy+.066)/.0100)**2)\n     z-=fm*.00105*crease\n     sidewall=math.exp(-((x-side*.0108)/.0135)**2-((yy+.018)/.0410)**2)\n     z+=fm*.00115*sidewall"
if old not in s:
    raise SystemExit('v14.4 nasal sidewall anchor missing')
s=s.replace(old,new,1)

# Seat the actual eye stack about 1.2-1.7 mm farther into the v14 orbit and reduce the spherical bulge.
repls=(
 ("add_sphere(HEAD,f'EyeScleraGlobeV133_{side}',(ex,eye_y,.0936),(eye_rx*.82,eye_ry*.84,.0102),SCLERA,34,22)",
  "add_sphere(HEAD,f'EyeScleraGlobeV164_{side}',(ex,eye_y,.0926),(eye_rx*.80,eye_ry*.82,.00945),SCLERA,34,22)"),
 ("add_sphere(HEAD,f'EyeIrisVolumeV134_{side}',(ex,eye_y-.00010,.09915),(eye_rx*.278,eye_ry*.445,.00470),IRIS,28,18)",
  "add_sphere(HEAD,f'EyeIrisVolumeV164_{side}',(ex,eye_y-.00010,.09825),(eye_rx*.270,eye_ry*.430,.00420),IRIS,28,18)"),
 ("add_sphere(HEAD,f'EyePupilVolumeV134_{side}',(ex,eye_y-.00025,.10055),(eye_rx*.100,eye_ry*.215,.00335),PUPIL,24,16)",
  "add_sphere(HEAD,f'EyePupilVolumeV164_{side}',(ex,eye_y-.00025,.09960),(eye_rx*.098,eye_ry*.208,.00300),PUPIL,24,16)"),
 ("add_sphere(HEAD,f'EyeProfileIrisV135_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.10010),(eye_rx*.175,eye_ry*.34,.00325),IRIS_INNER,22,14)",
  "add_sphere(HEAD,f'EyeProfileIrisV164_{side}',(ex+side*eye_rx*.70,eye_y+.00010,.09915),(eye_rx*.165,eye_ry*.31,.00285),IRIS_INNER,22,14)"),
 ("add_sphere(HEAD,f'EyeProfilePupilV135_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10105),(eye_rx*.060,eye_ry*.17,.00225),PUPIL,18,12)",
  "add_sphere(HEAD,f'EyeProfilePupilV164_{side}',(ex+side*eye_rx*.765,eye_y-.00005,.10005),(eye_rx*.056,eye_ry*.155,.00195),PUPIL,18,12)"),
 ("add_almond_surface(HEAD,f'EyeScleraV140_{side}',ex,eye_y,.10235,eye_rx,eye_ry,.00118,SCLERA,96,side,eye_tilt*.74)",
  "add_almond_surface(HEAD,f'EyeScleraV164_{side}',ex,eye_y,.10120,eye_rx,eye_ry,.00102,SCLERA,96,side,eye_tilt*.74)"),
 ("add_ellipse_surface(HEAD,f'IrisOuterV140_{side}',ex,eye_y-.00025,.10362,.01145*iris_scale,.00895*iris_scale,IRIS,52)",
  "add_ellipse_surface(HEAD,f'IrisOuterV164_{side}',ex,eye_y-.00025,.10240,.01120*iris_scale,.00870*iris_scale,IRIS,52)"),
 ("add_ellipse_surface(HEAD,f'IrisInnerV140_{side}',ex,eye_y-.00005,.10384,.00865*iris_scale,.00655*iris_scale,IRIS_INNER,48)",
  "add_ellipse_surface(HEAD,f'IrisInnerV164_{side}',ex,eye_y-.00005,.10262,.00845*iris_scale,.00635*iris_scale,IRIS_INNER,48)"),
 ("add_iris_rays_v129(HEAD,f'IrisRaysV140_{side}',ex,eye_y-.00005,.10396,.00785*iris_scale,.00590*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)",
  "add_iris_rays_v129(HEAD,f'IrisRaysV164_{side}',ex,eye_y-.00005,.10274,.00765*iris_scale,.00572*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)"),
 ("add_ellipse_surface(HEAD,f'PupilV140_{side}',ex,eye_y-.00045,.10410,.00300*iris_scale,.00375*iris_scale,PUPIL,36)",
  "add_ellipse_surface(HEAD,f'PupilV164_{side}',ex,eye_y-.00045,.10288,.00292*iris_scale,.00362*iris_scale,PUPIL,36)"),
)
for old,new in repls:
    if old not in s:
        raise SystemExit('v14.4 eye seating anchor missing: '+old[:62])
    s=s.replace(old,new,1)

# v14.3's side-facing helper still read like a small bead in 3/4. Pull it back toward the real canthus and make it a thin glint.
repls=(
 ("ex+side*eye_rx*1.185,eye_y+.0001,.1012,eye_ry*1.08,.01280,SCLERA,54",
  "ex+side*eye_rx*1.095,eye_y+.0001,.10055,eye_ry*.72,.00860,SCLERA,48"),
 ("ex+side*eye_rx*1.195,eye_y+.0002,.10215,eye_ry*.665,.00745,IRIS_INNER,46",
  "ex+side*eye_rx*1.102,eye_y+.0002,.10125,eye_ry*.43,.00465,IRIS_INNER,42"),
 ("ex+side*eye_rx*1.200,eye_y+.0001,.10255,eye_ry*.285,.00315,PUPIL,34",
  "ex+side*eye_rx*1.106,eye_y+.0001,.10152,eye_ry*.18,.00205,PUPIL,30"),
 ("ex+side*eye_rx*1.175,eye_y+eye_ry*.78,.1004","ex+side*eye_rx*1.075,eye_y+eye_ry*.66,.10015"),
 ("ex+side*eye_rx*1.190,eye_y+eye_ry*.34,.10810","ex+side*eye_rx*1.098,eye_y+eye_ry*.30,.10655"),
 ("ex+side*eye_rx*1.195,eye_y-.0001,.11030","ex+side*eye_rx*1.105,eye_y-.0001,.10835"),
 ("ex+side*eye_rx*1.175,eye_y-eye_ry*.72,.1006","ex+side*eye_rx*1.075,eye_y-eye_ry*.61,.10030"),
 ("ex+side*eye_rx*1.190,eye_y-eye_ry*.32,.10775","ex+side*eye_rx*1.098,eye_y-eye_ry*.28,.10630"),
 ("ex+side*eye_rx*1.195,eye_y-.0001,.10995","ex+side*eye_rx*1.105,eye_y-.0001,.10805"),
 ("(ex+side*eye_rx*1.08,eye_y+eye_tilt+.0032,.1043),(ex+side*eye_rx*1.18,eye_y+eye_tilt+.0057,.1086),(ex+side*eye_rx*1.27,eye_y+eye_tilt+.0044,.1130)",
  "(ex+side*eye_rx*1.04,eye_y+eye_tilt+.0030,.1033),(ex+side*eye_rx*1.11,eye_y+eye_tilt+.0050,.1068),(ex+side*eye_rx*1.18,eye_y+eye_tilt+.0040,.1100)"),
)
for old,new in repls:
    if old not in s:
        raise SystemExit('v14.4 canthus anchor missing: '+old[:58])
    s=s.replace(old,new,1)

# Slightly wider, fuller colour planes make the mouth readable without floating it off the shell.
for old,new in (
 ("add_panel(HEAD,'UpperLipV140_L',[(-.0285,-.0844,.1248),(-.0125,-.0820,.1276),(0,-.0844,.1292),(0,-.0878,.1294),(-.0110,-.0872,.1280),(-.0273,-.0888,.1253)],.00038*FACE120['surface']['lipThickness'],LIP)",
  "add_panel(HEAD,'UpperLipV164_L',[(-.0308,-.0842,.1245),(-.0135,-.0817,.1275),(0,-.0841,.1292),(0,-.0878,.1294),(-.0117,-.0871,.1280),(-.0295,-.0888,.1250)],.00044*FACE120['surface']['lipThickness'],LIP)"),
 ("add_panel(HEAD,'UpperLipV140_R',[(0,-.0844,.1292),(.0125,-.0820,.1276),(.0285,-.0844,.1248),(.0273,-.0888,.1253),(.0110,-.0872,.1280),(0,-.0878,.1294)],.00038*FACE120['surface']['lipThickness'],LIP)",
  "add_panel(HEAD,'UpperLipV164_R',[(0,-.0841,.1292),(.0135,-.0817,.1275),(.0308,-.0842,.1245),(.0295,-.0888,.1250),(.0117,-.0871,.1280),(0,-.0878,.1294)],.00044*FACE120['surface']['lipThickness'],LIP)"),
 ("add_panel(HEAD,'LowerLipV140',[(-.0272,-.0901,.1254),(0,-.0897,.1293),(.0272,-.0901,.1254),(.0228,-.0950,.1252),(0,-.0990,.1282),(-.0228,-.0950,.1252)],.00046*FACE120['surface']['lipThickness'],LIP)",
  "add_panel(HEAD,'LowerLipV164',[(-.0292,-.0901,.1251),(0,-.0896,.1293),(.0292,-.0901,.1251),(.0246,-.0952,.1249),(0,-.0988,.1284),(-.0246,-.0952,.1249)],.00054*FACE120['surface']['lipThickness'],LIP)"),
 ("add_strand(HEAD,'MouthSeamV140',[(-.0290,-.0890,.1254),(-.0130,-.0885,.1280),(0,-.0891,.1297),(.0130,-.0885,.1280),(.0290,-.0890,.1254)],.000085,FACE_DARK)",
  "add_strand(HEAD,'MouthSeamV164',[(-.0310,-.0889,.1251),(-.0138,-.0884,.1280),(0,-.0890,.1297),(.0138,-.0884,.1280),(.0310,-.0889,.1251)],.000075,FACE_DARK)"),
):
    if old not in s:
        raise SystemExit('v14.4 mouth anchor missing: '+old[:58])
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v14.3';"
new="ROOT['character_revision']='v14.4';"
if old not in s:
    raise SystemExit('v14.4 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.3';"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.4';",1)
needle="FACE_ASSET['profile_ocular_revision']='v14.3-wrapped-canthus';"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['profile_ocular_revision']='v14.4-deep-socket-canthus';",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['midface_plane_revision']='v14.4';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V164: deep socket, restrained canthus glint and stronger mid-face planes')
