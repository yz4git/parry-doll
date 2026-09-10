from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V99' in s:
    print('Blender heroine generator already carries REFERENCE_V99')
    raise SystemExit(0)
if '# REFERENCE_V98' not in s:
    raise SystemExit('REFERENCE_V98 generator required before v9.9')

marker='# REFERENCE_V98: a hidden convex temporal root underlay fills the fringe-to-side-lock scalp gap while preserving the canonical ears.'
if marker not in s:
    raise SystemExit('v9.9 REFERENCE_V98 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V99: side-hair roots stay substantial through the ear line, then taper behind the jaw instead of opening a large bare temporal patch.',1)

old_under=""" add_temporal_leaf_v95(HEAD,f'TemporalRootUnderlayV98_{side}',side,[
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
new_under=""" add_temporal_leaf_v95(HEAD,f'TemporalRootUnderlayV99_{side}',side,[
  (.170,head_w*.385, head_d*.042,.004,.0008),
  (.151,head_w*.440, head_d*.040,.024,.0021),
  (.128,head_w*.492, head_d*.034,.043,.0036),
  (.102,head_w*.530, head_d*.024,.058,.0048),
  (.075,head_w*.552, head_d*.010,.067,.0058),
  (.050,head_w*.560,-head_d*.004,.070,.0060),
  (.026,head_w*.558,-head_d*.020,.067,.0058),
  (.004,head_w*.550,-head_d*.038,.060,.0052),
  (-.018,head_w*.536,-head_d*.058,.050,.0044),
  (-.038,head_w*.516,-head_d*.078,.039,.0035),
  (-.056,head_w*.490,-head_d*.098,.027,.0026),
  (-.070,head_w*.458,-head_d*.116,.014,.0016),
  (-.078,head_w*.430,-head_d*.126,.004,.0007)
 ],HAIR,15)
"""
if old_under not in s:
    raise SystemExit('v9.9 v9.8 underlay block missing')
s=s.replace(old_under,new_under,1)

old_front=""" add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Front_{side}',side,[
  (.188,head_w*.365, head_d*.030,.003,.0010),
  (.163,head_w*.430, head_d*.022,.015,.0020),
  (.132,head_w*.485, head_d*.012,.027,.0030),
  (.095,head_w*.515, head_d*.000,.036,.0035),
  (.056,head_w*.520,-head_d*.018,.035,.0032),
  (.020,head_w*.505,-head_d*.035,.026,.0024),
  (-.012,head_w*.470,-head_d*.050,.013,.0014),
  (-.030,head_w*.435,-head_d*.058,.003,.0006)
 ],HAIR,9)
"""
new_front=""" add_temporal_leaf_v95(HEAD,f'TemporalLeafV99_Front_{side}',side,[
  (.188,head_w*.365, head_d*.030,.003,.0010),
  (.163,head_w*.430, head_d*.022,.016,.0020),
  (.132,head_w*.485, head_d*.012,.029,.0030),
  (.095,head_w*.515, head_d*.000,.039,.0036),
  (.056,head_w*.520,-head_d*.018,.040,.0035),
  (.020,head_w*.515,-head_d*.035,.036,.0030),
  (-.012,head_w*.502,-head_d*.052,.029,.0025),
  (-.038,head_w*.482,-head_d*.068,.020,.0019),
  (-.058,head_w*.458,-head_d*.080,.011,.0012),
  (-.070,head_w*.438,-head_d*.086,.003,.0006)
 ],HAIR,11)
"""
if old_front not in s:
    raise SystemExit('v9.9 front temporal leaf block missing')
s=s.replace(old_front,new_front,1)

old_mid=""" add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Mid_{side}',side,[
  (.186,head_w*.350,-head_d*.030,.003,.0009),
  (.158,head_w*.425,-head_d*.040,.016,.0018),
  (.124,head_w*.485,-head_d*.052,.030,.0029),
  (.084,head_w*.520,-head_d*.066,.039,.0035),
  (.042,head_w*.525,-head_d*.082,.039,.0033),
  (.004,head_w*.510,-head_d*.098,.030,.0025),
  (-.030,head_w*.480,-head_d*.112,.016,.0015),
  (-.050,head_w*.445,-head_d*.120,.003,.0006)
 ],HAIR,9)
"""
new_mid=""" add_temporal_leaf_v95(HEAD,f'TemporalLeafV99_Mid_{side}',side,[
  (.186,head_w*.350,-head_d*.030,.003,.0009),
  (.158,head_w*.425,-head_d*.040,.017,.0019),
  (.124,head_w*.485,-head_d*.052,.032,.0030),
  (.084,head_w*.520,-head_d*.066,.042,.0037),
  (.042,head_w*.530,-head_d*.082,.043,.0036),
  (.004,head_w*.522,-head_d*.100,.038,.0030),
  (-.032,head_w*.505,-head_d*.120,.030,.0024),
  (-.060,head_w*.482,-head_d*.138,.020,.0018),
  (-.080,head_w*.455,-head_d*.151,.010,.0011),
  (-.091,head_w*.430,-head_d*.158,.003,.0005)
 ],HAIR,11)
"""
if old_mid not in s:
    raise SystemExit('v9.9 mid temporal leaf block missing')
s=s.replace(old_mid,new_mid,1)

old_rear=""" add_temporal_leaf_v95(HEAD,f'TemporalLeafV95_Rear_{side}',side,[
  (.178,head_w*.330,-head_d*.090,.003,.0008),
  (.150,head_w*.405,-head_d*.105,.014,.0017),
  (.116,head_w*.468,-head_d*.122,.027,.0027),
  (.076,head_w*.505,-head_d*.140,.035,.0032),
  (.034,head_w*.515,-head_d*.158,.034,.0030),
  (-.004,head_w*.500,-head_d*.174,.025,.0022),
  (-.034,head_w*.468,-head_d*.187,.012,.0012),
  (-.052,head_w*.435,-head_d*.194,.003,.0005)
 ],HAIR,9)
"""
new_rear=""" add_temporal_leaf_v95(HEAD,f'TemporalLeafV99_Rear_{side}',side,[
  (.178,head_w*.330,-head_d*.090,.003,.0008),
  (.150,head_w*.405,-head_d*.105,.015,.0018),
  (.116,head_w*.468,-head_d*.122,.029,.0028),
  (.076,head_w*.505,-head_d*.140,.038,.0034),
  (.034,head_w*.520,-head_d*.158,.039,.0033),
  (-.004,head_w*.514,-head_d*.176,.035,.0028),
  (-.040,head_w*.500,-head_d*.195,.027,.0022),
  (-.068,head_w*.478,-head_d*.210,.018,.0016),
  (-.088,head_w*.452,-head_d*.220,.009,.0010),
  (-.098,head_w*.430,-head_d*.225,.003,.0005)
 ],HAIR,11)
"""
if old_rear not in s:
    raise SystemExit('v9.9 rear temporal leaf block missing')
s=s.replace(old_rear,new_rear,1)

# Extend the subtle direction accent with the same downward flow, but keep it buried on the hair surface.
old_flow=""" add_strand(HEAD,f'TemporalFlowV96_{side}',[
  (side*head_w*.486,.142,-head_d*.052),
  (side*head_w*.526,.078,-head_d*.078),
  (side*head_w*.510,.010,-head_d*.108),
  (side*head_w*.474,-.030,-head_d*.124)
 ],.000040,HAIR_HI)
"""
new_flow=""" add_strand(HEAD,f'TemporalFlowV99_{side}',[
  (side*head_w*.486,.142,-head_d*.052),
  (side*head_w*.526,.078,-head_d*.078),
  (side*head_w*.520,.012,-head_d*.108),
  (side*head_w*.500,-.038,-head_d*.137),
  (side*head_w*.468,-.074,-head_d*.160)
 ],.000036,HAIR_HI)
"""
if old_flow not in s:
    raise SystemExit('v9.9 temporal flow anchor missing')
s=s.replace(old_flow,new_flow,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V99: side-hair roots remain filled through ear line and taper behind jaw')
