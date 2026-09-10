from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V89' in s:
    print('Blender heroine generator already carries REFERENCE_V89')
    raise SystemExit(0)
if '# REFERENCE_V88' not in s:
    raise SystemExit('REFERENCE_V88 generator required before v8.9')

s=s.replace(
    '# REFERENCE_V88: tapered-root side sweep over a scalp-tight undercap, eliminating the v8.7 crown fin and skin notch.',
    '# REFERENCE_V88: tapered-root side sweep over a scalp-tight undercap, eliminating the v8.7 crown fin and skin notch.\n# REFERENCE_V89: zero-width fringe roots plus rounded scalp blends remove closed-end fins and the last hairline notch.',
    1,
)

old="""# v8.8: a quiet scalp-tight undercap closes the hairline first. It stays high on the cranium and
# never projects into the forehead, so it reads as continuous hair mass rather than a third bang.
add_fringe_surface_v85(HEAD,'FringeUnderCapV88',[(-.075,.203,.031),(-.050,.195,.050),(-.018,.184,.069),(.018,.171,.085),(.052,.157,.096)],[.090,.108,.116,.104,.062],[.0018,.0022,.0025,.0023,.0014],HAIR,.0024)
# The visible sweep now starts narrow, gains width only after leaving the crown, and tapers cleanly
# toward the heroine's right temple. This removes the v8.7 triangular crown fin.
add_fringe_surface_v85(HEAD,'FringeSurfaceV88_Main',[(-.094,.201,.035),(-.083,.190,.050),(-.068,.175,.068),(-.046,.157,.085),(-.017,.139,.099),(.018,.122,.106),(.055,.109,.109),(.090,.101,.106)],[.042,.068,.088,.096,.090,.073,.047,.015],[.0030,.0040,.0050,.0058,.0055,.0044,.0028,.0010],HAIR,.0030)
add_fringe_surface_v85(HEAD,'FringeSurfaceV88_Over',[(-.050,.199,.037),(-.038,.186,.054),(-.020,.169,.073),(.004,.151,.090),(.034,.135,.101),(.067,.121,.107),(.099,.112,.104)],[.032,.050,.063,.066,.057,.036,.011],[.0026,.0034,.0043,.0047,.0040,.0027,.0009],HAIR_HI,.0025)
# Hair-direction accents follow the tapered surface and never bridge exposed skin.
add_strand(HEAD,'FringeFineV88_A',[(-.084,.190,.052),(-.047,.158,.086),(.026,.122,.108)],.000038,HAIR_HI)
add_strand(HEAD,'FringeFineV88_B',[(-.040,.187,.055),(.004,.153,.090),(.080,.120,.106)],.000036,HAIR_HI)
"""
new="""# v8.9: rounded root blends seal the scalp/hairline without exposing a rectangular strip edge.
# These low ellipsoids sit under the visible sweep and read as scalp volume from front and profile.
add_sphere(HEAD,'FringeRootBlendV89_A',(-.035,.181,.081),(.055,.027,.0105),HAIR,30,18)
add_sphere(HEAD,'FringeRootBlendV89_B',(.020,.164,.094),(.050,.024,.0085),HAIR,30,18)
# Visible surfaces now begin at almost zero width inside the crown. Their closed start caps are therefore
# sub-pixel in portrait views instead of becoming the vertical triangular fins seen in v8.7-v8.8.
add_fringe_surface_v85(HEAD,'FringeSurfaceV89_Main',[(-.105,.207,.027),(-.096,.201,.036),(-.084,.190,.051),(-.068,.175,.069),(-.046,.157,.086),(-.017,.139,.100),(.018,.122,.107),(.055,.109,.109),(.090,.101,.106)],[.006,.024,.056,.084,.101,.097,.076,.047,.014],[.0010,.0022,.0035,.0047,.0055,.0052,.0042,.0026,.0008],HAIR,.0028)
add_fringe_surface_v85(HEAD,'FringeSurfaceV89_Over',[(-.061,.204,.030),(-.052,.198,.038),(-.039,.186,.055),(-.020,.169,.074),(.004,.151,.091),(.034,.135,.102),(.067,.121,.107),(.099,.112,.104)],[.005,.018,.043,.061,.069,.060,.037,.010],[.0008,.0018,.0030,.0040,.0045,.0039,.0025,.0007],HAIR_HI,.0023)
# Fine directional accents stay fully on top of the visible mass.
add_strand(HEAD,'FringeFineV89_A',[(-.087,.191,.052),(-.048,.159,.087),(.026,.122,.108)],.000036,HAIR_HI)
add_strand(HEAD,'FringeFineV89_B',[(-.043,.187,.056),(.004,.153,.091),(.080,.120,.106)],.000034,HAIR_HI)
"""
if old not in s:
    raise SystemExit('v8.9 v8.8 fringe block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V89: zero-width roots, rounded scalp blends, closed final hairline notch')
