from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V81' in s:
    print('Blender heroine generator already carries REFERENCE_V81')
    raise SystemExit(0)
if '# REFERENCE_V80' not in s:
    raise SystemExit('REFERENCE_V80 generator required before v8.1')

s=s.replace(
    '# REFERENCE_V80: mature flush almond eyes, softened centre profile and rounded side-swept hair masses.',
    '# REFERENCE_V80: mature flush almond eyes, softened centre profile and rounded side-swept hair masses.\n# REFERENCE_V81: clean cheek silhouette, lifted side wisps and sealed crown root for production portrait readability.',
    1,
)

# Seal the tiny skin-coloured crown opening left between the rounded v8.0 locks without returning
# to a flat visor card. This is a short scalp-following volume that disappears into the main cap.
anchor="""add_smooth_lock(HEAD,'FringeAccentV80',[(-.112,.184,.024),(-.092,.169,.050),(-.064,.153,.074),(-.028,.140,.090),(.012,.132,.098)],[.025,.027,.024,.018,.007],[.010,.010,.009,.006,.003],HAIR_HI,12,5)
"""
insert=anchor+"""add_smooth_lock(HEAD,'CrownRootSealV81',[(.004,.203,.018),(.018,.195,.037),(.034,.184,.055),(.050,.173,.071)],[.034,.032,.024,.009],[.014,.013,.010,.004],HAIR,14,5)
"""
if anchor not in s: raise SystemExit('v8.1 fringe accent anchor missing')
s=s.replace(anchor,insert,1)

# v6.3 face wisps sat almost coplanar with the cheek and appeared as dotted/z-clipped vertical marks
# in three-quarter/profile audits. Keep the design cue but route the strand fully outside the face contour.
old="""for side in(-1,1):
 add_strand(HEAD,f'FaceWispV63_{side}',[(side*.105,.124,.094),(side*.116,.072,.101),(side*.120,.010,.099),(side*.112,-.052,.094)],.00010,HAIR_HI)
"""
new="""for side in(-1,1):
 add_strand(HEAD,f'SideWispV81_{side}',[(side*.124,.118,.103),(side*.132,.075,.106),(side*.136,.022,.104),(side*.132,-.032,.099),(side*.124,-.073,.092)],.000075,HAIR_HI)
"""
if old not in s: raise SystemExit('v8.1 face-wisp anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V81: clean cheek silhouette, exterior side wisps, sealed rounded crown root')
