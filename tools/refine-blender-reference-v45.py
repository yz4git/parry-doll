from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V45' in s:
    print('Blender heroine generator already carries REFERENCE_V45')
    raise SystemExit(0)
if '# REFERENCE_V44' not in s:
    raise SystemExit('REFERENCE_V44 generator required before v4.5')

s=s.replace(
    '# REFERENCE_V44: rebuilt portrait head topology, larger inset eyes and sheet-like swept bangs.',
    '# REFERENCE_V44: rebuilt portrait head topology, larger inset eyes and sheet-like swept bangs.\n# REFERENCE_V45: safe layered lock fringe, warmer portrait materials and stronger eyes/lips.',
    1,
)

# Portrait material tuning after the v4.4 WebGL audit: reduce the porcelain-white face read.
s=s.replace("SKIN=material('Skin',(0.68,0.48,0.45),0,.54)", "SKIN=material('Skin',(0.60,0.41,0.39),0,.56)", 1)
s=s.replace("SCLERA=material('Sclera',(0.86,0.84,0.82),0,.42)", "SCLERA=material('Sclera',(0.76,0.72,0.69),0,.46)", 1)
s=s.replace("IRIS=material('Iris',(0.12,0.085,0.070),.02,.34)", "IRIS=material('Iris',(0.10,0.067,0.055),.02,.30)", 1)
s=s.replace("LIP=material('Lip',(0.38,0.22,0.22),0,.60)", "LIP=material('Lip',(0.34,0.16,0.17),0,.56)", 1)

# Increase iris coverage and lip width slightly so both survive the iPhone-size face preset.
s=s.replace("(head_w*.0435,.0104,.0030),IRIS", "(head_w*.0480,.0108,.0030),IRIS", 1)
s=s.replace("add_almond_surface(HEAD,'UpperLipV44',0,-.0810,head_d*.550,.0300,.0045,.0018,LIP,40,1,0.0)", "add_almond_surface(HEAD,'UpperLipV45',0,-.0810,head_d*.550,.0340,.0052,.0020,LIP,44,1,0.0)", 1)
s=s.replace("add_almond_surface(HEAD,'LowerLipV44',0,-.0890,head_d*.549,.0275,.0054,.0021,LIP,40,1,0.0)", "add_almond_surface(HEAD,'LowerLipV45',0,-.0893,head_d*.549,.0315,.0060,.0023,LIP,44,1,0.0)", 1)
s=s.replace("add_strand(HEAD,'MouthSeamV44',[(-.0255,-.0850,head_d*.552),(0,-.0863,head_d*.553),(.0255,-.0850,head_d*.552)],.00034,FACE_DARK)", "add_strand(HEAD,'MouthSeamV45',[(-.0290,-.0852,head_d*.552),(0,-.0864,head_d*.553),(.0290,-.0852,head_d*.552)],.00036,FACE_DARK)", 1)

# V4.4 proved add_flow_ribbon is unsuitable for child meshes parented to HEAD: the sheets were
# transformed away from the scalp. Replace every front fringe sheet with the same lock mesh helper
# used successfully by earlier versions. Roots overlap, paths curve across the forehead, and tip
# widths stay broad enough to avoid the old claw/comb silhouette.
a=s.index('# Hair v4.4:')
b=s.index('# True side-flow ponytail v4.3:',a)
hair="""# Hair v4.5: overlapping curved lock fringe using the proven local-space lock helper.
add_sphere(HEAD,'HairBackV45',(0,.032,-head_d*.366),(head_w*.510,.130,head_d*.456),HAIR,56,36)
add_sphere(HEAD,'HairCrownV45',(-.020,.120,-head_d*.205),(head_w*.474,.061,head_d*.325),HAIR,52,32)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV45_{side}',(side*head_w*.407,.021,-.030),(head_w*.080,.074,head_d*.132),HAIR,32,22)

# Six broad, overlapping masses form one continuous side-swept fringe. The final width deliberately
# remains 25-35% of the root width so no strand ends as a spike.
fringe=[
 (-.123,-.105,-.072,-.048,.058,.154,.052,.017),
 (-.098,-.074,-.038,-.008,.071,.160,.054,.017),
 (-.068,-.038,.000,.034,.083,.165,.053,.016),
 (-.034,.000,.042,.074,.079,.164,.052,.016),
 (.004,.040,.080,.105,.066,.159,.050,.015),
 (.044,.078,.112,.130,.048,.151,.046,.014),
]
for i,(rx,mx,cx,tx,ty,ry,w,tipw) in enumerate(fringe):
 pts=[
  (rx,ry,-head_d*.016),
  (mx,ry-.020,head_d*.165),
  (cx,.112,head_d*.355),
  (tx,ty,head_d*.516),
 ]
 add_lock_mesh(HEAD,f'ForeheadLockV45_{i}',pts,[w*.62,w,w*.70,tipw],[.0085,.0100,.0075,.0038],HAIR_HI if i in(0,5) else HAIR,10)

# Three shallower crossing locks hide root gaps and establish the diagonal part without forming bars.
for i,(rx,mx,tx,ty) in enumerate(((-.112,-.072,-.020,.077),(-.068,-.018,.048,.082),(-.012,.045,.112,.056))):
 pts=[(rx,.148,head_d*.008),(mx,.126,head_d*.265),((mx+tx)*.5,.101,head_d*.430),(tx,ty,head_d*.518)]
 add_lock_mesh(HEAD,f'FringeLayerV45_{i}',pts,[.026,.030,.021,.009],[.0058,.0064,.0048,.0028],HAIR_HI if i==2 else HAIR,8)

# Fine edge wisps are sparse and follow the same sweep.
for i,(rx,tx,ty) in enumerate(((-.104,-.056,.066),(-.050,.018,.081),(.018,.094,.058))):
 add_strand(HEAD,f'BangWispV45_{i}',[(rx,.141,head_d*.014),((rx+tx)*.5,.112,head_d*.320),(tx,ty,head_d*.523)],.00048,HAIR_HI if i!=1 else HAIR)

for side in(-1,1):
 pts=[(side*head_w*.350,.087,-.010),(side*head_w*.397,.018,head_d*.068),(side*head_w*.410,-.130,head_d*.005),(side*head_w*.372,-.310,-.030)]
 add_lock_mesh(HEAD,f'FaceLockV45_{side}',pts,[.020,.023,.014,.0045],[.0050,.0054,.0040,.0022],HAIR,8)
 add_strand(HEAD,f'FaceWispV45_{side}',[(side*head_w*.382,.074,-.006),(side*head_w*.425,-.030,head_d*.035),(side*head_w*.414,-.205,-.006),(side*head_w*.394,-.405,-.030)],.00050,HAIR_HI)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V45: safe layered lock fringe and warmer portrait tuning')
