from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V105' in s:
    print('Blender heroine generator already carries REFERENCE_V105')
    raise SystemExit(0)
if '# REFERENCE_V104' not in s:
    raise SystemExit('REFERENCE_V104 generator required before v10.5')

marker='# REFERENCE_V104: the notched temporal undercap widens rearward into the rear-hair shell, covering the exposed side scalp without hiding the ears.'
if marker not in s:
    raise SystemExit('v10.5 REFERENCE_V104 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V105: visible rear-hair geometry expands around ear height while the buried v10.4 undercap returns to the compact v10.3 footprint.',1)

old_shell="""add_rear_hair_shell(HEAD,'HairRearShellV59',[
 (-.025,head_w*.300,head_d*.410,-head_d*.066),
 (.012,head_w*.430,head_d*.500,-head_d*.058),
 (.052,head_w*.505,head_d*.550,-head_d*.050),
 (.096,head_w*.528,head_d*.562,-head_d*.042),
 (.138,head_w*.490,head_d*.517,-head_d*.033),
 (.170,head_w*.394,head_d*.422,-head_d*.024),
 (.194,head_w*.230,head_d*.270,-head_d*.013),
 (.206,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,44)
"""
new_shell="""add_rear_hair_shell(HEAD,'HairRearShellV105',[
 # The old shell collapsed to 0.30*head_w at ear height, exposing a large skin-colored side plane.
 # These first three sections stay outside the cranium and slightly behind EarV103, so the ear remains readable.
 (-.055,head_w*.410,head_d*.340,-head_d*.125),
 (-.025,head_w*.472,head_d*.455,-head_d*.102),
 (.012,head_w*.505,head_d*.535,-head_d*.078),
 (.052,head_w*.520,head_d*.565,-head_d*.058),
 (.096,head_w*.528,head_d*.562,-head_d*.042),
 (.138,head_w*.490,head_d*.517,-head_d*.033),
 (.170,head_w*.394,head_d*.422,-head_d*.024),
 (.194,head_w*.230,head_d*.270,-head_d*.013),
 (.206,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,48)
"""
if old_shell not in s:
    raise SystemExit('v10.5 HairRearShellV59 block missing')
s=s.replace(old_shell,new_shell,1)

old_cap=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV104_{side}',side,[
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
new_cap=""" add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV105_{side}',side,[
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
    raise SystemExit('v10.5 TemporalUnderCapV104 block missing')
s=s.replace(old_cap,new_cap,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V105: rear-hair shell now visibly covers ear-height scalp while keeping the ear and compact temporal root clear')
