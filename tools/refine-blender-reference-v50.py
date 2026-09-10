from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V50' in s:
    print('Blender heroine generator already carries REFERENCE_V50')
    raise SystemExit(0)
if '# REFERENCE_V49' not in s:
    raise SystemExit('REFERENCE_V49 generator required before v5.0')

s=s.replace(
    '# REFERENCE_V49: skull-hugging hair, vertical pony cascade, readable warm irises and stronger profile.',
    '# REFERENCE_V49: skull-hugging hair, vertical pony cascade, readable warm irises and stronger profile.\n# REFERENCE_V50: open rear hair shell, readable portrait eyes, softer profile and connected shoulders.',
    1,
)

# A full 360-degree section mesh inevitably becomes a helmet at the cheeks. Build a rear-only scalp shell
# and let the fringe cover the open front instead.
helper=r'''
def add_rear_hair_shell(p,name,sections,mat,segments=36):
 verts=[]
 # Logical Z is front/back; only sample the rear half of each horizontal section.
 angles=[math.pi+.055+(math.pi-.110)*i/segments for i in range(segments+1)]
 for yy,w,depth,zoff in sections:
  for ang in angles:
   verts.append(bpos((math.cos(ang)*w,yy,zoff+math.sin(ang)*depth)))
 row=len(angles);faces=[]
 for r in range(len(sections)-1):
  base=r*row;nxt=(r+1)*row
  for i in range(row-1):faces.append((base+i,base+i+1,nxt+i+1,nxt+i))
 # Close the two temple seams and the small top/bottom openings, while leaving the face fully open.
 left=[r*row for r in range(len(sections))];right=[r*row+row-1 for r in range(len(sections))]
 faces.append(tuple(left));faces.append(tuple(reversed(right)))
 faces.append(tuple(range(row-1,-1,-1)));last=(len(sections)-1)*row;faces.append(tuple(last+i for i in range(row)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('rear_hair_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)
'''
if 'def add_rear_hair_shell(' not in s:
    s=s.replace("ROOT=empty('BLENDER_HEROINE')",helper+"\nROOT=empty('BLENDER_HEROINE')",1)

# Stronger deltoid bridge reaches the actual visual shoulder joint without increasing runtime shoulder width.
s=s.replace("add_sphere(TORSO,f'DeltoidBridge_{side}',(side*bust_w*.335,.238,.002),(bust_w*.096,.060,bust_d*.136),BLACK,30,20)",
            "add_sphere(TORSO,f'DeltoidBridgeV50_{side}',(side*bust_w*.415,.238,.002),(bust_w*.126,.062,bust_d*.142),BLACK,34,22)",1)
s=s.replace("(side*bust_w*.392,.225,bust_d*.18)","(side*bust_w*.475,.225,bust_d*.18)",2)

# The v4.9 profile over-emphasized the nose while the mouth/chin stayed behind it. Rebalance the shell.
s=s.replace("z+=fm*.0620*math.exp(-(x/(head_w*.076))**2-((yy+.043)/.025)**2)",
            "z+=fm*.0530*math.exp(-(x/(head_w*.078))**2-((yy+.043)/.026)**2)",1)
s=s.replace("z+=fm*.0155*math.exp(-(x/(head_w*.158))**2-((yy+.082)/.026)**2)",
            "z+=fm*.0220*math.exp(-(x/(head_w*.164))**2-((yy+.082)/.028)**2)",1)
s=s.replace("z+=fm*.0170*math.exp(-(x/(head_w*.122))**2-((yy+.118)/.022)**2)",
            "z+=fm*.0240*math.exp(-(x/(head_w*.128))**2-((yy+.116)/.024)**2)",1)

# Softer, brighter warm iris survives the iPhone-sized face preset without becoming a black dot.
s=s.replace("IRIS=material('Iris',(0.38,0.20,0.12),.02,.36)","IRIS=material('Iris',(0.48,0.27,0.16),.01,.42)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.56,0.27,0.12),.01,.40)","IRIS_INNER=material('Iris Inner',(0.66,0.36,0.17),.01,.44)",1)

a=s.index('# Anatomy v4.9:')
b=s.index('# Hair v4.9:',a)
face=r'''# Anatomy v5.0: wider readable almond eye, flattened iris layers and a balanced nose-mouth-chin profile.
face_front=head_d*.531
eye_y=.0300
eye_x=head_w*.144
eye_rx=head_w*.132
eye_ry=.0138
eye_tilt=.0035
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV50_{side}',(ex,eye_y,head_d*.425),(head_w*.098,.0200,head_d*.067),SCLERA,46,28)
 add_almond_surface(HEAD,f'EyeOpeningV50_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0023,SCLERA,56,side,eye_tilt)
 # Flattened ellipsoids sit almost coplanar with the eye opening so the brown iris reads as an iris, not a dot.
 add_sphere(HEAD,f'IrisV50_{side}',(ex,eye_y,face_front+.0033),(head_w*.091,.0125,.00155),IRIS,46,28)
 add_sphere(HEAD,f'IrisInnerV50_{side}',(ex,eye_y-.0003,face_front+.0047),(head_w*.057,.0091,.00105),IRIS_INNER,40,24)
 add_sphere(HEAD,f'PupilV50_{side}',(ex,eye_y-.0003,face_front+.0057),(head_w*.020,.0052,.00075),PUPIL,30,18)
 add_sphere(HEAD,f'EyeLightV50A_{side}',(ex-side*head_w*.019,eye_y+.0050,face_front+.0065),(head_w*.0064,.0028,.00055),SCLERA,14,8)
 add_sphere(HEAD,f'EyeLightV50B_{side}',(ex+side*head_w*.010,eye_y+.0016,face_front+.0066),(head_w*.0023,.0013,.00040),SCLERA,10,6)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV50_{side}',[(inner,inner_y+.0009,face_front+.0032),(ex,eye_y+.0140,face_front+.0055),(outer,outer_y+.0010,face_front+.0032)],.00048,FACE_DARK)
 add_strand(HEAD,f'UpperLashV50_{side}',[(inner,inner_y+.0015,face_front+.0055),(ex,eye_y+.0148,face_front+.0068),(outer,outer_y+.0017,face_front+.0056)],.00062,HAIR)
 add_strand(HEAD,f'LashWingV50_{side}',[(outer,outer_y+.0017,face_front+.0056),(outer+side*head_w*.016,outer_y+.0058,face_front+.0059)],.00042,HAIR)
 add_strand(HEAD,f'BrowV50_{side}',[(ex-side*eye_rx*.76,.0685,head_d*.524),(ex,.0785,head_d*.528),(ex+side*eye_rx*.96,.0660,head_d*.524)],.00082,HAIR)

# Keep only subtle finishing volumes; the continuous shell now carries the profile.
add_sphere(HEAD,'NoseTipSoftV50',(0,-.0430,head_d*.690),(.0066,.0061,.0038),SKIN,30,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV50_{side}',(side*.0058,-.0515,head_d*.671),(.00090,.00065,.00060),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV50',0,-.0770,head_d*.674,.0380,.0058,.0022,LIP,54,1,0.0)
add_almond_surface(HEAD,'LowerLipV50',0,-.0862,head_d*.670,.0365,.0068,.0025,LIP,54,1,0.0)
add_strand(HEAD,'MouthSeamV50',[(-.0320,-.0818,head_d*.681),(0,-.0832,head_d*.684),(.0320,-.0818,head_d*.681)],.00024,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v4.9:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.0: open rear scalp shell plus layered front fringe; no cheek-level helmet ring.
add_rear_hair_shell(HEAD,'HairRearShellV50',[
 (-.058,head_w*.330,head_d*.430,-head_d*.060),
 (-.020,head_w*.445,head_d*.505,-head_d*.055),
 (.025,head_w*.505,head_d*.545,-head_d*.050),
 (.075,head_w*.525,head_d*.558,-head_d*.043),
 (.120,head_w*.500,head_d*.525,-head_d*.034),
 (.158,head_w*.410,head_d*.440,-head_d*.025),
 (.187,head_w*.245,head_d*.285,-head_d*.014),
 (.202,head_w*.090,head_d*.115,-head_d*.006)
],HAIR,42)

# Six dark overlapping sheets make a single swept fringe while leaving both eyes readable.
bangs=[
 ((-.124,.171,head_d*.008),(-.107,.143,head_d*.270),(-.080,.104,head_d*.475),(-.055,.055,head_d*.548),.046,.017),
 ((-.091,.176,head_d*.008),(-.070,.146,head_d*.294),(-.040,.103,head_d*.494),(-.013,.047,head_d*.556),.049,.018),
 ((-.054,.179,head_d*.006),(-.029,.147,head_d*.306),(.005,.102,head_d*.500),(.033,.040,head_d*.557),.050,.018),
 ((-.017,.178,head_d*.005),(.011,.146,head_d*.305),(.046,.099,head_d*.495),(.076,.033,head_d*.554),.048,.017),
 ((.020,.174,head_d*.004),(.047,.141,head_d*.290),(.082,.093,head_d*.478),(.109,.026,head_d*.546),.043,.016),
 ((.053,.166,head_d*.003),(.079,.133,head_d*.265),(.110,.084,head_d*.452),(.131,.020,head_d*.536),.037,.014),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(bangs):
 add_flow_ribbon(HEAD,f'BangSheetV50_{i}',[p0,p1,p2,p3],[w0,w0*.91,w0*.64,w1],.0023,HAIR)

# Hairline accents are extremely fine; they should never read as bright ribbons.
for i,(x0,x1,x2,y2) in enumerate(((-.106,-.042,.016,.058),(-.057,.012,.072,.049),(-.004,.058,.116,.033))):
 add_strand(HEAD,f'BangHighlightV50_{i}',[(x0+.004,.169,head_d*.010),(x1+.004,.124,head_d*.355),(x2+.003,y2+.003,head_d*.558)],.00016,HAIR_HI)

# Narrow face-framing pieces sit behind the cheek plane instead of forming vertical side bars.
for side in(-1,1):
 pts=[(side*head_w*.382,.102,-head_d*.020),(side*head_w*.420,.034,head_d*.018),(side*head_w*.428,-.060,head_d*.022),(side*head_w*.412,-.150,-.012),(side*head_w*.392,-.245,-.046)]
 add_lock_mesh(HEAD,f'FaceLockV50_{side}',pts,[.013,.016,.014,.009,.0035],[.010,.011,.009,.006,.003],HAIR,12)
 add_strand(HEAD,f'FaceWispV50_{side}',[(side*head_w*.401,.088,-.012),(side*head_w*.438,-.020,head_d*.012),(side*head_w*.424,-.160,-.022),(side*head_w*.402,-.300,-.050)],.00032,HAIR_HI)

# Seven separated locks form a tapered cascade. Depth offsets and alternating curves keep side view from collapsing into one board.
add_box(HEAD,'HairTieV50',(.015,.132,-head_d*.535),(.076,.018,.030),SILVER,.0035)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(7):
 lane=(i-3)/3
 depth_lane=lane*.020+((i%2)-.5)*.012
 pts=[
  (lane*.024+.015,.132,-head_d*.545+depth_lane*.25),
  (lane*.032+.018,.020,-head_d*.620+depth_lane),
  (lane*.043+.022,-.200,-.245+depth_lane*1.2),
  (lane*.055+.025,-.470,-.205+depth_lane*1.4),
  (lane*.066+.030,-.770,-.165+depth_lane*1.5),
  (lane*.078+.035,-1.080,-.128+depth_lane*1.5),
  (lane*.088+.040,-1.400-(i%3)*.025,-.095+depth_lane*1.3)
 ]
 base=.066-.010*abs(lane)
 add_lock_mesh(PONY,f'PonyMassV50_{i}',pts,[base*.70,base,base*.96,base*.88,base*.68,base*.40,.0065],[.034,.040,.043,.039,.031,.020,.005],HAIR_HI if i in(1,5) else HAIR,12)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV50_{i}',[(lane*.026+.015,.132,-head_d*.548),(lane*.035+.020,-.030,-head_d*.630),(lane*.048+.026,-.330,-.230),(lane*.065+.034,-.800,-.155),(lane*.084+.045,-1.420-(i%2)*.028,-.088)],.00030+(i%2)*.00005,HAIR_HI if i%2==0 else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V50: open rear hair shell, readable eyes, softer profile and connected shoulders')
