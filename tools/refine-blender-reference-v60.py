from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V60' in s:
    print('Blender heroine generator already carries REFERENCE_V60')
    raise SystemExit(0)
if '# REFERENCE_V59' not in s:
    raise SystemExit('REFERENCE_V59 generator required before v6.0')

s=s.replace(
    '# REFERENCE_V59: broad swept fringe, full high pony cascade and softer human limb volume.',
    '# REFERENCE_V59: broad swept fringe, full high pony cascade and softer human limb volume.\n# REFERENCE_V60: stable UV portrait head, continuous facial planes and restrained adult profile.',
    1,
)

helper=r'''
def add_anime_head_v60(p,name,mat,segments=96,rings=48):
 # Smooth UV topology replaces row-profile rings that produced horizontal shading bands.
 verts=[]
 top=bpos((0,.179,0));bottom=bpos((0,-.151,0));verts.append(top)
 for r in range(1,rings):
  theta=math.pi*r/rings
  sy=math.cos(theta);rad=math.sin(theta)
  yy=.014+.165*sy
  # Adult/anime silhouette: broad cranium, tapered lower cheek and compact chin.
  lower=max(0.0,min(1.0,(-.030-yy)/.120))
  cheek=math.exp(-((yy+.010)/.060)**2)
  width=.132*(1.0-.205*lower+.025*cheek)
  for i in range(segments):
   phi=2*math.pi*i/segments
   cp=math.cos(phi);sp=math.sin(phi)
   x=width*rad*cp
   depth=(.103 if sp<0 else .0975)*rad
   z=depth*sp
   if sp>0:
    fm=sp**2.0
    # Recess the eye sockets while supporting the zygomatic plane.
    for side in (-1,1):
     ex=side*.0415
     z-=fm*.0042*math.exp(-((x-ex)/.026)**2-((yy-.033)/.022)**2)
     z+=fm*.0034*math.exp(-((x-side*.054)/.035)**2-((yy+.004)/.040)**2)
    # Restrained central profile: bridge, small tip, philtrum break and chin support.
    z+=fm*.0038*math.exp(-(x/.019)**2-((yy+.002)/.052)**2)
    z+=fm*.0080*math.exp(-(x/.017)**2-((yy+.043)/.017)**2)
    z-=fm*.0025*math.exp(-(x/.018)**2-((yy+.061)/.012)**2)
    z+=fm*.0018*math.exp(-(x/.038)**2-((yy+.081)/.015)**2)
    z+=fm*.0028*math.exp(-(x/.034)**2-((yy+.118)/.020)**2)
   verts.append(bpos((x,yy,z)))
 bottom_idx=len(verts);verts.append(bottom)
 faces=[]
 first=1
 for i in range(segments):faces.append((0,first+i,first+(i+1)%segments))
 for r in range(rings-2):
  a=1+r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 last=1+(rings-2)*segments
 for i in range(segments):faces.append((last+i,bottom_idx,last+(i+1)%segments))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 return parent(o,p)
'''
if 'def add_anime_head_v60(' not in s:
    s=s.replace("ROOT=empty('BLENDER_HEROINE')",helper+"\nROOT=empty('BLENDER_HEROINE')",1)

a=s.index('# === HEAD / FACE ===')
b=s.index('# Hair v5.9:',a)
face=r'''# === HEAD / FACE ===
# v6.0 uses one dense UV surface. Facial depth is deliberately restrained to avoid the v5.x muzzle/nose blowout.
add_anime_head_v60(HEAD,'HeadShellV60',SKIN,96,48)
add_cylinder(HEAD,'Neck',(0,-.158,-.008),W('neck')*.33,.084,SKIN,26)
add_cylinder(HEAD,'Choker',(0,-.139,-.006),W('neck')*.46,.034,BLACK,28)
add_cylinder(HEAD,'ChokerTrim',(0,-.124,-.006),W('neck')*.47,.009,SILVER,28)
for side in(-1,1):add_sphere(HEAD,f'EarV60_{side}',(side*.126,-.018,-.012),(.009,.021,.008),SKIN,20,12)

# Large but adult almond eyes seated directly on the smooth shell.
face_front=.0964
eye_y=.0330
eye_x=.0415
eye_rx=.0368
eye_ry=.0168
eye_tilt=.0030
for side in(-1,1):
 ex=side*eye_x
 add_sphere(HEAD,f'EyeballHiddenV60_{side}',(ex,eye_y,.0835),(.0205,.0160,.0122),SCLERA,46,28)
 add_almond_surface(HEAD,f'EyeOpeningV60_{side}',ex,eye_y,face_front,eye_rx,eye_ry,.00115,SCLERA,64,side,eye_tilt)
 add_ellipse_surface(HEAD,f'IrisV60_{side}',ex,eye_y,face_front+.0014,.0184,.0122,IRIS,48)
 add_ellipse_surface(HEAD,f'IrisInnerV60_{side}',ex,eye_y-.0002,face_front+.0020,.0116,.0077,IRIS_INNER,42)
 add_ellipse_surface(HEAD,f'PupilV60_{side}',ex,eye_y-.0002,face_front+.0026,.0044,.0049,PUPIL,32)
 add_ellipse_surface(HEAD,f'EyeLightV60_{side}',ex-side*.0052,eye_y+.0052,face_front+.0032,.0016,.0014,SCLERA,18)
 inner=ex-side*eye_rx*.94;outer=ex+side*eye_rx*1.02
 add_strand(HEAD,f'UpperLashV60_{side}',[(inner,eye_y-eye_tilt+.0012,face_front+.0025),(ex,eye_y+.0173,face_front+.0030),(outer,eye_y+eye_tilt+.0011,face_front+.0026)],.00042,HAIR)
 add_strand(HEAD,f'LowerLidV60_{side}',[(inner+side*.004,eye_y-eye_tilt-.0003,face_front+.0018),(ex,eye_y-.0102,face_front+.0021),(outer-side*.004,eye_y+eye_tilt-.0003,face_front+.0018)],.00012,FACE_DARK)
 add_strand(HEAD,f'BrowV60_{side}',[(ex-side*.027,.067,.101),(ex,.075,.103),(ex+side*.032,.064,.1015)],.00052,HAIR)

# Only tiny surface accents are separate; the head mesh owns the actual nose/chin profile.
for side in(-1,1):add_sphere(HEAD,f'NostrilV60_{side}',(side*.0042,-.0535,.1055),(.00042,.00030,.00026),FACE_DARK,10,7)
add_almond_surface(HEAD,'UpperLipV60',0,-.0770,.1012,.0265,.0038,.00075,LIP,54,1,0.0)
add_almond_surface(HEAD,'LowerLipV60',0,-.0840,.1018,.0255,.0042,.00085,LIP,54,1,0.0)
add_strand(HEAD,'MouthSeamV60',[(-.0225,-.0805,.1024),(0,-.0812,.1028),(.0225,-.0805,.1024)],.00011,FACE_DARK)

'''
s=s[:a]+face+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V60: stable UV portrait head with restrained adult profile')
