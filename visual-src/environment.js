import * as THREE from 'three';
let seed=9823;
const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const matrix=new THREE.Matrix4(),rotation=new THREE.Quaternion();
function batch(scene,geometry,material,items,shadow=true){const mesh=new THREE.InstancedMesh(geometry,material,items.length);items.forEach((o,i)=>{rotation.setFromEuler(new THREE.Euler(...(o.r||[0,0,0])));matrix.compose(new THREE.Vector3(...o.p),rotation,new THREE.Vector3(...o.s));mesh.setMatrixAt(i,matrix);if(o.c)mesh.setColorAt(i,new THREE.Color(o.c))});mesh.castShadow=shadow;mesh.receiveShadow=true;scene.add(mesh);return mesh}
const obj=(p,s,r,c)=>({p,s,r,c});
export function makeEnvironment(scene,baseURL){
 seed=9823;
 const loader=new THREE.TextureLoader(),load=(name,color=false)=>{const t=loader.load(new URL('assets/'+name,baseURL).href);t.wrapS=t.wrapT=THREE.RepeatWrapping;if(color)t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;return t};
 const map=load('stone-color.png',true),normalMap=load('stone-normal.png'),roughnessMap=load('stone-rough.png');
 const stone=new THREE.MeshStandardMaterial({map,normalMap,roughnessMap,normalScale:new THREE.Vector2(.45,.45),roughness:.92,color:'#b7bbb5'});
 const darkStone=stone.clone();darkStone.color.set('#687b79');
 const bronze=new THREE.MeshStandardMaterial({color:'#9e7950',metalness:.75,roughness:.53});
 const wood=new THREE.MeshStandardMaterial({color:'#252b2a',roughness:.89});
 const box=new THREE.BoxGeometry(1,1,1),cylinder=new THREE.CylinderGeometry(1,1,1,12);
 // Same level, same navigable radius. All new tall scenery is outside the gameplay boundary.
 const floorMap=map.clone();floorMap.needsUpdate=true;floorMap.repeat.set(4,4);
 const floorNormal=normalMap.clone();floorNormal.needsUpdate=true;floorNormal.repeat.set(4,4);
 const floorRough=roughnessMap.clone();floorRough.needsUpdate=true;floorRough.repeat.set(4,4);
 const floorMaterial=new THREE.MeshStandardMaterial({map:floorMap,normalMap:floorNormal,roughnessMap:floorRough,normalScale:new THREE.Vector2(.24,.24),color:'#b1c0bd',metalness:.12,roughness:.78});
 const floor=new THREE.Mesh(new THREE.CircleGeometry(12.18,128),floorMaterial);floor.rotation.x=-Math.PI/2;floor.position.y=-.018;floor.receiveShadow=true;scene.add(floor);
 for(const radius of [3.9,4.1,9.75,9.92,11.75]){const ring=new THREE.Mesh(new THREE.TorusGeometry(radius,radius>11?.045:.022,5,160),bronze);ring.rotation.x=Math.PI/2;ring.position.y=-.002;ring.receiveShadow=true;scene.add(ring)}
 const radial=[];for(let i=0;i<32;i++){const a=i*Math.PI/16;radial.push(obj([Math.sin(a)*11.15,-.008,Math.cos(a)*11.15],[.035,.025,.6],[0,a,0]))}batch(scene,box,bronze,radial,false);
 const tiles=[],columns=[],capstones=[],woodParts=[],bronzeParts=[];
 for(let i=0;i<48;i++){const a=i*Math.PI/24,r=12.5;tiles.push(obj([Math.sin(a)*r,-.07,Math.cos(a)*r],[1.58,.4,1.15],[0,a,0]));}
 for(let i=0;i<16;i++){
  const a=i*Math.PI/8,r=13.5,x=Math.sin(a)*r,z=Math.cos(a)*r,h=2.2+(i%3)*.5;
  columns.push(obj([x,h/2,z],[.52,h,.52],[0,a,0]));capstones.push(obj([x,.1,z],[1.0,.2,1.0],[0,a,0]));capstones.push(obj([x,h,z],[.95,.22,.95],[0,a,0]));
  if(i%4!==0){const a2=a+Math.PI/16;woodParts.push(obj([Math.sin(a2)*r,.82,Math.cos(a2)*r],[4.7,.2,.22],[0,-a2,0]));}
 }
 // Stone stair and weathered gate, with a curved silhouette built from roof segments.
 for(let i=0;i<6;i++)tiles.push(obj([0,-.1+i*.17,-12.9-i*.56],[8-i*.12,.32,.65]));
 for(const side of [-1,1]){columns.push(obj([side*4.1,3.2,-17],[.85,6.4,.85]));capstones.push(obj([side*4.1,.18,-17],[1.6,.36,1.6]));bronzeParts.push(obj([side*4.1,5.6,-17],[1.02,.16,1.02]));}
 woodParts.push(obj([0,5.75,-17],[10.0,.5,.82]));woodParts.push(obj([0,4.85,-17],[8.8,.28,.6]));
 for(let i=-6;i<=6;i++){const x=i*.82,y=6.05+.035*x*x;capstones.push(obj([x,y,-17],[.86,.32,1.4],[0,0,x*.065]));bronzeParts.push(obj([x,y+.18,-16.24],[.85,.035,.04],[0,0,x*.065]));}
 // Outer retaining walls and long roofed galleries give real depth to the courtyard.
 for(const side of [-1,1])for(let i=0;i<8;i++){
  const z=-20+i*5;columns.push(obj([side*22,3,z],[.65,6,.65]));tiles.push(obj([side*24,1.6,z],[.7,3.2,4.6]));woodParts.push(obj([side*22,5.45,z],[.35,.42,5.2]));capstones.push(obj([side*22,6.15,z],[5,.22,5.2],[0,0,side*.12]));
 }
 for(let i=0;i<10;i++){
  const x=-22+i*4.9;tiles.push(obj([x,1.7,-26],[4.8,3.4,.7]));columns.push(obj([x,3.1,-26],[.65,6.2,.65]));capstones.push(obj([x,6.4,-26],[5.2,.3,4],[.06,0,0]));
 }
 batch(scene,box,stone,tiles);batch(scene,box,darkStone,columns);batch(scene,box,stone,capstones);batch(scene,box,wood,woodParts);batch(scene,box,bronze,bronzeParts);
 const rocks=[];for(let i=0;i<70;i++){const a=rand()*Math.PI*2,r=14+rand()*23,s=.4+rand()*1.6;rocks.push(obj([Math.cos(a)*r,-.12,Math.sin(a)*r],[s,.3+rand()*s,s*.8],[rand()*.5,rand()*6,rand()*.5],i%3?'#435453':'#65726a'))}batch(scene,new THREE.IcosahedronGeometry(1,1),stone,rocks);
 const mountains=[];for(let i=0;i<24;i++){const a=i*Math.PI/12,r=60+rand()*16;mountains.push(obj([Math.sin(a)*r,-5,Math.cos(a)*r],[9+rand()*13,12+rand()*24,10+rand()*15],[0,rand()*6,.1-rand()*.2]))}batch(scene,new THREE.ConeGeometry(1,1,7,2),new THREE.MeshStandardMaterial({color:'#223f48',roughness:1}),mountains,false);
 // Moonlit sky, authored as a shader, unaffected by game time or input.
 const sky=new THREE.Mesh(new THREE.SphereGeometry(110,32,16),new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,uniforms:{},vertexShader:'varying vec3 dir;void main(){dir=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec3 dir;void main(){vec3 d=normalize(dir);float h=smoothstep(-.1,.8,d.y);vec3 c=mix(vec3(.12,.22,.26),vec3(.018,.041,.074),h);float moon=pow(max(0.,dot(d,normalize(vec3(-.4,.55,-.8)))),160.);c+=vec3(.35,.43,.41)*moon;gl_FragColor=vec4(c,1.);}'}));scene.add(sky);
 const moon=new THREE.Mesh(new THREE.SphereGeometry(2.6,24,16),new THREE.MeshBasicMaterial({color:'#dbe8d8',fog:false}));moon.position.set(-25,35,-65);scene.add(moon);
 // Lanterns, using emissive cores and only two point lights to keep mobile costs bounded.
 const lanternFrames=[],lanternGlass=[];
 for(const [x,z] of [[-8,-10],[8,-10],[-11,4],[11,4],[-4.8,-15],[4.8,-15]]){
  lanternFrames.push(obj([x,.42,z],[.8,.84,.8]));lanternFrames.push(obj([x,1.14,z],[.9,.14,.9]));lanternFrames.push(obj([x,1.9,z],[1.02,.2,1.02]));lanternGlass.push(obj([x,1.51,z],[.56,.57,.56]));
  for(const dx of [-.32,.32])for(const dz of [-.32,.32])lanternFrames.push(obj([x+dx,1.51,z+dz],[.055,.7,.055]));
 }
 batch(scene,box,bronze,lanternFrames);const lanternMat=new THREE.MeshStandardMaterial({color:'#ffd196',emissive:'#fbb058',emissiveIntensity:2.3,roughness:.5});batch(scene,box,lanternMat,lanternGlass,false);
 const lights=[];for(const [x,z] of [[-8,-10],[8,-10]]){const light=new THREE.PointLight('#ffb86c',14,12,2);light.position.set(x,1.8,z);scene.add(light);lights.push(light)}
 const flags=[];for(const side of [-1,1]){
  const pole=new THREE.Mesh(cylinder,bronze);pole.scale.set(.055,5.3,.055);pole.position.set(side*7.7,2.65,-16);scene.add(pole);
  const geometry=new THREE.PlaneGeometry(1.5,3.2,6,14),mat=new THREE.MeshStandardMaterial({color:side<0?'#722e2b':'#263f43',roughness:1,side:THREE.DoubleSide});
  const flag=new THREE.Mesh(geometry,mat);flag.position.set(side*7.7,3.4,-16);flag.castShadow=true;flag.userData.base=Float32Array.from(geometry.attributes.position.array);scene.add(flag);flags.push(flag);
 }
 return {update(clock){lights.forEach((l,i)=>l.intensity=13+Math.sin(clock*3.3+i)*.7);flags.forEach((flag,k)=>{const a=flag.geometry.attributes.position,base=flag.userData.base;for(let i=0;i<a.count;i++){const x=base[i*3],y=base[i*3+1];a.setZ(i,Math.sin(clock*1.6+y*1.7+k)*.12*(1.6-y)/3.2+Math.sin(x*3+clock)*.035)}a.needsUpdate=true;flag.geometry.computeVertexNormals()})}};
}
