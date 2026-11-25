"""N4 anime lab: separate, non-deploying Blender candidate from accepted v18.5 r2.
Donor head David Onizaki (CC BY); hair Dawn to Dusk Games Anime Female Adventurer v1.2 (CC0 per upstream project).
No N4 photo is uploaded; geometry is an initial design interpretation, not a measured fit.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
from array import array

out=Path(sys.argv[sys.argv.index('--')+1]); out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(Path('dist/assets/models/heroine-blender.glb').resolve()))
head=bpy.data.objects.get('HeadShellV140')
hair=bpy.data.objects.get('HairPremiumV185_Adventurer')
assert head and hair, 'accepted base not found'
def under(o,n):
    while o:
        if o.name==n: return True
        o=o.parent
    return False
def points(o): return [o.matrix_world @ v.co for v in o.data.vertices]
def bounds(ps):
    lo=Vector(tuple(min(p[i] for p in ps) for i in range(3)))
    hi=Vector(tuple(max(p[i] for p in ps) for i in range(3)))
    return lo,hi,(lo+hi)/2,hi-lo
lo,hi,c,s=bounds(points(head))
iris=[o for o in bpy.data.objects if o.type=='MESH' and 'irisouter' in o.name.lower()]
sign=-1 if not iris or sum(bounds(points(o))[2].y for o in iris)/len(iris)<c.y else 1
headobjs=[o for o in bpy.data.objects if o.type=='MESH' and under(o,'BL_HEAD') and not under(o,'BL_HAIR_ASSET') and not o.name.startswith('HairPremium')]
def warp(p):
    h=max(0,min(1,(p.z-lo.z)/s.z))
    # restrained oval jaw, compact chin, preserve eye and mouth placement
    w=math.exp(-((h-.22)/.22)**2)
    p.x=c.x+(p.x-c.x)*(1-.045*w)
    return p
for o in headobjs:
    if o.data.users>1:o.data=o.data.copy()
    inv=o.matrix_world.inverted()
    for v in o.data.vertices: v.co=inv@warp(o.matrix_world@v.co)
    o.data.update()
# preserve texture variation rather than replacing authored hair with flat color
hairobjs=[o for o in bpy.data.objects if o.type=='MESH' and (under(o,'BL_HAIR_ASSET') or o.name.startswith('HairPremium'))]
seen=set(); recolored={}
for o in hairobjs:
    for m in o.data.materials:
        if not m or m.name in seen:continue
        seen.add(m.name)
        if not m.use_nodes:continue
        b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if not b:continue
        bc=b.inputs['Base Color']
        if bc.is_linked:
            source=bc.links[0].from_node
            if source.type=='TEX_IMAGE' and source.image:
                im=source.image
                if im.name not in recolored:
                    cp=im.copy(); cp.name='N4_espresso_'+im.name
                    px=array('f',[0.0])*len(im.pixels); im.pixels.foreach_get(px)
                    for k in range(0,len(px),4):
                        l=max(0,min(1,.2126*px[k]+.7152*px[k+1]+.0722*px[k+2]))
                        # espresso with chestnut glints, retain alpha
                        px[k]=min(1,.040+.46*l);px[k+1]=min(1,.023+.29*l);px[k+2]=min(1,.018+.23*l)
                    cp.pixels.foreach_set(px);cp.update();cp.pack();recolored[im.name]=cp
                source.image=recolored[im.name]
        else:bc.default_value=(.055,.031,.025,1)
        b.inputs['Roughness'].default_value=.42
# lengthen lower hair gently without affecting crown and bangs
for o in [hair]:
    if o.data.users>1:o.data=o.data.copy()
    inv=o.matrix_world.inverted()
    for v in o.data.vertices:
        p=o.matrix_world@v.co
        f=max(0,min(1,(c.z-.20*s.z-p.z)/(s.z*1.15)))
        p.z-=s.z*.55*f*f
        v.co=inv@p
    o.data.update()
# remove held weapon for character asset; retain hierarchy and other original materials
removed=[]
for o in list(bpy.data.objects):
    if o.type=='MESH' and (under(o,'BL_SWORD') or under(o,'BL_WEAPON')):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
    if o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True
root=bpy.data.objects.get('BLENDER_HEROINE')
if root:
    root['candidate']='N4 anime donor lab C';root['source']='Parry Doll v18.5 r2 / David Onizaki CC BY / Dawn to Dusk Games CC0'

# Original game GLB uses unplaced body modules; reconstruct runtime REST in Blender coordinates.
from mathutils import Matrix
def v(x,y,z):return Vector((x,-z,y))
P={'pelvis':v(0,1.38,0),'neck':v(0,2.09,0),'head':v(0,2.29,0),'chest':v(0,1.94,0)}
for side,k in [('L',-1),('R',1)]:
    for name,xyz in [('shoulder',(k*.172,1.95,0)),('elbow',(k*.34,1.50,.025)),('hand',(k*.46,1.03,.035)),('hip',(k*.151,1.384,0)),('knee',(k*.18,.76,.04)),('foot',(k*.20,.16,.12))]:P[name+side]=v(*xyz)
F=v(0,0,1)
groups={}
def place(name,center,axis,stretch=1.0):
    z=axis.normalized();x=z.cross(F).normalized();y=z.cross(x).normalized()
    o=bpy.data.objects.get(name);assert o,name
    o.matrix_world=Matrix(((x.x,y.x,z.x*stretch,center.x),(x.y,y.y,z.y*stretch,center.y),(x.z,y.z,z.z*stretch,center.z),(0,0,0,1)))
    groups[name]=o
up=P['neck']-P['pelvis']
place('BL_PELVIS',P['pelvis'],up);place('BL_TORSO',(P['pelvis']+P['neck'])/2,up);place('BL_HEAD',P['head'],up)
for side in ['L','R']:
    for g,a,b in [('UPPER_ARM','shoulder','elbow'),('FOREARM','elbow','hand'),('THIGH','hip','knee'),('SHIN','knee','foot')]:
        aa,bb=P[a+side],P[b+side];place('BL_'+g+'_'+side,(aa+bb)/2,bb-aa,(bb-aa).length)
    place('BL_HAND_'+side,P['hand'+side],P['hand'+side]-P['elbow'+side])
    place('BL_FOOT_'+side,P['foot'+side],up)
bpy.context.view_layer.update()
# Preserve world positions while building standard glTF skin, with rigid initial weights.
spec={'BL_PELVIS':(P['pelvis'],P['pelvis']+v(0,.15,0),None),'BL_TORSO':(P['pelvis'],P['neck'],'BL_PELVIS'),'BL_HEAD':(P['neck'],P['head']+v(0,.12,0),'BL_TORSO')}
for side in ['L','R']:
    for g,a,b,parent in [('UPPER_ARM','shoulder','elbow','BL_TORSO'),('FOREARM','elbow','hand','BL_UPPER_ARM_'+side),('THIGH','hip','knee','BL_PELVIS'),('SHIN','knee','foot','BL_THIGH_'+side)]:
        spec['BL_'+g+'_'+side]=(P[a+side],P[b+side],parent)
    spec['BL_HAND_'+side]=(P['hand'+side],P['hand'+side]+(P['hand'+side]-P['elbow'+side]).normalized()*.15,'BL_FOREARM_'+side)
    spec['BL_FOOT_'+side]=(P['foot'+side],P['foot'+side]+v(0,0,.18),'BL_SHIN_'+side)
arm=bpy.data.armatures.new('N4 Skeleton');rig=bpy.data.objects.new('N4 Skeleton',arm);bpy.context.collection.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for name,(a,b,parent) in spec.items():
    eb=arm.edit_bones.new(name);eb.head=a;eb.tail=b
    if parent:eb.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
for o in list(bpy.data.objects):
    if o.type!='MESH':continue
    anc=o
    while anc and anc.name not in groups:anc=anc.parent
    if not anc:continue
    name=anc.name;mw=o.matrix_world.copy()
    if o.data.users>1:o.data=o.data.copy()
    o.data.transform(mw,shape_keys=True);o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
    for vg in list(o.vertex_groups):o.vertex_groups.remove(vg)
    vg=o.vertex_groups.new(name=name);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
    mod=o.modifiers.new('N4 initial skin','ARMATURE');mod.object=rig
bpy.context.view_layer.update()
lo,hi,c,s=bounds(points(head))
# Slightly warmer and lighter skin on body/neck to better match donor face.
skin=bpy.data.materials.get('Skin')
if skin and skin.use_nodes:
    bs=next((n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bs and not bs.inputs['Base Color'].is_linked:bs.inputs['Base Color'].default_value=(.63,.40,.33,1)


# N4 C: replace the blue donor ponytail with layered, individually shaped long locks.
# At this point meshes are in world space and attached to the rest-pose armature.
import bmesh
from mathutils import Vector
old_hair_names={q.name for q in hairobjs}
for o in list(bpy.data.objects):
    if o.type=='MESH' and (o.name.startswith('HairPremium') or o.name in old_hair_names):
        bpy.data.objects.remove(o,do_unlink=True)
def mat(name,color,rough=.47):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
    b.inputs['Specular IOR Level'].default_value=.27
    return m
palette=[mat('N4 Espresso root',(.035,.018,.014)),mat('N4 Chestnut mass',(.065,.034,.026)),mat('N4 Warm brown ribbon',(.095,.052,.038)),mat('N4 Soft brown sheen',(.13,.076,.054)),mat('N4 Deep overlap',(.022,.011,.009))]
def bind_mesh(name,verts,faces,inds):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    for m in palette:me.materials.append(m)
    for p,i in zip(me.polygons,inds):p.material_index=i;p.use_smooth=True
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o.parent=rig;vg=o.vertex_groups.new(name='BL_HEAD');vg.add(list(range(len(me.vertices))),1,'REPLACE')
    mod=o.modifiers.new('Hair head binding','ARMATURE');mod.object=rig
    return o
# Copy scalp geometry with a wider cap reaching sideburns and nape, avoiding visible skin holes.
vs=[];fs=[];lookup={}
for poly in head.data.polygons:
    pp=[head.matrix_world@head.data.vertices[i].co for i in poly.vertices]
    p=sum(pp,Vector())/len(pp)
    h=(p.z-lo.z)/s.z;front=(p.y-c.y)*sign
    if h<(.69 if front>.025 else .36):continue
    f=[]
    for i,wp in zip(poly.vertices,pp):
        if i not in lookup:
            d=wp-c;d.x*=1.055;d.y*=1.065;d.z*=1.045;lookup[i]=len(vs);vs.append(c+d)
        f.append(lookup[i])
    fs.append(f)
bind_mesh('N4 sculpted scalp',vs,fs,[0]*len(fs))
# coordinates normalized to head width and height; front-positive coordinate converted to Blender
def pt(x,z,f):return c+Vector((x*s.x,sign*f*s.y,z*s.z))
def cat(a,b,d,e,t):
    return .5*((2*b)+(-a+d)*t+(2*a-5*b+4*d-e)*t*t+(-a+3*b-3*d+e)*t*t*t)
def lock(name,controls,width,depth,col=1):
    P=[pt(*p) for p in controls];vs=[];fs=[];mi=[];steps=42;sides=14
    for i in range(steps+1):
        u=i/steps*(len(P)-1);j=min(len(P)-2,int(u));t=u-j
        a,b,d,e=P[max(0,j-1)],P[j],P[j+1],P[min(len(P)-1,j+2)]
        q=cat(a,b,d,e,t);q0=cat(a,b,d,e,max(0,t-.006));q1=cat(a,b,d,e,min(1,t+.006));tangent=(q1-q0).normalized()
        if tangent.length<.01:tangent=Vector((0,0,-1))
        radial=Vector((q.x-c.x,q.y-c.y,0)).normalized()
        if radial.length<.01:radial=Vector((0,sign,0))
        side=tangent.cross(radial).normalized()
        if side.length<.01:side=Vector((1,0,0))
        normal=side.cross(tangent).normalized()
        f=i/steps;w=width*s.x*(.28+.72*math.sin(math.pi*min(.999,f*.96+.04))**.55)*(1-f**7)+.00045
        dpth=depth*s.x*(.4+.6*math.sin(math.pi*f))*(1-f**6)+.0003
        for k in range(sides):
            th=k*2*math.pi/sides;vs.append(q+side*(math.cos(th)*w)+normal*(math.sin(th)*dpth))
        if i:
            for k in range(sides):
                a0=(i-1)*sides+k;b0=(i-1)*sides+(k+1)%sides
                fs.append((a0,b0,b0+sides,a0+sides));mi.append(2 if k in (2,3) else (4 if k in (9,10) else col))
    fs.append(tuple(reversed(range(sides))));mi.append(0);fs.append(tuple(range(steps*sides,(steps+1)*sides)));mi.append(col)
    return bind_mesh(name,vs,fs,mi)
# Broad rear silhouette, layered side lengths, then thin face-framing bangs.
for i in range(13):
    a=-math.pi*.94+i*math.pi*1.88/12; x=math.sin(a);f=-abs(math.cos(a))
    lock('N4 back lock %02d'%i,[(x*.12,.47,f*.18),(x*.42,.25,f*.49),(x*.54,-.35,f*.58),(x*.57,-1.05,f*.72),(x*.55+math.sin(i*2)*.07,-1.82-(i%3)*.11,f*.64)],.115,.058,1 if i%3 else 0)
for k in [-1,1]:
    for j in range(4):
        a=.16+j*.095
        lock('N4 side %s %d'%(k,j),[(k*(.10+j*.035),.48,.08),(k*(.43+j*.025),.19,.19-j*.07),(k*(.52+j*.025),-.43,.15-j*.09),(k*(.59+j*.016),-1.15,.17-j*.10),(k*(.65+j*.015),-1.80-(j%2)*.15,.24-j*.08)],.087,.045,1 if j%2 else 2)
# Fine, asymmetrical feathered bangs with eyebrow gap; no giant uniform chunks.
for i in range(11):
    x=-.45+i*.085;root=x*.39+.065;end=x+(.06 if i<5 else -.035)
    length=.08+abs(x)*.33+(.035 if i%3==0 else 0)
    lock('N4 fringe %02d'%i,[(root,.49,.10),(x*.70,.38,.35),(x,.23,.52),(end,.11-length,.54-abs(x)*.12)],.047 if i in (0,10) else .038,.024,1 if i%3 else 2)
# Dark brown eyes with a stronger iris silhouette; move complete iris assemblies, not just pupils.
for o in list(bpy.data.objects):
    if o.type!='MESH':continue
    n=o.name.lower()
    if not any(t in n for t in ('irisouter','irisinner','irisrays','pupil','eyelight')):continue
    center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    side=1 if center.x>c.x else -1
    anchor=Vector((c.x+side*.047,center.y,2.320))
    for v in o.data.vertices:
        v.co.x=anchor.x+(v.co.x-anchor.x)*1.20;v.co.z=anchor.z+(v.co.z-anchor.z)*1.22
        v.co.y+=sign*.0008
    o.data.update()
# Use material multiplication to retain existing iris detail while shifting toward brown.
for m in bpy.data.materials:
    if 'iris' not in m.name.lower() or not m.use_nodes:continue
    bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs:continue
    bc=bs.inputs['Base Color']
    if bc.is_linked:
        source=bc.links[0].from_node
        if source.type=='TEX_IMAGE' and source.image:
            im=source.image; cp=bpy.data.images.new('N4 brown '+im.name,width=im.size[0],height=im.size[1],alpha=True)
            px=array('f',[0.0])*len(im.pixels);im.pixels.foreach_get(px)
            for k in range(0,len(px),4):
                l=max(0,min(1,.2126*px[k]+.7152*px[k+1]+.0722*px[k+2]))
                px[k]=.035+.58*l;px[k+1]=.018+.32*l;px[k+2]=.008+.16*l
            cp.pixels.foreach_set(px);cp.update();cp.pack();source.image=cp
    else:bc.default_value=(.21,.10,.045,1)
bpy.context.view_layer.update()

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'N4_donor_C.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'N4_donor_C.glb'),export_format='GLB',export_apply=False)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
report={'blender':bpy.app.version_string,'source_commit':'8867f677a9c2ce86ec1cc290766f0706b14fab15','mesh_objects':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'armatures':sum(o.type=='ARMATURE' for o in bpy.data.objects),'hair_materials':sorted(seen),'removed_weapon_meshes':removed,'reference_fit':'not measured','status':'candidate, not approved'}
(out/'report.json').write_text(json.dumps(report,indent=2))
def look(o,t):o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.world.color=(.12,.12,.12)
scene.view_settings.view_transform='AgX'
cam=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO'
lights=[]
for name,power,size in [('Key',4.0,1.8),('Fill',1.8,2.0),('Rim',3.5,1.2)]:
    l=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,l);scene.collection.objects.link(ob);lights.append((ob,power,size))
alllo,allhi,ac,az=bounds([p for o in meshes for p in points(o)])
for name,angle,full in [('face_front',0,False),('face_45',45,False),('face_profile',90,False),('full_front',0,True),('full_back',180,True)]:
    t=ac if full else c+Vector((0,0,-.06*s.z));extent=az.z*1.13 if full else s.z*1.75
    scene.render.resolution_x=800;scene.render.resolution_y=1200 if full else 800
    cam.data.ortho_scale=extent;ang=math.radians(angle)
    cam.location=t+Vector((math.sin(ang)*extent*3,sign*math.cos(ang)*extent*3,extent*.035));look(cam,t)
    for (ob,power,size),offset in zip(lights,[(-1.0,sign*1.6,1.2),(1.2,sign*1.2,.4),(.5,-sign*1.1,1.1)]):
        ob.location=t+Vector(offset)*extent;ob.data.energy=power*extent*extent*40;ob.data.size=size*extent;look(ob,t)
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('N4_BLENDER_LAB_COMPLETE',json.dumps(report))
