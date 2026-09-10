from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V104' in s:
    print('Blender heroine generator already carries REFERENCE_V104')
    raise SystemExit(0)
if '# REFERENCE_V103' not in s:
    raise SystemExit('REFERENCE_V103 generator required before v10.4')

marker='# REFERENCE_V103: adult visible ears sit outside a notched temporal undercap, restoring a natural hairline-to-ear transition in profile.'
if marker not in s:
    raise SystemExit('v10.4 REFERENCE_V103 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V104: the notched temporal undercap widens rearward into the rear-hair shell, covering the exposed side scalp without hiding the ears.',1)

old=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV103_{side}',side,[
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
new=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV104_{side}',side,[
  (.171,head_w*.360, head_d*.030,.003,.0004),
  (.151,head_w*.405, head_d*.016,.021,.0009),
  (.126,head_w*.442,-head_d*.004,.039,.0014),
  (.098,head_w*.462,-head_d*.045,.052,.0018),
  (.068,head_w*.465,-head_d*.095,.058,.0020),
  (.043,head_w*.446,-head_d*.150,.060,.0020),
  # Ear notch: the radial base moves inward here while the sheet extends behind the ear in Z.
  (.022,head_w*.421,-head_d*.210,.054,.0018),
  (.004,head_w*.402,-head_d*.265,.043,.0015),
  (-.014,head_w*.406,-head_d*.320,.035,.0012),
  (-.031,head_w*.424,-head_d*.365,.025,.0009),
  (-.045,head_w*.442,-head_d*.400,.012,.0005)
 ],HAIR,21)
"""
if old not in s:
    raise SystemExit('v10.4 TemporalUnderCapV103 block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V104: rearward temporal scalp bridge closes the ear-to-rear-hair exposure')
