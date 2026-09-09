from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V49' in s:
    print('Blender heroine generator already carries REFERENCE_V49')
    raise SystemExit(0)
if '# REFERENCE_V48' not in s:
    raise SystemExit('REFERENCE_V48 generator required before v4.9')

s=s.replace(
    '# REFERENCE_V48: unified hair cap, sheet fringe, iris-dominant eyes and rebuilt side-profile depth.',
    '# REFERENCE_V48: unified hair cap, sheet fringe, iris-dominant eyes and rebuilt side-profile depth.\n# REFERENCE_V49: skull-hugging hair, vertical pony cascade, readable warm irises and stronger profile.',
    1,
)

# Warm eye layers must remain readable against the nearly-black pupil under the bright WebGL viewer.
s=s.replace("SCLERA=material('Sclera',(0.76,0.72,0.69),0,.46)", "SCLERA=material('Sclera',(0.82,0.78,0.75),0,.50)", 1)
s=s.replace("IRIS=material('Iris',(0.25,0.135,0.090),.02,.31)", "IRIS=material('Iris',(0.38,0.20,0.12),.02,.36)\nIRIS_INNER=material('Iris Inner',(0.56,0.27,0.12),.01,.40)", 1)
s=s.replace("HAIR_HI=material('Hair Highlight',(0.070,0.045,0.052),0.0,.48)", "HAIR_HI=material('Hair Highlight',(0.045,0.029,0.036),0.0,.54)", 1)

# Give the continuous face shell enough profile depth to survive the bright flat viewer lighting.
s=s.replace("z+=fm*.0250*math.exp(-(x/(head_w*.064))**2-((yy+.005)/.060)**2)",
            "z+=fm*.0300*math.exp(-(x/(head_w*.066))**2-((yy+.005)/.062)**2)",1)
s=s.replace("z+=fm*.0540*math.exp(-(x/(head_w*.074))**2-((yy+.043)/.024)**2)",
            "z+=fm*.0620*math.exp(-(x/(head_w*.076))**2-((yy+.043)/.025)**2)",1)
s=s.replace("z+=fm*.0110*math.exp(-(x/(head_w*.155))**2-((yy+.082)/.025)**2)",
            "z+=fm*.0155*math.exp(-(x/(head_w*.158))**2-((yy+.082)/.026)**2)",1)
s=s.replace("z+=fm*.0140*math.exp(-(x/(head_w*.120))**2-((yy+.120)/.021)**2)",
            "z+=fm*.0170*math.exp(-(x/(head_w*.122))**2-((yy+.118)/.022)**2)",1)

a=s.index('# Anatomy v4.8:')
b=s.index('# Hair v4.8:',a)
face="""# Anatomy v4.9: warm layered iris, calmer almond opening and stronger side-profile cues.
face_front=head_d*.528
eye_y=.0295
eye_x=head_w*.144
eye_rx=head_w*.122
eye_ry=.0119
eye_tilt=.0032
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV49_{side}',(ex,eye_y,head_d*.426),(head_w*.090,.0175,head_d*.066),SCLERA,44,26)
 add_almond_surface(HEAD,f'EyeOpeningV49_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0024,SCLERA,52,side,eye_tilt)
 add_sphere(HEAD,f'IrisV49_{side}',(ex,eye_y,face_front+.0062),(head_w*.0780,.0105,.0032),IRIS,44,26)
 add_sphere(HEAD,f'IrisInnerV49_{side}',(ex,eye_y-.0004,face_front+.0082),(head_w*.0470,.0078,.0022),IRIS_INNER,38,22)
 add_sphere(HEAD,f'PupilV49_{side}',(ex,eye_y-.0005,face_front+.0100),(head_w*.0240,.0052,.0017),PUPIL,28,16)
 add_sphere(HEAD,f'EyeLightV49A_{side}',(ex-side*head_w*.0160,eye_y+.0046,face_front+.0118),(head_w*.0060,.0025,.0010),SCLERA,14,8)
 add_sphere(HEAD,f'EyeLightV49B_{side}',(ex+side*head_w*.0100,eye_y+.0015,face_front+.0120),(head_w*.0022,.0012,.0007),SCLERA,10,6)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV49_{side}',[(inner,inner_y+.0009,face_front+.0039),(ex,eye_y+.0124,face_front+.0065),(outer,outer_y+.0010,face_front+.0039)],.00058,FACE_DARK)
 add_strand(HEAD,f'UpperLashV49_{side}',[(inner,inner_y+.0016,face_front+.0067),(ex,eye_y+.0130,face_front+.0084),(outer,outer_y+.0018,face_front+.0068)],.00068,HAIR)
 add_strand(HEAD,f'LashWingV49_{side}',[(outer,outer_y+.0018,face_front+.0069),(outer+side*head_w*.016,outer_y+.0058,face_front+.0073)],.00045,HAIR)
 add_strand(HEAD,f'BrowV49_{side}',[(ex-side*eye_rx*.77,.0685,head_d*.523),(ex,.0780,head_d*.527),(ex+side*eye_rx*.97,.0665,head_d*.523)],.00088,HAIR)

# Small finishing volumes sit on the now-stronger shell profile rather than trying to define it alone.
add_sphere(HEAD,'NoseTipSoftV49',(0,-.0435,head_d*.720),(.0078,.0068,.0048),SKIN,30,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV49_{side}',(side*.0060,-.0520,head_d*.680),(.0010,.00070,.00065),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV49',0,-.0780,head_d*.645,.0370,.0054,.0020,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV49',0,-.0865,head_d*.638,.0350,.0063,.0024,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV49',[(-.0315,-.0820,head_d*.651),(0,-.0835,head_d*.654),(.0315,-.0820,head_d*.651)],.00027,FACE_DARK)

"""
s=s[:a]+face+s[b:]

# Rebuild the cap tighter to the skull and remove the low helmet curtain. Keep sheet bangs dark;
# highlights become hairline strands, not pale broad surfaces.
a=s.index('# Hair v4.8:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v4.9: skull-hugging cap, dark layered fringe and a near-vertical pony cascade.
hair_cap=add_section_mesh(HEAD,'HairCapV49',[
 (-.082,head_w*.365,head_d*.455,head_d*.060,-head_d*.078),
 (-.045,head_w*.455,head_d*.505,head_d*.085,-head_d*.072),
 (.000,head_w*.500,head_d*.540,head_d*.115,-head_d*.064),
 (.050,head_w*.520,head_d*.552,head_d*.145,-head_d*.055),
 (.098,head_w*.505,head_d*.535,head_d*.160,-head_d*.046),
 (.138,head_w*.445,head_d*.470,head_d*.145,-head_d*.036),
 (.168,head_w*.340,head_d*.360,head_d*.110,-head_d*.026),
 (.190,head_w*.185,head_d*.205,head_d*.060,-head_d*.016)
],HAIR,64)
_hmod=hair_cap.modifiers.new('hair_cap_subdivision','SUBSURF');_hmod.levels=1;_hmod.render_levels=1
bpy.context.view_layer.objects.active=hair_cap;bpy.ops.object.modifier_apply(modifier=_hmod.name)

bangs=[
 ((-.125,.158,head_d*.024),(-.105,.132,head_d*.260),(-.080,.094,head_d*.468),(-.053,.052,head_d*.552),.047,.021),
 ((-.094,.164,head_d*.022),(-.070,.136,head_d*.282),(-.040,.097,head_d*.486),(-.014,.045,head_d*.558),.050,.022),
 ((-.058,.168,head_d*.020),(-.032,.138,head_d*.298),(.004,.099,head_d*.493),(.032,.038,head_d*.559),.052,.022),
 ((-.022,.168,head_d*.019),(.006,.137,head_d*.300),(.044,.097,head_d*.490),(.074,.031,head_d*.557),.050,.021),
 ((.016,.165,head_d*.018),(.043,.133,head_d*.288),(.080,.092,head_d*.476),(.106,.025,head_d*.550),.045,.019),
 ((.050,.158,head_d*.017),(.076,.126,head_d*.266),(.108,.083,head_d*.454),(.128,.018,head_d*.542),.039,.016),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(bangs):
 add_flow_ribbon(HEAD,f'BangSheetV49_{i}',[p0,p1,p2,p3],[w0,w0*.92,w0*.68,w1],.0028,HAIR)

for i,(x0,x1,x2,y2) in enumerate(((-.107,-.041,.016,.057),(-.060,.012,.071,.048),(-.006,.058,.115,.032))):
 add_flow_ribbon(HEAD,f'BangVeilV49_{i}',[(x0,.160,head_d*.026),(x1,.122,head_d*.345),(x2,y2,head_d*.558)],[.026,.024,.010],.0021,HAIR)
 # Fine highlight follows the sheet centreline without turning into a silver ribbon.
 add_strand(HEAD,f'BangHighlightV49_{i}',[(x0+.004,.158,head_d*.029),(x1+.004,.122,head_d*.350),(x2+.003,y2+.003,head_d*.562)],.00022,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.365,.096,-.002),(side*head_w*.414,.025,head_d*.075),(side*head_w*.426,-.072,head_d*.070),(side*head_w*.408,-.175,.030),(side*head_w*.382,-.285,-.015)]
 add_lock_mesh(HEAD,f'FaceLockV49_{side}',pts,[.016,.019,.017,.012,.004],[.012,.014,.012,.008,.0035],HAIR,12)
 add_strand(HEAD,f'FaceWispV49_{side}',[(side*head_w*.390,.084,.002),(side*head_w*.438,-.025,head_d*.043),(side*head_w*.424,-.175,.004),(side*head_w*.395,-.335,-.032)],.00040,HAIR_HI)

# No spherical pony-root bun: the tie and first pony sections emerge directly from the rear cap.
add_box(HEAD,'HairTieV49',(.018,.126,-head_d*.565),(.080,.020,.036),SILVER,.004)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(5):
 lane=(i-2)/2
 pts=[
  (lane*.026+.018,.128,-head_d*.565+lane*.006),
  (lane*.036+.022,.010,-head_d*.690-lane*.004),
  (lane*.050+.026,-.230,-.190-lane*.010),
  (lane*.064+.030,-.520,-.175+lane*.008),
  (lane*.078+.035,-.850,-.145+lane*.012),
  (lane*.090+.040,-1.180,-.115+lane*.012),
  (lane*.100+.045,-1.500-(i%2)*.030,-.085+lane*.010)
 ]
 base=.095-.013*abs(lane)
 add_lock_mesh(PONY,f'PonyMassV49_{i}',pts,[base*.72,base,base*1.02,base*.96,base*.76,base*.46,.009],[.050,.060,.064,.058,.046,.028,.007],HAIR_HI if i in(1,3) else HAIR,14)
for i in range(7):
 lane=(i-3)/3
 add_strand(PONY,f'PonyWispV49_{i}',[(lane*.030+.018,.128,-head_d*.575),(lane*.040+.024,-.040,-head_d*.705),(lane*.055+.030,-.350,-.185),(lane*.074+.038,-.820,-.140),(lane*.095+.048,-1.500-(i%3)*.030,-.075)],.00038+(i%3)*.00006,HAIR_HI if i%2==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V49: skull hair, vertical pony, warm irises and stronger profile')
