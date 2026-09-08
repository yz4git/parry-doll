'use strict';
// Combat FX hierarchy: visual-only impact staging layered after the detailed WebGL renderer.
(()=>{
 const gameCanvas=$('game'),fxCanvas=document.createElement('canvas');
 fxCanvas.id='combat-fx-v2';fxCanvas.setAttribute('aria-hidden','true');
 Object.assign(fxCanvas.style,{position:'fixed',inset:'0',width:'100%',height:'100%',pointerEvents:'none',mixBlendMode:'normal'});
 gameCanvas.parentNode.insertBefore(fxCanvas,gameCanvas.nextSibling);
 const fctx=fxCanvas.getContext('2d',{alpha:true});
 let fxDpr=1,beats=[],parryAura=0,parryAuraPerfect=false,cameraPunch=0,lastBreakBoss=null;
 const rand=(a,b)=>a+Math.random()*(b-a),cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
 const vec=(x=0,y=0,z=0)=>({x,y,z}),vadd=(a,b)=>vec(a.x+b.x,a.y+b.y,a.z+b.z),vsub=(a,b)=>vec(a.x-b.x,a.y-b.y,a.z-b.z),vmul=(a,s)=>vec(a.x*s,a.y*s,a.z*s);
 const vlength=a=>Math.hypot(a.x,a.y,a.z),vnorm=a=>{const l=vlength(a)||1;return vmul(a,1/l)};
 const EFFECTS={
  hit1:{life:.18,flash:.11,glow:42,rays:9,rayLen:48,ring:.22,shake:.14,stop:.052,push:.035,color:'#baffed',core:'#ffffff'},
  hit2:{life:.21,flash:.15,glow:52,rays:12,rayLen:62,ring:.28,shake:.20,stop:.062,push:.055,color:'#a7fff0',core:'#ffffff'},
  hit3:{life:.29,flash:.24,glow:74,rays:20,rayLen:92,ring:.48,shake:.34,stop:.095,push:.12,color:'#8cffe8',core:'#ffffff'},
  parry:{life:.27,flash:.26,glow:78,rays:22,rayLen:90,ring:.55,shake:.38,stop:.092,push:.09,color:'#ffd36b',core:'#fff9d8'},
  perfect:{life:.34,flash:.42,glow:104,rays:30,rayLen:125,ring:.78,shake:.50,stop:.118,push:.15,color:'#ffd05d',core:'#ffffff'},
  counter:{life:.34,flash:.36,glow:96,rays:24,rayLen:122,ring:.62,shake:.52,stop:.118,push:.18,color:'#8dffe7',core:'#fffef1'},
  break:{life:.48,flash:.46,glow:118,rays:32,rayLen:145,ring:1.25,shake:.60,stop:.142,push:.23,color:'#ffd16b',core:'#fff8d4'},
  finish:{life:.66,flash:.72,glow:170,rays:42,rayLen:190,ring:1.70,shake:.78,stop:.185,push:.38,color:'#ffd07a',core:'#ffffff'},
  playerHit:{life:.24,flash:.12,glow:54,rays:10,rayLen:64,ring:.18,shake:.18,stop:.055,push:0,color:'#ff986f',core:'#ffe5d7'}
 };
 function resizeFx(){
  const d=Math.min(devicePixelRatio||1,1.5),w=Math.max(1,Math.round(W*d)),h=Math.max(1,Math.round(H*d));
  if(fxCanvas.width!==w||fxCanvas.height!==h){fxCanvas.width=w;fxCanvas.height=h;fxDpr=d}
  fctx.setTransform(fxDpr,0,0,fxDpr,0,0);
 }
 function screenDir(point,dir){
  const a=project(point),b=project(vadd(point,vmul(dir,1.2)));if(!a||!b||a.z<=.01||b.z<=.01)return {x:1,y:0};
  const dx=b.x-a.x,dy=b.y-a.y,l=Math.hypot(dx,dy)||1;return{x:dx/l,y:dy/l};
 }
 function moveSlashDir(move){
  const idx=Math.max(0,Math.min(2,move?.combo||0)),pose=COMBO_POSES[idx];if(!pose)return vnorm(vsub(boss.pos,player.pos));
  const local=vsub(pose.hit.blade,pose.ready.blade),c=Math.cos(player.face),sn=Math.sin(player.face);
  return vnorm(vec(local.x*c+local.z*sn,local.y,-local.x*sn+local.z*c));
 }
 function buildRays(count,len,dir2,spread=Math.PI*.95){
  const rays=[];const base=Math.atan2(dir2.y,dir2.x);
  for(let i=0;i<count;i++){
   const bias=i<count*.46?0:Math.PI,ang=base+bias+rand(-spread,spread),l=len*rand(.45,1.08),w=rand(.7,2.2);
   rays.push({ang,len:l,width:w,delay:rand(0,.06),warm:Math.random()>.35});
  }
  return rays;
 }
 function buildShards(count,dir2){
  const shards=[];const base=Math.atan2(dir2.y,dir2.x);
  for(let i=0;i<count;i++){const a=base+rand(-1.15,1.15),speed=rand(38,125);shards.push({a,speed,size:rand(2.5,6.5),spin:rand(-8,8)})}
  return shards;
 }
 function spawn(kind,point,dir=vec(0,1,0),opts={}){
  const spec=EFFECTS[kind]||EFFECTS.hit1,scale=feel?.reduced?.55:1,p={...point},dir3=vnorm(dir),d2=screenDir(p,dir3),max=spec.life*(feel?.reduced?.8:1);
  const beat={kind,p,dir:dir3,dir2:d2,life:max,max,spec:{...spec},rays:buildRays(Math.round(spec.rays*scale),spec.rayLen*scale,d2,kind==='finish'?.58:kind==='counter'?.72:1.05),shards:buildShards(Math.round((kind==='finish'?20:kind==='break'?15:kind==='hit3'?9:kind==='perfect'?12:4)*scale),d2)};
  beats.push(beat);if(beats.length>18)beats.splice(0,beats.length-18);
  shake=Math.max(shake,spec.shake*scale);hitstop=Math.max(hitstop,spec.stop*scale);cameraPunch=Math.max(cameraPunch,spec.push*scale);
  if(kind==='break')feel.slow=Math.max(feel.slow,feel.reduced?.06:.20);
  if(kind==='finish')feel.slow=Math.max(feel.slow,feel.reduced?.14:.46);
  if(kind==='perfect'){parryAura=Math.max(parryAura,.42);parryAuraPerfect=true}
  else if(kind==='parry'){parryAura=Math.max(parryAura,.30);parryAuraPerfect=false}
  const worldCount=Math.round((kind==='finish'?26:kind==='break'?20:kind==='perfect'?18:kind==='counter'?16:kind==='hit3'?12:7)*scale);
  for(let i=0;i<worldCount;i++){
   const lateral=vec(rand(-1,1),rand(-.35,1.2),rand(-1,1)),vel=vadd(vmul(dir3,rand(3,9)),vmul(vnorm(lateral),rand(2,10)));
   particles.push({p:{...p},v:vel,life:rand(.22,.52),max:.55,color:i%3===0?spec.core:spec.color});
  }
  if(particles.length>260)particles.splice(0,particles.length-260);
  return beat;
 }
 function impactPointForMove(move){
  if(!boss?.nodes?.length)return boss?.pos||vec();
  if(move?.combo===1)return boss.nodes.find(n=>n.name==='head')?.p||boss.nodes[2]?.p||boss.nodes[1].p;
  if(move?.combo===2)return boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1].p;
  return boss.nodes.find(n=>n.name==='shoulder')?.p||boss.nodes[1].p;
 }
 function parryContact(){
  const hand=player.nodes.find(n=>n.name==='hand')?.p||player.nodes[1].p;
  if(boss.spec.type==='human'){const enemyHand=boss.nodes.find(n=>n.name==='hand')?.p||boss.nodes[1].p;const q=vmul(vadd(hand,enemyHand),.5);q.y+=.18*Math.min(1.4,boss.spec.scale);return q}
  let best=boss.nodes[0]?.p||boss.pos,dist=Infinity;for(const n of boss.nodes){const d=vlength(vsub(n.p,hand));if(d<dist){dist=d;best=n.p}}return vmul(vadd(hand,best),.5);
 }
 function drawLineGlow(x1,y1,x2,y2,color,width,alpha){
  fctx.save();fctx.globalCompositeOperation='lighter';fctx.globalAlpha=alpha;fctx.strokeStyle=color;fctx.lineCap='round';fctx.shadowColor=color;fctx.shadowBlur=width*4;fctx.lineWidth=width;fctx.beginPath();fctx.moveTo(x1,y1);fctx.lineTo(x2,y2);fctx.stroke();fctx.restore();
 }
 function drawShockwave(beat,p2,t,alpha){
  if(beat.spec.ring<=0)return;const r=beat.spec.ring*(.25+t*.95),cx=p2.x,cy=p2.y;
  const px=project(vadd(beat.p,vec(r,0,0))),pz=project(vadd(beat.p,vec(0,0,r)));if(!px||!pz||px.z<=0||pz.z<=0)return;
  const rx=Math.max(8,Math.abs(px.x-cx)),ry=Math.max(4,Math.abs(pz.y-cy));
  fctx.save();fctx.globalCompositeOperation='lighter';fctx.globalAlpha=alpha*.72;fctx.strokeStyle=beat.spec.color;fctx.lineWidth=Math.max(1,4*(1-t));fctx.shadowColor=beat.spec.color;fctx.shadowBlur=16*(1-t);fctx.beginPath();fctx.ellipse(cx,cy,rx,ry,0,0,Math.PI*2);fctx.stroke();fctx.restore();
 }
 function drawPlayerParryAura(alpha){
  if(parryAura<=0||!player?.links)return;
  fctx.save();fctx.globalCompositeOperation='lighter';fctx.lineCap='round';
  const phase=cl(parryAura/.42),gold=parryAuraPerfect?'#ffe18b':'#b4fff1';
  for(const l of player.links){const a=project(player.nodes[l.a].p),b=project(player.nodes[l.b].p);if(!a||!b||a.z<=.05||b.z<=.05)continue;fctx.globalAlpha=.18+.54*phase;fctx.strokeStyle=gold;fctx.shadowColor=gold;fctx.shadowBlur=10+18*phase;fctx.lineWidth=Math.max(1.1,l.r*19*phase);fctx.beginPath();fctx.moveTo(a.x,a.y);fctx.lineTo(b.x,b.y);fctx.stroke()}
  const hand=player.nodes.find(n=>n.name==='hand');if(hand){const h=project(hand.p);if(h?.z>0){const g=fctx.createRadialGradient(h.x,h.y,0,h.x,h.y,42*phase);g.addColorStop(0,'rgba(255,249,211,.9)');g.addColorStop(.28,parryAuraPerfect?'rgba(255,209,91,.52)':'rgba(139,255,234,.52)');g.addColorStop(1,'rgba(0,0,0,0)');fctx.globalAlpha=.9;fctx.fillStyle=g;fctx.fillRect(h.x-45,h.y-45,90,90)}}
  fctx.restore();
 }
 function drawBeat(beat){
  const p2=project(beat.p);if(!p2||p2.z<=.01)return;const t=1-beat.life/beat.max,fade=Math.pow(1-t,.58),spec=beat.spec;
  fctx.save();fctx.globalCompositeOperation='lighter';const radius=spec.glow*(.52+t*.62);const g=fctx.createRadialGradient(p2.x,p2.y,0,p2.x,p2.y,radius);g.addColorStop(0,`rgba(255,255,255,${cl(spec.flash*fade*1.75)})`);g.addColorStop(.13,beat.kind==='counter'?'rgba(142,255,233,.72)':beat.kind==='playerHit'?'rgba(255,117,82,.58)':'rgba(255,206,92,.70)');g.addColorStop(.48,beat.kind==='hit1'||beat.kind==='hit2'||beat.kind==='hit3'?'rgba(118,255,231,.20)':'rgba(255,171,63,.16)');g.addColorStop(1,'rgba(0,0,0,0)');fctx.fillStyle=g;fctx.fillRect(p2.x-radius,p2.y-radius,radius*2,radius*2);fctx.restore();
  for(const r of beat.rays){const local=t-r.delay;if(local<=0)continue;const q=cl(local/(1-r.delay)),grow=Math.sin(Math.min(1,q)*Math.PI*.72),len=r.len*grow,cs=Math.cos(r.ang),sn=Math.sin(r.ang),start=4+len*.08,end=len,alpha=fade*(1-q*.52);drawLineGlow(p2.x+cs*start,p2.y+sn*start,p2.x+cs*end,p2.y+sn*end,r.warm?spec.color:spec.core,r.width,alpha)}
  if(beat.kind==='parry'||beat.kind==='perfect'){
   const L=beat.kind==='perfect'?118:86,alpha=fade*(beat.kind==='perfect'?.96:.76);drawLineGlow(p2.x-L,p2.y,p2.x+L,p2.y,spec.core,beat.kind==='perfect'?5.8:4.2,alpha);drawLineGlow(p2.x,p2.y-L*.66,p2.x,p2.y+L*.66,spec.color,beat.kind==='perfect'?6.8:4.8,alpha*.78);
  }
  if(beat.kind==='break'){
   for(let k=0;k<3;k++){const rr=(.30+k*.22)+t*(.68+k*.18),fake={...beat,spec:{...spec,ring:rr}};drawShockwave(fake,p2,cl(t+k*.07),fade*(1-k*.18))}
   drawLineGlow(p2.x,p2.y-92*(1-t),p2.x,p2.y+72*(1-t),spec.core,5.2,fade*.72);
  }
  if(!['parry','perfect','break','playerHit'].includes(beat.kind)){
   const d=beat.dir2,perp={x:-d.y,y:d.x},len=beat.kind==='finish'?Math.min(W,H)*.70:beat.kind==='counter'?Math.min(W,H)*.58:beat.kind==='hit3'?Math.min(W,H)*.46:Math.min(W,H)*.18;
   const width=beat.kind==='finish'?8:beat.kind==='counter'?7.2:beat.kind==='hit3'?6.2:2.4,alpha=fade*(beat.kind==='hit1'?.52:.78);
   drawLineGlow(p2.x-d.x*len*.45,p2.y-d.y*len*.45,p2.x+d.x*len*.55,p2.y+d.y*len*.55,spec.core,width,alpha);
   if(beat.kind==='finish'||beat.kind==='counter'||beat.kind==='hit3')drawLineGlow(p2.x-d.x*len*.34+perp.x*6,p2.y-d.y*len*.34+perp.y*6,p2.x+d.x*len*.44+perp.x*6,p2.y+d.y*len*.44+perp.y*6,spec.color,width*2.05,alpha*.42);
  }
  drawShockwave(beat,p2,t,fade);
  fctx.save();fctx.globalCompositeOperation='lighter';for(const s of beat.shards){const dist=s.speed*t,ang=s.a+s.spin*t*.06,x=p2.x+Math.cos(ang)*dist,y=p2.y+Math.sin(ang)*dist+t*t*28;fctx.globalAlpha=fade*.75;fctx.fillStyle=spec.color;fctx.beginPath();fctx.moveTo(x,y-s.size);fctx.lineTo(x+s.size*.55,y+s.size*.65);fctx.lineTo(x-s.size*.35,y+s.size*.3);fctx.closePath();fctx.fill()}fctx.restore();
 }
 function drawScreenGrade(){
  let dark=0,white=0,warm=0;
  for(const b of beats){const phase=b.life/b.max;if(b.kind==='finish'){dark=Math.max(dark,.30*phase);white=Math.max(white,.30*Math.sin((1-phase)*Math.PI));warm=Math.max(warm,.15*phase)}else if(b.kind==='break'){dark=Math.max(dark,.17*phase);white=Math.max(white,.10*phase)}else if(b.kind==='perfect'){white=Math.max(white,.16*phase);warm=Math.max(warm,.08*phase)}}
  if(dark>0){fctx.save();fctx.globalAlpha=dark;fctx.fillStyle='#020609';fctx.fillRect(0,0,W,H);fctx.restore()}
  if(warm>0){fctx.save();fctx.globalCompositeOperation='screen';fctx.globalAlpha=warm;fctx.fillStyle='#8b4b18';fctx.fillRect(0,0,W,H);fctx.restore()}
  if(white>0){fctx.save();fctx.globalCompositeOperation='screen';fctx.globalAlpha=white;fctx.fillStyle='#fff7df';fctx.fillRect(0,0,W,H);fctx.restore()}
 }
 const fxResolveSwingBase=resolveSwing;
 resolveSwing=function(){
  const move=player.swing?{...player.swing}:null,beforeHP=boss?.hp||0,point=move?{...impactPointForMove(move)}:null,dir=move?moveSlashDir(move):(boss&&player?vnorm(vsub(boss.pos,player.pos)):vec(0,0,-1));
  const out=fxResolveSwingBase();
  if(move&&point&&beforeHP>0&&boss.hp<beforeHP){const kind=move.finisher?'finish':move.counter?'counter':move.combo===2?'hit3':move.combo===1?'hit2':'hit1';spawn(kind,point,dir)}
  return out;
 };
 const fxEnemyImpactBase=enemyImpact;
 enemyImpact=function(move=null){
  const beforeP=parries,beforePerfect=perfects,contact=player&&boss?parryContact():vec();const incoming=player&&boss?vnorm(vsub(player.pos,boss.pos)):vec(0,0,1),out=fxEnemyImpactBase(move);
  if(parries>beforeP)spawn(perfects>beforePerfect?'perfect':'parry',contact,incoming);
  return out;
 };
 const fxHurtBase=hurt;
 hurt=function(d,amount,force,point){const before=d?.hp||0,out=fxHurtBase(d,amount,force,point);if(out&&d===player&&before>player.hp)spawn('playerHit',point,vnorm(force));return out};
 const fxStepBase=step;
 step=function(dt){
  const beforeBoss=boss,beforeBroken=boss?.broken||0;fxStepBase(dt);
  if(mode==='play'&&boss&&boss===beforeBoss&&beforeBroken<=0&&boss.broken>0){const p=boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1].p;spawn('break',p,vnorm(vsub(boss.pos,player.pos)));lastBreakBoss=boss}
 };
 const fxSetCameraBase=setCamera;
 setCamera=function(){fxSetCameraBase();if(cameraPunch>0&&basis?.f){camera=vadd(camera,vmul(basis.f,cameraPunch));const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),u=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up:u}}};
 const fxRenderBase=render;
 let fxLast=performance.now();
 render=function(){
  fxRenderBase();resizeFx();const now=performance.now(),dt=Math.min(.05,Math.max(1/120,(now-fxLast)/1000));fxLast=now;
  fctx.clearRect(0,0,W,H);drawScreenGrade();for(const b of beats)drawBeat(b);drawPlayerParryAura();
  beats.forEach(b=>b.life=Math.max(0,b.life-dt));beats=beats.filter(b=>b.life>0);parryAura=Math.max(0,parryAura-dt);cameraPunch=Math.max(0,cameraPunch-dt*2.8);
 };
 const fxResetBase=reset;
 reset=function(l=0){beats=[];parryAura=0;parryAuraPerfect=false;cameraPunch=0;lastBreakBoss=null;return fxResetBase(l)};
 window.parryFxDiagnostics=()=>({active:beats.map(b=>b.kind),parryAura:+parryAura.toFixed(3),cameraPunch:+cameraPunch.toFixed(3)});
})();
