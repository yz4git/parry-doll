from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V142' in s:
    print('Blender heroine generator already carries REFERENCE_V142')
    raise SystemExit(0)
if '# REFERENCE_V141' not in s:
    raise SystemExit('REFERENCE_V141 generator required before v13.12')

marker="# REFERENCE_V141: swept-temple/ear-exposure pass recesses the side undercap, pulls the front temporal lock behind the ear and adds fine rearward flow strands to match the supplied ponytail profile."
if marker not in s:
    raise SystemExit('v13.12 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V142: explicit-ear silhouette pass enlarges and slightly externalizes the canonical ear while further recessing the lower temple mass, leaving only fine sideburn strands across the ear-front region.",1)

# Make the canonical ear read from exact profile instead of as a tiny circular patch. Keep the change restrained
# so three-quarter/front views still look natural.
old="add_sphere(HEAD,f'EarV103_{side}',(side*.1265,-.020,-.012),(.0122,.0350,.0170),SKIN,30,20)"
new="add_sphere(HEAD,f'EarV103_{side}',(side*.1325,-.020,-.012),(.0142,.0385,.0188),SKIN,32,22)"
if old not in s: raise SystemExit('v13.12 ear sphere anchor missing')
s=s.replace(old,new,1)

# Move helix/concha/earring accents with the externalized ear shell.
for old,new in (
 ("side*.1380,.004,-.021","side*.1450,.004,-.021"),
 ("side*.1390,-.007,-.012","side*.1460,-.007,-.012"),
 ("side*.1393,-.021,-.010","side*.1463,-.021,-.010"),
 ("side*.1388,-.035,-.016","side*.1458,-.035,-.016"),
 ("side*.1376,-.044,-.025","side*.1446,-.044,-.025"),
 ("side*.1385,-.010,-.018","side*.1455,-.010,-.018"),
 ("side*.1390,-.020,-.015","side*.1460,-.020,-.015"),
 ("side*.1384,-.030,-.020","side*.1454,-.030,-.020"),
 ("side*.1390,-.043,-.010","side*.1460,-.043,-.010"),
 ("side*.1392,-.057,-.009","side*.1462,-.057,-.009"),
 ("side*.1390,-.071,-.010","side*.1460,-.071,-.010"),
 ("side*.1390,-.075,-.010","side*.1460,-.075,-.010"),
 ):
    if old in s: s=s.replace(old,new,1)

# Recess the accepted v13.11 lower undercap another small step behind the ear silhouette.
old=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV105_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.434, head_d*.008,.030,.0011),
  (.098,head_w*.444,-head_d*.006,.035,.0013),
  (.068,head_w*.436,-head_d*.030,.033,.0012),
  (.043,head_w*.420,-head_d*.052,.028,.0011),
  (.022,head_w*.399,-head_d*.074,.020,.0009),
  (.004,head_w*.384,-head_d*.092,.013,.0007),
  (-.014,head_w*.388,-head_d*.108,.009,.0006),
  (-.031,head_w*.402,-head_d*.122,.006,.0005),
  (-.045,head_w*.416,-head_d*.132,.0025,.0003)
 ],HAIR,17)
"""
new=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV105_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.400, head_d*.018,.017,.0008),
  (.126,head_w*.425, head_d*.002,.027,.0010),
  (.098,head_w*.427,-head_d*.014,.029,.0011),
  (.068,head_w*.414,-head_d*.040,.026,.0010),
  (.043,head_w*.397,-head_d*.064,.021,.0009),
  (.022,head_w*.377,-head_d*.086,.015,.0008),
  (.004,head_w*.365,-head_d*.104,.010,.0006),
  (-.014,head_w*.370,-head_d*.120,.007,.0005),
  (-.031,head_w*.386,-head_d*.134,.0045,.0004),
  (-.045,head_w*.400,-head_d*.144,.0020,.0003)
 ],HAIR,17)
"""
if old not in s: raise SystemExit('v13.12 undercap anchor missing')
s=s.replace(old,new,1)

# Narrow and rear-bias the visible front temple lock further; it should frame the ear, not cover it.
old=""" add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.018),
  (side*head_w*.410,.145, head_d*.006),
  (side*head_w*.450,.108,-head_d*.018),
  (side*head_w*.462,.068,-head_d*.052),
  (side*head_w*.452,.030,-head_d*.094),
  (side*head_w*.432,.010,-head_d*.128),
  (side*head_w*.402,-.006,-head_d*.150)
 ],[.0028,.0055,.0072,.0074,.0058,.0036,.0009],[.006,.010,.012,.0125,.0095,.0058,.0020],HAIR,14,6)
"""
new=""" add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.014),
  (side*head_w*.400,.145,-head_d*.002),
  (side*head_w*.432,.108,-head_d*.030),
  (side*head_w*.442,.068,-head_d*.067),
  (side*head_w*.430,.030,-head_d*.108),
  (side*head_w*.410,.010,-head_d*.140),
  (side*head_w*.386,-.006,-head_d*.160)
 ],[.0025,.0046,.0056,.0058,.0043,.0027,.00075],[.0052,.0080,.0092,.0096,.0072,.0044,.0017],HAIR,14,6)
"""
if old not in s: raise SystemExit('v13.12 temporal lock anchor missing')
s=s.replace(old,new,1)

anchor="# v13.11 supplied-reference swept temple flow around the exposed ear."
if anchor not in s: raise SystemExit('v13.12 wisp anchor missing')
insert="""# v13.12 fine sideburns leave the ear itself visible while preserving the supplied-reference softness.
for _side in (-1,1):
 add_strand(HEAD,f'EarFrontWispV142_A_{_side}',[(_side*.116,.084,.095),(_side*.122,.046,.091),(_side*.120,.010,.086),(_side*.112,-.030,.080),(_side*.104,-.074,.073)],.000021,HAIR)
 add_strand(HEAD,f'EarFrontWispV142_B_{_side}',[(_side*.108,.104,.097),(_side*.114,.070,.094),(_side*.113,.036,.090),(_side*.106,-.002,.084),(_side*.098,-.044,.078)],.000017,HAIR_HI)

"""
s=s.replace(anchor,insert+anchor,1)

old="ROOT['character_revision']='v13.11';"
new="ROOT['character_revision']='v13.12';"
if old not in s: raise SystemExit('v13.12 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.11'","HEAD_ASSET['reference_profile_silhouette']='v13.12'",1)
s=s.replace("HAIR_ASSET['reference_profile_hair_revision']='v13.11'","HAIR_ASSET['reference_profile_hair_revision']='v13.12'",1)
s=s.replace("HAIR_ASSET['ear_exposure_revision']='v13.11'","HAIR_ASSET['ear_exposure_revision']='v13.12'",1)
s=s.replace("HAIR_ASSET['temple_sweep_revision']='v13.11'","HAIR_ASSET['temple_sweep_revision']='v13.12'",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V142: larger externalized ears, deeper temple recess and fine sideburn framing')
