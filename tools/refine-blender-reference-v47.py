from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V47' in s:
    print('Blender heroine generator already carries REFERENCE_V47')
    raise SystemExit(0)
if '# REFERENCE_V46' not in s:
    raise SystemExit('REFERENCE_V46 generator required before v4.7')

s=s.replace(
    '# REFERENCE_V46: cinematic almond eyes, readable nasal bridge and fuller natural mouth.',
    '# REFERENCE_V46: cinematic almond eyes, readable nasal bridge and fuller natural mouth.\n# REFERENCE_V47: reference-silhouette face, softer hourglass torso and fuller layered hair.',
    1,
)

# Softer portrait materials: still pale, but less porcelain-flat under the bright model-viewer sky.
s=s.replace("SKIN=material('Skin',(0.57,0.39,0.37),0,.60)", "SKIN=material('Skin',(0.54,0.36,0.34),0,.68)", 1)
s=s.replace("IRIS=material('Iris',(0.18,0.105,0.080),.02,.28)", "IRIS=material('Iris',(0.25,0.135,0.090),.02,.31)", 1)
s=s.replace("LIP=material('Lip',(0.34,0.16,0.17),0,.56)", "LIP=material('Lip',(0.42,0.18,0.18),0,.60)", 1)

# The v4.6 screenshot still read as a narrow black tube. Keep the tiny waist while restoring a
# continuous bust/ribcage curve and a softer taper into the neck.
old_torso="""add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.49,waist_d*.49,waist_d*.54,-.006),
 (-.285,waist_w*.47,waist_d*.47,waist_d*.54,-.004),
 (-.220,waist_w*.49,waist_d*.46,waist_d*.55,-.001),
 (-.150,bust_w*.37,bust_d*.40,bust_d*.47,.004),
 (-.075,bust_w*.43,bust_d*.41,bust_d*.54,.011),
 (.000,bust_w*.48,bust_d*.42,bust_d*.62,.021),
 (.075,bust_w*.515,bust_d*.44,bust_d*.675,.030),
 (.135,bust_w*.505,bust_d*.44,bust_d*.655,.030),
 (.195,bust_w*.465,bust_d*.42,bust_d*.57,.022),
 (.255,bust_w*.405,bust_d*.39,bust_d*.48,.012),
 (.315,bust_w*.340,bust_d*.34,bust_d*.385,.002)
],BLACK,48)"""
new_torso="""add_section_mesh(TORSO,'TorsoSuitV47',[
 (-.340,waist_w*.455,waist_d*.47,waist_d*.54,-.006),
 (-.285,waist_w*.440,waist_d*.46,waist_d*.55,-.004),
 (-.220,waist_w*.470,waist_d*.45,waist_d*.58,-.001),
 (-.150,bust_w*.355,bust_d*.40,bust_d*.51,.005),
 (-.075,bust_w*.430,bust_d*.41,bust_d*.59,.014),
 (.000,bust_w*.490,bust_d*.43,bust_d*.675,.027),
 (.075,bust_w*.525,bust_d*.45,bust_d*.735,.039),
 (.135,bust_w*.515,bust_d*.45,bust_d*.705,.037),
 (.195,bust_w*.455,bust_d*.42,bust_d*.585,.023),
 (.255,bust_w*.375,bust_d*.37,bust_d*.455,.010),
 (.315,bust_w*.300,bust_d*.31,bust_d*.350,.000)
],BLACK,56)"""
if old_torso not in s: raise SystemExit('v4.6 torso block not found')
s=s.replace(old_torso,new_torso,1)
s=s.replace("(side*bust_w*.365,.238,.002),(bust_w*.108,.061,bust_d*.142)", "(side*bust_w*.335,.238,.002),(bust_w*.096,.060,bust_d*.136)", 1)

# Slightly fuller pelvis and upper legs: long-legged remains the priority, but the reference is not stick-thin.
old_pelvis="""add_section_mesh(PELVIS,'PelvisSuit',[
 (-.180,pelvis_w*.42,pelvis_d*.60,pelvis_d*.48,-.018),
 (-.080,pelvis_w*.50,pelvis_d*.58,pelvis_d*.52,-.012),
 (.040,pelvis_w*.49,pelvis_d*.52,pelvis_d*.51,-.005),
 (.155,waist_w*.57,waist_d*.56,waist_d*.59,0.000)
],BLACK,36)"""
new_pelvis="""add_section_mesh(PELVIS,'PelvisSuitV47',[
 (-.180,pelvis_w*.445,pelvis_d*.62,pelvis_d*.51,-.018),
 (-.080,pelvis_w*.525,pelvis_d*.60,pelvis_d*.56,-.011),
 (.040,pelvis_w*.510,pelvis_d*.54,pelvis_d*.55,-.004),
 (.155,waist_w*.545,waist_d*.55,waist_d*.60,0.000)
],BLACK,44)"""
if old_pelvis not in s: raise SystemExit('v4.6 pelvis block not found')
s=s.replace(old_pelvis,new_pelvis,1)
s=s.replace("ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.50;kn=W('knee_each')*.50;calf=W('calf_each')*.50;ank=W('ankle_each')*.50",
            "ua=W('upper_arm')*.50;fa=W('forearm')*.50;th=W('thigh_each')*.58;kn=W('knee_each')*.54;calf=W('calf_each')*.53;ank=W('ankle_each')*.48",1)

# Less mask-like head envelope: a slightly broader jaw transition and cheek platform, while the chin stays delicate.
old_head="""add_portrait_head_v44(HEAD,'HeadShellV44',[
 (-.148,head_w*.050,head_d*.145,head_d*.188,.052),
 (-.137,head_w*.105,head_d*.190,head_d*.238,.047),
 (-.123,head_w*.190,head_d*.248,head_d*.302,.038),
 (-.105,head_w*.270,head_d*.302,head_d*.360,.028),
 (-.083,head_w*.335,head_d*.350,head_d*.414,.018),
 (-.058,head_w*.382,head_d*.390,head_d*.454,.009),
 (-.030,head_w*.414,head_d*.420,head_d*.480,.002),
 (.000,head_w*.434,head_d*.438,head_d*.492,-.003),
 (.030,head_w*.444,head_d*.450,head_d*.494,-.007),
 (.060,head_w*.438,head_d*.458,head_d*.480,-.011),
 (.090,head_w*.414,head_d*.456,head_d*.446,-.016),
 (.117,head_w*.372,head_d*.444,head_d*.400,-.022),
 (.140,head_w*.312,head_d*.420,head_d*.344,-.027),
 (.158,head_w*.225,head_d*.390,head_d*.282,-.030)
],SKIN,96)"""
new_head="""add_portrait_head_v44(HEAD,'HeadShellV47',[
 (-.143,head_w*.066,head_d*.150,head_d*.194,.049),
 (-.133,head_w*.135,head_d*.198,head_d*.248,.044),
 (-.119,head_w*.225,head_d*.258,head_d*.313,.035),
 (-.101,head_w*.305,head_d*.313,head_d*.372,.025),
 (-.080,head_w*.362,head_d*.360,head_d*.425,.015),
 (-.056,head_w*.401,head_d*.399,head_d*.463,.006),
 (-.030,head_w*.426,head_d*.427,head_d*.486,-.001),
 (.000,head_w*.442,head_d*.444,head_d*.498,-.006),
 (.030,head_w*.450,head_d*.456,head_d*.500,-.010),
 (.060,head_w*.444,head_d*.463,head_d*.486,-.014),
 (.090,head_w*.422,head_d*.459,head_d*.451,-.019),
 (.117,head_w*.381,head_d*.447,head_d*.405,-.024),
 (.141,head_w*.320,head_d*.423,head_d*.349,-.029),
 (.160,head_w*.236,head_d*.392,head_d*.286,-.032)
],SKIN,96)"""
if old_head not in s: raise SystemExit('v4.6 head block not found')
s=s.replace(old_head,new_head,1)
# Stronger cheek planes with less hollow eye sockets make the face read more like the reference close-up.
s=s.replace("z+=fm*.0145*math.exp(-((x-cheek_x)/(head_w*.105))**2-((yy+.010)/.040)**2)",
            "z+=fm*.0180*math.exp(-((x-cheek_x)/(head_w*.110))**2-((yy+.010)/.043)**2)",1)
s=s.replace("z-=fm*.0205*math.exp(-((x-eye_x)/(head_w*.118))**2-((yy-.031)/.025)**2)",
            "z-=fm*.0165*math.exp(-((x-eye_x)/(head_w*.124))**2-((yy-.030)/.027)**2)",1)

# Rebuild face features at the larger anime-realistic proportions visible in the reference portrait.
a=s.index('# Anatomy v4.6:')
b=s.index('# Hair v4.5:',a)
face="""# Anatomy v4.7: larger expressive almond eyes, softer nose and fuller mouth.
face_front=head_d*.520
eye_y=.0305
eye_x=head_w*.145
eye_rx=head_w*.126
eye_ry=.0158
eye_tilt=.0040
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV47_{side}',(ex,eye_y,head_d*.420),(head_w*.094,.0200,head_d*.068),SCLERA,44,26)
 add_almond_surface(HEAD,f'EyeOpeningV47_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0030,SCLERA,52,side,eye_tilt)
 add_sphere(HEAD,f'IrisV47_{side}',(ex,eye_y+.0001,face_front+.0065),(head_w*.0610,.0138,.0035),IRIS,40,24)
 add_sphere(HEAD,f'PupilV47_{side}',(ex,eye_y,face_front+.0095),(head_w*.0130,.0062,.0020),PUPIL,26,16)
 add_sphere(HEAD,f'EyeLightV47A_{side}',(ex-side*head_w*.0120,eye_y+.0062,face_front+.0115),(head_w*.0060,.0029,.0012),SCLERA,14,8)
 add_sphere(HEAD,f'EyeLightV47B_{side}',(ex+side*head_w*.0090,eye_y+.0017,face_front+.0117),(head_w*.0024,.0014,.0008),SCLERA,10,6)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV47_{side}',[(inner,inner_y+.0012,face_front+.0040),(ex,eye_y+.0163,face_front+.0067),(outer,outer_y+.0013,face_front+.0040)],.00068,FACE_DARK)
 add_strand(HEAD,f'LowerLidV47_{side}',[(inner,inner_y-.0002,face_front+.0029),(ex,eye_y-.0090,face_front+.0037),(outer,outer_y-.0003,face_front+.0029)],.00033,SKIN)
 add_strand(HEAD,f'UpperLashV47_{side}',[(inner,inner_y+.0020,face_front+.0068),(ex,eye_y+.0168,face_front+.0087),(outer,outer_y+.0022,face_front+.0069)],.00078,HAIR)
 add_strand(HEAD,f'LashWingV47_{side}',[(outer,outer_y+.0022,face_front+.0070),(outer+side*head_w*.018,outer_y+.0072,face_front+.0075)],.00054,HAIR)
 add_strand(HEAD,f'BrowV47_{side}',[(ex-side*eye_rx*.78,.0710,head_d*.516),(ex,.0820,head_d*.520),(ex+side*eye_rx*.98,.0690,head_d*.516)],.00100,HAIR)

add_sphere(HEAD,'NoseBridgeV47',(0,-.0060,head_d*.542),(.0068,.041,.0067),SKIN,30,18)
add_sphere(HEAD,'NoseTipV47',(0,-.0445,head_d*.556),(.0098,.0087,.0063),SKIN,30,18)
add_sphere(HEAD,'ColumellaV47',(0,-.0530,head_d*.551),(.0028,.0043,.0028),SKIN,18,10)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV47_{side}',(side*.0097,-.0500,head_d*.548),(.0046,.0043,.0034),SKIN,20,12)
 add_sphere(HEAD,f'NostrilV47_{side}',(side*.0068,-.0520,head_d*.553),(.00120,.00085,.00075),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV47',0,-.0795,head_d*.554,.0390,.0060,.0022,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV47',0,-.0885,head_d*.553,.0365,.0069,.0026,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV47',[(-.0330,-.0840,head_d*.556),(0,-.0855,head_d*.557),(.0330,-.0840,head_d*.556)],.00031,FACE_DARK)

"""
s=s[:a]+face+s[b:]

# Hair v4.7: broader overlapping fringe + a full nine-lock ponytail. Keep all geometry local to HEAD.
a=s.index('# Hair v4.5:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v4.7: soft layered fringe and a high-volume ponytail matching the reference silhouette.
add_sphere(HEAD,'HairBackV47',(0,.034,-head_d*.370),(head_w*.525,.136,head_d*.470),HAIR,60,38)
add_sphere(HEAD,'HairCrownV47',(-.018,.122,-head_d*.205),(head_w*.488,.064,head_d*.338),HAIR,56,34)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV47_{side}',(side*head_w*.414,.018,-.025),(head_w*.092,.082,head_d*.145),HAIR,34,22)

fringe=[
 (-.132,-.110,-.074,-.050,.050,.156,.060,.022),
 (-.105,-.079,-.040,-.012,.064,.161,.062,.023),
 (-.075,-.043,-.004,.026,.075,.165,.062,.023),
 (-.042,-.004,.034,.065,.079,.166,.061,.023),
 (-.006,.032,.072,.100,.073,.162,.058,.022),
 (.030,.068,.106,.128,.060,.157,.053,.020),
 (.063,.099,.126,.142,.043,.149,.047,.018),
]
for i,(rx,mx,cx,tx,ty,ry,w,tipw) in enumerate(fringe):
 pts=[(rx,ry,-head_d*.020),(mx,ry-.018,head_d*.160),(cx,.114,head_d*.360),(tx,ty,head_d*.523)]
 add_lock_mesh(HEAD,f'ForeheadLockV47_{i}',pts,[w*.70,w,w*.82,tipw],[.0090,.0105,.0082,.0044],HAIR_HI if i in(0,6) else HAIR,12)

for i,(rx,mx,tx,ty) in enumerate(((-.115,-.072,-.018,.071),(-.072,-.022,.046,.077),(-.020,.035,.106,.060))):
 pts=[(rx,.151,head_d*.004),(mx,.127,head_d*.268),((mx+tx)*.5,.102,head_d*.432),(tx,ty,head_d*.524)]
 add_lock_mesh(HEAD,f'FringeLayerV47_{i}',pts,[.031,.035,.027,.013],[.0060,.0068,.0052,.0031],HAIR_HI if i==2 else HAIR,10)

for side in(-1,1):
 pts=[(side*head_w*.347,.095,-.012),(side*head_w*.403,.024,head_d*.075),(side*head_w*.423,-.105,head_d*.055),(side*head_w*.400,-.255,.020),(side*head_w*.365,-.390,-.025)]
 add_lock_mesh(HEAD,f'FaceLockV47_{side}',pts,[.026,.030,.026,.018,.008],[.0060,.0062,.0052,.0040,.0025],HAIR,10)
 add_strand(HEAD,f'FaceWispV47_{side}',[(side*head_w*.390,.080,-.004),(side*head_w*.433,-.040,head_d*.035),(side*head_w*.420,-.220,.000),(side*head_w*.388,-.430,-.035)],.00048,HAIR_HI)

add_sphere(HEAD,'PonyRootV47',(.028,.157,-head_d*.438),(.100,.071,.086),HAIR,40,28)
add_box(HEAD,'HairTieV47',(.030,.151,-head_d*.495),(.098,.024,.038),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(9):
 lane=(i-4)/4
 zoff=((i%3)-1)*.014-.010*abs(lane)
 endx=.110+lane*.190
 pts=[
  (lane*.040+.028,.154,-head_d*.525+zoff),
  (lane*.060+.045,.040,-head_d*.770+zoff),
  (lane*.092+.070,-.235,-.595+zoff*.45),
  (lane*.125+.090,-.585,-.500),
  (lane*.150+.105,-.970,-.405),
  (endx,-1.330,-.305),
  (endx+lane*.035,-1.650-(i%3)*.024,-.205)
 ]
 base_w=.112-.026*abs(lane)
 add_lock_mesh(PONY,f'PonyLockV47_{i}',pts,[base_w*.78,base_w,base_w*1.08,base_w,base_w*.80,base_w*.48,.010],[.021,.024,.024,.021,.017,.011,.0045],HAIR_HI if i in(1,4,7) else HAIR,12)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyFlyV47_{i}',[(lane*.030+.028,.150,-head_d*.525),(lane*.055+.050,-.060,-head_d*.790),(lane*.100+.075,-.430,-.565),(lane*.155+.100,-.900,-.405),(lane*.205+.130,-1.650-(i%2)*.035,-.190)],.00058+(i%2)*.00008,HAIR_HI if i%2==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V47: reference silhouette face, hourglass torso and fuller layered hair')
