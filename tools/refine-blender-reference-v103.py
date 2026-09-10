from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V103' in s:
    print('Blender heroine generator already carries REFERENCE_V103')
    raise SystemExit(0)
if '# REFERENCE_V102' not in s:
    raise SystemExit('REFERENCE_V102 generator required before v10.3')

marker='# REFERENCE_V102: temporal lock tips sweep rearward around the ear instead of dropping into straight claw-like prongs.'
if marker not in s:
    raise SystemExit('v10.3 REFERENCE_V102 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V103: adult visible ears sit outside a notched temporal undercap, restoring a natural hairline-to-ear transition in profile.',1)

# Replace the tiny almost-buried canonical ear rather than layering a second ear on top of it.
old_ear="for side in(-1,1):add_sphere(HEAD,f'EarV78_{side}',(side*.121,-.018,-.012),(.0085,.0205,.0078),SKIN,20,12)"
new_ear="""for side in(-1,1):
 add_sphere(HEAD,f'EarV103_{side}',(side*.1265,-.020,-.020),(.0120,.0305,.0145),SKIN,28,18)
 # A restrained helix/concha line is enough to read as an ear at iPhone portrait scale without becoming a dark decal.
 add_strand(HEAD,f'EarHelixV103_{side}',[
  (side*.1380,.004,-.021),
  (side*.1390,-.007,-.012),
  (side*.1393,-.021,-.010),
  (side*.1388,-.035,-.016),
  (side*.1376,-.044,-.025)
 ],.00028,EAR_SHADOW)
 add_strand(HEAD,f'EarConchaV103_{side}',[
  (side*.1385,-.010,-.018),
  (side*.1390,-.020,-.015),
  (side*.1384,-.030,-.020)
 ],.00022,EAR_SHADOW)
"""
if old_ear not in s:
    raise SystemExit('v10.3 canonical EarV78 anchor missing')
s=s.replace(old_ear,new_ear,1)

# Cut the visible hair root inward around the ear instead of letting the undercap sit outside it.
# The upper rows stay unchanged, then the hairline bends behind the enlarged ear and recovers rearward below it.
old_cap=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV101_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.442, head_d*.012,.032,.0012),
  (.098,head_w*.462, head_d*.000,.041,.0015),
  (.068,head_w*.468,-head_d*.014,.043,.0016),
  (.039,head_w*.465,-head_d*.028,.038,.0014),
  (.014,head_w*.455,-head_d*.041,.028,.0011),
  (-.004,head_w*.442,-head_d*.050,.016,.0008),
  (-.014,head_w*.430,-head_d*.055,.004,.0003)
 ],HAIR,15)
"""
new_cap=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV103_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.022,.018,.0008),
  (.126,head_w*.442, head_d*.012,.032,.0012),
  (.098,head_w*.462, head_d*.000,.041,.0015),
  (.068,head_w*.465,-head_d*.014,.041,.0015),
  (.043,head_w*.446,-head_d*.031,.034,.0013),
  (.022,head_w*.421,-head_d*.049,.024,.0010),
  (.004,head_w*.402,-head_d*.067,.015,.0008),
  (-.014,head_w*.406,-head_d*.085,.010,.0007),
  (-.031,head_w*.424,-head_d*.101,.008,.0006),
  (-.045,head_w*.442,-head_d*.113,.003,.0003)
 ],HAIR,17)
"""
if old_cap not in s:
    raise SystemExit('v10.3 TemporalUnderCapV101 anchor missing')
s=s.replace(old_cap,new_cap,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V103: adult visible ears plus a rear-curving temporal undercap notch')
