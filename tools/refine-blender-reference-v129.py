from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')
runtime=Path(__file__).resolve().parents[1]/'visual-src'/'blender-heroine.js'
r=runtime.read_text(encoding='utf-8')

gen_done='# REFERENCE_V129' in s
runtime_done='// IRIS_DETAIL_V129' in r
if gen_done and runtime_done:
    print('Blender heroine generator/runtime already carry v12.9 radial iris detail')
    raise SystemExit(0)
if '# REFERENCE_V128' not in s:
    raise SystemExit('REFERENCE_V128 generator required before v12.9')

if not gen_done:
    marker="# REFERENCE_V128: portrait PBR pass adds mobile-safe eye wetline geometry plus skin/sclera/iris/lip specular tuning without changing accepted v12.7 proportions."
    if marker not in s: raise SystemExit('v12.9 REFERENCE_V128 marker anchor missing')
    s=s.replace(marker,marker+"\n# REFERENCE_V129: texture-like radial iris detail uses one tiny indexed mesh per eye, adding warm/dark spokes without image textures or extra draw-call-heavy strand objects.",1)

    # Two closely related iris tones create a fine radial texture that survives downsampling as
    # richer warm-brown variation rather than obvious stripes.
    old="""IRIS_INNER=material('Iris Inner',(0.175,0.105,0.082),.01,.40)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.28)
"""
    new="""IRIS_INNER=material('Iris Inner',(0.175,0.105,0.082),.01,.40)
IRIS_RAY_WARM=material('Iris Ray Warm',(0.205,0.118,0.078),.01,.40)
IRIS_RAY_DARK=material('Iris Ray Dark',(0.105,0.055,0.042),.01,.43)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.28)
"""
    if old not in s: raise SystemExit('v12.9 iris material anchor missing')
    s=s.replace(old,new,1)
    old="""tune_principled(IRIS_INNER,specular=.48,coat=.22,coat_roughness=.20)
tune_principled(PUPIL,specular=.34,coat=.12,coat_roughness=.20)
"""
    new="""tune_principled(IRIS_INNER,specular=.48,coat=.22,coat_roughness=.20)
tune_principled(IRIS_RAY_WARM,specular=.46,coat=.18,coat_roughness=.22)
tune_principled(IRIS_RAY_DARK,specular=.42,coat=.14,coat_roughness=.24)
tune_principled(PUPIL,specular=.34,coat=.12,coat_roughness=.20)
"""
    if old not in s: raise SystemExit('v12.9 iris PBR anchor missing')
    s=s.replace(old,new,1)

    # Insert a compact indexed annulus helper next to the existing ellipse helper. Material index
    # alternates in an irregular 3/5 rhythm, avoiding a mechanical pinwheel read.
    anchor="""def add_smooth_lock(p,name,pts,widths,depths,mat,ring_segments=12,samples=5):
"""
    helper="""def add_iris_rays_v129(p,name,cx,cy,cz,rx,ry,inner_ratio,mats,segments=24):
 verts=[]
 for radius in (inner_ratio,1.0):
  for i in range(segments):
   a=2*math.pi*i/segments
   verts.append(bpos((cx+rx*radius*math.cos(a),cy+ry*radius*math.sin(a),cz)))
 faces=[]
 for i in range(segments):
  j=(i+1)%segments
  faces.append((i,j,segments+j,segments+i))
 mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
 for mat in mats:o.data.materials.append(mat)
 for i,poly in enumerate(o.data.polygons):poly.material_index=0 if (i%5 in (0,2) or i%3==1) else 1
 smooth(o);return parent(o,p)


def add_smooth_lock(p,name,pts,widths,depths,mat,ring_segments=12,samples=5):
"""
    if anchor not in s: raise SystemExit('v12.9 iris helper anchor missing')
    s=s.replace(anchor,helper,1)

    old=""" add_ellipse_surface(HEAD,f'IrisInnerV119_{side}',ex,eye_y-.00005,.10472,.00875*iris_scale,.00670*iris_scale,IRIS_INNER,48)
 add_ellipse_surface(HEAD,f'PupilV119_{side}',ex,eye_y-.00045,.10502,.00305*iris_scale,.00385*iris_scale,PUPIL,36)
"""
    new=""" add_ellipse_surface(HEAD,f'IrisInnerV119_{side}',ex,eye_y-.00005,.10472,.00875*iris_scale,.00670*iris_scale,IRIS_INNER,48)
 add_iris_rays_v129(HEAD,f'IrisRaysV129_{side}',ex,eye_y-.00005,.10484,.00795*iris_scale,.00605*iris_scale,.34,(IRIS_RAY_WARM,IRIS_RAY_DARK),24)
 add_ellipse_surface(HEAD,f'PupilV119_{side}',ex,eye_y-.00045,.10502,.00305*iris_scale,.00385*iris_scale,PUPIL,36)
"""
    if old not in s: raise SystemExit('v12.9 iris geometry anchor missing')
    s=s.replace(old,new,1)

    old="ROOT['character_revision']='v12.8';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
    new="ROOT['character_revision']='v12.9';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';FACE_ASSET['iris_detail_revision']='v12.9-radial';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
    if old not in s: raise SystemExit('v12.9 revision anchor missing')
    s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')

if not runtime_done:
    old="""   }else if(n==='iris'||n==='iris inner'){
    m.metalness=0;m.roughness=.40;m.envMapIntensity=.92;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,n==='iris inner'?.22:.18);m.clearcoatRoughness=.20}
"""
    new="""   }else if(n==='iris'||n==='iris inner'){
    m.metalness=0;m.roughness=.40;m.envMapIntensity=.92;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,n==='iris inner'?.22:.18);m.clearcoatRoughness=.20}
   // IRIS_DETAIL_V129: two radial materials share the accepted v12.8 eye reflectance envelope.
   }else if(n==='iris ray warm'||n==='iris ray dark'){
    m.metalness=0;m.roughness=n==='iris ray warm'?.39:.43;m.envMapIntensity=.90;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,n==='iris ray warm'?.18:.14);m.clearcoatRoughness=.22}
"""
    if old not in r: raise SystemExit('v12.9 runtime iris material anchor missing')
    r=r.replace(old,new,1)
    runtime.write_text(r,encoding='utf-8')

print('Applied REFERENCE_V129: one-mesh-per-eye radial iris detail with warm/dark PBR spokes')
