from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V39' in s:
    print('Blender heroine generator already carries REFERENCE_V39')
    raise SystemExit(0)
if '# REFERENCE_V38' not in s:
    raise SystemExit('REFERENCE_V38 generator required before v3.9')

s=s.replace(
    '# REFERENCE_V38: tilted expressive almond eyes and stronger central portrait cues.',
    '# REFERENCE_V38: tilted expressive almond eyes and stronger central portrait cues.\n# REFERENCE_V39: portrait de-doll pass with slimmer eyes, stronger nose/lips and finer asymmetric fringe.',
    1,
)

# The v3.8 audit still read too doll-like at iPhone distance: eye whites dominated the face,
# the nose/lips collapsed into dots, and the fringe formed five chunky fingers. Rebuild only
# the visible portrait assembly while preserving the measured skull envelope.
a=s.index('# Anatomy v3.8:')
b=s.index('# Hair v3.6:',a)
face="""# Anatomy v3.9: narrower cinematic eyes, clearer nose/lips, and a softer adult portrait read.
face_front=head_d*.512
eye_y=.031
eye_x=head_w*.137
eye_rx=head_w*.098
eye_ry=.0132
eye_tilt=.0032
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV39_{side}',(ex,eye_y,head_d*.425),(head_w*.082,.017,head_d*.064),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeOpeningV39_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0028,SCLERA,34,side,eye_tilt)
 # Darker/larger iris coverage keeps the eyes expressive without the white-heavy doll stare.
 add_sphere(HEAD,f'IrisV39_{side}',(ex,eye_y+.0008,face_front+.0057),(head_w*.040,.0106,.0030),IRIS,30,18)
 add_sphere(HEAD,f'PupilV39_{side}',(ex,eye_y+.0008,face_front+.0085),(head_w*.0148,.0055,.0020),PUPIL,22,12)
 add_sphere(HEAD,f'EyeLightV39_{side}',(ex-side*head_w*.0095,eye_y+.0054,face_front+.0105),(head_w*.0058,.0026,.0012),SCLERA,12,8)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.01
 inner_y=eye_y-eye_tilt
 outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV39_{side}',[(inner,inner_y+.0010,face_front+.0027),(ex,eye_y+.0134,face_front+.0058),(outer,outer_y+.0012,face_front+.0028)],.00120,SKIN)
 add_strand(HEAD,f'LowerLidV39_{side}',[(inner,inner_y-.0008,face_front+.0022),(ex,eye_y-.0080,face_front+.0032),(outer,outer_y-.0008,face_front+.0022)],.00068,SKIN)
 add_strand(HEAD,f'UpperLashV39_{side}',[(inner,inner_y+.0025,face_front+.0066),(ex,eye_y+.0146,face_front+.0082),(outer,outer_y+.0027,face_front+.0068)],.00175,HAIR)
 add_strand(HEAD,f'LashWingV39_{side}',[(outer,outer_y+.0027,face_front+.0068),(outer+side*head_w*.026,outer_y+.0090,face_front+.0074)],.00128,HAIR)
 add_strand(HEAD,f'LowerLashV39_{side}',[(inner,inner_y,face_front+.0048),(ex,eye_y-.0072,face_front+.0051),(outer,outer_y,face_front+.0048)],.00038,HAIR)
 # Lower, flatter brows improve the mature key-art expression and reduce forehead emptiness.
 add_strand(HEAD,f'BrowV39_{side}',[(ex-side*eye_rx*.86,.067,head_d*.511),(ex,.076,head_d*.517),(ex+side*eye_rx*1.06,.065,head_d*.511)],.00162,HAIR)

# Readable front/profile nose: preserve the connected shell but give bridge, tip and nostrils distinct planes.
add_strand(HEAD,'NoseBridgeCueV39',[(0,.035,head_d*.516),(-.001,-.005,head_d*.523),(-.002,-.033,head_d*.531)],.00055,FACE_DARK)
add_sphere(HEAD,'NoseTipSoftV39',(0,-.043,head_d*.536),(.0105,.0088,.0057),SKIN,22,14)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV39_{side}',(side*.0108,-.050,head_d*.530),(.0058,.0051,.0040),SKIN,18,10)
 add_sphere(HEAD,f'NostrilV39_{side}',(side*.0075,-.052,head_d*.536),(.0026,.0018,.0014),FACE_DARK,12,8)
add_strand(HEAD,'NoseUndersideV39',[(-.0105,-.050,head_d*.534),(0,-.055,head_d*.538),(.0105,-.050,head_d*.534)],.00088,FACE_DARK)

# Slightly fuller, lower lips survive normal gameplay distance without reading as a painted dot.
add_strand(HEAD,'UpperLipLeftV39',[(-.032,-.080,head_d*.534),(-.016,-.075,head_d*.538),(0,-.080,head_d*.539)],.00162,LIP)
add_strand(HEAD,'UpperLipRightV39',[(0,-.080,head_d*.539),(.016,-.075,head_d*.538),(.032,-.080,head_d*.534)],.00162,LIP)
add_strand(HEAD,'MouthLineV39',[(-.032,-.084,head_d*.537),(0,-.087,head_d*.540),(.032,-.084,head_d*.537)],.00115,FACE_DARK)
add_strand(HEAD,'LowerLipV39',[(-.025,-.088,head_d*.535),(0,-.094,head_d*.538),(.025,-.088,head_d*.535)],.00136,LIP)
for side in(-1,1):
 add_sphere(HEAD,f'MouthCornerV39_{side}',(side*.032,-.084,head_d*.537),(.0019,.0015,.0012),FACE_DARK,10,6)

"""
s=s[:a]+face+s[b:]

# Replace the chunky five-finger fringe and thick vertical cheek bars with a finer, layered,
# asymmetric silhouette. Ponytail geometry is intentionally preserved.
a=s.index('# Hair v3.6:')
b=s.index('# Preserve the successful separated high ponytail silhouette',a)
hair="""# Hair v3.9: compact scalp mass, seven finer swept fringe locks, and slimmer cheek framing.
add_sphere(HEAD,'HairBackV39',(0,.030,-head_d*.365),(head_w*.508,.128,head_d*.452),HAIR,48,32)
add_sphere(HEAD,'HairCrownV39',(-.014,.118,-head_d*.208),(head_w*.468,.058,head_d*.320),HAIR,46,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV39_{side}',(side*head_w*.407,.020,-.031),(head_w*.082,.074,head_d*.132),HAIR,30,20)

# Fine layered fringe: most tips stop around brow height, leaving the eye line readable.
primary=[
 (-.118,-.100,-.072,.054,.150,.038,.0060),
 (-.088,-.069,-.039,.068,.157,.037,.0055),
 (-.054,-.033,-.004,.080,.162,.034,.0050),
 (-.020,.004,.030,.084,.164,.032,.0048),
 (.018,.039,.064,.076,.160,.034,.0052),
 (.054,.073,.096,.061,.154,.036,.0058),
 (.086,.101,.120,.045,.147,.032,.0055),
]
for i,(rx,mx,tx,ty,ry,w,tipw) in enumerate(primary):
 pts=[(rx,ry,-head_d*.014),(mx,ry-.022,head_d*.160),((mx+tx)*.5,.112,head_d*.365),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'ForeheadLockV39_{i}',pts,[w*.58,w,w*.60,tipw],[.0075,.0090,.0070,.0028],HAIR_HI if i in(0,6) else HAIR,6)

# Crossing ribbons create a continuous side-part sweep without restoring the chunky helmet fringe.
secondary=[(-.108,-.077,.072),(-.074,-.043,.083),(-.036,.000,.090),(.010,.048,.081),(.050,.088,.067),(.082,.114,.052)]
for i,(rx,tx,ty) in enumerate(secondary):
 pts=[(rx,.146,head_d*.008),((rx+tx)*.5,.121,head_d*.285),(tx,.096,head_d*.444),(tx,ty,head_d*.520)]
 add_lock_mesh(HEAD,f'FringeLayerV39_{i}',pts,[.015,.017,.011,.0038],[.0045,.0050,.0040,.0020],HAIR_HI if i in(0,5) else HAIR,6)
for i,(rx,tx,ty) in enumerate(((-.104,-.088,.061),(-.062,-.040,.074),(-.016,.010,.083),(.036,.064,.070),(.078,.108,.054))):
 add_strand(HEAD,f'BangWispV39_{i}',[(rx,.139,head_d*.020),((rx+tx)*.5,.112,head_d*.320),(tx,ty,head_d*.523)],.00082,HAIR_HI if i in(0,4) else HAIR)

# Face framing is deliberately slim and bowed away from the cheeks; the v3.8 audit showed dark vertical bars.
for side in(-1,1):
 pts=[(side*head_w*.344,.082,-.010),(side*head_w*.394,.010,head_d*.075),(side*head_w*.410,-.145,head_d*.010),(side*head_w*.372,-.335,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV39_{side}',pts,[.022,.025,.016,.0038],[.0055,.0060,.0045,.0022],HAIR,6)
 add_strand(HEAD,f'FaceWispV39_{side}',[(side*head_w*.380,.070,-.006),(side*head_w*.430,-.040,head_d*.040),(side*head_w*.420,-.235,-.004),(side*head_w*.395,-.455,-.030)],.00085,HAIR_HI)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V39: mature portrait proportions and finer asymmetric fringe')
