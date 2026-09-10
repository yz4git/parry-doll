from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V56' in s:
    print('Blender heroine generator already carries REFERENCE_V56')
    raise SystemExit(0)
if '# REFERENCE_V55' not in s:
    raise SystemExit('REFERENCE_V55 generator required before v5.6')

s=s.replace(
    '# REFERENCE_V55: single closed profile head, recessed orbits and scalp-covered swept hair.',
    '# REFERENCE_V55: single closed profile head, recessed orbits and scalp-covered swept hair.\n# REFERENCE_V56: cleaner adult profile, visible almond eyes and eyebrow-clear swept fringe.',
    1,
)

# Rebalance the single closed head itself: smaller nasal tip, recessed philtrum/labiomental plane,
# a separate chin point and a flatter orbit/forehead transition. No overlapping face shell is added.
a=s.index("add_profile_head_v55(HEAD,'HeadShellV55',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_profile_head_v55(HEAD,'HeadShellV56',[
 (-.148,.030,.046,.055),
 (-.140,.046,.058,.074),
 (-.132,.064,.071,.094),
 (-.122,.082,.081,.108),
 (-.112,.098,.088,.102),
 (-.102,.110,.092,.094),
 (-.092,.119,.095,.099),
 (-.084,.125,.097,.108),
 (-.076,.129,.098,.110),
 (-.068,.132,.099,.101),
 (-.058,.133,.100,.100),
 (-.048,.133,.100,.121),
 (-.040,.133,.101,.126),
 (-.030,.133,.102,.111),
 (-.016,.133,.103,.103),
 (.000,.133,.103,.098),
 (.018,.133,.103,.093),
 (.034,.133,.103,.091),
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

# Move portrait features just in front of the recessed orbit and keep the iris large enough to read
# without returning to the oversized circular-button look of earlier revisions.
a=s.index('# Anatomy v5.5:')
b=s.index('# Hair v5.5:',a)
face=r'''# Anatomy v5.6: visible almond eyes on the orbit surface, smaller nose cues and restrained lips.
face_front=.0918
eye_y=.0320
eye_x=head_w*.146
eye_rx=head_w*.112
eye_ry=.0128
eye_tilt=.0030
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV56_{side}',(ex,eye_y,.0780),(head_w*.072,.0145,.0110),SCLERA,42,24)
 add_almond_surface(HEAD,f'EyeOpeningV56_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00125,SCLERA,60,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV56_{side}',ex,eye_y,face_front+.0014,head_w*.049,.0090,IRIS,44)
 add_ellipse_surface(HEAD,f'IrisInnerV56_{side}',ex,eye_y-.0002,face_front+.0020,head_w*.030,.0061,IRIS_INNER,38)
 add_ellipse_surface(HEAD,f'PupilV56_{side}',ex,eye_y-.0002,face_front+.0026,head_w*.0125,.0035,PUPIL,30)
 add_ellipse_surface(HEAD,f'EyeLightV56_{side}',ex-side*head_w*.0090,eye_y+.0034,face_front+.0032,head_w*.0031,.00155,SCLERA,16)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV56_{side}',[(inner,inner_y+.0010,face_front+.0021),(ex,eye_y+.0130,face_front+.0028),(outer,outer_y+.0010,face_front+.0022)],.00032,FACE_DARK)
 add_strand(HEAD,f'UpperLashV56_{side}',[(inner,inner_y+.0013,face_front+.0028),(ex,eye_y+.0135,face_front+.0033),(outer,outer_y+.0013,face_front+.0029)],.00042,HAIR)
 add_strand(HEAD,f'LowerLidV56_{side}',[(inner+side*eye_rx*.12,inner_y-.0002,face_front+.0018),(ex,eye_y-.0080,face_front+.0022),(outer-side*eye_rx*.12,outer_y-.0002,face_front+.0018)],.00014,FACE_DARK)
 add_strand(HEAD,f'BrowV56_{side}',[(ex-side*eye_rx*.78,.0655,.1015),(ex,.0740,.1032),(ex+side*eye_rx*.98,.0630,.1020)],.00055,HAIR)

# The single shell owns the nose and chin silhouette. These are only small readable details.
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV56_{side}',(side*.0044,-.0540,.1175),(.00048,.00034,.00030),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV56',0,-.0765,.1088,.0285,.0041,.00095,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV56',0,-.0840,.1096,.0275,.0046,.00105,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV56',[(-.0240,-.0807,.1104),(0,-.0817,.1109),(.0240,-.0807,.1104)],.00014,FACE_DARK)

'''
s=s[:a]+face+s[b:]

# Clear the eye line. Hair still sweeps diagonally like the reference, but the ends stop around eyebrow height.
a=s.index('# Hair v5.5:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.6: crown coverage retained, but fringe is lifted off the eyes and consolidated into two broad flows.
add_section_mesh(HEAD,'HairTopCapV56',[
 (.066,head_w*.448,head_d*.438,head_d*.486,-.018),
 (.100,head_w*.442,head_d*.430,head_d*.476,-.020),
 (.134,head_w*.398,head_d*.388,head_d*.432,-.021),
 (.164,head_w*.308,head_d*.298,head_d*.338,-.018),
 (.188,head_w*.184,head_d*.178,head_d*.205,-.010),
 (.203,head_w*.068,head_d*.068,head_d*.078,-.002)
],HAIR,56)
add_rear_hair_shell(HEAD,'HairRearShellV56',[
 (-.024,head_w*.288,head_d*.396,-head_d*.065),
 (.012,head_w*.416,head_d*.486,-head_d*.057),
 (.052,head_w*.490,head_d*.534,-head_d*.049),
 (.096,head_w*.512,head_d*.546,-head_d*.041),
 (.138,head_w*.474,head_d*.502,-head_d*.032),
 (.170,head_w*.380,head_d*.408,-head_d*.023),
 (.194,head_w*.222,head_d*.260,-head_d*.012),
 (.205,head_w*.076,head_d*.100,-head_d*.005)
],HAIR,44)

# Main side sweep stays above the eye centres and opens the left/central face.
add_flow_ribbon(HEAD,'FringeSweepV56_A',[(-.108,.181,.010),(-.091,.159,.044),(-.060,.132,.073),(-.020,.104,.094),(.025,.082,.103),(.066,.069,.106)],[.080,.082,.075,.060,.043,.026],.00135,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV56_B',[(-.040,.183,.010),(-.018,.158,.046),(.016,.130,.075),(.052,.102,.096),(.086,.080,.104),(.112,.066,.106)],[.068,.067,.060,.047,.033,.020],.00130,HAIR)
# A short side accent gives asymmetry without dropping across an eye.
add_flow_ribbon(HEAD,'FringeAccentV56',[(.012,.176,.011),(.038,.151,.048),(.070,.123,.077),(.098,.097,.097),(.118,.078,.103)],[.040,.038,.032,.024,.014],.00118,HAIR_HI)
add_strand(HEAD,'FringeEdgeV56_A',[(-.102,.173,.014),(-.063,.135,.070),(.015,.090,.102)],.00010,HAIR_HI)
add_strand(HEAD,'FringeEdgeV56_B',[(-.034,.174,.014),(.018,.134,.073),(.096,.084,.103)],.00009,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.390,.110,-head_d*.036),(side*head_w*.418,.047,-.012),(side*head_w*.422,-.030,-.015),(side*head_w*.410,-.102,-.042),(side*head_w*.395,-.172,-.061)]
 add_smooth_lock(HEAD,f'FaceLockV56_{side}',pts,[.0085,.0108,.0090,.0052,.0022],[.0070,.0080,.0062,.0040,.0020],HAIR,10,5)

add_box(HEAD,'HairTieV56',(.014,.136,-head_d*.526),(.066,.015,.024),SILVER,.003)
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
 add_smooth_lock(PONY,f'PonyMassV56_{i}',pts,widths,depths,HAIR,10,6)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV56_{i}',[(lane*.022+.014,.134,-head_d*.543),(lane*.031+.020,-.030,-head_d*.607),(lane*.044+.026,-.345,-.214),(lane*.061+.034,-.810,-.147),(lane*.078+.045,-1.450-(i%2)*.020,-.087)],.00020+(i%2)*.00003,HAIR_HI if i in(1,3) else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V56: cleaner profile, visible eyes and eyebrow-clear swept fringe')
