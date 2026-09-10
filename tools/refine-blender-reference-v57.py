from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V57' in s:
    print('Blender heroine generator already carries REFERENCE_V57')
    raise SystemExit(0)
if '# REFERENCE_V56' not in s:
    raise SystemExit('REFERENCE_V56 generator required before v5.7')

s=s.replace(
    '# REFERENCE_V56: cleaner adult profile, visible almond eyes and eyebrow-clear swept fringe.',
    '# REFERENCE_V56: cleaner adult profile, visible almond eyes and eyebrow-clear swept fringe.\n# REFERENCE_V57: expressive realistic-anime eyes, tapered lower face and filled side-swept hairline.',
    1,
)

# Slightly taper the lower face and create a more visible labiomental break while preserving v5.6's safer nose.
a=s.index("add_profile_head_v55(HEAD,'HeadShellV56',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_profile_head_v55(HEAD,'HeadShellV57',[
 (-.149,.029,.045,.054),
 (-.141,.044,.057,.073),
 (-.133,.061,.070,.091),
 (-.123,.078,.080,.103),
 (-.113,.091,.087,.097),
 (-.103,.103,.091,.090),
 (-.093,.114,.094,.097),
 (-.084,.121,.096,.108),
 (-.076,.126,.098,.110),
 (-.068,.130,.099,.100),
 (-.058,.132,.100,.099),
 (-.048,.133,.100,.120),
 (-.040,.133,.101,.124),
 (-.030,.133,.102,.110),
 (-.016,.133,.103,.102),
 (.000,.133,.103,.097),
 (.018,.133,.103,.092),
 (.034,.133,.103,.090),
 (.052,.132,.102,.096),
 (.072,.129,.101,.101),
 (.095,.121,.099,.101),
 (.118,.108,.095,.094),
 (.140,.088,.087,.082),
 (.160,.062,.073,.066),
 (.176,.032,.052,.045)
],SKIN,96)
"""
s=s[:a]+head+s[b:]

# Reduce the toy-white sclera and make the iris a dark warm brown closer to the portrait reference.
s=s.replace("SCLERA=material('Sclera',(0.82,0.78,0.75),0,.50)","SCLERA=material('Sclera',(0.72,0.69,0.67),0,.54)",1)
s=s.replace("IRIS=material('Iris',(0.17,0.075,0.048),.01,.36)","IRIS=material('Iris',(0.115,0.050,0.036),.01,.38)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.30,0.135,0.065),.01,.38)","IRIS_INNER=material('Iris Inner',(0.205,0.090,0.050),.01,.40)",1)

a=s.index('# Anatomy v5.6:')
b=s.index('# Hair v5.6:',a)
face=r'''# Anatomy v5.7: wider realistic-anime almond eyes and compact natural mouth.
face_front=.0923
eye_y=.0325
eye_x=head_w*.146
eye_rx=head_w*.126
eye_ry=.0148
eye_tilt=.0034
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV57_{side}',(ex,eye_y,.0785),(head_w*.078,.0150,.0118),SCLERA,44,26)
 add_almond_surface(HEAD,f'EyeOpeningV57_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00130,SCLERA,64,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV57_{side}',ex,eye_y,face_front+.00145,head_w*.058,.0107,IRIS,48)
 add_ellipse_surface(HEAD,f'IrisInnerV57_{side}',ex,eye_y-.0001,face_front+.00205,head_w*.036,.0070,IRIS_INNER,42)
 add_ellipse_surface(HEAD,f'PupilV57_{side}',ex,eye_y-.0001,face_front+.00270,head_w*.0145,.0040,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV57A_{side}',ex-side*head_w*.0105,eye_y+.0042,face_front+.00330,head_w*.0037,.00185,SCLERA,18)
 add_ellipse_surface(HEAD,f'EyeLightV57B_{side}',ex+side*head_w*.0060,eye_y+.0015,face_front+.00335,head_w*.0016,.00085,SCLERA,14)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV57_{side}',[(inner,inner_y+.0010,face_front+.0022),(ex,eye_y+.0151,face_front+.0029),(outer,outer_y+.0010,face_front+.0023)],.00033,FACE_DARK)
 add_strand(HEAD,f'UpperLashV57_{side}',[(inner,inner_y+.0013,face_front+.0029),(ex,eye_y+.0157,face_front+.0034),(outer,outer_y+.0013,face_front+.0030)],.00047,HAIR)
 add_strand(HEAD,f'LashWingV57_{side}',[(outer,outer_y+.0013,face_front+.0030),(outer+side*head_w*.012,outer_y+.0048,face_front+.0030)],.00028,HAIR)
 add_strand(HEAD,f'LowerLidV57_{side}',[(inner+side*eye_rx*.12,inner_y-.0002,face_front+.0019),(ex,eye_y-.0090,face_front+.00225),(outer-side*eye_rx*.12,outer_y-.0002,face_front+.0019)],.00013,FACE_DARK)
 add_strand(HEAD,f'BrowV57_{side}',[(ex-side*eye_rx*.78,.0668,.1018),(ex,.0757,.1035),(ex+side*eye_rx*.98,.0638,.1022)],.00058,HAIR)

for side in(-1,1):
 add_sphere(HEAD,f'NostrilV57_{side}',(side*.0042,-.0540,.1164),(.00044,.00031,.00028),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV57',0,-.0760,.1084,.0270,.0040,.00090,LIP,54,1,0.0)
add_almond_surface(HEAD,'LowerLipV57',0,-.0835,.1092,.0263,.0045,.00100,LIP,54,1,0.0)
add_strand(HEAD,'MouthSeamV57',[(-.0230,-.0802,.1100),(0,-.0812,.1105),(.0230,-.0802,.1100)],.00013,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v5.6:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.7: dark forehead underlay removes the pale scalp gaps while preserving an open eye line.
add_section_mesh(HEAD,'HairTopCapV57',[
 (.066,head_w*.448,head_d*.438,head_d*.486,-.018),
 (.100,head_w*.442,head_d*.430,head_d*.476,-.020),
 (.134,head_w*.398,head_d*.388,head_d*.432,-.021),
 (.164,head_w*.308,head_d*.298,head_d*.338,-.018),
 (.188,head_w*.184,head_d*.178,head_d*.205,-.010),
 (.203,head_w*.068,head_d*.068,head_d*.078,-.002)
],HAIR,56)
add_rear_hair_shell(HEAD,'HairRearShellV57',[
 (-.024,head_w*.288,head_d*.396,-head_d*.065),
 (.012,head_w*.416,head_d*.486,-head_d*.057),
 (.052,head_w*.490,head_d*.534,-head_d*.049),
 (.096,head_w*.512,head_d*.546,-head_d*.041),
 (.138,head_w*.474,head_d*.502,-head_d*.032),
 (.170,head_w*.380,head_d*.408,-head_d*.023),
 (.194,head_w*.222,head_d*.260,-head_d*.012),
 (.205,head_w*.076,head_d*.100,-head_d*.005)
],HAIR,44)
# A shallow dark underlay sits only above the brows; the visible skin below remains untouched.
add_panel(HEAD,'HairlineUnderlayV57',[(-.111,.137,.101),(-.071,.169,.101),(-.015,.181,.101),(.052,.173,.101),(.111,.135,.101),(.102,.099,.103),(.048,.109,.104),(-.016,.101,.104),(-.080,.098,.103)],.0010,HAIR)

add_flow_ribbon(HEAD,'FringeSweepV57_A',[(-.110,.181,.011),(-.093,.160,.045),(-.062,.135,.074),(-.022,.109,.095),(.024,.087,.104),(.066,.073,.107)],[.074,.076,.070,.057,.041,.025],.00130,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV57_B',[(-.041,.183,.011),(-.019,.159,.047),(.015,.133,.076),(.051,.107,.097),(.086,.086,.105),(.113,.072,.107)],[.062,.061,.055,.044,.031,.019],.00125,HAIR)
add_flow_ribbon(HEAD,'FringeAccentV57',[(.014,.177,.012),(.040,.153,.049),(.072,.127,.078),(.100,.102,.098),(.120,.084,.104)],[.036,.034,.029,.021,.013],.00115,HAIR_HI)
add_strand(HEAD,'FringeEdgeV57_A',[(-.100,.174,.015),(-.061,.139,.071),(.016,.096,.103)],.00009,HAIR_HI)
add_strand(HEAD,'FringeEdgeV57_B',[(-.033,.175,.015),(.020,.137,.074),(.098,.090,.104)],.000085,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.390,.111,-head_d*.036),(side*head_w*.418,.048,-.012),(side*head_w*.422,-.029,-.015),(side*head_w*.410,-.101,-.042),(side*head_w*.395,-.171,-.061)]
 add_smooth_lock(HEAD,f'FaceLockV57_{side}',pts,[.0085,.0108,.0090,.0052,.0022],[.0070,.0080,.0062,.0040,.0020],HAIR,10,5)

add_box(HEAD,'HairTieV57',(.014,.136,-head_d*.526),(.066,.015,.024),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(9):
 lane=(i-4)/4
 dz=lane*.034+((i%3)-1)*.010
 sway=.020*math.sin((i+1)*1.7)
 pts=[
  (lane*.020+.014,.136,-head_d*.538+dz*.20),
  (lane*.028+.018+sway*.20,.020,-head_d*.602+dz*.75),
  (lane*.040+.022+sway*.55,-.245,-.232+dz),
  (lane*.052+.027+sway,-.555,-.186+dz*1.20),
  (lane*.063+.032+sway*.70,-.890,-.143+dz*1.25),
  (lane*.073+.038+sway*.35,-1.210,-.112+dz*1.15),
  (lane*.082+.043,-1.445-(i%3)*.018,-.091+dz)
 ]
 base=.043-.006*abs(lane)
 widths=[base*.70,base,base*.94,base*.80,base*.59,base*.31,.0044]
 depths=[.022,.029,.029,.025,.019,.011,.0036]
 add_smooth_lock(PONY,f'PonyMassV57_{i}',pts,widths,depths,HAIR,10,6)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV57_{i}',[(lane*.022+.014,.134,-head_d*.543),(lane*.031+.020,-.030,-head_d*.607),(lane*.044+.026,-.345,-.214),(lane*.061+.034,-.810,-.147),(lane*.078+.045,-1.450-(i%2)*.020,-.087)],.00020+(i%2)*.00003,HAIR_HI if i in(1,3) else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V57: expressive eyes, tapered face and filled side-swept hairline')
