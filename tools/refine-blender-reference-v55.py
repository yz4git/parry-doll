from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V55' in s:
    print('Blender heroine generator already carries REFERENCE_V55')
    raise SystemExit(0)
if '# REFERENCE_V54' not in s:
    raise SystemExit('REFERENCE_V54 generator required before v5.5')

s=s.replace(
    '# REFERENCE_V54: dedicated facial surface patch, explicit profile landmarks and unified fringe mass.',
    '# REFERENCE_V54: dedicated facial surface patch, explicit profile landmarks and unified fringe mass.\n# REFERENCE_V55: single closed profile head, recessed orbits and scalp-covered swept hair.',
    1,
)

helper='''
def add_profile_head_v55(p,name,rows,mat,segments=96):
 # rows: logical_y, half_width, back_depth, front_depth. A single closed surface owns the entire head.
 verts=[]
 for yy,w,back,front in rows:
  for i in range(segments):
   ang=2*math.pi*i/segments;cs=math.cos(ang);sn=math.sin(ang)
   x=cs*w
   z=sn*(front if sn>=0 else back)
   if sn>0:
    fm=sn**1.55
    # Orbital recess, brow plane and cheekbone support.
    for side in (-1,1):
     ex=side*head_w*.147
     z-=fm*.0078*math.exp(-((x-ex)/(head_w*.082))**2-((yy-.030)/.021)**2)
     z+=fm*.0030*math.exp(-((x-ex)/(head_w*.105))**2-((yy-.063)/.024)**2)
     cx=side*head_w*.205
     z+=fm*.0052*math.exp(-((x-cx)/(head_w*.105))**2-((yy+.004)/.040)**2)
     z-=fm*.0022*math.exp(-((x-side*head_w*.255)/(head_w*.105))**2-((yy+.058)/.038)**2)
    # Narrow bridge and tip reinforce the explicit centre-line profile without inflating the whole muzzle.
    z+=fm*.0042*math.exp(-(x/(head_w*.062))**2-((yy-.002)/.052)**2)
    z+=fm*.0090*math.exp(-(x/(head_w*.062))**2-((yy+.043)/.018)**2)
    z-=fm*.0028*math.exp(-(x/(head_w*.052))**2-((yy+.061)/.012)**2)
    z+=fm*.0024*math.exp(-(x/(head_w*.142))**2-((yy+.082)/.018)**2)
    z+=fm*.0030*math.exp(-(x/(head_w*.118))**2-((yy+.116)/.019)**2)
   verts.append(bpos((x,yy,z)))
 faces=[]
 for r in range(len(rows)-1):
  a=r*segments;b=(r+1)*segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 faces.append(tuple(range(segments-1,-1,-1)))
 last=(len(rows)-1)*segments;faces.append(tuple(last+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('profile_head_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)
'''
if 'def add_profile_head_v55(' not in s:
    s=s.replace("ROOT=empty('BLENDER_HEROINE')",helper+"\nROOT=empty('BLENDER_HEROINE')",1)

# Remove the overlapping v4.8 shell + v5.4 face patch and replace both with one manifold portrait surface.
a=s.index("add_portrait_head_v44(HEAD,'HeadShellV48',[")
b=s.index("add_cylinder(HEAD,'Neck'",a)
head="""add_profile_head_v55(HEAD,'HeadShellV55',[
 (-.142,.038,.050,.064),
 (-.133,.058,.064,.078),
 (-.122,.078,.078,.096),
 (-.110,.094,.086,.104),
 (-.097,.108,.091,.107),
 (-.086,.118,.094,.110),
 (-.075,.125,.096,.109),
 (-.062,.130,.098,.103),
 (-.050,.132,.099,.108),
 (-.043,.133,.100,.132),
 (-.032,.133,.101,.120),
 (-.018,.133,.102,.112),
 (.000,.133,.103,.104),
 (.022,.132,.103,.097),
 (.040,.131,.103,.094),
 (.063,.128,.102,.103),
 (.088,.120,.100,.102),
 (.113,.106,.096,.094),
 (.138,.086,.087,.082),
 (.158,.061,.073,.067),
 (.174,.032,.052,.046)
],SKIN,96)
"""
s=s[:a]+head+s[b:]

# Eye placement follows the recessed v5.5 orbit of the new shell.
a=s.index('# Anatomy v5.4:')
b=s.index('# Hair v5.4:',a)
face=r'''# Anatomy v5.5: compact adult eyes seated in the recessed single-shell orbit.
face_front=.0848
eye_y=.0300
eye_x=head_w*.147
eye_rx=head_w*.098
eye_ry=.0107
eye_tilt=.0026
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV55_{side}',(ex,eye_y,.0740),(head_w*.067,.0140,.0105),SCLERA,42,24)
 add_almond_surface(HEAD,f'EyeOpeningV55_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00135,SCLERA,58,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV55_{side}',ex,eye_y,face_front+.0013,head_w*.038,.0079,IRIS,42)
 add_ellipse_surface(HEAD,f'IrisInnerV55_{side}',ex,eye_y-.0002,face_front+.0019,head_w*.023,.0053,IRIS_INNER,36)
 add_ellipse_surface(HEAD,f'PupilV55_{side}',ex,eye_y-.0002,face_front+.0025,head_w*.0108,.0032,PUPIL,28)
 add_ellipse_surface(HEAD,f'EyeLightV55_{side}',ex-side*head_w*.0075,eye_y+.0030,face_front+.0030,head_w*.0028,.0014,SCLERA,16)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV55_{side}',[(inner,inner_y+.0009,face_front+.0020),(ex,eye_y+.0110,face_front+.0027),(outer,outer_y+.0009,face_front+.0021)],.00034,FACE_DARK)
 add_strand(HEAD,f'UpperLashV55_{side}',[(inner,inner_y+.0012,face_front+.0027),(ex,eye_y+.0115,face_front+.0032),(outer,outer_y+.0012,face_front+.0028)],.00044,HAIR)
 add_strand(HEAD,f'LowerLidV55_{side}',[(inner+side*eye_rx*.10,inner_y-.0001,face_front+.0017),(ex,eye_y-.0071,face_front+.0021),(outer-side*eye_rx*.10,outer_y-.0001,face_front+.0017)],.00015,FACE_DARK)
 add_strand(HEAD,f'BrowV55_{side}',[(ex-side*eye_rx*.76,.0635,.1025),(ex,.0710,.1045),(ex+side*eye_rx*.96,.0608,.1030)],.00058,HAIR)

# Nose form belongs to HeadShellV55. Separate details are intentionally tiny.
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV55_{side}',(side*.0048,-.0530,.1280),(.00060,.00044,.00038),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV55',0,-.0778,.1127,.0305,.0046,.00120,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV55',0,-.0850,.1134,.0295,.0052,.00140,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV55',[(-.0265,-.0812,.1145),(0,-.0822,.1150),(.0265,-.0812,.1145)],.00016,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v5.4:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.5: upper scalp cap closes crown gaps; layered sweep sits over it; smooth pony is retained.
# Full cap exists only above the temple line, so it cannot become the old cheek-level helmet.
add_section_mesh(HEAD,'HairTopCapV55',[
 (.060,head_w*.455,head_d*.445,head_d*.500,-.018),
 (.095,head_w*.448,head_d*.438,head_d*.490,-.020),
 (.130,head_w*.405,head_d*.395,head_d*.445,-.021),
 (.160,head_w*.315,head_d*.305,head_d*.350,-.018),
 (.185,head_w*.190,head_d*.185,head_d*.215,-.010),
 (.202,head_w*.070,head_d*.070,head_d*.082,-.002)
],HAIR,56)
add_rear_hair_shell(HEAD,'HairRearShellV55',[
 (-.026,head_w*.292,head_d*.402,-head_d*.066),
 (.010,head_w*.420,head_d*.492,-head_d*.058),
 (.050,head_w*.495,head_d*.540,-head_d*.050),
 (.094,head_w*.518,head_d*.552,-head_d*.042),
 (.136,head_w*.480,head_d*.507,-head_d*.033),
 (.168,head_w*.386,head_d*.414,-head_d*.024),
 (.193,head_w*.226,head_d*.265,-head_d*.013),
 (.205,head_w*.078,head_d*.102,-head_d*.005)
],HAIR,44)

# Three overlapping sweeps now have a dark cap beneath them, so gaps read as hair rather than scalp.
add_flow_ribbon(HEAD,'FringeSweepV55_A',[(-.094,.180,.010),(-.080,.151,.047),(-.052,.118,.077),(-.012,.083,.099),(.032,.053,.111)],[.092,.092,.082,.064,.042],.00145,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV55_B',[(-.035,.181,.010),(-.014,.149,.050),(.020,.112,.081),(.060,.074,.102),(.094,.041,.111)],[.080,.077,.068,.052,.034],.00140,HAIR)
add_flow_ribbon(HEAD,'FringeSweepV55_C',[(.018,.175,.009),(.041,.142,.048),(.071,.104,.079),(.101,.064,.100),(.124,.028,.108)],[.064,.060,.052,.039,.026],.00135,HAIR)
add_strand(HEAD,'FringeEdgeV55_A',[(-.105,.170,.014),(-.067,.125,.076),(.012,.058,.112)],.00011,HAIR_HI)
add_strand(HEAD,'FringeEdgeV55_B',[(-.030,.172,.014),(.022,.120,.078),(.103,.038,.109)],.00010,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.392,.106,-head_d*.038),(side*head_w*.421,.040,-.013),(side*head_w*.425,-.038,-.016),(side*head_w*.412,-.108,-.043),(side*head_w*.397,-.177,-.062)]
 add_smooth_lock(HEAD,f'FaceLockV55_{side}',pts,[.009,.0115,.0095,.0055,.0024],[.0075,.0085,.0065,.0042,.0021],HAIR,10,5)

add_box(HEAD,'HairTieV55',(.014,.136,-head_d*.526),(.066,.015,.024),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(9):
 lane=(i-4)/4
 dz=lane*.034+((i%3)-1)*.010
 sway=.020*math.sin((i+1)*1.7)
 pts=[
  (lane*.020+.014,.136,-head_d*.538+dz*.20),
  (lane*.028+.018+sway*.20,.020,-head_d*.602+dz*.75),
  (lane*.040+.022+sway*.55,-.245,-.232+dz),
  (lane*.052+.027+sway,-.555,-.186+dz*1.20),
  (lane*.063+.032+sway*.70,-.890,-.143+dz*1.25),
  (lane*.073+.038+sway*.35,-1.210,-.112+dz*1.15),
  (lane*.082+.043,-1.445-(i%3)*.018,-.091+dz)
 ]
 base=.043-.006*abs(lane)
 widths=[base*.70,base,base*.94,base*.80,base*.59,base*.31,.0044]
 depths=[.022,.029,.029,.025,.019,.011,.0036]
 add_smooth_lock(PONY,f'PonyMassV55_{i}',pts,widths,depths,HAIR,10,6)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV55_{i}',[(lane*.022+.014,.134,-head_d*.543),(lane*.031+.020,-.030,-head_d*.607),(lane*.044+.026,-.345,-.214),(lane*.061+.034,-.810,-.147),(lane*.078+.045,-1.450-(i%2)*.020,-.087)],.00020+(i%2)*.00003,HAIR_HI if i in(1,3) else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V55: unified closed profile head, recessed orbit and scalp-covered hair')
