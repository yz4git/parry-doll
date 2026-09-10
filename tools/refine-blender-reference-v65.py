from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V65' in s:
    print('Blender heroine generator already carries REFERENCE_V65')
    raise SystemExit(0)
if '# REFERENCE_V64' not in s:
    raise SystemExit('REFERENCE_V64 generator required before v6.5')

s=s.replace(
    '# REFERENCE_V64: readable soft grey-brown gaze and continuous restrained nose-lip-chin profile.',
    '# REFERENCE_V64: readable soft grey-brown gaze and continuous restrained nose-lip-chin profile.\n# REFERENCE_V65: reference silhouette limb volume, readable warm skin and overlapping pony foundation mass.',
    1,
)

# The audit/game daylight was washing the pale face to white. Keep fair skin but restore warm midtone shading.
s=s.replace("SKIN=material('Skin',(0.50,0.335,0.320),0,.72)","SKIN=material('Skin',(0.36,0.235,0.215),0,.76)",1)
s=s.replace("SCLERA=material('Sclera',(0.66,0.635,0.615),0,.62)","SCLERA=material('Sclera',(0.58,0.565,0.550),0,.64)",1)

# Recover human soft-tissue volume from the measured reference instead of multiplying the diameters down so aggressively.
s=s.replace(
    "ua=W('upper_arm')*.64;fa=W('forearm')*.60;th=W('thigh_each')*.68;kn=W('knee_each')*.61;calf=W('calf_each')*.59;ank=W('ankle_each')*.50",
    "ua=W('upper_arm')*.74;fa=W('forearm')*.69;th=W('thigh_each')*.82;kn=W('knee_each')*.70;calf=W('calf_each')*.72;ank=W('ankle_each')*.56",
    1,
)

# Slightly stronger ribcage-to-waist and pelvis transition while preserving the narrow shoulder joint locations.
s=s.replace("(.000,bust_w*.515,bust_d*.43,bust_d*.705,.030)","(.000,bust_w*.535,bust_d*.43,bust_d*.705,.030)",1)
s=s.replace("(.075,bust_w*.555,bust_d*.45,bust_d*.770,.044)","(.075,bust_w*.580,bust_d*.45,bust_d*.770,.044)",1)
s=s.replace("(.135,bust_w*.540,bust_d*.45,bust_d*.735,.041)","(.135,bust_w*.565,bust_d*.45,bust_d*.735,.041)",1)
s=s.replace("(-.080,pelvis_w*.525,pelvis_d*.60,pelvis_d*.56,-.011)","(-.080,pelvis_w*.555,pelvis_d*.60,pelvis_d*.56,-.011)",1)
s=s.replace("(.040,pelvis_w*.510,pelvis_d*.54,pelvis_d*.55,-.004)","(.040,pelvis_w*.540,pelvis_d*.54,pelvis_d*.55,-.004)",1)

# A five-lock overlapping foundation sits behind the eleven detail locks. This reads as one high pony mass at gameplay distance.
anchor="PONY=empty('BL_PONY_DYNAMIC',HEAD)\n# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry."
foundation="""PONY=empty('BL_PONY_DYNAMIC',HEAD)\n# v6.5 overlapping foundation: broad spline locks eliminate the separated vertical-string silhouette.\nfor i in range(5):\n lane=(i-2)/2\n sideflow=.055*lane\n pts=[\n  (lane*.018+.014,.138,-head_d*.540),\n  (lane*.030+.018,.025,-head_d*.615),\n  (lane*.046+.030,-.220,-.255),\n  (lane*.060+.055+sideflow*.25,-.500,-.210),\n  (lane*.075+.085+sideflow*.55,-.820,-.162),\n  (lane*.090+.110+sideflow*.75,-1.150,-.120),\n  (lane*.105+.125+sideflow,-1.485,-.085)\n ]\n widths=[.052,.095,.118,.122,.104,.070,.014]\n depths=[.026,.040,.047,.048,.041,.029,.008]\n add_smooth_lock(PONY,f'PonyFoundationV65_{i}',pts,widths,depths,HAIR_HI if i in(1,3) else HAIR,14,7)\n# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry."""
if anchor not in s:
    raise SystemExit('v5.9 pony anchor not found')
s=s.replace(anchor,foundation,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V65: fuller reference silhouette, readable skin and unified pony mass')
