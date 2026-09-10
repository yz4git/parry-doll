from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V52' in s:
    print('Blender heroine generator already carries REFERENCE_V52')
    raise SystemExit(0)
if '# REFERENCE_V51' not in s:
    raise SystemExit('REFERENCE_V51 generator required before v5.2')

s=s.replace(
    '# REFERENCE_V51: explicit iris discs, asymmetric fringe and smoother pony flow.',
    '# REFERENCE_V51: explicit iris discs, asymmetric fringe and smoother pony flow.\n# REFERENCE_V52: Catmull-smoothed pony, broad swept fringe and larger dark-brown eyes.',
    1,
)

helper=r'''
def add_smooth_lock(p,name,pts,widths,depths,mat,ring_segments=12,samples=5):
 out=[];ow=[];od=[];n=len(pts)
 for i in range(n-1):
  p0=pts[max(0,i-1)];p1=pts[i];p2=pts[i+1];p3=pts[min(n-1,i+2)]
  for j in range(samples):
   t=j/samples;t2=t*t;t3=t2*t
   q=[]
   for k in range(3):
    q.append(.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t3))
   out.append(tuple(q));ow.append(widths[i]*(1-t)+widths[i+1]*t);od.append(depths[i]*(1-t)+depths[i+1]*t)
 out.append(pts[-1]);ow.append(widths[-1]);od.append(depths[-1])
 return add_lock_mesh(p,name,out,ow,od,mat,ring_segments)
'''
if 'def add_smooth_lock(' not in s:
    s=s.replace("ROOT=empty('BLENDER_HEROINE')",helper+"\nROOT=empty('BLENDER_HEROINE')",1)

# The reference reads as a dark iris filling most of the almond opening, not a tiny coloured dot.
s=s.replace("IRIS=material('Iris',(0.24,0.12,0.075),.01,.38)","IRIS=material('Iris',(0.17,0.075,0.048),.01,.36)",1)
s=s.replace("IRIS_INNER=material('Iris Inner',(0.39,0.20,0.10),.01,.40)","IRIS_INNER=material('Iris Inner',(0.30,0.135,0.065),.01,.38)",1)

a=s.index('# Anatomy v5.1:')
b=s.index('# Hair v5.1:',a)
face=r'''# Anatomy v5.2: larger dark-brown irises occupy the eye opening while preserving a slim almond sclera.
face_front=head_d*.531
eye_y=.0305
eye_x=head_w*.144
eye_rx=head_w*.145
eye_ry=.0180
eye_tilt=.0038
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV52_{side}',(ex,eye_y,head_d*.425),(head_w*.105,.0220,head_d*.068),SCLERA,48,30)
 add_almond_surface(HEAD,f'EyeOpeningV52_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0022,SCLERA,60,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV52_{side}',ex,eye_y,face_front+.0028,head_w*.115,.0146,IRIS,48)
 add_ellipse_surface(HEAD,f'IrisInnerV52_{side}',ex,eye_y-.0002,face_front+.0037,head_w*.074,.0107,IRIS_INNER,44)
 add_ellipse_surface(HEAD,f'PupilV52_{side}',ex,eye_y-.0003,face_front+.0045,head_w*.031,.0059,PUPIL,38)
 add_ellipse_surface(HEAD,f'EyeLightV52A_{side}',ex-side*head_w*.022,eye_y+.0058,face_front+.0052,head_w*.0066,.0028,SCLERA,20)
 add_ellipse_surface(HEAD,f'EyeLightV52B_{side}',ex+side*head_w*.012,eye_y+.0018,face_front+.0053,head_w*.0024,.0013,SCLERA,16)
 inner=ex-side*eye_rx*.95;outer=ex+side*eye_rx*1.02
 inner_y=eye_y-eye_tilt;outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLashV52_{side}',[(inner,inner_y+.0015,face_front+.0049),(ex,eye_y+.0187,face_front+.0060),(outer,outer_y+.0018,face_front+.0050)],.00062,HAIR)
 add_strand(HEAD,f'LashWingV52_{side}',[(outer,outer_y+.0018,face_front+.0050),(outer+side*head_w*.018,outer_y+.0068,face_front+.0053)],.00040,HAIR)
 add_strand(HEAD,f'BrowV52_{side}',[(ex-side*eye_rx*.75,.0700,head_d*.524),(ex,.0802,head_d*.528),(ex+side*eye_rx*.95,.0668,head_d*.524)],.00076,HAIR)

add_sphere(HEAD,'NoseTipSoftV52',(0,-.0430,head_d*.688),(.0061,.0056,.0034),SKIN,30,18)
for side in(-1,1):
 add_sphere(HEAD,f'NostrilV52_{side}',(side*.0056,-.0510,head_d*.670),(.00082,.00058,.00052),FACE_DARK,12,8)
add_almond_surface(HEAD,'UpperLipV52',0,-.0768,head_d*.678,.0390,.0060,.0023,LIP,56,1,0.0)
add_almond_surface(HEAD,'LowerLipV52',0,-.0860,head_d*.674,.0375,.0070,.0026,LIP,56,1,0.0)
add_strand(HEAD,'MouthSeamV52',[(-.0330,-.0816,head_d*.685),(0,-.0830,head_d*.688),(.0330,-.0816,head_d*.685)],.00022,FACE_DARK)

'''
s=s[:a]+face+s[b:]

a=s.index('# Hair v5.1:')
b=s.index('# === LIMBS ===',a)
hair=r'''# Hair v5.2: broad diagonal fringe over the open rear shell, plus spline-smoothed pony locks.
add_rear_hair_shell(HEAD,'HairRearShellV52',[
 (-.030,head_w*.300,head_d*.410,-head_d*.064),
 (.005,head_w*.425,head_d*.495,-head_d*.057),
 (.045,head_w*.497,head_d*.542,-head_d*.050),
 (.090,head_w*.520,head_d*.554,-head_d*.042),
 (.132,head_w*.482,head_d*.510,-head_d*.033),
 (.166,head_w*.390,head_d*.420,-head_d*.024),
 (.192,head_w*.230,head_d*.270,-head_d*.013),
 (.205,head_w*.080,head_d*.105,-head_d*.005)
],HAIR,44)

# Three broad swept sheets replace the repeated pointed-lock rhythm.
swept=[
 ((-.132,.181,head_d*.005),(-.105,.151,head_d*.285),(-.045,.104,head_d*.492),(.041,.050,head_d*.556),.076,.026),
 ((-.073,.184,head_d*.004),(-.040,.151,head_d*.312),(.025,.098,head_d*.507),(.091,.034,head_d*.551),.073,.024),
 ((-.010,.179,head_d*.003),(.026,.143,head_d*.300),(.086,.087,head_d*.480),(.132,.020,head_d*.538),.062,.020),
]
for i,(p0,p1,p2,p3,w0,w1) in enumerate(swept):
 add_flow_ribbon(HEAD,f'BangSweepV52_{i}',[p0,p1,p2,p3],[w0,w0*.90,w0*.63,w1],.00215,HAIR)

# Two irregular wisps break the silhouette without recreating a comb.
for i,(pts,w) in enumerate((
 ([(-.105,.174,head_d*.011),(-.052,.124,head_d*.365),(.030,.059,head_d*.555)],.00018),
 ([(-.035,.176,head_d*.009),(.026,.121,head_d*.382),(.112,.037,head_d*.544)],.00015),
)):
 add_strand(HEAD,f'BangWispV52_{i}',pts,w,HAIR_HI)

for side in(-1,1):
 pts=[(side*head_w*.394,.105,-head_d*.035),(side*head_w*.424,.038,-.010),(side*head_w*.428,-.043,-.012),(side*head_w*.414,-.115,-.042),(side*head_w*.400,-.190,-.063)]
 add_smooth_lock(HEAD,f'FaceLockV52_{side}',pts,[.010,.013,.011,.0065,.0028],[.0085,.0095,.0075,.0048,.0024],HAIR,10,4)

add_box(HEAD,'HairTieV52',(.014,.134,-head_d*.528),(.070,.017,.027),SILVER,.003)
PONY=empty('BL_PONY_DYNAMIC',HEAD)
for i in range(7):
 lane=(i-3)/3
 dz=lane*.019+((i%2)-.5)*.012
 # Fewer design bends, then Catmull interpolation generates the smooth cascade between them.
 pts=[
  (lane*.022+.014,.134,-head_d*.540+dz*.2),
  (lane*.032+.018,.010,-head_d*.610+dz),
  (lane*.046+.022,-.250,-.238+dz*1.15),
  (lane*.060+.027,-.560,-.190+dz*1.30),
  (lane*.072+.032,-.900,-.145+dz*1.35),
  (lane*.082+.037,-1.225,-.112+dz*1.30),
  (lane*.090+.042,-1.455-(i%3)*.020,-.092+dz*1.18)
 ]
 base=.057-.009*abs(lane)
 widths=[base*.68,base,base*.92,base*.78,base*.58,base*.32,.0050]
 depths=[.028,.038,.037,.032,.025,.015,.0042]
 add_smooth_lock(PONY,f'PonyMassV52_{i}',pts,widths,depths,HAIR_HI if i in(1,5) else HAIR,12,5)
for i in range(5):
 lane=(i-2)/2
 add_strand(PONY,f'PonyWispV52_{i}',[(lane*.024+.014,.132,-head_d*.545),(lane*.034+.019,-.040,-head_d*.605),(lane*.048+.025,-.350,-.218),(lane*.065+.033,-.820,-.150),(lane*.082+.044,-1.455-(i%2)*.024,-.086)],.00026+(i%2)*.00004,HAIR_HI if i%2==0 else HAIR)

'''
s=s[:a]+hair+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V52: smooth pony, swept fringe and larger dark-brown eyes')
