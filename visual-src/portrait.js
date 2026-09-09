import * as THREE from 'three';
import {headData} from './head-data.js';
const skinColor=new THREE.Color('#e7beae');
function paint(g,c){const color=new THREE.Color(c),a=[];for(let i=0;i<g.attributes.position.count;i++)a.push(color.r,color.g,color.b);g.setAttribute('color',new THREE.Float32BufferAttribute(a,3));return g}
function curveMesh(points,radius,material,color){const g=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),24,radius,5,false);return new THREE.Mesh(paint(g,color),material)}
function eyeDepth(x,y){return Math.sqrt(Math.max(.01,1-Math.pow(x/.632,2)))*.604+.03-.05*Math.exp(-Math.pow((Math.abs(x)-.275)/.14,2)-Math.pow((y-.12)/.12,2))+.012}
function eyeSurface(side){const p=[],idx=[],nx=24,ny=8;for(let i=0;i<=nx;i++){const u=i/nx,angle=Math.PI*u,x=side*.275+(u-.5)*.35;for(let j=0;j<=ny;j++){const v=j/ny,y=.115+Math.sin(angle)*(.088*(1-v)-.054*v)+(u-.5)*side*.038,z=eyeDepth(x,y)+Math.sin(angle)*Math.sin(Math.PI*v)*.012;p.push(x,y,z)}}for(let i=0;i<nx;i++)for(let j=0;j<ny;j++){const a=i*(ny+1)+j,b=a+ny+1;idx.push(a,a+1,b,b,a+1,b+1)}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();return g}
export function makePortrait(mats){
 const group=new THREE.Group();group.name='sculpted-portrait';
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(headData.positions,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(headData.uvs,2));g.setIndex(headData.indices);g.computeVertexNormals();const colors=[];for(let i=0;i<g.attributes.position.count;i++){const x=g.attributes.position.getX(i),y=g.attributes.position.getY(i),z=g.attributes.position.getZ(i),blush=z>.25?Math.exp(-Math.pow((Math.abs(x)-.36)/.18,2)-Math.pow((y+.15)/.18,2))*.13:0;colors.push(skinColor.r,skinColor.g*(1-blush),skinColor.b*(1-blush*.55))}g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));const face=new THREE.Mesh(g,mats.skin);face.name='anatomical-face';face.castShadow=true;group.add(face);
 for(const side of [-1,1]){
  const eye=new THREE.Mesh(paint(eyeSurface(side),'#e7ddd6'),mats.skin);eye.name='almond-eye';group.add(eye);
  const iris=new THREE.Mesh(paint(new THREE.SphereGeometry(1,24,16),'#51403b'),mats.skin);iris.position.set(side*.273,.119,eyeDepth(side*.273,.119)+.018);iris.scale.set(.063,.069,.019);group.add(iris);
  const pupil=new THREE.Mesh(paint(new THREE.SphereGeometry(1,16,12),'#151219'),mats.skin);pupil.position.set(side*.273,.12,eyeDepth(side*.273,.12)+.035);pupil.scale.set(.025,.041,.006);group.add(pupil);
  for(let j=0;j<2;j++){const glint=new THREE.Mesh(paint(new THREE.SphereGeometry(1,8,6),'#fff5e9'),mats.glow);glint.position.set(side*.273-.017+j*.032,.142-j*.04,eyeDepth(side*.273,.12)+.040);glint.scale.setScalar(j?.007:.012);group.add(glint)}
  const upper=[],lower=[],brow=[];for(let i=0;i<=16;i++){const u=i/16,x=side*.275+(u-.5)*.35,y=.115+(u-.5)*side*.038;const uy=y+Math.sin(u*Math.PI)*.09,ly=y-Math.sin(u*Math.PI)*.055,by=.275+Math.sin(u*Math.PI)*.035+(u-.5)*side*.015;upper.push([x,uy,eyeDepth(x,uy)+.003]);lower.push([x,ly,eyeDepth(x,ly)]);brow.push([x,by,eyeDepth(x,by)-.007]);}
  group.add(curveMesh(upper,.009,mats.hair,'#27212a'));group.add(curveMesh(lower,.004,mats.skin,'#946c66'));group.add(curveMesh(brow,.013,mats.hair,'#3c3036'));
  const ear=new THREE.Mesh(paint(new THREE.SphereGeometry(1,20,16),'#dbad9e'),mats.skin);ear.position.set(side*.62,-.04,.012);ear.scale.set(.104,.19,.085);group.add(ear);
 }
 group.add(curveMesh([[-.135,-.437,.463],[-.06,-.418,.49],[0,-.432,.50],[.06,-.418,.49],[.135,-.437,.463]],.016,mats.skin,'#bd8480'));
 group.add(curveMesh([[-.13,-.445,.464],[0,-.474,.50],[.13,-.445,.464]],.022,mats.skin,'#d29590'));
 group.add(curveMesh([[-.12,-.442,.48],[0,-.447,.507],[.12,-.442,.48]],.004,mats.skin,'#795558'));
 return group;
}
