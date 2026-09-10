from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V113' in s:
    print('Blender heroine generator already carries REFERENCE_V113')
    raise SystemExit(0)
if '# REFERENCE_V112' not in s:
    raise SystemExit('REFERENCE_V112 generator required before v11.3')

marker='# REFERENCE_V112: public-model study reset; one independently generated continuous adult-anime head shell replaces HeadShellV60 plus the CC0 overlay patch.'
if marker not in s:
    raise SystemExit('v11.3 REFERENCE_V112 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V113: the new single shell gains an explicit adult S-profile and seated orbital surfaces after five-view validation exposed the v11.2 flat side silhouette.',1)

start=s.find('def add_reference_head_v112(')
end=s.find("ROOT=empty('BLENDER_HEROINE')",start)
if start<0 or end<0:
    raise SystemExit('v11.3 v11.2 head builder block missing')

builder=r'''def add_reference_head_v113(p,name,mat,segments=112):
 # Clean single-shell rebuild, informed by public CC0 basemesh practice but authored independently.
 # A profile cage supplies the adult forehead/nose/lips/chin rhythm, while lateral falloff preserves
 # full three-dimensional cheeks instead of creating a centre-line ridge.
 sections=[
  (.164,.071,.078,.080,-.010),(.150,.101,.084,.086,-.008),(.132,.119,.089,.091,-.006),
  (.108,.128,.094,.095,-.003),(.082,.131,.098,.097,-.001),(.058,.129,.100,.098,.001),
  (.036,.125,.101,.099,.002),(.014,.128,.102,.099,.003),(-.008,.127,.102,.100,.003),
  (-.030,.123,.102,.101,.002),(-.052,.118,.101,.102,.001),(-.072,.110,.100,.103,.000),
  (-.089,.102,.098,.103,-.001),(-.103,.094,.096,.102,-.003),(-.115,.085,.094,.101,-.004),
  (-.126,.075,.091,.098,-.006),(-.135,.062,.087,.093,-.008),(-.141,.047,.081,.086,-.009),
  (-.145,.030,.072,.078,-.010)
 ]
 profile=[
  (.090,.0970),(.060,.0985),(.035,.1010),(.015,.1040),(-.005,.1080),(-.025,.1145),
  (-.044,.1265),(-.055,.1180),(-.066,.1040),(-.076,.1085),(-.086,.1113),(-.095,.1110),
  (-.105,.0990),(-.118,.1050),(-.128,.1020),(-.137,.0940),(-.145,.0820)
 ]
 def sample_profile(y):
  if y>=profile[0][0]:return profile[0][1]
  if y<=profile[-1][0]:return profile[-1][1]
  for j in range(len(profile)-1):
   y0,z0=profile[j];y1,z1=profile[j+1]
   if y0>=y>=y1:
    t=(y0-y)/(y0-y1)
    t=t*t*(3.0-2.0*t)
    return z0+(z1-z0)*t
  return .100

 verts=[]
 for yy,w,back,front,zoff in sections:
  pz=sample_profile(yy)
  for i in range(segments):
   phi=2*math.pi*i/segments
   cp=math.cos(phi);sp=math.sin(phi)
   x=cp*w
   depth=front if sp>=0 else back
   z=zoff+sp*depth
   if sp>0:
    fm=sp**1.48
    # Broad facial plane: keep the eye/cheek zone forward enough to meet the feature surfaces.
    face_band=math.exp(-((yy+.018)/.125)**4)
    face_lat=1.0/(1.0+(abs(x)/.096)**6)
    neutral=.1005 + .0012*math.exp(-((yy+.008)/.070)**2)
    z+=fm*face_band*face_lat*(neutral-z)*.78

    # Explicit centre profile. A .034 lateral half-width gives the nose a readable side silhouette,
    # while the sixth-power falloff prevents the old mask/plate look in the cheeks.
    profile_lat=1.0/(1.0+(abs(x)/.034)**6)
    profile_band=math.exp(-((yy+.032)/.148)**6)
    z+=fm*profile_lat*profile_band*(pz-z)*.96

    for side in (-1,1):
     ex=side*.0465
     # Eye socket is shallow enough that the existing almond eye can sit inside it rather than hover.
     z-=fm*.0017*math.exp(-((x-ex)/.0265)**2-((yy-.033)/.0190)**2)
     # Brow/zygomatic bridge and adult cheek break.
     z+=fm*.0022*math.exp(-((x-ex)/.031)**2-((yy-.061)/.022)**2)
     z+=fm*.0048*math.exp(-((x-side*.057)/.033)**2-((yy+.004)/.035)**2)
     z-=fm*.0021*math.exp(-((x-side*.068)/.029)**2-((yy+.053)/.034)**2)
     z-=fm*.0016*math.exp(-((x-side*.087)/.025)**2-((yy-.040)/.041)**2)
     # Alar wing / nasolabial transition remains part of the shell.
     z+=fm*.0028*math.exp(-((x-side*.0105)/.0110)**2-((yy+.055)/.0135)**2)
     z-=fm*.0012*math.exp(-((x-side*.018)/.014)**2-((yy+.071)/.017)**2)
     # Jaw angle turns inward before the chin, preventing a boxy lower-face slab.
     z-=fm*.0022*math.exp(-((x-side*.065)/.029)**2-((yy+.108)/.027)**2)

    # Muzzle and chin are broad supports; the profile cage supplies the actual centre projection.
    z+=fm*.0044*math.exp(-(x/.052)**2-((yy+.086)/.023)**2)
    z+=fm*.0060*math.exp(-(x/.038)**2-((yy+.119)/.019)**2)
   verts.append(bpos((x,yy,z)))

 top_idx=len(verts);verts.append(bpos((0,.176,-.006)))
 bottom_idx=len(verts);verts.append(bpos((0,-.147,-.011)))
 faces=[];rows=len(sections)
 for r in range(rows-1):
  a=r*segments;b=a+segments
  for i in range(segments):
   j=(i+1)%segments;faces.append((a+i,a+j,b+j,b+i))
 for i in range(segments):
  j=(i+1)%segments;faces.append((top_idx,j,i))
  a=(rows-1)*segments;faces.append((bottom_idx,a+i,a+j))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);smooth(o)
 mod=o.modifiers.new('reference_head_subdivision','SUBSURF');mod.levels=1;mod.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return parent(o,p)

'''
s=s[:start]+builder+s[end:]
s=s.replace("add_reference_head_v112(HEAD,'HeadShellV112',SKIN,112)","add_reference_head_v113(HEAD,'HeadShellV113',SKIN,112)",1)

# Seat the portrait eye surfaces against the rebuilt orbital plane. Keep adult v10.0 aperture/spacing.
s=s.replace("add_almond_surface(HEAD,f'EyeScleraV100_{side}',ex,eye_y,.1030,.0288,.0097,.00115,SCLERA,72,side,eye_tilt*.70)","add_almond_surface(HEAD,f'EyeScleraV113_{side}',ex,eye_y,.1017,.0288,.0097,.00105,SCLERA,72,side,eye_tilt*.70)",1)
s=s.replace("add_ellipse_surface(HEAD,f'IrisV100_{side}',ex,eye_y,.10430,.0094,.0078,IRIS_INNER,40)","add_ellipse_surface(HEAD,f'IrisV113_{side}',ex,eye_y,.10270,.0094,.0078,IRIS_INNER,40)",1)
s=s.replace("add_ellipse_surface(HEAD,f'PupilV100_{side}',ex,eye_y-.00015,.10466,.00285,.00345,PUPIL,30)","add_ellipse_surface(HEAD,f'PupilV113_{side}',ex,eye_y-.00015,.10302,.00285,.00345,PUPIL,30)",1)
s=s.replace("add_ellipse_surface(HEAD,f'EyeLightV100_{side}',ex-side*.0030,eye_y+.0028,.10488,.00090,.00072,SCLERA,16)","add_ellipse_surface(HEAD,f'EyeLightV113_{side}',ex-side*.0030,eye_y+.0028,.10318,.00090,.00072,SCLERA,16)",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V113: strong adult side profile and seated eyes on the clean single-shell rebuild')
