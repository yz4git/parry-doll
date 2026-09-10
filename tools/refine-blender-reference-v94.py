from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V94' in s:
    print('Blender heroine generator already carries REFERENCE_V94')
    raise SystemExit(0)
if '# REFERENCE_V93' not in s:
    raise SystemExit('REFERENCE_V93 generator required before v9.4')

marker='# REFERENCE_V93: rear-biased lower temporal shells cover the ear-zone scalp while preserving the cheek and eye silhouette.'
if marker not in s:
    raise SystemExit('v9.4 REFERENCE_V93 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V94: smooth elliptical side locks replace the rectangular temporal sheets and cover the ear-zone scalp naturally.',1)

old="""# v9.2 fills the true remaining gap: side scalp between the side-swept fringe and rear shell.
# It stops above the ears and remains outside the facial plane, avoiding the old on-cheek wisp artifacts.
for side in (-1,1):
 add_temporal_shell_v92(HEAD,f'TemporalHairShellV93_{side}',side,[
  (.178,head_w*.405,head_d*.365,-head_d*.020),
  (.150,head_w*.470,head_d*.430,-head_d*.028),
  (.118,head_w*.515,head_d*.485,-head_d*.036),
  (.083,head_w*.542,head_d*.520,-head_d*.044),
  (.048,head_w*.548,head_d*.535,-head_d*.051),
  (.014,head_w*.535,head_d*.535,-head_d*.057),
  (-.018,head_w*.510,head_d*.520,-head_d*.062),
  (-.046,head_w*.468,head_d*.495,-head_d*.066),
  (-.066,head_w*.420,head_d*.455,-head_d*.068)
 ],HAIR,22)
"""
new="""# v9.4 replaces the sheet-like side patch with a volumetric, vertically flowing lock.
# Its radial X thickness stays thin while the logical-Z depth is broad enough to bridge temple to rear hair.
# The front edge stops well behind the cheek/nose plane, so the face silhouette remains clean.
for side in (-1,1):
 add_smooth_lock(HEAD,f'SideScalpLockV94_{side}',[
  (side*head_w*.455,.176,-head_d*.025),
  (side*head_w*.495,.145,-head_d*.030),
  (side*head_w*.520,.108,-head_d*.040),
  (side*head_w*.530,.068,-head_d*.050),
  (side*head_w*.522,.026,-head_d*.066),
  (side*head_w*.505,-.014,-head_d*.082),
  (side*head_w*.478,-.047,-head_d*.098),
  (side*head_w*.435,-.069,-head_d*.112)
 ],[.008,.013,.017,.019,.019,.017,.012,.0045],[.020,.036,.050,.058,.060,.056,.044,.014],HAIR,16,6)
 # A restrained rear-biased highlight breaks up the mass without creating a second hanging panel.
 add_smooth_lock(HEAD,f'SideScalpAccentV94_{side}',[
  (side*head_w*.482,.158,-head_d*.105),
  (side*head_w*.510,.115,-head_d*.125),
  (side*head_w*.518,.066,-head_d*.142),
  (side*head_w*.505,.018,-head_d*.155),
  (side*head_w*.472,-.030,-head_d*.162)
 ],[.004,.006,.007,.006,.002],[.010,.015,.018,.016,.006],HAIR_HI,12,5)
"""
if old not in s:
    raise SystemExit('v9.4 v9.3 temporal block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V94: smooth elliptical side locks replace rectangular temporal shells')
