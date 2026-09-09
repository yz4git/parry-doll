from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V38' in s:
    print('Blender heroine generator already carries REFERENCE_V38')
    raise SystemExit(0)
if '# REFERENCE_V37' not in s:
    raise SystemExit('REFERENCE_V37 generator required before v3.8')
s=s.replace('# REFERENCE_V37: separate skull width from hair span and retarget portrait features to the narrower face.','# REFERENCE_V37: separate skull width from hair span and retarget portrait features to the narrower face.\n# REFERENCE_V38: tilted expressive almond eyes and stronger central portrait cues.',1)

# Upgrade the visible-eye helper so the almond can tilt upward toward the outer corner.
a=s.index('def add_almond_surface(')
b=s.index('def add_ribbon(',a)
helper="""def add_almond_surface(p,name,cx,cy,cz,rx,ry,bulge,mat,segments=28,side=1,tilt=0.0):
 verts=[bpos((cx,cy,cz+bulge))]
 for i in range(segments):
  a=2*math.pi*i/segments
  ca=math.cos(a);sa=math.sin(a)
  x=cx+rx*ca
  # Pinched almond with a slight canthal tilt: the outer corner sits higher than the inner corner.
  yy=cy+ry*sa*(.68+.32*abs(ca))+tilt*side*ca
  verts.append(bpos((x,yy,cz)))
 faces=[]
 for i in range(segments):faces.append((0,1+i,1+((i+1)%segments)))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o);return parent(o,p)

"""
s=s[:a]+helper+s[b:]

# Slightly reinforce the nose bridge/tip in the connected head shell. No separate mask is introduced.
a=s.index('def add_anatomical_head(')
b=s.index('def add_lock_mesh(',a)
head_helper=s[a:b]
head_helper=head_helper.replace("z+=fm*.0145*math.exp(-(x/(head_w*.060))**2-((yy-.020)/.086)**2)","z+=fm*.0170*math.exp(-(x/(head_w*.060))**2-((yy-.020)/.086)**2)",1)
head_helper=head_helper.replace("z+=fm*.0315*math.exp(-(x/(head_w*.076))**2-((yy+.041)/.025)**2)","z+=fm*.0355*math.exp(-(x/(head_w*.076))**2-((yy+.041)/.025)**2)",1)
head_helper=head_helper.replace("z+=fm*.0060*math.exp(-(x/(head_w*.052))**2-((yy+.058)/.017)**2)","z+=fm*.0072*math.exp(-(x/(head_w*.052))**2-((yy+.058)/.017)**2)",1)
s=s[:a]+head_helper+s[b:]

# Replace only the portrait feature assembly. The v3.7 skull/hair/body remain unchanged.
a=s.index('# Anatomy v3.6:')
b=s.index('# Hair v3.6:',a)
face="""# Anatomy v3.8: narrower v3.7 skull with expressive tilted almond eyes and readable central features.
face_front=head_d*.512
eye_y=.030
eye_x=head_w*.139
eye_rx=head_w*.122
eye_ry=.0168
eye_tilt=.0044
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV38_{side}',(ex,eye_y,head_d*.423),(head_w*.098,.019,head_d*.072),SCLERA,34,22)
 add_almond_surface(HEAD,f'EyeOpeningV38_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.0032,SCLERA,32,side,eye_tilt)
 # Iris coverage is increased so the eye reads expressive rather than googly/white-heavy.
 add_sphere(HEAD,f'IrisV38_{side}',(ex,eye_y+.0010,face_front+.0058),(head_w*.050,.0122,.0030),IRIS,28,18)
 add_sphere(HEAD,f'PupilV38_{side}',(ex,eye_y+.0010,face_front+.0084),(head_w*.0185,.0063,.0020),PUPIL,20,12)
 add_sphere(HEAD,f'EyeLightV38_{side}',(ex-side*head_w*.012,eye_y+.0065,face_front+.0104),(head_w*.0075,.0032,.0013),SCLERA,12,8)
 inner=ex-side*eye_rx*.93;outer=ex+side*eye_rx*.99
 # The lash arc follows the same outward-up tilt as the sclera opening.
 inner_y=eye_y-eye_tilt
 outer_y=eye_y+eye_tilt
 add_strand(HEAD,f'UpperLidV38_{side}',[(inner,inner_y+.001,face_front+.0024),(ex,eye_y+.0165,face_front+.0056),(outer,outer_y+.001,face_front+.0024)],.00125,SKIN)
 add_strand(HEAD,f'LowerLidV38_{side}',[(inner,inner_y-.001,face_front+.0020),(ex,eye_y-.0105,face_front+.0030),(outer,outer_y-.001,face_front+.0020)],.00078,SKIN)
 add_strand(HEAD,f'UpperLashV38_{side}',[(inner,inner_y+.003,face_front+.0065),(ex,eye_y+.0180,face_front+.0080),(outer,outer_y+.003,face_front+.0065)],.00205,HAIR)
 add_strand(HEAD,f'LashWingV38_{side}',[(outer,outer_y+.003,face_front+.0068),(outer+side*head_w*.034,outer_y+.011,face_front+.0075)],.00155,HAIR)
 add_strand(HEAD,f'LowerLashV38_{side}',[(inner,inner_y,face_front+.0047),(ex,eye_y-.0095,face_front+.0050),(outer,outer_y,face_front+.0047)],.00048,HAIR)
 # Brows are closer to the eye and follow a gentle key-art arch.
 add_strand(HEAD,f'BrowV38_{side}',[(ex-side*eye_rx*.82,.070,head_d*.510),(ex,.081,head_d*.516),(ex+side*eye_rx*1.04,.067,head_d*.510)],.00172,HAIR)

# Connected shell supplies bridge and tip; tiny cues underneath make it readable front-on.
add_sphere(HEAD,'NoseTipSoftV38',(0,-.041,head_d*.531),(.0098,.0078,.0050),SKIN,20,12)
for side in(-1,1):
 add_sphere(HEAD,f'NoseWingSoftV38_{side}',(side*.0100,-.049,head_d*.526),(.0054,.0048,.0037),SKIN,16,10)
 add_sphere(HEAD,f'NostrilV38_{side}',(side*.0071,-.050,head_d*.531),(.0025,.0017,.0013),FACE_DARK,12,8)
add_strand(HEAD,'NoseUndersideV38',[(-.010,-.049,head_d*.529),(0,-.054,head_d*.532),(.010,-.049,head_d*.529)],.00095,FACE_DARK)

# Wider, clearer mouth line while keeping the lips compact and embedded in the muzzle.
add_strand(HEAD,'UpperLipLeftV38',[(-.030,-.079,head_d*.529),(-.015,-.074,head_d*.532),(0,-.079,head_d*.533)],.00142,LIP)
add_strand(HEAD,'UpperLipRightV38',[(0,-.079,head_d*.533),(.015,-.074,head_d*.532),(.030,-.079,head_d*.529)],.00142,LIP)
add_strand(HEAD,'MouthLineV38',[(-.030,-.083,head_d*.531),(0,-.086,head_d*.533),(.030,-.083,head_d*.531)],.00108,FACE_DARK)
add_strand(HEAD,'LowerLipV38',[(-.024,-.087,head_d*.529),(0,-.092,head_d*.532),(.024,-.087,head_d*.529)],.00115,LIP)
for side in(-1,1):
 add_sphere(HEAD,f'MouthCornerV38_{side}',(side*.030,-.083,head_d*.531),(.0018,.0015,.0011),FACE_DARK,10,6)

"""
s=s[:a]+face+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V38: outward retargeted tilted almond eyes and stronger portrait cues')
