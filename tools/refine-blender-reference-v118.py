from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V118' in s:
    print('Blender heroine generator already carries REFERENCE_V118')
    raise SystemExit(0)
if '# REFERENCE_V117' not in s:
    raise SystemExit('REFERENCE_V117 generator required before v11.8')

marker='# REFERENCE_V117: model-editor-style local Gaussian/RBF fields sculpt alar wings, philtrum, volumetric lips, mouth corners and the labiomental fold directly into the single-shell face.'
if marker not in s:
    raise SystemExit('v11.8 REFERENCE_V117 marker anchor missing')
s=s.replace(marker,marker+'\n# REFERENCE_V118: reference-locked adult portrait pass narrows the lower face, strengthens brow/bridge/tip/columella profile planes and upgrades the cinematic almond-eye treatment.',1)

if "FACE117_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v117.json')" not in s:
    raise SystemExit('v11.8 FACE117 path anchor missing')
s=s.replace("FACE117_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v117.json')","FACE118_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v118.json')",1)
if "with open(FACE117_PATH,'r',encoding='utf-8') as f:FACE117=json.load(f)" not in s:
    raise SystemExit('v11.8 FACE117 load anchor missing')
s=s.replace("with open(FACE117_PATH,'r',encoding='utf-8') as f:FACE117=json.load(f)","with open(FACE118_PATH,'r',encoding='utf-8') as f:FACE118=json.load(f)",1)
s=s.replace('FACE117','FACE118')

s=s.replace('def add_reference_head_v117(','def add_reference_head_v118(',1)
s=s.replace("add_reference_head_v117(HEAD,'HeadShellV117',SKIN,112)","add_reference_head_v118(HEAD,'HeadShellV118',SKIN,112)",1)

old=""" alar=surface['alarVolume'];philtrum=surface['philtrumDepth'];corner=surface['mouthCornerDepth']
 labiomental=surface['labiomentalDepth'];lip_volume=surface['lipThickness']
"""
new=""" alar=surface['alarVolume'];philtrum=surface['philtrumDepth'];corner=surface['mouthCornerDepth']
 labiomental=surface['labiomentalDepth'];lip_volume=surface['lipThickness']
 glabella=surface['glabellaRelief'];bridge_relief=surface['bridgeRelief'];tip_relief=surface['tipRelief']
 columella=surface['columellaRelief'];infraorbital=surface['infraorbitalSoftness'];nasolabial=surface['nasolabialDepth']
"""
if old not in s:
    raise SystemExit('v11.8 facial plane control anchor missing')
s=s.replace(old,new,1)

old="""    # Labiomental fold separates the lower lip from a broad chin pad.
    z-=fm*.00155*labiomental*math.exp(-(x/.0260)**2-((yy+.1060)/.0075)**2)
    z+=fm*.0060*math.exp(-(x/.038)**2-((yy+.119)/.019)**2)
   verts.append(bpos((x,yy,z)))
"""
new="""    # Labiomental fold separates the lower lip from a more feminine, compact chin pad.
    z-=fm*.00165*labiomental*math.exp(-(x/.0245)**2-((yy+.1060)/.0075)**2)
    z+=fm*.00535*math.exp(-(x/.0315)**2-((yy+.119)/.0180)**2)

    # v11.8 adult facial planes. These are local depth fields, not detached feature meshes,
    # so the silhouette remains one continuous head surface from front through three-quarter views.
    z+=fm*.00215*glabella*math.exp(-(x/.0220)**2-((yy-.0470)/.0180)**2)
    z+=fm*.00355*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)
    z+=fm*.00610*tip_relief*math.exp(-(x/.0115)**2-((yy+.0475)/.0105)**2)
    z+=fm*.00215*columella*math.exp(-(x/.0095)**2-((yy+.0615)/.0080)**2)

    # Soften the lower-orbit to malar transition but keep a readable cheek plane under cinematic light.
    for side in (-1,1):
     io=math.exp(-((x-side*.0445*eye_spacing)/(.0260*eye_size))**2-((yy-.0140)/.0185)**2)
     z+=fm*.00155*infraorbital*io
     nl=math.exp(-((x-side*.0300)/.0145)**2-((yy+.0690)/.0180)**2)
     z-=fm*.00085*nasolabial*nl
   verts.append(bpos((x,yy,z)))
"""
if old not in s:
    raise SystemExit('v11.8 lower-face anatomy anchor missing')
s=s.replace(old,new,1)

old="""face_front=.0974
eye_y=.0330
eye_x=.0465*FACE118['frontal']['eyeSpacing']
eye_rx=.0262*FACE118['frontal']['eyeSize']
eye_ry=.0099*FACE118['frontal']['eyeSize']
eye_tilt=.0018
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV113_{side}',ex,eye_y,.1017,.0288,.0097,.00105,SCLERA,72,side,eye_tilt*.70)
 add_ellipse_surface(HEAD,f'IrisV113_{side}',ex,eye_y,.10270,.0094,.0078,IRIS_INNER,40)
 add_ellipse_surface(HEAD,f'PupilV113_{side}',ex,eye_y-.00015,.10302,.00285,.00345,PUPIL,30)
 add_ellipse_surface(HEAD,f'EyeLightV113_{side}',ex-side*.0030,eye_y+.0028,.10318,.00090,.00072,SCLERA,16)
"""
new="""face_front=.0974
eye_y=.0318
eye_x=.0458*FACE118['frontal']['eyeSpacing']
eye_rx=.0292*FACE118['frontal']['eyeSize']
eye_ry=.01055*FACE118['frontal']['eyeSize']
eye_tilt=.00235
iris_scale=FACE118['surface']['irisScale']
for side in(-1,1):
 ex=side*eye_x
 add_almond_surface(HEAD,f'EyeScleraV118_{side}',ex,eye_y,.10182,eye_rx,eye_ry,.00110,SCLERA,80,side,eye_tilt*.72)
 add_ellipse_surface(HEAD,f'IrisV118_{side}',ex,eye_y-.00015,.10282,.00965*iris_scale,.00810*iris_scale,IRIS_INNER,44)
 add_ellipse_surface(HEAD,f'PupilV118_{side}',ex,eye_y-.00030,.10314,.00275*iris_scale,.00330*iris_scale,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV118_{side}',ex-side*.00315,eye_y+.00275,.10330,.00105,.00082,SCLERA,18)
"""
if old not in s:
    raise SystemExit('v11.8 eye construction anchor missing')
s=s.replace(old,new,1)

s=s.replace("UpperLidRimV117_","UpperLidRimV118_")
s=s.replace("UpperLashV117_","UpperLashV118_")
s=s.replace("UpperLidFoldV117_","UpperLidFoldV118_")
s=s.replace("LowerLidV117_","LowerLidV118_")
old_lash=" add_strand(HEAD,f'UpperLashV118_{side}',[(inner,eye_y-eye_tilt+.0006,.10255),(ex,eye_y+.0101,.10305),(outer,eye_y+eye_tilt+.0006,.10260)],.00048,HAIR)\n"
new_lash=" add_strand(HEAD,f'UpperLashV118_{side}',[(inner,eye_y-eye_tilt+.0006,.10266),(ex,eye_y+.0103,.10316),(outer,eye_y+eye_tilt+.0006,.10271)],.00062,HAIR)\n"
if old_lash not in s:
    raise SystemExit('v11.8 upper lash anchor missing')
s=s.replace(old_lash,new_lash,1)
s=s.replace("BrowV100_","BrowV118_")

s=s.replace("UpperLipV117_L","UpperLipV118_L").replace("UpperLipV117_R","UpperLipV118_R")
s=s.replace("LowerLipV117","LowerLipV118").replace("MouthSeamV117","MouthSeamV118")
s=s.replace("NostrilTintV117_","NostrilTintV118_")

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V118: slimmer reference face, stronger profile planes and cinematic almond-eye treatment')
