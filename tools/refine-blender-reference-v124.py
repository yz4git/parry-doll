from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V124' in s:
    print('Blender heroine generator already carries REFERENCE_V124')
    raise SystemExit(0)
if '# REFERENCE_V123' not in s:
    raise SystemExit('REFERENCE_V123 generator required before v12.4')

marker="# REFERENCE_V123: TPS silhouette pass keeps measured rig endpoints while narrowing visual deltoid/clavicle armor and upper-chest shell bulk."
if marker not in s:
    raise SystemExit('v12.4 REFERENCE_V123 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V124: layered crown and hero-ponytail masses break the helmet/flat-sheet silhouette while preserving the existing dynamic pony root.",1)

# Add broad asymmetric crown ribbons over the scalp-tight cap.  These are deliberately few and
# overlap the existing cap, creating large readable planes at iPhone/TPS distance instead of many tiny fibers.
anchor="# v9.0: the fringe is born inside the existing crown cap instead of being patched to it with blobs.\n"
if anchor not in s:
    raise SystemExit('v12.4 crown insertion anchor missing')
crown="""# v12.4 hero crown breakup: large overlapping sweeps give the top silhouette direction and asymmetry.
_crown_v124=[
 ('L',[(-.010,.214,-.003),(-.032,.209,.008),(-.058,.198,.020),(-.084,.180,.025),(-.103,.158,.014),(-.111,.132,-.006)],[.008,.021,.037,.046,.039,.009],[.003,.007,.011,.014,.012,.003],HAIR),
 ('C',[(.006,.216,-.012),(.022,.210,.002),(.035,.198,.017),(.043,.181,.029),(.038,.160,.035),(.024,.138,.027)],[.007,.019,.034,.043,.036,.008],[.003,.006,.010,.013,.011,.003],HAIR_HI),
 ('R',[(.018,.213,-.006),(.044,.207,.005),(.070,.195,.018),(.091,.176,.022),(.105,.151,.008),(.108,.124,-.014)],[.008,.022,.039,.047,.037,.009],[.003,.007,.011,.014,.011,.003],HAIR)
]
for _name,_pts,_widths,_depths,_mat in _crown_v124:
 add_smooth_lock(HEAD,f'HeroCrownV124_{_name}',_pts,_widths,_depths,_mat,14,7)
# A pair of long direction lines makes the crown read as hair rather than a smooth helmet under mobile lighting.
add_strand(HEAD,'HeroCrownHiV124_L',[(-.026,.207,.010),(-.058,.191,.025),(-.092,.158,.016),(-.106,.132,-.004)],.000075,HAIR_HI)
add_strand(HEAD,'HeroCrownHiV124_R',[(.038,.205,.007),(.070,.189,.023),(.099,.154,.012),(.106,.126,-.010)],.000060,HAIR_HI)

"""
s=s.replace(anchor,crown+anchor,1)

# Add three hero-scale outer pony ribbons.  Existing V65/V66/V67 masses remain and still provide
# the dense core; these ribbons only improve the still-frame contour and asymmetric side read.
anchor="# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry.\n"
if anchor not in s:
    raise SystemExit('v12.4 pony insertion anchor missing')
pony="""# v12.4 asymmetric hero pony contour: wide near the shoulder blades, tapering cleanly below the hips.
_hero_pony_v124=[
 ('L',[( -.020,.145,-head_d*.548),(-.050,.035,-head_d*.618),(-.105,-.180,-.274),(-.205,-.430,-.222),(-.295,-.720,-.170),(-.310,-1.000,-.132),(-.245,-1.270,-.105),(-.150,-1.520,-.080)],[.045,.082,.112,.132,.140,.112,.068,.010],HAIR),
 ('M',[( .012,.146,-head_d*.552),(.020,.030,-head_d*.620),(.035,-.190,-.268),(.060,-.455,-.214),(.082,-.755,-.163),(.095,-1.055,-.125),(.082,-1.315,-.100),(.060,-1.535,-.078)],[.040,.076,.104,.124,.128,.102,.060,.009],HAIR_HI),
 ('R',[( .032,.143,-head_d*.546),(.058,.030,-head_d*.616),(.108,-.175,-.270),(.180,-.420,-.220),(.235,-.700,-.172),(.245,-.970,-.134),(.205,-1.230,-.107),(.130,-1.480,-.084)],[.043,.080,.108,.126,.132,.105,.064,.010],HAIR)
]
for _name,_pts,_widths,_mat in _hero_pony_v124:
 add_smooth_lock(PONY,f'HeroPonyV124_{_name}',_pts,_widths,[.026,.040,.050,.055,.052,.043,.029,.007],_mat,16,8)
add_strand(PONY,'HeroPonyHiV124_L',[(-.045,.030,-head_d*.620),(-.142,-.300,-.244),(-.280,-.720,-.168),(-.270,-1.120,-.118),(-.165,-1.470,-.086)],.00018,HAIR_HI)
add_strand(PONY,'HeroPonyHiV124_R',[(.052,.030,-head_d*.616),(.135,-.290,-.242),(.224,-.700,-.170),(.226,-1.080,-.121),(.142,-1.430,-.087)],.00014,HAIR_HI)

"""
s=s.replace(anchor,pony+anchor,1)

old="ROOT['character_revision']='v12.3';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
new="ROOT['character_revision']='v12.4';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
if old not in s:
    raise SystemExit('v12.4 assembly property anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V124: layered crown and hero-scale asymmetric ponytail silhouette')
