import * as THREE from 'three';
import {HeroineRig} from './heroine-rig.js';
import {bodyData} from './heroine-mesh-data.js';
import {makeSkirt,updateSkirt} from './couture.js';
import {heroineMaterials} from './heroine-materials.js';
// All coordinates belong to the render rig. The simulation dolls are read-only.
const Y=new THREE.Vector3(0,1,0);
function taper(points,radius){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const g=new THREE.TubeGeometry(curve,18,radius,6,false),p=g.attributes.position;for(let i=0;i<p.count;i++){const t=Math.floor(i/7)/18,center=curve.getPointAt(t),f=Math.pow(1-t,.55)*.94+.035;p.setXYZ(i,center.x+(p.getX(i)-center.x)*f,center.y+(p.getY(i)-center.y)*f,center.z+(p.getZ(i)-center.z)*f)}g.computeVertexNormals();return g}
function profile(points){return new THREE.LatheGeometry(points.map(p=>new THREE.Vector2(...p)),24)}
function sculptFace(){
 const rows=28,cols=40,positions=[],indices=[];
 for(let i=0;i<=rows;i++){const t=i/rows,phi=.001+(Math.PI-.002)*t,y=Math.cos(phi)*.88,r=Math.sin(phi),jaw=1-.25*Math.max(0,-y)/.88;
  for(let j=0;j<=cols;j++){const a=j/cols*Math.PI*2,x=Math.cos(a)*r*.69*jaw;let z=Math.sin(a)*r*.65;
   if(z>0){const front=Math.pow(Math.max(0,Math.sin(a)),5),nose=Math.exp(-x*x/ .009-Math.pow((y+.1)/.27,2))*.1,cheek=Math.exp(-Math.pow((Math.abs(x)-.36)/.19,2)-Math.pow((y+.19)/.24,2))*.035,eyes=Math.exp(-Math.pow((Math.abs(x)-.28)/.17,2)-Math.pow((y-.09)/.12,2))*.035;z+=front*(nose+cheek-eyes);}
   positions.push(x,y,z+.035);
  }
 }
 for(let i=0;i<rows;i++)for(let j=0;j<cols;j++){const a=i*(cols+1)+j,b=a+1,c=a+cols+1,d=c+1;indices.push(a,b,c,b,d,c)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setIndex(indices);g.computeVertexNormals();return g;
}
export class Heroine {
 constructor(d,scene,mats,{Assembly,frame}){
  this.surfaces=heroineMaterials(mats);mats=this.surfaces.mats;this.frame=frame;this.root=new THREE.Group();scene.add(this.root);this.rig=new HeroineRig(this.root);this.links=[];this.nodes=[];this.hair=[];this.tails=[];
  const white='#ece9e3',black='#151923',silver='#b9c4cf',skin='#edc1ab',hair='#2a252c';
  const bodyGeometry=new THREE.BufferGeometry();bodyGeometry.setAttribute('position',new THREE.Float32BufferAttribute(bodyData.positions,3));bodyGeometry.setAttribute('color',new THREE.Float32BufferAttribute(bodyData.colors,3));bodyGeometry.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(bodyData.skinIndices,4));bodyGeometry.setAttribute('skinWeight',new THREE.Float32BufferAttribute(bodyData.skinWeights,4));bodyGeometry.setIndex(bodyData.indices);bodyGeometry.computeVertexNormals();bodyGeometry.setAttribute('uv',new THREE.Float32BufferAttribute(bodyData.uvs,2));let groupStart=0;for(let i=1;i<=bodyData.faceMaterials.length;i++){if(i===bodyData.faceMaterials.length||bodyData.faceMaterials[i]!==bodyData.faceMaterials[groupStart]){bodyGeometry.addGroup(groupStart*3,(i-groupStart)*3,bodyData.faceMaterials[groupStart]);groupStart=i;}}
  this.body=new THREE.SkinnedMesh(bodyGeometry,[mats.leather,mats.cloth,mats.skin]);this.body.castShadow=true;this.body.receiveShadow=true;this.body.frustumCulled=false;this.root.add(this.body);this.body.bind(this.rig.skeleton);this.body.normalizeSkinWeights();
  const add=a=>{const p=a.build();this.root.add(p);return p};
  for(const l of d.links){const a=new Assembly(mats),names=[d.nodes[l.a].name,d.nodes[l.b].name],torso=l.a===0&&l.b===1,neck=names.includes('head'),leg=names.includes('knee')||names.includes('foot');
   if(torso){
    // Continuous, weighted torso is supplied by the offline-authored body mesh.
    a.add('box',black,[0,-.05,-.53],[.22,.83,.08],[0,0,0],'cloth');
    for(const s of [-1,1]){a.add('box',black,[s*.49,.05,-.43],[.095,.82,.085],[0,0,-s*.10],'cloth');a.add('box',silver,[s*.51,.08,-.49],[.047,.29,.038]);a.add('plate',black,[s*.47,.31,.4],[.30,.27,.20],[0,s*.23,0],'cloth');a.add('box',silver,[s*.52,.18,.57],[.040,.36,.038],[0,0,-s*.17]);}
    a.add('box',silver,[0,.18,-.59],[.065,.34,.025]);a.add('box',black,[0,.39,-.57],[1.2,.065,.035],[0,0,0],'cloth');a.add('plate',white,[0,.18,-.585],[.72,.24,.045],[0,0,0],'porcelain');a.add('plate',white,[0,-.12,-.56],[.56,.18,.04],[0,0,0],'porcelain');a.add('box',silver,[0,.02,-.625],[.055,.62,.025]);
   }else if(neck){a.add('cylinder',skin,[0,.02,0],[.45,.85,.45],[0,0,0],'skin');a.add('cylinder',black,[0,-.29,0],[.59,.3,.55],[0,0,0],'cloth');}
   else{
    const width=leg?.57:.49;
    // Smooth limb surface is skinned across the elbow/knee, with separate armor accents.
    if(names.includes('elbow')&&!names.includes('shoulder')){a.add('plate',white,[0,-.02,.49],[.52,.58,.21],[0,0,0],'porcelain');a.add('plate',black,[0,.13,.575],[.35,.34,.085]);a.add('box',silver,[0,.08,.615],[.06,.48,.04]);}
    if(names.includes('foot')){a.add('plate',white,[0,.10,.55],[.43,.65,.13],[0,0,0],'porcelain');a.add('box',silver,[0,.11,.65],[.07,.52,.06]);}
    if(names.includes('shoulder')){a.add('cylinder',silver,[0,.25,0],[width*.82,.04,width*.78]);a.add('plate',white,[0,.07,.45],[.35,.31,.11],[.045,0,0],'porcelain');}
   }
   this.links.push({l,p:add(a)});
  }
  d.nodes.forEach(n=>{const a=new Assembly(mats);
   if(n.name==='head'){
    // Smaller adult head, sculpted jaw, lids, irises, nose and layered fringe.
    const face=sculptFace();a.add(face,skin,[0,0,0],[1,1,1],[0,0,0],'skin');face.dispose();
    a.add('sphere',skin,[0,-.15,.68],[.071,.12,.065],[0,0,0],'skin');
    for(const s of [-1,1]){a.add('sphere','#ede9e6',[s*.29,.08,.613],[.19,.087,.04],[0,s*.15,s*-.08],'skin');a.add('sphere','#777b86',[s*.285,.08,.65],[.065,.077,.022],[0,0,0],'skin');a.add('sphere','#171725',[s*.285,.08,.668],[.031,.048,.01],[0,0,0],'skin');a.add('sphere','#ffffff',[s*.27,.105,.677],[.015,.017,.009],[0,0,0],'glow');a.add('box',hair,[s*.29,.17,.63],[.34,.022,.035],[0,s*.14,s*.13],'hair');a.add('sphere',skin,[s*.68,-.1,.02],[.12,.23,.14],[0,0,0],'skin');a.add('gem',silver,[s*.72,-.28,.1],[.055,.13,.06]);}
    a.add('sphere','#ae7475',[0,-.42,.59],[.16,.028,.023],[0,0,0],'skin');
    a.add('sphere',hair,[0,.37,-.17],[.75,.62,.68],[0,0,0],'hair');a.add('sphere',hair,[0,.07,-.37],[.70,.83,.48],[0,0,0],'hair');
    for(let i=0;i<11;i++){const x=-.68+i*.13;const g=taper([[x,.73,.07],[x+.18,.6,.48],[x+.07,.30,.66],[x-.18,-.03+Math.abs(x)*.12,.65]],.14);a.add(g,i%3?'#292731':'#45404a',[0,0,0],[1,1,1],[0,0,0],'hair');g.dispose();}
    for(const s of [-1,1])for(let i=0;i<3;i++){const g=taper([[s*.62,.47,0],[s*(.76+i*.03),-.08,.06],[s*.70,-.83,.19],[s*.80,-1.48-i*.15,-.02]],.13);a.add(g,hair,[0,0,0],[1,1,1],[0,0,0],'hair');g.dispose();}
    a.add('ring',silver,[0,.51,-.70],[.29,.28,.29],[Math.PI/2,0,0]);
   }else if(n.name==='hip'){
    a.add('cylinder',black,[0,.2,0],[1.0,.22,.75],[0,0,0],'cloth');a.add('box',silver,[.32,.2,.72],[.25,.17,.06]);
    for(const s of [-1,1]){a.add('box',silver,[s*.97,.19,.04],[.09,.20,.29]);a.add('box',black,[s*.63,.19,-.61],[.11,.32,.06],[0,0,0],'cloth');}
    a.add('box',silver,[0,.20,-.77],[.30,.13,.035]);a.add('box',black,[0,.20,-.795],[.22,.065,.012],[0,0,0],'cloth');
   }else if(n.name==='chest'){a.add('sphere',black,[0,0,0],[.61,.32,.47],[0,0,0],'cloth');a.add('ring',silver,[0,.25,0],[.34,.34,.34],[Math.PI/2,0,0]);}
   else if(n.name==='shoulder'){a.add('plate',white,[0,.21,-.04],[.45,.36,.43],[.19,0,0],'porcelain');a.add('plate',silver,[0,.20,.31],[.27,.19,.085]);}
   else if(n.name==='foot'){a.add('sphere',black,[0,-.15,.18],[.65,.53,.99],[0,0,0],'cloth');a.add('box',black,[0,-.45,.17],[1.03,.17,1.5],[0,0,0],'cloth');a.add('box',silver,[0,-.33,.76],[.7,.13,.09]);}
   else if(n.name==='hand'||n.name==='offhand'){a.add('box',black,[0,-.1,0],[.72,.9,.42],[0,0,0],'cloth');for(let j=0;j<4;j++){a.add('sphere',black,[(j-1.5)*.18,-.53,.13],[.12,.32,.13],[.18,0,0],'cloth');a.add('box',silver,[(j-1.5)*.18,-.12,.25],[.12,.22,.045]);}}else{a.add('plate',silver,[0,.02,.54],[.33,.27,.09]);}
   const p=add(a);this.nodes.push(p);
  });
  for(let i=0;i<17;i++){const a=new Assembly(mats),x=(i-8)*.058,fan=(i-8)*.018,g=taper([[x,.54,-.66],[x*.82+.10,.16,-1.15],[x+fan,-1.18,-1.19],[x*.72-.12,-2.95,-.92],[x+fan*2+.22,-4.85-(i%4)*.18,-.63]],.145);a.add(g,i%4?'#29262f':'#403943',[0,0,0],[1,1,.70],[0,0,0],'hair');g.dispose();const p=a.build();this.nodes[2].add(p);this.hair.push(p);}
  this.skirt=makeSkirt(mats);this.nodes[0].add(this.skirt);this.tails.push(this.skirt);
  const blade=new Assembly(mats);blade.add('blade','#dbe4ec',[0,.06,0],[1,1,1]);blade.add('blade','#87cddd',[.013,.09,.023],[.23,.9,.2]);blade.add('box',silver,[0,.015,0],[.33,.055,.14]);blade.add('cylinder',black,[0,-.13,0],[.036,.24,.036],[0,0,0],'cloth');for(let i=0;i<6;i++)blade.add('cylinder',silver,[0,-.22+i*.034,0],[.038,.008,.038]);this.weapon=add(blade);
 }
 update(d,pose,clock=0){const vec=p=>new THREE.Vector3(p.x,p.y,p.z),torso=vec(d.nodes[1].p).sub(vec(d.nodes[0].p)),rot=this.frame(torso,d.face);
  const points=this.rig.update(d);
  for(const {l,p} of this.links){const [a,b]=this.rig.segment(d,l),delta=b.clone().sub(a);p.position.copy(a).lerp(b,.5);p.quaternion.copy(this.frame(delta,d.face));p.scale.set(l.r,delta.length(),l.r);}
  this.nodes.forEach((p,i)=>{const n=d.nodes[i];p.position.copy(points[this.rig.nodeName(n)]);p.quaternion.copy(rot);p.scale.setScalar(n.r*(n.name==='head'?.84:n.name==='shoulder'?.74:n.name==='elbow'||n.name==='knee'?.72:1))});
  const dt=this.previousClock===undefined?0:Math.max(0,Math.min(.05,clock-this.previousClock));this.previousClock=clock;
  const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a)),turn=this.previousFace===undefined?0:wrap(d.face-this.previousFace);this.previousFace=d.face;
  const motion=Math.min(.36,Math.hypot(d.vel?.x||0,d.vel?.z||0)*.04),targetSide=Math.max(-.35,Math.min(.35,-turn*4));this.flow=this.flow||{x:0,z:0};const damping=1-Math.exp(-dt*9);this.flow.x+=(-motion-this.flow.x)*damping;this.flow.z+=(targetSide-this.flow.z)*damping;
  this.hair.forEach((p,i)=>{p.rotation.x=this.flow.x+Math.sin(clock*2.5+i*.5)*.035;p.rotation.z=this.flow.z+Math.sin(clock*2+i*.7)*.035});
  updateSkirt(this.skirt,clock,this.flow,motion);
  const hand=d.nodes.find(n=>n.name==='hand'),v=vec(pose),length=v.length();v.applyAxisAngle(Y,d.face);this.weapon.position.copy(vec(hand.p));this.weapon.quaternion.setFromUnitVectors(Y,v.normalize());this.weapon.scale.set(d.spec.scale,d.spec.scale*length/1.51,d.spec.scale);
 }
 dispose(){this.surfaces.dispose();this.rig.dispose();this.root.traverse(o=>{if(o.isMesh)o.geometry.dispose()});this.root.removeFromParent()}
}
