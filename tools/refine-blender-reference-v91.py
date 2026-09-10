from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V91' in s:
    print('Blender heroine generator already carries REFERENCE_V91')
    raise SystemExit(0)
if '# REFERENCE_V90' not in s:
    raise SystemExit('REFERENCE_V90 generator required before v9.1')

s=s.replace(
    '# REFERENCE_V90: crown-buried zero-width roots replace filler blobs and create continuous hair-cap/fringe overlap.',
    '# REFERENCE_V90: crown-buried zero-width roots replace filler blobs and create continuous hair-cap/fringe overlap.\n# REFERENCE_V91: fuller upper crown cap wraps the buried roots and removes the remaining 3/4 scalp stripe.',
    1,
)

old="""add_section_mesh(HEAD,'HairTopCapV59',[
 (.064,head_w*.452,head_d*.442,head_d*.492,-.018),
 (.098,head_w*.446,head_d*.434,head_d*.482,-.020),
 (.133,head_w*.402,head_d*.392,head_d*.438,-.021),
 (.164,head_w*.312,head_d*.302,head_d*.344,-.018),
 (.189,head_w*.187,head_d*.181,head_d*.209,-.010),
 (.204,head_w*.070,head_d*.070,head_d*.080,-.002)
],HAIR,56)
"""
new="""add_section_mesh(HEAD,'HairTopCapV91',[
 (.064,head_w*.452,head_d*.442,head_d*.492,-.018),
 (.098,head_w*.448,head_d*.436,head_d*.486,-.020),
 (.133,head_w*.414,head_d*.404,head_d*.452,-.021),
 # v9.1 keeps crown width longer instead of collapsing into a narrow cone above the forehead.
 (.164,head_w*.356,head_d*.342,head_d*.390,-.018),
 (.189,head_w*.258,head_d*.242,head_d*.286,-.010),
 (.204,head_w*.142,head_d*.126,head_d*.158,-.002),
 (.213,head_w*.052,head_d*.048,head_d*.060,.002)
],HAIR,64)
"""
if old not in s:
    raise SystemExit('v9.1 HairTopCapV59 block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V91: fuller upper crown cap wraps v9.0 buried fringe roots')
