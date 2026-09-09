from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V33' in s:
    print('Blender heroine generator already carries REFERENCE_V33')
    raise SystemExit(0)
if '# REFERENCE_V32' not in s:
    raise SystemExit('REFERENCE_V32 generator required before v3.3')
s=s.replace('# REFERENCE_V32: stronger facial planes and tapered volumetric hair locks.','# REFERENCE_V32: stronger facial planes and tapered volumetric hair locks.\n# REFERENCE_V33: portrait-first facial proportions and layered blade-like hair locks.',1)

# -----------------------------------------------------------------------------
# PORTRAIT: keep a single connected head shell, but tune the envelope toward
# the supplied four-view key art: narrower lower face, stronger cheek break,
# smaller jaw and a slightly pointed chin. No second face patch is introduced.
# -----------------------------------------------------------------------------
a=s.index("add_anatomical_head(HEAD,'HeadShellV31',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_anatomical_head(HEAD,'HeadShellV33',[
 (-.139,head_w*.078,head_d*.150,head_d*.205,.052),
 (-.128,head_w*.175,head_d*.210,head_d*.272,.046),
 (-.114,head_w*.255,head_d*.270,head_d*.330,.038),
 (-.096,head_w*.318,head_d*.312,head_d*.372,.031),
 (-.074,head_w*.372,head_d*.348,head_d*.412,.023),
 (-.050,head_w*.420,head_d*.382,head_d*.449,.014),
 (-.024,head_w*.458,head_d*.414,head_d*.478,.006),
 (.004,head_w*.482,head_d*.438,head_d*.496,-.001),
 (.032,head_w*.490,head_d*.458,head_d*.494,-.006),
 (.060,head_w*.480,head_d*.474,head_d*.476,-.011),
 (.086,head_w*.455,head_d*.480,head_d*.446,-.016),
 (.110,head_w*.418,head_d*.473,head_d*.407,-.021),
 (.131,head_w*.366,head_d*.455,head_d*.358,-.026),
 (.148,head_w*.298,head_d*.425,head_d*.298,-.030)
],SKIN,72)
"""
s=s[:a]+head+s[b:]

# Refine the low-frequency deformations in the anatomical head helper itself.
# Eye sockets become wider/shallower vertically, the cheek plane is stronger,
# and the nose/muzzle/chin read from both front and profile.
a=s.index('def add_anatomical_head(')
b=s.index('def add_lock_mesh(',a)
helper=s[a:b]
repls={
 "z+=fm*.0105*math.exp(-((x-cheek_x)/(head_w*.118))**2-((yy+.006)/.050)**2)":"z+=fm*.0130*math.exp(-((x-cheek_x)/(head_w*.112))**2-((yy+.006)/.052)**2)",
 "z-=fm*.0115*math.exp(-((x-eye_x)/(head_w*.105))**2-((yy-.024)/.030)**2)":"z-=fm*.0135*math.exp(-((x-eye_x)/(head_w*.118))**2-((yy-.024)/.024)**2)",
 "z+=fm*.0050*math.exp(-((x-eye_x)/(head_w*.125))**2-((yy-.070)/.029)**2)":"z+=fm*.0058*math.exp(-((x-eye_x)/(head_w*.130))**2-((yy-.070)/.026)**2)",
 "z+=fm*.0095*math.exp(-(x/(head_w*.062))**2-((yy-.022)/.078)**2)":"z+=fm*.0115*math.exp(-(x/(head_w*.058))**2-((yy-.021)/.082)**2)",
 "z+=fm*.0210*math.exp(-(x/(head_w*.078))**2-((yy+.041)/.025)**2)":"z+=fm*.0245*math.exp(-(x/(head_w*.074))**2-((yy+.040)/.024)**2)",
 "z+=fm*.0044*math.exp(-(x/(head_w*.180))**2-((yy+.082)/.029)**2)":"z+=fm*.0058*math.exp(-(x/(head_w*.165))**2-((yy+.082)/.026)**2)",
 "z+=fm*.0040*math.exp(-(x/(head_w*.145))**2-((yy+.116)/.024)**2)":"z+=fm*.0056*math.exp(-(x/(head_w*.125))**2-((yy+.119)/.022)**2)",
}
for old,new in repls.items():
 if old not in helper: raise SystemExit('v33 anatomical anchor missing: '+old)
 helper=helper.replace(old,new,1)
s=s[:a]+helper+s[b:]

# Portrait features: less circular eye opening, slightly closer-set irises,
# thinner lid curves and a smaller, softer mouth. The eyeballs remain embedded.
a=s.index('# Anatomy v3.1:')
b=s.index('# Hair v3.2:',a)
face=s[a:b]
face=face.replace('eye_x=head_w*.160','eye_x=head_w*.154')
face=face.replace('eye_rx=head_w*.105','eye_rx=head_w*.112')
face=face.replace('eye_ry=.0270','eye_ry=.0208')
face=face.replace('eye_rz=head_d*.078','eye_rz=head_d*.072')
face=face.replace("(head_w*.057,.0128,.0044)","(head_w*.050,.0106,.0042)")
face=face.replace("(head_w*.021,.0072,.0028)","(head_w*.018,.0059,.0026)")
face=face.replace(".0021,SKIN)",".00165,SKIN)")
face=face.replace(".00145,SKIN)",".00115,SKIN)")
face=face.replace(".00155,HAIR)",".00135,HAIR)")
face=face.replace(".0017,HAIR)",".00145,HAIR)")
face=face.replace("(.0063,.0062,.0042)","(.0055,.0057,.0040)")
face=face.replace(".00185,LIP)",".00150,LIP)")
face=face.replace(".00172,LIP)",".00138,LIP)")
s=s[:a]+face+s[b:]

# Slightly calmer skin response helps the facial planes remain readable under
# the bright model-viewer sky instead of clipping toward a flat white mask.
s=s.replace("SKIN=material('Skin',(0.84,0.61,0.54),0,.48)","SKIN=material('Skin',(0.76,0.54,0.49),0,.56)",1)

# -----------------------------------------------------------------------------
# HAIR: replace the seven short rounded bangs with five long blade-like locks
# plus smaller crossing pieces. The cross-sections are deliberately flatter
# than v3.2 so they read as hair masses rather than beads/tubes.
# -----------------------------------------------------------------------------
a=s.index('# Hair v3.2:')
b=s.index('# === LIMBS ===',a)
hair="""# Hair v3.3: scalp -> five primary blade locks -> secondary crossings -> layered ponytail.
add_sphere(HEAD,'HairBackV33',(0,.028,-head_d*.365),(head_w*.520,.132,head_d*.455),HAIR,46,32)
add_sphere(HEAD,'HairCrownV33',(0,.112,-head_d*.210),(head_w*.475,.058,head_d*.320),HAIR,44,28)
for side in(-1,1):
 add_sphere(HEAD,f'HairTempleV33_{side}',(side*head_w*.418,.018,-.030),(head_w*.092,.080,head_d*.142),HAIR,30,20)

# Five principal locks are intentionally asymmetric and longer at the centre.
primary=[
 (-.112,-.087,-.077,.030,.143,.061),
 (-.066,-.050,-.040,.018,.150,.058),
 (-.018,-.004,.006,-.012,.157,.054),
 (.035,.050,.044,.018,.148,.058),
 (.086,.104,.096,.035,.141,.061),
]
for i,(rx,mx,tx,ty,ry,w) in enumerate(primary):
 pts=[(rx,ry,-head_d*.010),(mx,ry-.018,head_d*.150),(tx,.096,head_d*.355),(tx*.98,ty,head_d*.510)]
 add_lock_mesh(HEAD,f'PrimaryBangV33_{i}',pts,[w*.58,w,w*.66,.0045],[.010,.011,.009,.0030],HAIR_HI if i in(1,3) else HAIR,6)
# Narrow crossing locks break the five large masses and create the swept key-art fringe.
secondary=[(-.100,-.070,.048),(-.078,-.048,.032),(-.046,-.018,.015),(.010,.026,.010),(.050,.076,.031),(.088,.112,.022)]
for i,(rx,tx,ty) in enumerate(secondary):
 pts=[(rx,.136,head_d*.006),((rx+tx)*.5,.112,head_d*.250),(tx,.076,head_d*.430),(tx,ty,head_d*.513)]
 add_lock_mesh(HEAD,f'SecondaryBangV33_{i}',pts,[.022,.025,.016,.0035],[.0065,.007,.0055,.0025],HAIR_HI if i in(0,5) else HAIR,6)
# Only a handful of fine hairs are retained around the tips.
for i,(rx,tx,ty) in enumerate(((-.096,-.083,.022),(-.052,-.038,.014),(.016,.027,.012),(.061,.080,.028),(.098,.114,.018))):
 add_strand(HEAD,f'BangWispV33_{i}',[(rx,.130,head_d*.020),((rx+tx)*.5,.105,head_d*.285),(tx,ty,head_d*.514)],.00125,HAIR_HI if i in(0,4) else HAIR)

# Long face-framing locks taper below the jaw and stay close to the silhouette.
for side in(-1,1):
 for j,(off,end_y) in enumerate(((0.00,-.35),(.024,-.47))):
  pts=[(side*(head_w*.350+off),.076,-.008),(side*(head_w*.420+off),-.014,head_d*.085),(side*(head_w*.438+off),-.170,head_d*.020),(side*(head_w*.385+off),end_y,-.026)]
  add_lock_mesh(HEAD,f'FaceBladeV33_{side}_{j}',pts,[.034-j*.008,.039-j*.008,.027-j*.006,.0045],[.010,.011,.009,.003],HAIR_HI if j else HAIR,6)

# High ponytail with a broad but separated cascade. Each lock is flat enough to
# read as a hair sheet while overlapping neighbours preserve the dense rear mass.
add_sphere(HEAD,'PonyRootV33',(0,.152,-head_d*.420),(.082,.064,.067),HAIR,34,24)
add_box(HEAD,'HairTieV33',(0,.147,-head_d*.480),(.092,.023,.034),SILVER,.006)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(17):
 lane=(i-8)/8
 sway=(-1 if i%2==0 else 1)*(.011+.005*abs(lane))
 zoff=((i%3)-1)*.012-.010*abs(lane)
 endx=lane*.250+sway
 pts=[
  (lane*.052,.150,-head_d*.510+zoff),
  (lane*.077,.032,-head_d*.748+zoff),
  (lane*.112+sway,-.245,-.490+zoff*.40),
  (lane*.158-sway,-.610,-.355),
  (lane*.210+sway,-1.000,-.228),
  (endx,-1.390,-.112),
  (endx*.96,-1.680-(i%4)*.018,-.028),
 ]
 base_w=.054-.011*abs(lane)
 add_lock_mesh(PONY,f'PonyBladeV33_{i}',pts,[base_w*.60,base_w,base_w*1.04,base_w*.94,base_w*.72,base_w*.36,.0055],[.014,.016,.017,.015,.012,.008,.003],HAIR_HI if i in(4,8,12) else HAIR,6)
# Sparse secondary strands soften the outer contour without recreating wire hair.
for i in range(10):
 lane=(i-4.5)/4.5;sgn=-1 if i%2==0 else 1
 add_strand(PONY,f'PonyFlyV33_{i}',[(lane*.046,.147,-head_d*.515),(lane*.080+sgn*.009,-.055,-head_d*.780),(lane*.140-sgn*.014,-.435,-.442),(lane*.210+sgn*.016,-.915,-.266),(lane*.278-sgn*.012,-1.320,-.125),(lane*.307,-1.675-(i%4)*.028,-.022)],.00130+(i%3)*.00018,HAIR_HI if i%4==0 else HAIR)

"""
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V33: portrait-first single-shell face and layered blade hair')
