from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V66' in s:
    print('Blender heroine generator already carries REFERENCE_V66')
    raise SystemExit(0)
if '# REFERENCE_V65' not in s:
    raise SystemExit('REFERENCE_V65 generator required before v6.6')

s=s.replace(
    '# REFERENCE_V65: reference silhouette limb volume, readable warm skin and overlapping pony foundation mass.',
    '# REFERENCE_V65: reference silhouette limb volume, readable warm skin and overlapping pony foundation mass.\n# REFERENCE_V66: surfaced bust contour, visible white bodice couture and fanned pony flow.',
    1,
)

# The old soft-bust spheres were completely inside the torso envelope. Move them to the actual front surface.
s=s.replace(
    "add_sphere(TORSO,f'BustSoftV58_{side}',(side*bust_w*.215,.105,bust_d*.350),(bust_w*.235,.090,bust_d*.205),BLACK,40,24)",
    "add_sphere(TORSO,f'BustContourV66_{side}',(side*bust_w*.205,.100,bust_d*.655),(bust_w*.245,.092,bust_d*.160),BLACK,44,28)",
    1,
)

# Surface the existing couture panels just above the measured torso instead of burying them under it.
s=s.replace(
    "add_panel(TORSO,'BodiceWhiteV35_L',[(-bust_w*.455,.218,bust_d*.515),(-bust_w*.255,.190,bust_d*.585),(-waist_w*.245,-.190,waist_d*.675),(-waist_w*.520,-.225,waist_d*.585)],.010,WHITE)",
    "add_panel(TORSO,'BodiceWhiteV66_L',[(-bust_w*.455,.218,bust_d*.600),(-bust_w*.255,.190,bust_d*.640),(-waist_w*.245,-.190,waist_d*.720),(-waist_w*.520,-.225,waist_d*.640)],.010,WHITE)",
    1,
)
s=s.replace(
    "add_panel(TORSO,'BodiceWhiteV35_R',[(bust_w*.255,.190,bust_d*.585),(bust_w*.455,.218,bust_d*.515),(waist_w*.520,-.225,waist_d*.585),(waist_w*.245,-.190,waist_d*.675)],.010,WHITE)",
    "add_panel(TORSO,'BodiceWhiteV66_R',[(bust_w*.255,.190,bust_d*.640),(bust_w*.455,.218,bust_d*.600),(waist_w*.520,-.225,waist_d*.640),(waist_w*.245,-.190,waist_d*.720)],.010,WHITE)",
    1,
)
s=s.replace("f'BodiceEdgeV35_{side}'","f'BodiceEdgeV66_{side}'",1)
s=s.replace("bust_d*.600),(.012,.330,.009)","bust_d*.670),(.012,.330,.009)",1)

# Fan three broad secondary pony locks out of the unified v6.5 foundation so the back silhouette is dynamic, not a curtain.
anchor="# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry."
fan="""# v6.6 fanned secondary mass: broad curves give the pony a graceful lateral silhouette.\nfor i,target in enumerate((-.120,.145,.265)):\n lane=(i-1)*.030\n pts=[\n  (lane+.014,.137,-head_d*.548),\n  (lane+.022,.025,-head_d*.620),\n  (lane+target*.16,-.205,-.258),\n  (lane+target*.34,-.455,-.218),\n  (lane+target*.55,-.720,-.175),\n  (lane+target*.74,-.995,-.137),\n  (lane+target*.90,-1.285,-.105),\n  (target,-1.505,-.082)\n ]\n widths=[.038,.070,.090,.098,.094,.078,.048,.008]\n depths=[.024,.038,.045,.046,.042,.034,.022,.006]\n add_smooth_lock(PONY,f'PonyFanV66_{i}',pts,widths,depths,HAIR_HI if i==1 else HAIR,14,7)\n# Eleven broad spline-smoothed locks create one readable hair mass with controlled asymmetry."""
if anchor not in s:
    raise SystemExit('pony detail anchor not found')
s=s.replace(anchor,fan,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V66: surfaced bust couture and fanned pony flow')
