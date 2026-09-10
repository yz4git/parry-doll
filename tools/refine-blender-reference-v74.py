from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V74' in s:
    print('Blender heroine generator already carries REFERENCE_V74')
    raise SystemExit(0)
if '# REFERENCE_V73' not in s:
    raise SystemExit('REFERENCE_V73 generator required before v7.4')

s=s.replace(
    '# REFERENCE_V73: CC0-topology-informed continuous profile depth and fully exposed almond eye aperture.',
    '# REFERENCE_V73: CC0-topology-informed continuous profile depth and fully exposed almond eye aperture.\n# REFERENCE_V74: data-driven single profile spline, flush mouth tint and five-view consistency.',
    1,
)

# Load explicit multiview profile data generated from the PARRY DOLL face sheets and CC0 topology study.
old_load="""REF_PATH=os.path.join(ROOT_DIR,'tools','heroine-reference-proportions.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
"""
new_load="""REF_PATH=os.path.join(ROOT_DIR,'tools','heroine-reference-proportions.json')
FACE74_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v74.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE74_PATH,'r',encoding='utf-8') as f:FACE74=json.load(f)
"""
if old_load not in s:
    raise SystemExit('reference load block not found')
s=s.replace(old_load,new_load,1)

# A monotone smooth interpolation prevents overlapping Gaussian peaks from creating a 3/4-only muzzle.
anchor="""def add_anime_head_v60(p,name,mat,segments=96,rings=48):
"""
helper="""def sample_face_profile_v74(yy):
 pts=FACE74['profile_curve']
 if yy>=pts[0]['y']:
  return pts[0]['depth_offset'],pts[0]['half_width']
 if yy<=pts[-1]['y']:
  return pts[-1]['depth_offset'],pts[-1]['half_width']
 for a,b in zip(pts,pts[1:]):
  if a['y']>=yy>=b['y']:
   t=(a['y']-yy)/max(a['y']-b['y'],1e-8)
   t=t*t*(3.0-2.0*t)
   d=a['depth_offset']*(1-t)+b['depth_offset']*t
   w=a['half_width']*(1-t)+b['half_width']*t
   return d,w
 return 0.0,.03

def add_anime_head_v60(p,name,mat,segments=96,rings=48):
"""
if anchor not in s:
    raise SystemExit('anime head anchor not found')
s=s.replace(anchor,helper,1)

old_profile="""    # CC0-informed continuous facial depth field: glabella -> dorsum -> tip -> philtrum -> lips -> chin.
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
new_profile="""    # v7.4: one sampled centre-line profile controls the whole forehead/nose/mouth/chin transition.
    pd,pw=sample_face_profile_v74(yy)
    z+=fm*pd*math.exp(-(x/max(pw,1e-5))**2)
"""
if old_profile not in s:
    raise SystemExit('v7.3 profile block not found')
s=s.replace(old_profile,new_profile,1)

# Reveal a touch more almond sclera and avoid target-like concentric rings.
s=s.replace(
    "add_almond_lens(HEAD,f'EyeScleraV73_{side}',ex,eye_y,.0950,.0305,.0116,.0065,SCLERA,8,64,side,eye_tilt*.62)",
    "add_almond_lens(HEAD,f'EyeScleraV74_{side}',ex,eye_y,.0972,.0315,.0120,.0052,SCLERA,8,64,side,eye_tilt*.66)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisV73_{side}',(ex,eye_y,.1018),(.0106,.0095,.00165),IRIS,44,26)",
    "add_sphere(HEAD,f'IrisV74_{side}',(ex,eye_y,.1028),(.0102,.0091,.00155),IRIS_INNER,44,26)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisInnerV73_{side}',(ex,eye_y-.0001,.1027),(.0074,.0069,.00142),IRIS_INNER,40,24)",
    "add_sphere(HEAD,f'IrisInnerV74_{side}',(ex,eye_y-.0001,.1035),(.0061,.0057,.00130),IRIS,38,22)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'PupilV73_{side}',(ex,eye_y-.0001,.1035),(.0028,.0033,.00112),PUPIL,30,20)",
    "add_sphere(HEAD,f'PupilV74_{side}',(ex,eye_y-.0001,.1042),(.00255,.0030,.00105),PUPIL,30,20)",
    1,
)
s=s.replace("ex-side*.0034,eye_y+.0042,.1040,.0012,.0010","ex-side*.0032,eye_y+.0040,.1047,.00115,.00095",1)

old_lash=""" add_strand(HEAD,f'UpperLashV73_{side}',[(inner,eye_y-eye_tilt+.0010,.1020),(ex,eye_y+.0128,.1032),(outer,eye_y+eye_tilt+.0010,.1021)],.00070,HAIR)
 add_strand(HEAD,f'LowerLidV73_{side}',[(inner+side*.0038,eye_y-eye_tilt-.0002,.1001),(ex,eye_y-.0088,.1007),(outer-side*.0038,eye_y+eye_tilt-.0002,.1001)],.000095,FACE_DARK)
 add_strand(HEAD,f'BrowV73_{side}',[(ex-side*.025,.064,.1000),(ex,.071,.1016),(ex+side*.029,.061,.1004)],.00060,HAIR)
"""
new_lash=""" add_strand(HEAD,f'UpperLashV74_{side}',[(inner,eye_y-eye_tilt+.0010,.1030),(ex,eye_y+.0131,.1040),(outer,eye_y+eye_tilt+.0010,.1031)],.00072,HAIR)
 add_strand(HEAD,f'LowerLidV74_{side}',[(inner+side*.0038,eye_y-eye_tilt-.0002,.1016),(ex,eye_y-.0090,.1020),(outer-side*.0038,eye_y+eye_tilt-.0002,.1016)],.000090,FACE_DARK)
 add_strand(HEAD,f'BrowV74_{side}',[(ex-side*.025,.064,.1000),(ex,.071,.1016),(ex+side*.029,.061,.1004)],.00058,HAIR)
"""
if old_lash not in s:
    raise SystemExit('v7.3 lash block not found')
s=s.replace(old_lash,new_lash,1)

# The v7.3 tint was too far in front of the actual mouth plane. Put it almost flush with the integrated surface.
s=s.replace(
    "add_almond_surface(HEAD,'LipTintV73',0,-.0850,.1080,.0235,.0064,.00042,LIP,68,1,0.0)",
    "add_almond_surface(HEAD,'LipTintV74',0,-.0850,.0962,.0250,.0062,.00028,LIP,72,1,0.0)",
    1,
)
s=s.replace(
    "add_strand(HEAD,'MouthSeamV73',[(-.0200,-.0842,.1086),(0,-.0850,.1091),(.0200,-.0842,.1086)],.000070,FACE_DARK)",
    "add_strand(HEAD,'MouthSeamV74',[(-.0210,-.0842,.0968),(0,-.0850,.0972),(.0210,-.0842,.0968)],.000065,FACE_DARK)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V74: data-driven single face profile and flush portrait features')
