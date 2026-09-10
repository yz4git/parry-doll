from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V73' in s:
    print('Blender heroine generator already carries REFERENCE_V73')
    raise SystemExit(0)
if '# REFERENCE_V72' not in s:
    raise SystemExit('REFERENCE_V72 generator required before v7.3')

s=s.replace(
    '# REFERENCE_V72: smooth 3D almond sclera lens, stronger integrated S-profile and three-quarter-safe portrait proportions.',
    '# REFERENCE_V72: smooth 3D almond sclera lens, stronger integrated S-profile and three-quarter-safe portrait proportions.\n# REFERENCE_V73: CC0-topology-informed continuous profile depth and fully exposed almond eye aperture.',
    1,
)

# CC0 MakeHuman/MPFB topology study: distribute projection over the complete facial S-curve.
# Keep every major volume in the single UV head surface. The profile must remain visible in true side view,
# not only at three-quarter angles.
old_profile="""    # Multiview landmark profile: explicit but continuous forehead -> nose -> lips -> chin S-curve.
    z+=fm*.0065*math.exp(-(x/.020)**2-((yy+.004)/.060)**2)   # glabella / bridge
    z+=fm*.0090*math.exp(-(x/.016)**2-((yy+.025)/.034)**2)   # narrow dorsum
    z+=fm*.0180*math.exp(-(x/.017)**2-((yy+.045)/.018)**2)   # small projected tip
    z+=fm*.0070*math.exp(-(x/.012)**2-((yy+.058)/.014)**2)   # columella
    z-=fm*.0028*math.exp(-(x/.018)**2-((yy+.068)/.012)**2)   # philtrum break
    z+=fm*.0100*math.exp(-(x/.034)**2-((yy+.080)/.012)**2)   # upper lip volume
    z+=fm*.0110*math.exp(-(x/.036)**2-((yy+.090)/.013)**2)   # lower lip volume
    z-=fm*.0040*math.exp(-(x/.032)**2-((yy+.104)/.013)**2)   # labiomental crease
    z+=fm*.0240*math.exp(-(x/.040)**2-((yy+.122)/.025)**2)   # chin support
"""
new_profile="""    # CC0-informed continuous facial depth field: glabella -> dorsum -> tip -> philtrum -> lips -> chin.
    z+=fm*.0075*math.exp(-(x/.022)**2-((yy+.003)/.062)**2)   # glabella / root support
    z+=fm*.0135*math.exp(-(x/.018)**2-((yy+.026)/.038)**2)   # dorsum, spread vertically
    z+=fm*.0270*math.exp(-(x/.019)**2-((yy+.046)/.020)**2)   # readable but narrow tip
    z+=fm*.0100*math.exp(-(x/.014)**2-((yy+.059)/.014)**2)   # columella
    z-=fm*.0052*math.exp(-(x/.020)**2-((yy+.069)/.011)**2)   # subnasal / philtrum setback
    z+=fm*.0125*math.exp(-(x/.035)**2-((yy+.080)/.012)**2)   # upper lip
    z+=fm*.0145*math.exp(-(x/.038)**2-((yy+.091)/.013)**2)   # lower lip
    z-=fm*.0063*math.exp(-(x/.034)**2-((yy+.105)/.013)**2)   # labiomental crease
    z+=fm*.0220*math.exp(-(x/.043)**2-((yy+.124)/.024)**2)   # compact chin support
"""
if old_profile not in s:
    raise SystemExit('v7.2 profile block not found')
s=s.replace(old_profile,new_profile,1)

# Slightly stronger lower-face taper keeps the added profile depth feminine rather than muzzle-like.
s=s.replace("width=.132*(1.0-.335*lower+.034*cheek)","width=.132*(1.0-.365*lower+.036*cheek)",1)

# Expose the entire almond aperture. In v7.2 the perimeter sat behind the orbital surface,
# so only the circular centre survived the depth test.
s=s.replace(
    "add_almond_lens(HEAD,f'EyeScleraV72_{side}',ex,eye_y,.0920,.0280,.0106,.0072,SCLERA,7,56,side,eye_tilt*.55)",
    "add_almond_lens(HEAD,f'EyeScleraV73_{side}',ex,eye_y,.0950,.0305,.0116,.0065,SCLERA,8,64,side,eye_tilt*.62)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisV72_{side}',(ex,eye_y,.0998),(.0092,.0088,.00155),IRIS,40,24)",
    "add_sphere(HEAD,f'IrisV73_{side}',(ex,eye_y,.1018),(.0106,.0095,.00165),IRIS,44,26)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisInnerV72_{side}',(ex,eye_y-.0001,.1006),(.0067,.0064,.00135),IRIS_INNER,36,22)",
    "add_sphere(HEAD,f'IrisInnerV73_{side}',(ex,eye_y-.0001,.1027),(.0074,.0069,.00142),IRIS_INNER,40,24)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'PupilV72_{side}',(ex,eye_y-.0001,.1013),(.0025,.0030,.00110),PUPIL,28,18)",
    "add_sphere(HEAD,f'PupilV73_{side}',(ex,eye_y-.0001,.1035),(.0028,.0033,.00112),PUPIL,30,20)",
    1,
)
s=s.replace("ex-side*.0031,eye_y+.0038,.1019,.0011,.0009","ex-side*.0034,eye_y+.0042,.1040,.0012,.0010",1)

old_lash=""" add_strand(HEAD,f'UpperLashV72_{side}',[(inner,eye_y-eye_tilt+.0010,.1000),(ex,eye_y+.0119,.1010),(outer,eye_y+eye_tilt+.0010,.1001)],.00062,HAIR)
 add_strand(HEAD,f'LowerLidV72_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0003,.0988),(ex,eye_y-.0081,.0992),(outer-side*.0035,eye_y+eye_tilt-.0003,.0988)],.00010,FACE_DARK)
 add_strand(HEAD,f'BrowV72_{side}',[(ex-side*.025,.064,.0995),(ex,.071,.1010),(ex+side*.029,.061,.1000)],.00062,HAIR)
"""
new_lash=""" add_strand(HEAD,f'UpperLashV73_{side}',[(inner,eye_y-eye_tilt+.0010,.1020),(ex,eye_y+.0128,.1032),(outer,eye_y+eye_tilt+.0010,.1021)],.00070,HAIR)
 add_strand(HEAD,f'LowerLidV73_{side}',[(inner+side*.0038,eye_y-eye_tilt-.0002,.1001),(ex,eye_y-.0088,.1007),(outer-side*.0038,eye_y+eye_tilt-.0002,.1001)],.000095,FACE_DARK)
 add_strand(HEAD,f'BrowV73_{side}',[(ex-side*.025,.064,.1000),(ex,.071,.1016),(ex+side*.029,.061,.1004)],.00060,HAIR)
"""
if old_lash not in s:
    raise SystemExit('v7.2 lash block not found')
s=s.replace(old_lash,new_lash,1)

# Move lip tint/seam onto the more projected integrated mouth surface.
s=s.replace(
    "add_almond_surface(HEAD,'LipTintV72',0,-.0845,.1017,.0228,.0060,.00045,LIP,64,1,0.0)",
    "add_almond_surface(HEAD,'LipTintV73',0,-.0850,.1080,.0235,.0064,.00042,LIP,68,1,0.0)",
    1,
)
s=s.replace(
    "add_strand(HEAD,'MouthSeamV72',[(-.0195,-.0837,.1023),(0,-.0845,.1027),(.0195,-.0837,.1023)],.000075,FACE_DARK)",
    "add_strand(HEAD,'MouthSeamV73',[(-.0200,-.0842,.1086),(0,-.0850,.1091),(.0200,-.0842,.1086)],.000070,FACE_DARK)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V73: CC0-informed continuous profile depth and exposed almond aperture')
