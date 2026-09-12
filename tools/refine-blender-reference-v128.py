from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')
runtime=Path(__file__).resolve().parents[1]/'visual-src'/'blender-heroine.js'
r=runtime.read_text(encoding='utf-8')

gen_done='# REFERENCE_V128' in s
runtime_done='// PORTRAIT_MATERIAL_V128' in r
if gen_done and runtime_done:
    print('Blender heroine generator/runtime already carry v12.8 portrait material pass')
    raise SystemExit(0)
if '# REFERENCE_V127' not in s:
    raise SystemExit('REFERENCE_V127 generator required before v12.8')

if not gen_done:
    marker="# REFERENCE_V127: profile-balance pass reduces excessive nasal projection and restores a cleaner nose-lip-chin S-curve while preserving the accepted v12.6 frontal mask."
    if marker not in s:
        raise SystemExit('v12.8 REFERENCE_V127 marker anchor missing')
    s=s.replace(marker,marker+"\n# REFERENCE_V128: portrait PBR pass adds mobile-safe eye wetline geometry plus skin/sclera/iris/lip specular tuning without changing accepted v12.7 proportions.",1)

    # Add a version-tolerant Principled tuning helper. Ubuntu Blender versions expose either the
    # legacy Clearcoat/Specular names or Blender 4.x Coat/Specular IOR names.
    anchor="def material(name,color,metallic=0.0,roughness=.45):\n m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metallic;b.inputs['Roughness'].default_value=roughness;return m\n"
    helper="""def material(name,color,metallic=0.0,roughness=.45):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metallic;b.inputs['Roughness'].default_value=roughness;return m

def tune_principled(mat,specular=None,coat=None,coat_roughness=None):
 b=mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
 if not b:return mat
 def set_any(names,value):
  if value is None:return
  for name in names:
   inp=b.inputs.get(name)
   if inp is not None:
    inp.default_value=value
    return
 set_any(('Specular IOR Level','Specular'),specular)
 set_any(('Coat Weight','Clearcoat'),coat)
 set_any(('Coat Roughness','Clearcoat Roughness'),coat_roughness)
 return mat
"""
    if anchor not in s:
        raise SystemExit('v12.8 material helper anchor missing')
    s=s.replace(anchor,helper,1)

    old="""SCLERA=material('Sclera',(0.60,0.575,0.555),0,.66)
IRIS=material('Iris',(0.052,0.032,0.030),.01,.56)
IRIS_INNER=material('Iris Inner',(0.175,0.105,0.082),.01,.58)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.30)
LIP=material('Lip',(0.285,0.105,0.125),0,.67)
FACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)
EAR_SHADOW=material('Ear Inner',(0.255,0.145,0.135),0,.78)
GLOW=material('Cyan Accent',(0.20,0.56,0.61),.38,.18)
"""
    new="""SCLERA=material('Sclera',(0.60,0.575,0.555),0,.42)
IRIS=material('Iris',(0.052,0.032,0.030),.01,.42)
IRIS_INNER=material('Iris Inner',(0.175,0.105,0.082),.01,.40)
PUPIL=material('Pupil',(0.004,0.005,0.006),0,.28)
LIP=material('Lip',(0.285,0.105,0.125),0,.42)
FACE_DARK=material('Face Detail',(0.20,0.075,0.070),0,.68)
EYE_WET=material('Eye Wetline',(0.34,0.155,0.145),0,.24)
EAR_SHADOW=material('Ear Inner',(0.255,0.145,0.135),0,.78)
GLOW=material('Cyan Accent',(0.20,0.56,0.61),.38,.18)
tune_principled(SKIN,specular=.32,coat=.035,coat_roughness=.70)
tune_principled(SCLERA,specular=.52,coat=.32,coat_roughness=.18)
tune_principled(IRIS,specular=.46,coat=.18,coat_roughness=.22)
tune_principled(IRIS_INNER,specular=.48,coat=.22,coat_roughness=.20)
tune_principled(PUPIL,specular=.34,coat=.12,coat_roughness=.20)
tune_principled(LIP,specular=.44,coat=.30,coat_roughness=.24)
tune_principled(EYE_WET,specular=.58,coat=.52,coat_roughness=.12)
"""
    if old not in s:
        raise SystemExit('v12.8 portrait material anchor missing')
    s=s.replace(old,new,1)

    # Add a thin glossy lower wetline and tiny inner-canthus cue. These are opaque micro-surfaces,
    # avoiding mobile transparency sorting while still catching a moving specular highlight.
    anchor=" add_strand(HEAD,f'UpperLidFoldV119_{side}',[(inner+side*.0050,eye_y-eye_tilt+.0038,.10340),(ex,eye_y+.0153,.10375),(outer-side*.0060,eye_y+eye_tilt+.0036,.10342)],.00017,FACE_DARK)\n # Lower, fuller brows match the key-art expression and visually reduce the oversized forehead.\n"
    insert=""" add_strand(HEAD,f'UpperLidFoldV119_{side}',[(inner+side*.0050,eye_y-eye_tilt+.0038,.10340),(ex,eye_y+.0153,.10375),(outer-side*.0060,eye_y+eye_tilt+.0036,.10342)],.00017,FACE_DARK)
 # v12.8 glossy waterline follows only the inner two-thirds of the lower lid so it reads as moisture, not eyeliner.
 add_strand(HEAD,f'EyeWetlineV128_{side}',[(inner+side*.0050,eye_y-eye_tilt-.00005,.10404),(ex,eye_y-.00785,.10412),(outer-side*.0100,eye_y+eye_tilt-.00005,.10403)],.00011,EYE_WET)
 add_ellipse_surface(HEAD,f'InnerCanthusV128_{side}',inner+side*.0014,eye_y-eye_tilt+.00025,.10408,.00135,.00058,EYE_WET,18)
 # Lower, fuller brows match the key-art expression and visually reduce the oversized forehead.
"""
    if anchor not in s:
        raise SystemExit('v12.8 eyelid anchor missing')
    s=s.replace(anchor,insert,1)

    old="ROOT['character_revision']='v12.7';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
    new="ROOT['character_revision']='v12.8';ROOT['assembly_workflow']='body-head-hair';BODY_ASSET['scale_reference']=True;BODY_ASSET['tps_silhouette_review']=True;HEAD_ASSET['profile_review']=True;HEAD_ASSET['facial_depth_review']=True;HEAD_ASSET['compact_face_review']=True;HEAD_ASSET['balanced_profile_review']=True;HAIR_ASSET['scalp_fit_review']=True;HAIR_ASSET['hero_silhouette_review']=True;FACE_ASSET['expression_ready']=True;FACE_ASSET['blink_system']='morph-eyelids';FACE_ASSET['mobile_gaze_review']=True;FACE_ASSET['portrait_material_revision']='v12.8-pbr';EYE_L['expression_pivot']='left-eye';EYE_R['expression_pivot']='right-eye';MOUTH_ASSET['expression_pivot']='mouth'"
    if old not in s:
        raise SystemExit('v12.8 revision anchor missing')
    s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')

if not runtime_done:
    anchor="const REF_HIP_HALF=.151;\n\nfunction referenceRetarget(d,base){"
    helper="""const REF_HIP_HALF=.151;

// PORTRAIT_MATERIAL_V128: keep the exported PBR intent stable in Three.js/iPhone Safari.
function tunePortraitMaterials(root){
 const seen=new Set();
 root.traverse(o=>{
  if(!o.isMesh)return;
  const mats=Array.isArray(o.material)?o.material:[o.material];
  for(const m of mats){
   if(!m||seen.has(m))continue;seen.add(m);
   const n=(m.name||'').toLowerCase();
   if(n==='skin'){
    m.metalness=0;m.roughness=.62;m.envMapIntensity=.72;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.035);m.clearcoatRoughness=.70}
   }else if(n==='sclera'){
    m.metalness=0;m.roughness=.36;m.envMapIntensity=1.05;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.32);m.clearcoatRoughness=.18}
   }else if(n==='iris'||n==='iris inner'){
    m.metalness=0;m.roughness=.40;m.envMapIntensity=.92;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,n==='iris inner'?.22:.18);m.clearcoatRoughness=.20}
   }else if(n==='pupil'){
    m.metalness=0;m.roughness=.26;m.envMapIntensity=.70;
   }else if(n==='lip'){
    m.metalness=0;m.roughness=.40;m.envMapIntensity=.88;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.30);m.clearcoatRoughness=.24}
   }else if(n==='eye wetline'){
    m.metalness=0;m.roughness=.20;m.envMapIntensity=1.18;
    if(m.isMeshPhysicalMaterial){m.clearcoat=Math.max(m.clearcoat||0,.52);m.clearcoatRoughness=.12}
   }
   m.needsUpdate=true;
  }
 });
}

function referenceRetarget(d,base){"""
    if anchor not in r:
        raise SystemExit('v12.8 runtime material anchor missing')
    r=r.replace(anchor,helper,1)
    old="this.model=gltf.scene;this.model.name='blender-heroine-model';this.model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false}});this.root.add(this.model);"
    new="this.model=gltf.scene;this.model.name='blender-heroine-model';this.model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false}});tunePortraitMaterials(this.model);this.root.add(this.model);"
    if old not in r:
        raise SystemExit('v12.8 runtime load anchor missing')
    r=r.replace(old,new,1)
    runtime.write_text(r,encoding='utf-8')

print('Applied REFERENCE_V128: portrait PBR material tuning and mobile-safe eye wetline detail')
