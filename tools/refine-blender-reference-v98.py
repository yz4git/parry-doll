from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V98' in s:
    print('Blender heroine generator already carries REFERENCE_V98')
    raise SystemExit(0)
if '# REFERENCE_V97' not in s:
    raise SystemExit('REFERENCE_V97 generator required before v9.8')

marker='# REFERENCE_V97: rear hair shell wraps forward around both temples; duplicate v9.6 ears are removed while the original EarV78 anatomy remains.'
if marker not in s:
    raise SystemExit('v9.8 REFERENCE_V97 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V98: a hidden convex temporal root underlay fills the fringe-to-side-lock scalp gap while preserving the canonical ears.',1)

anchor="""add_rear_hair_shell(HEAD,'HairRearShellV59',[
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
if anchor not in s:
    raise SystemExit('v9.8 rear-shell call anchor missing')
addition=anchor+"""# v9.8 root underlay: this is intentionally broad but sits underneath the visible v9.5 leaves.
# It covers only the upper side scalp and tapers out above the ear, preventing a helmet panel or ear-pad read.
for side in (-1,1):
 add_temporal_leaf_v95(HEAD,f'TemporalRootUnderlayV98_{side}',side,[
  (.170,head_w*.385, head_d*.042,.004,.0008),
  (.151,head_w*.440, head_d*.040,.022,.0020),
  (.128,head_w*.492, head_d*.035,.040,.0034),
  (.102,head_w*.530, head_d*.026,.055,.0046),
  (.075,head_w*.552, head_d*.014,.064,.0056),
  (.050,head_w*.560, head_d*.002,.066,.0058),
  (.029,head_w*.556,-head_d*.010,.058,.0050),
  (.014,head_w*.542,-head_d*.020,.044,.0038),
  (.006,head_w*.520,-head_d*.026,.022,.0020)
 ],HAIR,15)

"""
s=s.replace(anchor,addition,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V98: hidden convex temporal root underlay fills upper side-scalp gap')
