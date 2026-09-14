from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V153' in s:
    print('Blender heroine generator already carries REFERENCE_V153')
    raise SystemExit(0)
if '# REFERENCE_V152' not in s:
    raise SystemExit('REFERENCE_V152 generator required before v13.23')

marker="# REFERENCE_V152: nose-philtrum-lip integration pass narrows the alar base, deepens the subnasal/philtrum break and sculpts a cleaner Cupid bow, lower-lip volume and mouth-corner transition while preserving the accepted eye/jaw silhouette."
if marker not in s:
    raise SystemExit('v13.23 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V153: nasion/bridge profile pass deepens the orbital-to-nose root break and builds a narrow continuous dorsum into the accepted small nose tip without changing the mouth, jaw or frontal face width.",1)

# Slightly strengthen the centreline nose depth while staying near the accepted v13.22 silhouette.
old="nose_proj=profile_ctrl['noseProjection']*.71;nose_width=profile_ctrl['noseWidth']"
new="nose_proj=profile_ctrl['noseProjection']*.735;nose_width=profile_ctrl['noseWidth']"
if old not in s:
    raise SystemExit('v13.23 nose projection anchor missing')
s=s.replace(old,new,1)

# Narrow the centreline influence so three-quarter views read a slim bridge rather than a broad facial mound.
old="pw=(.030*nose_width) if yy>-.068 else (.043 if yy>-.108 else .039)"
new="pw=(.0275*nose_width) if yy>-.068 else (.043 if yy>-.108 else .039)"
if old not in s:
    raise SystemExit('v13.23 profile width anchor missing')
s=s.replace(old,new,1)

# Rebuild only the forehead-root-bridge-tip section of the data-driven profile spline.
old="(.090,.1002),(.060,.1010),(.038,.1000),(.020,.0984),(.006,.0995),(-.008,.1042),\n  (-.022,.1112),(-.035,.1200),(-.046,.1264),(-.053,.1290),(-.059,.1266),"
new="(.090,.1002),(.060,.1010),(.038,.1000),(.020,.0976),(.006,.0988),(-.008,.1048),\n  (-.022,.1128),(-.035,.1212),(-.046,.1270),(-.053,.1294),(-.059,.1265),"
if old not in s:
    raise SystemExit('v13.23 base profile anchor missing')
s=s.replace(old,new,1)

# Add a shallow nasion recess that remains visible in 3Q, then let the existing bridge/tip fields carry forward.
needle="z+=fm*.00215*glabella*math.exp(-(x/.0220)**2-((yy-.0470)/.0180)**2)\n    z+=fm*.00345*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)"
replacement="z+=fm*.00215*glabella*math.exp(-(x/.0220)**2-((yy-.0470)/.0180)**2)\n    z-=fm*.00085*math.exp(-(x/.0150)**2-((yy-.0160)/.0160)**2)\n    z+=fm*.00345*bridge_relief*math.exp(-(x/.0145)**2-((yy+.0100)/.0340)**2)"
if needle not in s:
    raise SystemExit('v13.23 nasion relief anchor missing')
s=s.replace(needle,replacement,1)

old="ROOT['character_revision']='v13.22';"
new="ROOT['character_revision']='v13.23';"
if old not in s:
    raise SystemExit('v13.23 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['reference_profile_silhouette']='v13.19'"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['reference_profile_silhouette']='v13.23'",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['nasion_bridge_revision']='v13.23';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V153: deeper nasion break and narrow continuous nose bridge into the accepted small tip')
