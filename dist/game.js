'use strict';
// Dependency-free 3D projection + fixed-step active position-based ragdolls.
const $=id=>document.getElementById(id),canvas=$('game'),ctx=canvas.getContext('2d');
const V=(x=0,y=0,z=0)=>({x,y,z}),add=(a,b)=>V(a.x+b.x,a.y+b.y,a.z+b.z),sub=(a,b)=>V(a.x-b.x,a.y-b.y,a.z-b.z),mul=(a,s)=>V(a.x*s,a.y*s,a.z*s),len=a=>Math.hypot(a.x,a.y,a.z),norm=a=>mul(a,1/(len(a)||1)),clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const bosses=[{name:'灰の剣士',sub:'ASHEN DUELIST',type:'human',scale:1.15,hp:135,color:'#bd6449',speed:2.2,damage:12,wind:1.0,attackName:'連ね斬り'},{name:'鎖骨の獣',sub:'THE HOLLOW HOUND',type:'beast',scale:1.3,hp:175,color:'#859eac',speed:3.1,damage:14,wind:.88,attackName:'牙の突進'},{name:'糸なき蜘蛛',sub:'THE THREADLESS',type:'spider',scale:1.2,hp:210,color:'#a090be',speed:2.0,damage:15,wind:.82,attackName:'八脚薙ぎ'},{name:'鐘楼の巨人',sub:'BELL TOWER COLOSSUS',type:'human',scale:2.15,hp:290,color:'#ba975a',speed:1.45,damage:22,wind:1.15,attackName:'鐘砕き'}];
let W=1,H=1,DPR=1,time=0,mode='title',level=0,player,boss,particles=[],rings=[],shapes=[],shake=0,hitstop=0,toastT=0,combo=0,parries=0,perfects=0,elapsed=0,muted=false,audio=null,camera=V(0,12,18),target=V(0,1,0),last=0,acc=0,attackQueued=false,parryQueued=false;
let attackBuffer=0,parryBuffer=0;
const MOVES=[{duration:.38,wind:.09,recover:.27,damage:13,force:13,lunge:4.8},{duration:.4,wind:.10,recover:.29,damage:15,force:17,lunge:5.4},{duration:.52,wind:.15,recover:.43,damage:25,force:32,lunge:6.2}];
const keys=new Set(),input={x:0,z:0,id:null};
function resize(){W=innerWidth;H=innerHeight;DPR=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(W*DPR);canvas.height=Math.round(H*DPR);ctx.setTransform(DPR,0,0,DPR,0,0)}
addEventListener('resize',resize);resize();
function sound(f=440,d=.1,type='triangle',volume=.05){if(muted||!audio)return;const o=audio.createOscillator(),g=audio.createGain();o.type=type;o.frequency.setValueAtTime(f,audio.currentTime);o.frequency.exponentialRampToValueAtTime(Math.max(40,f*.35),audio.currentTime+d);g.gain.setValueAtTime(volume,audio.currentTime);g.gain.exponentialRampToValueAtTime(.001,audio.currentTime+d);o.connect(g);g.connect(audio.destination);o.start();o.stop(audio.currentTime+d)}
function announce(t,d=1.2){$('toast').textContent=t;toastT=d}
// Presentation advances in real time, even during hit stop.
const feel={impacts:[],slashes:[],zoom:0,slow:0,flash:0,pulse:0,damage:0,reduced:false,clock:0,dt:1/60};
function combatSound(kind){
 if(muted||!audio)return;
 const heavy=kind==='finish'||kind==='break';
 sound(heavy?70:kind==='parry'?1560:115,heavy?.42:.18,kind==='parry'?'triangle':'sine',heavy?.10:.065);
 if(kind==='parry'){sound(2350,.24,'sine',.035);sound(3200,.14,'sine',.018)}
 const duration=heavy?.28:kind==='parry'?.12:.085,buffer=audio.createBuffer(1,Math.ceil(audio.sampleRate*duration),audio.sampleRate),data=buffer.getChannelData(0);
 for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*Math.pow(1-i/data.length,2);
 const source=audio.createBufferSource(),filter=audio.createBiquadFilter(),gain=audio.createGain();
 source.buffer=buffer;filter.type='highpass';filter.frequency.value=kind==='parry'?2400:heavy?180:700;gain.gain.value=heavy?.13:.065;
 source.connect(filter);filter.connect(gain);gain.connect(audio.destination);source.start();source.onended=()=>{source.disconnect();filter.disconnect();gain.disconnect()};
}
function impact(p,kind='hit',power=1){
 feel.impacts.push({p:{...p},kind,power,life:.32,max:.32,seed:Math.random()*6.28});
 if(feel.impacts.length>12)feel.impacts.shift();
 feel.zoom=Math.max(feel.zoom,kind==='finish'?.9:kind==='parry'?.48:.16*power);
 feel.flash=Math.max(feel.flash,kind==='finish'?.19:kind==='parry'?.13:.04);
 if(kind==='finish'){feel.slow=.5;feel.pulse=.7}else if(kind==='break'){feel.slow=.25;feel.pulse=.5}
 combatSound(kind);
}
function slash(d,move){
 feel.slashes.push({p:add(d.pos,V(0,1.35*d.spec.scale,0)),face:d.face,combo:move.combo||0,radius:2.1*d.spec.scale,life:.2,max:.2,color:move.counter?'#adffed':d.player?'#c6fff1':'#ffb66e'});
 if(feel.slashes.length>8)feel.slashes.shift();
}
function updateFeel(dt){
 feel.dt=dt;feel.clock+=dt;
 for(const key of ['slow','flash','pulse','damage'])feel[key]=Math.max(0,feel[key]-dt);
 feel.zoom*=Math.exp(-dt*6);shake=Math.max(0,shake-dt*1.8);
 for(const list of [feel.impacts,feel.slashes]){for(const f of list)f.life-=dt;while(list.length&&list[0].life<=0)list.shift()}
}
function drawFeel(){
 ctx.save();ctx.globalCompositeOperation='lighter';
 for(const f of feel.slashes){
  ctx.globalAlpha=clamp(f.life/f.max,0,1)*.7;const t=1-f.life/f.max;
  for(let band=0;band<3;band++){const points=[];for(let k=0;k<=18;k++){const a=f.face+(k/18-.5)*2.5+(f.combo===1?-t:t)*.6,r=f.radius-band*.13;points.push(project(add(f.p,V(Math.sin(a)*r,Math.sin(k/18*Math.PI)*.35,Math.cos(a)*r))))}
   ctx.beginPath();points.forEach((q,i)=>i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y));ctx.strokeStyle=f.color;ctx.lineWidth=band===0?3:1;ctx.stroke();}
 }
 for(const f of feel.impacts){const q=project(f.p);if(q.z<=0)continue;const t=1-f.life/f.max,r=q.s*(.2+t*1.6)*f.power;
  ctx.globalAlpha=(1-t)*.85;ctx.strokeStyle=f.kind==='parry'?'#ffe1a1':f.kind==='finish'?'#ffbd64':'#baffed';
  for(let i=0;i<10;i++){const a=f.seed+i*Math.PI/5,rr=r*(i%2?.7:1.2);ctx.lineWidth=i%2?1:2;ctx.beginPath();ctx.moveTo(q.x+Math.cos(a)*rr*.28,q.y+Math.sin(a)*rr*.28);ctx.lineTo(q.x+Math.cos(a)*rr,q.y+Math.sin(a)*rr);ctx.stroke()}
  ctx.beginPath();ctx.ellipse(q.x,q.y,r*.7,r*.7,0,0,Math.PI*2);ctx.lineWidth=1.5;ctx.stroke();
 }
 ctx.restore();
 if(!feel.reduced&&feel.flash>0){ctx.fillStyle=`rgba(255,211,140,${Math.min(.10,feel.flash*.6)})`;ctx.fillRect(0,0,W,H)}
 if(feel.damage>0){ctx.strokeStyle=`rgba(193,62,43,${Math.min(.6,feel.damage)})`;ctx.lineWidth=14;ctx.strokeRect(0,0,W,H)}
}
class Doll{
 constructor(spec,isPlayer=false){this.spec=spec;this.player=isPlayer;this.pos=V(0,0,isPlayer?3:-3);this.vel=V();this.face=isPlayer?Math.PI:0;this.hp=spec.hp;this.posture=0;this.stun=0;this.down=0;this.invuln=0;this.attack=0;this.parry=0;this.cool=0;this.parryCool=0;this.ai=1.6;this.wind=0;this.strike=0;this.didHit=false;this.sequence=0;this.comboWindow=0;this.counter=0;this.broken=0;this.swing=null;this.swingClock=0;this.dash=0;this.recovery=1;this.airborne=false;this.impactCool=0;this.enraged=false;this.nodes=[];this.links=[];this.build();}
 node(name,p,r){this.nodes.push({name,rest:p,p:add(this.pos,p),prev:add(this.pos,p),r:r*this.spec.scale});return this.nodes.length-1}
 link(a,b,r){this.links.push({a,b,length:len(sub(this.nodes[a].rest,this.nodes[b].rest)),r:r*this.spec.scale})}
 build(){let s=this.spec.scale;const n=(name,x,y,z,r=.17)=>this.node(name,V(x*s,y*s,z*s),r),l=(a,b,r=.14)=>this.link(a,b,r);
 if(this.spec.type==='human'){n('hip',0,1.1,0,.24);n('chest',0,1.85,0,.34);n('head',0,2.4,0,.24);l(0,1,.29);l(1,2,.16);for(const side of [-1,1]){let a=n('shoulder',side*.46,1.9,0,.19),b=n('elbow',side*.72,1.4,.08),c=n(side===1?'hand':'offhand',side*.7,1.0,.2);l(1,a,.2);l(a,b);l(b,c,.12);let d=n('knee',side*.26,.6,.1),e=n('foot',side*.28,.16,.22,.18);l(0,d,.19);l(d,e,.15)}
 }else{n('hip',0,1.1,-.55,.38);n('chest',0,1.25,.5,.47);n('head',0,1.35,1.03,.3);l(0,1,.4);l(1,2,.23);const legs=this.spec.type==='spider'?4:2;for(let k=0;k<legs;k++)for(const side of [-1,1]){let z=-.8+k*1.6/(legs-1),a=n('knee',side*(this.spec.type==='spider'?1.25:.67),.9,z),b=n('foot',side*(this.spec.type==='spider'?1.7:.8),.13,z+.22,.16);l(k<legs/2?0:1,a,.13);l(a,b,.1)}}
 // Cross braces retain torso structure when motors release.
 }
 local(p){const c=Math.cos(this.face),s=Math.sin(this.face);return V(p.x*c+p.z*s,p.y,-p.x*s+p.z*c)}
 impulse(point,force){
  const heavy=len(force)>24,center=this.nodes[0].p;
  const sorted=this.nodes.map(n=>({n,d:len(sub(n.p,point))})).sort((a,b)=>a.d-b.d);
  for(let i=0;i<sorted.length;i++){
   const n=sorted[i].n,w=(heavy?.30:.035)+(i===0?.7:.2/(1+sorted[i].d));
   const offset=sub(n.p,center),spin=heavy?V(-offset.y*force.x*.10,(offset.x*force.x+offset.z*force.z)*.08,-offset.y*force.z*.10):V();
   n.prev=sub(n.prev,mul(add(mul(force,w),spin),1/60));
  }
  this.vel=add(this.vel,mul(force,heavy?.27:.15));
 }
 physics(dt){let speed=Math.hypot(this.vel.x,this.vel.z);const fallen=this.hp<=0||this.down>0;this.recovery=fallen?0:Math.min(1,this.recovery+dt*2.8);let motor=fallen?0:(this.stun>0?12:65)*(.18+.82*this.recovery);const attackPose=Math.sin(clamp(this.attack/(this.player?(this.swing?.duration||.42):.42),0,1)*Math.PI),walk=time*10;
 for(let i=0;i<this.nodes.length;i++){const n=this.nodes[i],rest={...n.rest};if(n.name==='foot'||n.name==='knee'){rest.z+=Math.sin(walk+(i%2)*Math.PI)*Math.min(speed*.09,.25);if(n.name==='foot')rest.y+=Math.max(0,Math.sin(walk+(i%2)*Math.PI))*.15*Math.min(speed,1)}if(n.name==='hand'){rest.z+=attackPose*1.4;rest.y+=attackPose*(this.player&&combo===2?1.1:.6);if(this.player)rest.x+=Math.sin((1-this.attack/.45)*Math.PI*2)*attackPose*(combo===1?-.8:.8);if(this.parry>0){rest.y+=.9;rest.z+=.6}}if(n.name==='offhand'&&this.parry>0){rest.y+=.65;rest.z+=.55}if(this.wind>0&&n.name==='hand'){rest.y+=1.1;rest.z-=.5}
 const goal=add(this.pos,this.local(rest));let velocity=mul(sub(n.p,n.prev),fallen?.987:.93);n.prev={...n.p};n.p=add(n.p,velocity);n.p.y-=18*dt*dt;if(motor){n.p=add(n.p,mul(sub(goal,n.p),Math.min(motor*dt*dt, .1)));n.p.y+=18*dt*dt*.85}}
 const fallingSpeed=(this.nodes[0].p.y-this.nodes[0].prev.y)/dt;
 for(let pass=0;pass<7;pass++){for(const l of this.links){const a=this.nodes[l.a],b=this.nodes[l.b],v=sub(b.p,a.p),d=len(v)||.001,c=mul(v,(d-l.length)/d*.5);a.p=add(a.p,c);b.p=sub(b.p,c)}for(const n of this.nodes){if(n.p.y<n.r){n.p.y=n.r;n.prev.x+=(n.p.x-n.prev.x)*.16;n.prev.z+=(n.p.z-n.prev.z)*.16}const rad=Math.hypot(n.p.x,n.p.z);if(rad>11.5){n.p.x*=11.5/rad;n.p.z*=11.5/rad}}}
 const hip=this.nodes[0];this.impactCool=Math.max(0,this.impactCool-dt);
 if(fallen){
  this.pos.x=hip.p.x;this.pos.z=hip.p.z;
  if(hip.p.y>hip.r+.55)this.airborne=true;
  if(this.airborne&&hip.p.y<hip.r+.16&&fallingSpeed<-1.4&&this.impactCool===0){
   this.airborne=false;this.impactCool=.55;groundImpact(hip.p,this.spec.scale);
  }
  if(Math.hypot(hip.p.x,hip.p.z)>11.15&&this.impactCool===0){
   this.impactCool=.65;groundImpact(hip.p,this.spec.scale);this.vel=mul(this.vel,-.22);
  }
 }
 }
}
function reset(l=0){level=l;player=new Doll({type:'human',scale:.85,hp:100,color:'#78c1bb'},true);boss=new Doll(bosses[l]);particles=[];rings=[];combo=-1;parries=0;perfects=0;elapsed=0;time=0;hitstop=0;feel.impacts=[];feel.slashes=[];feel.zoom=feel.slow=feel.flash=feel.pulse=feel.damage=0;clearInput();updateHUD()}
function begin(){if(!audio){try{audio=new (window.AudioContext||window.webkitAudioContext)()}catch{}}audio?.resume();if(mode==='paused'){mode='play'}else{reset(mode==='lost'?level:0);mode='play'}$('overlay').classList.add('hidden');sound(330,.3);}
$('start').onclick=begin;
function showOverlay(title,desc,button){$('title').textContent=title;$('description').textContent=desc;$('help').classList.add('hidden');$('start').innerHTML=button+' <span>→</span>';$('overlay').classList.remove('hidden')}
function pause(){if(mode==='play'){mode='paused';clearInput();showOverlay('PAUSED','ひと呼吸。戦いはここから。','戦いに戻る')}else if(mode==='paused')begin()}
$('motion').onclick=()=>{feel.reduced=!feel.reduced;$('motion').textContent=feel.reduced?'演出 控えめ':'演出 標準'};
$('pause').onclick=pause;$('sound').onclick=()=>{muted=!muted;$('sound').textContent=muted?'音 OFF':'音 ON'};
function clearInput(){keys.clear();input.x=input.z=0;input.id=null;attackQueued=parryQueued=false;attackBuffer=parryBuffer=0;$('knob').style.transform='';document.querySelectorAll('.pressed').forEach(e=>e.classList.remove('pressed'))}
addEventListener('blur',()=>{if(mode==='play')pause();clearInput()});document.addEventListener('visibilitychange',()=>{if(document.hidden&&mode==='play')pause()});
addEventListener('keydown',e=>{if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();keys.add(e.code);if(!e.repeat){if(e.code==='KeyJ'||e.code==='Space')attackQueued=true;if(e.code==='KeyK')parryQueued=true;if(e.code==='Escape')pause()}});addEventListener('keyup',e=>keys.delete(e.code));
const stick=$('stick');function moveStick(e){if(e.pointerId!==input.id)return;const r=stick.getBoundingClientRect(),dx=e.clientX-r.left-r.width/2,dz=e.clientY-r.top-r.height/2,d=Math.hypot(dx,dz),m=r.width*.35;input.x=dx/Math.max(m,d);input.z=dz/Math.max(m,d);$('knob').style.transform=`translate(${input.x*m}px,${input.z*m}px)`}
stick.onpointerdown=e=>{e.preventDefault();if(input.id!==null)return;input.id=e.pointerId;stick.setPointerCapture(e.pointerId);moveStick(e)};stick.onpointermove=moveStick;function endStick(e){if(e.pointerId===input.id){input.id=null;input.x=input.z=0;$('knob').style.transform=''}}stick.onpointerup=endStick;stick.onpointercancel=endStick;stick.onlostpointercapture=endStick;
for(const id of ['attack','parry']){const b=$(id);b.onpointerdown=e=>{e.preventDefault();b.setPointerCapture(e.pointerId);b.classList.add('pressed');if(id==='attack')attackQueued=true;else parryQueued=true};for(const event of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(event,()=>b.classList.remove('pressed'))}
function burst(p,color,count=24,power=6){for(let i=0;i<count;i++){const v=V((Math.random()-.5)*power,Math.random()*power,(Math.random()-.5)*power);particles.push({p:{...p},v,life:.35+Math.random()*.4,max:.75,color})}if(particles.length>260)particles.splice(0,particles.length-260)}
function ring(p,color){rings.push({p:{...p},life:.5,color})}
function groundImpact(p,power){
 burst(V(p.x,.12,p.z),'#a39e8b',Math.round(12+power*7),3.5+power);
 ring(V(p.x,.06,p.z),'#d4b98a');shake=Math.max(shake,Math.min(.3,power*.12));
 impact(V(p.x,.18,p.z),'ground',Math.min(1.7,power));
}
function hurt(d,amount,force,point){if(d.invuln>0||d.hp<=0)return false;d.hp=Math.max(0,d.hp-amount);d.invuln=d.player?.32:.12;d.stun=d.player?.22:.075;if(d.player){d.swing=null;d.attack=0;d.counter=0;}d.impulse(point,force);burst(point,d.player?'#8ce6df':'#edac73',18,5);shake=Math.max(shake,amount>=25?.25:.12);hitstop=amount>=25?.08:.042;impact(point,amount>=60?'finish':'hit',amount>=25?1.5:1);if(d.player)feel.damage=.5;if(len(force)>24){d.down=amount>=60?1.2:.85;d.stun=amount>=60?1.6:1.15}if(d.hp<=0){d.down=99;d.impulse(point,mul(force,1.8));d.wind=0;if(!d.player){impact(point,'finish',2.3);feel.slow=.65;groundImpact(d.pos,d.spec.scale)}announce(d.player?'敗 北':'討 伐',2.6);transition=2.7}return true}
let transition=0;
function playerAttack(){
 if(player.cool>0||player.down>0||player.hp<=0)return false;
 const finisher=boss.broken>0,counter=player.counter>0;
 combo=player.comboWindow>0?(combo+1)%3:0;
 const move=MOVES[combo];player.swing={...move,combo,finisher,counter};
 player.attack=finisher?.62:move.duration;player.swingClock=finisher?.17:move.wind;
 player.cool=finisher?.65:move.recover;player.comboWindow=.82;
 player.dash=.13;const v=sub(boss.pos,player.pos);player.face=Math.atan2(v.x,v.z);
 const distance=len(v),u=norm(v),stop=.9+boss.spec.scale*.5;
 const speed=Math.min(finisher?9:move.lunge,Math.max(0,(distance-stop)/.13));
 player.vel.x=u.x*speed;player.vel.z=u.z*speed;
 if(counter)player.counter=0;
 sound(220+combo*80,.12,'triangle',.04);
 return true;
}
function resolveSwing(){
 const move=player.swing;player.swing=null;
 if(!move||player.hp<=0||player.down>0||boss.hp<=0)return;
 slash(player,move);const v=sub(boss.pos,player.pos),distance=len(v),reach=2.15+boss.spec.scale*.55;
 if(distance>reach)return;
 const finisher=move.finisher&&boss.broken>0;
 const point=boss.nodes[move.combo===1?2:1].p;
 const force=mul(norm(v),finisher?55:move.counter?36:move.force);force.y=finisher?20:move.counter?12:move.combo===2?10:3;
 const damage=finisher?65:move.damage+(move.counter?14:0);
 if(hurt(boss,damage,force,point)){
  boss.posture+=finisher?0:move.counter?19:move.combo===2?15:8;
  if(finisher){boss.broken=0;boss.posture=0;announce('決 着 の 一 撃',1.2);ring(point,'#ffd287');hitstop=.15;shake=.5;sound(65,.5,'sawtooth',.1)}
  else if(move.counter){announce('弾 き 返 し',.7);ring(point,'#baffee');hitstop=.085;shake=.3;}
 }
}
function playerParry(){if(player.parryCool>0||player.down>0||player.hp<=0)return false;player.parry=.56;player.parryCool=.62;player.swing=null;player.attack=0;player.cool=Math.min(player.cool,.1);ring(player.nodes[1].p,'#8de7e0');sound(680,.1,'sine',.025);return true}
function enemyImpact(){if(boss.hp<=0||boss.stun>0||player.hp<=0)return;const v=sub(player.pos,boss.pos),distance=len(v);if(distance>2.5+boss.spec.scale*.8)return;
 if(player.parry>0){const perfect=player.parry>.22;parries++;if(perfect)perfects++;boss.posture+=perfect?32:24;boss.stun=.5;boss.wind=0;boss.strike=0;player.invuln=.28;player.counter=1.25;player.parryCool=.1;player.cool=0;const point=boss.nodes[2].p;boss.impulse(point,add(mul(norm(v),-15),V(0,6,0)));burst(player.nodes[1].p,'#ffde8e',45,10);ring(player.nodes[1].p,'#ffdf91');announce(perfect?'PERFECT PARRY':'PARRY',.65);shake=.28;hitstop=.075;impact(player.nodes[1].p,'parry',1.6);player.parry=0;
 }else{const force=add(mul(norm(v),boss.spec.scale>2?29:18),V(0,boss.spec.scale>2?11:5,0));hurt(player,boss.spec.damage,force,player.nodes[boss.sequence%2?2:1].p)}}
function updateHUD(){$('bossName').textContent=boss.spec.name;$('phase').textContent=boss.enraged?'覚醒':`0${level+1} / 04`;$('bossHP').style.width=100*boss.hp/boss.spec.hp+'%';$('posture').style.width=clamp(boss.posture,0,100)+'%';$('playerHP').style.width=player.hp+'%';$('stats').textContent=player.counter>0?'反撃チャンス！':`PARRY ${parries} · PERFECT ${perfects}`;$('round').textContent=boss.spec.sub;}
function step(dt){time+=dt;for(const d of [player,boss]){for(const k of ['invuln','stun','down','attack','parry','cool','parryCool','comboWindow','counter','broken','dash'])d[k]=Math.max(0,d[k]-dt)}if(mode==='play'){
 if(player.hp>0&&boss.hp>0){if(!boss.enraged&&boss.hp<=boss.spec.hp*.5){boss.enraged=true;ring(boss.pos,'#ff9564');announce('覚 醒 — '+boss.spec.attackName,1);combatSound('break')}if(attackQueued)attackBuffer=.24;if(parryQueued)parryBuffer=.18;attackQueued=parryQueued=false;
 attackBuffer=Math.max(0,attackBuffer-dt);parryBuffer=Math.max(0,parryBuffer-dt);
 if(parryBuffer>0&&playerParry()){parryBuffer=0;attackBuffer=0;}else if(attackBuffer>0&&playerAttack())attackBuffer=0;
 if(player.swing){player.swingClock-=dt;if(player.swingClock<=0)resolveSwing();}
 let x=input.x+(keys.has('KeyD')||keys.has('ArrowRight')?1:0)-(keys.has('KeyA')||keys.has('ArrowLeft')?1:0),z=input.z+(keys.has('KeyS')||keys.has('ArrowDown')?1:0)-(keys.has('KeyW')||keys.has('ArrowUp')?1:0);let magnitude=Math.max(1,Math.hypot(x,z));if(player.down===0&&player.stun===0&&player.dash===0){player.vel.x+=(x/magnitude*4.4-player.vel.x)*.2;player.vel.z+=(z/magnitude*4.4-player.vel.z)*.2;player.face=Math.atan2(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z)}
 let v=sub(player.pos,boss.pos),dist=len(v);if(boss.stun===0&&boss.down===0){boss.face=Math.atan2(v.x,v.z);if(boss.wind>0){boss.wind-=dt;boss.vel.x*=.88;boss.vel.z*=.88;if(boss.wind<=0){boss.strike=.28;boss.attack=.42;boss.didHit=false;boss.sequence++;boss.ai=boss.spec.type==='human'&&boss.spec.scale<2&&boss.sequence%2===1?.3:boss.hp<boss.spec.hp*.5?.55:.95;}}
 else if(boss.strike>0){boss.strike-=dt;const u=norm(v);boss.vel.x=u.x*(boss.spec.type==='beast'?8:3);boss.vel.z=u.z*(boss.spec.type==='beast'?8:3);if(boss.strike<.16&&!boss.didHit){boss.didHit=true;slash(boss,{combo:boss.sequence%3});if(boss.spec.scale>2)groundImpact(add(boss.pos,boss.local(V(0,0,1.7))),1.5);enemyImpact()}}
 else if(dist>2.1+boss.spec.scale*.55){const u=norm(v);boss.vel.x=u.x*boss.spec.speed;boss.vel.z=u.z*boss.spec.speed;boss.ai=Math.max(.3,boss.ai-dt)}else{boss.vel.x*=.8;boss.vel.z*=.8;boss.ai-=dt;if(boss.ai<=0){boss.wind=boss.spec.wind*(boss.hp<boss.spec.hp*.5?.82:1);sound(220,.1,'sine',.015)}}}else if(boss.down>0||boss.broken>0){boss.wind=0;boss.strike=0}
 if(boss.posture>=100&&boss.stun<1.5){boss.posture=0;boss.stun=3.5;boss.broken=3.5;boss.down=.65;boss.wind=0;announce('体 勢 崩 し — 斬 れ',1.8);impact(boss.nodes[1].p,'break',2)}if(boss.stun===0)boss.posture=Math.max(0,boss.posture-dt*2);
 // Root collision avoids interpenetration without freezing the limb response.
 v=sub(player.pos,boss.pos);dist=len(v);const separation=.65+boss.spec.scale*.5;if(dist<separation){const push=mul(norm(dist?v:V(1,0,0)),(separation-dist)*.5);player.pos=add(player.pos,push);boss.pos=sub(boss.pos,push)}
 }else{transition-=dt;attackQueued=parryQueued=false;if(transition<=0){if(player.hp<=0){mode='lost';showOverlay('もう一度、弾け。',`${boss.spec.name}との再戦。パリィは金色の合図から少し早めでも成功します。`,'この敵に再挑戦')}else if(level<3){const health=Math.min(100,player.hp+35);level++;boss=new Doll(bosses[level]);const shift=sub(V(0,0,3),player.pos);player.pos=V(0,0,3);player.vel=V();for(const n of player.nodes){n.p=add(n.p,shift);n.prev={...n.p}}player.swing=null;player.attack=0;player.cool=0;player.counter=0;player.hp=health;player.invuln=1;announce(boss.spec.name,2)}else{mode='won';showOverlay('四 異 討 伐',`全4体を撃破。パリィ ${parries}回 / PERFECT ${perfects}回 / ${Math.floor(elapsed)}秒`,'もう一度挑む')}}}
 }
 for(const d of [player,boss]){if(d.hp>0&&d.down===0){d.pos.x+=d.vel.x*dt;d.pos.z+=d.vel.z*dt;d.vel=mul(d.vel,.97);let r=Math.hypot(d.pos.x,d.pos.z);if(r>10){d.pos.x*=10/r;d.pos.z*=10/r}}d.physics(dt)}
 for(const p of particles){p.life-=dt;p.p=add(p.p,mul(p.v,dt));p.v.y-=16*dt;if(p.p.y<.05){p.p.y=.05;p.v.y*=-.35}}particles=particles.filter(p=>p.life>0);for(const r of rings)r.life-=dt;rings=rings.filter(r=>r.life>0);toastT-=dt;if(toastT<=0)$('toast').textContent='';
 $('cue').textContent=mode==='play'&&boss.wind>0&&boss.wind<.36?'弾 け':mode==='play'&&boss.wind>=.36?boss.spec.attackName:'';updateHUD();}
// Perspective painter: all geometry shares one camera transform and depth ordering.
let basis;
function setCamera(){
 const midpoint=mul(add(player.pos,boss.pos),.5),smoothing=1-Math.exp(-feel.dt*8);
 target.x+=(midpoint.x-target.x)*smoothing;target.z+=(midpoint.z-target.z)*smoothing;target.y=1.1;
 const distance=len(sub(player.pos,boss.pos)),portrait=W<H,giant=boss.spec.scale>2;
 const pullback=Math.max(0,distance-3)*(portrait?.68:.48),kick=feel.reduced?0:feel.zoom;
 camera=add(target,V(0,(portrait?8.7:6.9)+(giant?1.1:0)+pullback*.65-kick*.45,(portrait?12:10.1)+(giant?1.1:0)+pullback-kick));
 const f=norm(sub(target,camera)),right=norm(V(-f.z,0,f.x)),up=V(right.y*f.z-right.z*f.y,right.z*f.x-right.x*f.z,right.x*f.y-right.y*f.x);basis={f,right,up};
}
const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
function project(p){let v=sub(p,camera),z=dot(v,basis.f),f=Math.min(W,H)*1.18;return{x:W/2+dot(v,basis.right)*f/z,y:H*.49-dot(v,basis.up)*f/z,z,s:f/z}}
function polygon(points,color,stroke){const p=points.map(project);if(p.some(q=>q.z<.1))return;shapes.push({depth:p.reduce((s,q)=>s+q.z,0)/p.length,draw(){ctx.beginPath();p.forEach((q,i)=>i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y));ctx.closePath();ctx.fillStyle=color;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=.6;ctx.stroke()}}})}
function segment(a,b,r,color){const p=project(a),q=project(b);if(p.z<.1||q.z<.1)return;shapes.push({depth:(p.z+q.z)/2,draw(){ctx.lineCap='round';ctx.lineWidth=Math.max(1,(p.s+q.s)*r);ctx.strokeStyle='#0b151b';ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();ctx.lineWidth=Math.max(1,(p.s+q.s)*r*.78);ctx.strokeStyle=color;ctx.stroke();ctx.lineCap='butt'}})}
function orb(p,r,color){const q=project(p);if(q.z<.1)return;shapes.push({depth:q.z,draw(){ctx.fillStyle=color;ctx.beginPath();ctx.arc(q.x,q.y,Math.max(1,r*q.s),0,Math.PI*2);ctx.fill();ctx.fillStyle='#ffffff25';ctx.beginPath();ctx.arc(q.x-r*q.s*.22,q.y-r*q.s*.25,r*q.s*.45,0,Math.PI*2);ctx.fill()}})}
function floorRing(p,r,color,width=1){const ps=Array.from({length:49},(_,i)=>project(add(p,V(Math.cos(i/48*Math.PI*2)*r,0,Math.sin(i/48*Math.PI*2)*r))));ctx.beginPath();ps.forEach((q,i)=>i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke()}
function box(x,y,z,w,h,d,color){const a=V(x-w/2,y,z-d/2),b=V(x+w/2,y,z-d/2),c=V(x+w/2,y,z+d/2),e=V(x-w/2,y,z+d/2),lift=p=>add(p,V(0,h,0));polygon([a,b,lift(b),lift(a)],color);polygon([b,c,lift(c),lift(b)],'#253039');polygon([c,e,lift(e),lift(c)],color);polygon([e,a,lift(a),lift(e)],'#17212a');polygon([lift(a),lift(b),lift(c),lift(e)],'#4d5558')}
function drawDoll(d){let color=d.invuln>0?'#f7ecd6':d.spec.color;for(const l of d.links)segment(d.nodes[l.a].p,d.nodes[l.b].p,l.r,color);for(const n of d.nodes)orb(n.p,n.r,n.name==='head'?'#e4d4b5':color);
 const head=d.nodes[2].p,eyes=add(head,d.local(V(0,.02,d.nodes[2].r*.88)));segment(add(eyes,d.local(V(-.15,0,0))),add(eyes,d.local(V(.15,0,0))),.035,d.player?'#c6ffff':'#ffdf8d');
 if(d.spec.type==='human'){const hand=d.nodes.find(n=>n.name==='hand').p,blade=add(hand,d.local(V(.03,d.attack>0?.35:.85,d.attack>0?1.3:.55)));segment(hand,blade,.045,d.player?'#c5f8ee':'#f2c57c');orb(hand,.12,'#e9c989');if(d.attack>0){const end=add(blade,d.local(V(-.5,.1,-.15)));segment(blade,end,.06,'#ffe5a077')}}
 if(d.parry>0){const p=project(d.nodes[1].p);shapes.push({depth:p.z-.3,draw(){ctx.strokeStyle='#b9ffef';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,p.s*.85,-2.8,.2);ctx.stroke()}})}
}
function render(){setCamera();ctx.save();const recoil=feel.reduced?0:shake;ctx.translate(Math.sin(feel.clock*113)*recoil*14,Math.cos(feel.clock*139)*recoil*8);const bg=ctx.createLinearGradient(0,0,0,H);bg.addColorStop(0,'#0b131e');bg.addColorStop(.55,'#27313a');bg.addColorStop(1,'#101820');ctx.fillStyle=bg;ctx.fillRect(-20,-20,W+40,H+40);shapes=[];
 // In-world arena and monumental gate, rendered geometry rather than backdrop art.
 polygon([V(-14,-.1,-14),V(14,-.1,-14),V(14,-.1,14),V(-14,-.1,14)],'#303b40');for(let i=-12;i<12;i+=2)for(let j=-12;j<12;j+=2){polygon([V(i,0,j),V(i+1.94,0,j),V(i+1.94,0,j+1.94),V(i,0,j+1.94)],(i+j)%4?'#354044':'#313b40','#56606522')}
 for(let i=0;i<12;i++){const a=i*Math.PI/6,x=Math.cos(a)*12,z=Math.sin(a)*12;box(x,0,z,.8,2.7+(i%3)*.65,.8,'#3b454a');orb(V(x,3+(i%3)*.65,z),.12,'#e2ab64')}
 box(-4,0,-12,1.5,6,1.3,'#37424a');box(4,0,-12,1.5,6,1.3,'#37424a');box(0,5.5,-12,9,1,1.5,'#404b51');
 shapes.sort((a,b)=>b.depth-a.depth);for(const s of shapes)s.draw();shapes=[];
 floorRing(V(0,.03,0),9.8,'#c4a57155',2);floorRing(V(0,.035,0),4,'#b3a28a33');
 if(mode==='play'&&boss.wind>0){const ready=boss.wind<.36;floorRing(V(boss.pos.x,.04,boss.pos.z),(2.2+boss.spec.scale*.6)*(1-clamp(boss.wind/boss.spec.wind,0,1)*.18),ready?'#ffcf8288':'#ed886644',ready?2.5:1)}
 if(boss.broken>0)floorRing(V(boss.pos.x,.05,boss.pos.z),1.3+Math.sin(feel.clock*7)*.08,'#ffe2a3',2);
 if(player.counter>0)floorRing(V(player.pos.x,.05,player.pos.z),.8,'#99ffee',2);
 for(const d of [player,boss]){const p=project(V(d.pos.x,.02,d.pos.z));ctx.fillStyle='#03060955';ctx.beginPath();ctx.ellipse(p.x,p.y,p.s*d.spec.scale*.75,p.s*d.spec.scale*.28,0,0,Math.PI*2);ctx.fill();drawDoll(d)}
 for(const p of particles)orb(p.p,.035+p.life*.025,p.color);shapes.sort((a,b)=>b.depth-a.depth);for(const s of shapes)s.draw();for(const r of rings)floorRing(V(r.p.x,.06,r.p.z),(.5-r.life)*7,r.color,Math.max(1,r.life*5));
 if(boss.wind>0&&mode==='play'){const q=project(add(boss.nodes[2].p,V(0,.55,0)));ctx.fillStyle=boss.wind<.36?'#ffdc86':'#d48d64';ctx.font='bold 24px system-ui';ctx.textAlign='center';ctx.fillText(boss.wind<.36?'◇':'·',q.x,q.y)}
 drawFeel();ctx.restore();}
function frame(now){
 const dt=Math.min((now-last)/1000||0,.05);last=now;
 if(mode!=='paused'){
  updateFeel(dt);if(mode==='play')elapsed+=dt;
  if(hitstop>0)hitstop=Math.max(0,hitstop-dt);
  else{acc+=dt*(feel.slow>0?.45:1);let steps=0;while(acc>=1/60&&steps++<4){step(1/60);acc-=1/60;if(hitstop>0){acc=0;break}}}
 }
 render();requestAnimationFrame(frame);
}
reset();requestAnimationFrame(frame);
// Read-only diagnostics for regression checks; gameplay never depends on this API.
window.parryDoll={snapshot:()=>({mode,level,playerHP:player.hp,bossHP:boss.hp,parries,finite:[player,boss].every(d=>d.nodes.every(n=>Object.values(n.p).every(Number.isFinite))),particles:particles.length})};
