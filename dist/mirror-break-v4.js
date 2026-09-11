'use strict';
// MIRROR BREAK v4 — persistent visible severing/shattering without changing the ragdoll physics graph.
(()=>{
 if(window.__parryMirrorBreakV4Loaded)return;window.__parryMirrorBreakV4Loaded=true;
 const state=window.__mirrorBreakState;if(!state)return;
 const s={bossRef:null,lastBroken:false,debris:[],severs:0,lastPlan:null};
 window.__mirrorBreakV4State=s;
 const partNode=()=>{
  if(!boss||!state.part)return null;
  const list=boss.nodes.filter(n=>n.name===state.part.node);if(!list.length)return boss.nodes[1]||boss.nodes[0];
  if(state.part.kind==='LEG'&&list.length>1)return list.reduce((a,n)=>n.rest.z>a.rest.z?n:a,list[0]);
  return list[list.length-1];
 };
 function plan(d=boss){
  if(!d||!state.broken||state.boss!==d||!state.part)return null;
  const target=partNode();if(!target)return null;const targetIndex=d.nodes.indexOf(target),hidden=new Set(),kind=state.part.kind;
  let anchor=null,branch=target;
  if(kind==='ARM'){
   hidden.add(targetIndex);const handParent=d.links.find(l=>l.b===targetIndex||l.a===targetIndex);const elbowIndex=handParent?(handParent.a===targetIndex?handParent.b:handParent.a):-1;
   if(elbowIndex>=0){hidden.add(elbowIndex);const parent=d.links.find(l=>(l.a===elbowIndex&&!hidden.has(l.b))||(l.b===elbowIndex&&!hidden.has(l.a)));if(parent){const ai=parent.a===elbowIndex?parent.b:parent.a;anchor=d.nodes[ai]}}
  }else if(kind==='LEG'){
   hidden.add(targetIndex);const footLink=d.links.find(l=>l.a===targetIndex||l.b===targetIndex);let footIndex=-1;if(footLink){const oi=footLink.a===targetIndex?footLink.b:footLink.a;if(d.nodes[oi]?.name==='foot'){footIndex=oi;hidden.add(oi)}}
   const rootLink=d.links.find(l=>(l.a===targetIndex&&!hidden.has(l.b))||(l.b===targetIndex&&!hidden.has(l.a)));if(rootLink){const ai=rootLink.a===targetIndex?rootLink.b:rootLink.a;anchor=d.nodes[ai]}
   if(footIndex>=0)branch=d.nodes[footIndex];
  }else if(kind==='CORE')anchor=d.nodes.find(n=>n.name==='chest')||target;
  if(!anchor&&kind!=='CORE'){
   const link=d.links.find(l=>(hidden.has(l.a)&&!hidden.has(l.b))||(hidden.has(l.b)&&!hidden.has(l.a)));if(link)anchor=d.nodes[hidden.has(link.a)?link.b:link.a];
  }
  return{kind,target,targetIndex,hidden,anchor,branch,label:state.part.label||kind,level};
 }
 function stumpPoint(p){if(!p?.anchor||!p.target)return p?.anchor?.p||p?.target?.p||boss?.pos||V();return add(p.anchor.p,mul(sub(p.target.p,p.anchor.p),p.kind==='ARM'?.31:.26))}
 function addCrack(q,r,alpha=.8){const p=project(q);if(p.z<=.25)return;shapes.push({depth:p.z-.64,draw(){ctx.save();ctx.strokeStyle=`rgba(255,174,112,${alpha})`;ctx.lineWidth=Math.max(1,p.s*.012);for(let i=0;i<5;i++){const a=i*Math.PI*.4+.22,rr=r*p.s*(i%2?.72:1);ctx.beginPath();ctx.moveTo(p.x+Math.cos(a)*rr*.12,p.y+Math.sin(a)*rr*.12);ctx.lineTo(p.x+Math.cos(a)*rr,p.y+Math.sin(a)*rr);ctx.stroke()}ctx.restore()}})}
 function drawDamage(p){
  if(!p)return;
  if(p.kind==='CORE'){
   const c=p.anchor?.p||p.target.p,sc=boss.spec.scale;orb(c,.24*sc,'#241b1c');orb(add(c,boss.local(V(0,0,.035*sc))),.12*sc,'#ffd08a');addCrack(c,.46*sc,.92);return;
  }
  const q=stumpPoint(p),sc=boss.spec.scale;segment(p.anchor?.p||q,q,p.kind==='ARM'?.105*sc:.09*sc,'#4a2927');orb(q,.105*sc,'#5b2c27');orb(add(q,boss.local(V(0,0,.022*sc))),.058*sc,'#ffb16f');addCrack(q,.16*sc,.7);
 }
 function drawDebris(){
  for(const f of s.debris){if(f.life<=0)continue;const a=clamp(f.life/f.max,0,1),col=f.weapon?'#dfbf76':f.heavy?'#9d7658':'#c48c68';if(f.weapon){segment(f.p,add(f.p,f.axis),f.r,col);orb(f.p,f.r*.9,'#57473a')}else{orb(f.p,f.r,col);if(f.heavy)addCrack(f.p,f.r*2.2,Math.min(.72,a))}}
 }
 function spawnSever(){
  const p=plan();if(!p)return;s.lastPlan=p;s.severs++;const origin=p.kind==='CORE'?(p.anchor?.p||p.target.p):(p.branch?.p||p.target.p),sc=boss.spec.scale,count=p.kind==='CORE'?8:p.level===3?7:5;
  for(let i=0;i<count;i++){const outward=boss.local(V((Math.random()-.5)*(p.kind==='LEG'?4.5:5.8),3.2+Math.random()*5.5,(Math.random()-.5)*5.2));s.debris.push({p:{...origin},v:outward,r:(.05+Math.random()*.07)*sc,life:3.2+Math.random()*1.3,max:4.5,heavy:p.level===3||p.kind==='CORE'})}
  if(p.kind==='ARM'){const axis=boss.local(V(0,.02,-.72*sc));s.debris.push({p:{...origin},v:boss.local(V((Math.random()-.5)*3.4,5.4,2.2)),axis,r:.045*sc,life:5.2,max:5.2,weapon:true,heavy:p.level===3})}
  if(s.debris.length>22)s.debris.splice(0,s.debris.length-22);
 }
 function updateDebris(dt){for(const f of s.debris){if(f.life<=0)continue;f.life=Math.max(0,f.life-dt);f.v.y-=13*dt;f.p=add(f.p,mul(f.v,dt));const floor=f.r*.85;if(f.p.y<floor){f.p.y=floor;if(f.v.y<0)f.v.y*=-.26;f.v.x*=.72;f.v.z*=.72}f.axis=f.weapon?add(mul(f.axis,.995),V(Math.sin(time*7)*.0005,0,Math.cos(time*5)*.0005)):f.axis}while(s.debris.length&&s.debris[0].life<=0)s.debris.shift()}
 function syncBreak(){
  if(boss!==s.bossRef){s.bossRef=boss;s.lastBroken=false;s.debris=[];s.lastPlan=null}
  const now=!!(state.broken&&state.boss===boss);if(now&&!s.lastBroken)spawnSever();s.lastBroken=now;
  if(now){const hud=document.getElementById('mbBreakHud'),span=hud?.querySelector('span');if(span)span.textContent=state.part?.kind==='CORE'?'CORE SHATTERED':'PART SEVERED'}
 }
 const baseDrawDoll=drawDoll;drawDoll=function(d){
  if(d!==boss||!state.broken||state.boss!==boss){baseDrawDoll(d);return}
  const p=plan(d);if(!p){baseDrawDoll(d);return}
  const oldLinks=d.links,oldType=d.spec.type,saved=[];for(const i of p.hidden){const n=d.nodes[i];if(n){saved.push([n,n.r]);n.r=.001}}
  if(p.hidden.size)d.links=oldLinks.filter(l=>!p.hidden.has(l.a)&&!p.hidden.has(l.b));if(p.kind==='ARM'&&oldType==='human')d.spec.type='broken-human';
  if(p.kind==='CORE'&&p.target){saved.push([p.target,p.target.r]);p.target.r*=.62}
  try{baseDrawDoll(d)}finally{d.links=oldLinks;d.spec.type=oldType;for(const [n,r] of saved)n.r=r}
  drawDamage(p);drawDebris();
 };
 const baseResolveSwing=resolveSwing;resolveSwing=function(){const out=baseResolveSwing();syncBreak();return out};
 const baseStep=step;step=function(dt){const out=baseStep(dt);syncBreak();updateDebris(dt);return out};
 const baseReset=reset;reset=function(l=0){const out=baseReset(l);s.bossRef=boss;s.lastBroken=false;s.debris=[];s.lastPlan=null;return out};
 const priorDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=priorDiag?priorDiag():{},p=plan();return{...d,v4:true,visibleSever:!!p,visualBreakKind:p?.kind||null,hiddenNodes:p?[...p.hidden].map(i=>boss.nodes[i]?.name||String(i)):[],breakDebris:s.debris.filter(x=>x.life>0).length,severs:s.severs,persistentDamage:true}};
 syncBreak();
})();