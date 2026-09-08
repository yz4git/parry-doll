import * as THREE from 'three';
// All coordinates belong to the render rig. The simulation dolls are read-only.
const Y=new THREE.Vector3(0,1,0);
function taper(points,radius){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const g=new THREE.TubeGeometry(curve,18,radius,6,false),p=g.attributes.position;for(let i=0;i<p.count;i++){const t=Math.floor(i/7)/18,center=curve.getPointAt(t),f=Math.pow(1-t,.55)*.94+.035;p.setXYZ(i,center.x+(p.getX(i)-center.x)*f,center.y+(p.getY(i)-center.y)*f,center.z+(p.getZ(i)-center.z)*f)}g.computeVertexNormals();return g}
function profile(points){return new THREE.LatheGeometry(points.map(p=>new THREE.Vector2(...p)),24)}
export class Heroine {
 constructor(d,scene,mats,{Assembly,frame}){
  this.frame=frame;this.root=new THREE.Group();scene.add(this.root);this.links=[];this.nodes=[];this.hair=[];this.tails=[];
  const white='#e8e5df',black='#171b27',silver='#aeb9c5',skin='#edc1ab',hair='#25232c';
  const add=a=>{const p=a.build();this.root.add(p);return p};
  for(const l of d.links){const a=new Assembly(mats),names=[d.nodes[l.a].name,d.nodes[l.b].name],torso=l.a===0&&l.b===1,neck=names.includes('head'),leg=names.includes('knee')||names.includes('foot');
   if(torso){
    a.add(profile([[.75,-.5],[.78,-.4],[.66,-.16],[.76,.12],[.96,.34],[.88,.5]]),white,[0,0,0],[1,1,.68],[0,0,0],'porcelain');
    a.add('box',black,[0,-.05,-.53],[.22,.83,.08],[0,0,0],'cloth');
    for(const s of [-1,1]){a.add('box',black,[s*.59,.05,-.43],[.11,.83,.09],[0,0,-s*.14],'cloth');a.add('box',silver,[s*.61,.08,-.49],[.055,.3,.04]);a.add('plate',black,[s*.57,.32,.4],[.38,.3,.23],[0,s*.3,0],'cloth');a.add('box',silver,[s*.62,.19,.57],[.045,.4,.04],[0,0,-s*.22]);}
    a.add('ring',silver,[0,.05,-.59],[.21,.15,.21]);
   }else if(neck){a.add('cylinder',skin,[0,.02,0],[.45,.85,.45],[0,0,0],'skin');a.add('cylinder',black,[0,-.29,0],[.59,.3,.55],[0,0,0],'cloth');}
   else{
    const width=leg?.57:.49;
    a.add(profile([[width*.75,-.5],[width,-.35],[width*1.08,.2],[width*.9,.5]]),black,[0,0,0],[1,1,.88],[0,0,0],'cloth');
    if(names.includes('elbow')&&!names.includes('shoulder')){a.add('plate',silver,[0,-.01,.48],[.48,.55,.2]);a.add('plate',black,[0,.13,.57],[.39,.38,.1]);}
    if(names.includes('foot')){a.add('plate',white,[0,.10,.55],[.43,.65,.13],[0,0,0],'porcelain');a.add('box',silver,[0,.11,.65],[.07,.52,.06]);}
    if(names.includes('shoulder'))a.add('cylinder',silver,[0,.25,0],[width*1.06,.045,width*.94]);
   }
   this.links.push({l,p:add(a)});
  }
  d.nodes.forEach(n=>{const a=new Assembly(mats);
   if(n.name==='head'){
    // Smaller adult head, sculpted jaw, lids, irises, nose and layered fringe.
    a.add('sphere',skin,[0,-.02,.03],[.69,.88,.65],[0,0,0],'skin');a.add('sphere',skin,[0,-.45,.24],[.47,.4,.42],[0,0,0],'skin');
    a.add('sphere',skin,[0,-.12,.66],[.095,.19,.13],[0,0,0],'skin');
    for(const s of [-1,1]){a.add('sphere','#ede9e6',[s*.29,.08,.613],[.19,.087,.04],[0,s*.15,s*-.08],'skin');a.add('sphere','#777b86',[s*.285,.08,.65],[.065,.077,.022],[0,0,0],'skin');a.add('sphere','#171725',[s*.285,.08,.668],[.031,.048,.01],[0,0,0],'skin');a.add('sphere','#ffffff',[s*.27,.105,.677],[.015,.017,.009],[0,0,0],'glow');a.add('box',hair,[s*.29,.17,.63],[.38,.035,.035],[0,s*.14,s*.13],'hair');a.add('sphere',skin,[s*.68,-.1,.02],[.12,.23,.14],[0,0,0],'skin');a.add('gem',silver,[s*.72,-.28,.1],[.055,.13,.06]);}
    a.add('sphere','#ae7475',[0,-.42,.59],[.16,.028,.023],[0,0,0],'skin');
    a.add('sphere',hair,[0,.37,-.17],[.75,.62,.68],[0,0,0],'hair');a.add('sphere',hair,[0,.07,-.37],[.70,.83,.48],[0,0,0],'hair');
    for(let i=0;i<11;i++){const x=-.68+i*.13;const g=taper([[x,.73,.07],[x+.18,.6,.48],[x+.07,.30,.66],[x-.18,-.03+Math.abs(x)*.12,.65]],.14);a.add(g,i%3?'#292731':'#45404a',[0,0,0],[1,1,1],[0,0,0],'hair');g.dispose();}
    for(const s of [-1,1])for(let i=0;i<3;i++){const g=taper([[s*.62,.47,0],[s*(.76+i*.03),-.08,.06],[s*.70,-.83,.19],[s*.80,-1.48-i*.15,-.02]],.13);a.add(g,hair,[0,0,0],[1,1,1],[0,0,0],'hair');g.dispose();}
    a.add('ring',silver,[0,.51,-.70],[.29,.28,.29],[Math.PI/2,0,0]);
   }else if(n.name==='hip'){
    a.add('sphere',black,[0,-.1,0],[.87,.63,.68],[0,0,0],'cloth');a.add('cylinder',black,[0,.2,0],[1.0,.22,.75],[0,0,0],'cloth');a.add('box',silver,[.32,.2,.72],[.25,.17,.06]);
    for(const s of [-1,1]){a.add('plate',white,[s*.72,-.27,.1],[.47,.68,.37],[0,s*.22,s*.15],'porcelain');a.add('box',silver,[s*.72,-.2,.37],[.07,.62,.05],[0,0,s*.15]);}
   }else if(n.name==='chest'){a.add('sphere',black,[0,0,0],[.68,.33,.49],[0,0,0],'cloth');a.add('ring',silver,[0,.26,0],[.37,.37,.37],[Math.PI/2,0,0]);}
   else if(n.name==='shoulder'){a.add('sphere',black,[0,0,0],[.83,.7,.78],[0,0,0],'cloth');a.add('plate',white,[0,.25,-.05],[.65,.45,.55],[.25,0,0],'porcelain');a.add('plate',silver,[0,.24,.33],[.39,.24,.1]);}
   else if(n.name==='foot'){a.add('sphere',black,[0,-.15,.18],[.65,.53,.99],[0,0,0],'cloth');a.add('box',black,[0,-.45,.17],[1.03,.17,1.5],[0,0,0],'cloth');a.add('box',silver,[0,-.33,.76],[.7,.13,.09]);}
   else{a.add('sphere',black,[0,0,0],[.68,.68,.66],[0,0,0],'cloth');a.add('plate',silver,[0,.02,.54],[.33,.27,.09]);}
   const p=add(a);this.nodes.push(p);
  });
  for(let i=0;i<9;i++){const a=new Assembly(mats),x=(i-4)*.10,g=taper([[x,.52,-.66],[x+.12,.24,-1.14],[x+.20,-1.1,-1.2],[x-.12,-2.7,-.95],[x+.28,-4.2-(i%3)*.24,-.7]],.18);a.add(g,i%3?'#27252e':'#49434b',[0,0,0],[1,1,1],[0,0,0],'hair');g.dispose();const p=a.build();this.nodes[2].add(p);this.hair.push(p);}
  for(const s of [-1,1]){const a=new Assembly(mats);a.add('plate',white,[s*.55,-1.35,-.55],[.63,1.65,.16],[0,s*.12,s*.13],'porcelain');a.add('box',black,[s*.64,-1.31,-.39],[.09,1.75,.035],[0,0,s*.13],'cloth');a.add('plate',silver,[s*.68,-2.1,-.42],[.30,.26,.07]);const p=a.build();this.nodes[0].add(p);this.tails.push(p);}
  const blade=new Assembly(mats);blade.add('blade','#dbe4ec',[0,.06,0],[1,1,1]);blade.add('blade','#87cddd',[.013,.09,.023],[.23,.9,.2]);blade.add('box',silver,[0,.015,0],[.33,.055,.14]);blade.add('cylinder',black,[0,-.13,0],[.036,.24,.036],[0,0,0],'cloth');for(let i=0;i<6;i++)blade.add('cylinder',silver,[0,-.22+i*.034,0],[.038,.008,.038]);this.weapon=add(blade);
 }
 update(d,pose,clock=0){const vec=p=>new THREE.Vector3(p.x,p.y,p.z),torso=vec(d.nodes[1].p).sub(vec(d.nodes[0].p)),rot=this.frame(torso,d.face);
  // Lengthen the leg silhouette and narrow the shoulders without moving hands or hitboxes.
  const up=torso.clone().normalize(),right=new THREE.Vector3(Math.cos(d.face),0,-Math.sin(d.face));
  const display=d.nodes.map(n=>{const p=vec(n.p);if(n.name==='hip')p.addScaledVector(up,.25*d.spec.scale);if(n.name==='knee')p.addScaledVector(up,.08*d.spec.scale);if(n.name==='shoulder')p.addScaledVector(right,-Math.sign(n.rest.x)*.12*d.spec.scale);return p});
  for(const {l,p} of this.links){const a=display[l.a],b=display[l.b],delta=b.clone().sub(a);p.position.copy(a).lerp(b,.5);p.quaternion.copy(this.frame(delta,d.face));p.scale.set(l.r,delta.length(),l.r);}
  this.nodes.forEach((p,i)=>{p.position.copy(display[i]);p.quaternion.copy(rot);p.scale.setScalar(d.nodes[i].r*(i===2?.88:1))});
  const motion=Math.min(.35,Math.hypot(d.vel?.x||0,d.vel?.z||0)*.035);this.hair.forEach((p,i)=>{p.rotation.x=-motion+Math.sin(clock*2.5+i*.5)*.065;p.rotation.z=Math.sin(clock*2+i*.7)*.05});this.tails.forEach((p,i)=>{p.rotation.x=-motion*.7+Math.sin(clock*2+i)*.04});
  const hand=d.nodes.find(n=>n.name==='hand'),v=vec(pose),length=v.length();v.applyAxisAngle(Y,d.face);this.weapon.position.copy(vec(hand.p));this.weapon.quaternion.setFromUnitVectors(Y,v.normalize());this.weapon.scale.set(d.spec.scale,d.spec.scale*length/1.51,d.spec.scale);
 }
 dispose(){this.root.traverse(o=>{if(o.isMesh)o.geometry.dispose()});this.root.removeFromParent()}
}
