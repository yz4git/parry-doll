from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V82' in s:
    print('Blender heroine generator already carries REFERENCE_V82')
    raise SystemExit(0)
if '# REFERENCE_V81' not in s:
    raise SystemExit('REFERENCE_V81 generator required before v8.2')

s=s.replace(
    '# REFERENCE_V81: clean cheek silhouette, lifted side wisps and sealed crown root for production portrait readability.',
    '# REFERENCE_V81: clean cheek silhouette, lifted side wisps and sealed crown root for production portrait readability.\n# REFERENCE_V82: artifact-free cheeks, no detached side strands and a front-visible overlapping crown seal.',
    1,
)

old_seal="""add_smooth_lock(HEAD,'CrownRootSealV81',[(.004,.203,.018),(.018,.195,.037),(.034,.184,.055),(.050,.173,.071)],[.034,.032,.024,.009],[.014,.013,.010,.004],HAIR,14,5)
"""
new_seal="""# v8.2 overlaps the exact front crown gap visible in the five-view audit. Two small rounded
# masses sit on the scalp/front transition; neither extends down across the forehead like a card.
add_smooth_lock(HEAD,'CrownRootSealV82_A',[(-.030,.187,.078),(-.016,.180,.092),(0,.172,.101),(.020,.164,.104)],[.033,.038,.032,.009],[.011,.012,.010,.003],HAIR,14,6)
add_smooth_lock(HEAD,'CrownRootSealV82_B',[(.000,.190,.074),(.014,.181,.091),(.032,.170,.101),(.050,.160,.103)],[.028,.031,.024,.007],[.010,.010,.008,.003],HAIR_HI,12,5)
"""
if old_seal not in s:
    raise SystemExit('v8.2 crown seal anchor missing')
s=s.replace(old_seal,new_seal,1)

old_wisps="""for side in(-1,1):
 add_strand(HEAD,f'SideWispV81_{side}',[(side*.124,.118,.103),(side*.132,.075,.106),(side*.136,.022,.104),(side*.132,-.032,.099),(side*.124,-.073,.092)],.000075,HAIR_HI)

"""
new_wisps="""# v8.2 deliberately omits isolated cheek wisps. At portrait scale even a physically thin curve
# reads as a detached black scratch in profile; the existing broad temple/face locks carry the hairstyle.

"""
if old_wisps not in s:
    raise SystemExit('v8.2 side-wisp anchor missing')
s=s.replace(old_wisps,new_wisps,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V82: removed detached cheek strands and sealed the visible crown gap')
