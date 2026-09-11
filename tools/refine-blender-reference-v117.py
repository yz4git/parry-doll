from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V117' in s:
    print('Blender heroine generator already carries REFERENCE_V117')
    raise SystemExit(0)
if '# REFERENCE_V116' not in s:
    raise SystemExit('REFERENCE_V116 generator required before v11.7')

marker='# REFERENCE_V116: model-editor-inspired independent frontal/profile/surface controls drive the single-shell face so depth tuning no longer disturbs frontal proportions.'
if marker not in s:
    raise SystemExit('v11.7 REFERENCE_V116 marker anchor missing')
s=s.replace(marker,marker+'\n# REFERENCE_V117: model-editor-style local Gaussian/RBF fields sculpt alar wings, philtrum, volumetric lips, mouth corners and the labiomental fold directly into the single-shell face.',1)

# Promote the data-driven controls to v11.7.
if "FACE116_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v116.json')" not in s:
    raise SystemExit('v11.7 FACE116 path anchor missing')
s=s.replace("FACE116_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v116.json')","FACE117_PATH=os.path.join(ROOT_DIR,'tools','heroine-face-controls-v117.json')",1)
if "with open(FACE116_PATH,'r',encoding='utf-8') as f:FACE116=json.load(f)" not in s:
    raise SystemExit('v11.7 FACE116 load anchor missing')
s=s.replace("with open(FACE116_PATH,'r',encoding='utf-8') as f:FACE116=json.load(f)","with open(FACE117_PATH,'r',encoding='utf-8') as f:FACE117=json.load(f)",1)
# All v11.6 feature consumers now read the v11.7 control set.
s=s.replace('FACE116','FACE117')

# Rename the clean head builder and rendered shell; topology remains the v11.6 single continuous surface.
s=s.replace('def add_reference_head_v116(','def add_reference_head_v117(',1)
s=s.replace("add_reference_head_v116(HEAD,'HeadShellV116',SKIN,112)","add_reference_head_v117(HEAD,'HeadShellV117',SKIN,112)",1)

# Expose the extra surface controls beside the existing orbit/malar controls.
old=" orbital=surface['orbitalDepth'];malar=surface['malarSupport'];hollow=surface['lowerCheekHollow']\n"
new=""" orbital=surface['orbitalDepth'];malar=surface['malarSupport'];hollow=surface['lowerCheekHollow']
 alar=surface['alarVolume'];philtrum=surface['philtrumDepth'];corner=surface['mouthCornerDepth']
 labiomental=surface['labiomentalDepth'];lip_volume=surface['lipThickness']
"""
if old not in s:
    raise SystemExit('v11.7 surface-control anchor missing')
s=s.replace(old,new,1)

# Replace the former generic muzzle/chin support with explicit local facial anatomy fields.
old="""    z+=fm*.0044*math.exp(-(x/.052)**2-((yy+.086)/.023)**2)
    z+=fm*.0060*math.exp(-(x/.038)**2-((yy+.119)/.019)**2)
   verts.append(bpos((x,yy,z)))
"""
new="""    # v11.7 local RBF anatomy, adapted from model-editor's measured-base deformation strategy.
    # Each field is deliberately local so nose/mouth depth can change without widening the frontal jaw.
    for side in (-1,1):
     # Alar wings move slightly outward and forward around the nasal base.
     aw=math.exp(-((x-side*.0115)/(.0105*nose_width))**2-((yy+.0555)/.0115)**2)
     x+=side*.00155*alar*aw
     z+=fm*.0035*alar*aw
     # The nostril floor/alar crease sits just below and medial to the wing.
     nr=math.exp(-((x-side*.0075)/.0085)**2-((yy+.0630)/.0075)**2)
     z-=fm*.00175*surface['nostrilScale']*nr

    # Subnasal break and philtrum groove keep nose and upper lip from melting into one mound.
    z-=fm*.00155*math.exp(-(x/.0105)**2-((yy+.0665)/.0075)**2)
    z-=fm*.00145*philtrum*math.exp(-(x/.0070)**2-((yy+.0760)/.0105)**2)

    # Upper lip is two soft lobes with a shallow central Cupid notch; lower lip is one broad volume.
    mouth_w=frontal['mouthWidth']
    ul=(math.exp(-((x-.0105*mouth_w)/(.0120*mouth_w))**2-((yy+.0845)/.0080)**2)+
        math.exp(-((x+.0105*mouth_w)/(.0120*mouth_w))**2-((yy+.0845)/.0080)**2))
    z+=fm*.00265*lip_volume*ul
    z-=fm*.00075*lip_volume*math.exp(-(x/.0055)**2-((yy+.0847)/.0055)**2)
    ll=math.exp(-(x/(.0255*mouth_w))**2-((yy+.0940)/.0085)**2)
    z+=fm*.00310*lip_volume*ll
    # Mouth seam and corners recess into the muzzle rather than floating as a drawn line.
    z-=fm*.00080*math.exp(-(x/(.0280*mouth_w))**4-((yy+.0887)/.0032)**2)
    for side in (-1,1):
     mc=math.exp(-((x-side*.0285*mouth_w)/.0090)**2-((yy+.0890)/.0070)**2)
     z-=fm*.00135*corner*mc

    # Labiomental fold separates the lower lip from a broad chin pad.
    z-=fm*.00155*labiomental*math.exp(-(x/.0260)**2-((yy+.1060)/.0075)**2)
    z+=fm*.0060*math.exp(-(x/.038)**2-((yy+.119)/.019)**2)
   verts.append(bpos((x,yy,z)))
"""
if old not in s:
    raise SystemExit('v11.7 muzzle/chin anchor missing')
s=s.replace(old,new,1)

# Rename and slightly strengthen the physical upper-lid rim; aperture itself remains data-controlled.
s=s.replace("UpperLidRimV116_","UpperLidRimV117_")
s=s.replace("UpperLashV115_","UpperLashV117_")
s=s.replace("UpperLidFoldV115_","UpperLidFoldV117_")
s=s.replace("LowerLidV115_","LowerLidV117_")

# Surface tint remains secondary to the shell volume; retag it for audit visibility.
s=s.replace("UpperLipV115_L","UpperLipV117_L").replace("UpperLipV115_R","UpperLipV117_R")
s=s.replace("LowerLipV115","LowerLipV117").replace("MouthSeamV115","MouthSeamV117")
s=s.replace("NostrilTintV114_","NostrilTintV117_")

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V117: local RBF nose/lip/mouth/chin anatomy on the independent single-shell face')
