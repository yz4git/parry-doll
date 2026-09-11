from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V119' in s:
    print('Blender heroine generator already carries REFERENCE_V119')
    raise SystemExit(0)
if '# REFERENCE_V118' not in s:
    raise SystemExit('REFERENCE_V118 generator required before v11.9')

marker='# REFERENCE_V118: reference-locked adult portrait pass narrows the lower face, strengthens brow/bridge/tip/columella profile planes and upgrades the cinematic almond-eye treatment.'
if marker not in s:
    raise SystemExit('v11.9 REFERENCE_V118 marker anchor missing')
s=s.replace(marker,marker+'\n# REFERENCE_V119: visual-audit portrait pass boosts iPhone-scale eye contrast, shortens the lower face, exaggerates the key-art profile and adds layered asymmetric brow-length bangs.',1)

s=s.replace("FACE118_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v118.json')","FACE119_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v119.json')",1)
s=s.replace("with open(FACE118_PATH,'r',encoding='utf-8') as f:FACE118=json.load(f)","with open(FACE119_PATH,'r',encoding='utf-8') as f:FACE119=json.load(f)",1)
s=s.replace('FACE118','FACE119')
s=s.replace('def add_reference_head_v118(','def add_reference_head_v119(',1)
s=s.replace("add_reference_head_v118(HEAD,'HeadShellV118',SKIN,112)","add_reference_head_v119(HEAD,'HeadShellV119',SKIN,128)",1)

old="""# v10.0 adult-scale almond eyes: narrower apertures, lower iris coverage and subtler lids remove the child/doll read.
face_front=.0974
eye_y=.0318
eye_x=.0458*FACE119['frontal']['eyeSpacing']
eye_rx=.0292*FACE119['frontal']['eyeSize']
eye_ry=.01055*FACE119['frontal']['eyeSize']
eye_tilt=.00235
iris_scale=FACE119['surface']['irisScale']
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV118_{side}',ex,eye_y,.10182,eye_rx,eye_ry,.00110,SCLERA,80,side,eye_tilt*.72)
 add_ellipse_surface(HEAD,f'IrisV118_{side}',ex,eye_y-.00015,.10282,.00965*iris_scale,.00810*iris_scale,IRIS_INNER,44)
 add_ellipse_surface(HEAD,f'PupilV118_{side}',ex,eye_y-.00030,.10314,.00275*iris_scale,.00330*iris_scale,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV118_{side}',ex-side*.00315,eye_y+.00275,.10330,.00105,.00082,SCLERA,18)
 inner=ex-side*eye_rx*.96;outer=ex+side*eye_rx*1.03
 add_strand(HEAD,f'UpperLidRimV118_{side}',[(inner+side*.0018,eye_y-eye_tilt+.0010,.10205),(ex,eye_y+.0095,.10252),(outer-side*.0018,eye_y+eye_tilt+.0010,.10210)],.00030*FACE119['surface']['upperLidThickness'],SKIN)
 add_strand(HEAD,f'UpperLashV118_{side}',[(inner,eye_y-eye_tilt+.0006,.10266),(ex,eye_y+.0103,.10316),(outer,eye_y+eye_tilt+.0006,.10271)],.00062,HAIR)
 add_strand(HEAD,f'UpperLidFoldV118_{side}',[(inner+side*.0035,eye_y-eye_tilt+.0025,.10215),(ex,eye_y+.0124,.10255),(outer-side*.0035,eye_y+eye_tilt+.0025,.10215)],.00011,FACE_DARK)
 add_strand(HEAD,f'LowerLidV118_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0001,.10205),(ex,eye_y-.0072,.10227),(outer-side*.0035,eye_y+eye_tilt-.0001,.10205)],.000045,FACE_DARK)
 add_strand(HEAD,f'BrowV118_{side}',[(ex-side*.0235,.0645,.1018),(ex,.0698,.1023),(ex+side*.0255,.0630,.1019)],.00038,HAIR)
"""
new="""# v11.9 key-art eyes: the white aperture stays adult-shaped, but a dark complete contour and larger warm iris
# preserve the expressive anime-real portrait read at actual iPhone gameplay distance.
face_front=.0974
eye_y=.0295
eye_x=.0450*FACE119['frontal']['eyeSpacing']
eye_rx=.0308*FACE119['frontal']['eyeSize']
eye_ry=.0109*FACE119['frontal']['eyeSize']
eye_tilt=.00315
iris_scale=FACE119['surface']['irisScale']
eye_contrast=FACE119['surface']['eyeContrast']
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV119_{side}',ex,eye_y,.10310,eye_rx,eye_ry,.00128,SCLERA,96,side,eye_tilt*.74)
 # Dark outer iris first, then a smaller warm inner iris and pupil; this gives a readable limbal ring.
 add_ellipse_surface(HEAD,f'IrisOuterV119_{side}',ex,eye_y-.00025,.10448,.01095*iris_scale,.00905*iris_scale,IRIS,52)
 add_ellipse_surface(HEAD,f'IrisInnerV119_{side}',ex,eye_y-.00005,.10472,.00825*iris_scale,.00655*iris_scale,IRIS_INNER,48)
 add_ellipse_surface(HEAD,f'PupilV119_{side}',ex,eye_y-.00045,.10502,.00305*iris_scale,.00385*iris_scale,PUPIL,36)
 add_ellipse_surface(HEAD,f'EyeLightV119A_{side}',ex-side*.00355,eye_y+.00335,.10520,.00135,.00103,SCLERA,20)
 add_ellipse_surface(HEAD,f'EyeLightV119B_{side}',ex+side*.00205,eye_y+.00105,.10518,.00048,.00040,SCLERA,16)
 inner=ex-side*eye_rx*.965;outer=ex+side*eye_rx*1.035
 # Explicit dark eyelid silhouette. The previous skin-coloured rim disappeared against the face at mobile scale.
 add_strand(HEAD,f'UpperLashV119_{side}',[(inner,eye_y-eye_tilt+.0002,.10402),(ex-side*.0030,eye_y+.01145,.10478),(outer,eye_y+eye_tilt+.0002,.10410)],.00088*eye_contrast,HAIR)
 add_strand(HEAD,f'OuterLashV119_{side}',[(outer-side*.0040,eye_y+eye_tilt+.0015,.10416),(outer+side*.0048,eye_y+eye_tilt+.0042,.10418),(outer+side*.0080,eye_y+eye_tilt+.0030,.10405)],.00044*eye_contrast,HAIR)
 add_strand(HEAD,f'LowerLidV119_{side}',[(inner+side*.0040,eye_y-eye_tilt-.0004,.10372),(ex,eye_y-.00855,.10400),(outer-side*.0030,eye_y+eye_tilt-.0003,.10380)],.00016*eye_contrast,FACE_DARK)
 add_strand(HEAD,f'UpperLidFoldV119_{side}',[(inner+side*.0050,eye_y-eye_tilt+.0038,.10340),(ex,eye_y+.0153,.10375),(outer-side*.0060,eye_y+eye_tilt+.0036,.10342)],.00013,FACE_DARK)
 # Lower, fuller brows match the key-art expression and visually reduce the oversized forehead.
 add_strand(HEAD,f'BrowV119_{side}',[(ex-side*.0240,.0580,.1030),(ex,.0634,.10355),(ex+side*.0265,.0560,.10305)],.00062,HAIR)
"""
if old not in s:
    raise SystemExit('v11.9 eye block anchor missing')
s=s.replace(old,new,1)

old="""add_panel(HEAD,'UpperLipV118_L',[(-.0265*FACE119['frontal']['mouthWidth'],-.0849,.1189),(-.0130,-.0801,.1205),(0,-.0831,.1222),(0,-.0868,.1225),(-.0110,-.0860,.1213),(-.0250*FACE119['frontal']['mouthWidth'],-.0882,.1195)],.00027*FACE119['surface']['lipThickness'],LIP)
add_panel(HEAD,'UpperLipV118_R',[(0,-.0831,.1222),(.0130,-.0801,.1205),(.0265*FACE119['frontal']['mouthWidth'],-.0849,.1189),(.0250*FACE119['frontal']['mouthWidth'],-.0882,.1195),(.0110,-.0860,.1213),(0,-.0868,.1225)],.00027*FACE119['surface']['lipThickness'],LIP)
add_panel(HEAD,'LowerLipV118',[(-.0250*FACE119['frontal']['mouthWidth'],-.0884,.1196),(0,-.0878,.1222),(.0250*FACE119['frontal']['mouthWidth'],-.0884,.1196),(.0210*FACE119['frontal']['mouthWidth'],-.0945,.1194),(0,-.0971,.1208),(-.0210*FACE119['frontal']['mouthWidth'],-.0945,.1194)],.00031*FACE119['surface']['lipThickness'],LIP)
add_strand(HEAD,'MouthSeamV118',[(-.0255,-.0869,.1196),(-.0118,-.0863,.1211),(0,-.0872,.1226),(.0118,-.0863,.1211),(.0255,-.0869,.1196)],.000038,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV118_{side}',side*.0062*FACE119['profile']['noseWidth'],-.0570,.1250,.00165*FACE119['surface']['nostrilScale'],.00058*FACE119['surface']['nostrilScale'],FACE_DARK,18)
"""
new="""add_panel(HEAD,'UpperLipV119_L',[(-.0280*FACE119['frontal']['mouthWidth'],-.0845,.1268),(-.0135,-.0796,.1284),(0,-.0827,.1302),(0,-.0867,.1305),(-.0115,-.0860,.1292),(-.0268*FACE119['frontal']['mouthWidth'],-.0884,.1273)],.00034*FACE119['surface']['lipThickness'],LIP)
add_panel(HEAD,'UpperLipV119_R',[(0,-.0827,.1302),(.0135,-.0796,.1284),(.0280*FACE119['frontal']['mouthWidth'],-.0845,.1268),(.0268*FACE119['frontal']['mouthWidth'],-.0884,.1273),(.0115,-.0860,.1292),(0,-.0867,.1305)],.00034*FACE119['surface']['lipThickness'],LIP)
add_panel(HEAD,'LowerLipV119',[(-.0268*FACE119['frontal']['mouthWidth'],-.0886,.1272),(0,-.0879,.1301),(.0268*FACE119['frontal']['mouthWidth'],-.0886,.1272),(.0228*FACE119['frontal']['mouthWidth'],-.0952,.1270),(0,-.0985,.1291),(-.0228*FACE119['frontal']['mouthWidth'],-.0952,.1270)],.00039*FACE119['surface']['lipThickness'],LIP)
add_strand(HEAD,'MouthSeamV119',[(-.0282,-.0871,.1272),(-.0128,-.0863,.1290),(0,-.0872,.1307),(.0128,-.0863,.1290),(.0282,-.0871,.1272)],.000075,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV119_{side}',side*.0065*FACE119['profile']['noseWidth'],-.0580,.1485,.00195*FACE119['surface']['nostrilScale'],.00072*FACE119['surface']['nostrilScale'],FACE_DARK,20)
"""
if old not in s:
    raise SystemExit('v11.9 lip/nose accent anchor missing')
s=s.replace(old,new,1)

# Add layered key-art bangs after the existing broad swept foundation. These locks overlap the crown/fringe,
# so they read as one hairstyle rather than detached cheek scratches.
anchor="add_strand(HEAD,'FringeFineV90_B',[(-.039,.186,.057),(.000,.153,.092),(.078,.120,.106)],.000032,HAIR_HI)\n"
if anchor not in s:
    raise SystemExit('v11.9 fringe anchor missing')
bangs="""add_strand(HEAD,'FringeFineV90_B',[(-.039,.186,.057),(.000,.153,.092),(.078,.120,.106)],.000032,HAIR_HI)
# v11.9 asymmetric portrait bangs: narrower overlapping locks break up the old helmet-like sweep and
# lower the visual hairline to the brow/outer-eye zone, matching the current Parry Doll key art.
_bang_specs=[
 ('A',[(-.072,.172,.084),(-.061,.137,.103),(-.052,.096,.111),(-.061,.055,.111),(-.073,.022,.106)],[.010,.016,.017,.013,.0028]),
 ('B',[(-.046,.188,.067),(-.032,.151,.099),(-.020,.112,.113),(-.026,.077,.116),(-.039,.047,.111)],[.010,.018,.019,.014,.0030]),
 ('C',[(-.016,.199,.051),(-.003,.160,.091),(.012,.122,.112),(.018,.091,.117),(.010,.061,.114)],[.009,.017,.018,.013,.0028]),
 ('D',[(.017,.198,.050),(.028,.160,.088),(.040,.124,.109),(.050,.095,.114),(.056,.069,.110)],[.009,.016,.018,.013,.0028]),
 ('E',[(.047,.187,.066),(.061,.151,.094),(.073,.116,.107),(.081,.084,.108),(.087,.056,.103)],[.010,.017,.018,.012,.0025])
]
for _name,_pts,_widths in _bang_specs:
 add_smooth_lock(HEAD,f'KeyArtBangV119_{_name}',_pts,_widths,[.0045,.0060,.0062,.0046,.0012],HAIR,12,6)
# Fine warm highlights trace only three locks, keeping the mass dark while revealing strand direction.
for _name,_pts in (
 ('B',[(-.044,.181,.070),(-.029,.143,.102),(-.023,.094,.116),(-.038,.051,.112)]),
 ('C',[(-.013,.191,.054),(.001,.153,.095),(.016,.112,.115),(.011,.065,.114)]),
 ('D',[(.022,.190,.054),(.033,.151,.093),(.047,.112,.112),(.056,.073,.110)])):
 add_strand(HEAD,f'KeyArtBangHiV119_{_name}',_pts,.000055,HAIR_HI)
"""
s=s.replace(anchor,bangs,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V119: high-contrast key-art eyes, compact V-line face, stronger profile and layered asymmetric bangs')
