from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V43' in s:
    print('Blender heroine generator already carries REFERENCE_V43')
    raise SystemExit(0)
if '# REFERENCE_V42' not in s:
    raise SystemExit('REFERENCE_V42 generator required before v4.3')

s=s.replace(
    '# REFERENCE_V42: portrait depth pass with volumetric lips, softer orbital detail and an offset rear ponytail.',
    '# REFERENCE_V42: portrait depth pass with volumetric lips, softer orbital detail and an offset rear ponytail.\n# REFERENCE_V43: softer adult portrait, blunt side-swept fringe and a true side-flow ponytail.',
    1,
)

s=s.replace(
    "SKIN=material('Skin',(0.69,0.49,0.45),0,.62)",
    "SKIN=material('Skin',(0.68,0.48,0.45),0,.54)",
    1,
)

a=s.index('# Anatomy v4.2:')
b=s.index('# Hair v4.2:',a)
face="""# Anatomy v4.3: adult portrait with continuous lips and subtle nose definition.
face_front=head_d*.512
eye_y=.0315
eye_x=head_w*.141
eye_rx=head_w*.091
eye_ry=.0114
eye_tilt=.0028
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV43_{side}',(ex,eye_y,head_d*.426),(head_w*.076,.0155,head_d*.058),SCLERA,36,22)
 add_almond_surface(HEAD,f'EyeOpeningV43_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0025,SCLERA,38,side,eye_tilt)
 add_sphere(HEAD,f'IrisV43_{side}',(ex,eye_y+.0005,face_front+.0057),(head_w*.0385,.0093,.0029),IRIS,32,18)
 add_sphere(HEAD,f'PupilV43_{side}',(ex,eye_y+.0004,face_front+.0083),(head_w*.0132,.0048,.0018),PUPIL,22,12)
 add_sphere(HEAD,f'EyeLightV43_{side}',(ex-side*head_w*.0083,eye_y+.0044,face_front+.0102),(head_w*.0046,.0020,.0010),SCLERA,12,8)
 inner=ex-side*eye_rx*.96;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_sphere(HEAD,f'UpperLidSoftV43_{side}',(ex,eye_y+.0106,face_front-.0012),(head_w*.073,.0055,.0046),SKIN,24,12)
 add_sphere(HEAD,f'LowerLidSoftV43_{side}',(ex,eye_y-.0066,face_front-.0019),(head_w*.066,.0040,.0034),SKIN,24,12)
 add_strand(HEAD,f'UpperLashV43_{side}',[(inner,inner_y+.0017,face_front+.0062),(ex,eye_y+.0119,face_front+.0079),(outer,outer_y+.0019,face_front+.0064)],.00084,HAIR)
 add_strand(HEAD,f'LashWingV43_{side}',[(outer,outer_y+.0019,face_front+.0064),(outer+side*head_w*.015,outer_y+.0060,face_front+.0069)],.00062,HAIR)
 add_strand(HEAD,f'BrowV43_{side}',[(ex-side*eye_rx*.88,.0655,head_d*.5115),(ex,.0727,head_d*.5162),(ex+side*eye_rx*1.05,.0640,head_d*.5115)],.00108,HAIR)

add_sphere(HEAD,'NoseTipSoftV43',(0,-.044,head_d*.545),(.0100,.0087,.0063),SKIN,24,14)
add_sphere(HEAD,'ColumellaSoftV43',(0,-.053,head_d*.541),(.0032,.0045,.0031),SKIN,18,10)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV43_{side}',(side*.0100,-.050,head_d*.537),(.0052,.0047,.0038),SKIN,18,10)
 add_sphere(HEAD,f'NostrilV43_{side}',(side*.0070,-.052,head_d*.543),(.00155,.00105,.00090),FACE_DARK,12,8)
add_strand(HEAD,'NoseUndersideV43',[(-.0090,-.0510,head_d*.5415),(0,-.0540,head_d*.5440),(.0090,-.0510,head_d*.5415)],.00036,FACE_DARK)

add_flow_ribbon(HEAD,'UpperLipV43',[(-.028,-.0815,head_d*.5420),(-.014,-.0785,head_d*.5435),(0,-.0805,head_d*.5442),(.014,-.0785,head_d*.5435),(.028,-.0815,head_d*.5420)],[.0046,.0064,.0054,.0064,.0046],.0032,LIP)
add_flow_ribbon(HEAD,'LowerLipV43',[(-.025,-.0865,head_d*.5415),(-.012,-.0900,head_d*.5428),(0,-.0915,head_d*.5434),(.012,-.0900,head_d*.5428),(.025,-.0865,head_d*.5415)],[.0038,.0058,.0062,.0058,.0038],.0030,LIP)
add_strand(HEAD,'MouthLineV43',[(-.027,-.0840,head_d*.5430),(0,-.0853,head_d*.5441),(.027,-.0840,head_d*.5430)],.00042,FACE_DARK)

"""
s=s[:a]+face+s[b:]

a=s.index('# Hair v4.2:')
b=s.index('# Offset rear ponytail v4.2:',a)
hair="""# Hair v4.3: three blunt side-swept locks with a clean asymmetric forehead opening.
add_sphere(HEAD,'HairBackV43',(0,.031,-head_d*.366),(head_w*.505,.127,head_d*.452),HAIR,48,32)
add_sphere(HEAD,'HairCrownV43',(-.024,.120,-head_d*.212),(head_w*.468,.059,head_d*.320),HAIR,46,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV43_{side}',(side*head_w*.404,.020,-.032),(head_w*.077,.072,head_d*.129),HAIR,30,20)

primary=[
 (-.122,-.092,-.050,.057,.151,.056,.0130),
 (-.072,-.030,.030,.084,.164,.058,.0110),
 (-.008,.046,.120,.046,.154,.054,.0135),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(primary):
 pts=[(rx,ry,-head_d*.020),(mx,ry-.020,head_d*.162),((mx+tx)*.5,.114,head_d*.360),(tx,ty,head_d*.516)]
 add_lock_mesh(HEAD,f'ForeheadLockV43_{i}',pts,[w*.62,w,w*.64,tipw],[.0090,.0100,.0074,.0038],HAIR_HI if i in(0,2) else HAIR,10)

for i,(rx,tx,ty,w) in enumerate(((-.102,.002,.083,.020),(-.040,.090,.060,.018))):
 pts=[(rx,.148,head_d*.002),((rx+tx)*.5,.122,head_d*.288),(tx,.098,head_d*.440),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'FringeLayerV43_{i}',pts,[w*.90,w,w*.68,.0070],[.0054,.0058,.0043,.0026],HAIR_HI if i==1 else HAIR,8)

for i,(rx,tx,ty) in enumerate(((-.092,-.042,.071),(.015,.106,.054))):
 add_strand(HEAD,f'BangWispV43_{i}',[(rx,.139,head_d*.016),((rx+tx)*.5,.112,head_d*.320),(tx,ty,head_d*.522)],.00052,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.346,.083,-.012),(side*head_w*.390,.014,head_d*.068),(side*head_w*.401,-.136,head_d*.002),(side*head_w*.366,-.310,-.034)]
 add_lock_mesh(HEAD,f'FaceLockV43_{side}',pts,[.018,.021,.012,.0032],[.0047,.0050,.0036,.0019],HAIR,6)
 add_strand(HEAD,f'FaceWispV43_{side}',[(side*head_w*.378,.070,-.008),(side*head_w*.418,-.038,head_d*.032),(side*head_w*.407,-.218,-.010),(side*head_w*.388,-.418,-.034)],.00054,HAIR_HI)

"""
s=s[:a]+hair+s[b:]

a=s.index('# Offset rear ponytail v4.2:')
b=s.index('# === LIMBS ===',a)
pony="""# True side-flow ponytail v4.3: seven broad locks bend right while staying behind the body.
add_sphere(HEAD,'PonyRootV43',(.036,.152,-head_d*.425),(.082,.064,.069),HAIR,34,24)
add_box(HEAD,'HairTieV43',(.040,.147,-head_d*.486),(.090,.022,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(7):
 lane=(i-3)/3
 zoff=((i%3)-1)*.010-.008*abs(lane)
 endx=.300+lane*.165
 pts=[
  (lane*.036+.036,.150,-head_d*.520+zoff),
  (lane*.050+.080,.030,-head_d*.765+zoff),
  (lane*.070+.145,-.245,-.555+zoff*.40),
  (lane*.090+.205,-.610,-.455),
  (lane*.110+.250,-1.000,-.360),
  (endx,-1.390,-.270),
  (endx+.035,-1.660-(i%3)*.018,-.190)
 ]
 base_w=.088-.016*abs(lane)
 add_lock_mesh(PONY,f'PonyLockV43_{i}',pts,[base_w*.70,base_w,base_w*1.04,base_w*.94,base_w*.72,base_w*.40,.0080],[.017,.020,.021,.018,.014,.009,.0040],HAIR_HI if i in(1,5) else HAIR,10)
for i in range(3):
 lane=(i-1)
 add_strand(PONY,f'PonyFlyV43_{i}',[(lane*.028+.036,.148,-head_d*.522),(lane*.045+.085,-.060,-head_d*.792),(lane*.070+.150,-.440,-.515),(lane*.100+.235,-.930,-.370),(lane*.120+.320,-1.645-(i%2)*.025,-.180)],.00066+(i%2)*.00008,HAIR_HI if i!=1 else HAIR)

"""
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V43: softer portrait, blunt swept fringe and true side-flow ponytail')
