from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V152' in s:
    print('Blender heroine generator already carries REFERENCE_V152')
    raise SystemExit(0)
if '# REFERENCE_V151' not in s:
    raise SystemExit('REFERENCE_V151 generator required before v13.22')

marker="# REFERENCE_V151: eyelid-integration pass narrows the frontal/three-quarter aperture, reduces iris dominance and increases canthal tilt while preserving the accepted exact-profile eye readability."
if marker not in s:
    raise SystemExit('v13.22 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V152: nose-philtrum-lip integration pass narrows the alar base, deepens the subnasal/philtrum break and sculpts a cleaner Cupid bow, lower-lip volume and mouth-corner transition while preserving the accepted eye/jaw silhouette.",1)

# Refine the nasal base without altering the accepted bridge/tip silhouette.
for old,new in (
    ("aw=math.exp(-((x-side*.0115)/(.0105*nose_width))**2-((yy+.0555)/.0115)**2)",
     "aw=math.exp(-((x-side*.0108)/(.0098*nose_width))**2-((yy+.0555)/.0110)**2)"),
    ("x+=side*.00155*alar*aw","x+=side*.00110*alar*aw"),
    ("z+=fm*.0035*alar*aw","z+=fm*.00310*alar*aw"),
    ("nr=math.exp(-((x-side*.0075)/.0085)**2-((yy+.0630)/.0075)**2)",
     "nr=math.exp(-((x-side*.0070)/.0078)**2-((yy+.0625)/.0072)**2)"),
    ("z-=fm*.00175*surface['nostrilScale']*nr","z-=fm*.00195*surface['nostrilScale']*nr"),
):
    if old not in s:
        raise SystemExit('v13.22 nasal anchor missing: '+old[:48])
    s=s.replace(old,new,1)

# Sharpen the subnasal break and philtrum so the upper lip grows from the face instead of one smooth muzzle.
for old,new in (
    ("z-=fm*.00155*math.exp(-(x/.0105)**2-((yy+.0665)/.0075)**2)",
     "z-=fm*.00182*math.exp(-(x/.0102)**2-((yy+.0660)/.0072)**2)"),
    ("z-=fm*.00145*philtrum*math.exp(-(x/.0070)**2-((yy+.0760)/.0105)**2)",
     "z-=fm*.00178*philtrum*math.exp(-(x/.0067)**2-((yy+.0755)/.0100)**2)"),
):
    if old not in s:
        raise SystemExit('v13.22 philtrum anchor missing: '+old[:48])
    s=s.replace(old,new,1)

# Sculpt the lip volumes: clearer Cupid bow, fuller lower centre, tighter corners and stronger labiomental separation.
for old,new in (
    ("math.exp(-((x-.0105*mouth_w)/(.0120*mouth_w))**2-((yy+.0845)/.0080)**2)+",
     "math.exp(-((x-.0098*mouth_w)/(.0115*mouth_w))**2-((yy+.0838)/.0077)**2)+"),
    ("math.exp(-((x+.0105*mouth_w)/(.0120*mouth_w))**2-((yy+.0845)/.0080)**2))",
     "math.exp(-((x+.0098*mouth_w)/(.0115*mouth_w))**2-((yy+.0838)/.0077)**2))"),
    ("z+=fm*.00362*lip_volume*ul","z+=fm*.00392*lip_volume*ul"),
    ("z-=fm*.00075*lip_volume*math.exp(-(x/.0055)**2-((yy+.0847)/.0055)**2)",
     "z-=fm*.00100*lip_volume*math.exp(-(x/.0052)**2-((yy+.0843)/.0051)**2)"),
    ("ll=math.exp(-(x/(.0255*mouth_w))**2-((yy+.0940)/.0085)**2)",
     "ll=math.exp(-(x/(.0248*mouth_w))**2-((yy+.0935)/.0083)**2)"),
    ("z+=fm*.00430*lip_volume*ll","z+=fm*.00462*lip_volume*ll"),
    ("z-=fm*.00080*math.exp(-(x/(.0280*mouth_w))**4-((yy+.0887)/.0032)**2)",
     "z-=fm*.00096*math.exp(-(x/(.0274*mouth_w))**4-((yy+.0885)/.0030)**2)"),
    ("mc=math.exp(-((x-side*.0285*mouth_w)/.0090)**2-((yy+.0890)/.0070)**2)",
     "mc=math.exp(-((x-side*.0278*mouth_w)/.0084)**2-((yy+.0888)/.0066)**2)"),
    ("z-=fm*.00135*corner*mc","z-=fm*.00155*corner*mc"),
    ("z-=fm*.00135*labiomental*math.exp(-(x/.0245)**2-((yy+.1060)/.0082)**2)",
     "z-=fm*.00158*labiomental*math.exp(-(x/.0238)**2-((yy+.1052)/.0078)**2)"),
):
    if old not in s:
        raise SystemExit('v13.22 lip-sculpt anchor missing: '+old[:52])
    s=s.replace(old,new,1)

# Retarget the visible lip tint panels to the newly sculpted shell; keep them shallow so they remain colour/material cues.
for old,new in (
    ("(-.0294*FACE120['frontal']['mouthWidth'],-.0835,.1268)","(-.0288*FACE120['frontal']['mouthWidth'],-.0834,.1271)"),
    ("(-.0135,-.0796,.1284)","(-.0129,-.0799,.1290)"),
    ("(0,-.0827,.1302)","(0,-.0824,.1308)"),
    ("(0,-.0867,.1305)","(0,-.0866,.1310)"),
    ("(-.0115,-.0860,.1292)","(-.0112,-.0858,.1297)"),
    ("(-.0282*FACE120['frontal']['mouthWidth'],-.0878,.1273)","(-.0277*FACE120['frontal']['mouthWidth'],-.0877,.1276)"),
    ("(.0135,-.0796,.1284)","(.0129,-.0799,.1290)"),
    ("(.0294*FACE120['frontal']['mouthWidth'],-.0835,.1268)","(.0288*FACE120['frontal']['mouthWidth'],-.0834,.1271)"),
    ("(.0282*FACE120['frontal']['mouthWidth'],-.0878,.1273)","(.0277*FACE120['frontal']['mouthWidth'],-.0877,.1276)"),
    ("(.0115,-.0860,.1292)","(.0112,-.0858,.1297)"),
    ("(-.0282*FACE120['frontal']['mouthWidth'],-.0880,.1272)","(-.0277*FACE120['frontal']['mouthWidth'],-.0880,.1275)"),
    ("(0,-.0879,.1301)","(0,-.0878,.1308)"),
    ("(.0282*FACE120['frontal']['mouthWidth'],-.0880,.1272)","(.0277*FACE120['frontal']['mouthWidth'],-.0880,.1275)"),
    ("(.0238*FACE120['frontal']['mouthWidth'],-.0944,.1270)","(.0233*FACE120['frontal']['mouthWidth'],-.0941,.1274)"),
    ("(0,-.0985,.1291)","(0,-.0980,.1298)"),
    ("(-.0238*FACE120['frontal']['mouthWidth'],-.0944,.1270)","(-.0233*FACE120['frontal']['mouthWidth'],-.0941,.1274)"),
    ("[(-.0300,-.0868,.1272),(-.0135,-.0860,.1290),(0,-.0869,.1307),(.0135,-.0860,.1290),(.0300,-.0868,.1272)]",
     "[(-.0292,-.0867,.1275),(-.0130,-.0859,.1295),(0,-.0868,.1312),(.0130,-.0859,.1295),(.0292,-.0867,.1275)]"),
    ("side*.0065*FACE120['profile']['noseWidth'],-.0580,.1368,.00205*FACE120['surface']['nostrilScale'],.00088*FACE120['surface']['nostrilScale']",
     "side*.0062*FACE120['profile']['noseWidth'],-.0588,.1361,.00190*FACE120['surface']['nostrilScale'],.00078*FACE120['surface']['nostrilScale']"),
):
    if old not in s:
        raise SystemExit('v13.22 visible-accent anchor missing: '+old[:58])
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.21';"
new="ROOT['character_revision']='v13.22';"
if old not in s:
    raise SystemExit('v13.22 revision anchor missing')
s=s.replace(old,new,1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"MOUTH_ASSET['nose_philtrum_lip_revision']='v13.22';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V152: integrated alar base, philtrum, Cupid bow, lower lip and mouth-corner sculpt')
