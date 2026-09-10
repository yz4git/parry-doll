from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V101' in s:
    print('Blender heroine generator already carries REFERENCE_V101')
    raise SystemExit(0)
if '# REFERENCE_V100' not in s:
    raise SystemExit('REFERENCE_V100 generator required before v10.1')

marker='# REFERENCE_V100: adult portrait reset reduces oversized doll eyes and tightens the lower-face silhouette while preserving the established profile and hair.'
if marker not in s:
    raise SystemExit('v10.1 REFERENCE_V100 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V101: side hair becomes a scalp-tight undercap plus several rounded swept locks, replacing the large profile-facing leaf plate.',1)

start=s.index('# v9.8 root underlay:')
end=s.index('# v9.0: the fringe is born', start)
new_block="""# v10.1: a scalp-tight undercap provides dark root coverage without becoming the visible silhouette.
# head_w is the full measured head width, so ~0.46*head_w tracks the actual cranium instead of floating far outside it.
for side in (-1,1):
 add_temporal_leaf_v95(HEAD,f'TemporalUnderCapV101_{side}',side,[
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

 # Rounded swept locks sit above the undercap. Each covers only a narrow front/back band, so profile reads as layered hair.
 add_smooth_lock(HEAD,f'TemporalLockV101_Front_{side}',[
  (side*head_w*.350,.174, head_d*.026),
  (side*head_w*.420,.145, head_d*.018),
  (side*head_w*.468,.108, head_d*.006),
  (side*head_w*.486,.068,-head_d*.010),
  (side*head_w*.482,.028,-head_d*.027),
  (side*head_w*.466,-.006,-head_d*.043),
  (side*head_w*.438,-.032,-head_d*.055)
 ],[.003,.006,.009,.010,.009,.006,.0015],[.007,.012,.016,.019,.017,.011,.0035],HAIR,14,6)

 add_smooth_lock(HEAD,f'TemporalLockV101_Mid_{side}',[
  (side*head_w*.344,.170,-head_d*.030),
  (side*head_w*.410,.139,-head_d*.041),
  (side*head_w*.462,.101,-head_d*.056),
  (side*head_w*.490,.059,-head_d*.073),
  (side*head_w*.489,.016,-head_d*.091),
  (side*head_w*.470,-.020,-head_d*.108),
  (side*head_w*.440,-.048,-head_d*.121)
 ],[.003,.006,.009,.011,.010,.006,.0015],[.008,.014,.019,.022,.020,.013,.004],HAIR,14,6)

 add_smooth_lock(HEAD,f'TemporalLockV101_Rear_{side}',[
  (side*head_w*.332,.164,-head_d*.082),
  (side*head_w*.392,.132,-head_d*.096),
  (side*head_w*.448,.094,-head_d*.113),
  (side*head_w*.480,.051,-head_d*.132),
  (side*head_w*.482,.008,-head_d*.151),
  (side*head_w*.463,-.030,-head_d*.168),
  (side*head_w*.432,-.058,-head_d*.181)
 ],[.003,.006,.009,.011,.010,.006,.0015],[.008,.014,.020,.023,.020,.013,.004],HAIR,14,6)

 # One very fine highlight follows the flow; no whole lock is tinted brown.
 add_strand(HEAD,f'TemporalFlowV101_{side}',[
  (side*head_w*.445,.142,-head_d*.055),
  (side*head_w*.482,.090,-head_d*.078),
  (side*head_w*.488,.036,-head_d*.101),
  (side*head_w*.468,-.012,-head_d*.124),
  (side*head_w*.438,-.046,-head_d*.142)
 ],.000032,HAIR_HI)

"""
s=s[:start]+new_block+s[end:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V101: scalp-tight undercap with layered rounded temporal locks')
