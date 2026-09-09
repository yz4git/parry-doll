import * as THREE from 'three';
import {skirtData} from './couture-data.js';
export function makeSkirt(materials){
 const group=new THREE.Group();group.name='continuous-wrap-skirt';
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(skirtData.positions,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(skirtData.colors,3));geometry.setIndex(skirtData.indices);geometry.computeVertexNormals();
 const outer=new THREE.Mesh(geometry,materials.cloth);outer.castShadow=true;outer.receiveShadow=true;outer.name='woven-outer';group.add(outer);
 // Separate inward-facing lining, a few millimetres inside the fabric, not a solid padded slab.
 const lining=geometry.clone(),p=lining.attributes.position,c=lining.attributes.color;
 for(let i=0;i<p.count;i++){p.setX(i,p.getX(i)*.992);p.setZ(i,p.getZ(i)*.992);c.setXYZ(i,.016,.019,.028)}
 const indices=Array.from(lining.index.array);for(let i=0;i<indices.length;i+=3)[indices[i+1],indices[i+2]]=[indices[i+2],indices[i+1]];lining.setIndex(indices);lining.computeVertexNormals();
 const inner=new THREE.Mesh(lining,materials.cloth);inner.name='dark-lining';group.add(inner);
 group.traverse(m=>{if(m.isMesh)m.userData.base=Float32Array.from(m.geometry.attributes.position.array)});return group;
}
export function updateSkirt(group,clock,flow,motion){
 group.traverse(m=>{if(!m.isMesh)return;const a=m.geometry.attributes.position,b=m.userData.base;
  for(let i=0;i<a.count;i++){const x=b[i*3],y=b[i*3+1],z=b[i*3+2],weight=Math.pow(Math.max(0,.14-y)/1.88,2),wave=Math.sin(clock*2.2+x*2.4)*.024; a.setXYZ(i,x+flow.z*weight*.18,y,z+(motion*.16+wave)*weight)}
  a.needsUpdate=true;m.geometry.computeVertexNormals();
 });
}
