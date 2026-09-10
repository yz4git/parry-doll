from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V53' in s:
    print('Blender heroine generator already carries REFERENCE_V53')
    raise SystemExit(0)
if '# REFERENCE_V52' not in s:
    raise SystemExit('REFERENCE_V52 generator required before v5.3')

s=s.replace(
    '# REFERENCE_V52: Catmull-smoothed pony, broad swept fringe and larger dark-brown eyes.',
    '# REFERENCE_V52: Catmull-smoothed pony, broad swept fringe and larger dark-brown eyes.\n# REFERENCE_V53: embedded portrait features, realistic iris scale, unified fringe and soft profile.',
    1,
)

# Pull the sculpted face back from the caricatured v5.2 profile. The shell should carry the
# nose-mouth-chin silhouette; coloured feature meshes should only finish the surface.
s=s.replace("z+=fm*.0180*math.exp(-((x-cheek_x)/(head_w*.110))**2-((yy+.010)/.043)**2)",
            "z+=fm*.0125*math.exp(-((x-cheek_x)/(head_w*.112))**2-((yy+.010)/.045)**2)",1)
s=s.replace("z+=fm*.0300*math.exp(-(x/(head_w*.066))**2-((yy+.005)/.062)**2)",
            "z+=fm*.0185*math.exp(-(x/(head_w*.068))**2-((yy+.005)/.064)**2)",1)
s=s.replace("z+=fm*.0530*math.exp(-(x/(head_w*.078))**2-((yy+.043)/.026)**2)",
            "z+=fm*.0305*math.exp(-(x/(head_w*.080))**2-((yy+.043)/.027)**2)",1)
s=s.replace("z+=fm*.0220*math.exp(-(x/(head_w*.164))**2-((yy+.082)/.028)**2)",
            "z+=fm*.0135*math.exp(-(x/(head_w*.168))**2-((yy+.082)/.030)**2)",1)
s=s.replace("z+=fm*.0240*math.exp(-(x/(head_w*.128))**2-((yy+.116)/.024)**2)",
            "z+=fm*.0155*math.exp(-(x/(head_w*.132))**2-((yy+.116)/.026)**2)",1)

# Neutral portrait materials: warm but not orange, with a dark outer iris and a softer amber centre.
s=s.replace("SKIN=material('Skin',(0.54,0.36,0.34),0,.68)","SKIN=material('Skin',(0.58,0.405,0.390),0,.66)",1)
s=s.replace("SCLERA=material('Sclera',(0.82,0.78,0.75),0,.50)","SCLERA=material('Sclera',(0.86,0.83,0.81),0,.54)",1)
s=s.replace("IRIS=material('Iris',(0.17,0.075,0.048),.01,.36)","IRIS=material('Iris',(0.105,0.045,0.030),.01,.38)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.30,0.135,0.065),.01,.38)","IRIS_INNER=material('Iris Inner',(0.34,0.145,0.070),.01,.42)",1)
s=s.replace("LIP=material('Lip',(0.42,0.18,0.18),0,.60)","LIP=material('Lip',(0.36,0.135,0.150),0,.62)",1)

a=s.index('# Anatomy v5.2:')
b=s.index('# Hair v5.2:',a)
face=r'''# Anatomy v5.3: features sit inside the sculpted shell instead of floating in front of it.
face_front=head_d*.466
eye_y=.0300
eye_x=head_w*.147
eye_rx=head_w*.108
eye_ry=.0112
eye_tilt=.0030
for side in(-1,1):
 ex=side*eye_x
 # The hidden globe supplies curved sclera at glancing angles; the visible opening remains a slim adult almond.
 add_sphere(HEAD,f'EyeballHiddenV53_{side}',(ex,eye_y,head_d*.398),(head_w*.076,.0160,head_d*.050),SCLERA,44,26)
 add_almond_surface(HEAD,f'EyeOpeningV53_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0017,SCLERA,58,side,eye_tilt)
 # Human-scale iris discs: large enough to read on iPhone, but no longer button-like.
 add_ellipse_surface(HEAD,f'IrisV53_{side}',ex,eye_y,face_front+.0017,head_w*.047,.0092,IRIS,44)
 add_ellipse_surface(HEAD,f'IrisInnerV53_{side}',ex,eye_y-.0002,face_front+.0023,head_w*.031,.0065,IRIS_INNER,40)
 add_ellipse_surface(HEAD,f'PupilV53_{side}',ex,eye_y-.0002,face_front+.0029,head_w*.014,.0040,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV53_{side}',ex-side*head_w*.010,eye_y+.0034,face_front+.0034,head_w*.0038,.0018,SCLERA,18)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV53_{side}',[(inner,inner_y+.0010,face_front+.0025),(ex,eye_y+.0118,face_front+.0032),(outer,outer_y+.0010,face_front+.0025)],.00042,FACE_DARK)
 add_strand(HEAD,f'UpperLashV53_{side}',[(inner,inner_y+.0015,face_front+.0032),(ex,eye_y+.0124,face_front+.0038),(outer,outer_y+.0015,face_front+.0033)],.00053,HAIR)
 add_strand(HEAD,f'LashWingV53_{side}',[(outer,outer_y+.0015,face_front+.0033),(outer+side*head_w*.014,outer_y+.0048,face_front+.0034)],.00034,HAIR)
 # Softer brows follow the orbital ridge rather than sitting high on the forehead.
 add_strand(HEAD,f'BrowV53_{side}',[(ex-side*eye_rx*.74,.0645,head_d*.472),(ex,.0728,head_d*.477),(ex+side*eye_rx*.96,.0620,head_d*.473)],.00066,HAIR)

# Finishing features stay close to the face shell; profile depth now comes from add_portrait_head_v44.
add_sphere(HEAD,'NoseTipSoftV53',(0,-.0430,head_d*.620),(.0055,.0051,.0030),SKIN,28,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV53_{side}',(side*.0052,-.0510,head_d*.602),(.00072,.00052,.00046),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV53',0,-.0775,head_d*.558,.0360,.0048,.0017,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV53',0,-.0850,head_d*.554,.0345,.0056,.0019,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV53',[(-.0300,-.0812,head_d*.564),(0,-.0824,head_d*.566),(.0300,-.0812,head_d*.564)],.00018,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v5.2:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.3: continuous side-swept fringe over the open rear shell and soft multi-lock pony.
add_rear_hair_shell(HEAD,'HairRearShellV53',[
 (-.026,head_w*.292,head_d*.402,-head_d*.066),
 (.010,head_w*.420,head_d*.492,-head_d*.058),
 (.050,head_w*.495,head_d*.540,-head_d*.050),
 (.094,head_w*.518,head_d*.552,-head_d*.042),
 (.136,head_w*.480,head_d*.507,-head_d*.033),
 (.168,head_w*.386,head_d*.414,-head_d*.024),
 (.193,head_w*.226,head_d*.265,-head_d*.013),
 (.205,head_w*.078,head_d*.102,-head_d*.005)
],HAIR,44)

# Four heavily-overlapped sheets read as one fringe silhouette. Their ends keep width instead of forming claws.
swept=[
 ((-.135,.181,head_d*.003),(-.108,.151,head_d*.274),(-.060,.108,head_d*.468),(.010,.058,head_d*.531),.067,.038),
 ((-.087,.184,head_d*.003),(-.055,.151,head_d*.302),(-.002,.103,head_d*.490),(.061,.044,head_d*.536),.066,.035),
 ((-.039,.183,head_d*.002),(-.006,.148,head_d*.309),(.045,.097,head_d*.486),(.101,.032,head_d*.530),.060,.030),
 ((.008,.177,head_d*.002),(.039,.141,head_d*.286),(.083,.088,head_d*.458),(.128,.021,head_d*.516),.050,.024),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(swept):
 add_flow_ribbon(HEAD,f'BangSweepV53_{i}',[p0,p1,p2,p3],[w0,w0*.94,w0*.76,w1],.00175,HAIR)

# Two near-black hairline accents give flow without bright painted stripes.
for i,pts in enumerate((
 [(-.111,.174,head_d*.007),(-.064,.128,head_d*.342),(.018,.060,head_d*.532)],
 [(-.046,.176,head_d*.006),(.010,.124,head_d*.354),(.095,.039,head_d*.524)],
)):
 add_strand(HEAD,f'BangWispV53_{i}',pts,.00013,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.392,.106,-head_d*.038),(side*head_w*.421,.040,-.013),(side*head_w*.425,-.038,-.016),(side*head_w*.412,-.108,-.043),(side*head_w*.397,-.177,-.062)]
 add_smooth_lock(HEAD,f'FaceLockV53_{side}',pts,[.009,.0115,.0095,.0055,.0024],[.0075,.0085,.0065,.0042,.0021],HAIR,10,5)

add_box(HEAD,'HairTieV53',(.014,.136,-head_d*.526),(.068,.016,.025),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# Nine slimmer locks with stronger depth staggering prevent the side view collapsing into one flat board.
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
 add_smooth_lock(PONY,f'PonyMassV53_{i}',pts,widths,depths,HAIR,10,6)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV53_{i}',[(lane*.022+.014,.134,-head_d*.543),(lane*.031+.020,-.030,-head_d*.607),(lane*.044+.026,-.345,-.214),(lane*.061+.034,-.810,-.147),(lane*.078+.045,-1.450-(i%2)*.020,-.087)],.00020+(i%2)*.00003,HAIR_HI if i in(1,3) else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V53: embedded portrait, realistic iris scale and unified swept hair')
