'use strict';
// PHASE BREAK v3 — boss signature phase arts + fair mirror parry for THE PARRY DOLL.
(()=>{
 if(window.__parryPhaseBreakV3Loaded)return;window.__parryPhaseBreakV3Loaded=true;
 const s={lastBoss:null,lastLevel:-1,lastPhase:1,specialClock:0,specials:0,mirrorT:0,mirrorMax:0,mirrorCounterT:0,mirrorCountered:0,mirrorArmed:0,mirrorCooldown:2.2,lastPlayerAttackAt:-9};
 window.__phaseBreakV3State=s;
 const pbDiag=()=>typeof window.parryPhaseBreakDiagnostics==='function'?window.parryPhaseBreakDiagnostics():null;
 const v2=()=>window.__phaseBreakV2State||null;
 const specials={
  0:{
   2:{name:'残火・抜刀三閃',kind:'combo',shape:'cone',wind:.70,active:.88,hits:[.10,.36,.64],range:3.65,arc:1.72,speed:1.85,damage:.78,force:20,recover:.82,motion:0},
   3:{name:'灰燼・返し五連',kind:'combo',shape:'cone',wind:.62,active:1.17,hits:[.09,.30,.51,.73,.97],range:3.75,arc:1.88,speed:1.95,damage:.72,force:22,recover:.76,motion:0}
  },
  1:{
   2:{name:'骨鎖・跳牙',kind:'leap',shape:'cone',wind:.72,active:.57,hits:[.13,.40],range:4.8,arc:1.18,speed:6.2,damage:1.0,force:25,recover:.86,motion:2},
   3:{name:'飢餓・裂走',kind:'rush',shape:'line',wind:.60,active:.90,hits:[.12,.38,.67],range:5.4,width:.78,speed:7.2,damage:.88,force:28,recover:.78,motion:1}
  },
  2:{
   2:{name:'天蓋・双糸槍',kind:'thrust',shape:'line',wind:.76,active:.64,hits:[.14,.43],range:5.1,width:.78,speed:4.8,damage:1.02,force:24,recover:.86,motion:1},
   3:{name:'断糸・八方乱舞',kind:'combo',shape:'cone',wind:.67,active:1.36,hits:[.10,.28,.46,.64,.82,1.02,1.20],range:4.25,arc:2.48,speed:1.9,damage:.66,force:21,recover:.84,motion:0}
  },
  3:{
   2:{name:'崩鐘・二重震脚',kind:'stomp',shape:'circle',wind:.88,active:.76,hits:[.14,.49],range:4.55,speed:0,damage:.92,force:31,recover:1.08,motion:2},
   3:{name:'天砕き・三重落',kind:'slam',shape:'cone',wind:.90,active:1.02,hits:[.15,.47,.80],range:4.0,arc:1.30,speed:.85,damage:1.02,force:34,recover:1.02,motion:2}
  },
  4:{
   2:{name:'鏡界・返刃四式',kind:'combo',shape:'cone',wind:.64,active:1.04,hits:[.10,.33,.57,.83],range:3.75,arc:1.88,speed:1.9,damage:.76,force:22,recover:.76,motion:0},
   3:{name:'零式・反照六連',kind:'combo',shape:'cone',wind:.58,active:1.36,hits:[.08,.28,.48,.69,.91,1.15],range:3.95,arc:2.08,speed:2.05,damage:.70,force:24,recover:.72,motion:0}
  }
 };
 const mirrorCounter={name:'鏡返し・追撃',kind:'thrust',shape:'line',wind:.30,active:.33,hits:[.12],range:4.45,width:.72,speed:6.1,damage:1.02,force:28,recover:.72,motion:1};
 const style=document.createElement('style');style.textContent=`#pbMirror{position:fixed;left:50%;top:29%;transform:translate(-50%,6px) scale(.94);z-index:31;pointer-events:none;opacity:0;padding:5px 14px;border:1px solid #cffff066;background:linear-gradient(90deg,transparent,#07131ee6 18%,#07131ee6 82%,transparent);color:#e8fff9;text-shadow:0 2px 10px #000;letter-spacing:3px;font-size:10px;transition:opacity .08s,transform .12s}#pbMirror.show{opacity:1;transform:translate(-50%,0) scale(1)}#pbMirror b{color:#fff0b7;margin-right:8px}@media(max-height:500px){#pbMirror{top:26%}}`;document.head.appendChild(style);
 const mirrorUI=document.createElement('div');mirrorUI.id='pbMirror';mirrorUI.innerHTML='<b>鏡 構 え</b>攻撃すれば返される';document.body.appendChild(mirrorUI);
 function phase(){return pbDiag()?.phase||1}
 function directEnemyAttack(move){if(!boss||boss.hp<=0||boss.stun>0||boss.wind>0||boss.strike>0)return false;const m={...move,hits:[...(move.hits||[])]};boss.pattern=m;boss.wind=m.wind*(boss.enraged?.9:1);boss.windDuration=boss.wind;boss.aim=boss.face;boss.hitIndex=0;boss.strikeElapsed=0;sound(m.kind==='slam'||m.kind==='stomp'?120:220,.13,'sine',.025);return true}
 function canSpecial(){const vv=v2();return mode==='play'&&boss?.hp>0&&player?.hp>0&&boss.stun<=0&&boss.wind<=0&&boss.strike<=0&&boss.broken<=0&&!(vv?.cineT>0)&&!(vv?.ultimateT>0)}
 function specialDue(){const p=phase();if(p<2||!canSpecial())return false;const interval=p>=3?3.3:4.8;return s.specialClock>=interval}
 function trySignature(){if(!specialDue())return false;const p=phase(),m=specials[level]?.[p];s.specialClock=0;if(!m)return false;s.specials++;const ok=directEnemyAttack(m);if(ok){const d=$('pbDanger');if(d){d.innerHTML=`<strong>${p>=3?'秘 奥':'変 化 技'}</strong>${m.name}`;d.classList.add('show')}if($('attackHud'))$('attackHud').textContent=m.name;feel.pulse=Math.max(feel.pulse,.08);sound(p>=3?150:185,.16,'triangle',.028)}return ok}
 function armMirror(){if(level!==4||phase()<2||!canSpecial()||s.mirrorCooldown>0||s.mirrorT>0)return false;const vv=v2(),aggressive=(vv?.attacks||0)>Math.max(2,(vv?.parryAttempts||0)*.78),rate=(vv?.attacks||0)%3===1;if(!aggressive&&!rate&&phase()<3)return false;s.mirrorT=phase()>=3?1.05:.86;s.mirrorMax=s.mirrorT;s.mirrorCooldown=phase()>=3?2.65:3.5;s.mirrorArmed++;boss.stun=Math.max(boss.stun,s.mirrorT*.72);boss.vel=V();mirrorUI.classList.add('show');if($('attackHud'))$('attackHud').textContent='鏡 構 え';ring(boss.nodes.find(n=>n.name==='hand')?.p||boss.nodes[1].p,'#cffff4');sound(760,.12,'sine',.026);return true}
 function mirrorParry(){const move=player.swing;if(!move||s.mirrorT<=0||level!==4)return false;const v=sub(boss.pos,player.pos),distance=len(v),reach=2.15+boss.spec.scale*.55;if(distance>reach)return false;player.swing=null;player.attack=0;player.cool=Math.max(player.cool,.30);player.stun=Math.max(player.stun,.34);player.counter=0;const away=norm(sub(player.pos,boss.pos)),hand=boss.nodes.find(n=>n.name==='hand')?.p||boss.nodes[2]?.p||boss.nodes[1].p;player.vel=mul(away,4.6);boss.face=Math.atan2(-away.x,-away.z);boss.stun=Math.min(boss.stun,.08);s.mirrorT=0;s.mirrorCounterT=.22;s.mirrorCountered++;mirrorUI.classList.remove('show');ring(hand,'#fff0b2');burst(hand,'#d7fff5',26,7);burst(hand,'#ffd678',18,6);impact(hand,'parry',1.75);shake=Math.max(shake,.27);hitstop=Math.max(hitstop,.075);feel.flash=Math.max(feel.flash,.045);announce('鏡 弾 き',.55);sound(920,.10,'square',.035);return true}
 const v3ResolveSwing=resolveSwing;resolveSwing=function(){if(mirrorParry())return;return v3ResolveSwing()};
 const v3PlayerAttack=playerAttack;playerAttack=function(){const ok=v3PlayerAttack();if(ok)s.lastPlayerAttackAt=time;return ok};
 const v3Reset=reset;reset=function(l=0){const out=v3Reset(l);s.lastBoss=boss;s.lastLevel=level;s.lastPhase=phase();s.specialClock=0;s.mirrorT=s.mirrorCounterT=0;s.mirrorCooldown=2.2;mirrorUI.classList.remove('show');return out};
 const v3Step=step;step=function(dt){v3Step(dt);const p=phase(),vv=v2();if(boss!==s.lastBoss||level!==s.lastLevel){s.lastBoss=boss;s.lastLevel=level;s.lastPhase=p;s.specialClock=0;s.mirrorT=s.mirrorCounterT=0;s.mirrorCooldown=2.2;mirrorUI.classList.remove('show')}if(mode==='play'&&boss?.hp>0&&player?.hp>0&&!(vv?.cineT>0)){s.specialClock+=dt;s.mirrorCooldown=Math.max(0,s.mirrorCooldown-dt);if(level===4){if(s.mirrorT>0){s.mirrorT=Math.max(0,s.mirrorT-dt);boss.vel=V();boss.stun=Math.max(boss.stun,Math.min(.18,s.mirrorT+.02));if(s.mirrorT<=0)mirrorUI.classList.remove('show')}else if(s.mirrorCounterT>0){s.mirrorCounterT=Math.max(0,s.mirrorCounterT-dt);if(s.mirrorCounterT<=0&&canSpecial()){directEnemyAttack(mirrorCounter);if($('attackHud'))$('attackHud').textContent=mirrorCounter.name}}else if(s.specialClock>2.0&&phase()>=2)armMirror()}if(s.mirrorT<=0&&s.mirrorCounterT<=0)trySignature()}else{s.mirrorT=Math.max(0,s.mirrorT-dt);mirrorUI.classList.remove('show')}s.lastPhase=p};
 window.parryPhaseBreakV3Diagnostics=()=>({phase:phase(),specials:s.specials,specialClock:+s.specialClock.toFixed(2),mirror:+s.mirrorT.toFixed(2),mirrorArmed:s.mirrorArmed,mirrorCountered:s.mirrorCountered,mirrorCounter:+s.mirrorCounterT.toFixed(2),lastAttack:+s.lastPlayerAttackAt.toFixed(2)});
})();
