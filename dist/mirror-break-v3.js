'use strict';
// MIRROR BREAK v3 — final-duel presentation director, stronger persistent destruction and ZERO TRACE payoff.
(()=>{
 if(window.__parryMirrorBreakV3Loaded)return;window.__parryMirrorBreakV3Loaded=true;
 const state=window.__mirrorBreakState,v2=window.__mirrorBreakV2State;if(!state||!v2)return;
 const s={finalBoss:null,lastPhase:0,shiftT:0,auraClock:0,zeroCharges:0,zeroPulse:0,breakPulse:0,lastBroken:false,lastLevel:-1};
 window.__mirrorBreakV3State=s;
 const roman=n=>['I','II','III'][Math.max(0,Math.min(2,(n||1)-1))];
 const dominant=c=>{const m=Math.max(c.EDGE,c.MIRROR,c.PULSE);if(m<=0)return'NONE';if(c.EDGE===m)return'EDGE';if(c.MIRROR===m)return'MIRROR';return'PULSE'};
 const zeroLevel=c=>Math.min(c.EDGE||0,c.MIRROR||0,c.PULSE||0);
 function synergy(c=state.cores){
  const z=zeroLevel(c);if(z>0)return['ZERO TRACE',z];
  if(c.EDGE>0&&c.MIRROR>0)return['REFLECT EDGE',Math.min(c.EDGE,c.MIRROR)];
  if(c.EDGE>0&&c.PULSE>0)return['RUPTURE DRIVE',Math.min(c.EDGE,c.PULSE)];
  if(c.MIRROR>0&&c.PULSE>0)return['RESONANT MIRROR',Math.min(c.MIRROR,c.PULSE)];
  return[dominant(c),Math.max(c.EDGE,c.MIRROR,c.PULSE)];
 }
 const style=document.createElement('style');style.textContent=`
 body.mb-final-duel #pbBanner,body.mb-final-duel #pbPhaseStrip{opacity:0!important;visibility:hidden!important}
 body.mb-final-duel #pbCineCaption{opacity:0!important;visibility:hidden!important}
 body.mb-final-duel #mbSynergyHud{display:none!important}
 body.mb-final-duel #mbBreakHud{top:28%!important;min-width:150px;font-size:8px;letter-spacing:1.5px}
 body.mb-final-duel #mbBreakHud:not(.exposed):not(.broken){opacity:0!important}
 body.mb-final-duel #mbBreakHud.broken{opacity:.48!important;transform:translateX(-50%) scale(.92)!important}
 body.mb-final-duel #mbMirrorLoadout{top:19.5%!important;min-width:260px;padding:6px 13px;background:#071019c9;border-color:#c9b27748;font-size:8px;line-height:1.5}
 body.mb-final-duel #mbMirrorLoadout b{display:block;font-size:10px;letter-spacing:4px}body.mb-final-duel #mbMirrorLoadout i{margin:0 5px}
 #mbFinalAura{position:fixed;inset:0;z-index:4;pointer-events:none;opacity:0;transition:opacity .32s;background:radial-gradient(circle at 50% 44%,rgba(174,255,238,.13),transparent 31%),linear-gradient(180deg,rgba(210,246,255,.035),transparent 35%,rgba(255,210,143,.025));mix-blend-mode:screen}
 body.mb-final-duel #mbFinalAura{opacity:.52}body.mb-final-duel.mb-final-p2 #mbFinalAura{opacity:.68;background:radial-gradient(circle at 50% 43%,rgba(255,223,147,.14),transparent 29%),radial-gradient(circle at 50% 58%,rgba(143,255,232,.07),transparent 37%)}body.mb-final-duel.mb-final-p3 #mbFinalAura{opacity:.82;background:radial-gradient(circle at 50% 43%,rgba(255,231,166,.16),transparent 24%),radial-gradient(circle at 50% 48%,rgba(112,255,233,.11),transparent 40%)}
 #mbMirrorShift{position:fixed;left:50%;top:43%;transform:translate(-50%,-50%) scale(.96);z-index:36;pointer-events:none;opacity:0;text-align:center;padding:7px 18px;border-left:1px solid #f0d28a88;border-right:1px solid #f0d28a88;background:linear-gradient(90deg,transparent,#06101bd9 19%,#06101bd9 81%,transparent);text-shadow:0 3px 14px #000;transition:opacity .12s,transform .12s;white-space:nowrap}
 #mbMirrorShift.show{opacity:1;transform:translate(-50%,-50%) scale(1)}#mbMirrorShift small{display:block;color:#b8cbc7;font-size:8px;letter-spacing:4px}#mbMirrorShift b{display:block;margin-top:3px;color:#f8df9f;font-size:17px;letter-spacing:6px}#mbMirrorShift em{display:block;margin-top:3px;color:#c5d8d4;font-style:normal;font-size:8px;letter-spacing:2px}
 #mbZeroTrace{position:absolute;left:50%;bottom:max(62px,calc(env(safe-area-inset-bottom) + 55px));transform:translateX(-50%);z-index:28;pointer-events:none;opacity:0;padding:4px 9px;border:1px solid #d8c17a44;background:#071018a8;color:#bdd3cd;font-size:8px;letter-spacing:2px;text-shadow:0 2px 8px #000;transition:opacity .12s,transform .12s}#mbZeroTrace.show{opacity:.86}#mbZeroTrace.hot{opacity:1;transform:translateX(-50%) scale(1.06);color:#ffe3a0;border-color:#f1cb6d88}
 @media(max-height:500px){body.mb-final-duel #mbMirrorLoadout{top:18%}body.mb-final-duel #mbBreakHud{top:28.5%}#mbMirrorShift{top:46%}#mbZeroTrace{bottom:max(48px,calc(env(safe-area-inset-bottom) + 44px))}}
 `;document.head.appendChild(style);
 const aura=document.createElement('div');aura.id='mbFinalAura';document.body.appendChild(aura);
 const shift=document.createElement('div');shift.id='mbMirrorShift';shift.innerHTML='<small>MIRROR SYSTEM</small><b>BUILD MIRROR</b><em></em>';document.body.appendChild(shift);
 const zero=document.createElement('div');zero.id='mbZeroTrace';document.body.appendChild(zero);
 function showShift(phase){
  const c=state.cores,[syn,lv]=synergy(c),d=dominant(c);s.shiftT=phase===1?1.05:.82;
  shift.querySelector('small').textContent=phase===1?'MIRROR SYSTEM':phase===2?'SECONDARY CORE ONLINE':'FULL BUILD SYNC';
  shift.querySelector('b').textContent=phase===1?'BUILD MIRROR':`MIRROR SHIFT ${roman(phase)}`;
  shift.querySelector('em').textContent=phase===1?`${d} PRIMARY · ${syn}${lv?` ${lv}`:''}`:phase===2?`${syn} · ADAPTATION RISING`:`${syn} · ZERO-TRACE PATTERN`;
  shift.classList.add('show');
  const p=boss?.nodes?.find(n=>n.name==='chest')?.p||boss?.nodes?.[1]?.p;if(p){ring(p,phase===3?'#fff0b0':'#aaffee');burst(p,phase===3?'#ffe0a0':'#b8fff0',phase===3?18:10,phase===3?6:4)}
 }
 function syncFinalHud(){
  const final=level===4&&boss&&boss.hp>0&&mode==='play',phase=final?Math.max(1,v2.finalPhase||1):0;
  document.body.classList.toggle('mb-final-duel',final);document.body.classList.toggle('mb-final-p2',final&&phase===2);document.body.classList.toggle('mb-final-p3',final&&phase>=3);
  if(final){
   const c=state.cores,[syn,lv]=synergy(c),mh=document.getElementById('mbMirrorLoadout');if(mh){mh.classList.add('show');mh.innerHTML=`<b>MIRROR ${roman(phase)}</b><i>${dominant(c)} PRIMARY</i><i>${syn}${lv?` ${lv}`:''}</i><i>E${c.EDGE} · M${c.MIRROR} · P${c.PULSE}</i>`}
  }
  const zl=zeroLevel(state.cores);zero.classList.toggle('show',zl>0&&mode==='play');zero.classList.toggle('hot',s.zeroPulse>0);zero.textContent=zl>0?`ZERO TRACE ${s.zeroCharges>0?`READY ×${s.zeroCharges}`:`SYNC ${zl}`}`:'';
 }
 const saveNode=(list,n)=>{if(n&&!list.some(q=>q.n===n))list.push({n,p:{...n.p},r:n.r})};
 function extraBreakDeform(){
  if(!boss||!state.broken||state.boss!==boss||!state.part)return[];const saved=[],part=state.part,local=q=>boss.local(q),off=(n,q,scale=1)=>{if(!n)return;saveNode(saved,n);n.p=add(n.p,local(q));n.r*=scale};
  if(part.kind==='ARM'){
   const hand=boss.nodes.find(n=>n.name==='hand'),elbows=boss.nodes.filter(n=>n.name==='elbow'),shoulders=boss.nodes.filter(n=>n.name==='shoulder'),sign=Math.sign(hand?.rest?.x||1),elbow=elbows.find(n=>Math.sign(n.rest.x||1)===sign)||elbows[0],shoulder=shoulders.find(n=>Math.sign(n.rest.x||1)===sign)||shoulders[0];
   off(hand,V(-.11*sign,-.34,-.16),.72);off(elbow,V(-.07*sign,-.18,-.08),.84);off(shoulder,V(-.025*sign,-.07,-.03),.93);
  }else if(part.kind==='LEG'){
   const feet=boss.nodes.filter(n=>n.name==='foot'),foot=feet.reduce((a,n)=>!a||n.rest.z>a.rest.z?n:a,null),knees=boss.nodes.filter(n=>n.name==='knee'),knee=knees.reduce((a,n)=>!a||n.rest.z>a.rest.z?n:a,null),sign=Math.sign(foot?.rest?.x||1),hip=boss.nodes.find(n=>n.name==='hip');
   off(foot,V(.14*sign,-.16,-.27),.78);off(knee,V(.09*sign,-.10,-.14),.86);off(hip,V(-.035*sign,-.025,-.03),.98);
  }else if(part.kind==='CORE'){
   const chest=boss.nodes.find(n=>n.name==='chest'),head=boss.nodes.find(n=>n.name==='head'),hands=boss.nodes.filter(n=>n.name==='hand'||n.name==='offhand');off(chest,V(0,-.05,-.12),.82);off(head,V(.04,-.03,-.07),.94);for(const h of hands)off(h,V(Math.sign(h.rest.x||1)*.04,-.06,-.05),.96);
  }
  return saved;
 }
 const v3Render=render;render=function(){const saves=extraBreakDeform();try{return v3Render()}finally{for(const q of saves){q.n.p=q.p;q.n.r=q.r}}};
 const v3DrawDoll=drawDoll;drawDoll=function(d){v3DrawDoll(d);if(d!==boss||!state.broken||state.boss!==boss)return;const part=state.part,n=part?.node?boss.nodes.find(x=>x.name===part.node):null;if(!n)return;const p=project(n.p);if(p.z<=.3)return;shapes.push({depth:p.z-.55,draw(){const r=Math.max(7,p.s*n.r*1.05);ctx.save();ctx.strokeStyle='rgba(255,187,125,.62)';ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(p.x-r*.72,p.y-r*.62);ctx.lineTo(p.x+r*.66,p.y+r*.52);ctx.moveTo(p.x+r*.62,p.y-r*.70);ctx.lineTo(p.x-r*.48,p.y+r*.62);ctx.stroke();ctx.restore()}})};
 const v3EnemyImpact=enemyImpact;enemyImpact=function(move=null){const before=perfects,out=v3EnemyImpact(move),zl=zeroLevel(state.cores);if(perfects>before&&zl>0){s.zeroCharges=Math.min(2,s.zeroCharges+1);s.zeroPulse=.48;const p=player?.nodes?.find(n=>n.name==='hand')?.p||player?.nodes?.[1]?.p;if(p)ring(p,'#fff0b0')}return out};
 const v3ResolveSwing=resolveSwing;resolveSwing=function(){const zl=zeroLevel(state.cores),use=zl>0&&s.zeroCharges>0&&!!player.swing?.counter&&boss?.hp>0,before=boss?.hp||0,wasBroken=state.broken;if(use&&player.swing){player.swing.damage*=1+.055*zl;player.swing.force*=1+.08*zl}const out=v3ResolveSwing(),landed=boss&&boss.hp<before;if(use&&landed){s.zeroCharges--;s.zeroPulse=.62;boss.posture=Math.min(115,boss.posture+4*zl);boss.stun=Math.max(boss.stun,.28+.08*zl);player.counter=Math.max(player.counter,.34+.05*zl);if(window.__phaseBreakV2State)window.__phaseBreakV2State.resolve=Math.min(100,(window.__phaseBreakV2State.resolve||0)+3*zl);const p=boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1]?.p;if(p){ring(p,'#fff2b8');burst(p,'#c8fff0',6+zl*2,3.6)}sound(680,.09,'triangle',.018)}if(!wasBroken&&state.broken)s.breakPulse=.72;return out};
 const v3Reset=reset;reset=function(l=0){const out=v3Reset(l);s.finalBoss=null;s.lastPhase=0;s.shiftT=0;s.auraClock=0;s.breakPulse=0;if(l===0)s.zeroCharges=0;document.body.classList.remove('mb-final-duel','mb-final-p2','mb-final-p3');shift.classList.remove('show');syncFinalHud();return out};
 const v3Step=step;step=function(dt){const out=v3Step(dt),final=level===4&&boss&&boss.hp>0&&mode==='play',phase=final?Math.max(1,v2.finalPhase||1):0;if(final&&(s.finalBoss!==boss||s.lastPhase!==phase)){s.finalBoss=boss;s.lastPhase=phase;showShift(phase);s.auraClock=0}else if(!final){s.finalBoss=null;s.lastPhase=0}s.shiftT=Math.max(0,s.shiftT-dt);s.zeroPulse=Math.max(0,s.zeroPulse-dt);s.breakPulse=Math.max(0,s.breakPulse-dt);shift.classList.toggle('show',s.shiftT>0);if(final&&phase>=2){s.auraClock-=dt;if(s.auraClock<=0){const p=boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1]?.p;if(p)ring(p,phase>=3?'#ffe1a0':'#a8ffec');s.auraClock=phase>=3?.46:.82}}syncFinalHud();s.lastBroken=state.broken;s.lastLevel=level;return out};
 const previousDiag=window.parryMirrorBreakDiagnostics;window.parryMirrorBreakDiagnostics=()=>{const d=previousDiag?previousDiag():{};return{...d,v3:true,finalHudClean:document.body.classList.contains('mb-final-duel'),mirrorShift:s.shiftT>0,zeroTraceCharges:s.zeroCharges,zeroTraceLevel:zeroLevel(state.cores),destructionPass:true}};
 syncFinalHud();
})();
