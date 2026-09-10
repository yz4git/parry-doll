from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V63' in s:
    print('Blender heroine generator already carries REFERENCE_V63')
    raise SystemExit(0)
if '# REFERENCE_V62' not in s:
    raise SystemExit('REFERENCE_V62 generator required before v6.3')

s=s.replace(
    '# REFERENCE_V62: cinematic almond gaze, warm skin response and subtle readable side-profile nose.',
    '# REFERENCE_V62: cinematic almond gaze, warm skin response and subtle readable side-profile nose.\n# REFERENCE_V63: layered grey-brown irises, smaller pupils and fine separated portrait fringe.',
    1,
)

# Dark limbal ring + larger warm-grey inner iris: avoids both amber buttons and black-dot eyes.
s=s.replace("IRIS=material('Iris',(0.050,0.032,0.030),.01,.46)","IRIS=material('Iris',(0.030,0.023,0.024),.01,.48)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.115,0.066,0.055),.01,.48)","IRIS_INNER=material('Iris Inner',(0.115,0.078,0.070),.01,.50)",1)
s=s.replace('eye_y=.0330','eye_y=.0315',1)
s=s.replace('eye_rx=.0445','eye_rx=.0455',1)
s=s.replace('eye_ry=.0166','eye_ry=.0161',1)
s=s.replace(".0228,.0141,IRIS",".0260,.0146,IRIS",1)
s=s.replace(".0147,.0096,IRIS_INNER",".0200,.0115,IRIS_INNER",1)
s=s.replace(".0058,.0068,PUPIL",".0048,.0058,PUPIL",1)
s=s.replace("eye_y+.0172","eye_y+.0168",1)

# Slightly more readable side profile while keeping the nose narrow in front.
s=s.replace("add_sphere(HEAD,'NoseTipV62',(0,-.043,.1103),(.0118,.0112,.0092),SKIN,30,20)","add_sphere(HEAD,'NoseTipV63',(0,-.043,.1122),(.0114,.0110,.0090),SKIN,30,20)",1)
s=s.replace("add_sphere(HEAD,'NoseBridgeV62',(0,-.006,.1030),(.0080,.038,.0062),SKIN,30,20)","add_sphere(HEAD,'NoseBridgeV63',(0,-.006,.1040),(.0078,.038,.0061),SKIN,30,20)",1)

# Fine hair-flow lines break the broad v5.9 fringe into layered strands without reopening scalp gaps.
anchor="add_strand(HEAD,'FringeFineV59_B',[(-.036,.176,.018),(.014,.135,.077),(.091,.087,.108)],.000080,HAIR_HI)"
insert=anchor+"\nadd_strand(HEAD,'FringeFineV63_C',[(-.116,.170,.017),(-.085,.142,.061),(-.032,.105,.101)],.000070,HAIR_HI)\nadd_strand(HEAD,'FringeFineV63_D',[(-.068,.181,.016),(-.026,.143,.063),(.038,.096,.106)],.000072,HAIR_HI)\nadd_strand(HEAD,'FringeFineV63_E',[(-.005,.180,.016),(.034,.143,.064),(.095,.087,.107)],.000068,HAIR_HI)\nfor side in(-1,1):\n add_strand(HEAD,f'FaceWispV63_{side}',[(side*.105,.124,.094),(side*.116,.072,.101),(side*.120,.010,.099),(side*.112,-.052,.094)],.00010,HAIR_HI)"
if anchor not in s:
    raise SystemExit('v5.9 fringe anchor not found')
s=s.replace(anchor,insert,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V63: layered grey-brown gaze and separated portrait fringe')
