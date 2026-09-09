import * as THREE from 'three';
function paint(g,color){const c=new THREE.Color(color),a=[];for(let i=0;i<g.attributes.position.count;i++)a.push(c.r,c.g,c.b);g.setAttribute('color',new THREE.Float32BufferAttribute(a,3));return g}
function ribbon(points,width,material,color){
 const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),p=[],uv=[],idx=[],rows=28,cols=6;
 for(let i=0;i<=rows;i++){const t=i/rows,c=curve.getPoint(t),tangent=curve.getTangent(t),across=new THREE.Vector3().crossVectors(tangent,new THREE.Vector3(0,0,1)).normalize(),w=width*Math.pow(Math.max(.015,1-t),.52)*(1+.11*Math.sin(t*6));for(let j=0;j<=cols;j++){const u=j/cols,q=c.clone().addScaledVector(across,(u-.5)*w);q.z+=Math.sin(u*Math.PI)*width*.018;p.push(q.x,q.y,q.z);uv.push(u,t)}}
 for(let i=0;i<rows;i++)for(let j=0;j<cols;j++){const a=i*(cols+1)+j,b=a+1,c=a+cols+1,d=c+1;idx.push(a,b,c,b,d,c)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();paint(g,color);const m=new THREE.Mesh(g,material);m.castShadow=true;return m;
}
function scalp(material){const p=[],uv=[],idx=[],rows=22,cols=64;for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){const a=j/cols*Math.PI*2,front=Math.max(0,Math.sin(a)),back=Math.max(0,-Math.sin(a)),bottom=-.28+front*.73-back*.28,phi=.01+(Math.acos(bottom/.98)-.01)*i/rows,groove=1+Math.sin(a*37)*.007;p.push(Math.cos(a)*Math.sin(phi)*.665*groove,Math.cos(phi)*.98,Math.sin(a)*Math.sin(phi)*.65-.015);uv.push(j/cols,i/rows)}for(let i=0;i<rows;i++)for(let j=0;j<cols;j++){const a=i*(cols+1)+j,b=a+1,c=a+cols+1,d=c+1;idx.push(a,b,c,b,d,c)}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();return new THREE.Mesh(paint(g,'#2b252d'),material)}
export function makeHair(mats){
 const root=new THREE.Group();root.name='layered-swept-hair';const cap=scalp(mats.hair);cap.castShadow=true;root.add(cap);const flowing=[];
 // Broad swept locks overlap at the scalp; alpha fibers soften their edges.
 for(let i=0;i<10;i++){const x=-.56+i*.12,rootX=.25+(i-5)*.028,rootY=.86-Math.abs(i-5)*.012;const lock=ribbon([[rootX,rootY,.20],[x+.24,.65,.50],[x+.12,.39,.61],[x-.045,.245-Math.abs(x)*.58,.58]],.19,mats.hairCard,i%4?'#332a31':'#40333a');root.add(lock);}
 for(const side of [-1,1])for(let i=0;i<4;i++)root.add(ribbon([[side*.51,.70,.32],[side*.66,.19,.36],[side*(.67+i*.023),-.46,.28],[side*.78,-1.22-i*.18,.13]],.14,mats.hairCard,'#352b33'));
 // High tied ponytail fans into long, overlapping S-shaped sheets rather than tubes.
 for(let i=0;i<24;i++){const lane=(i-11.5)/11.5,layer=i%4,fan=lane*.42;const lock=ribbon([[lane*.12,.82,-.50],[lane*.37,.55,-.92-layer*.04],[fan+.16,-.70,-1.12-layer*.04],[fan*1.35-.12,-2.35,-.94-layer*.04],[fan*1.75+.22,-4.4-(i%5)*.14,-.62-layer*.03]],.28+(i%3)*.035,mats.hairCard,i%5?'#30262e':'#45353d');root.add(lock);flowing.push(lock);}
 return{root,flowing};
}
