from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V83' in s:
    print('Blender heroine generator already carries REFERENCE_V83')
    raise SystemExit(0)
if '# REFERENCE_V82' not in s:
    raise SystemExit('REFERENCE_V82 generator required before v8.3')

s=s.replace(
    '# REFERENCE_V82: artifact-free cheeks, no detached side strands and a front-visible overlapping crown seal.',
    '# REFERENCE_V82: artifact-free cheeks, no detached side strands and a front-visible overlapping crown seal.\n# REFERENCE_V83: +10% mature almond aperture, lower side-swept fringe and clean temple silhouette.',
    1,
)

# Restore the measured reference eye opening by about ten percent while preserving v8.0's
# shallow, face-hugging construction. The increase is in aperture only, not forward bulge.
for old,new in [
    ('eye_rx=.0284','eye_rx=.0312'),
    ('eye_ry=.0112','eye_ry=.0123'),
    ("add_almond_surface(HEAD,f'EyeScleraV80_{side}',ex,eye_y,.1030,.0310,.0108,.00130,SCLERA,72,side,eye_tilt*.70)",
     "add_almond_surface(HEAD,f'EyeScleraV83_{side}',ex,eye_y,.1030,.0340,.0118,.00130,SCLERA,76,side,eye_tilt*.70)"),
    ("add_ellipse_surface(HEAD,f'IrisV80_{side}',ex,eye_y,.10445,.0108,.0090,IRIS_INNER,40)",
     "add_ellipse_surface(HEAD,f'IrisV83_{side}',ex,eye_y,.10445,.0118,.0097,IRIS_INNER,42)"),
    ("add_ellipse_surface(HEAD,f'PupilV80_{side}',ex,eye_y-.0002,.10482,.00315,.00405,PUPIL,32)",
     "add_ellipse_surface(HEAD,f'PupilV83_{side}',ex,eye_y-.0002,.10482,.00330,.00425,PUPIL,32)"),
    ("add_strand(HEAD,f'UpperLashV80_{side}',[(inner,eye_y-eye_tilt+.0008,.1040),(ex,eye_y+.0114,.10465),(outer,eye_y+eye_tilt+.0008,.10405)],.00058,HAIR)",
     "add_strand(HEAD,f'UpperLashV83_{side}',[(inner,eye_y-eye_tilt+.0008,.1040),(ex,eye_y+.0125,.10465),(outer,eye_y+eye_tilt+.0008,.10405)],.00062,HAIR)"),
    ("add_strand(HEAD,f'UpperLidFoldV80_{side}',[(inner+side*.0040,eye_y-eye_tilt+.0028,.10355),(ex,eye_y+.0140,.1040),(outer-side*.0040,eye_y+eye_tilt+.0028,.10355)],.00015,FACE_DARK)",
     "add_strand(HEAD,f'UpperLidFoldV83_{side}',[(inner+side*.0042,eye_y-eye_tilt+.0030,.10355),(ex,eye_y+.0152,.1040),(outer-side*.0042,eye_y+eye_tilt+.0030,.10355)],.00016,FACE_DARK)"),
    ("add_strand(HEAD,f'LowerLidV80_{side}',[(inner+side*.0040,eye_y-eye_tilt-.0001,.10345),(ex,eye_y-.0080,.10375),(outer-side*.0040,eye_y+eye_tilt-.0001,.10345)],.000055,FACE_DARK)",
     "add_strand(HEAD,f'LowerLidV83_{side}',[(inner+side*.0042,eye_y-eye_tilt-.0001,.10345),(ex,eye_y-.0088,.10375),(outer-side*.0042,eye_y+eye_tilt-.0001,.10345)],.000058,FACE_DARK)"),
]:
    if old not in s:
        raise SystemExit(f'v8.3 eye anchor missing: {old[:72]}')
    s=s.replace(old,new,1)

# Bring the main fringe down over the upper forehead and push its exit toward the heroine's right.
# Rounded spline masses keep the v8.x volumetric read while removing the receding/bald forehead impression.
hair_repls=[
("add_smooth_lock(HEAD,'FringeMassV80_A',[(-.090,.190,.030),(-.075,.177,.055),(-.048,.160,.078),(-.010,.145,.095),(.034,.134,.101),(.076,.126,.098)],[.048,.052,.049,.039,.026,.010],[.018,.019,.017,.013,.009,.004],HAIR,14,6)",
 "add_smooth_lock(HEAD,'FringeMassV83_A',[(-.098,.190,.030),(-.084,.173,.056),(-.060,.151,.080),(-.026,.127,.099),(.018,.108,.106),(.066,.094,.107)],[.054,.058,.054,.043,.028,.010],[.019,.020,.018,.014,.009,.004],HAIR,14,6)"),
("add_smooth_lock(HEAD,'FringeMassV80_B',[(-.035,.194,.026),(-.016,.181,.052),(.014,.165,.076),(.050,.150,.094),(.086,.138,.099),(.112,.130,.096)],[.041,.043,.039,.030,.019,.008],[.016,.017,.015,.011,.007,.003],HAIR,14,6)",
 "add_smooth_lock(HEAD,'FringeMassV83_B',[(-.040,.194,.026),(-.020,.178,.053),(.010,.156,.078),(.048,.132,.098),(.086,.111,.105),(.118,.098,.104)],[.046,.048,.043,.033,.021,.008],[.017,.018,.016,.012,.007,.003],HAIR,14,6)"),
("add_smooth_lock(HEAD,'FringeAccentV80',[(-.112,.184,.024),(-.092,.169,.050),(-.064,.153,.074),(-.028,.140,.090),(.012,.132,.098)],[.025,.027,.024,.018,.007],[.010,.010,.009,.006,.003],HAIR_HI,12,5)",
 "add_smooth_lock(HEAD,'FringeAccentV83',[(-.116,.185,.025),(-.098,.166,.052),(-.072,.145,.077),(-.038,.124,.096),(.002,.110,.104)],[.028,.030,.027,.020,.007],[.011,.011,.010,.007,.003],HAIR_HI,12,5)"),
]
for old,new in hair_repls:
    if old not in s:
        raise SystemExit(f'v8.3 fringe anchor missing: {old[:60]}')
    s=s.replace(old,new,1)

# The old temple locks were useful before the rear shell became full, but their front edge now reads
# as a detached black stroke in true profile. Remove them completely; the v5.9 shell plus v8.3 fringe
# already close the temple silhouette from every audit view.
old_temple="""for side in(-1,1):
 pts=[(side*head_w*.394,.112,-head_d*.038),(side*head_w*.423,.050,-.013),(side*head_w*.428,-.028,-.016),(side*head_w*.416,-.103,-.044),(side*head_w*.401,-.178,-.064)]
 add_smooth_lock(HEAD,f'FaceLockV59_{side}',pts,[.010,.013,.0105,.0060,.0026],[.008,.009,.007,.0045,.0022],HAIR,10,5)

"""
new_temple="""# v8.3: no isolated front temple locks; the rear shell/fringe own this silhouette continuously.

"""
if old_temple not in s:
    raise SystemExit('v8.3 temple-lock anchor missing')
s=s.replace(old_temple,new_temple,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V83: larger mature almond aperture, lower side sweep, clean profile temples')
