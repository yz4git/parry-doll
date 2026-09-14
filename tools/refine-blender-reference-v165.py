from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V165' in s and face.get('revision')=='v14.5':
    print('Blender heroine generator already carries REFERENCE_V165 / v14.5')
    raise SystemExit(0)
if '# REFERENCE_V164' not in s:
    raise SystemExit('REFERENCE_V164 generator required before v14.5')

marker="# REFERENCE_V164: v14.4 seats the real eye deeper, turns the side helper into a restrained canthus glint, and strengthens orbital, nasal, malar and mouth planes for a less mannequin-like close portrait."
if marker not in s:
    raise SystemExit('v14.5 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V165: v14.5 rebuilds portrait readability around a larger but deeper-set almond aperture, clearer alar/nostril anatomy and fuller integrated lips while keeping the compact v14 jaw and single wrapped profile eye.",1)

face['revision']='v14.5'
face['reference_intent']='adult realistic-anime heroine; larger almond aperture seated deeper in a real orbit; narrow readable nose root/alar base; fuller cupid upper lip and rounded lower lip; compact soft jaw retained; no detached profile-eye geometry'
face['surface_strength']['orbit_recess']=0.00875
face['surface_strength']['brow_support']=0.00335
face['surface_strength']['malar_projection']=0.00690
face['surface_strength']['buccal_hollow']=0.00320
face['surface_strength']['alar_projection']=0.00265
face['surface_strength']['philtrum_recess']=0.00245
face['surface_strength']['upper_lip']=0.00475
face['surface_strength']['lower_lip']=0.00545
face['surface_strength']['mouth_corner']=0.00186
face['surface_strength']['labiomental_recess']=0.00218
face['surface_strength']['chin_pad']=0.00380
face['eye_target']['aperture_rx']=0.03025
face['eye_target']['aperture_ry']=0.00958
face['eye_target']['iris_scale_multiplier']=0.855
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# Strengthen three-quarter anatomy without widening the silhouette.
old="     z+=fm*.00170*infra"
new="     z+=fm*.00192*infra"
if old not in s: raise SystemExit('v14.5 infraorbital anchor missing')
s=s.replace(old,new,1)
old="     sidewall=math.exp(-((x-side*.0108)/.0135)**2-((yy+.018)/.0410)**2)\n     z+=fm*.00115*sidewall"
new="     sidewall=math.exp(-((x-side*.0108)/.0132)**2-((yy+.018)/.0400)**2)\n     z+=fm*.00155*sidewall\n     alar_shelf=math.exp(-((x-side*.0105)/.0090)**2-((yy+.0585)/.0090)**2)\n     z+=fm*.00072*alar_shelf"
if old not in s: raise SystemExit('v14.5 nose sidewall anchor missing')
s=s.replace(old,new,1)

# Pull the real eyeball stack farther into the socket while allowing a larger almond opening.
repls=(
 ("add_sphere(HEAD,f'EyeScleraGlobeV164_{side}',(ex,eye_y,.0926),(eye_rx*.80,eye_ry*.82,.00945),SCLERA,34,22)",
  "add_sphere(HEAD,f'EyeScleraGlobeV165_{side}',(ex,eye_y,.0917),(eye_rx*.79,eye_ry*.81,.00895),SCLERA,36,24)"),
 ("add_sphere(HEAD,f'EyeIrisVolumeV164_{side}',(ex,eye_y-.00010,.09825),(eye_rx*.270,eye_ry*.430,.00420),IRIS,28,18)",
  "add_sphere(HEAD,f'EyeIrisVolumeV165_{side}',(ex,eye_y-.00010,.09750),(eye_rx*.258,eye_ry*.412,.00385),IRIS,30,20)"),
 ("add_sphere(HEAD,f'EyePupilVolumeV164_{side}',(ex,eye_y-.00025,.09960),(eye_rx*.098,eye_ry*.208,.00300),PUPIL,24,16)",
  "add_sphere(HEAD,f'EyePupilVolumeV165_{side}',(ex,eye_y-.00025,.09882),(eye_rx*.094,eye_ry*.198,.00270),PUPIL,24,16)"),
 ("add_almond_surface(HEAD,f'EyeScleraV164_{side}',ex,eye_y,.10120,eye_rx,eye_ry,.00102,SCLERA,96,side,eye_tilt*.74)",
  "add_almond_surface(HEAD,f'EyeScleraV165_{side}',ex,eye_y,.10028,eye_rx,eye_ry,.00092,SCLERA,112,side,eye_tilt*.72)"),
 ("add_ellipse_surface(HEAD,f'IrisOuterV164_{side}',ex,eye_y-.00025,.10240,.01120*iris_scale,.00870*iris_scale,IRIS,52)",
  "add_ellipse_surface(HEAD,f'IrisOuterV165_{side}',ex,eye_y-.00025,.10142,.01120*iris_scale,.00865*iris_scale,IRIS,56)"),
 ("add_ellipse_surface(HEAD,f'IrisInnerV164_{side}',ex,eye_y-.00005,.10262,.00845*iris_scale,.00635*iris_scale,IRIS_INNER,48)",
  "add_ellipse_surface(HEAD,f'IrisInnerV165_{side}',ex,eye_y-.00005,.10165,.00840*iris_scale,.00628*iris_scale,IRIS_INNER,52)"),
 ("add_iris_rays_v129(HEAD,f'IrisRaysV164_{side}',ex,eye_y-.00005,.10274,.00765*iris_scale,.00572*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)",
  "add_iris_rays_v129(HEAD,f'IrisRaysV165_{side}',ex,eye_y-.00005,.10178,.00755*iris_scale,.00562*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),26)"),
 ("add_ellipse_surface(HEAD,f'PupilV164_{side}',ex,eye_y-.00045,.10288,.00292*iris_scale,.00362*iris_scale,PUPIL,36)",
  "add_ellipse_surface(HEAD,f'PupilV165_{side}',ex,eye_y-.00045,.10192,.00288*iris_scale,.00352*iris_scale,PUPIL,38)"),
)
for old,new in repls:
    if old not in s: raise SystemExit('v14.5 eye anchor missing: '+old[:70])
    s=s.replace(old,new,1)

# Bring front eyelid/lash graphics back toward the deeper aperture so the eye no longer looks pasted on.
for old,new in (
 (".10402),(ex-side*.0030,eye_y+.01055,.10482),(outer+side*.0012,eye_y+eye_tilt+.00045,.10413)",
  ".10310),(ex-side*.0030,eye_y+.01055,.10378),(outer+side*.0012,eye_y+eye_tilt+.00045,.10322)"),
 (".10417),(outer+side*.0058,eye_y+eye_tilt+.0052,.10422),(outer+side*.0108,eye_y+eye_tilt+.0037,.10408)",
  ".10325),(outer+side*.0058,eye_y+eye_tilt+.0052,.10330),(outer+side*.0108,eye_y+eye_tilt+.0037,.10318)"),
 (".10374),(ex,eye_y-.00770,.10403),(outer-side*.0024,eye_y+eye_tilt-.00015,.10383)",
  ".10292),(ex,eye_y-.00770,.10318),(outer-side*.0024,eye_y+eye_tilt-.00015,.10302)"),
):
    if old not in s: raise SystemExit('v14.5 lid seating anchor missing')
    s=s.replace(old,new,1)

# Fuller, warmer lips with a slightly deeper seam. Geometry still follows the unified head shell.
old="LIP=material('Lip',(0.285,0.105,0.125),0,.42)"
new="LIP=material('Lip',(0.335,0.125,0.145),0,.39)"
if old not in s: raise SystemExit('v14.5 lip material anchor missing')
s=s.replace(old,new,1)
for old,new in (
 ("add_panel(HEAD,'UpperLipV164_L',[(-.0308,-.0842,.1245),(-.0135,-.0817,.1275),(0,-.0841,.1292),(0,-.0878,.1294),(-.0117,-.0871,.1280),(-.0295,-.0888,.1250)],.00044*FACE120['surface']['lipThickness'],LIP)",
  "add_panel(HEAD,'UpperLipV165_L',[(-.0315,-.0840,.1244),(-.0138,-.0812,.1278),(0,-.0837,.1295),(0,-.0882,.1297),(-.0120,-.0875,.1282),(-.0302,-.0890,.1249)],.00062*FACE120['surface']['lipThickness'],LIP)"),
 ("add_panel(HEAD,'UpperLipV164_R',[(0,-.0841,.1292),(.0135,-.0817,.1275),(.0308,-.0842,.1245),(.0295,-.0888,.1250),(.0117,-.0871,.1280),(0,-.0878,.1294)],.00044*FACE120['surface']['lipThickness'],LIP)",
  "add_panel(HEAD,'UpperLipV165_R',[(0,-.0837,.1295),(.0138,-.0812,.1278),(.0315,-.0840,.1244),(.0302,-.0890,.1249),(.0120,-.0875,.1282),(0,-.0882,.1297)],.00062*FACE120['surface']['lipThickness'],LIP)"),
 ("add_panel(HEAD,'LowerLipV164',[(-.0292,-.0901,.1251),(0,-.0896,.1293),(.0292,-.0901,.1251),(.0246,-.0952,.1249),(0,-.0988,.1284),(-.0246,-.0952,.1249)],.00054*FACE120['surface']['lipThickness'],LIP)",
  "add_panel(HEAD,'LowerLipV165',[(-.0300,-.0903,.1249),(0,-.0896,.1295),(.0300,-.0903,.1249),(.0251,-.0960,.1247),(0,-.1000,.1287),(-.0251,-.0960,.1247)],.00074*FACE120['surface']['lipThickness'],LIP)"),
 ("add_strand(HEAD,'MouthSeamV164',[(-.0310,-.0889,.1251),(-.0138,-.0884,.1280),(0,-.0890,.1297),(.0138,-.0884,.1280),(.0310,-.0889,.1251)],.000075,FACE_DARK)",
  "add_strand(HEAD,'MouthSeamV165',[(-.0315,-.0891,.1249),(-.0140,-.0887,.1281),(0,-.0893,.1298),(.0140,-.0887,.1281),(.0315,-.0891,.1249)],.000105,FACE_DARK)"),
 ("add_ellipse_surface(HEAD,f'NostrilTintV140_{side}',side*.0059,-.0615,.1267,.00162*FACE120['surface']['nostrilScale'],.00064*FACE120['surface']['nostrilScale'],FACE_DARK,20)",
  "add_ellipse_surface(HEAD,f'NostrilTintV165_{side}',side*.0066,-.0610,.1270,.00212*FACE120['surface']['nostrilScale'],.00082*FACE120['surface']['nostrilScale'],FACE_DARK,24)"),
):
    if old not in s: raise SystemExit('v14.5 mouth/nose anchor missing: '+old[:70])
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v14.4';"
new="ROOT['character_revision']='v14.5';"
if old not in s: raise SystemExit('v14.5 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.4';"
if needle in s: s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.5';",1)
needle="FACE_ASSET['profile_ocular_revision']='v14.4-deep-socket-canthus';"
if needle in s: s=s.replace(needle,"FACE_ASSET['profile_ocular_revision']='v14.5-deeper-almond-canthus';",1)
needle="FACE_ASSET['midface_plane_revision']='v14.4';"
if needle in s: s=s.replace(needle,"FACE_ASSET['midface_plane_revision']='v14.5';",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V165: larger deeper-set almond eye, clearer nose base and fuller integrated lips')
