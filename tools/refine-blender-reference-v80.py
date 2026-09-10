from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V80' in s:
    print('Blender heroine generator already carries REFERENCE_V80')
    raise SystemExit(0)
if '# REFERENCE_V79' not in s:
    raise SystemExit('REFERENCE_V79 generator required before v8.0')

s=s.replace(
    '# REFERENCE_V79: embedded eyes, stronger adult nose bridge, integrated lips and an open asymmetric fringe.',
    '# REFERENCE_V79: embedded eyes, stronger adult nose bridge, integrated lips and an open asymmetric fringe.\n# REFERENCE_V80: mature flush almond eyes, softened centre profile and rounded side-swept hair masses.',
    1,
)

# v7.9 proved the centre-line profile is visible, but the extra tip impulse is too sharp in profile.
s=s.replace("z+=.0034*bridge_lat*math.exp(-((yy+.006)/.050)**2)",
            "z+=.0024*bridge_lat*math.exp(-((yy+.006)/.052)**2)",1)
s=s.replace("z+=.0048*tip_lat*math.exp(-((yy+.045)/.0175)**2)",
            "z+=.0022*tip_lat*math.exp(-((yy+.045)/.0195)**2)",1)

# Mature gaze: reduce the sclera aperture substantially and make every visible eye layer a shallow,
# face-hugging surface. This removes the spherical/contact-lens read in three-quarter/profile views.
for old,new in [
    ('eye_x=.0498','eye_x=.0478'),
    ('eye_rx=.0318','eye_rx=.0284'),
    ('eye_ry=.0128','eye_ry=.0112'),
    ("add_almond_lens(HEAD,f'EyeScleraV79_{side}',ex,eye_y,.1022,.0392,.0129,.00265,SCLERA,8,80,side,eye_tilt*.72)",
     "add_almond_surface(HEAD,f'EyeScleraV80_{side}',ex,eye_y,.1030,.0310,.0108,.00130,SCLERA,72,side,eye_tilt*.70)"),
    ("add_sphere(HEAD,f'IrisV79_{side}',(ex,eye_y,.1050),(.0134,.0102,.00118),IRIS_INNER,52,30)",
     "add_ellipse_surface(HEAD,f'IrisV80_{side}',ex,eye_y,.10445,.0108,.0090,IRIS_INNER,40)"),
    ("add_sphere(HEAD,f'PupilV79_{side}',(ex,eye_y-.0002,.1061),(.00270,.00325,.00078),PUPIL,32,22)",
     "add_ellipse_surface(HEAD,f'PupilV80_{side}',ex,eye_y-.0002,.10482,.00315,.00405,PUPIL,32)"),
    ("add_ellipse_surface(HEAD,f'EyeLightV79_{side}',ex-side*.0043,eye_y+.0040,.1068,.00118,.00094,SCLERA,18)",
     "add_ellipse_surface(HEAD,f'EyeLightV80_{side}',ex-side*.0037,eye_y+.0035,.10505,.00108,.00088,SCLERA,18)"),
    ("add_strand(HEAD,f'UpperLashV79_{side}',[(inner,eye_y-eye_tilt+.0010,.1045),(ex,eye_y+.0138,.1057),(outer,eye_y+eye_tilt+.0010,.1046)],.00082,HAIR)",
     "add_strand(HEAD,f'UpperLashV80_{side}',[(inner,eye_y-eye_tilt+.0008,.1040),(ex,eye_y+.0114,.10465),(outer,eye_y+eye_tilt+.0008,.10405)],.00058,HAIR)"),
    ("add_strand(HEAD,f'UpperLidFoldV79_{side}',[(inner+side*.0042,eye_y-eye_tilt+.0032,.1039),(ex,eye_y+.0160,.1047),(outer-side*.0042,eye_y+eye_tilt+.0032,.1039)],.00019,FACE_DARK)",
     "add_strand(HEAD,f'UpperLidFoldV80_{side}',[(inner+side*.0040,eye_y-eye_tilt+.0028,.10355),(ex,eye_y+.0140,.1040),(outer-side*.0040,eye_y+eye_tilt+.0028,.10355)],.00015,FACE_DARK)"),
    ("add_strand(HEAD,f'LowerLidV79_{side}',[(inner+side*.0042,eye_y-eye_tilt-.0002,.1036),(ex,eye_y-.0095,.1041),(outer-side*.0042,eye_y+eye_tilt-.0002,.1036)],.000070,FACE_DARK)",
     "add_strand(HEAD,f'LowerLidV80_{side}',[(inner+side*.0040,eye_y-eye_tilt-.0001,.10345),(ex,eye_y-.0080,.10375),(outer-side*.0040,eye_y+eye_tilt-.0001,.10345)],.000055,FACE_DARK)"),
    ("add_strand(HEAD,f'BrowV78_{side}',[(ex-side*.028,.0655,.1014),(ex,.0725,.1024),(ex+side*.032,.0625,.1016)],.00052,HAIR)",
     "add_strand(HEAD,f'BrowV80_{side}',[(ex-side*.026,.0650,.1018),(ex,.0710,.1024),(ex+side*.029,.0630,.1019)],.00042,HAIR)"),
]:
    if old not in s:
        raise SystemExit(f'v8.0 eye anchor missing: {old[:70]}')
    s=s.replace(old,new,1)

# Lip colour should follow the face rather than read as stacked plates. Reduce width/depth and keep
# a soft Cupid bow; the underlying quad surface provides the actual silhouette.
old_lips="""add_panel(HEAD,'UpperLipV79_L',[(-.0255,-.0850,.1098),(-.0125,-.0798,.1105),(0,-.0829,.1112),(0,-.0870,.1114),(-.0108,-.0860,.1110),(-.0238,-.0883,.1102)],.00050,LIP)
add_panel(HEAD,'UpperLipV79_R',[(0,-.0829,.1112),(.0125,-.0798,.1105),(.0255,-.0850,.1098),(.0238,-.0883,.1102),(.0108,-.0860,.1110),(0,-.0870,.1114)],.00050,LIP)
add_panel(HEAD,'LowerLipV79',[(-.0238,-.0884,.1105),(0,-.0875,.1115),(.0238,-.0884,.1105),(.0202,-.0952,.1104),(0,-.0983,.1109),(-.0202,-.0952,.1104)],.00054,LIP)
add_strand(HEAD,'MouthSeamV79',[(-.0242,-.0868,.1103),(-.0112,-.0862,.1110),(0,-.0871,.1116),(.0112,-.0862,.1110),(.0242,-.0868,.1103)],.000045,FACE_DARK)
"""
new_lips="""add_panel(HEAD,'UpperLipV80_L',[(-.0225,-.0848,.1095),(-.0110,-.0802,.1101),(0,-.0833,.1107),(0,-.0867,.1108),(-.0095,-.0859,.1105),(-.0210,-.0880,.1099)],.00030,LIP)
add_panel(HEAD,'UpperLipV80_R',[(0,-.0833,.1107),(.0110,-.0802,.1101),(.0225,-.0848,.1095),(.0210,-.0880,.1099),(.0095,-.0859,.1105),(0,-.0867,.1108)],.00030,LIP)
add_panel(HEAD,'LowerLipV80',[(-.0210,-.0882,.1100),(0,-.0876,.1108),(.0210,-.0882,.1100),(.0178,-.0942,.1099),(0,-.0969,.1103),(-.0178,-.0942,.1099)],.00034,LIP)
add_strand(HEAD,'MouthSeamV80',[(-.0215,-.0867,.1099),(-.0100,-.0862,.1105),(0,-.0870,.1109),(.0100,-.0862,.1105),(.0215,-.0867,.1099)],.000038,FACE_DARK)
"""
if old_lips not in s: raise SystemExit('v8.0 lip block missing')
s=s.replace(old_lips,new_lips,1)

# Remove every wide flat forehead ribbon from v7.8/7.9. Replace them with rounded overlapping locks
# that follow the scalp and sweep to the right temple, leaving the central forehead and eye line open.
old_hair="""# v7.8 swept root closes the seam without reading as a horizontal visor across the forehead.
add_flow_ribbon(HEAD,'HairlineRootV78',[(-.038,.196,.048),(-.030,.184,.069),(-.014,.169,.087),(.010,.152,.101),(.036,.136,.108)],[.060,.092,.118,.112,.082],.00092,HAIR)
add_flow_ribbon(HEAD,'HairlineRootHiV78',[(-.070,.188,.046),(-.056,.173,.069),(-.034,.156,.088),(-.006,.142,.101)],[.034,.050,.058,.044],.00052,HAIR_HI)

# Two wide dark planes establish a natural side-swept fringe instead of repeated finger-like locks.
add_flow_ribbon(HEAD,'FringeSweepV79_A',[(-.112,.182,.012),(-.095,.161,.045),(-.062,.139,.074),(-.018,.120,.095),(.030,.105,.105),(.078,.096,.108)],[.072,.074,.065,.050,.033,.018],.00130,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV79_B',[(-.048,.184,.012),(-.022,.163,.047),(.018,.142,.077),(.061,.121,.098),(.096,.106,.106),(.121,.098,.108)],[.058,.060,.052,.039,.026,.014],.00126,HAIR)
# Short overlapping strips break the broad masses without covering the eyes.
add_flow_ribbon(HEAD,'FringeLayerV79_C',[(-.083,.177,.014),(-.056,.156,.049),(-.020,.137,.078),(.020,.119,.099),(.060,.108,.106)],[.030,.031,.027,.019,.009],.00102,HAIR_HI)
add_flow_ribbon(HEAD,'FringeLayerV79_D',[(-.014,.179,.013),(.014,.157,.049),(.052,.138,.079),(.087,.119,.100),(.112,.106,.106)],[.026,.028,.024,.017,.008],.00100,HAIR)
"""
new_hair="""# v8.0 rounded scalp-following fringe. Broad geometry lives above the forehead, not as flat face cards.
add_smooth_lock(HEAD,'FringeMassV80_A',[(-.090,.190,.030),(-.075,.177,.055),(-.048,.160,.078),(-.010,.145,.095),(.034,.134,.101),(.076,.126,.098)],[.048,.052,.049,.039,.026,.010],[.018,.019,.017,.013,.009,.004],HAIR,14,6)
add_smooth_lock(HEAD,'FringeMassV80_B',[(-.035,.194,.026),(-.016,.181,.052),(.014,.165,.076),(.050,.150,.094),(.086,.138,.099),(.112,.130,.096)],[.041,.043,.039,.030,.019,.008],[.016,.017,.015,.011,.007,.003],HAIR,14,6)
add_smooth_lock(HEAD,'FringeAccentV80',[(-.112,.184,.024),(-.092,.169,.050),(-.064,.153,.074),(-.028,.140,.090),(.012,.132,.098)],[.025,.027,.024,.018,.007],[.010,.010,.009,.006,.003],HAIR_HI,12,5)
"""
if old_hair not in s: raise SystemExit('v8.0 broad fringe block missing')
s=s.replace(old_hair,new_hair,1)

# Re-route the hairline micro-strands so none crosses the centre of the eyes/forehead.
for old,new in [
("add_strand(HEAD,'FringeFineV59_A',[(-.096,.173,.018),(-.057,.137,.074),(.012,.092,.109)],.000085,HAIR_HI)",
 "add_strand(HEAD,'FringeFineV80_A',[(-.098,.177,.028),(-.058,.155,.076),(.030,.132,.101)],.000070,HAIR_HI)"),
("add_strand(HEAD,'FringeFineV59_B',[(-.036,.176,.018),(.014,.135,.077),(.091,.087,.108)],.000080,HAIR_HI)",
 "add_strand(HEAD,'FringeFineV80_B',[(-.040,.181,.027),(.018,.158,.077),(.098,.133,.099)],.000066,HAIR_HI)"),
("add_strand(HEAD,'FringeFineV63_C',[(-.116,.170,.017),(-.085,.142,.061),(-.032,.105,.101)],.000070,HAIR_HI)",
 "add_strand(HEAD,'FringeFineV80_C',[(-.116,.176,.026),(-.082,.158,.062),(-.012,.137,.095)],.000060,HAIR_HI)"),
("add_strand(HEAD,'FringeFineV63_D',[(-.068,.181,.016),(-.026,.143,.063),(.038,.096,.106)],.000072,HAIR_HI)",
 "add_strand(HEAD,'FringeFineV80_D',[(-.070,.184,.025),(-.024,.162,.065),(.058,.137,.098)],.000060,HAIR_HI)"),
("add_strand(HEAD,'FringeFineV63_E',[(-.005,.180,.016),(.034,.143,.064),(.095,.087,.107)],.000068,HAIR_HI)",
 "add_strand(HEAD,'FringeFineV80_E',[(-.008,.184,.025),(.038,.163,.066),(.108,.136,.097)],.000058,HAIR_HI)"),
]:
    if old not in s: raise SystemExit(f'v8.0 fine fringe anchor missing: {old[:52]}')
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V80: flush mature gaze, softer profile, integrated lips, rounded side sweep')
