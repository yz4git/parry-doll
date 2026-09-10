from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V59' in s:
    print('Blender heroine generator already carries REFERENCE_V59')
    raise SystemExit(0)
if '# REFERENCE_V58' not in s:
    raise SystemExit('REFERENCE_V58 generator required before v5.9')

s=s.replace(
    '# REFERENCE_V58: reference body volume, layered rounded fringe and larger portrait eyes.',
    '# REFERENCE_V58: reference body volume, layered rounded fringe and larger portrait eyes.\n# REFERENCE_V59: broad swept fringe, full high pony cascade and softer human limb volume.',
    1,
)

# Slightly taller eye opening and iris: keep the v5.8 width but make the gaze readable at gameplay distance.
s=s.replace('eye_ry=.0162','eye_ry=.0194',1)
s=s.replace("head_w*.066,.0118,IRIS","head_w*.067,.0141,IRIS",1)
s=s.replace("head_w*.041,.0077,IRIS_INNER","head_w*.041,.0092,IRIS_INNER",1)
s=s.replace("head_w*.0160,.0045,PUPIL","head_w*.0160,.0053,PUPIL",1)
s=s.replace("eye_y+.0165","eye_y+.0194",1)
s=s.replace("eye_y+.0171","eye_y+.0200",1)
s=s.replace("eye_y-.0097","eye_y-.0115",1)

# Replace the five rounded finger-like bangs with two broad stable sweeps and two slim crossing layers.
a=s.index('# Hair v5.8:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.9: broad layered side sweep with an open eye line, plus a much fuller high pony cascade.
add_section_mesh(HEAD,'HairTopCapV59',[
 (.064,head_w*.452,head_d*.442,head_d*.492,-.018),
 (.098,head_w*.446,head_d*.434,head_d*.482,-.020),
 (.133,head_w*.402,head_d*.392,head_d*.438,-.021),
 (.164,head_w*.312,head_d*.302,head_d*.344,-.018),
 (.189,head_w*.187,head_d*.181,head_d*.209,-.010),
 (.204,head_w*.070,head_d*.070,head_d*.080,-.002)
],HAIR,56)
add_rear_hair_shell(HEAD,'HairRearShellV59',[
 (-.025,head_w*.300,head_d*.410,-head_d*.066),
 (.012,head_w*.430,head_d*.500,-head_d*.058),
 (.052,head_w*.505,head_d*.550,-head_d*.050),
 (.096,head_w*.528,head_d*.562,-head_d*.042),
 (.138,head_w*.490,head_d*.517,-head_d*.033),
 (.170,head_w*.394,head_d*.422,-head_d*.024),
 (.194,head_w*.230,head_d*.270,-head_d*.013),
 (.206,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,44)

# Two wide dark planes establish a natural side-swept fringe instead of repeated finger-like locks.
add_flow_ribbon(HEAD,'FringeSweepV59_A',[(-.112,.182,.012),(-.096,.160,.045),(-.066,.134,.074),(-.027,.107,.096),(.018,.085,.106),(.060,.071,.110)],[.086,.088,.080,.064,.046,.028],.00145,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV59_B',[(-.047,.184,.012),(-.025,.160,.047),(.010,.133,.077),(.048,.106,.099),(.085,.083,.108),(.114,.069,.110)],[.072,.071,.064,.050,.035,.021],.00140,HAIR)
# Short overlapping strips break the broad masses without covering the eyes.
add_flow_ribbon(HEAD,'FringeLayerV59_C',[(-.083,.177,.014),(-.059,.153,.049),(-.026,.126,.078),(.012,.101,.100),(.043,.085,.108)],[.035,.037,.033,.024,.012],.00115,HAIR_HI)
add_flow_ribbon(HEAD,'FringeLayerV59_D',[(-.015,.179,.013),(.010,.153,.049),(.043,.125,.079),(.078,.099,.101),(.105,.082,.108)],[.032,.034,.030,.022,.011],.00112,HAIR)
add_strand(HEAD,'FringeFineV59_A',[(-.096,.173,.018),(-.057,.137,.074),(.012,.092,.109)],.000085,HAIR_HI)
add_strand(HEAD,'FringeFineV59_B',[(-.036,.176,.018),(.014,.135,.077),(.091,.087,.108)],.000080,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.394,.112,-head_d*.038),(side*head_w*.423,.050,-.013),(side*head_w*.428,-.028,-.016),(side*head_w*.416,-.103,-.044),(side*head_w*.401,-.178,-.064)]
 add_smooth_lock(HEAD,f'FaceLockV59_{side}',pts,[.010,.013,.0105,.0060,.0026],[.008,.009,.007,.0045,.0022],HAIR,10,5)

add_box(HEAD,'HairTieV59',(.014,.138,-head_d*.530),(.072,.017,.027),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry.
for i in range(11):
 lane=(i-5)/5
 dz=lane*.046+((i%3)-1)*.012
 sway=.055*math.sin((i+1)*1.37)
 flare=lane*.070
 pts=[
  (lane*.025+.014,.138,-head_d*.540+dz*.18),
  (lane*.042+.020+sway*.12,.030,-head_d*.615+dz*.55),
  (lane*.068+.026+sway*.45,-.220,-.250+dz*.80),
  (lane*.095+.032+sway+flare*.35,-.520,-.205+dz),
  (lane*.125+.040+sway*.78+flare*.60,-.850,-.158+dz*1.10),
  (lane*.145+.048+sway*.44+flare*.80,-1.170,-.120+dz*1.05),
  (lane*.158+.054+flare,-1.500-(i%3)*.025,-.092+dz*.88)
 ]
 base=.064-.009*abs(lane)
 widths=[base*.72,base,base*.98,base*.90,base*.72,base*.43,.0060]
 depths=[.030,.043,.044,.040,.032,.020,.0050]
 add_smooth_lock(PONY,f'PonyMassV59_{i}',pts,widths,depths,HAIR_HI if i in(2,8) else HAIR,12,6)
for i in range(7):
 lane=(i-3)/3
 sway=.040*math.sin((i+2)*1.41)
 add_strand(PONY,f'PonyWispV59_{i}',[(lane*.028+.014,.136,-head_d*.548),(lane*.046+.020,-.020,-head_d*.616),(lane*.075+.026+sway*.4,-.330,-.235),(lane*.115+.036+sway,-.805,-.158),(lane*.155+.050,-1.515-(i%2)*.030,-.086)],.00022+(i%2)*.000035,HAIR_HI if i%2==0 else HAIR)

'''
s=s[:a]+hair+s[b:]

# Keep the narrow shoulder joint positions, but remove the stick-limb look with modestly fuller cross-sections.
s=s.replace(
    "ua=W('upper_arm')*.56;fa=W('forearm')*.54;th=W('thigh_each')*.64;kn=W('knee_each')*.58;calf=W('calf_each')*.56;ank=W('ankle_each')*.49",
    "ua=W('upper_arm')*.64;fa=W('forearm')*.60;th=W('thigh_each')*.68;kn=W('knee_each')*.61;calf=W('calf_each')*.59;ank=W('ankle_each')*.50",
    1,
)
s=s.replace(
    "(UA_L,'UpperArmL',ua*1.02,ua*.80,ua_d*1.02,ua_d*.84,SKIN),(UA_R,'UpperArmR',ua*1.02,ua*.80,ua_d*1.02,ua_d*.84,SKIN)",
    "(UA_L,'UpperArmL',ua*1.04,ua*.82,ua_d*1.05,ua_d*.86,SKIN),(UA_R,'UpperArmR',ua*1.04,ua*.82,ua_d*1.05,ua_d*.86,SKIN)",
    1,
)
s=s.replace(
    "(FA_L,'ForearmL',fa*.92,fa*.68,fa_d,fa_d*.72,BLACK),(FA_R,'ForearmR',fa*.92,fa*.68,fa_d,fa_d*.72,BLACK)",
    "(FA_L,'ForearmL',fa*.96,fa*.72,fa_d*1.02,fa_d*.75,BLACK),(FA_R,'ForearmR',fa*.96,fa*.72,fa_d*1.02,fa_d*.75,BLACK)",
    1,
)
s=s.replace(
    "(TH_L,'ThighL',th*1.10,kn*.92,th_d*1.04,th_d*.80,SKIN),(TH_R,'ThighR',th*1.10,kn*.92,th_d*1.04,th_d*.80,SKIN)",
    "(TH_L,'ThighL',th*1.12,kn*.94,th_d*1.06,th_d*.82,SKIN),(TH_R,'ThighR',th*1.12,kn*.94,th_d*1.06,th_d*.82,SKIN)",
    1,
)
s=s.replace(
    "add_sphere(group,'DeltoidBlendV58'+name,(0,-.430,0),(ua*1.08,.088,ua_d*1.06),SKIN,28,18)",
    "add_sphere(group,'DeltoidBlendV59'+name,(0,-.430,0),(ua*1.10,.095,ua_d*1.08),SKIN,30,20)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V59: broad fringe, full pony cascade and softer limb volume')
