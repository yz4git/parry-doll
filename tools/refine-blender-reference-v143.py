from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V143' in s:
    print('Blender heroine generator already carries REFERENCE_V143')
    raise SystemExit(0)
if '# REFERENCE_V142' not in s:
    raise SystemExit('REFERENCE_V142 generator required before v13.13')

marker="# REFERENCE_V142: explicit-ear silhouette pass enlarges and slightly externalizes the canonical ear while further recessing the lower temple mass, leaving only fine sideburn strands across the ear-front region."
if marker not in s: raise SystemExit('v13.13 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V143: natural-neck profile pass replaces the mannequin cylinder with a tapered asymmetric neck shell that slopes rearward from jaw to collar, matching the supplied elegant side silhouette.",1)

old="add_cylinder(HEAD,'Neck',(0,-.181,-.030),W('neck')*.292,.134,SKIN,30)"
new="""_neck_r=W('neck')*.292
add_section_mesh(HEAD,'Neck',[
 (-.112,_neck_r*.82,_neck_r*.82,_neck_r*.74,-.027),
 (-.137,_neck_r*.90,_neck_r*.94,_neck_r*.80,-.030),
 (-.168,_neck_r*.98,_neck_r*1.03,_neck_r*.86,-.034),
 (-.202,_neck_r*1.04,_neck_r*1.08,_neck_r*.91,-.039),
 (-.238,_neck_r*1.08,_neck_r*1.12,_neck_r*.96,-.045)
],SKIN,42)"""
if old not in s: raise SystemExit('v13.13 neck cylinder anchor missing')
s=s.replace(old,new,1)

# Fine nape hairs visually bridge the high pony roots into the new neck without hiding its contour.
anchor="add_cylinder(HEAD,'ChokerTrim',(0,-.186,-.028),W('neck')*.435,.008,SILVER,30)"
if anchor not in s: raise SystemExit('v13.13 choker anchor missing')
insert="""\nfor _side in (-1,1):
 add_strand(HEAD,f'NapeWispV143_A_{_side}',[(_side*.071,-.070,-.082),(_side*.067,-.105,-.079),(_side*.059,-.142,-.071),(_side*.050,-.182,-.061)],.000020,HAIR)
 add_strand(HEAD,f'NapeWispV143_B_{_side}',[(_side*.060,-.060,-.075),(_side*.057,-.096,-.073),(_side*.050,-.132,-.066),(_side*.043,-.168,-.058)],.000016,HAIR_HI)
"""
s=s.replace(anchor,anchor+insert,1)

old="ROOT['character_revision']='v13.12';"
new="ROOT['character_revision']='v13.13';"
if old not in s: raise SystemExit('v13.13 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.12'","HEAD_ASSET['reference_profile_silhouette']='v13.13'",1)
s=s.replace("HEAD_ASSET['reference_neck_revision']='v13.7'","HEAD_ASSET['reference_neck_revision']='v13.13'",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V143: tapered asymmetric rear-sloping neck shell and fine nape wisps')
