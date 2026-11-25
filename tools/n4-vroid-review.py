import bpy,sys,math,json
from mathutils import Vector
from pathlib import Path
src,out=map(Path,sys.argv[sys.argv.index('--')+1:]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(src))
bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert meshes and arms
def bb(objects):
    ps=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in ps) for i in range(3)));hi=Vector(tuple(max(p[i] for p in ps) for i in range(3)))
    return lo,hi
lo,hi=bb(meshes);h=hi.z-lo.z
face=[o for o in meshes if 'face' in o.name.lower()]
# VRM 0 humanoid faces -Z in glTF (+Y after Blender import).
if face:
    fl,fh=bb(face);c=(fl+fh)/2
    c.z=max(c.z,lo.z+h*.83)
    extent=max((fh.z-fl.z)*1.35,h*.27)
else:c=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z+h*.89));extent=h*.32
for o in meshes:
    for p in o.data.polygons:p.use_smooth=True
# Keep all original skin weights and facial morphs; candidate is a palette change, not a fitted N4 face.
report={'source':src.name,'blender':bpy.app.version_string,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'armatures':len(arms),'bones':[len(a.data.bones) for a in arms],'shape_keys':{o.name:[k.name for k in o.data.shape_keys.key_blocks] for o in meshes if o.data.shape_keys},'face_objects':[o.name for o in face],'bounds':[list(lo),list(hi)]}
(out/'audit.json').write_text(json.dumps(report,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'editable.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'game.glb'),export_format='GLB',export_apply=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.world.color=(.15,.15,.15);scene.view_settings.view_transform='Standard'
scene.render.image_settings.file_format='PNG'
cam=bpy.data.objects.new('Review',bpy.data.cameras.new('Review'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO'
def aim(o,t):o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
lights=[]
for name in ['Key','Fill','Rim']:
    ob=bpy.data.objects.new(name,bpy.data.lights.new(name,'AREA'));scene.collection.objects.link(ob);lights.append(ob)
for name,angle,full in [('front',0,False),('quarter',45,False),('profile',90,False),('opposite',180,False),('body',0,True)]:
    t=(lo+hi)/2 if full else c
    e=h*1.15 if full else extent
    a=math.radians(angle);cam.location=t+Vector((math.sin(a)*e*3,math.cos(a)*e*3,e*.02));cam.data.ortho_scale=e;aim(cam,t)
    for ob,offset,power in zip(lights,[(-1,1.5,1.2),(1.2,1.4,.4),(.4,-1.2,1.0)],[90,50,85]):
        ob.location=t+Vector(offset)*e;ob.data.energy=power*e*e;ob.data.size=e*1.5;aim(ob,t)
    scene.render.resolution_x=800;scene.render.resolution_y=1200 if full else 800;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('N4_VROID_AUDIT',json.dumps(report))
