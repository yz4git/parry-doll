from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V93' in s:
    print('Blender heroine generator already carries REFERENCE_V93')
    raise SystemExit(0)
if '# REFERENCE_V92' not in s:
    raise SystemExit('REFERENCE_V92 generator required before v9.3')

marker='# REFERENCE_V92: dedicated scalp-hugging temporal shells bridge fringe to rear hair above the ears without cheek wisps.'
if marker not in s:
    raise SystemExit('v9.3 REFERENCE_V92 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V93: rear-biased lower temporal shells cover the ear-zone scalp while preserving the cheek and eye silhouette.',1)

# v9.2 reached too far toward the face but stopped vertically above the ear. Re-center the shell
# toward the rear hemisphere so it can safely descend through the anatomical ear zone.
old="angles=[-.72+1.46*i/arc_segments for i in range(arc_segments+1)]"
new="angles=[-1.12+1.28*i/arc_segments for i in range(arc_segments+1)]"
if old not in s:
    raise SystemExit('v9.3 temporal arc anchor missing')
s=s.replace(old,new,1)

old_rows=""" add_temporal_shell_v92(HEAD,f'TemporalHairShellV92_{side}',side,[
  (.176,head_w*.390,head_d*.338,-head_d*.018),
  (.151,head_w*.455,head_d*.405,-head_d*.024),
  (.121,head_w*.492,head_d*.455,-head_d*.030),
  (.090,head_w*.505,head_d*.470,-head_d*.036),
  (.062,head_w*.474,head_d*.438,-head_d*.041),
  (.044,head_w*.425,head_d*.392,-head_d*.044)
 ],HAIR,18)"""
new_rows=""" add_temporal_shell_v92(HEAD,f'TemporalHairShellV93_{side}',side,[
  (.178,head_w*.405,head_d*.365,-head_d*.020),
  (.150,head_w*.470,head_d*.430,-head_d*.028),
  (.118,head_w*.515,head_d*.485,-head_d*.036),
  (.083,head_w*.542,head_d*.520,-head_d*.044),
  (.048,head_w*.548,head_d*.535,-head_d*.051),
  (.014,head_w*.535,head_d*.535,-head_d*.057),
  (-.018,head_w*.510,head_d*.520,-head_d*.062),
  (-.046,head_w*.468,head_d*.495,-head_d*.066),
  (-.066,head_w*.420,head_d*.455,-head_d*.068)
 ],HAIR,22)"""
if old_rows not in s:
    raise SystemExit('v9.3 temporal rows anchor missing')
s=s.replace(old_rows,new_rows,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V93: lower rear-biased temporal coverage closes ear-zone scalp exposure')
