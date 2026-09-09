from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V41' in s:
    print('Blender heroine generator already carries REFERENCE_V41')
    raise SystemExit(0)
if '# REFERENCE_V40' not in s:
    raise SystemExit('REFERENCE_V40 generator required before v4.1')

s=s.replace(
    '# REFERENCE_V40: narrower shoulder flow and split couture skirt that exposes the long-leg silhouette.',
    '# REFERENCE_V40: narrower shoulder flow and split couture skirt that exposes the long-leg silhouette.\n# REFERENCE_V41: sculptural face, swept fringe and consolidated ponytail for a less procedural silhouette.',
    1,
)

# Replace the v3.9 portrait with a more sculptural adult face. The audit showed that the
# black eye/lash curves still read like 2D ink at close range, so line weight is reduced and
# the 3D nose/lip volumes carry more of the portrait.
a=s.index('# Anatomy v3.9:')
b=s.index('# Hair v3.9:',a)
face="""# Anatomy v4.1: smaller inset eyes and stronger 3D central facial volumes.
face_front=head_d*.512
eye_y=.0315
eye_x=head_w*.142
eye_rx=head_w*.085
eye_ry=.0104
eye_tilt=.0025
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV41_{side}',(ex,eye_y,head_d*.427),(head_w*.072,.015,head_d*.056),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeOpeningV41_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0024,SCLERA,36,side,eye_tilt)
 add_sphere(HEAD,f'IrisV41_{side}',(ex,eye_y+.0006,face_front+.0056),(head_w*.034,.0088,.0028),IRIS,30,18)
 add_sphere(HEAD,f'PupilV41_{side}',(ex,eye_y+.0005,face_front+.0082),(head_w*.0122,.0046,.0018),PUPIL,22,12)
 add_sphere(HEAD,f'EyeLightV41_{side}',(ex-side*head_w*.0080,eye_y+.0043,face_front+.0100),(head_w*.0044,.0020,.0010),SCLERA,12,8)
 inner=ex-side*eye_rx*.96;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 # Only a fine upper lash is dark; lower contours are skin-colored so the eye no longer reads as inked-on.
 add_strand(HEAD,f'UpperLidV41_{side}',[(inner,inner_y+.0008,face_front+.0028),(ex,eye_y+.0105,face_front+.0057),(outer,outer_y+.0010,face_front+.0029)],.00082,SKIN)
 add_strand(HEAD,f'LowerLidV41_{side}',[(inner,inner_y-.0005,face_front+.0023),(ex,eye_y-.0060,face_front+.0031),(outer,outer_y-.0005,face_front+.0023)],.00055,SKIN)
 add_strand(HEAD,f'UpperLashV41_{side}',[(inner,inner_y+.0018,face_front+.0061),(ex,eye_y+.0113,face_front+.0078),(outer,outer_y+.0020,face_front+.0063)],.00108,HAIR)
 add_strand(HEAD,f'LashWingV41_{side}',[(outer,outer_y+.0020,face_front+.0063),(outer+side*head_w*.018,outer_y+.0066,face_front+.0069)],.00082,HAIR)
 # Slimmer brows sit close to the orbital ridge.
 add_strand(HEAD,f'BrowV41_{side}',[(ex-side*eye_rx*.88,.0655,head_d*.512),(ex,.0725,head_d*.517),(ex+side*eye_rx*1.05,.0640,head_d*.512)],.00122,HAIR)

# Nose projection is carried by skin geometry rather than a dark center line.
add_sphere(HEAD,'NoseBridgeSoftV41',(0,-.004,head_d*.526),(.0072,.039,.0065),SKIN,24,14)
add_sphere(HEAD,'NoseTipSoftV41',(0,-.044,head_d*.546),(.0107,.0092,.0068),SKIN,24,14)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV41_{side}',(side*.0104,-.050,head_d*.538),(.0056,.0050,.0042),SKIN,18,10)
 add_sphere(HEAD,f'NostrilV41_{side}',(side*.0072,-.052,head_d*.544),(.0020,.00135,.0011),FACE_DARK,12,8)
add_strand(HEAD,'NoseUndersideV41',[(-.0095,-.050,head_d*.541),(0,-.054,head_d*.545),(.0095,-.050,head_d*.541)],.00055,FACE_DARK)

# Slightly fuller lips and a shorter mouth line give a softer key-art expression.
add_strand(HEAD,'UpperLipLeftV41',[(-.029,-.080,head_d*.538),(-.0145,-.0755,head_d*.543),(0,-.080,head_d*.544)],.00178,LIP)
add_strand(HEAD,'UpperLipRightV41',[(0,-.080,head_d*.544),(.0145,-.0755,head_d*.543),(.029,-.080,head_d*.538)],.00178,LIP)
add_strand(HEAD,'MouthLineV41',[(-.029,-.0835,head_d*.541),(0,-.0860,head_d*.544),(.029,-.0835,head_d*.541)],.00078,FACE_DARK)
add_strand(HEAD,'LowerLipV41',[(-.023,-.0875,head_d*.539),(0,-.0930,head_d*.543),(.023,-.0875,head_d*.539)],.00152,LIP)

"""
s=s[:a]+face+s[b:]

# Replace comb-like fringe with six broad diagonal layers. Each tip is displaced laterally,
# producing a side-swept silhouette rather than evenly spaced vertical teeth.
a=s.index('# Hair v3.9:')
b=s.index('# Preserve the successful separated high ponytail silhouette',a)
hair="""# Hair v4.1: asymmetric side-swept fringe with fewer, broader locks.
add_sphere(HEAD,'HairBackV41',(0,.031,-head_d*.365),(head_w*.505,.127,head_d*.452),HAIR,48,32)
add_sphere(HEAD,'HairCrownV41',(-.020,.119,-head_d*.210),(head_w*.466,.058,head_d*.318),HAIR,46,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV41_{side}',(side*head_w*.405,.021,-.031),(head_w*.078,.073,head_d*.130),HAIR,30,20)

primary=[
 (-.120,-.097,-.060,.059,.150,.029,.0046),
 (-.085,-.058,-.020,.071,.159,.030,.0044),
 (-.046,-.018,.020,.081,.164,.028,.0041),
 (-.004,.028,.062,.077,.163,.030,.0044),
 (.040,.072,.101,.061,.156,.031,.0047),
 (.080,.105,.128,.043,.148,.027,.0043),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(primary):
 pts=[(rx,ry,-head_d*.016),(mx,ry-.020,head_d*.170),((mx+tx)*.5,.114,head_d*.370),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'ForeheadLockV41_{i}',pts,[w*.54,w,w*.56,tipw],[.0068,.0080,.0060,.0024],HAIR_HI if i in(0,5) else HAIR,6)

# One long crossing layer establishes the part direction; finer wisps break the edge.
for i,(rx,tx,ty) in enumerate(((-.105,-.050,.080),(-.065,.005,.089),(-.020,.055,.079),(.030,.095,.060))):
 pts=[(rx,.148,head_d*.006),((rx+tx)*.5,.123,head_d*.292),(tx,.098,head_d*.448),(tx,ty,head_d*.520)]
 add_lock_mesh(HEAD,f'FringeLayerV41_{i}',pts,[.0135,.0150,.0095,.0032],[.0040,.0044,.0035,.0018],HAIR_HI if i in(0,3) else HAIR,6)
for i,(rx,tx,ty) in enumerate(((-.100,-.070,.069),(-.048,-.006,.080),(.006,.054,.072),(.058,.105,.052))):
 add_strand(HEAD,f'BangWispV41_{i}',[(rx,.140,head_d*.018),((rx+tx)*.5,.113,head_d*.325),(tx,ty,head_d*.524)],.00068,HAIR_HI if i in(0,3) else HAIR)

for side in(-1,1):
 pts=[(side*head_w*.345,.083,-.010),(side*head_w*.392,.012,head_d*.073),(side*head_w*.407,-.142,head_d*.008),(side*head_w*.370,-.325,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV41_{side}',pts,[.019,.022,.013,.0033],[.0048,.0052,.0038,.0020],HAIR,6)
 add_strand(HEAD,f'FaceWispV41_{side}',[(side*head_w*.379,.071,-.006),(side*head_w*.424,-.040,head_d*.037),(side*head_w*.414,-.228,-.005),(side*head_w*.392,-.440,-.030)],.00068,HAIR_HI)

"""
s=s[:a]+hair+s[b:]

# Consolidate the long ponytail. The v4.0 front audit exposed the legs but also revealed
# nineteen thin locks as a black wire curtain. Eleven wider ribbons preserve the measured
# ponytail length while reading as hair mass; only six flyaways remain.
a=s.index('# Preserve the successful separated high ponytail silhouette')
b=s.index('# === LIMBS ===',a)
pony="""# Consolidated ponytail v4.1: layered mass with a gentle rightward sweep.
add_sphere(HEAD,'PonyRootV41',(.010,.152,-head_d*.420),(.082,.064,.068),HAIR,34,24)
add_box(HEAD,'HairTieV41',(.010,.147,-head_d*.480),(.090,.022,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(11):
 lane=(i-5)/5
 sweep=.035+(.018 if i%2 else -.006)
 zoff=((i%3)-1)*.010-.008*abs(lane)
 endx=lane*.235+sweep
 pts=[
  (lane*.050+.010,.150,-head_d*.510+zoff),
  (lane*.074+.018,.030,-head_d*.744+zoff),
  (lane*.108+.028,-.245,-.490+zoff*.40),
  (lane*.150+.040,-.610,-.355),
  (lane*.192+.050,-1.000,-.228),
  (endx,-1.390,-.112),
  (endx*.97,-1.675-(i%3)*.018,-.028)
 ]
 base_w=.070-.012*abs(lane)
 add_lock_mesh(PONY,f'PonyLockV41_{i}',pts,[base_w*.66,base_w,base_w*1.02,base_w*.92,base_w*.70,base_w*.34,.0055],[.014,.017,.018,.016,.012,.007,.0032],HAIR_HI if i in(3,7) else HAIR,6)
for i in range(6):
 lane=(i-2.5)/2.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV41_{i}',[(lane*.044+.010,.148,-head_d*.515),(lane*.078+.020+sgn*.010,-.060,-head_d*.775),(lane*.138+.040-sgn*.012,-.440,-.440),(lane*.214+.060+sgn*.015,-.930,-.260),(lane*.285+.060,-1.660-(i%3)*.024,-.020)],.00088+(i%2)*.00012,HAIR_HI if i in(0,5) else HAIR)

"""
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V41: sculptural portrait, swept fringe and consolidated ponytail')
