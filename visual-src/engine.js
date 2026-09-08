import * as THREE from 'three';
import {Heroine} from './heroine.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {makeEnvironment} from './environment.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

const ASSET_BASE=new URL('.',document.currentScript?.src||location.href);
const Y=new THREE.Vector3(0,1,0),v=new THREE.Vector3(),q=new THREE.Quaternion(),m=new THREE.Matrix4();
const geometries={
 box:new THREE.BoxGeometry(1,1,1),sphere:new THREE.SphereGeometry(1,16,12),
 cylinder:new THREE.CylinderGeometry(1,1,1,12),cone:new THREE.ConeGeometry(1,1,12),
 ring:new THREE.TorusGeometry(1,.08,6,24),gem:new THREE.IcosahedronGeometry(1,0)
};
function geoShape(points,depth=.15){const shape=new THREE.Shape();points.forEach((p,i)=>i?shape.lineTo(...p):shape.moveTo(...p));shape.closePath();return new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.035,bevelThickness:.035,curveSegments:6})}
geometries.plate=geoShape([[-.65,-.5],[-.9,.15],[-.55,.62],[.55,.62],[.9,.15],[.65,-.5],[0,-.7]],.14);
geometries.blade=geoShape([[-.038,0],[-.032,1.18],[0,1.45],[.065,1.2],[.09,0]],.018);
geometries.fang=new THREE.ConeGeometry(1,1,7);
const color=c=>new THREE.Color(c);
class Assembly {
 constructor(materials){this.buckets=new Map();this.materials=materials}
 add(type,col,pos=[0,0,0],scale=[1,1,1],rot=[0,0,0],material='metal'){
  const base=typeof type==='string'?geometries[type]:type,g=base.index?base.toNonIndexed():base.clone();
  const mat=new THREE.Matrix4().compose(new THREE.Vector3(...pos),new THREE.Quaternion().setFromEuler(new THREE.Euler(...rot)),new THREE.Vector3(...scale));g.applyMatrix4(mat);
  const c=color(col),cs=new Float32Array(g.attributes.position.count*3);for(let i=0;i<cs.length;i+=3){cs[i]=c.r;cs[i+1]=c.g;cs[i+2]=c.b}g.setAttribute('color',new THREE.BufferAttribute(cs,3));
  if(g.attributes.uv)g.deleteAttribute('uv');const bucket=this.buckets.get(material)||[];bucket.push(g);this.buckets.set(material,bucket);return this;
 }
 build(){const group=new THREE.Group();for(const [name,list] of this.buckets){const merged=mergeGeometries(list,false);const mesh=new THREE.Mesh(merged,this.materials[name]);mesh.castShadow=name!=='glow';mesh.receiveShadow=true;group.add(mesh);list.forEach(g=>g.dispose())}return group}
}
function frame(up,face){const y=up.clone().normalize(),f=new THREE.Vector3(Math.sin(face),0,Math.cos(face)),x=new THREE.Vector3().crossVectors(y,f);if(x.lengthSq()<.001)x.set(1,0,0);x.normalize();const z=new THREE.Vector3().crossVectors(x,y).normalize();return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x,y,z))}
function copyP(dst,p){dst.set(p.x,p.y,p.z)}
function palette(d){return d.player?{plate:'#345e60',dark:'#142a32',trim:'#d0a263',cloth:'#226e71',bone:'#bfc8c0',glow:'#90ffe8'}:d.spec.type==='beast'?{plate:'#5f737d',dark:'#1f303a',trim:'#a9b6b2',cloth:'#282c31',bone:'#d8ccb0',glow:'#eebc68'}:d.spec.type==='spider'?{plate:'#514264',dark:'#211d2a',trim:'#a78d68',cloth:'#272030',bone:'#958490',glow:'#e7a2dd'}:d.spec.scale>1.8?{plate:'#79634a',dark:'#322e27',trim:'#cfad71',cloth:'#5d3930',bone:'#c1ac82',glow:'#ffd074'}:{plate:'#753e37',dark:'#2f2428',trim:'#bb8c57',cloth:'#983f33',bone:'#c9b394',glow:'#ffbe77'}}
export class Actor {
 constructor(d,scene,mats){if(d.player)return new Heroine(d,scene,mats,{Assembly,frame});this.d=d;this.root=new THREE.Group();scene.add(this.root);this.parts=[];this.palette=palette(d);const c=this.palette;
  for(const link of d.links){const a=d.nodes[link.a],b=d.nodes[link.b],assembly=new Assembly(mats),torso=link.a===0&&link.b===1;
   assembly.add('cylinder',c.dark,[0,0,0],[.82,1,.78],[0,0,0],'cloth');
   if(torso){
    for(let i=0;i<4;i++)assembly.add('plate',c.plate,[0,.30-i*.19,.55],[1.10-i*.06,.22,.6]);
    assembly.add('plate',c.trim,[0,.32,.63],[.23,.16,.25]);
    for(const side of [-1,1]){assembly.add('box',c.trim,[side*.85,.08,.2],[.075,.72,1.3]);for(let i=0;i<4;i++)assembly.add('sphere',c.trim,[side*.7,.28-i*.18,.73],[.07,.035,.06])}
    for(let i=0;i<3;i++)assembly.add('box',c.cloth,[0,-.35+i*.06,-.02],[1.9,.032,1.65],[0,0,0],'cloth');
   }else{
    assembly.add('cylinder',c.plate,[0,.06,0],[1.05,.72,.94]);
    assembly.add('box',c.trim,[0,.05,.92],[.13,.66,.09]);
    for(const y of [-.36,.37])assembly.add('cylinder',c.trim,[0,y,0],[1.12,.055,1.04]);
    if(d.spec.type==='spider'){assembly.add('cone',c.trim,[0,.08,-1.1],[.4,.35,.9],[Math.PI/2,0,0]);}
   }
   const part=assembly.build();this.root.add(part);this.parts.push({part,link});
  }
  this.nodes=[];
  d.nodes.forEach((n,i)=>{const a=new Assembly(mats);
   if(n.name==='head'){
    a.add('sphere',c.dark,[0,0,0],[.94,1.05,.94]);
    if(d.spec.type==='human'){
     a.add('sphere',c.plate,[0,.22,-.05],[1.13,.95,1.02]);
     a.add('plate',c.bone,[0,-.08,.88],[.83,1.0,.12]);
     a.add('box',c.dark,[0,.18,1.05],[1.15,.13,.11]);
     a.add('box',c.glow,[0,.18,1.12],[.9,.032,.028],[0,0,0],'glow');
     a.add('plate',c.trim,[0,.75,.92],[.14,.8,.12]);
     for(const side of [-1,1]){
      a.add('plate',c.plate,[side*.87,-.34,.25],[.33,.77,.62],[0,side*.4,side*.14]);
      a.add('cone',c.trim,[side*.87,1.05,0],[.19,1.22,.2],[0,0,side*-.55]);
     }
     if(d.spec.scale>1.8){a.add('ring',c.trim,[0,.48,-.45],[1.65,1.65,1.65]);a.add('cone',c.trim,[0,1.36,0],[.26,1.4,.26]);}
    }else if(d.spec.type==='beast'){
     a.add('sphere',c.bone,[0,-.12,.77],[.83,.6,.87]);a.add('box',c.dark,[0,-.23,1.25],[1.02,.25,.8]);
     for(const side of [-1,1]){a.add('gem',c.glow,[side*.56,.25,.83],[.18,.11,.1],[0,0,0],'glow');a.add('cone',c.bone,[side*.72,1.02,-.15],[.24,1.75,.29],[0,0,-side*.3]);a.add('cone',c.bone,[side*.43,-.46,1.28],[.12,.68,.13],[0,0,Math.PI]);}
    }else{
     for(let j=0;j<3;j++)for(const side of [-1,1])a.add('gem',c.glow,[side*(.28+j*.24),.22-j*.18,.86],[.14,.14,.1],[0,0,0],'glow');
     for(const side of [-1,1])a.add('cone',c.trim,[side*.48,-.65,.72],[.23,1.12,.3],[0,side*.3,side*.3+Math.PI]);
    }
   }else if(n.name==='hip'){
    a.add('sphere',c.dark,[0,0,0],[1,1,1],[0,0,0],'cloth');a.add('cylinder',c.trim,[0,0,0],[1.22,.24,1.15]);
    if(d.spec.type==='human')for(const side of [-1,1])a.add('plate',c.cloth,[side*.75,-.72,.22],[.65,1.0,.5],[0,side*.3,side*.18],'cloth');
    else{a.add('sphere',c.plate,[0,.12,-.25],d.spec.type==='spider'?[1.45,1.32,1.85]:[1.28,.85,1.35]);for(let j=0;j<3;j++)a.add('ring',c.trim,[0,.1,-.6+j*.42],[1.15,1.08,.75],[Math.PI/2,0,0]);}
   }else if(n.name==='shoulder'){
    a.add('sphere',c.plate,[0,.1,0],[1.35,.8,1.25]);a.add('plate',c.trim,[0,.06,.94],[1.06,.7,.1]);
    if(!d.player)a.add('cone',c.trim,[Math.sign(n.rest.x)*.7,.65,-.05],[.24,1.05,.3],[0,0,-Math.sign(n.rest.x)*.35]);
   }else if(n.name==='foot'){
    a.add('box',c.dark,[0,-.1,.22],[1.45,.85,2.05],[0,0,0],'cloth');a.add('plate',c.plate,[0,.27,.7],[.88,.38,.3],[Math.PI/2,0,0]);
   }else{a.add('sphere',c.dark,[0,0,0],[1.03,1.03,1.03]);a.add('sphere',c.trim,[0,0,.7],[.72,.6,.45]);}
   const part=a.build();this.root.add(part);this.nodes.push(part);
  });
  if(d.spec.type==='human'){
   const a=new Assembly(mats);a.add('blade','#d1dad8',[0,.06,0],[1,1,1]);a.add('blade',c.trim,[.015,.04,.025],[.3,.84,.28]);a.add('box',c.trim,[0,.02,0],[.34,.055,.18]);a.add('cylinder',c.dark,[0,-.13,0],[.045,.23,.045],[0,0,0],'cloth');for(let j=0;j<5;j++)a.add('cylinder',c.trim,[0,-.22+j*.041,0],[.047,.013,.047]);this.weapon=a.build();this.root.add(this.weapon);
  }
  this.hitLight=new THREE.PointLight(c.glow,0,2.1,2);this.root.add(this.hitLight);
 }
 update(d,pose){const torso=new THREE.Vector3().subVectors(new THREE.Vector3(d.nodes[1].p.x,d.nodes[1].p.y,d.nodes[1].p.z),new THREE.Vector3(d.nodes[0].p.x,d.nodes[0].p.y,d.nodes[0].p.z)),rotation=frame(torso,d.face);
  for(const {part,link} of this.parts){const a=d.nodes[link.a].p,b=d.nodes[link.b].p;part.position.set((a.x+b.x)*.5,(a.y+b.y)*.5,(a.z+b.z)*.5);v.set(b.x-a.x,b.y-a.y,b.z-a.z);part.quaternion.copy(frame(v,d.face));part.scale.set(link.r,v.length(),link.r);}
  this.nodes.forEach((part,i)=>{copyP(part.position,d.nodes[i].p);part.quaternion.copy(rotation);part.scale.setScalar(d.nodes[i].r)});
  if(this.weapon){const hand=d.nodes.find(n=>n.name==='hand');copyP(this.weapon.position,hand.p);v.set(pose.x,pose.y,pose.z);const bladeLength=v.length();v.applyAxisAngle(Y,d.face);this.weapon.quaternion.setFromUnitVectors(Y,v.normalize());this.weapon.scale.set(d.spec.scale,d.spec.scale*bladeLength/1.51,d.spec.scale);}
  this.hitLight.intensity=0;
  if(d.player&&d.parry>0){const hand=d.nodes.find(n=>n.name==='hand');copyP(this.hitLight.position,hand.p);this.hitLight.intensity=.7}
  if(d.hitRegionT>0&&d.hp>0){const n=d.nodes.find(n=>n.name===({head:'head',arm:'elbow',leg:'knee',body:'chest'}[d.hitRegion]||'chest'))||d.nodes[1];copyP(this.hitLight.position,n.p);this.hitLight.intensity=Math.min(2,d.hitRegionT*5)}
 }
 dispose(){this.root.traverse(o=>{if(o.isMesh)o.geometry.dispose()});this.root.removeFromParent()}
}
export class VisualScene {
 constructor(canvas){
  this.renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});this.renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.65));this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.18;
  this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#bbd6e8');this.scene.fog=new THREE.FogExp2('#c7dce8',.009);const environmentRoom=new RoomEnvironment(),pmrem=new THREE.PMREMGenerator(this.renderer);this.envTarget=pmrem.fromScene(environmentRoom,.06);this.scene.environment=this.envTarget.texture;this.scene.environmentIntensity=.85;environmentRoom.dispose();pmrem.dispose();this.camera=new THREE.PerspectiveCamera(45,1,.12,140);
  this.materials={skin:new THREE.MeshStandardMaterial({vertexColors:true,roughness:.65}),hair:new THREE.MeshStandardMaterial({vertexColors:true,roughness:.36,metalness:.15}),porcelain:new THREE.MeshStandardMaterial({vertexColors:true,roughness:.32,metalness:.25}),metal:new THREE.MeshStandardMaterial({vertexColors:true,metalness:.7,roughness:.43}),cloth:new THREE.MeshStandardMaterial({vertexColors:true,metalness:.02,roughness:.95}),glow:new THREE.MeshBasicMaterial({vertexColors:true})};
  this.scene.add(new THREE.HemisphereLight('#c8e2ff','#716e59',2.15));const sun=new THREE.DirectionalLight('#fff0d7',3.5);sun.position.set(-7,13,4);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-13,right:13,top:13,bottom:-13,near:1,far:40});sun.shadow.bias=-.0005;sun.shadow.normalBias=.025;this.scene.add(sun);this.key=sun;
  const rim=new THREE.DirectionalLight('#88bde5',2.4);rim.position.set(5,5,-9);this.scene.add(rim);
  const floor=new THREE.Mesh(new THREE.CylinderGeometry(12.2,12.5,.28,96),new THREE.MeshStandardMaterial({color:'#9bacae',roughness:.85,metalness:.08}));floor.position.y=-.19;floor.receiveShadow=true;this.scene.add(floor);this.floor=floor;this.environment=makeEnvironment(this.scene,ASSET_BASE);
  this.actors=[];this.dolls=[];this.frameCount=0;
  this.sparks=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.042,0),new THREE.MeshBasicMaterial({color:0xffffff}),260);this.sparks.instanceMatrix.setUsage(THREE.DynamicDrawUsage);this.sparks.frustumCulled=false;this.scene.add(this.sparks);
 }
 render(state){
  const {width,height,camera,forward,up,player,boss,poses,particles,clock,recoil}=state;
  if(this.width!==width||this.height!==height){this.width=width;this.height=height;this.renderer.setSize(width,height,false)}
  this.camera.aspect=width/height;this.camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(height/(2*Math.min(width,height)*1.18)));this.camera.updateProjectionMatrix();
  copyP(this.camera.position,camera);copyP(this.camera.up,up);this.camera.lookAt(camera.x+forward.x,camera.y+forward.y,camera.z+forward.z);
  // Match the original projection centre and shake exactly; camera decisions stay in the game.
  this.camera.projectionMatrix.elements[8]=-2*(Math.sin(clock*113)*recoil*14)/width;
  this.camera.projectionMatrix.elements[9]=-.02+2*(Math.cos(clock*139)*recoil*8)/height;
  [player,boss].forEach((d,i)=>{if(this.dolls[i]!==d){this.actors[i]?.dispose();this.actors[i]=new Actor(d,this.scene,this.materials);this.dolls[i]=d}this.actors[i].update(d,poses[i],clock);});
  this.sparks.count=Math.min(260,particles.length);particles.slice(0,260).forEach((p,i)=>{m.makeTranslation(p.p.x,p.p.y,p.p.z);this.sparks.setMatrixAt(i,m);this.sparks.setColorAt(i,color(p.color))});this.sparks.instanceMatrix.needsUpdate=true;if(this.sparks.instanceColor)this.sparks.instanceColor.needsUpdate=true;
  this.environment.update(clock);this.renderer.render(this.scene,this.camera);this.frameCount++;
 }
 get diagnostics(){return{frames:this.frameCount,calls:this.renderer.info.render.calls,triangles:this.renderer.info.render.triangles,geometries:this.renderer.info.memory.geometries,textures:this.renderer.info.memory.textures}}
}
window.ParryVisual={VisualScene};
