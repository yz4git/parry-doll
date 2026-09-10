from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V68' in s:
    print('Blender heroine generator already carries REFERENCE_V68')
    raise SystemExit(0)
if '# REFERENCE_V67' not in s:
    raise SystemExit('REFERENCE_V67 generator required before v6.8')

s=s.replace(
    '# REFERENCE_V67: integrated bust contour, upper-chest couture wings, almond gaze and wide high-pony silhouette.',
    '# REFERENCE_V67: integrated bust contour, upper-chest couture wings, almond gaze and wide high-pony silhouette.\n# REFERENCE_V68: layered porcelain torso shell, narrow black corset centre and natural portrait eye spacing.',
    1,
)

# The core torso already owns the bust volume. Keep only a very shallow soft contour so it cannot read as two spheres.
s=s.replace(
    "add_sphere(TORSO,f'BustContourV67_{side}',(side*bust_w*.182,.102,bust_d*.670),(bust_w*.205,.074,bust_d*.112),BLACK_SOFT,44,28)",
    "add_sphere(TORSO,f'BustContourV68_{side}',(side*bust_w*.175,.102,bust_d*.676),(bust_w*.155,.058,bust_d*.072),BLACK_SOFT,44,28)",
    1,
)

anchor="""for side in(-1,1):
 add_box(TORSO,f'ChestSeamV67_{side}',(side*bust_w*.245,.120,bust_d*.785),(.010,.205,.010),SILVER,.0032,rot=(0,0,side*.11))
"""
layer=anchor+"""
# v6.8 porcelain shell covers the old black capsule; a narrow black centre panel restores the reference couture contrast.
add_panel(TORSO,'PorcelainShellV68_L',[(-bust_w*.520,.250,bust_d*.485),(-bust_w*.115,.226,bust_d*.690),(-bust_w*.095,.072,bust_d*.875),(-waist_w*.105,-.188,waist_d*.905),(-waist_w*.535,-.238,waist_d*.735),(-bust_w*.500,.058,bust_d*.750)],.013,WHITE)
add_panel(TORSO,'PorcelainShellV68_R',[(bust_w*.115,.226,bust_d*.690),(bust_w*.520,.250,bust_d*.485),(bust_w*.500,.058,bust_d*.750),(waist_w*.535,-.238,waist_d*.735),(waist_w*.105,-.188,waist_d*.905),(bust_w*.095,.072,bust_d*.875)],.013,WHITE)
add_panel(TORSO,'CenterCorsetV68',[(-bust_w*.135,.235,bust_d*.730),(bust_w*.135,.235,bust_d*.730),(bust_w*.205,.070,bust_d*.915),(waist_w*.125,-.205,waist_d*.970),(-waist_w*.125,-.205,waist_d*.970),(-bust_w*.205,.070,bust_d*.915)],.014,BLACK)
add_panel(TORSO,'CenterCorsetInlayV68',[(-bust_w*.045,.215,bust_d*.748),(bust_w*.045,.215,bust_d*.748),(bust_w*.060,.050,bust_d*.935),(waist_w*.038,-.185,waist_d*.990),(-waist_w*.038,-.185,waist_d*.990),(-bust_w*.060,.050,bust_d*.935)],.008,BLACK_SOFT)
for side in(-1,1):
 add_box(TORSO,f'CorsetTrimV68_{side}',(side*bust_w*.150,.035,bust_d*.920),(.008,.330,.008),SILVER,.0028,rot=(0,0,side*.055))
"""
if anchor not in s:
    raise SystemExit('v6.7 chest seam anchor not found')
s=s.replace(anchor,layer,1)

# Natural portrait spacing: retain large anime readability but separate the inner corners and reduce the oversized iris-disc look.
s=s.replace('eye_x=.0415','eye_x=.0435',1)
s=s.replace('eye_rx=.0460','eye_rx=.0415',1)
s=s.replace('eye_ry=.0144','eye_ry=.0142',1)
s=s.replace('.0262,.0129,IRIS','.0210,.0122,IRIS',1)
s=s.replace('.0208,.0101,IRIS_INNER','.0154,.0091,IRIS_INNER',1)
s=s.replace('.0038,.0044,PUPIL','.0035,.0042,PUPIL',1)
s=s.replace('eye_y+.0151','eye_y+.0148',1)
s=s.replace('eye_y-.0088','eye_y-.0086',1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V68: layered couture shell and natural portrait eye spacing')
