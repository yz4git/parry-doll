from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V100' in s:
    print('Blender heroine generator already carries REFERENCE_V100')
    raise SystemExit(0)
if '# REFERENCE_V99' not in s:
    raise SystemExit('REFERENCE_V99 generator required before v10.0')

marker='# REFERENCE_V99: side-hair roots stay substantial through the ear line, then taper behind the jaw instead of opening a large bare temporal patch.'
if marker not in s:
    raise SystemExit('v10.0 REFERENCE_V99 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V100: adult portrait reset reduces oversized doll eyes and tightens the lower-face silhouette while preserving the established profile and hair.',1)

old="""# Large but adult almond eyes seated directly on the smooth shell.
face_front=.0974
eye_y=.0330
eye_x=.0478
eye_rx=.0312
eye_ry=.0123
eye_tilt=.0024
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV83_{side}',ex,eye_y,.1030,.0340,.0118,.00130,SCLERA,76,side,eye_tilt*.70)
 # v7.1: the embedded eyeball itself supplies the curved visible sclera; no flat white sticker surface.
 add_ellipse_surface(HEAD,f'IrisV83_{side}',ex,eye_y,.10445,.0118,.0097,IRIS_INNER,42)
 # v7.5 intentionally uses a single iris field; no concentric inner target ring.
 add_ellipse_surface(HEAD,f'PupilV83_{side}',ex,eye_y-.0002,.10482,.00330,.00425,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV80_{side}',ex-side*.0037,eye_y+.0035,.10505,.00108,.00088,SCLERA,18)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 add_strand(HEAD,f'UpperLashV83_{side}',[(inner,eye_y-eye_tilt+.0008,.1040),(ex,eye_y+.0125,.10465),(outer,eye_y+eye_tilt+.0008,.10405)],.00062,HAIR)
 add_strand(HEAD,f'UpperLidFoldV83_{side}',[(inner+side*.0042,eye_y-eye_tilt+.0030,.10355),(ex,eye_y+.0152,.1040),(outer-side*.0042,eye_y+eye_tilt+.0030,.10355)],.00016,FACE_DARK)
 add_strand(HEAD,f'LowerLidV83_{side}',[(inner+side*.0042,eye_y-eye_tilt-.0001,.10345),(ex,eye_y-.0088,.10375),(outer-side*.0042,eye_y+eye_tilt-.0001,.10345)],.000058,FACE_DARK)
 add_strand(HEAD,f'BrowV80_{side}',[(ex-side*.026,.0650,.1018),(ex,.0710,.1024),(ex+side*.029,.0630,.1019)],.00042,HAIR)
"""
new="""# v10.0 adult-scale almond eyes: narrower apertures, lower iris coverage and subtler lids remove the child/doll read.
face_front=.0974
eye_y=.0330
eye_x=.0465
eye_rx=.0262
eye_ry=.0099
eye_tilt=.0018
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV100_{side}',ex,eye_y,.1030,.0288,.0097,.00115,SCLERA,72,side,eye_tilt*.70)
 add_ellipse_surface(HEAD,f'IrisV100_{side}',ex,eye_y,.10430,.0094,.0078,IRIS_INNER,40)
 add_ellipse_surface(HEAD,f'PupilV100_{side}',ex,eye_y-.00015,.10466,.00285,.00345,PUPIL,30)
 add_ellipse_surface(HEAD,f'EyeLightV100_{side}',ex-side*.0030,eye_y+.0028,.10488,.00090,.00072,SCLERA,16)
 inner=ex-side*eye_rx*.96;outer=ex+side*eye_rx*1.03
 add_strand(HEAD,f'UpperLashV100_{side}',[(inner,eye_y-eye_tilt+.0006,.10395),(ex,eye_y+.0101,.10450),(outer,eye_y+eye_tilt+.0006,.10400)],.00054,HAIR)
 add_strand(HEAD,f'UpperLidFoldV100_{side}',[(inner+side*.0035,eye_y-eye_tilt+.0025,.10350),(ex,eye_y+.0124,.10392),(outer-side*.0035,eye_y+eye_tilt+.0025,.10350)],.00014,FACE_DARK)
 add_strand(HEAD,f'LowerLidV100_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0001,.10342),(ex,eye_y-.0072,.10368),(outer-side*.0035,eye_y+eye_tilt-.0001,.10342)],.000052,FACE_DARK)
 add_strand(HEAD,f'BrowV100_{side}',[(ex-side*.0235,.0645,.1018),(ex,.0698,.1023),(ex+side*.0255,.0630,.1019)],.00038,HAIR)
"""
if old not in s:
    raise SystemExit('v10.0 eye block anchor missing')
s=s.replace(old,new,1)

old_shell="width=.1285*(1.0-.345*lower+.038*cheek)"
new_shell="width=.1285*(1.0-.385*lower+.034*cheek)"
if old_shell not in s:
    raise SystemExit('v10.0 lower-face shell anchor missing')
s=s.replace(old_shell,new_shell,1)

old_patch="x=vx*.238*(1.0-.135*jaw_t)"
new_patch="x=vx*.238*(1.0-.175*jaw_t)"
if old_patch not in s:
    raise SystemExit('v10.0 CC0 lower-face taper anchor missing')
s=s.replace(old_patch,new_patch,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V100: adult-scale eyes and tighter lower-face silhouette')
