from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V71' in s:
    print('Blender heroine generator already carries REFERENCE_V71')
    raise SystemExit(0)
if '# REFERENCE_V70' not in s:
    raise SystemExit('REFERENCE_V70 generator required before v7.1')

s=s.replace(
    '# REFERENCE_V70: volumetric portrait eyes, unified nose form and curved natural lips.',
    '# REFERENCE_V70: volumetric portrait eyes, unified nose form and curved natural lips.\n# REFERENCE_V71: multiview-constrained integrated face surface, embedded eyes and surface-following lip tint.',
    1,
)

# Keep the lower face elegant but avoid the over-long pointed v7.0 chin.
s=s.replace("top=bpos((0,.179,0));bottom=bpos((0,-.161,0));verts.append(top)","top=bpos((0,.179,0));bottom=bpos((0,-.157,0));verts.append(top)",1)
s=s.replace("yy=.009+.170*sy","yy=.011+.168*sy",1)
s=s.replace("width=.132*(1.0-.355*lower+.032*cheek)","width=.132*(1.0-.335*lower+.034*cheek)",1)
s=s.replace("ex=side*.0475","ex=side*.0470",1)

# Replace the coarse five-term centre profile with a continuous landmark profile.
old_profile="""    # Restrained central profile: bridge, small tip, philtrum break and chin support.
    z+=fm*.0054*math.exp(-(x/.019)**2-((yy+.002)/.052)**2)
    z+=fm*.0140*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)
    z-=fm*.0036*math.exp(-(x/.018)**2-((yy+.061)/.012)**2)
    z+=fm*.0046*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)
    z+=fm*.0060*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)
"""
new_profile="""    # Multiview landmark profile: one continuous surface owns bridge -> tip -> philtrum -> lips -> chin.
    z+=fm*.0058*math.exp(-(x/.021)**2-((yy+.004)/.060)**2)   # glabella / bridge
    z+=fm*.0065*math.exp(-(x/.018)**2-((yy+.025)/.034)**2)   # dorsum
    z+=fm*.0105*math.exp(-(x/.020)**2-((yy+.045)/.018)**2)   # restrained tip
    z+=fm*.0045*math.exp(-(x/.014)**2-((yy+.058)/.014)**2)   # columella
    z-=fm*.0020*math.exp(-(x/.020)**2-((yy+.068)/.012)**2)   # philtrum break
    z+=fm*.0075*math.exp(-(x/.036)**2-((yy+.080)/.012)**2)   # upper lip volume
    z+=fm*.0080*math.exp(-(x/.038)**2-((yy+.090)/.013)**2)   # lower lip volume
    z-=fm*.0035*math.exp(-(x/.034)**2-((yy+.104)/.013)**2)   # labiomental crease
    z+=fm*.0170*math.exp(-(x/.042)**2-((yy+.122)/.025)**2)   # chin support
"""
if old_profile not in s:
    raise SystemExit('v7.0 centre profile block not found')
s=s.replace(old_profile,new_profile,1)

# Reduce sclera dominance under the bright WebGL audit sky.
s=s.replace("SCLERA=material('Sclera',(0.58,0.565,0.550),0,.64)","SCLERA=material('Sclera',(0.50,0.485,0.475),0,.68)",1)

# Eye proportions from a front/profile constraint: smaller visible white envelope, iris seated in an exposed ellipsoid.
s=s.replace('eye_x=.0485','eye_x=.0475',1)
s=s.replace('eye_rx=.0365','eye_rx=.0260',1)
s=s.replace('eye_ry=.0152','eye_ry=.0118',1)
s=s.replace(
    "add_sphere(HEAD,f'EyeballHiddenV60_{side}',(ex,eye_y,.0835),(.0205,.0160,.0122),SCLERA,46,28)",
    "add_sphere(HEAD,f'EyeballV71_{side}',(ex,eye_y,.0962),(.0258,.0118,.0062),SCLERA,48,28)",
    1,
)
s=s.replace(
    "add_almond_surface(HEAD,f'EyeOpeningV60_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00115,SCLERA,64,side,eye_tilt)",
    "# v7.1: the embedded eyeball itself supplies the curved visible sclera; no flat white sticker surface.",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisV70_{side}',(ex,eye_y,face_front+.0018),(.0136,.0113,.00155),IRIS,40,24)",
    "add_sphere(HEAD,f'IrisV71_{side}',(ex,eye_y,.1016),(.0098,.0092,.00175),IRIS,40,24)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisInnerV70_{side}',(ex,eye_y-.0001,face_front+.0030),(.0099,.0085,.00145),IRIS_INNER,36,22)",
    "add_sphere(HEAD,f'IrisInnerV71_{side}',(ex,eye_y-.0001,.1025),(.0067,.0065,.00145),IRIS_INNER,36,22)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'PupilV70_{side}',(ex,eye_y-.0001,face_front+.0040),(.0036,.0045,.00135),PUPIL,28,18)",
    "add_sphere(HEAD,f'PupilV71_{side}',(ex,eye_y-.0001,.1032),(.0028,.0032,.00120),PUPIL,28,18)",
    1,
)
s=s.replace("ex-side*.0052,eye_y+.0052,face_front+.0032,.0016,.0014","ex-side*.0035,eye_y+.0040,.1038,.0012,.0010",1)
s=s.replace('eye_y+.0146','eye_y+.0122',1)
s=s.replace('eye_y-.0090','eye_y-.0084',1)

# Remove pasted-on nose geometry entirely; nose volume now lives in the single UV head mesh.
nose_old="""# v6.1 explicit portrait accents remain shallow; they only make the profile readable.
add_section_mesh(HEAD,'NoseFormV70',[(.031,.0045,.0026,.0038,.1035),(.008,.0054,.0031,.0050,.1068),(-.016,.0068,.0036,.0065,.1103),(-.035,.0087,.0041,.0086,.1146),(-.046,.0100,.0045,.0094,.1165),(-.055,.0082,.0037,.0055,.1133)],SKIN,32)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingV70_{side}',(side*.0063,-.050,.1148),(.0042,.0048,.0036),SKIN,22,14)
 add_sphere(HEAD,f'NostrilV70_{side}',(side*.0040,-.0535,.1190),(.00040,.00030,.00024),FACE_DARK,12,8)
add_flow_ribbon(HEAD,'UpperLipV70_L',[(-.026,-.0810,.1132),(-.014,-.0762,.1143),(0,-.0792,.1150)],[.0020,.0052,.0028],.00100,LIP)
add_flow_ribbon(HEAD,'UpperLipV70_R',[(0,-.0792,.1150),(.014,-.0762,.1143),(.026,-.0810,.1132)],[.0028,.0052,.0020],.00100,LIP)
add_flow_ribbon(HEAD,'LowerLipV70',[(-.025,-.0820,.1134),(-.012,-.0860,.1144),(0,-.0874,.1152),(.012,-.0860,.1144),(.025,-.0820,.1134)],[.0020,.0048,.0062,.0048,.0020],.00118,LIP)
add_strand(HEAD,'MouthSeamV70',[(-.024,-.0814,.1152),(0,-.0819,.1158),(.024,-.0814,.1152)],.000105,FACE_DARK)
"""
nose_new="""# v7.1 integrated portrait accents: head topology owns all nose/mouth depth.
# Only a shallow colour patch remains for the lips, following the actual mouth plane instead of floating in front of it.
add_almond_surface(HEAD,'LipTintV71',0,-.0840,.0966,.0208,.0053,.00035,LIP,58,1,0.0)
add_strand(HEAD,'MouthSeamV71',[(-.0185,-.0832,.0972),(0,-.0840,.0975),(.0185,-.0832,.0972)],.000080,FACE_DARK)
"""
if nose_old not in s:
    raise SystemExit('v7.0 separate nose/lip block not found')
s=s.replace(nose_old,nose_new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V71: integrated multiview face surface and embedded eyes')
