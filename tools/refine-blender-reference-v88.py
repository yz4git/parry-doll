from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V88' in s:
    print('Blender heroine generator already carries REFERENCE_V88')
    raise SystemExit(0)
if '# REFERENCE_V87' not in s:
    raise SystemExit('REFERENCE_V87 generator required before v8.8')

s=s.replace(
    '# REFERENCE_V87: unified two-layer side sweep; crown root folded into the main fringe instead of a third fin.',
    '# REFERENCE_V87: unified two-layer side sweep; crown root folded into the main fringe instead of a third fin.\n# REFERENCE_V88: tapered-root side sweep over a scalp-tight undercap, eliminating the v8.7 crown fin and skin notch.',
    1,
)

old="""# v8.7: one broad scalp-following sweep carries the crown/root volume itself; a narrower upper
# layer only adds direction and highlight. This removes the three-fin silhouette from v8.5/v8.6.
add_fringe_surface_v85(HEAD,'FringeSurfaceV87_Main',[(-.082,.204,.032),(-.076,.192,.047),(-.064,.175,.066),(-.043,.155,.083),(-.014,.136,.097),(.022,.119,.105),(.060,.107,.108),(.094,.101,.106)],[.118,.122,.119,.111,.098,.078,.050,.018],[.0046,.0052,.0058,.0061,.0058,.0048,.0032,.0012],HAIR,.0033)
add_fringe_surface_v85(HEAD,'FringeSurfaceV87_Over',[(-.034,.202,.034),(-.026,.188,.052),(-.009,.170,.071),(.016,.151,.088),(.047,.134,.100),(.080,.120,.106),(.110,.112,.104)],[.070,.074,.073,.068,.057,.036,.012],[.0038,.0045,.0050,.0052,.0045,.0030,.0010],HAIR_HI,.0028)
"""
new="""# v8.8: a quiet scalp-tight undercap closes the hairline first. It stays high on the cranium and
# never projects into the forehead, so it reads as continuous hair mass rather than a third bang.
add_fringe_surface_v85(HEAD,'FringeUnderCapV88',[(-.075,.203,.031),(-.050,.195,.050),(-.018,.184,.069),(.018,.171,.085),(.052,.157,.096)],[.090,.108,.116,.104,.062],[.0018,.0022,.0025,.0023,.0014],HAIR,.0024)
# The visible sweep now starts narrow, gains width only after leaving the crown, and tapers cleanly
# toward the heroine's right temple. This removes the v8.7 triangular crown fin.
add_fringe_surface_v85(HEAD,'FringeSurfaceV88_Main',[(-.094,.201,.035),(-.083,.190,.050),(-.068,.175,.068),(-.046,.157,.085),(-.017,.139,.099),(.018,.122,.106),(.055,.109,.109),(.090,.101,.106)],[.042,.068,.088,.096,.090,.073,.047,.015],[.0030,.0040,.0050,.0058,.0055,.0044,.0028,.0010],HAIR,.0030)
add_fringe_surface_v85(HEAD,'FringeSurfaceV88_Over',[(-.050,.199,.037),(-.038,.186,.054),(-.020,.169,.073),(.004,.151,.090),(.034,.135,.101),(.067,.121,.107),(.099,.112,.104)],[.032,.050,.063,.066,.057,.036,.011],[.0026,.0034,.0043,.0047,.0040,.0027,.0009],HAIR_HI,.0025)
"""
if old not in s:
    raise SystemExit('v8.8 v8.7 fringe block missing')
s=s.replace(old,new,1)

old_fine="""# Two hair-direction accents are enough once the mass reads as a single sweep.
add_strand(HEAD,'FringeFineV87_A',[(-.078,.193,.050),(-.038,.157,.086),(.032,.121,.108)],.000042,HAIR_HI)
add_strand(HEAD,'FringeFineV87_B',[(-.028,.193,.047),(.018,.158,.084),(.090,.119,.105)],.000040,HAIR_HI)
"""
new_fine="""# Hair-direction accents follow the tapered surface and never bridge exposed skin.
add_strand(HEAD,'FringeFineV88_A',[(-.084,.190,.052),(-.047,.158,.086),(.026,.122,.108)],.000038,HAIR_HI)
add_strand(HEAD,'FringeFineV88_B',[(-.040,.187,.055),(.004,.153,.090),(.080,.120,.106)],.000036,HAIR_HI)
"""
if old_fine not in s:
    raise SystemExit('v8.8 fine fringe block missing')
s=s.replace(old_fine,new_fine,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V88: tapered visible sweep over a scalp-tight undercap')
