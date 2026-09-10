from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V90' in s:
    print('Blender heroine generator already carries REFERENCE_V90')
    raise SystemExit(0)
if '# REFERENCE_V89' not in s:
    raise SystemExit('REFERENCE_V89 generator required before v9.0')

s=s.replace(
    '# REFERENCE_V89: zero-width fringe roots plus rounded scalp blends remove closed-end fins and the last hairline notch.',
    '# REFERENCE_V89: zero-width fringe roots plus rounded scalp blends remove closed-end fins and the last hairline notch.\n# REFERENCE_V90: crown-buried zero-width roots replace filler blobs and create continuous hair-cap/fringe overlap.',
    1,
)

old="""# v8.9: rounded root blends seal the scalp/hairline without exposing a rectangular strip edge.
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
new="""# v9.0: the fringe is born inside the existing crown cap instead of being patched to it with blobs.
# The first two samples are narrow and hidden under the cap; width only opens after the path exits the crown.
add_fringe_surface_v85(HEAD,'FringeSurfaceV90_Main',[(-.008,.214,.004),(-.028,.207,.019),(-.050,.199,.036),(-.070,.188,.053),(-.076,.174,.070),(-.057,.157,.087),(-.025,.139,.101),(.012,.122,.108),(.052,.109,.110),(.090,.101,.106)],[.004,.010,.026,.052,.082,.101,.098,.078,.047,.014],[.0004,.0008,.0016,.0030,.0044,.0053,.0050,.0040,.0025,.0008],HAIR,.0027)
add_fringe_surface_v85(HEAD,'FringeSurfaceV90_Over',[(.004,.211,.006),(-.010,.204,.021),(-.028,.197,.039),(-.041,.186,.056),(-.028,.169,.075),(-.002,.151,.092),(.030,.135,.102),(.065,.121,.107),(.099,.112,.104)],[.003,.008,.019,.040,.060,.069,.060,.037,.010],[.0003,.0007,.0015,.0028,.0039,.0044,.0038,.0024,.0007],HAIR_HI,.0022)
# Direction lines start only after the root is already covered by the crown cap.
add_strand(HEAD,'FringeFineV90_A',[(-.067,.188,.054),(-.050,.159,.088),(.024,.122,.109)],.000034,HAIR_HI)
add_strand(HEAD,'FringeFineV90_B',[(-.039,.186,.057),(.000,.153,.092),(.078,.120,.106)],.000032,HAIR_HI)
"""
if old not in s:
    raise SystemExit('v9.0 v8.9 fringe block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V90: crown-buried roots, no filler blobs, continuous scalp/fringe join')
