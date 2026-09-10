from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V58' in s:
    print('Blender heroine generator already carries REFERENCE_V58')
    raise SystemExit(0)
if '# REFERENCE_V57' not in s:
    raise SystemExit('REFERENCE_V57 generator required before v5.8')

s=s.replace(
    '# REFERENCE_V57: expressive realistic-anime eyes, tapered lower face and filled side-swept hairline.',
    '# REFERENCE_V57: expressive realistic-anime eyes, tapered lower face and filled side-swept hairline.\n# REFERENCE_V58: reference body volume, layered rounded fringe and larger portrait eyes.',
    1,
)

# Stronger bust-to-waist contrast while keeping the same narrow shoulder envelope.
a=s.index("add_section_mesh(TORSO,'TorsoSuitV47',[")
b=s.index('# Shallow soft-tissue support',a)
torso="""add_section_mesh(TORSO,'TorsoSuitV58',[
 (-.340,waist_w*.430,waist_d*.46,waist_d*.54,-.006),
 (-.285,waist_w*.415,waist_d*.45,waist_d*.55,-.004),
 (-.220,waist_w*.455,waist_d*.45,waist_d*.58,-.001),
 (-.150,bust_w*.350,bust_d*.40,bust_d*.52,.005),
 (-.075,bust_w*.445,bust_d*.41,bust_d*.61,.015),
 (.000,bust_w*.515,bust_d*.43,bust_d*.705,.030),
 (.075,bust_w*.555,bust_d*.45,bust_d*.770,.044),
 (.135,bust_w*.540,bust_d*.45,bust_d*.735,.041),
 (.195,bust_w*.480,bust_d*.42,bust_d*.610,.026),
 (.255,bust_w*.392,bust_d*.37,bust_d*.470,.011),
 (.315,bust_w*.300,bust_d*.31,bust_d*.350,.000)
],BLACK,56)
"""
s=s[:a]+torso+s[b:]
s=s.replace(
    "add_sphere(TORSO,f'BustSoft_{side}',(side*bust_w*.205,.105,bust_d*.330),(bust_w*.205,.082,bust_d*.180),BLACK,36,22)",
    "add_sphere(TORSO,f'BustSoftV58_{side}',(side*bust_w*.215,.105,bust_d*.350),(bust_w*.235,.090,bust_d*.205),BLACK,40,24)",
    1,
)

# Larger but still horizontally almond eyes, matching the realistic-anime key art more closely.
a=s.index('# Anatomy v5.7:')
b=s.index('# Hair v5.7:',a)
face=r'''# Anatomy v5.8: larger dark portrait eyes with stronger lashes and the v5.7 tapered lower face.
face_front=.0925
eye_y=.0328
eye_x=head_w*.146
eye_rx=head_w*.138
eye_ry=.0162
eye_tilt=.0036
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV58_{side}',(ex,eye_y,.0785),(head_w*.082,.0155,.0122),SCLERA,46,28)
 add_almond_surface(HEAD,f'EyeOpeningV58_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00135,SCLERA,66,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV58_{side}',ex,eye_y,face_front+.0015,head_w*.066,.0118,IRIS,50)
 add_ellipse_surface(HEAD,f'IrisInnerV58_{side}',ex,eye_y-.0001,face_front+.0021,head_w*.041,.0077,IRIS_INNER,44)
 add_ellipse_surface(HEAD,f'PupilV58_{side}',ex,eye_y-.0001,face_front+.0028,head_w*.0160,.0045,PUPIL,34)
 add_ellipse_surface(HEAD,f'EyeLightV58A_{side}',ex-side*head_w*.0120,eye_y+.0048,face_front+.0034,head_w*.0041,.0020,SCLERA,18)
 add_ellipse_surface(HEAD,f'EyeLightV58B_{side}',ex+side*head_w*.0070,eye_y+.0017,face_front+.00345,head_w*.0017,.0009,SCLERA,14)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV58_{side}',[(inner,inner_y+.0010,face_front+.00225),(ex,eye_y+.0165,face_front+.0030),(outer,outer_y+.0010,face_front+.00235)],.00034,FACE_DARK)
 add_strand(HEAD,f'UpperLashV58_{side}',[(inner,inner_y+.0014,face_front+.0030),(ex,eye_y+.0171,face_front+.0035),(outer,outer_y+.0014,face_front+.0031)],.00052,HAIR)
 add_strand(HEAD,f'LashWingV58_{side}',[(outer,outer_y+.0014,face_front+.0031),(outer+side*head_w*.015,outer_y+.0054,face_front+.0031)],.00030,HAIR)
 add_strand(HEAD,f'LowerLidV58_{side}',[(inner+side*eye_rx*.12,inner_y-.0002,face_front+.00195),(ex,eye_y-.0097,face_front+.0023),(outer-side*eye_rx*.12,outer_y-.0002,face_front+.00195)],.00013,FACE_DARK)
 add_strand(HEAD,f'BrowV58_{side}',[(ex-side*eye_rx*.78,.0672,.1018),(ex,.0764,.1035),(ex+side*eye_rx*.98,.0640,.1022)],.00060,HAIR)

for side in(-1,1):
 add_sphere(HEAD,f'NostrilV58_{side}',(side*.0042,-.0540,.1162),(.00042,.00030,.00027),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV58',0,-.0760,.1084,.0275,.0040,.00092,LIP,54,1,0.0)
add_almond_surface(HEAD,'LowerLipV58',0,-.0835,.1093,.0268,.0046,.00102,LIP,54,1,0.0)
add_strand(HEAD,'MouthSeamV58',[(-.0235,-.0802,.1101),(0,-.0812,.1106),(.0235,-.0802,.1101)],.00013,FACE_DARK)

'''
s=s[:a]+face+s[b:]

# Replace the visor-like underlay and flat ribbons with rounded, overlapping swept locks.
a=s.index('# Hair v5.7:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.8: rounded layered fringe instead of a flat visor; crown/rear shell and smooth pony remain.
add_section_mesh(HEAD,'HairTopCapV58',[
 (.066,head_w*.448,head_d*.438,head_d*.486,-.018),
 (.100,head_w*.442,head_d*.430,head_d*.476,-.020),
 (.134,head_w*.398,head_d*.388,head_d*.432,-.021),
 (.164,head_w*.308,head_d*.298,head_d*.338,-.018),
 (.188,head_w*.184,head_d*.178,head_d*.205,-.010),
 (.203,head_w*.068,head_d*.068,head_d*.078,-.002)
],HAIR,56)
add_rear_hair_shell(HEAD,'HairRearShellV58',[
 (-.024,head_w*.288,head_d*.396,-head_d*.065),
 (.012,head_w*.416,head_d*.486,-head_d*.057),
 (.052,head_w*.490,head_d*.534,-head_d*.049),
 (.096,head_w*.512,head_d*.546,-head_d*.041),
 (.138,head_w*.474,head_d*.502,-head_d*.032),
 (.170,head_w*.380,head_d*.408,-head_d*.023),
 (.194,head_w*.222,head_d*.260,-head_d*.012),
 (.205,head_w*.076,head_d*.100,-head_d*.005)
],HAIR,44)

bangs=[
 ([(-.105,.179,.018),(-.094,.153,.054),(-.078,.124,.083),(-.058,.097,.102),(-.044,.083,.107)],[.030,.034,.031,.020,.0080],[.008,.009,.008,.005,.0028],HAIR),
 ([(-.072,.184,.016),(-.057,.156,.054),(-.032,.126,.084),(-.005,.099,.103),(.018,.084,.108)],[.034,.038,.034,.022,.0085],[.0085,.0095,.0085,.0052,.0028],HAIR),
 ([(-.030,.186,.014),(-.011,.158,.054),(.018,.128,.085),(.049,.100,.104),(.071,.082,.108)],[.034,.038,.034,.021,.0080],[.0085,.0095,.0085,.0050,.0026],HAIR_HI),
 ([(.012,.183,.014),(.034,.154,.053),(.063,.124,.083),(.090,.097,.102),(.108,.079,.106)],[.032,.036,.032,.019,.0075],[.008,.009,.008,.0048,.0025],HAIR),
 ([(.052,.176,.015),(.073,.149,.052),(.096,.120,.080),(.116,.094,.099),(.127,.077,.104)],[.026,.030,.027,.016,.0065],[.007,.008,.007,.0043,.0023],HAIR),
]
for i,(pts,widths,depths,mat) in enumerate(bangs):
 add_smooth_lock(HEAD,f'BangLockV58_{i}',pts,widths,depths,mat,10,5)
add_strand(HEAD,'BangFineV58_A',[(-.092,.171,.022),(-.054,.129,.079),(.008,.089,.107)],.000085,HAIR_HI)
add_strand(HEAD,'BangFineV58_B',[(-.028,.177,.020),(.020,.132,.080),(.090,.085,.105)],.000080,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.390,.111,-head_d*.036),(side*head_w*.418,.048,-.012),(side*head_w*.422,-.029,-.015),(side*head_w*.410,-.101,-.042),(side*head_w*.395,-.171,-.061)]
 add_smooth_lock(HEAD,f'FaceLockV58_{side}',pts,[.0085,.0108,.0090,.0052,.0022],[.0070,.0080,.0062,.0040,.0020],HAIR,10,5)

add_box(HEAD,'HairTieV58',(.014,.136,-head_d*.526),(.066,.015,.024),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(9):
 lane=(i-4)/4
 dz=lane*.034+((i%3)-1)*.010
 sway=.024*math.sin((i+1)*1.7)
 pts=[
  (lane*.020+.014,.136,-head_d*.538+dz*.20),
  (lane*.030+.018+sway*.20,.020,-head_d*.602+dz*.75),
  (lane*.044+.022+sway*.58,-.245,-.232+dz),
  (lane*.058+.027+sway,-.555,-.186+dz*1.20),
  (lane*.071+.032+sway*.72,-.890,-.143+dz*1.25),
  (lane*.082+.038+sway*.38,-1.210,-.112+dz*1.15),
  (lane*.092+.043,-1.445-(i%3)*.018,-.091+dz)
 ]
 base=.046-.006*abs(lane)
 widths=[base*.70,base,base*.96,base*.82,base*.61,base*.33,.0046]
 depths=[.023,.031,.031,.027,.020,.012,.0038]
 add_smooth_lock(PONY,f'PonyMassV58_{i}',pts,widths,depths,HAIR,10,6)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV58_{i}',[(lane*.022+.014,.134,-head_d*.543),(lane*.032+.020,-.030,-head_d*.607),(lane*.046+.026,-.345,-.214),(lane*.065+.034,-.810,-.147),(lane*.084+.045,-1.450-(i%2)*.020,-.087)],.00020+(i%2)*.00003,HAIR_HI if i in(1,3) else HAIR)

'''
s=s[:a]+hair+s[b:]

# Fuller human limb volumes while the runtime joint positions and overall narrow shoulder span stay unchanged.
s=s.replace(
    "ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.58;kn=W('knee_each')*.54;calf=W('calf_each')*.53;ank=W('ankle_each')*.48",
    "ua=W('upper_arm')*.56;fa=W('forearm')*.54;th=W('thigh_each')*.64;kn=W('knee_each')*.58;calf=W('calf_each')*.56;ank=W('ankle_each')*.49",
    1,
)
s=s.replace(
    "(UA_L,'UpperArmL',ua*.98,ua*.78,ua_d,ua_d*.82,SKIN),(UA_R,'UpperArmR',ua*.98,ua*.78,ua_d,ua_d*.82,SKIN)",
    "(UA_L,'UpperArmL',ua*1.02,ua*.80,ua_d*1.02,ua_d*.84,SKIN),(UA_R,'UpperArmR',ua*1.02,ua*.80,ua_d*1.02,ua_d*.84,SKIN)",
    1,
)
s=s.replace(
    "(TH_L,'ThighL',th*1.08,kn*.90,th_d,th_d*.78,SKIN),(TH_R,'ThighR',th*1.08,kn*.90,th_d,th_d*.78,SKIN)",
    "(TH_L,'ThighL',th*1.10,kn*.92,th_d*1.04,th_d*.80,SKIN),(TH_R,'ThighR',th*1.10,kn*.92,th_d*1.04,th_d*.80,SKIN)",
    1,
)
s=s.replace(
    "add_sphere(group,'DeltoidBlend'+name,(0,-.430,0),(ua*.94,.075,ua_d*.96),SKIN,24,16)",
    "add_sphere(group,'DeltoidBlendV58'+name,(0,-.430,0),(ua*1.08,.088,ua_d*1.06),SKIN,28,18)",
    1,
)
s=s.replace(
    "add_sphere(group,'HipThighBlend'+name,(0,-.430,0),(th*1.02,.082,th_d*.98),SKIN,26,16)",
    "add_sphere(group,'HipThighBlendV58'+name,(0,-.430,0),(th*1.08,.092,th_d*1.04),SKIN,28,18)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V58: body volume, rounded layered fringe and larger portrait eyes')
