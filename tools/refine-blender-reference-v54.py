from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V54' in s:
    print('Blender heroine generator already carries REFERENCE_V54')
    raise SystemExit(0)
if '# REFERENCE_V53' not in s:
    raise SystemExit('REFERENCE_V53 generator required before v5.4')

s=s.replace(
    '# REFERENCE_V53: embedded portrait features, realistic iris scale, unified fringe and soft profile.',
    '# REFERENCE_V53: embedded portrait features, realistic iris scale, unified fringe and soft profile.\n# REFERENCE_V54: dedicated facial surface patch, explicit profile landmarks and unified fringe mass.',
    1,
)

helper='''
def add_face_patch_v54(p,name,rows,mat,cols=40):
 verts=[]
 for yy,half_w,front_z,edge_z in rows:
  for j in range(cols+1):
   u=-1.0+2.0*j/cols
   x=u*half_w
   blend=max(0.0,1.0-u*u)**0.62
   z=edge_z+(front_z-edge_z)*blend+.0012
   # Adult facial planes: cheekbone, orbital bowl and lower-cheek break.
   for side in (-1,1):
    ex=side*head_w*.147
    z-=.0066*math.exp(-((x-ex)/(head_w*.086))**2-((yy-.030)/.021)**2)
    cx=side*head_w*.205
    z+=.0058*math.exp(-((x-cx)/(head_w*.105))**2-((yy+.004)/.040)**2)
    z-=.0026*math.exp(-((x-side*head_w*.255)/(head_w*.105))**2-((yy+.058)/.038)**2)
   # Central profile is intentionally narrow; the row profile supplies most of the depth.
   z+=.0060*math.exp(-(x/(head_w*.062))**2-((yy-.006)/.055)**2)
   z+=.0170*math.exp(-(x/(head_w*.065))**2-((yy+.043)/.019)**2)
   z-=.0030*math.exp(-(x/(head_w*.055))**2-((yy+.061)/.013)**2)
   z+=.0035*math.exp(-(x/(head_w*.145))**2-((yy+.081)/.018)**2)
   z+=.0038*math.exp(-(x/(head_w*.118))**2-((yy+.116)/.020)**2)
   verts.append(bpos((x,yy,z)))
 row=cols+1;faces=[]
 for r in range(len(rows)-1):
  a=r*row;b=(r+1)*row
  for j in range(cols):
   faces.append((a+j,a+j+1,b+j+1,b+j))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('face_patch_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)
'''
if 'def add_face_patch_v54(' not in s:
    s=s.replace("ROOT=empty('BLENDER_HEROINE')",helper+"\nROOT=empty('BLENDER_HEROINE')",1)

# Demote the old ring shell from facial sculpt to cranium support. The new front patch will own the profile.
s=s.replace("z+=fm*.0100*math.exp(-(x/(head_w*.070))**2-((yy-.036)/.080)**2)",
            "z+=fm*.0065*math.exp(-(x/(head_w*.072))**2-((yy-.036)/.082)**2)",1)
s=s.replace("z+=fm*.0185*math.exp(-(x/(head_w*.068))**2-((yy+.005)/.064)**2)",
            "z+=fm*.0105*math.exp(-(x/(head_w*.070))**2-((yy+.005)/.066)**2)",1)
s=s.replace("z+=fm*.0305*math.exp(-(x/(head_w*.080))**2-((yy+.043)/.027)**2)",
            "z+=fm*.0165*math.exp(-(x/(head_w*.082))**2-((yy+.043)/.028)**2)",1)
s=s.replace("z+=fm*.0135*math.exp(-(x/(head_w*.168))**2-((yy+.082)/.030)**2)",
            "z+=fm*.0075*math.exp(-(x/(head_w*.170))**2-((yy+.082)/.032)**2)",1)
s=s.replace("z+=fm*.0155*math.exp(-(x/(head_w*.132))**2-((yy+.116)/.026)**2)",
            "z+=fm*.0090*math.exp(-(x/(head_w*.136))**2-((yy+.116)/.028)**2)",1)

# Insert a dedicated facial surface just in front of the cranium. The side profile is encoded by row.
anchor="] ,SKIN,96)"
# The real generator has no space before the comma; keep an explicit exact fallback.
needle="],SKIN,96)\nadd_cylinder(HEAD,'Neck'"
if needle not in s:
    raise SystemExit('Head shell insertion anchor not found for v5.4')
face_patch="""],SKIN,96)
add_face_patch_v54(HEAD,'FacePatchV54',[
 (-.137,head_w*.135,head_d*.300,.046),
 (-.126,head_w*.225,head_d*.420,.040),
 (-.114,head_w*.292,head_d*.485,.033),
 (-.101,head_w*.340,head_d*.505,.025),
 (-.088,head_w*.375,head_d*.525,.017),
 (-.076,head_w*.402,head_d*.520,.011),
 (-.062,head_w*.420,head_d*.490,.005),
 (-.047,head_w*.432,head_d*.535,-.001),
 (-.035,head_w*.438,head_d*.555,-.004),
 (-.020,head_w*.444,head_d*.520,-.007),
 (.000,head_w*.448,head_d*.495,-.010),
 (.022,head_w*.452,head_d*.462,-.012),
 (.042,head_w*.450,head_d*.452,-.014),
 (.064,head_w*.440,head_d*.478,-.017),
 (.088,head_w*.420,head_d*.472,-.021),
 (.112,head_w*.380,head_d*.438,-.026),
 (.136,head_w*.315,head_d*.385,-.030),
 (.157,head_w*.225,head_d*.318,-.033)
],SKIN,40)
add_cylinder(HEAD,'Neck'"""
s=s.replace(needle,face_patch,1)

# Dark neutral eyes and lips that sit on the face patch instead of projecting far in front.
s=s.replace("IRIS=material('Iris',(0.105,0.045,0.030),.01,.38)","IRIS=material('Iris',(0.075,0.036,0.024),.01,.40)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.34,0.145,0.070),.01,.42)","IRIS_INNER=material('Iris Inner',(0.28,0.115,0.052),.01,.44)",1)

a=s.index('# Anatomy v5.3:')
b=s.index('# Hair v5.3:',a)
face=r'''# Anatomy v5.4: compact adult eyes and mouth are seated directly on the dedicated facial patch.
face_front=head_d*.408
eye_y=.0300
eye_x=head_w*.147
eye_rx=head_w*.096
eye_ry=.0104
eye_tilt=.0025
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV54_{side}',(ex,eye_y,head_d*.376),(head_w*.067,.0140,head_d*.044),SCLERA,42,24)
 add_almond_surface(HEAD,f'EyeOpeningV54_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0014,SCLERA,58,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV54_{side}',ex,eye_y,face_front+.0013,head_w*.036,.0077,IRIS,42)
 add_ellipse_surface(HEAD,f'IrisInnerV54_{side}',ex,eye_y-.0002,face_front+.0019,head_w*.022,.0051,IRIS_INNER,36)
 add_ellipse_surface(HEAD,f'PupilV54_{side}',ex,eye_y-.0002,face_front+.0025,head_w*.0105,.0032,PUPIL,28)
 add_ellipse_surface(HEAD,f'EyeLightV54_{side}',ex-side*head_w*.0075,eye_y+.0029,face_front+.0030,head_w*.0028,.0014,SCLERA,16)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV54_{side}',[(inner,inner_y+.0009,face_front+.0020),(ex,eye_y+.0108,face_front+.0027),(outer,outer_y+.0009,face_front+.0021)],.00034,FACE_DARK)
 add_strand(HEAD,f'UpperLashV54_{side}',[(inner,inner_y+.0012,face_front+.0027),(ex,eye_y+.0113,face_front+.0032),(outer,outer_y+.0012,face_front+.0028)],.00044,HAIR)
 add_strand(HEAD,f'LowerLidV54_{side}',[(inner+side*eye_rx*.10,inner_y-.0001,face_front+.0017),(ex,eye_y-.0070,face_front+.0021),(outer-side*eye_rx*.10,outer_y-.0001,face_front+.0017)],.00016,FACE_DARK)
 add_strand(HEAD,f'BrowV54_{side}',[(ex-side*eye_rx*.76,.0635,head_d*.438),(ex,.0710,head_d*.444),(ex+side*eye_rx*.96,.0608,head_d*.439)],.00058,HAIR)

# The patch already forms the nose. Only nostrils and lips are separate finishing geometry.
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV54_{side}',(side*.0049,-.0525,head_d*.598),(.00062,.00046,.00040),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV54',0,-.0778,head_d*.552,.0310,.0046,.00125,LIP,52,1,0.0)
add_almond_surface(HEAD,'LowerLipV54',0,-.0850,head_d*.548,.0300,.0052,.00145,LIP,52,1,0.0)
add_strand(HEAD,'MouthSeamV54',[(-.0270,-.0812,head_d*.557),(0,-.0822,head_d*.559),(.0270,-.0812,head_d*.557)],.00016,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v5.3:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.4: one dominant swept fringe mass, one secondary layer and the proven smooth v5.3 pony.
add_rear_hair_shell(HEAD,'HairRearShellV54',[
 (-.026,head_w*.292,head_d*.402,-head_d*.066),
 (.010,head_w*.420,head_d*.492,-head_d*.058),
 (.050,head_w*.495,head_d*.540,-head_d*.050),
 (.094,head_w*.518,head_d*.552,-head_d*.042),
 (.136,head_w*.480,head_d*.507,-head_d*.033),
 (.168,head_w*.386,head_d*.414,-head_d*.024),
 (.193,head_w*.226,head_d*.265,-head_d*.013),
 (.205,head_w*.078,head_d*.102,-head_d*.005)
],HAIR,44)

# A broad main sheet unifies the crown-to-forehead flow instead of exposing four independent claws.
add_flow_ribbon(HEAD,'FringeMassV54',[
 (-.075,.181,head_d*.002),(-.064,.158,head_d*.205),(-.036,.128,head_d*.370),(.004,.094,head_d*.487),(.050,.058,head_d*.530)
],[.150,.150,.137,.108,.066],.00165,HAIR)
add_flow_ribbon(HEAD,'FringeSideV54',[
 (.015,.176,head_d*.002),(.043,.147,head_d*.225),(.075,.109,head_d*.385),(.104,.067,head_d*.492),(.128,.027,head_d*.516)
],[.082,.078,.067,.050,.030],.00155,HAIR)
# Fine breakup at the edge keeps the mass organic without a comb of separate locks.
add_strand(HEAD,'FringeEdgeV54_A',[(-.106,.170,head_d*.006),(-.067,.127,head_d*.350),(.012,.061,head_d*.532)],.00013,HAIR_HI)
add_strand(HEAD,'FringeEdgeV54_B',[(-.032,.174,head_d*.006),(.024,.122,head_d*.363),(.103,.039,head_d*.514)],.00011,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.392,.106,-head_d*.038),(side*head_w*.421,.040,-.013),(side*head_w*.425,-.038,-.016),(side*head_w*.412,-.108,-.043),(side*head_w*.397,-.177,-.062)]
 add_smooth_lock(HEAD,f'FaceLockV54_{side}',pts,[.009,.0115,.0095,.0055,.0024],[.0075,.0085,.0065,.0042,.0021],HAIR,10,5)

add_box(HEAD,'HairTieV54',(.014,.136,-head_d*.526),(.066,.015,.024),SILVER,.003)
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
 add_smooth_lock(PONY,f'PonyMassV54_{i}',pts,widths,depths,HAIR,10,6)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV54_{i}',[(lane*.022+.014,.134,-head_d*.543),(lane*.031+.020,-.030,-head_d*.607),(lane*.044+.026,-.345,-.214),(lane*.061+.034,-.810,-.147),(lane*.078+.045,-1.450-(i%2)*.020,-.087)],.00020+(i%2)*.00003,HAIR_HI if i in(1,3) else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V54: dedicated face patch, explicit profile and unified fringe mass')
