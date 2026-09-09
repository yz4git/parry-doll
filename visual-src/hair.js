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

// Hair v3.1: split scalp coverage into a closed top cap and a rear shell.
// The previous single shell sat inside the anatomical forehead at some view
// angles, exposing a skin-coloured crown.  The top cap is deliberately outside
// the sculpt only above the hairline; the rear shell fills occipital/side gaps
// without becoming a helmet over the face.
function scalp(material){
  const group=new THREE.Group();group.name='hair-v3-scalp-coverage';
  const top=new THREE.SphereGeometry(1,64,26,0,Math.PI*2,0,.94);
  top.scale(.725,1.035,.755);top.translate(0,.018,-.005);top.computeVertexNormals();
  const topMesh=new THREE.Mesh(paint(top,'#2b232c'),material);topMesh.name='hair-v3-top-cap';topMesh.castShadow=true;group.add(topMesh);
  const back=new THREE.SphereGeometry(1,56,22,Math.PI,Math.PI,.56,1.02);
  back.scale(.715,1.01,.735);back.translate(0,.005,-.035);back.computeVertexNormals();
  const backMesh=new THREE.Mesh(paint(back,'#282129'),material);backMesh.name='hair-v3-rear-shell';backMesh.castShadow=true;group.add(backMesh);
  return group;
}

function addCrown(root,mats){
  // Opaque under-locks bridge crown -> temples/back so no skin gap can appear
  // between the shell and the translucent strand cards.
  for(let i=0;i<11;i++){
    const lane=(i-5)/5,x=lane*.46;
    const lock=ribbon([
      [x*.18,.985,.00],
      [x*.54,.85,.25],
      [x*.88,.59,.44],
      [x*1.08,.31,.43]
    ],.235,mats.hair,i%3?'#302731':'#3a2d36',{rows:22,cols:5,taper:.42,flare:.04});
    lock.name='hair-v3-crown-underlay';root.add(lock);
  }
  for(const side of [-1,1]){
    root.add(ribbon([[side*.14,.94,.20],[side*.40,.78,.46],[side*.56,.43,.53],[side*.56,.08,.45]],.31,mats.hair,'#2f2730',{rows:24,cols:6,taper:.42}));
    root.add(ribbon([[side*.28,.84,-.15],[side*.56,.61,-.31],[side*.66,.20,-.26],[side*.60,-.20,-.18]],.29,mats.hair,'#2a232c',{rows:24,cols:6,taper:.45}));
  }
}

function addFringe(root,mats){
  // Side-swept fringe with overlapping roots. Roots begin high enough to hide
  // the cap edge, then split toward the brow and temples.
  for(let i=0;i<17;i++){
    const lane=(i-8)/8,rootX=-.16+lane*.45,tipX=-.42+lane*.60;
    const lock=ribbon([
      [rootX,.955,.18],
      [rootX-.055,.79,.43],
      [tipX*.82,.51,.59],
      [tipX,.17-Math.abs(lane)*.075,.575]
    ],.14+(i%3)*.018,mats.hairCard,i%4?'#352a33':'#44343d',{rows:26,cols:5,taper:.62,flare:.10});
    lock.name='hair-v3-fringe';root.add(lock);
  }
  for(const side of [-1,1])for(let i=0;i<6;i++){
    const x=side*(.44+i*.024),tip=side*(.55+i*.035);
    const lock=ribbon([[x,.74,.39],[side*.58,.39,.51],[tip,-.08,.44],[side*(.59+i*.038),-.78-i*.105,.27]],.15,mats.hairCard,'#342a32',{rows:27,cols:5,taper:.57});
    lock.name='hair-v3-face-lock';root.add(lock);
  }
}

function addBackAndPony(root,mats,flowing){
  for(const side of [-1,1])for(let i=0;i<5;i++){
    root.add(ribbon([[side*(.18+i*.065),.80,-.28],[side*(.34+i*.055),.49,-.50],[side*(.39+i*.05),.05,-.48],[side*(.34+i*.055),-.55-i*.09,-.31]],.17,mats.hair,'#2c242d',{rows:24,cols:5,taper:.52}));
  }
  const tie=[0,.72,-.69];
  for(let i=0;i<14;i++){
    const lane=(i-6.5)/6.5;
    root.add(ribbon([[lane*.40,.90,-.14],[lane*.34,.80,-.42],[lane*.18,.73,-.61],tie],.16,mats.hair,i%3?'#302630':'#3b2d37',{rows:18,cols:5,taper:.36,flare:.03}));
  }
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
