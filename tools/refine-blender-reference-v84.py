from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V84' in s:
    print('Blender heroine generator already carries REFERENCE_V84')
    raise SystemExit(0)
if '# REFERENCE_V83' not in s:
    raise SystemExit('REFERENCE_V83 generator required before v8.4')

s=s.replace(
    '# REFERENCE_V83: +10% mature almond aperture, lower side-swept fringe and clean temple silhouette.',
    '# REFERENCE_V83: +10% mature almond aperture, lower side-swept fringe and clean temple silhouette.\n# REFERENCE_V84: overlap-closed front fringe with the v8.3 face and eye proportions frozen.',
    1,
)

old_a="""add_smooth_lock(HEAD,'FringeMassV83_A',[(-.098,.190,.030),(-.084,.173,.056),(-.060,.151,.080),(-.026,.127,.099),(.018,.108,.106),(.066,.094,.107)],[.054,.058,.054,.043,.028,.010],[.019,.020,.018,.014,.009,.004],HAIR,14,6)
"""
new_a="""add_smooth_lock(HEAD,'FringeMassV84_A',[(-.098,.190,.030),(-.084,.173,.056),(-.060,.151,.080),(-.026,.127,.101),(.018,.108,.108),(.066,.094,.107)],[.056,.061,.059,.058,.040,.012],[.020,.021,.020,.016,.011,.004],HAIR,14,6)
"""
if old_a not in s: raise SystemExit('v8.4 fringe A anchor missing')
s=s.replace(old_a,new_a,1)

old_b="""add_smooth_lock(HEAD,'FringeMassV83_B',[(-.040,.194,.026),(-.020,.178,.053),(.010,.156,.078),(.048,.132,.098),(.086,.111,.105),(.118,.098,.104)],[.046,.048,.043,.033,.021,.008],[.017,.018,.016,.012,.007,.003],HAIR,14,6)
"""
new_b="""add_smooth_lock(HEAD,'FringeMassV84_B',[(-.040,.194,.026),(-.020,.178,.053),(.010,.156,.080),(.044,.132,.102),(.084,.111,.107),(.118,.098,.104)],[.048,.051,.048,.050,.030,.009],[.018,.019,.018,.015,.009,.003],HAIR,14,6)
"""
if old_b not in s: raise SystemExit('v8.4 fringe B anchor missing')
s=s.replace(old_b,new_b,1)

# Slightly broaden the accent where the two main masses meet so the underlayer never exposes skin,
# but keep its lower tip narrow enough that it cannot become a flat horizontal fringe card.
old_c="""add_smooth_lock(HEAD,'FringeAccentV83',[(-.116,.185,.025),(-.098,.166,.052),(-.072,.145,.077),(-.038,.124,.096),(.002,.110,.104)],[.028,.030,.027,.020,.007],[.011,.011,.010,.007,.003],HAIR_HI,12,5)
"""
new_c="""add_smooth_lock(HEAD,'FringeAccentV84',[(-.116,.185,.025),(-.098,.166,.052),(-.072,.145,.079),(-.036,.124,.101),(.006,.110,.106)],[.030,.033,.032,.029,.009],[.012,.012,.011,.009,.003],HAIR_HI,12,5)
"""
if old_c not in s: raise SystemExit('v8.4 fringe accent anchor missing')
s=s.replace(old_c,new_c,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V84: closed front fringe overlap while freezing the v8.3 face')
