from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V29' in s:
    print('Blender heroine generator already carries REFERENCE_V29')
    raise SystemExit(0)
if '# REFERENCE_V28' not in s:
    raise SystemExit('REFERENCE_V28 generator required before v2.9')
s=s.replace('# REFERENCE_V28: low-specular black hair and staggered fringe roots.','# REFERENCE_V28: low-specular black hair and staggered fringe roots.\n# REFERENCE_V29: anatomy-first head, embedded eyes, eyelids, connected nose and continuous ribcage.',1)

# -----------------------------------------------------------------------------
# BODY: preserve the measured four-view envelope, but make the ribcage-to-waist
# transition read as one continuous human form under the costume.
# -----------------------------------------------------------------------------
a=s.index("add_section_mesh(TORSO,'TorsoSuit',[")
b=s.index('# Front-biased contours define the bust',a)
torso="""add_section_mesh(TORSO,'TorsoSuit',[
 (-.340,waist_w*.49,waist_d*.49,waist_d*.54,-.006),
 (-.285,waist_w*.47,waist_d*.47,waist_d*.54,-.004),
 (-.220,waist_w*.49,waist_d*.46,waist_d*.55,-.001),
 (-.150,bust_w*.37,bust_d*.40,bust_d*.47,.004),
 (-.075,bust_w*.43,bust_d*.41,bust_d*.54,.011),
 (.000,bust_w*.48,bust_d*.42,bust_d*.62,.021),
 (.075,bust_w*.515,bust_d*.44,bust_d*.675,.030),
 (.135,bust_w*.505,bust_d*.44,bust_d*.655,.030),
 (.195,bust_w*.465,bust_d*.42,bust_d*.57,.022),
 (.255,bust_w*.405,bust_d*.39,bust_d*.48,.012),
 (.315,bust_w*.340,bust_d*.34,bust_d*.385,.002)
],BLACK,48)
"""
s=s[:a]+torso+s[b:]

# Replace the old bulb-like bust helper volumes with broad, shallow forms that
# support the continuous ribcage instead of looking like attached spheres.
a=s.index('# Front-biased contours define the bust')
b=s.index('# Upper torso continuity',a)
bust="""# Shallow soft-tissue support over a continuous ribcage. The outer envelope remains reference-locked.
for side in(-1,1):
 add_sphere(TORSO,f'BustSoft_{side}',(side*bust_w*.205,.105,bust_d*.330),(bust_w*.205,.082,bust_d*.180),BLACK,36,22)
add_box(TORSO,'UnderBustLine',(0,.020,bust_d*.505),(bust_w*.70,.014,.009),SILVER,.003)
for side in(-1,1):
 add_box(TORSO,f'WaistContour_{side}',(side*waist_w*.44,-.150,waist_d*.50),(.012,.175,.009),SILVER,.0035,rot=(0,0,-side*.15))
"""
s=s[:a]+bust+s[b:]

# Clavicle/deltoid bridge: make the upper torso read as one body before the
# separate arm rig begins. This is still fully inside the measured shoulder span.
a=s.index('# Upper torso continuity:')
b=s.index('# Reference-like harness:',a)
shoulders="""# Anatomical clavicle/deltoid bridge inside the measured shoulder envelope.
for side in(-1,1):
 add_sphere(TORSO,f'DeltoidBridge_{side}',(side*bust_w*.405,.238,.002),(bust_w*.125,.064,bust_d*.150),BLACK,30,20)
 add_panel(TORSO,f'ClaviclePlane_{side}',[(side*bust_w*.080,.270,bust_d*.30),(side*bust_w*.285,.258,bust_d*.28),(side*bust_w*.430,.225,bust_d*.18),(side*bust_w*.275,.210,bust_d*.31)],.013,BLACK_SOFT)
 add_box(TORSO,f'ClavicleTrim_{side}',(side*bust_w*.225,.247,bust_d*.325),(bust_w*.285,.010,.008),SILVER,.0025,rot=(0,0,-side*.11))
"""
s=s[:a]+shoulders+s[b:]

# -----------------------------------------------------------------------------
# HEAD: rebuild the skull/jaw/cheek/forehead as a clearer set of continuous
# anatomical planes. The dimensions remain inside the measured head envelope.
# -----------------------------------------------------------------------------
a=s.index("add_section_mesh(HEAD,'HeadShell',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_section_mesh(HEAD,'HeadShell',[
 (-.145,head_w*.120,head_d*.170,head_d*.235,.052),  # chin tip
 (-.126,head_w*.235,head_d*.235,head_d*.305,.045),  # chin body
 (-.105,head_w*.315,head_d*.300,head_d*.360,.036),  # jaw
 (-.078,head_w*.385,head_d*.350,head_d*.410,.026),  # mouth / lower cheek
 (-.045,head_w*.445,head_d*.390,head_d*.455,.015),  # cheek lower
 (-.010,head_w*.490,head_d*.425,head_d*.500,.004),  # cheekbone / eye socket
 (.025,head_w*.505,head_d*.450,head_d*.515,-.004),  # eye level
 (.058,head_w*.490,head_d*.472,head_d*.490,-.010),  # brow / temple
 (.092,head_w*.455,head_d*.482,head_d*.445,-.017),  # forehead
 (.120,head_w*.395,head_d*.468,head_d*.385,-.024),  # upper forehead
 (.145,head_w*.310,head_d*.435,head_d*.315,-.030)   # crown transition
],SKIN,52)
"""
s=s[:a]+head+s[b:]

# Replace flat eye plates and floating facial primitives. Eyeballs sit partly
# inside the skull, eyelids wrap their visible surface, and the nose grows out
# of the brow/mid-face plane.
a=s.index('# Portrait feature plane is projected slightly beyond the continuous head shell.')
b=s.index('# Rear scalp never crosses the forehead;',a)
face="""# Anatomy-first portrait: embedded eyeballs, eyelids and a connected central face form.
face_z=head_d*.515
eye_y=.018
eye_z=face_z-.010
eye_x=head_w*.160
eye_rx=head_w*.090
eye_ry=.028
eye_rz=head_d*.100
for side in(-1,1):
 ex=side*eye_x
 # Eyeball first; the lids are built around its visible front surface.
 add_sphere(HEAD,f'Eyeball_{side}',(ex,eye_y,eye_z),(eye_rx,eye_ry,eye_rz),SCLERA,32,20)
 eye_front=eye_z+eye_rz*.96
 add_sphere(HEAD,f'Iris_{side}',(ex,eye_y-.001,eye_front+.003),(head_w*.048,.012,.0046),IRIS,26,16)
 add_sphere(HEAD,f'Pupil_{side}',(ex,eye_y-.001,eye_front+.0065),(head_w*.018,.0070,.0030),PUPIL,20,12)
 add_sphere(HEAD,f'EyeLight_{side}',(ex-side*head_w*.012,eye_y+.008,eye_front+.0095),(head_w*.010,.0040,.0018),SCLERA,12,8)
 # Upper and lower eyelid skin wraps the sphere rather than floating as a rectangular plate.
 lid_outer=ex+side*eye_rx*.95
 lid_inner=ex-side*eye_rx*.90
 add_panel(HEAD,f'UpperLid_{side}',[(lid_inner,.030,eye_front+.001),(ex,.043,eye_front+.004),(lid_outer,.028,eye_front+.001),(lid_outer,.018,eye_front+.004),(ex,.028,eye_front+.008),(lid_inner,.019,eye_front+.004)],.0023,SKIN)
 add_panel(HEAD,f'LowerLid_{side}',[(lid_inner,.008,eye_front+.003),(ex,-.004,eye_front+.004),(lid_outer,.009,eye_front+.003),(lid_outer,.015,eye_front+.005),(ex,.008,eye_front+.006),(lid_inner,.015,eye_front+.005)],.0020,SKIN)
 # Lashes/brows follow the eye arc and retain the stylized key-art readability.
 add_panel(HEAD,f'UpperLash_{side}',[(lid_inner,.032,eye_front+.008),(ex,.045,eye_front+.010),(lid_outer,.030,eye_front+.008),(lid_outer,.026,eye_front+.009),(ex,.040,eye_front+.011),(lid_inner,.027,eye_front+.009)],.0015,HAIR)
 add_panel(HEAD,f'Brow_{side}',[(ex-side*eye_rx*.82,.078,face_z+.007),(ex,.086,face_z+.010),(ex+side*eye_rx*.96,.073,face_z+.007),(ex+side*eye_rx*.90,.067,face_z+.008),(ex,.079,face_z+.011),(ex-side*eye_rx*.78,.071,face_z+.008)],.0015,HAIR)

# Nose bridge, tip and alar wings form one connected volume growing out of the face plane.
add_section_mesh(HEAD,'NoseForm',[
 (.073,.0045,.0035,.0050,face_z-.012),
 (.045,.0055,.0038,.0075,face_z-.009),
 (.015,.0070,.0040,.0105,face_z-.006),
 (-.012,.0085,.0042,.0140,face_z-.003),
 (-.034,.0110,.0045,.0180,face_z+.000),
 (-.050,.0135,.0048,.0195,face_z+.002)
],SKIN,24)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWing_{side}',(side*.0125,-.050,face_z+.010),(.0085,.0080,.0060),SKIN,18,10)

# Mouth stays embedded in the lower-face plane with a soft cupid bow and restrained projection.
add_panel(HEAD,'UpperLip',[(-.029,-.076,face_z+.004),(-.014,-.071,face_z+.005),(0,-.075,face_z+.006),(.014,-.071,face_z+.005),(.029,-.076,face_z+.004),(.020,-.081,face_z+.005),(0,-.080,face_z+.006),(-.020,-.081,face_z+.005)],.0018,LIP)
add_panel(HEAD,'LowerLip',[(-.024,-.082,face_z+.004),(0,-.087,face_z+.006),(.024,-.082,face_z+.004),(.017,-.091,face_z+.004),(0,-.094,face_z+.005),(-.017,-.091,face_z+.004)],.0017,LIP)
# Tiny philtrum/chin cues improve front/profile readability without adding hard mechanical lines.
add_box(HEAD,'Philtrum',(0,-.063,face_z+.002),(.006,.014,.003),SKIN,.001)
add_sphere(HEAD,'ChinPlane',(0,-.118,face_z-.010),(head_w*.115,.020,head_d*.055),SKIN,24,14)
"""
s=s[:a]+face+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V29: anatomy-first head, embedded eyes/eyelids, connected nose and continuous ribcage')
