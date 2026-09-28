from pathlib import Path

ENVIRONMENT = r'''import * as THREE from 'three';
import {archData} from './architecture-data.js';

let seed=9823;
const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const item=(p,s,r=null,c=null)=>({p,s,r,c});

function batch(scene,geometry,material,list,{cast=true,receive=true}={}){
 if(!list.length)return null;
 const mesh=new THREE.InstancedMesh(geometry,material,list.length);
 const matrix=new THREE.Matrix4(),position=new THREE.Vector3(),scale=new THREE.Vector3(),rotation=new THREE.Quaternion(),euler=new THREE.Euler(),colour=new THREE.Color();
 list.forEach((o,i)=>{
  position.set(...o.p);scale.set(...o.s);euler.set(...(o.r||[0,0,0]));rotation.setFromEuler(euler);matrix.compose(position,rotation,scale);mesh.setMatrixAt(i,matrix);
  if(o.c){colour.set(o.c);mesh.setColorAt(i,colour)}
 });
 mesh.castShadow=cast;mesh.receiveShadow=receive;scene.add(mesh);return mesh;
}

function archGeometry(){
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.Float32BufferAttribute(archData.positions,3));
 g.setIndex(archData.indices);g.computeVertexNormals();return g;
}


const textureCache=new Map();

function makeStainedGlassTexture(kind='blue'){
 const key='glass:'+kind;if(textureCache.has(key))return textureCache.get(key);
 const rose=kind==='rose',w=rose?256:128,h=rose?256:256;
 const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
 const ctx=canvas.getContext('2d');
 const palette=kind==='amber'
  ?['#3d2b33','#b66d3d','#e3bd6c','#72546d','#d78b55']
  :kind==='rose'
   ?['#26334e','#6b4d78','#c48764','#77a5b8','#d5b36b']
   :['#26384c','#4f7894','#87b8c7','#65739b','#c5a56b'];
 ctx.fillStyle='#172532';ctx.fillRect(0,0,w,h);
 if(rose){
  const cx=w/2,cy=h/2;
  for(let ring=0;ring<4;ring++){
   const inner=18+ring*24,outer=inner+21,segments=ring===0?8:12+ring*4;
   for(let i=0;i<segments;i++){
    const a0=i/segments*Math.PI*2+.10*ring,a1=(i+1)/segments*Math.PI*2+.10*ring;
    ctx.beginPath();ctx.moveTo(cx+Math.cos(a0)*inner,cy+Math.sin(a0)*inner);
    ctx.arc(cx,cy,outer,a0,a1);ctx.lineTo(cx+Math.cos(a1)*inner,cy+Math.sin(a1)*inner);
    ctx.arc(cx,cy,inner,a1,a0,true);ctx.closePath();
    ctx.fillStyle=palette[(i+ring*2)%palette.length];ctx.globalAlpha=.88;ctx.fill();
    ctx.globalAlpha=1;ctx.strokeStyle='#1a1d23';ctx.lineWidth=4;ctx.stroke();
   }
  }
  ctx.beginPath();ctx.arc(cx,cy,17,0,Math.PI*2);ctx.fillStyle='#d6ba74';ctx.fill();ctx.strokeStyle='#181b20';ctx.lineWidth=5;ctx.stroke();
 }else{
  for(let y=0;y<4;y++)for(let x=0;x<3;x++){
   const x0=x*w/3,y0=y*h/4,x1=(x+1)*w/3,y1=(y+1)*h/4;
   const inset=5,skew=((x+y)%2?9:-7);
   ctx.beginPath();ctx.moveTo(x0+inset,y0+inset);ctx.lineTo(x1-inset,y0+inset+skew*.30);ctx.lineTo(x1-inset-skew*.18,y1-inset);ctx.lineTo(x0+inset+skew*.12,y1-inset-skew*.22);ctx.closePath();
   ctx.fillStyle=palette[(x+y*2)%palette.length];ctx.globalAlpha=.90;ctx.fill();ctx.globalAlpha=1;
   ctx.strokeStyle='#1b2027';ctx.lineWidth=5;ctx.stroke();
  }
  ctx.strokeStyle='rgba(225,198,126,.55)';ctx.lineWidth=2;ctx.strokeRect(7,7,w-14,h-14);
  ctx.beginPath();ctx.moveTo(w*.5,8);ctx.lineTo(w*.5,h-8);ctx.stroke();
  ctx.beginPath();ctx.moveTo(8,h*.52);ctx.lineTo(w-8,h*.45);ctx.stroke();
 }
 const tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=2;
 textureCache.set(key,tex);return tex;
}

function makeBannerTexture(side,index){
 const key='banner:'+side+':'+index;if(textureCache.has(key))return textureCache.get(key);
 const canvas=document.createElement('canvas');canvas.width=128;canvas.height=256;const ctx=canvas.getContext('2d');
 const base=side<0?(index?'#435b73':'#314967'):(index?'#665f78':'#5a536d');
 ctx.fillStyle=base;ctx.fillRect(0,0,128,256);
 const grad=ctx.createLinearGradient(0,0,128,256);grad.addColorStop(0,'rgba(255,255,255,.14)');grad.addColorStop(.48,'rgba(255,255,255,0)');grad.addColorStop(1,'rgba(5,12,20,.32)');ctx.fillStyle=grad;ctx.fillRect(0,0,128,256);
 ctx.strokeStyle='#b79a67';ctx.lineWidth=5;ctx.strokeRect(9,8,110,240);
 ctx.strokeStyle='rgba(218,195,146,.55)';ctx.lineWidth=2;ctx.strokeRect(16,16,96,224);
 ctx.translate(64,112);
 ctx.strokeStyle='#d1b574';ctx.fillStyle='rgba(211,183,116,.16)';ctx.lineWidth=6;
 ctx.beginPath();ctx.moveTo(0,-45);ctx.lineTo(29,-8);ctx.lineTo(16,38);ctx.lineTo(0,54);ctx.lineTo(-16,38);ctx.lineTo(-29,-8);ctx.closePath();ctx.fill();ctx.stroke();
 ctx.beginPath();ctx.arc(0,-3,17,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(-42,6);ctx.lineTo(42,6);ctx.moveTo(0,-48);ctx.lineTo(0,56);ctx.stroke();
 ctx.resetTransform();
 ctx.fillStyle='rgba(230,214,177,.58)';for(let i=0;i<5;i++)ctx.fillRect(23+i*18,220+(i%2)*4,7,7);
 const tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=2;
 textureCache.set(key,tex);return tex;
}

function makeMaterials(baseURL){
 const loader=new THREE.TextureLoader();
 const load=(name,srgb=false)=>{
  const t=loader.load(new URL('assets/'+name,baseURL).href);
  t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=4;if(srgb)t.colorSpace=THREE.SRGBColorSpace;return t;
 };
 const stoneMap=load('stone-color.png',true),stoneNormal=load('stone-normal.png'),stoneRough=load('stone-rough.png');
 for(const t of [stoneMap,stoneNormal,stoneRough])t.repeat.set(4,4);
 return{
  floor:new THREE.MeshStandardMaterial({map:stoneMap,normalMap:stoneNormal,roughnessMap:stoneRough,normalScale:new THREE.Vector2(.22,.22),color:'#d4cbbc',roughness:.72,metalness:.07}),
  stone:new THREE.MeshStandardMaterial({color:'#b9b2a8',roughness:.8,normalMap:stoneNormal,normalScale:new THREE.Vector2(.16,.16)}),
  stoneCool:new THREE.MeshStandardMaterial({color:'#7f8c98',roughness:.9}),
  stoneDark:new THREE.MeshStandardMaterial({color:'#5c6976',roughness:.94}),
  metal:new THREE.MeshStandardMaterial({color:'#928777',metalness:.73,roughness:.4}),
  bronze:new THREE.MeshStandardMaterial({color:'#9a7653',metalness:.62,roughness:.46}),
  leaf:new THREE.MeshStandardMaterial({color:'#667957',roughness:1}),
  moss:new THREE.MeshStandardMaterial({color:'#75806a',roughness:1}),
  glow:new THREE.MeshBasicMaterial({color:'#d9efff'}),
  fire:new THREE.MeshBasicMaterial({color:'#ffd29a',transparent:true,opacity:.92}),
  blackGlass:new THREE.MeshBasicMaterial({color:'#1d3140'}),
  floorAccent:new THREE.MeshStandardMaterial({color:'#aea08e',roughness:.86,metalness:.02})
 };
}

function arenaFoundation(scene,m){
 const floor=new THREE.Mesh(new THREE.CircleGeometry(12.18,128),m.floor);floor.rotation.x=-Math.PI/2;floor.position.y=-.018;floor.receiveShadow=true;scene.add(floor);
 const lower=new THREE.Mesh(new THREE.CylinderGeometry(14.25,14.55,.72,96),m.stoneCool);lower.position.y=-.43;lower.receiveShadow=true;scene.add(lower);
 const upper=new THREE.Mesh(new THREE.CylinderGeometry(12.52,13.05,.28,96),m.stone);upper.position.y=-.12;upper.receiveShadow=true;scene.add(upper);
 for(const [r,y,w,mat] of [[3.9,.003,.022,m.bronze],[4.05,.003,.022,m.bronze],[9.75,.003,.024,m.metal],[9.92,.003,.024,m.metal],[11.73,.004,.032,m.bronze],[13.73,-.09,.028,m.metal]]){
  const t=new THREE.Mesh(new THREE.TorusGeometry(r,w,6,128),mat);t.rotation.x=Math.PI/2;t.position.y=y;scene.add(t);
 }
 const stones=[],box=new THREE.BoxGeometry(1,1,1);
 for(let i=0;i<28;i++){
  const a=i*Math.PI/14,r=10.72+(i%2)*.28;
  stones.push(item([Math.sin(a)*r,.012,Math.cos(a)*r],[1.15,.026,.92],[0,a,0],i%4===0?'#e2d9c9':'#cfc3b2'));
 }
 batch(scene,box,m.floorAccent,stones,{cast:false});
}

function nearRing(scene,m){
 const box=new THREE.BoxGeometry(1,1,1),cyl=new THREE.CylinderGeometry(1,1,1,10),cone=new THREE.ConeGeometry(1,1,8),rock=new THREE.IcosahedronGeometry(1,0);
 const parapets=[],caps=[],posts=[],braziers=[],flames=[],rubble=[],grass=[],moss=[],rail=[];
 for(let i=0;i<40;i++){
  const a=i*Math.PI/20,r=14.72,x=Math.sin(a)*r,z=Math.cos(a)*r;
  if(!([18,19,20,21,22].includes(i))){
   parapets.push(item([x,.48,z],[.82,.94,1.2],[0,a,0],i%5===0?'#c9c0b2':null));
   if(i%2===0)caps.push(item([x,1.02,z],[1.02,.11,1.38],[0,a,0]));
  }
  if(i%5===0){
   posts.push(item([Math.sin(a)*14.45,1.25,Math.cos(a)*14.45],[.11,1.55,.11]));
   braziers.push(item([Math.sin(a)*14.45,2.01,Math.cos(a)*14.45],[.31,.19,.31]));
   flames.push(item([Math.sin(a)*14.45,2.27,Math.cos(a)*14.45],[.16,.36,.16],null,i%10===0?'#ffdfaa':'#bfe7ff'));
  }
  if(i%3===1)rubble.push(item([Math.sin(a)*13.9,.13,Math.cos(a)*13.9],[.24+rand()*.48,.13+rand()*.18,.28+rand()*.5],[rand()*.45,rand()*6.2,rand()*.45],rand()>.7?'#87919a':'#a8a59e'));
 }
 for(let i=0;i<130;i++){
  const a=rand()*Math.PI*2,r=13.15+rand()*3.4,x=Math.sin(a)*r,z=Math.cos(a)*r;
  grass.push(item([x,.08+rand()*.15,z],[.12+rand()*.45,.16+rand()*.48,.12+rand()*.42],null,rand()>.9?'#9c9c7e':'#68775b'));
  if(i%7===0)moss.push(item([x,.025,z],[.28+rand()*.5,.035,.25+rand()*.55],[0,rand()*6.2,0]));
 }
 for(const side of [-1,1])for(let i=0;i<5;i++){
  const z=-16-i*1.7,x=side*(13.4+i*.38);
  rail.push(item([x,1.6,z],[.065,.065,1.1],[.04,side*.12,0]));
 }
 batch(scene,box,m.stone,parapets);batch(scene,box,m.stone,caps);batch(scene,cyl,m.metal,posts);batch(scene,cyl,m.bronze,braziers);batch(scene,cone,m.fire,flames,{cast:false,receive:false});batch(scene,rock,m.stoneCool,rubble,{cast:false});batch(scene,rock,m.leaf,grass,{cast:false});batch(scene,box,m.moss,moss,{cast:false});batch(scene,cyl,m.metal,rail,{cast:false});
}

function grandGate(scene,m){
 const box=new THREE.BoxGeometry(1,1,1),cyl=new THREE.CylinderGeometry(1,1,1,12),cone=new THREE.ConeGeometry(1,1,10),arch=archGeometry(),gem=new THREE.IcosahedronGeometry(1,1);
 const steps=[],walls=[],columns=[],caps=[],spires=[],arches=[],buttresses=[],windows=[],trims=[],statues=[],altar=[],glass=[];
 for(let i=0;i<8;i++)steps.push(item([0,.13+i*.21,-18.8-i*1.25],[10.6-i*.42,.21,1.48],null,i%2?'#c8c0b4':'#d4ccbf'));
 walls.push(item([0,2.05,-29.1],[11.8,.5,5.0]));walls.push(item([0,5.45,-35.8],[9.1,6.5,1.7]));
 arches.push(item([0,4.7,-34.85],[4.9,5.0,1.55]));
 caps.push(item([0,8.85,-35.8],[10.4,.42,2.2]));
 for(const side of [-1,1]){
  walls.push(item([side*9.1,4.1,-34.0],[1.5,4.5,4.4]));
  for(let i=0;i<5;i++){
   const x=side*(12.2+i*4.15),z=-27.2-i*2.05,y=3.1+i*.18;
   columns.push(item([x,y,z],[.44,6.2,.44]));
   caps.push(item([x,y+3.22,z],[.9,.15,.9]));
   arches.push(item([x-side*2.04,y+1.05,z],[3.05,2.7,1.0],[0,Math.PI/2,0]));
   walls.push(item([x-side*2.05,y+2.85,z],[4.35,.28,1.35]));
   windows.push(item([x,y+1.02,z+.58],[.26,.9,.07],null,i%2?'#dff1ff':'#bcdff0'));
   buttresses.push(item([x+side*.9,y-1.1,z-1.2],[.38,3.8,.72],[.12,0,side*.18]));
  }
 }
 const tower=(x,z,h,r=1.45)=>{
  columns.push(item([x,h*.5,z],[r,h,r]));
  caps.push(item([x,.32,z],[r*2.9,.64,r*2.9]));
  for(let k=1;k<5;k++){caps.push(item([x,h*k/5,z],[r*2.3,.18,r*2.3]));for(const s of [-1,1])trims.push(item([x+s*r*.88,h*k/5+.62,z+r],[.07,1.25,.07]));}
  spires.push(item([x,h+2.4,z],[r*1.18,5.2,r*1.18]));
  for(const dx of [-1,1])for(const dz of [-1,1]){columns.push(item([x+dx*r,h*.58,z+dz*r],[.18,h*1.1,.18]));spires.push(item([x+dx*r,h*1.16,z+dz*r],[.32,2,.32]));}
 };
 tower(-15.7,-40,16,1.5);tower(15.7,-40,18,1.55);tower(0,-49,31,2.55);tower(-8.7,-46,22,1.3);tower(8.9,-45,25,1.35);
 walls.push(item([0,8.2,-48.4],[8.5,9.8,5.4]));arches.push(item([0,8.5,-45.65],[3.8,4.3,1.2]));caps.push(item([0,13.3,-48.4],[10.0,.36,6.0]));
 for(const side of [-1,1]){
  for(let y=5.2;y<11;y+=2.5)windows.push(item([side*2.05,y,-45.58],[.34,1.0,.07],null,side<0?'#c6e7f7':'#f0d8b7'));
  statues.push(item([side*5.0,3.05,-24.8],[.58,2.7,.58]));statues.push(item([side*5.0,4.85,-24.8],[.94,1.05,.94]));statues.push(item([side*5.0,5.95,-24.8],[.32,1.7,.32]));
 }
 altar.push(item([0,2.55,-24.0],[2.15,.46,2.15]));altar.push(item([0,3.08,-24.0],[1.2,.26,1.2]));glass.push(item([0,3.72,-24.0],[.46,.65,.46],null,'#e5f7ff'));
 for(let i=0;i<7;i++){const a=i/7*Math.PI*2;glass.push(item([Math.sin(a)*1.12,3.47, -24+Math.cos(a)*1.12],[.10,.22,.10],null,i%2?'#9fdaf0':'#f0c889'))}
 batch(scene,box,m.floorAccent,steps);batch(scene,box,m.stone,walls);batch(scene,cyl,m.stone,columns);batch(scene,box,m.stone,caps);batch(scene,cone,m.stone,spires);batch(scene,arch,m.stone,arches);batch(scene,box,m.stoneCool,buttresses);batch(scene,box,m.metal,trims);batch(scene,box,m.glow,windows,{cast:false,receive:false});batch(scene,cyl,m.stoneCool,statues);batch(scene,box,m.stoneDark,altar);batch(scene,gem,m.glow,glass,{cast:false,receive:false});
}


function heroLandmarks(scene,m){
 const facadeZ=-45.50;

 // Large rose window: dark glass disk, stone/bronze rings and readable radial spokes.
 const roseGlass=new THREE.MeshBasicMaterial({map:makeStainedGlassTexture('rose'),transparent:true,opacity:.88,depthWrite:false,toneMapped:false});
 const glass=new THREE.Mesh(new THREE.CircleGeometry(1.62,40),roseGlass);
 glass.position.set(0,11.15,facadeZ);glass.castShadow=false;glass.receiveShadow=false;scene.add(glass);
 const outer=new THREE.Mesh(new THREE.TorusGeometry(1.86,.13,8,48),m.stoneCool);
 outer.position.set(0,11.15,facadeZ+.025);outer.castShadow=false;scene.add(outer);
 const inner=new THREE.Mesh(new THREE.TorusGeometry(1.28,.075,7,40),m.bronze);
 inner.position.set(0,11.15,facadeZ+.045);inner.castShadow=false;scene.add(inner);
 const spokes=[],box=new THREE.BoxGeometry(1,1,1);
 for(let i=0;i<12;i++){
  const a=i*Math.PI/6;
  spokes.push(item([Math.cos(a)*.73,11.15+Math.sin(a)*.73,facadeZ+.055],[1.35,.055,.055],[0,0,a],i%3===0?'#b39162':'#8b7b67'));
 }
 batch(scene,box,m.bronze,spokes,{cast:false,receive:false});

 // Dark sanctuary portal sits below the HUD and gives the boss a clean readable silhouette.
 const portal=new THREE.Mesh(new THREE.PlaneGeometry(7.4,6.3),m.blackGlass);
 portal.position.set(0,5.55,-34.93);portal.castShadow=false;portal.receiveShadow=false;scene.add(portal);
 const portalFrame=[];
 for(const x of [-3.55,3.55])portalFrame.push(item([x,5.55,-34.88],[.24,6.45,.20]));
 portalFrame.push(item([0,8.66,-34.88],[7.35,.24,.20]));
 batch(scene,box,m.stoneCool,portalFrame,{cast:false});

 // Low stained-glass windows remain visible during normal combat instead of hiding behind the boss HUD.
 const blueGlass=new THREE.MeshBasicMaterial({map:makeStainedGlassTexture('blue'),transparent:true,opacity:.72,depthWrite:false,toneMapped:false});
 const amberGlass=new THREE.MeshBasicMaterial({map:makeStainedGlassTexture('amber'),transparent:true,opacity:.68,depthWrite:false,toneMapped:false});
 for(const [x,mat] of [[-5.65,blueGlass],[5.65,amberGlass]]){
  const pane=new THREE.Mesh(new THREE.PlaneGeometry(1.12,2.75),mat);pane.position.set(x,6.40,-34.84);scene.add(pane);
  const frame=new THREE.Mesh(new THREE.TorusGeometry(.66,.075,7,28,Math.PI),m.bronze);
  frame.position.set(x,7.78,-34.80);frame.rotation.z=Math.PI;scene.add(frame);
  const mullion=new THREE.Mesh(new THREE.BoxGeometry(.08,2.70,.08),m.bronze);
  mullion.position.set(x,6.40,-34.79);scene.add(mullion);
 }

 // Strong cathedral crown: one gable and asymmetric needle cluster.
 const gable=new THREE.Mesh(new THREE.ConeGeometry(5.4,6.6,3),m.stoneDark);
 gable.position.set(0,17.0,-48.15);gable.rotation.y=Math.PI;gable.scale.z=.58;gable.castShadow=false;scene.add(gable);
 const crown=[];
 for(const [x,y,h,r] of [[-3.5,18.8,4.3,.48],[3.6,19.5,5.8,.52],[-1.5,20.0,3.4,.34],[1.45,20.6,4.1,.36]]){
  crown.push(item([x,y,-47.8],[r,h,r]));
 }
 batch(scene,new THREE.ConeGeometry(1,1,8),m.stoneDark,crown,{cast:false});

 // Flying buttresses: diagonal braces make the mass read as authored gothic architecture.
 const braces=[];
 for(const side of [-1,1]){
  const pairs=[
   [side*6.2,10.6,-45.5,side*.48],
   [side*9.2,8.8,-43.6,side*.55],
   [side*12.3,7.2,-41.8,side*.62],
  ];
  for(const [x,y,z,tilt] of pairs){
   braces.push(item([x,y,z],[4.8,.26,.44],[0,0,tilt]));
   braces.push(item([x+side*.2,y+.38,z-.22],[3.8,.11,.28],[0,0,tilt]));
  }
 }
 batch(scene,box,m.stoneCool,braces,{cast:false});

 // Broken guardian statues. Chunky primitives are intentional: silhouette matters more than micro-detail.
 const addGuardian=(x,z,mirror,broken)=>{
  const group=new THREE.Group();group.position.set(x,0,z);group.rotation.y=mirror<0?.20:-.20;
  const pedestal=new THREE.Mesh(new THREE.CylinderGeometry(.86,1.05,.55,10),m.stoneDark);pedestal.position.y=.28;group.add(pedestal);
  const skirt=new THREE.Mesh(new THREE.ConeGeometry(.72,1.9,8),m.stoneCool);skirt.position.y=1.45;group.add(skirt);
  const torso=new THREE.Mesh(new THREE.CylinderGeometry(.45,.60,1.55,9),m.stone);torso.position.y=2.82;torso.rotation.z=broken?.08:-.04;group.add(torso);
  const head=new THREE.Mesh(new THREE.IcosahedronGeometry(.39,1),m.stone);head.position.set(broken?.13:0,3.92,0);head.scale.set(.82,1.08,.86);group.add(head);
  const shoulderY=3.20;
  const armA=new THREE.Mesh(new THREE.CylinderGeometry(.13,.17,1.55,8),m.stone);armA.position.set(mirror*.55,shoulderY+.02,0);armA.rotation.z=mirror*(broken?.95:.64);group.add(armA);
  if(!broken){
   const armB=new THREE.Mesh(new THREE.CylinderGeometry(.12,.16,1.45,8),m.stone);armB.position.set(-mirror*.50,shoulderY-.03,0);armB.rotation.z=-mirror*.52;group.add(armB);
  }else{
   const stump=new THREE.Mesh(new THREE.CylinderGeometry(.15,.18,.55,8),m.stone);stump.position.set(-mirror*.36,shoulderY+.02,0);stump.rotation.z=-mirror*.82;group.add(stump);
   const fallen=new THREE.Mesh(new THREE.CylinderGeometry(.12,.16,1.02,8),m.stoneCool);fallen.position.set(-mirror*.95,.34,.58);fallen.rotation.set(.18,0,-mirror*1.08);group.add(fallen);
  }
  const wingMat=m.stoneCool;
  for(const side of [-1,1]){
   const wing=new THREE.Mesh(new THREE.BoxGeometry(.18,1.85,.70),wingMat);
   wing.position.set(side*.50,3.08,-.18);wing.rotation.z=side*(broken&&side===-1?.92:.58);wing.rotation.x=-.18;group.add(wing);
  }
  group.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});
  scene.add(group);
 };
 addGuardian(-7.2,-25.9,-1,true);
 addGuardian(7.4,-26.3,1,false);

 // Hanging sanctuary bell: a distinct mid-distance silhouette and focal accent.
 const bellGroup=new THREE.Group();bellGroup.position.set(0,14.45,-44.85);
 const yoke=new THREE.Mesh(new THREE.BoxGeometry(2.6,.20,.30),m.bronze);bellGroup.add(yoke);
 const bell=new THREE.Mesh(new THREE.CylinderGeometry(.55,.92,1.15,16,1,true),m.bronze);bell.position.y=-.72;bell.scale.y=.90;bellGroup.add(bell);
 const lip=new THREE.Mesh(new THREE.TorusGeometry(.91,.08,7,28),m.bronze);lip.rotation.x=Math.PI/2;lip.position.y=-1.25;bellGroup.add(lip);
 const clapper=new THREE.Mesh(new THREE.CylinderGeometry(.07,.10,.70,8),m.metal);clapper.position.y=-1.28;bellGroup.add(clapper);
 bellGroup.traverse(o=>{if(o.isMesh)o.castShadow=false});scene.add(bellGroup);
}

function arenaSigil(scene,m){
 // Thin low-cost ritual marks break the large floor disc without interfering with fighters.
 const rings=[
  [2.35,.020,m.bronze],[5.75,.018,m.floorAccent],[8.55,.018,m.bronze]
 ];
 for(const [r,w,mat] of rings){
  const t=new THREE.Mesh(new THREE.TorusGeometry(r,w,5,96),mat);
  t.rotation.x=Math.PI/2;t.position.y=.010;t.castShadow=false;t.receiveShadow=false;scene.add(t);
 }
 const box=new THREE.BoxGeometry(1,1,1),marks=[];
 for(let i=0;i<12;i++){
  const a=i*Math.PI/6,r=7.1,len=i%3===0?2.15:1.30;
  marks.push(item([Math.sin(a)*r,.012,Math.cos(a)*r],[.035,.012,len],[0,a,0],i%2?'#9f8b70':'#7f8790'));
 }
 batch(scene,box,m.floorAccent,marks,{cast:false,receive:false});
}

function cloisters(scene,m){
 const box=new THREE.BoxGeometry(1,1,1),cyl=new THREE.CylinderGeometry(1,1,1,10),arch=archGeometry(),cone=new THREE.ConeGeometry(1,1,9);
 const decks=[],columns=[],arches=[],rails=[],windows=[],pinnacles=[],hanging=[];
 for(const side of [-1,1])for(let i=0;i<6;i++){
  const x=side*(24.0+i*5.05),z=-7.2-i*6.45,y=4.0+i*.58;
  decks.push(item([x,y,z],[4.35,.28,2.15]));columns.push(item([x,y-2.0,z],[.30,4.0,.30]));columns.push(item([x-side*1.7,y-1.65,z+.75],[.18,3.3,.18]));columns.push(item([x+side*1.7,y-1.65,z+.75],[.18,3.3,.18]));
  rails.push(item([x,y+.62,z+1.0],[4.05,.07,.07]));arches.push(item([x-side*2.25,y+1.0,z],[2.9,2.25,.9],[0,Math.PI/2,0]));
  windows.push(item([x,y+1.04,z-.93],[.22,.74,.06],null,i%3===0?'#f0d1a1':'#c6e6f6'));pinnacles.push(item([x,y+3.25,z],[.42,1.55,.42]));
  if(i<5){const nx=side*(26.45+i*5.05),nz=-10.4-i*6.45;decks.push(item([(x+nx)/2,y+.9,(z+nz)/2],[5.5,.18,1.0],[.10,side*-.28,0]));}
  if(i%2===0)hanging.push(item([x,y-.55,z+1.07],[.055,.92,.055],[.1,0,0]));
 }
 batch(scene,box,m.stoneCool,decks);batch(scene,cyl,m.stone,columns);batch(scene,arch,m.stoneCool,arches);batch(scene,box,m.metal,rails);batch(scene,box,m.glow,windows,{cast:false,receive:false});batch(scene,cone,m.stone,pinnacles);batch(scene,cyl,m.metal,hanging,{cast:false});
}

function farCity(scene,m){
 const box=new THREE.BoxGeometry(1,1,1),cyl=new THREE.CylinderGeometry(1,1,1,10),cone=new THREE.ConeGeometry(1,1,9);
 const masses=[],towers=[],spires=[],bridges=[],lights=[];
 const skyline=(side)=>{
  for(let i=0;i<9;i++){
   const x=side*(34+i*7.2),z=-43-i*4.9-(side>0?i*.8:0),h=7.0+i*1.15+rand()*3.2,w=3.8+rand()*2.8;
   masses.push(item([x,h*.5,z],[w,h,3.8+rand()*2.2],null,i%3===0?'#586571':'#687480'));
   towers.push(item([x,h+3.5,z],[.85+rand()*.35,7+rand()*5,.85+rand()*.35]));
   spires.push(item([x,h+9,z],[1.2+rand()*.45,4+rand()*2.8,1.2+rand()*.45]));
   if(i%2===0)lights.push(item([x,h+1.5,z+2.05],[.14,.42,.06],null,side<0?'#b7e1f4':'#e6c996'));
  }
 };
 skyline(-1);skyline(1);
 for(let i=0;i<6;i++){
  bridges.push(item([19+i*5.6,12.3+i*.55,-55-i*2.0],[5.2,.34,1.2],[.03,-.17,0]));
  bridges.push(item([-18-i*5.7,10.4+i*.48,-53-i*2.25],[5.0,.32,1.15],[.06,.15,0]));
 }
 batch(scene,box,m.stoneDark,masses,{cast:false});batch(scene,cyl,m.stoneDark,towers,{cast:false});batch(scene,cone,m.stoneDark,spires,{cast:false});batch(scene,box,m.stoneCool,bridges,{cast:false});batch(scene,box,m.glow,lights,{cast:false,receive:false});
}

function floatingRuins(scene,m){
 const box=new THREE.BoxGeometry(1,1,1),cone=new THREE.ConeGeometry(1,1,9),cyl=new THREE.CylinderGeometry(1,1,1,10),rock=new THREE.IcosahedronGeometry(1,1);
 const islands=[],caps=[],shards=[],towers=[],lights=[],plants=[];
 for(let i=0;i<15;i++){
  const a=i/15*Math.PI*2,r=40+rand()*31,x=Math.sin(a)*r,z=Math.cos(a)*r-26,y=9+rand()*15,s=2.1+rand()*4.2;
  islands.push(item([x,y-s*.55,z],[s,s*1.55,s],[0,0,Math.PI]));caps.push(item([x,y+.1,z],[s*1.45,.28,s*1.2]));
  if(i%3===0){towers.push(item([x,y+1.55,z],[.36,3.1,.36]));lights.push(item([x,y+3.45,z],[.13,.36,.13],null,'#d5f0ff'))}
  for(let j=0;j<4;j++){shards.push(item([x+(rand()-.5)*s*2.1,y-1.0-j*.7,z+(rand()-.5)*s*1.5],[.16+rand()*.34,.55+rand()*.9,.16+rand()*.34],[rand()*.5,rand()*6.2,rand()*.5]));plants.push(item([x+(rand()-.5)*s*1.5,y+.36,z+(rand()-.5)*s*1.2],[.2+rand()*.55,.16+rand()*.34,.2+rand()*.5],null,'#6f8065'))}
 }
 for(const [x,y,z,r,tilt] of [[-29,21,-59,18,.22],[26,27,-72,24,-.29]]){
  const ring=new THREE.Mesh(new THREE.TorusGeometry(r,.58,8,96,Math.PI*1.62),m.stoneCool);ring.position.set(x,y,z);ring.rotation.set(0,tilt,tilt);ring.castShadow=false;ring.receiveShadow=false;scene.add(ring);
  for(let i=0;i<14;i++){const a=i/14*Math.PI*1.62;caps.push(item([x+Math.cos(a)*r,y+Math.sin(a)*r,z],[1.25,.46,1.6],[0,0,a]))}
 }
 batch(scene,cone,m.stoneDark,islands,{cast:false});batch(scene,box,m.stone,caps,{cast:false});batch(scene,box,m.stoneCool,shards,{cast:false});batch(scene,cyl,m.stone,towers,{cast:false});batch(scene,rock,m.leaf,plants,{cast:false});batch(scene,cone,m.glow,lights,{cast:false,receive:false});
}

function skyLayer(scene){
 const material=new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,uniforms:{uTime:{value:0}},
  vertexShader:'varying vec3 d;void main(){d=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader:`varying vec3 d;uniform float uTime;float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+1.),f.x),f.y);}void main(){vec3 v=normalize(d);float h=smoothstep(-.16,.9,v.y);vec3 c=mix(vec3(.11,.17,.25),vec3(.27,.43,.60),h);c=mix(c,vec3(.56,.69,.80),smoothstep(.28,.96,v.y));vec2 p=v.xz/max(.18,v.y+.34);float t=uTime*.012;float n=noise(p*2.1+vec2(t,0.))*.68+noise(p*4.7-vec2(t*.6,0.))*.32;float cloud=smoothstep(.53,.76,n)*smoothstep(-.08,.24,v.y);c=mix(c,vec3(.88,.91,.94),cloud*.76);vec3 md=normalize(vec3(-.4,.63,-.56));float moon=pow(max(0.,dot(v,md)),230.);float halo=pow(max(0.,dot(v,md)),17.);c+=vec3(.78,.84,.96)*moon*.92+vec3(.14,.18,.29)*halo*.58;gl_FragColor=vec4(c,1.);}`
 });
 const sky=new THREE.Mesh(new THREE.SphereGeometry(150,32,16),material);sky.frustumCulled=false;scene.add(sky);
 const moon=new THREE.Mesh(new THREE.CircleGeometry(6.0,48),new THREE.MeshBasicMaterial({color:'#dce7f7',transparent:true,opacity:.86,depthWrite:false}));moon.position.set(-58,70,-90);moon.lookAt(0,0,0);moon.frustumCulled=false;scene.add(moon);
 return{update(clock){material.uniforms.uTime.value=clock}};
}

function flags(scene){
 const list=[];
 for(const side of [-1,1])for(let i=0;i<3;i++){
  const mat=new THREE.MeshStandardMaterial({map:makeBannerTexture(side,i),color:'#ffffff',roughness:.92,side:THREE.DoubleSide});
  const flag=new THREE.Mesh(new THREE.PlaneGeometry(1.35+i*.16,3.5+i*.24,5,12),mat);flag.position.set(side*(10.5+i*4.0),8.5+i*1.45,-20-i*5.1);flag.rotation.y=side<0?.18:-.18;flag.userData.base=Float32Array.from(flag.geometry.attributes.position.array);scene.add(flag);list.push(flag);
 }
 return{update(clock){list.forEach((f,k)=>{const p=f.geometry.attributes.position,b=f.userData.base;for(let i=0;i<p.count;i++){const x=b[i*3],y=b[i*3+1],z=b[i*3+2];const w=Math.sin(clock*1.35+y*1.45+k*.63)*.13+Math.sin(clock*2.1+x*2.4+k)*.045;p.setXYZ(i,x,y,z+w*(1.8-y)/3.6)}p.needsUpdate=true;if((Math.floor(clock*30)+k)%3===0)f.geometry.computeVertexNormals()})}};
}

function dust(scene){
 const g=new THREE.BufferGeometry(),pts=[];
 for(let i=0;i<150;i++){const a=rand()*Math.PI*2,r=9+rand()*50;pts.push(Math.sin(a)*r,.8+rand()*11,Math.cos(a)*r-10-rand()*34)}
 g.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));g.userData.base=Float32Array.from(pts);
 const mat=new THREE.PointsMaterial({color:'#d9e8f3',size:.065,transparent:true,opacity:.24,depthWrite:false});const p=new THREE.Points(g,mat);scene.add(p);
 return{update(clock){const a=g.attributes.position,b=g.userData.base;for(let i=0;i<a.count;i++){const x=b[i*3],y=b[i*3+1],z=b[i*3+2];a.setXYZ(i,x+Math.sin(clock*.15+i)*.05,y+Math.sin(clock*.55+i*.73)*.09,z+Math.cos(clock*.12+i*.33)*.04)}a.needsUpdate=true}};
}

export function makeEnvironment(scene,baseURL){
 seed=9823;
 const m=makeMaterials(baseURL);
 arenaFoundation(scene,m);
 nearRing(scene,m);
 grandGate(scene,m);
 heroLandmarks(scene,m);
 arenaSigil(scene,m);
 cloisters(scene,m);
 farCity(scene,m);
 floatingRuins(scene,m);
 const sky=skyLayer(scene),cloth=flags(scene),air=dust(scene);
 return{update(clock){sky.update(clock);cloth.update(clock);air.update(clock)}};
}
'''

Path('visual-src/environment.js').write_text(ENVIRONMENT, encoding='utf-8')

doc=Path('docs/VISUAL_UPGRADE.md')
text=doc.read_text(encoding='utf-8')
marker='## Sakura Crossing-inspired environment remake'
section='''

## Sakura Crossing-inspired environment remake

The arena background was rebuilt as a layered authored world rather than a ring of disconnected props. The combat floor and gameplay geometry remain unchanged.

- Near layer: stepped foundation, broken parapets, braziers, rails, rubble, moss and ground scatter soften the transition from arena to world.
- Mid layer: a grand stair, gate, asymmetrical tower group, sanctuary, statues, altar, side cloisters, bridges and lit windows create a deliberate composition behind combat.
- Hero landmarks: a rose window, gable crown, flying buttresses, broken guardian statues, sanctuary bell and restrained arena sigil replace the previous generic-block feel with memorable silhouettes.
- Procedural detail: stained glass and heraldic cloth textures are generated once with Canvas2D, following Sakura Crossing's asset-light authored-detail approach without adding image downloads.
- Far layer: irregular skyline masses, bridges, floating ruins and broken orbital structures provide readable depth without expensive unique meshes.
- Sky layer: animated procedural clouds, moon/halo, cool aerial colour and sparse dust create atmosphere without extra texture assets.
- Performance: repeated architecture is instanced, most far geometry does not cast shadows, and the existing single shadow-casting key light remains the only dynamic shadow source.
- Rendering direction: the layout follows the Sakura Crossing principle of building depth from authored near/mid/far silhouettes and coloured-shadow readability, adapted to PARRY DOLL's darker combat presentation.

Validation is performed by the workflow with the existing visual build plus the full game logic check.
'''
if marker not in text:
    doc.write_text(text.rstrip()+section+'\n', encoding='utf-8')
print('Wrote layered Sakura-inspired environment remake.')
