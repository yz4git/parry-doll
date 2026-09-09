import * as THREE from 'three';

const WHITE=new THREE.Color('#e7e4df'),DARK=new THREE.Color('#171b27'),TRIM=new THREE.Color('#aeb9c5');
function paint(geometry,color){
 const c=[];for(let i=0;i<geometry.attributes.position.count;i++)c.push(color.r,color.g,color.b);
 geometry.setAttribute('color',new THREE.Float32BufferAttribute(c,3));return geometry;
}
function panelGeometry({side=1,topY=-.12,bottomY=-1.48,topX=.48,bottomX=.82,z=-.56,topHalf=.20,bottomHalf=.30,curve=.10,rows=8,cols=4}){
 const p=[],idx=[];
 for(let r=0;r<=rows;r++){
  const t=r/rows,ease=t*t*(3-2*t),cy=THREE.MathUtils.lerp(topY,bottomY,t),cx=THREE.MathUtils.lerp(topX,bottomX,ease)*side,half=THREE.MathUtils.lerp(topHalf,bottomHalf,t),cz=z-curve*Math.sin(Math.PI*t);
  for(let c=0;c<=cols;c++){
   const u=c/cols-.5,edge=1-Math.pow(Math.abs(u)*2,3)*.045;
   p.push(cx+u*half*2,cy+(1-edge)*.035,cz+Math.abs(u)*.055+Math.sin(t*Math.PI)*.018);
  }
 }
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){const a=r*(cols+1)+c,b=a+1,d=(r+1)*(cols+1)+c,e=d+1;idx.push(a,d,b,b,d,e)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
function addPanel(group,name,opts,color=WHITE){
 const g=paint(panelGeometry(opts),color),m=new THREE.Mesh(g,group.userData.materials.cloth);m.name=name;m.castShadow=true;m.receiveShadow=true;m.userData.role='panel';m.userData.side=opts.side||1;m.userData.topY=opts.topY;m.userData.bottomY=opts.bottomY;group.add(m);
 const lining=g.clone(),p=lining.attributes.position,c=lining.attributes.color;for(let i=0;i<p.count;i++){p.setZ(i,p.getZ(i)+.018);c.setXYZ(i,DARK.r,DARK.g,DARK.b)}const ii=Array.from(lining.index.array);for(let i=0;i<ii.length;i+=3)[ii[i+1],ii[i+2]]=[ii[i+2],ii[i+1]];lining.setIndex(ii);lining.computeVertexNormals();const inner=new THREE.Mesh(lining,group.userData.materials.cloth);inner.name=name+'-lining';inner.userData.role='lining';inner.userData.side=opts.side||1;inner.userData.topY=opts.topY;inner.userData.bottomY=opts.bottomY;group.add(inner);
}
export function makeSkirt(materials){
 const group=new THREE.Group();group.name='split-combat-skirt';group.userData.materials=materials;
 const yoke=paint(new THREE.CylinderGeometry(.92,1.03,.46,36,2,true),WHITE);yoke.scale(1,1,.76);const ym=new THREE.Mesh(yoke,materials.cloth);ym.position.y=.08;ym.name='high-waist-yoke';ym.castShadow=true;ym.receiveShadow=true;ym.userData.role='yoke';group.add(ym);
 const yokeIn=yoke.clone(),yp=yokeIn.attributes.position,yc=yokeIn.attributes.color;for(let i=0;i<yp.count;i++){yp.setX(i,yp.getX(i)*.985);yp.setZ(i,yp.getZ(i)*.985);yc.setXYZ(i,DARK.r,DARK.g,DARK.b)}const yi=Array.from(yokeIn.index.array);for(let i=0;i<yi.length;i+=3)[yi[i+1],yi[i+2]]=[yi[i+2],yi[i+1]];yokeIn.setIndex(yi);yokeIn.computeVertexNormals();const yim=new THREE.Mesh(yokeIn,materials.cloth);yim.position.y=.08;yim.name='yoke-lining';yim.userData.role='yoke';group.add(yim);
 addPanel(group,'rear-left',{side:-1,topX:.48,bottomX:.83,topHalf:.18,bottomHalf:.27,topY:-.10,bottomY:-1.52,z:-.57,curve:.13});
 addPanel(group,'rear-right',{side:1,topX:.48,bottomX:.83,topHalf:.18,bottomHalf:.27,topY:-.10,bottomY:-1.52,z:-.57,curve:.13});
 addPanel(group,'side-left',{side:-1,topX:.76,bottomX:.92,topHalf:.12,bottomHalf:.18,topY:-.08,bottomY:-.76,z:-.08,curve:.04,rows:5,cols:3},DARK);
 addPanel(group,'side-right',{side:1,topX:.76,bottomX:.92,topHalf:.12,bottomHalf:.18,topY:-.08,bottomY:-.76,z:-.08,curve:.04,rows:5,cols:3},DARK);
 const trim=paint(new THREE.TorusGeometry(.94,.027,6,36),TRIM);trim.scale(1,1,.76);trim.rotateX(Math.PI/2);const tm=new THREE.Mesh(trim,materials.metal);tm.position.y=.30;tm.name='waist-trim';tm.userData.role='yoke';group.add(tm);
 group.traverse(m=>{if(m.isMesh)m.userData.base=Float32Array.from(m.geometry.attributes.position.array)});delete group.userData.materials;return group;
}
export function updateSkirt(group,clock,flow,motion){
 group.traverse(m=>{if(!m.isMesh||!m.userData.base||m.userData.role==='yoke')return;const a=m.geometry.attributes.position,b=m.userData.base,top=m.userData.topY??-.1,bottom=m.userData.bottomY??-1.5,span=Math.max(.2,top-bottom),side=m.userData.side||1;
  for(let i=0;i<a.count;i++){
   const x=b[i*3],y=b[i*3+1],z=b[i*3+2],t=THREE.MathUtils.clamp((top-y)/span,0,1),w=t*t*(3-2*t),wave=Math.sin(clock*2.8+i*.17+side*.8)*.018;
   const lateral=flow.z*w*.20+side*Math.sin(clock*2.15+i*.07)*.008*w;
   const trail=(motion*.17+Math.max(0,-flow.x)*.12+wave)*w;
   a.setXYZ(i,x+lateral,y+motion*.035*w,z-trail);
  }
  a.needsUpdate=true;m.geometry.computeVertexNormals();
 });
}
