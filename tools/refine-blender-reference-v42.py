from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V42' in s:
    print('Blender heroine generator already carries REFERENCE_V42')
    raise SystemExit(0)
if '# REFERENCE_V41' not in s:
    raise SystemExit('REFERENCE_V41 generator required before v4.2')

s=s.replace(
    '# REFERENCE_V41: sculptural face, swept fringe and consolidated ponytail for a less procedural silhouette.',
    '# REFERENCE_V41: sculptural face, swept fringe and consolidated ponytail for a less procedural silhouette.\n# REFERENCE_V42: portrait depth pass with volumetric lips, softer orbital detail and an offset rear ponytail.',
    1,
)

# V4.1 successfully removed the doll stare, but the close audit still read as drawn facial lines.
# Keep the eyes expressive while reducing contour strokes and let small skin/lip volumes carry the portrait.
a=s.index('# Anatomy v4.1:')
b=s.index('# Hair v4.1:',a)
face="""# Anatomy v4.2: slightly reopened eyes, softer lids and volumetric central features.
face_front=head_d*.512
eye_y=.0315
eye_x=head_w*.141
eye_rx=head_w*.091
eye_ry=.0114
eye_tilt=.0028
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV42_{side}',(ex,eye_y,head_d*.426),(head_w*.076,.0155,head_d*.058),SCLERA,36,22)
 add_almond_surface(HEAD,f'EyeOpeningV42_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0025,SCLERA,38,side,eye_tilt)
 add_sphere(HEAD,f'IrisV42_{side}',(ex,eye_y+.0005,face_front+.0057),(head_w*.038,.0092,.0029),IRIS,32,18)
 add_sphere(HEAD,f'PupilV42_{side}',(ex,eye_y+.0004,face_front+.0083),(head_w*.0130,.0047,.0018),PUPIL,22,12)
 add_sphere(HEAD,f'EyeLightV42_{side}',(ex-side*head_w*.0083,eye_y+.0044,face_front+.0102),(head_w*.0046,.0020,.0010),SCLERA,12,8)
 inner=ex-side*eye_rx*.96;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 # Skin-colored lid volumes create a real orbital fold; dark geometry is limited to one fine upper lash.
 add_sphere(HEAD,f'UpperLidSoftV42_{side}',(ex,eye_y+.0108,face_front-.0010),(head_w*.072,.0058,.0048),SKIN,24,12)
 add_sphere(HEAD,f'LowerLidSoftV42_{side}',(ex,eye_y-.0068,face_front-.0018),(head_w*.066,.0042,.0036),SKIN,24,12)
 add_strand(HEAD,f'UpperLashV42_{side}',[(inner,inner_y+.0017,face_front+.0062),(ex,eye_y+.0120,face_front+.0079),(outer,outer_y+.0019,face_front+.0064)],.00090,HAIR)
 add_strand(HEAD,f'LashWingV42_{side}',[(outer,outer_y+.0019,face_front+.0064),(outer+side*head_w*.016,outer_y+.0062,face_front+.0069)],.00068,HAIR)
 add_strand(HEAD,f'BrowV42_{side}',[(ex-side*eye_rx*.88,.0655,head_d*.5115),(ex,.0728,head_d*.5165),(ex+side*eye_rx*1.05,.0640,head_d*.5115)],.00112,HAIR)

# The anatomical shell already carries most of the bridge. Only the tip, alae and columella are added.
add_sphere(HEAD,'NoseTipSoftV42',(0,-.044,head_d*.545),(.0102,.0089,.0064),SKIN,24,14)
add_sphere(HEAD,'ColumellaSoftV42',(0,-.053,head_d*.541),(.0033,.0047,.0032),SKIN,18,10)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV42_{side}',(side*.0101,-.050,head_d*.537),(.0053,.0048,.0039),SKIN,18,10)
 add_sphere(HEAD,f'NostrilV42_{side}',(side*.0070,-.052,head_d*.543),(.00165,.00115,.00095),FACE_DARK,12,8)

# Use shallow lip volumes instead of multiple heavy curves. This keeps the mouth readable under gameplay lighting.
for side in(-1,1):
 add_sphere(HEAD,f'UpperLipVolV42_{side}',(side*.0125,-.0810,head_d*.5415),(.0142,.0043,.0033),LIP,22,12)
add_sphere(HEAD,'LowerLipVolV42',(0,-.0890,head_d*.5410),(.0225,.0049,.0036),LIP,24,12)
add_strand(HEAD,'CupidBowV42',[(-.024,-.0810,head_d*.5415),(0,-.0780,head_d*.5440),(.024,-.0810,head_d*.5415)],.00062,LIP)
add_strand(HEAD,'MouthLineV42',[(-.028,-.0840,head_d*.5430),(0,-.0858,head_d*.5440),(.028,-.0840,head_d*.5430)],.00055,FACE_DARK)

"""
s=s[:a]+face+s[b:]

# The six-lock v4.1 fringe was much better, but still formed a regular row in front view.
# Reduce it to four large directional masses plus three crossing pieces with deliberately uneven tips.
a=s.index('# Hair v4.1:')
b=s.index('# Consolidated ponytail v4.1:',a)
hair="""# Hair v4.2: four broad side-swept masses with irregular tips and a cleaner forehead opening.
add_sphere(HEAD,'HairBackV42',(0,.031,-head_d*.366),(head_w*.505,.127,head_d*.452),HAIR,48,32)
add_sphere(HEAD,'HairCrownV42',(-.022,.120,-head_d*.212),(head_w*.467,.059,head_d*.320),HAIR,46,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV42_{side}',(side*head_w*.404,.020,-.032),(head_w*.077,.072,head_d*.129),HAIR,30,20)

primary=[
 (-.118,-.090,-.046,.057,.151,.045,.0060),
 (-.070,-.036,.016,.086,.164,.047,.0056),
 (-.012,.030,.076,.073,.163,.045,.0053),
 (.050,.086,.125,.044,.151,.041,.0052),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(primary):
 pts=[(rx,ry,-head_d*.018),(mx,ry-.022,head_d*.165),((mx+tx)*.5,.113,head_d*.368),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'ForeheadLockV42_{i}',pts,[w*.58,w,w*.58,tipw],[.0080,.0092,.0068,.0026],HAIR_HI if i in(0,3) else HAIR,8)

cross=[
 (-.108,-.035,.079,.0180),
 (-.060,.028,.090,.0170),
 (-.002,.086,.065,.0155),
]
for i,(rx,tx,ty,w) in enumerate(cross):
 pts=[(rx,.148,head_d*.004),((rx+tx)*.5,.122,head_d*.294),(tx,.096,head_d*.446),(tx,ty,head_d*.520)]
 add_lock_mesh(HEAD,f'FringeLayerV42_{i}',pts,[w*.86,w,w*.62,.0035],[.0048,.0050,.0038,.0019],HAIR_HI if i in(0,2) else HAIR,8)

for i,(rx,tx,ty) in enumerate(((-.096,-.058,.071),(-.030,.018,.085),(.042,.096,.057))):
 add_strand(HEAD,f'BangWispV42_{i}',[(rx,.140,head_d*.018),((rx+tx)*.5,.112,head_d*.324),(tx,ty,head_d*.524)],.00058,HAIR_HI if i!=1 else HAIR)

for side in(-1,1):
 pts=[(side*head_w*.346,.083,-.012),(side*head_w*.390,.014,head_d*.069),(side*head_w*.402,-.138,head_d*.004),(side*head_w*.368,-.315,-.032)]
 add_lock_mesh(HEAD,f'FaceLockV42_{side}',pts,[.018,.021,.012,.0031],[.0047,.0050,.0036,.0019],HAIR,6)
 add_strand(HEAD,f'FaceWispV42_{side}',[(side*head_w*.378,.070,-.008),(side*head_w*.420,-.038,head_d*.034),(side*head_w*.410,-.220,-.008),(side*head_w*.390,-.425,-.032)],.00058,HAIR_HI)

"""
s=s[:a]+hair+s[b:]

# Keep the ponytail behind the body and offset it to the heroine's right.
# V4.1 consolidated the strands, but the lower half still crossed the leg silhouette in front view.
a=s.index('# Consolidated ponytail v4.1:')
b=s.index('# === LIMBS ===',a)
pony="""# Offset rear ponytail v4.2: nine broad locks sweep right and remain behind the torso/legs.
add_sphere(HEAD,'PonyRootV42',(.028,.152,-head_d*.425),(.082,.064,.069),HAIR,34,24)
add_box(HEAD,'HairTieV42',(.030,.147,-head_d*.486),(.090,.022,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(9):
 lane=(i-4)/4
 sweep=.075+.018*(i%3)
 zoff=((i%3)-1)*.010-.009*abs(lane)
 endx=.165+lane*.220+sweep
 pts=[
  (lane*.046+.028,.150,-head_d*.520+zoff),
  (lane*.068+.045,.030,-head_d*.760+zoff),
  (lane*.100+.075,-.245,-.535+zoff*.40),
  (lane*.140+.105,-.610,-.430),
  (lane*.175+.135,-1.000,-.335),
  (endx,-1.390,-.245),
  (endx+.030,-1.660-(i%3)*.018,-.175)
 ]
 base_w=.076-.014*abs(lane)
 add_lock_mesh(PONY,f'PonyLockV42_{i}',pts,[base_w*.68,base_w,base_w*1.02,base_w*.92,base_w*.70,base_w*.36,.0060],[.015,.018,.019,.017,.013,.008,.0035],HAIR_HI if i in(2,6) else HAIR,8)
for i in range(4):
 lane=(i-1.5)/1.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV42_{i}',[(lane*.040+.028,.148,-head_d*.522),(lane*.070+.050+sgn*.008,-.060,-head_d*.790),(lane*.120+.095-sgn*.010,-.440,-.500),(lane*.190+.145+sgn*.012,-.930,-.340),(lane*.245+.190,-1.645-(i%2)*.025,-.165)],.00072+(i%2)*.00010,HAIR_HI if i in(0,3) else HAIR)

"""
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V42: volumetric portrait, irregular swept fringe and offset rear ponytail')
