import * as THREE from 'three';

const YOKE=new THREE.Color('#e7e4df'),PANEL=new THREE.Color('#c6ccd2'),DARK=new THREE.Color('#171b27'),TRIM=new THREE.Color('#aeb9c5');
function paint(geometry,color){
 const c=[];for(let i=0;i<geometry.attributes.position.count;i++)c.push(color.r,color.g,color.b);
 geometry.setAttribute('color',new THREE.Float32BufferAttribute(c,3));return geometry;
}
function panelGeometry({side=1,topY=-.01,bottomY=-1.32,topX=.58,bottomX=.88,z=-.55,topHalf=.14,bottomHalf=.035,curve=.07,rows=9,cols=4}){
 const p=[],idx=[];
 for(let r=0;r<=rows;r++){
  const t=r/rows,ease=t*t*(3-2*t),cy=THREE.MathUtils.lerp(topY,bottomY,t),cx=THREE.MathUtils.lerp(topX,bottomX,ease)*side,half=THREE.MathUtils.lerp(topHalf,bottomHalf,Math.pow(t,.82)),cz=z-curve*Math.sin(Math.PI*t);
  for(let c=0;c<=cols;c++){
   const u=c/cols-.5,edgeLift=Math.pow(Math.abs(u)*2,2)*.018;
   p.push(cx+u*half*2,cy+edgeLift,cz+Math.abs(u)*.035+Math.sin(t*Math.PI)*.012);
  }
 }
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){const a=r*(cols+1)+c,b=a+1,d=(r+1)*(cols+1)+c,e=d+1;idx.push(a,d,b,b,d,e)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
function addPanel(group,name,opts){
 const g=paint(panelGeometry(opts),PANEL),m=new THREE.Mesh(g,group.userData.materials.cloth);m.name=name;m.castShadow=true;m.receiveShadow=true;m.userData.role='panel';m.userData.side=opts.side;m.userData.topY=opts.topY;m.userData.bottomY=opts.bottomY;group.add(m);
 const lining=g.clone(),p=lining.attributes.position,c=lining.attributes.color;for(let i=0;i<p.count;i++){p.setZ(i,p.getZ(i)+.014);c.setXYZ(i,DARK.r,DARK.g,DARK.b)}const ii=Array.from(lining.index.array);for(let i=0;i<ii.length;i+=3)[ii[i+1],ii[i+2]]=[ii[i+2],ii[i+1]];lining.setIndex(ii);lining.computeVertexNormals();const inner=new THREE.Mesh(lining,group.userData.materials.cloth);inner.name=name+'-lining';inner.userData.role='lining';inner.userData.side=opts.side;inner.userData.topY=opts.topY;inner.userData.bottomY=opts.bottomY;group.add(inner);
}
export function makeSkirt(materials){
 const group=new THREE.Group();group.name='split-combat-skirt';group.userData.materials=materials;
 // A thin high-waist yoke raises the perceived leg origin without covering the upper thigh.
 const yoke=paint(new THREE.CylinderGeometry(.90,.98,.34,40,2,true),YOKE);yoke.scale(1,1,.73);const ym=new THREE.Mesh(yoke,materials.cloth);ym.position.y=.14;ym.name='high-waist-yoke';ym.castShadow=true;ym.receiveShadow=true;ym.userData.role='yoke';group.add(ym);
 const yokeIn=yoke.clone(),yp=yokeIn.attributes.position,yc=yokeIn.attributes.color;for(let i=0;i<yp.count;i++){yp.setX(i,yp.getX(i)*.985);yp.setZ(i,yp.getZ(i)*.985);yc.setXYZ(i,DARK.r,DARK.g,DARK.b)}const yi=Array.from(yokeIn.index.array);for(let i=0;i<yi.length;i+=3)[yi[i+1],yi[i+2]]=[yi[i+2],yi[i+1]];yokeIn.setIndex(yi);yokeIn.computeVertexNormals();const yim=new THREE.Mesh(yokeIn,materials.cloth);yim.position.y=.14;yim.name='yoke-lining';yim.userData.role='yoke';group.add(yim);
 // Only two narrow spear-shaped rear panels remain. Their tips sweep outward, leaving both thighs and the centre line open.
 addPanel(group,'rear-left',{side:-1,topX:.58,bottomX:.88,topHalf:.14,bottomHalf:.035,topY:-.01,bottomY:-1.32,z:-.55,curve:.07,rows:9,cols:4});
 addPanel(group,'rear-right',{side:1,topX:.58,bottomX:.88,topHalf:.14,bottomHalf:.035,topY:-.01,bottomY:-1.32,z:-.55,curve:.07,rows:9,cols:4});
 const trim=paint(new THREE.TorusGeometry(.92,.022,6,40),TRIM);trim.scale(1,1,.73);trim.rotateX(Math.PI/2);const tm=new THREE.Mesh(trim,materials.metal);tm.position.y=.31;tm.name='waist-trim';tm.userData.role='yoke';group.add(tm);
 group.traverse(m=>{if(m.isMesh)m.userData.base=Float32Array.from(m.geometry.attributes.position.array)});delete group.userData.materials;return group;
}
export function updateSkirt(group,clock,flow,motion){
 group.traverse(m=>{if(!m.isMesh||!m.userData.base||m.userData.role==='yoke')return;const a=m.geometry.attributes.position,b=m.userData.base,top=m.userData.topY??-.01,bottom=m.userData.bottomY??-1.32,span=Math.max(.2,top-bottom),side=m.userData.side||1;
  for(let i=0;i<a.count;i++){
   const x=b[i*3],y=b[i*3+1],z=b[i*3+2],t=THREE.MathUtils.clamp((top-y)/span,0,1),w=t*t*(3-2*t),wave=Math.sin(clock*2.55+i*.13+side*.9)*.012;
   const lateral=flow.z*w*.13+side*(motion*.018+Math.sin(clock*1.9+i*.05)*.004)*w;
   const trail=(motion*.09+Math.max(0,-flow.x)*.06+wave)*w;
   a.setXYZ(i,x+lateral,y+motion*.018*w,z-trail);
  }
  a.needsUpdate=true;m.geometry.computeVertexNormals();
 });
}
