from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V51' in s:
    print('Blender heroine generator already carries REFERENCE_V51')
    raise SystemExit(0)
if '# REFERENCE_V50' not in s:
    raise SystemExit('REFERENCE_V50 generator required before v5.1')

s=s.replace(
    '# REFERENCE_V50: open rear hair shell, readable portrait eyes, softer profile and connected shoulders.',
    '# REFERENCE_V50: open rear hair shell, readable portrait eyes, softer profile and connected shoulders.\n# REFERENCE_V51: explicit iris discs, asymmetric fringe and smoother pony flow.',
    1,
)

helper=r'''
def add_ellipse_surface(p,name,cx,cy,cz,rx,ry,mat,segments=40):
 verts=[bpos((cx,cy,cz))]
 for i in range(segments):
  a=2*math.pi*i/segments
  verts.append(bpos((cx+rx*math.cos(a),cy+ry*math.sin(a),cz)))
 faces=[(0,1+i,1+((i+1)%segments)) for i in range(segments)]
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)
'''
if 'def add_ellipse_surface(' not in s:
    s=s.replace("ROOT=empty('BLENDER_HEROINE')",helper+"\nROOT=empty('BLENDER_HEROINE')",1)

s=s.replace("IRIS=material('Iris',(0.48,0.27,0.16),.01,.42)","IRIS=material('Iris',(0.24,0.12,0.075),.01,.38)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.66,0.36,0.17),.01,.44)","IRIS_INNER=material('Iris Inner',(0.39,0.20,0.10),.01,.40)",1)

a=s.index('# Anatomy v5.0:')
b=s.index('# Hair v5.0:',a)
face=r'''# Anatomy v5.1: explicit flat iris discs guarantee readable dark-brown eyes at iPhone scale.
face_front=head_d*.531
eye_y=.0300
eye_x=head_w*.144
eye_rx=head_w*.138
eye_ry=.0150
eye_tilt=.0035
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV51_{side}',(ex,eye_y,head_d*.425),(head_w*.100,.0205,head_d*.067),SCLERA,46,28)
 add_almond_surface(HEAD,f'EyeOpeningV51_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0022,SCLERA,58,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV51_{side}',ex,eye_y,face_front+.0026,head_w*.094,.0126,IRIS,44)
 add_ellipse_surface(HEAD,f'IrisInnerV51_{side}',ex,eye_y-.0002,face_front+.0035,head_w*.061,.0092,IRIS_INNER,40)
 add_ellipse_surface(HEAD,f'PupilV51_{side}',ex,eye_y-.0002,face_front+.0043,head_w*.023,.0048,PUPIL,36)
 add_ellipse_surface(HEAD,f'EyeLightV51A_{side}',ex-side*head_w*.019,eye_y+.0048,face_front+.0050,head_w*.0062,.0026,SCLERA,20)
 add_ellipse_surface(HEAD,f'EyeLightV51B_{side}',ex+side*head_w*.010,eye_y+.0015,face_front+.0051,head_w*.0022,.0012,SCLERA,16)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLashV51_{side}',[(inner,inner_y+.0014,face_front+.0048),(ex,eye_y+.0159,face_front+.0058),(outer,outer_y+.0017,face_front+.0049)],.00059,HAIR)
 add_strand(HEAD,f'LashWingV51_{side}',[(outer,outer_y+.0017,face_front+.0049),(outer+side*head_w*.017,outer_y+.0062,face_front+.0052)],.00039,HAIR)
 add_strand(HEAD,f'BrowV51_{side}',[(ex-side*eye_rx*.76,.0680,head_d*.524),(ex,.0780,head_d*.528),(ex+side*eye_rx*.96,.0655,head_d*.524)],.00078,HAIR)

add_sphere(HEAD,'NoseTipSoftV51',(0,-.0430,head_d*.690),(.0063,.0058,.0035),SKIN,30,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV51_{side}',(side*.0057,-.0512,head_d*.671),(.00085,.00060,.00055),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV51',0,-.0770,head_d*.676,.0385,.0059,.0022,LIP,54,1,0.0)
add_almond_surface(HEAD,'LowerLipV51',0,-.0860,head_d*.672,.0370,.0069,.0025,LIP,54,1,0.0)
add_strand(HEAD,'MouthSeamV51',[(-.0325,-.0817,head_d*.683),(0,-.0831,head_d*.686),(.0325,-.0817,head_d*.683)],.00023,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v5.0:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.1: rear scalp remains open-front; fringe becomes broader and intentionally asymmetric.
add_rear_hair_shell(HEAD,'HairRearShellV51',[
 (-.035,head_w*.305,head_d*.415,-head_d*.064),
 (.000,head_w*.430,head_d*.500,-head_d*.057),
 (.040,head_w*.500,head_d*.545,-head_d*.050),
 (.085,head_w*.520,head_d*.555,-head_d*.042),
 (.128,head_w*.485,head_d*.515,-head_d*.033),
 (.163,head_w*.395,head_d*.425,-head_d*.024),
 (.190,head_w*.235,head_d*.275,-head_d*.013),
 (.204,head_w*.085,head_d*.110,-head_d*.005)
],HAIR,44)

# Four main sheets plus two crossing overlays remove the regular comb/tooth rhythm.
main_bangs=[
 ((-.126,.177,head_d*.006),(-.106,.146,head_d*.285),(-.064,.101,head_d*.495),(-.024,.048,head_d*.556),.061,.024),
 ((-.076,.181,head_d*.005),(-.050,.148,head_d*.306),(-.005,.100,head_d*.506),(.038,.038,head_d*.558),.065,.025),
 ((-.020,.180,head_d*.004),(.010,.145,head_d*.306),(.058,.094,head_d*.492),(.094,.027,head_d*.550),.060,.022),
 ((.035,.172,head_d*.003),(.064,.136,head_d*.280),(.105,.082,head_d*.462),(.132,.018,head_d*.538),.050,.018),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(main_bangs):
 add_flow_ribbon(HEAD,f'BangMainV51_{i}',[p0,p1,p2,p3],[w0,w0*.93,w0*.68,w1],.0022,HAIR)
for i,(p0,p1,p2,w0) in enumerate((
 ((-.105,.174,head_d*.012),(-.044,.126,head_d*.372),(.052,.055,head_d*.555),.032),
 ((-.045,.178,head_d*.010),(.025,.125,head_d*.385),(.115,.035,head_d*.545),.030),
)):
 add_flow_ribbon(HEAD,f'BangCrossV51_{i}',[p0,p1,p2],[w0,w0*.74,.010],.0019,HAIR)
 add_strand(HEAD,f'BangHighlightV51_{i}',[(p0[0]+.004,p0[1],p0[2]+.002),(p1[0]+.004,p1[1],p1[2]+.003),(p2[0]+.003,p2[1]+.002,p2[2]+.003)],.00014,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.392,.105,-head_d*.032),(side*head_w*.424,.036,-.004),(side*head_w*.428,-.050,-.004),(side*head_w*.414,-.125,-.035),(side*head_w*.398,-.205,-.060)]
 add_lock_mesh(HEAD,f'FaceLockV51_{side}',pts,[.011,.014,.012,.007,.0030],[.009,.010,.008,.005,.0026],HAIR,12)

# More control points round the pony curve; narrower staggered locks prevent a single angular board in profile.
add_box(HEAD,'HairTieV51',(.014,.134,-head_d*.530),(.072,.017,.028),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(7):
 lane=(i-3)/3
 dz=lane*.018+((i%2)-.5)*.010
 pts=[
  (lane*.022+.014,.134,-head_d*.540+dz*.2),
  (lane*.027+.016,.075,-head_d*.590+dz*.5),
  (lane*.033+.018,-.010,-head_d*.610+dz),
  (lane*.040+.020,-.130,-.315+dz*1.1),
  (lane*.048+.023,-.285,-.235+dz*1.2),
  (lane*.056+.026,-.470,-.200+dz*1.3),
  (lane*.064+.029,-.680,-.170+dz*1.35),
  (lane*.072+.033,-.910,-.142+dz*1.35),
  (lane*.080+.037,-1.150,-.118+dz*1.3),
  (lane*.087+.041,-1.390-(i%3)*.022,-.096+dz*1.2)
 ]
 base=.058-.009*abs(lane)
 widths=[base*.68,base*.86,base,base*.98,base*.91,base*.82,base*.69,base*.54,base*.34,.0055]
 depths=[.029,.034,.038,.039,.037,.034,.029,.023,.015,.0045]
 add_lock_mesh(PONY,f'PonyMassV51_{i}',pts,widths,depths,HAIR_HI if i in(1,5) else HAIR,12)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV51_{i}',[(lane*.024+.014,.132,-head_d*.545),(lane*.032+.018,-.020,-head_d*.610),(lane*.044+.024,-.300,-.225),(lane*.061+.032,-.760,-.158),(lane*.080+.043,-1.400-(i%2)*.026,-.090)],.00028+(i%2)*.00004,HAIR_HI if i%2==0 else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V51: explicit iris discs, asymmetric fringe and smoother pony flow')
