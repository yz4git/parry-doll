from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V144' in s:
    print('Blender heroine generator already carries REFERENCE_V144')
    raise SystemExit(0)
if '# REFERENCE_V143' not in s:
    raise SystemExit('REFERENCE_V143 generator required before v13.14')

marker="# REFERENCE_V143: natural-neck profile pass replaces the mannequin cylinder with a tapered asymmetric neck shell that slopes rearward from jaw to collar, matching the supplied elegant side silhouette."
if marker not in s:
    raise SystemExit('v13.14 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V144: ear-anatomy/layered-hair pass gives the exposed ear shallow 3D concha/tragus structure and overlays narrow swept crown/temple locks so the supplied profile reads as layered dark-brown hair instead of a smooth helmet mass.",1)

# Add restrained 3D ear anatomy after the canonical earring. The pieces stay shallow so they improve
# highlight/shadow readability without turning the ear into a dark decal at iPhone scale.
anchor=""" add_box(HEAD,f'EarringTipV137_{side}',(side*.1460,-.075,-.010),(.0045,.010,.0045),SILVER,.0015)
"""
if anchor not in s:
    raise SystemExit('v13.14 ear insertion anchor missing')
insert=""" add_sphere(HEAD,f'EarConchaBowlV144_{side}',(side*.1451,-.020,-.016),(.0023,.0128,.0064),EAR_SHADOW,22,14)
 add_sphere(HEAD,f'EarTragusV144_{side}',(side*.1460,-.019,-.0065),(.0022,.0048,.0034),SKIN,20,12)
 add_strand(HEAD,f'EarAntihelixV144_{side}',[
  (side*.1455,-.003,-.017),
  (side*.1458,-.012,-.012),
  (side*.1457,-.022,-.013),
  (side*.1453,-.032,-.018)
 ],.00016,EAR_SHADOW)
 add_strand(HEAD,f'EarLobeFoldV144_{side}',[
  (side*.1449,-.035,-.022),
  (side*.1443,-.042,-.025),
  (side*.1434,-.047,-.024)
 ],.00011,EAR_SHADOW)
"""
s=s.replace(anchor,anchor+insert,1)

# Overlay narrow swept locks on the existing crown/temple mass. These are deliberately shallow and
# asymmetric: they create strand grouping and specular breakup without increasing the overall head width.
anchor="# v9.0: the fringe is born inside the existing crown cap instead of being patched to it with blobs."
if anchor not in s:
    raise SystemExit('v13.14 crown layer insertion anchor missing')
insert="""# v13.14 reference-style layered crown and temple grouping.
_crown_layers_v144=[
 ('L0',[(-.020,.211,.012),(-.052,.199,.025),(-.084,.180,.024),(-.110,.151,.006),(-.119,.118,-.024)]),
 ('L1',[(-.004,.216,.002),(-.038,.205,.018),(-.073,.188,.028),(-.105,.161,.016),(-.119,.129,-.013)]),
 ('R0',[(.020,.211,.010),(.052,.199,.024),(.082,.181,.025),(.105,.154,.008),(.116,.121,-.022)]),
 ('R1',[(.004,.215,.000),(.038,.204,.017),(.071,.187,.027),(.101,.159,.015),(.116,.127,-.012)])
]
for _name,_pts in _crown_layers_v144:
 add_smooth_lock(HEAD,f'CrownLayerV144_{_name}',_pts,[.0018,.0068,.0090,.0064,.0012],[.0014,.0034,.0044,.0032,.0010],HAIR_HI if _name.endswith('1') else HAIR,12,5)

for _side in (-1,1):
 add_smooth_lock(HEAD,f'TempleRibbonV144_A_{_side}',[
  (_side*head_w*.330,.174,head_d*.016),
  (_side*head_w*.382,.145,-head_d*.004),
  (_side*head_w*.418,.110,-head_d*.030),
  (_side*head_w*.432,.070,-head_d*.061),
  (_side*head_w*.421,.030,-head_d*.098),
  (_side*head_w*.394,-.004,-head_d*.128)
 ],[.0015,.0052,.0070,.0064,.0040,.0008],[.0018,.0040,.0052,.0048,.0030,.0008],HAIR_HI,12,5)
 add_smooth_lock(HEAD,f'TempleRibbonV144_B_{_side}',[
  (_side*head_w*.300,.168,head_d*.005),
  (_side*head_w*.352,.136,-head_d*.016),
  (_side*head_w*.391,.099,-head_d*.041),
  (_side*head_w*.409,.057,-head_d*.071),
  (_side*head_w*.400,.015,-head_d*.104)
 ],[.0012,.0044,.0061,.0051,.0007],[.0015,.0034,.0045,.0038,.0007],HAIR,12,5)
 add_strand(HEAD,f'TempleFineV144_A_{_side}',[(_side*head_w*.318,.160,head_d*.012),(_side*head_w*.367,.126,-head_d*.012),(_side*head_w*.405,.086,-head_d*.044),(_side*head_w*.420,.043,-head_d*.080),(_side*head_w*.404,.002,-head_d*.113)],.000024,HAIR_HI)
 add_strand(HEAD,f'TempleFineV144_B_{_side}',[(_side*head_w*.286,.154,head_d*.002),(_side*head_w*.338,.119,-head_d*.022),(_side*head_w*.382,.079,-head_d*.050),(_side*head_w*.397,.036,-head_d*.083)],.000018,HAIR)

"""
s=s.replace(anchor,insert+anchor,1)

old="ROOT['character_revision']='v13.13';"
new="ROOT['character_revision']='v13.14';"
if old not in s:
    raise SystemExit('v13.14 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.13'","HEAD_ASSET['reference_profile_silhouette']='v13.14'",1)
s=s.replace("HAIR_ASSET['reference_profile_hair_revision']='v13.12'","HAIR_ASSET['reference_profile_hair_revision']='v13.14'",1)
s=s.replace("HAIR_ASSET['temple_sweep_revision']='v13.12'","HAIR_ASSET['temple_sweep_revision']='v13.14'",1)
# Record the detail pass without disturbing the established expression/eye metadata.
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['ear_anatomy_revision']='v13.14';HAIR_ASSET['layered_strand_revision']='v13.14';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V144: shallow 3D ear anatomy plus layered crown/temple hair grouping')
