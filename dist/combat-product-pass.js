'use strict';
// Product-level combat pass: spacing, body-type cameras, restrained parry flash and HUD-only attack messaging.
let p5ParryGlow=0,p5BreakPrompt=0,p5FinishBeat=0;
const p5Style=document.createElement('style');
p5Style.textContent=`
#attackHud{position:absolute;top:31px;left:8%;width:84%;height:20px;display:flex;align-items:center;justify-content:center;gap:7px;pointer-events:none;font-size:clamp(10px,1.6vw,13px);font-weight:750;letter-spacing:1.8px;color:#d9b984;text-shadow:0 2px 8px #000;background:linear-gradient(90deg,transparent,#0b1118b8 18%,#0b1118b8 82%,transparent);opacity:0;transform:translateY(-2px);transition:opacity .12s,transform .12s,color .12s}
#attackHud.show{opacity:1;transform:none}#attackHud.ready{color:#ffd98e}#attackHud.finish{color:#ffe7aa;font-size:clamp(13px,2vw,17px);letter-spacing:3.5px}
#attackHud .gem{font-size:9px;opacity:.65}#attackHud.ready .gem{opacity:1}
#cue{top:19%!important;font-size:clamp(12px,1.9vw,15px)!important;letter-spacing:3px!important}
@media(max-height:500px){#attackHud{top:30px}#cue{top:18%!important}}
`;
document.head.appendChild(p5Style);
const p5AttackHud=document.createElement('div');p5AttackHud.id='attackHud';p5AttackHud.innerHTML='<span class="gem">◇</span><span class="name"></span><span class="gem">◇</span>';$('bossHud').appendChild(p5AttackHud);
const p5AttackName=p5AttackHud.querySelector('.name');

function p5ShiftDoll(d,delta){
 d.pos=add(d.pos,delta);
 for(const n of d.nodes){n.p=add(n.p,delta);n.prev=add(n.prev,delta)}
}
function p5MaintainSpacing(){
 if(!player||!boss||mode!=='play'||player.hp<=0||boss.hp<=0)return;
 const delta=V(boss.pos.x-player.pos.x,0,boss.pos.z-player.pos.z),distance=Math.hypot(delta.x,delta.z);
 if(distance<.001)return;
 const normal=mul(delta,1/distance),type=boss.spec.type;
 let min=type==='spider'?1.95:type==='beast'?1.78:boss.spec.scale>1.8?2.18:1.58;
 if(player.swing?.finisher)min*=.90;
 if(boss.broken>0||boss.down>0)min*=.92;
 if(distance>=min)return;
 const penetration=min-distance;
 let playerShare=boss.spec.scale>1.8?.82:type==='spider'?.62:.56;
 if(boss.broken>0||boss.down>0)playerShare=.90;
 p5ShiftDoll(player,mul(normal,-penetration*playerShare));
 if(boss.down<=0&&boss.broken<=0)p5ShiftDoll(boss,mul(normal,penetration*(1-playerShare)));
 const pv=dot(player.vel,normal);if(pv>0){player.vel.x-=normal.x*pv*.78;player.vel.z-=normal.z*pv*.78}
 const bv=dot(boss.vel,normal);if(bv<0){boss.vel.x-=normal.x*bv*.72;boss.vel.z-=normal.z*bv*.72}
}
function p5SyncAttackHud(){
 if(!boss||mode!=='play'){p5AttackHud.className='';p5AttackName.textContent='';return}
 if(p5FinishBeat>0){p5AttackName.textContent='FINISH';p5AttackHud.className='show finish';return}
 if(p5BreakPrompt>0){p5AttackName.textContent='斬 れ';p5AttackHud.className='show finish';return}
 if(boss.wind>0||boss.strike>0){
  const move=enemyMove(),ready=boss.wind>0&&boss.wind<Math.max(.06,.48-move.hits[0]);
  p5AttackName.textContent=move.name;p5AttackHud.className='show'+(ready?' ready':'');
  return;
 }
 p5AttackHud.className='';p5AttackName.textContent='';
}

const p5AnnounceBase=announce;
announce=function(t,d){
 if(t==='体 勢 崩 し — 斬 れ'||t==='斬 れ'){p5BreakPrompt=Math.max(p5BreakPrompt,d||1.8);$('toast').textContent='';return}
 if(t==='決 着 の 一 撃'){p5BreakPrompt=0;p5FinishBeat=Math.max(p5FinishBeat,.55);$('toast').textContent='';return}
 return p5AnnounceBase(t,d);
};

const p5EnemyImpactBase=enemyImpact;
enemyImpact=function(move=null){
 const beforeParries=parries,out=p5EnemyImpactBase(move);
 if(parries>beforeParries){player.invuln=Math.min(player.invuln,.055);feel.flash=Math.min(feel.flash,.04);p5ParryGlow=.20}
 return out;
};

const p5DrawDollBase=drawDoll;
drawDoll=function(d){
 const savedInv=d.invuln,parryOutline=d.player&&p5ParryGlow>0;
 if(parryOutline)d.invuln=0;
 p5DrawDollBase(d);d.invuln=savedInv;
 if(parryOutline){
  const alpha=clamp(p5ParryGlow/.20,0,1),col=`rgba(198,255,241,${(.22+.42*alpha).toFixed(3)})`;
  for(const l of d.links){const a=d.nodes[l.a],b=d.nodes[l.b];if(a.name==='foot'||b.name==='foot')continue;segment(a.p,b.p,Math.max(.025,l.r*.28),col)}
  const hand=d.nodes.find(n=>n.name==='hand')||d.nodes[1];orb(hand.p,.14*d.spec.scale,'#e7fff6');
 }
};

const p5UpdateFeelBase=updateFeel;
updateFeel=function(dt){p5UpdateFeelBase(dt);p5ParryGlow=Math.max(0,p5ParryGlow-dt);p5BreakPrompt=Math.max(0,p5BreakPrompt-dt);p5FinishBeat=Math.max(0,p5FinishBeat-dt)};

const p5SetCameraBase=setCamera;
setCamera=function(){
 p5SetCameraBase();
 if(!player||!boss||mode!=='play'||!basis)return;
 let up=0,back=0,side=0;
 if(boss.spec.type==='beast'){up=.56;back=.40;side=.62}
 else if(boss.spec.type==='spider'){up=.86;back=.55;side=.48}
 else if(boss.spec.scale>1.8){up=.18;back=.92;side=.20}
 if(!up&&!back&&!side)return;
 const s=(level%2?-1:1);
 camera.y+=up;camera=sub(camera,mul(basis.f,back));camera=add(camera,mul(basis.right,side*s));
 const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),u=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up:u};
};

const p5StepBase=step;
step=function(dt){
 p5StepBase(dt);p5MaintainSpacing();
 // Core cue keeps only timing instructions; attack names live in the HUD above.
 if(mode==='play'){
  if(boss.wind>0&&boss.wind<Math.max(.06,.48-enemyMove().hits[0]))$('cue').textContent='弾 け';
  else if(boss.strike>0&&boss.hitIndex<enemyMove().hits.length)$('cue').textContent='続 け て 弾 け';
  else $('cue').textContent='';
 }
 p5SyncAttackHud();
};

if(window.parryDoll&&window.parryDoll.snapshot){
 const p5SnapshotBase=window.parryDoll.snapshot;
 window.parryDoll.snapshot=()=>({...p5SnapshotBase(),attackHud:p5AttackName.textContent,parryGlow:+p5ParryGlow.toFixed(3)});
}
