from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V48' in s:
    print('Blender heroine generator already carries REFERENCE_V48')
    raise SystemExit(0)
if '# REFERENCE_V47' not in s:
    raise SystemExit('REFERENCE_V47 generator required before v4.8')

s=s.replace(
    '# REFERENCE_V47: reference-silhouette face, softer hourglass torso and fuller layered hair.',
    '# REFERENCE_V47: reference-silhouette face, softer hourglass torso and fuller layered hair.\n# REFERENCE_V48: unified hair cap, sheet fringe, iris-dominant eyes and rebuilt side-profile depth.',
    1,
)

# The v4.7 profile still read as a flat mask. Strengthen the features in the continuous head shell
# instead of stacking more visible primitive pieces on top of the face.
s=s.replace("z+=fm*.0180*math.exp(-(x/(head_w*.060))**2-((yy+.005)/.058)**2)",
            "z+=fm*.0250*math.exp(-(x/(head_w*.064))**2-((yy+.005)/.060)**2)",1)
s=s.replace("z+=fm*.0410*math.exp(-(x/(head_w*.070))**2-((yy+.043)/.023)**2)",
            "z+=fm*.0540*math.exp(-(x/(head_w*.074))**2-((yy+.043)/.024)**2)",1)
s=s.replace("z+=fm*.0065*math.exp(-(x/(head_w*.150))**2-((yy+.082)/.024)**2)",
            "z+=fm*.0110*math.exp(-(x/(head_w*.155))**2-((yy+.082)/.025)**2)",1)
s=s.replace("z+=fm*.0105*math.exp(-(x/(head_w*.120))**2-((yy+.124)/.020)**2)",
            "z+=fm*.0140*math.exp(-(x/(head_w*.120))**2-((yy+.120)/.021)**2)",1)

# Shorten the lower face a little and preserve a small chin while giving the jaw enough width to
# stop the long porcelain-egg silhouette visible in the v4.7 front capture.
old_head="""add_portrait_head_v44(HEAD,'HeadShellV47',[
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
new_head="""add_portrait_head_v44(HEAD,'HeadShellV48',[
 (-.136,head_w*.072,head_d*.154,head_d*.214,.047),
 (-.127,head_w*.148,head_d*.203,head_d*.270,.041),
 (-.113,head_w*.242,head_d*.263,head_d*.332,.032),
 (-.096,head_w*.322,head_d*.318,head_d*.388,.022),
 (-.076,head_w*.378,head_d*.364,head_d*.437,.012),
 (-.053,head_w*.414,head_d*.402,head_d*.472,.004),
 (-.028,head_w*.438,head_d*.430,head_d*.493,-.003),
 (.000,head_w*.452,head_d*.447,head_d*.503,-.008),
 (.030,head_w*.457,head_d*.458,head_d*.503,-.012),
 (.060,head_w*.449,head_d*.464,head_d*.488,-.016),
 (.090,head_w*.426,head_d*.460,head_d*.453,-.021),
 (.117,head_w*.384,head_d*.448,head_d*.407,-.026),
 (.141,head_w*.322,head_d*.424,head_d*.351,-.031),
 (.160,head_w*.236,head_d*.393,head_d*.287,-.034)
],SKIN,96)"""
if old_head not in s: raise SystemExit('v4.7 head block not found')
s=s.replace(old_head,new_head,1)

# Eyes: dark iris dominates the opening as in the reference close-up. Reduce exposed sclera height,
# keep a soft upward outer corner and use a much larger iris with a visible warm ring.
a=s.index('# Anatomy v4.7:')
b=s.index('# Hair v4.7:',a)
face="""# Anatomy v4.8: iris-dominant soft eyes and a readable continuous profile.
face_front=head_d*.525
eye_y=.0300
eye_x=head_w*.145
eye_rx=head_w*.124
eye_ry=.0128
eye_tilt=.0035
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV48_{side}',(ex,eye_y,head_d*.424),(head_w*.092,.0180,head_d*.068),SCLERA,44,26)
 add_almond_surface(HEAD,f'EyeOpeningV48_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0025,SCLERA,52,side,eye_tilt)
 # Iris fills roughly two thirds of the visible eye width; pupil is large enough to read as a soft dark eye.
 add_sphere(HEAD,f'IrisV48_{side}',(ex,eye_y,face_front+.0060),(head_w*.0830,.0116,.0034),IRIS,44,26)
 add_sphere(HEAD,f'PupilV48_{side}',(ex,eye_y-.0002,face_front+.0090),(head_w*.0390,.0071,.0020),PUPIL,30,18)
 add_sphere(HEAD,f'EyeLightV48A_{side}',(ex-side*head_w*.0170,eye_y+.0050,face_front+.0112),(head_w*.0065,.0027,.0011),SCLERA,14,8)
 add_sphere(HEAD,f'EyeLightV48B_{side}',(ex+side*head_w*.0110,eye_y+.0016,face_front+.0114),(head_w*.0024,.0013,.0008),SCLERA,10,6)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV48_{side}',[(inner,inner_y+.0010,face_front+.0038),(ex,eye_y+.0134,face_front+.0064),(outer,outer_y+.0011,face_front+.0038)],.00062,FACE_DARK)
 add_strand(HEAD,f'UpperLashV48_{side}',[(inner,inner_y+.0017,face_front+.0065),(ex,eye_y+.0140,face_front+.0082),(outer,outer_y+.0019,face_front+.0066)],.00072,HAIR)
 add_strand(HEAD,f'LashWingV48_{side}',[(outer,outer_y+.0019,face_front+.0067),(outer+side*head_w*.017,outer_y+.0062,face_front+.0071)],.00049,HAIR)
 add_strand(HEAD,f'BrowV48_{side}',[(ex-side*eye_rx*.78,.0695,head_d*.520),(ex,.0795,head_d*.524),(ex+side*eye_rx*.98,.0675,head_d*.520)],.00093,HAIR)

# Only tiny finishing volumes remain; the main bridge/tip/chin silhouette is now sculpted into HeadShellV48.
add_sphere(HEAD,'NoseTipSoftV48',(0,-.0435,head_d*.645),(.0085,.0072,.0050),SKIN,30,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV48_{side}',(side*.0063,-.0520,head_d*.635),(.00105,.00072,.00070),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV48',0,-.0785,head_d*.607,.0375,.0055,.0020,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV48',0,-.0870,head_d*.602,.0355,.0065,.0024,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV48',[(-.0320,-.0825,head_d*.614),(0,-.0840,head_d*.616),(.0320,-.0825,head_d*.614)],.00028,FACE_DARK)

"""
s=s[:a]+face+s[b:]

# Replace every visible sphere-cap and chunky forehead tube with one continuous cap and thin swept sheets.
a=s.index('# Hair v4.7:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v4.8: one continuous scalp shell, thin swept fringe sheets and a deep flowing ponytail.
# The full ellipse sits behind the face at the front but extends beyond the skull at the sides/back,
# producing one uninterrupted hair silhouette instead of the v4.7 stack of visible spheres.
hair_cap=add_section_mesh(HEAD,'HairCapV48',[
 (-.132,head_w*.335,head_d*.500,head_d*.080,-head_d*.100),
 (-.092,head_w*.455,head_d*.590,head_d*.110,-head_d*.098),
 (-.045,head_w*.515,head_d*.650,head_d*.150,-head_d*.090),
 (.010,head_w*.548,head_d*.675,head_d*.190,-head_d*.082),
 (.065,head_w*.552,head_d*.660,head_d*.225,-head_d*.070),
 (.112,head_w*.515,head_d*.605,head_d*.235,-head_d*.058),
 (.150,head_w*.420,head_d*.500,head_d*.190,-head_d*.044),
 (.178,head_w*.275,head_d*.340,head_d*.125,-head_d*.030),
 (.194,head_w*.105,head_d*.150,head_d*.055,-head_d*.018)
],HAIR,64)
_hmod=hair_cap.modifiers.new('hair_cap_subdivision','SUBSURF');_hmod.levels=1;_hmod.render_levels=1
bpy.context.view_layer.objects.active=hair_cap;bpy.ops.object.modifier_apply(modifier=_hmod.name)

# Asymmetric sheets overlap like real bangs. They are intentionally thin in depth and stay just in front
# of the forehead, unlike the rounded add_lock_mesh tubes used in v4.7.
bangs=[
 ((-.125,.157,head_d*.020),(-.104,.132,head_d*.245),(-.078,.094,head_d*.455),(-.050,.052,head_d*.548),.052,.024),
 ((-.092,.164,head_d*.018),(-.068,.135,head_d*.270),(-.036,.096,head_d*.470),(-.010,.045,head_d*.552),.056,.026),
 ((-.055,.168,head_d*.016),(-.028,.137,head_d*.285),(.008,.098,head_d*.480),(.035,.038,head_d*.553),.058,.026),
 ((-.018,.168,head_d*.014),(.010,.136,head_d*.290),(.048,.096,head_d*.478),(.078,.030,head_d*.551),.056,.024),
 ((.020,.164,head_d*.014),(.047,.132,head_d*.278),(.083,.091,head_d*.462),(.108,.024,head_d*.545),.050,.021),
 ((.054,.156,head_d*.012),(.080,.124,head_d*.255),(.111,.081,head_d*.438),(.130,.016,head_d*.536),.043,.018),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(bangs):
 add_flow_ribbon(HEAD,f'BangSheetV48_{i}',[p0,p1,p2,p3],[w0,w0*.92,w0*.70,w1],.0032,HAIR_HI if i in(0,5) else HAIR)

# Small crossing veil breaks the comb rhythm and gives the reference's soft diagonal fringe.
for i,(x0,x1,x2,y2) in enumerate(((-.108,-.040,.018,.056),(-.060,.014,.074,.047),(-.005,.060,.118,.030))):
 add_flow_ribbon(HEAD,f'BangVeilV48_{i}',[(x0,.160,head_d*.022),(x1,.121,head_d*.330),(x2,y2,head_d*.554)],[.030,.028,.012],.0024,HAIR_HI if i==2 else HAIR)

for side in(-1,1):
 # Face-framing locks are flatter in X but have enough front/back depth to read in profile.
 pts=[(side*head_w*.360,.100,-.004),(side*head_w*.414,.030,head_d*.080),(side*head_w*.435,-.085,head_d*.070),(side*head_w*.420,-.225,.030),(side*head_w*.382,-.405,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV48_{side}',pts,[.018,.022,.020,.014,.005],[.014,.016,.014,.010,.004],HAIR,12)
 add_strand(HEAD,f'FaceWispV48_{side}',[(side*head_w*.392,.086,.002),(side*head_w*.442,-.035,head_d*.045),(side*head_w*.430,-.225,.004),(side*head_w*.395,-.440,-.040)],.00044,HAIR_HI)

# The ponytail uses five deep, overlapping masses rather than nine narrow pipes. Front/back depth is
# deliberately substantial so the side silhouette reads as a flowing ponytail instead of a beam.
add_sphere(HEAD,'PonyRootV48',(.020,.148,-head_d*.560),(.082,.060,.095),HAIR,40,28)
add_box(HEAD,'HairTieV48',(.022,.142,-head_d*.610),(.088,.022,.042),SILVER,.005)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(5):
 lane=(i-2)/2
 pts=[
  (lane*.028+.020,.145,-head_d*.610+lane*.010),
  (lane*.045+.025,.020,-head_d*.850-lane*.012),
  (lane*.070+.030,-.235,-.670-lane*.025),
  (lane*.095+.035,-.565,-.565+lane*.010),
  (lane*.115+.045,-.930,-.455+lane*.025),
  (lane*.135+.055,-1.285,-.335+lane*.030),
  (lane*.155+.060,-1.600-(i%2)*.035,-.205+lane*.020)
 ]
 base=.105-.015*abs(lane)
 add_lock_mesh(PONY,f'PonyMassV48_{i}',pts,[base*.78,base,base*1.05,base*.98,base*.80,base*.52,.010],[.060,.078,.082,.072,.056,.035,.008],HAIR_HI if i in(1,3) else HAIR,14)
for i in range(7):
 lane=(i-3)/3
 add_strand(PONY,f'PonyWispV48_{i}',[(lane*.038+.020,.146,-head_d*.620),(lane*.060+.035,-.040,-head_d*.875),(lane*.095+.050,-.390,-.635),(lane*.135+.070,-.860,-.445),(lane*.180+.090,-1.590-(i%3)*.035,-.185)],.00042+(i%3)*.00007,HAIR_HI if i%2==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V48: unified hair cap, sheet fringe, iris-dominant eyes and profile rebuild')
