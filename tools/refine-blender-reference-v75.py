from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V75' in s:
    print('Blender heroine generator already carries REFERENCE_V75')
    raise SystemExit(0)
if '# REFERENCE_V74' not in s:
    raise SystemExit('REFERENCE_V74 generator required before v7.5')

s=s.replace(
    '# REFERENCE_V74: data-driven single profile spline, flush mouth tint and five-view consistency.',
    '# REFERENCE_V74: data-driven single profile spline, flush mouth tint and five-view consistency.\n# REFERENCE_V75: CC0-informed facial plane, absolute profile cage, single iris and flush two-volume lips.',
    1,
)

old_load="""FACE74_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v74.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE74_PATH,'r',encoding='utf-8') as f:FACE74=json.load(f)
"""
new_load="""FACE75_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-profile-v75.json')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(REF_PATH,'r',encoding='utf-8') as f:REF=json.load(f)
with open(FACE75_PATH,'r',encoding='utf-8') as f:FACE75=json.load(f)
"""
if old_load not in s:
    raise SystemExit('v7.4 face profile load block not found')
s=s.replace(old_load,new_load,1)

old_sampler="""def sample_face_profile_v74(yy):
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
"""
new_sampler="""def sample_face_profile_v75(yy):
 pts=FACE75['profile_curve']
 if yy>=pts[0]['y']:
  return pts[0]['front_z'],pts[0]['half_width']
 if yy<=pts[-1]['y']:
  return pts[-1]['front_z'],pts[-1]['half_width']
 for a,b in zip(pts,pts[1:]):
  if a['y']>=yy>=b['y']:
   t=(a['y']-yy)/max(a['y']-b['y'],1e-8)
   t=t*t*(3.0-2.0*t)
   z=a['front_z']*(1-t)+b['front_z']*t
   w=a['half_width']*(1-t)+b['half_width']*t
   return z,w
 return .097,.04
"""
if old_sampler not in s:
    raise SystemExit('v7.4 sampler not found')
s=s.replace(old_sampler,new_sampler,1)

# A human/anime face is not a pure sphere. Bring the broad front facial plane toward a shallow plate
# before orbital/cheek sculpting, while preserving the cranium and true side silhouette.
old_fm="""   if sp>0:
    fm=sp**2.0
    # Recess the eye sockets while supporting the zygomatic plane.
"""
new_fm="""   if sp>0:
    fm=sp**2.0
    # CC0-informed facial plane: distribute the front surface through neighboring vertices instead of
    # leaving the cheeks on a spherical dome. This stabilizes the same silhouette in front, 3/4 and profile.
    face_band=math.exp(-((yy+.030)/.125)**4)
    plane_lat=1.0/(1.0+(abs(x)/.095)**6)
    front_plane=depth*.985
    z+=fm*face_band*plane_lat*(front_plane-z)*.62
    # Recess the eye sockets while supporting the zygomatic plane.
"""
if old_fm not in s:
    raise SystemExit('front face fm block not found')
s=s.replace(old_fm,new_fm,1)

# Broaden the lower jaw slightly so the chin reads as an elegant V rather than an egg point.
s=s.replace("width=.132*(1.0-.365*lower+.036*cheek)","width=.132*(1.0-.320*lower+.040*cheek)",1)

old_profile="""    # v7.4: one sampled centre-line profile controls the whole forehead/nose/mouth/chin transition.
    pd,pw=sample_face_profile_v74(yy)
    z+=fm*pd*math.exp(-(x/max(pw,1e-5))**2)
"""
new_profile="""    # v7.5: absolute centre-line target plus a broad CC0-like lateral falloff.
    # Using an absolute front Z compensates the UV sphere's severe lower-face recession at the chin.
    pz,pw=sample_face_profile_v75(yy)
    lateral=1.0/(1.0+(abs(x)/max(pw,1e-5))**4)
    z+=fm*(pz-depth)*lateral
"""
if old_profile not in s:
    raise SystemExit('v7.4 profile application block not found')
s=s.replace(old_profile,new_profile,1)

# Expose the whole almond aperture. One warm gray-brown iris is easier to read than concentric target rings.
s=s.replace(
    "add_almond_lens(HEAD,f'EyeScleraV74_{side}',ex,eye_y,.0972,.0315,.0120,.0052,SCLERA,8,64,side,eye_tilt*.66)",
    "add_almond_lens(HEAD,f'EyeScleraV75_{side}',ex,eye_y,.1032,.0320,.0118,.0042,SCLERA,8,64,side,eye_tilt*.66)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisV74_{side}',(ex,eye_y,.1028),(.0102,.0091,.00155),IRIS_INNER,44,26)",
    "add_sphere(HEAD,f'IrisV75_{side}',(ex,eye_y,.1080),(.0110,.0096,.00145),IRIS_INNER,44,26)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisInnerV74_{side}',(ex,eye_y-.0001,.1035),(.0061,.0057,.00130),IRIS,38,22)",
    "# v7.5 intentionally uses a single iris field; no concentric inner target ring.",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'PupilV74_{side}',(ex,eye_y-.0001,.1042),(.00255,.0030,.00105),PUPIL,30,20)",
    "add_sphere(HEAD,f'PupilV75_{side}',(ex,eye_y-.0001,.1091),(.00245,.00315,.00100),PUPIL,30,20)",
    1,
)
s=s.replace("ex-side*.0032,eye_y+.0040,.1047,.00115,.00095","ex-side*.0035,eye_y+.0041,.1097,.00115,.00095",1)

old_lash=""" add_strand(HEAD,f'UpperLashV74_{side}',[(inner,eye_y-eye_tilt+.0010,.1030),(ex,eye_y+.0131,.1040),(outer,eye_y+eye_tilt+.0010,.1031)],.00072,HAIR)
 add_strand(HEAD,f'LowerLidV74_{side}',[(inner+side*.0038,eye_y-eye_tilt-.0002,.1016),(ex,eye_y-.0090,.1020),(outer-side*.0038,eye_y+eye_tilt-.0002,.1016)],.000090,FACE_DARK)
 add_strand(HEAD,f'BrowV74_{side}',[(ex-side*.025,.064,.1000),(ex,.071,.1016),(ex+side*.029,.061,.1004)],.00058,HAIR)
"""
new_lash=""" add_strand(HEAD,f'UpperLashV75_{side}',[(inner,eye_y-eye_tilt+.0010,.1070),(ex,eye_y+.0130,.1082),(outer,eye_y+eye_tilt+.0010,.1071)],.00076,HAIR)
 add_strand(HEAD,f'UpperLidFoldV75_{side}',[(inner+side*.004,eye_y-eye_tilt+.0030,.1058),(ex,eye_y+.0150,.1065),(outer-side*.004,eye_y+eye_tilt+.0030,.1058)],.00018,FACE_DARK)
 add_strand(HEAD,f'LowerLidV75_{side}',[(inner+side*.0040,eye_y-eye_tilt-.0002,.1052),(ex,eye_y-.0090,.1057),(outer-side*.0040,eye_y+eye_tilt-.0002,.1052)],.000085,FACE_DARK)
 add_strand(HEAD,f'BrowV75_{side}',[(ex-side*.025,.064,.1010),(ex,.071,.1020),(ex+side*.029,.061,.1012)],.00058,HAIR)
"""
if old_lash not in s:
    raise SystemExit('v7.4 eyelid block not found')
s=s.replace(old_lash,new_lash,1)

# Two almost-flush colour surfaces follow the actual upper/lower lip depths instead of drawing one flat stripe.
old_mouth="""add_almond_surface(HEAD,'LipTintV74',0,-.0850,.0962,.0250,.0062,.00028,LIP,72,1,0.0)
add_strand(HEAD,'MouthSeamV74',[(-.0210,-.0842,.0968),(0,-.0850,.0972),(.0210,-.0842,.0968)],.000065,FACE_DARK)
"""
new_mouth="""add_almond_surface(HEAD,'UpperLipTintV75',0,-.0800,.1091,.0215,.0042,.00014,LIP,72,1,0.0)
add_almond_surface(HEAD,'LowerLipTintV75',0,-.0900,.1111,.0222,.0046,.00014,LIP,72,1,0.0)
add_strand(HEAD,'MouthSeamV75',[(-.0205,-.0850,.1100),(0,-.0854,.1104),(.0205,-.0850,.1100)],.000060,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV75_{side}',side*.0056,-.0570,.1157,.00155,.00058,FACE_DARK,16)
"""
if old_mouth not in s:
    raise SystemExit('v7.4 lip block not found')
s=s.replace(old_mouth,new_mouth,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V75: absolute CC0 face cage, facial plane, single iris and two-volume lips')
