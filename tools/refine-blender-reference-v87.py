from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V87' in s:
    print('Blender heroine generator already carries REFERENCE_V87')
    raise SystemExit(0)
if '# REFERENCE_V86' not in s:
    raise SystemExit('REFERENCE_V86 generator required before v8.7')

s=s.replace(
    '# REFERENCE_V86: high-sample Catmull-Clark fringe surfaces for smooth production hair silhouette.',
    '# REFERENCE_V86: high-sample Catmull-Clark fringe surfaces for smooth production hair silhouette.\n# REFERENCE_V87: unified two-layer side sweep; crown root folded into the main fringe instead of a third fin.',
    1,
)

old="""# v8.5: two overlapping convex surfaces form a coherent side-swept fringe instead of rope-like locks.
add_fringe_surface_v85(HEAD,'FringeSurfaceV85_Main',[(-.108,.194,.034),(-.092,.177,.060),(-.064,.154,.083),(-.026,.130,.099),(.020,.110,.105),(.072,.096,.106)],[.094,.100,.096,.082,.060,.025],[.0050,.0062,.0068,.0056,.0038,.0017],HAIR,.0034)
add_fringe_surface_v85(HEAD,'FringeSurfaceV85_Over',[(-.040,.199,.030),(-.022,.181,.055),(.006,.158,.079),(.042,.135,.097),(.082,.115,.103),(.116,.102,.103)],[.070,.076,.072,.060,.040,.017],[.0042,.0054,.0059,.0050,.0034,.0013],HAIR_HI,.0031)
# A compact root overlap seals the crown/front junction while remaining visibly part of the same hair sheet.
add_fringe_surface_v85(HEAD,'FringeSurfaceV85_Root',[(-.066,.202,.036),(-.048,.190,.061),(-.025,.176,.082),(.003,.163,.097)],[.070,.076,.066,.030],[.0046,.0054,.0050,.0025],HAIR,.0032)
"""
new="""# v8.7: one broad scalp-following sweep carries the crown/root volume itself; a narrower upper
# layer only adds direction and highlight. This removes the three-fin silhouette from v8.5/v8.6.
add_fringe_surface_v85(HEAD,'FringeSurfaceV87_Main',[(-.082,.204,.032),(-.076,.192,.047),(-.064,.175,.066),(-.043,.155,.083),(-.014,.136,.097),(.022,.119,.105),(.060,.107,.108),(.094,.101,.106)],[.118,.122,.119,.111,.098,.078,.050,.018],[.0046,.0052,.0058,.0061,.0058,.0048,.0032,.0012],HAIR,.0033)
add_fringe_surface_v85(HEAD,'FringeSurfaceV87_Over',[(-.034,.202,.034),(-.026,.188,.052),(-.009,.170,.071),(.016,.151,.088),(.047,.134,.100),(.080,.120,.106),(.110,.112,.104)],[.070,.074,.073,.068,.057,.036,.012],[.0038,.0045,.0050,.0052,.0045,.0030,.0010],HAIR_HI,.0028)
"""
if old not in s:
    raise SystemExit('v8.7 v8.6 fringe surface block missing')
s=s.replace(old,new,1)

old_fine="""add_strand(HEAD,'FringeFineV85_A',[(-.102,.187,.043),(-.062,.157,.084),(.026,.112,.108)],.000050,HAIR_HI)
add_strand(HEAD,'FringeFineV85_B',[(-.052,.194,.040),(.002,.160,.081),(.090,.113,.105)],.000048,HAIR_HI)
add_strand(HEAD,'FringeFineV85_C',[(-.090,.194,.040),(-.042,.172,.074),(.046,.129,.103)],.000044,HAIR_HI)
"""
new_fine="""# Two hair-direction accents are enough once the mass reads as a single sweep.
add_strand(HEAD,'FringeFineV87_A',[(-.078,.193,.050),(-.038,.157,.086),(.032,.121,.108)],.000042,HAIR_HI)
add_strand(HEAD,'FringeFineV87_B',[(-.028,.193,.047),(.018,.158,.084),(.090,.119,.105)],.000040,HAIR_HI)
"""
if old_fine not in s:
    raise SystemExit('v8.7 fine fringe block missing')
s=s.replace(old_fine,new_fine,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V87: unified two-layer side sweep with integrated crown root')
