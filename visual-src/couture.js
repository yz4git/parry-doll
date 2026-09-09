import * as THREE from 'three';

const YOKE=new THREE.Color('#e7e4df'),PANEL=new THREE.Color('#d8dce0'),DARK=new THREE.Color('#171b27'),TRIM=new THREE.Color('#aeb9c5');
function paint(geometry,color){
 const c=[];for(let i=0;i<geometry.attributes.position.count;i++)c.push(color.r,color.g,color.b);
 geometry.setAttribute('color',new THREE.Float32BufferAttribute(c,3));return geometry;
}
function highCutYokeGeometry(innerScale=1){
 const seg=48,p=[],idx=[];
 for(let r=0;r<3;r++){
  for(let i=0;i<=seg;i++){
   const a=i/seg*Math.PI*2,x=Math.cos(a),z=Math.sin(a),side=Math.abs(x);
   const top=.39,mid=.29+.055*side,bottom=.15+.15*side;
   const y=r===0?top:r===1?mid:bottom;
   const radiusX=(r===0?.88:r===1?.93:.98)*innerScale,radiusZ=(r===0?.67:r===1?.70:.72)*innerScale;
   p.push(x*radiusX,y,z*radiusZ);
  }
 }
 for(let r=0;r<2;r++)for(let i=0;i<seg;i++){const a=r*(seg+1)+i,b=a+1,d=(r+1)*(seg+1)+i,e=d+1;idx.push(a,d,b,b,d,e)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
function panelGeometry({side=1,topY=.12,bottomY=-1.18,topX=.54,bottomX=.84,z=-.54,topHalf=.18,bottomHalf=.055,curve=.075,rows=10,cols=5}){
 const p=[],idx=[];
 for(let r=0;r<=rows;r++){
  const t=r/rows,ease=t*t*(3-2*t),cy=THREE.MathUtils.lerp(topY,bottomY,t),cx=THREE.MathUtils.lerp(topX,bottomX,ease)*side,half=THREE.MathUtils.lerp(topHalf,bottomHalf,Math.pow(t,.88)),cz=z-curve*Math.sin(Math.PI*t);
  for(let c=0;c<=cols;c++){
   const u=c/cols-.5,edgeLift=Math.pow(Math.abs(u)*2,2)*.014;
   p.push(cx+u*half*2,cy+edgeLift,cz+Math.abs(u)*.032+Math.sin(t*Math.PI)*.012);
  }
 }
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){const a=r*(cols+1)+c,b=a+1,d=(r+1)*(cols+1)+c,e=d+1;idx.push(a,d,b,b,d,e)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
function addPanel(group,name,opts){
 const g=paint(panelGeometry(opts),PANEL),m=new THREE.Mesh(g,group.userData.materials.cloth);m.name=name;m.castShadow=true;m.receiveShadow=true;m.userData.role='panel';m.userData.side=opts.side;m.userData.topY=opts.topY;m.userData.bottomY=opts.bottomY;group.add(m);
 const lining=g.clone(),p=lining.attributes.position,c=lining.attributes.color;for(let i=0;i<p.count;i++){p.setZ(i,p.getZ(i)+.014);c.setXYZ(i,DARK.r,DARK.g,DARK.b)}const ii=Array.from(lining.index.array);for(let i=0;i<ii.length;i+=3)[ii[i+1],ii[i+2]]=[ii[i+2],ii[i+1]];lining.setIndex(ii);lining.computeVertexNormals();const inner=new THREE.Mesh(lining,group.userData.materials.cloth);inner.name=name+'-lining';inner.userData.role='lining';inner.userData.side=opts.side;inner.userData.topY=opts.topY;inner.userData.bottomY=opts.bottomY;group.add(inner);
}
function waistTrimGeometry(){
 const seg=64,p=[];
 for(let i=0;i<=seg;i++){
  const a=i/seg*Math.PI*2,x=Math.cos(a),z=Math.sin(a),side=Math.abs(x),y=.385-.025*(1-side);
  p.push(new THREE.Vector3(x*.89,y,z*.675));
 }
 const curve=new THREE.CatmullRomCurve3(p,true,'centripetal');return new THREE.TubeGeometry(curve,64,.018,5,true);
}
export function makeSkirt(materials){
 const group=new THREE.Group();group.name='split-combat-skirt';group.userData.materials=materials;
 // High-cut yoke: the lower edge climbs over the outer hip so the visible leg begins higher.
 const yoke=paint(highCutYokeGeometry(1),YOKE),ym=new THREE.Mesh(yoke,materials.cloth);ym.name='high-waist-yoke';ym.castShadow=true;ym.receiveShadow=true;ym.userData.role='yoke';group.add(ym);
 const yokeIn=paint(highCutYokeGeometry(.985),DARK),yi=Array.from(yokeIn.index.array);for(let i=0;i<yi.length;i+=3)[yi[i+1],yi[i+2]]=[yi[i+2],yi[i+1]];yokeIn.setIndex(yi);yokeIn.computeVertexNormals();const yim=new THREE.Mesh(yokeIn,materials.cloth);yim.name='yoke-lining';yim.userData.role='yoke';group.add(yim);
 // Two visible rear spears: wide enough at the root to read as cloth, tapered enough to avoid the old drooping-lobe silhouette.
 addPanel(group,'rear-left',{side:-1,topX:.54,bottomX:.84,topHalf:.18,bottomHalf:.055,topY:.12,bottomY:-1.18,z:-.54,curve:.075,rows:10,cols:5});
 addPanel(group,'rear-right',{side:1,topX:.54,bottomX:.84,topHalf:.18,bottomHalf:.055,topY:.12,bottomY:-1.18,z:-.54,curve:.075,rows:10,cols:5});
 const trim=paint(waistTrimGeometry(),TRIM),tm=new THREE.Mesh(trim,materials.metal);tm.name='waist-trim';tm.userData.role='yoke';group.add(tm);
 group.traverse(m=>{if(m.isMesh)m.userData.base=Float32Array.from(m.geometry.attributes.position.array)});delete group.userData.materials;return group;
}
export function updateSkirt(group,clock,flow,motion){
 group.traverse(m=>{if(!m.isMesh||!m.userData.base||m.userData.role==='yoke')return;const a=m.geometry.attributes.position,b=m.userData.base,top=m.userData.topY??.12,bottom=m.userData.bottomY??-1.18,span=Math.max(.2,top-bottom),side=m.userData.side||1;
  for(let i=0;i<a.count;i++){
   const x=b[i*3],y=b[i*3+1],z=b[i*3+2],t=THREE.MathUtils.clamp((top-y)/span,0,1),w=t*t*(3-2*t),wave=Math.sin(clock*2.45+i*.11+side*.9)*.011;
   const lateral=flow.z*w*.12+side*(motion*.017+Math.sin(clock*1.85+i*.05)*.004)*w;
   const trail=(motion*.085+Math.max(0,-flow.x)*.055+wave)*w;
   a.setXYZ(i,x+lateral,y+motion*.015*w,z-trail);
  }
  a.needsUpdate=true;m.geometry.computeVertexNormals();
 });
}
