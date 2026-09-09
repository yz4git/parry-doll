'use strict';
// Key-art parry presentation: additive screen-space burst, cinematic camera push and hero rim.
(()=>{
 if(window.__parryCinematicV3Loaded)return;window.__parryCinematicV3Loaded=true;
 const baseCanvas=$('game'),fx=document.createElement('canvas');fx.id='parry-cinematic-v3';fx.setAttribute('aria-hidden','true');
 Object.assign(fx.style,{position:'fixed',inset:'0',width:'100%',height:'100%',pointerEvents:'none',zIndex:'7'});baseCanvas.parentNode.insertBefore(fx,baseCanvas.nextSibling);
 const c=fx.getContext('2d',{alpha:true});let dpr=1,last=performance.now(),beat=null;
 const clamp01=x=>Math.max(0,Math.min(1,x)),rand=(a,b)=>a+Math.random()*(b-a);
 function resize(){const nd=Math.min(devicePixelRatio||1,1.35),w=Math.max(1,Math.round(W*nd)),h=Math.max(1,Math.round(H*nd));if(fx.width!==w||fx.height!==h){fx.width=w;fx.height=h;dpr=nd}c.setTransform(dpr,0,0,dpr,0,0)}
 function contactPoint(){
  const hand=player?.nodes?.find(n=>n.name==='hand')?.p||player?.nodes?.[1]?.p||player?.pos||V();
  if(!boss?.nodes?.length)return {...hand};
  let best=boss.nodes[0].p,dist=Infinity;for(const n of boss.nodes){const q=sub(n.p,hand),dd=len(q);if(dd<dist){dist=dd;best=n.p}}
  return mul(add(hand,best),.5);
 }
 function makeBurst(point,perfect){
  const p2=project(point),cx=p2&&p2.z>.01?p2.x:W*.52,cy=p2&&p2.z>.01?p2.y:H*.50;
  const rays=[],sparks=[],streaks=[];
  for(let i=0;i<(perfect?46:34);i++){const a=rand(-Math.PI,Math.PI),bias=i%4===0?rand(-.18,.18):rand(-.8,.8);rays.push({a:a+bias,len:rand(65,perfect?245:180),w:rand(.7,perfect?4.1:3),delay:rand(0,.06),warm:Math.random()>.24})}
  for(let i=0;i<(perfect?34:26);i++){const a=rand(-Math.PI,Math.PI),sp=rand(90,perfect?330:240);sparks.push({a,sp,size:rand(1.2,4.5),life:rand(.18,.42),spin:rand(-8,8)})}
  const base=perfect?-.28:-.22;for(let i=0;i<4;i++)streaks.push({a:base+(i-1.5)*rand(.22,.38)+(i%2?1.55:0),offset:rand(-18,18),w:rand(2.5,perfect?9:6.8),len:rand(.45,.82)*Math.hypot(W,H)});
  beat={point:{...point},cx,cy,perfect,life:perfect?.48:.37,max:perfect?.48:.37,rays,sparks,streaks};
  hitstop=Math.max(hitstop,perfect?.158:.126);shake=Math.max(shake,perfect?.72:.56);
  if(typeof feel==='object'&&feel)feel.slow=Math.max(feel.slow||0,perfect?.18:.10);
 }
 function glowLine(x1,y1,x2,y2,color,w,a,blur=18){c.save();c.globalCompositeOperation='lighter';c.globalAlpha=a;c.strokeStyle=color;c.shadowColor=color;c.shadowBlur=blur;c.lineCap='round';c.lineWidth=w;c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.stroke();c.restore()}
 function draw(){
  resize();c.clearRect(0,0,W,H);if(!beat)return;
  const t=1-beat.life/beat.max,fade=Math.pow(1-t,.56),flash=clamp01((.18-t)/.18),p2=project(beat.point),cx=p2&&p2.z>.01?p2.x:beat.cx,cy=p2&&p2.z>.01?p2.y:beat.cy;
  // Brief exposure lift plus darker edges makes the clash read like a promo-frame photograph.
  c.save();const vign=c.createRadialGradient(cx,cy,35,cx,cy,Math.max(W,H)*.78);vign.addColorStop(0,'rgba(0,0,0,0)');vign.addColorStop(.50,`rgba(4,7,12,${.06*fade})`);vign.addColorStop(1,`rgba(0,0,0,${.38*fade})`);c.fillStyle=vign;c.fillRect(0,0,W,H);c.restore();
  if(flash>0){c.save();c.globalCompositeOperation='screen';c.globalAlpha=(beat.perfect?.36:.27)*flash;c.fillStyle='#fff9e9';c.fillRect(0,0,W,H);c.restore()}
  const coreR=(beat.perfect?118:96)*(1+t*.62);c.save();c.globalCompositeOperation='lighter';const g=c.createRadialGradient(cx,cy,0,cx,cy,coreR);g.addColorStop(0,`rgba(255,255,255,${.86*fade})`);g.addColorStop(.08,`rgba(255,239,190,${.65*fade})`);g.addColorStop(.34,`rgba(255,176,72,${.28*fade})`);g.addColorStop(.68,`rgba(112,222,255,${.12*fade})`);g.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=g;c.fillRect(cx-coreR,cy-coreR,coreR*2,coreR*2);c.restore();
  for(const s of beat.streaks){const cs=Math.cos(s.a),sn=Math.sin(s.a),px=cx-sn*s.offset,py=cy+cs*s.offset,l=s.len*(.5+.5*Math.sin(Math.min(1,t*1.7)*Math.PI*.72));glowLine(px-cs*l*.52,py-sn*l*.52,px+cs*l*.48,py+sn*l*.48,'#ffffff',s.w,fade*.70,s.w*4.2);glowLine(px-cs*l*.46,py-sn*l*.46,px+cs*l*.42,py+sn*l*.42,beat.perfect?'#ffd46a':'#bff7ff',s.w*2.0,fade*.25,s.w*6)}
  for(const r of beat.rays){if(t<r.delay)continue;const q=clamp01((t-r.delay)/(1-r.delay)),grow=Math.sin(Math.min(1,q)*Math.PI*.76),L=r.len*grow,cs=Math.cos(r.a),sn=Math.sin(r.a),a=fade*(1-q*.45);glowLine(cx+cs*8,cy+sn*8,cx+cs*L,cy+sn*L,r.warm?'#ffd073':'#d8fbff',r.w,a,r.w*4)}
  // Expanding double shock ring.
  for(let k=0;k<2;k++){const q=clamp01(t-k*.08);if(q<=0)continue;const r=(30+q*(beat.perfect?190:145))*(1+k*.18);c.save();c.globalCompositeOperation='lighter';c.globalAlpha=fade*(.58-k*.18);c.strokeStyle=k?'#9eefff':'#ffe099';c.lineWidth=Math.max(1,5*(1-q));c.shadowColor=c.strokeStyle;c.shadowBlur=18;c.beginPath();c.ellipse(cx,cy,r,r*.45,-.16,0,Math.PI*2);c.stroke();c.restore()}
  c.save();c.globalCompositeOperation='lighter';for(const s of beat.sparks){const q=Math.min(1,t/(s.life/beat.max)),dist=s.sp*t,ang=s.a+s.spin*t*.035,x=cx+Math.cos(ang)*dist,y=cy+Math.sin(ang)*dist+t*t*65;c.globalAlpha=fade*(1-q*.42);c.fillStyle=Math.random()>.38?'#fff4c7':'#ffad45';c.fillRect(x,y,s.size*(1-q*.55),s.size*(1-q*.55))}c.restore();
  // Readable but brief key-art title treatment.
  const textA=fade*clamp01((.34-t)/.12)*clamp01(t/.045);if(textA>0){c.save();c.globalAlpha=textA;c.textAlign='center';c.font=`600 ${beat.perfect?Math.max(21,Math.min(30,W*.032)):Math.max(19,Math.min(27,W*.029))}px system-ui,sans-serif`;c.letterSpacing='0.22em';c.shadowColor=beat.perfect?'#ffd36b':'#c9f7ff';c.shadowBlur=22;c.fillStyle='#ffffff';c.fillText('PARRY',cx,Math.min(H-72,cy+78));c.restore()}
 }
 const baseEnemyImpact=enemyImpact;enemyImpact=function(move=null){const bp=parries,bpf=perfects,p=contactPoint(),out=baseEnemyImpact(move);if(parries>bp)makeBurst(p,perfects>bpf);return out};
 const baseSetCamera=setCamera;setCamera=function(){baseSetCamera();if(!beat||!basis?.f)return;const phase=Math.sin(clamp01(1-beat.life/beat.max)*Math.PI),strength=(beat.perfect?.64:.46)*phase;camera=add(camera,mul(basis.f,strength));camera.y-=.07*phase;const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),u=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up:u}};
 const baseRender=render;render=function(){baseRender();const now=performance.now(),dt=Math.min(.05,Math.max(1/120,(now-last)/1000));last=now;draw();if(beat){beat.life=Math.max(0,beat.life-dt);if(beat.life<=0)beat=null}};
 const baseReset=reset;reset=function(l=0){beat=null;return baseReset(l)};
 window.parryCinematicV3Diagnostics=()=>beat?{active:true,perfect:beat.perfect,life:+beat.life.toFixed(3)}:{active:false};
})();
