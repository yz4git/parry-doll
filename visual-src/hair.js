import * as THREE from 'three';

function paint(g,color){
  const c=new THREE.Color(color),a=[];
  for(let i=0;i<g.attributes.position.count;i++)a.push(c.r,c.g,c.b);
  g.setAttribute('color',new THREE.Float32BufferAttribute(a,3));
  return g;
}

function ribbon(points,width,material,color,{rows=30,cols=6,taper=.56,flare=.08}={}){
  const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),p=[],uv=[],idx=[];
  const zAxis=new THREE.Vector3(0,0,1),xAxis=new THREE.Vector3(1,0,0);
  for(let i=0;i<=rows;i++){
    const t=i/rows,c=curve.getPoint(t),tangent=curve.getTangent(t);
    let across=new THREE.Vector3().crossVectors(tangent,zAxis);
    if(across.lengthSq()<1e-6)across.crossVectors(tangent,xAxis);
    across.normalize();
    const w=width*Math.pow(Math.max(.02,1-t),taper)*(1+flare*Math.sin(t*Math.PI));
    for(let j=0;j<=cols;j++){
      const u=j/cols,q=c.clone().addScaledVector(across,(u-.5)*w);
      q.z+=Math.sin(u*Math.PI)*width*.018;
      p.push(q.x,q.y,q.z);uv.push(u,t);
    }
  }
  for(let i=0;i<rows;i++)for(let j=0;j<cols;j++){
    const a=i*(cols+1)+j,b=a+1,c=a+cols+1,d=c+1;idx.push(a,b,c,b,d,c);
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  g.setIndex(idx);g.computeVertexNormals();paint(g,color);
  const m=new THREE.Mesh(g,material);m.castShadow=true;return m;
}

// Hair v3: an opaque crown shell guarantees coverage around the scalp.  The old
// custom cap could expose the anatomical head from some camera angles because of
// its irregular lower edge/winding.  This shell deliberately stops above the
// brows; separate fringe/temple/nape layers create the hairline below it.
function scalp(material){
  const g=new THREE.SphereGeometry(1,64,28,0,Math.PI*2,.02,1.27);
  g.scale(.695,.995,.69);g.translate(0,.015,-.055);g.computeVertexNormals();
  const m=new THREE.Mesh(paint(g,'#2b232c'),material);m.name='hair-v3-crown-shell';m.castShadow=true;return m;
}

function addCrown(root,mats){
  // Opaque under-locks bridge crown -> temples/back so no skin gap can appear
  // between the shell and the translucent strand cards.
  for(let i=0;i<11;i++){
    const lane=(i-5)/5,side=Math.sign(lane)||1,x=lane*.46;
    const lock=ribbon([
      [x*.18,.975,.00],
      [x*.54,.84,.22],
      [x*.88,.58,.42],
      [x*1.08,.31,.43]
    ],.23,mats.hair,i%3?'#302731':'#3a2d36',{rows:22,cols:5,taper:.42,flare:.04});
    lock.name='hair-v3-crown-underlay';root.add(lock);
  }
  for(const side of [-1,1]){
    root.add(ribbon([[side*.18,.89,.28],[side*.42,.73,.47],[side*.56,.40,.52],[side*.56,.08,.45]],.30,mats.hair,'#2f2730',{rows:24,cols:6,taper:.42}));
    root.add(ribbon([[side*.30,.80,-.20],[side*.57,.58,-.30],[side*.66,.20,-.26],[side*.60,-.20,-.18]],.28,mats.hair,'#2a232c',{rows:24,cols:6,taper:.45}));
  }
}

function addFringe(root,mats){
  // Side-swept fringe with overlapping roots.  Roots sit inside the opaque shell
  // and only the tips separate, avoiding the "bald island" seen in the viewer.
  for(let i=0;i<15;i++){
    const lane=(i-7)/7,rootX=-.18+lane*.43,tipX=-.42+lane*.58;
    const depth=.31+Math.abs(lane)*.045;
    const lock=ribbon([
      [rootX,.91,.22],
      [rootX-.07,.75,.43],
      [tipX*.82,.50,.58],
      [tipX,.18-Math.abs(lane)*.08,.57]
    ],.135+(i%3)*.018,mats.hairCard,i%4?'#352a33':'#44343d',{rows:26,cols:5,taper:.62,flare:.10});
    lock.name='hair-v3-fringe';root.add(lock);
  }
  for(const side of [-1,1])for(let i=0;i<5;i++){
    const x=side*(.46+i*.025),tip=side*(.56+i*.035);
    const lock=ribbon([[x,.69,.40],[side*.58,.37,.50],[tip,-.08,.44],[side*(.59+i*.04),-.74-i*.11,.27]],.15,mats.hairCard,'#342a32',{rows:27,cols:5,taper:.57});
    lock.name='hair-v3-face-lock';root.add(lock);
  }
}

function addBackAndPony(root,mats,flowing){
  // Fill nape and build a visibly connected high tie instead of attaching the
  // ponytail as an isolated fan.
  for(const side of [-1,1])for(let i=0;i<5;i++){
    root.add(ribbon([[side*(.18+i*.065),.78,-.28],[side*(.34+i*.055),.48,-.50],[side*(.39+i*.05),.05,-.48],[side*(.34+i*.055),-.55-i*.09,-.31]],.17,mats.hair,'#2c242d',{rows:24,cols:5,taper:.52}));
  }
  const tie=[0,.72,-.69];
  for(let i=0;i<14;i++){
    const lane=(i-6.5)/6.5;
    root.add(ribbon([[lane*.40,.88,-.16],[lane*.34,.79,-.42],[lane*.18,.73,-.61],tie],.16,mats.hair,i%3?'#302630':'#3b2d37',{rows:18,cols:5,taper:.36,flare:.03}));
  }
  // Layered ponytail: dense inner mass + lighter outer strands.  Width tapers
  // strongly at the tips so the silhouette stays elegant rather than slab-like.
  for(let i=0;i<32;i++){
    const lane=(i-15.5)/15.5,layer=i%5,fan=lane*.40;
    const lock=ribbon([
      [lane*.055,.72,-.67],
      [lane*.23,.50,-.91-layer*.018],
      [fan+.08,-.40,-1.06-layer*.025],
      [fan*1.18-.06,-1.70,-.90-layer*.025],
      [fan*1.55+.12,-3.55-(i%6)*.12,-.56-layer*.018]
    ],.20+(i%4)*.022,mats.hairCard,i%5?'#30262f':'#44333d',{rows:32,cols:6,taper:.72,flare:.12});
    lock.name='hair-v3-ponytail';root.add(lock);flowing.push(lock);
  }
  // A few fine flyaways break the outer contour and improve the key-art read.
  for(const side of [-1,1])for(let i=0;i<4;i++){
    const lock=ribbon([[side*.08,.73,-.64],[side*(.26+i*.06),.44,-.88],[side*(.48+i*.08),-.45,-.94],[side*(.60+i*.13),-2.15-i*.22,-.60]],.065,mats.hairCard,'#493640',{rows:25,cols:4,taper:.82,flare:.04});
    lock.name='hair-v3-flyaway';root.add(lock);flowing.push(lock);
  }
}

export function makeHair(mats){
  const root=new THREE.Group();root.name='hair-v3-layered-swept';const flowing=[];
  root.add(scalp(mats.hair));
  addCrown(root,mats);
  addFringe(root,mats);
  addBackAndPony(root,mats,flowing);
  return{root,flowing};
}
