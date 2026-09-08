'use strict';
// Rendering-only bridge: never writes simulation, input, timing, hit, or camera state.
(()=>{
 const baseRender=render,gameCanvas=$('game'),webgl=document.createElement('canvas');
 webgl.id='visual-scene';webgl.setAttribute('aria-hidden','true');
 Object.assign(webgl.style,{position:'fixed',inset:'0',width:'100%',height:'100%',pointerEvents:'none'});
 gameCanvas.parentNode.insertBefore(webgl,gameCanvas);
 let scene=null,available=false,failure='';
 try{scene=new window.ParryVisual.VisualScene(webgl);available=true}catch(error){failure=String(error);webgl.style.display='none';console.warn('Detailed rendering unavailable; using the original renderer.',error)}
 webgl.addEventListener('webglcontextlost',event=>{event.preventDefault();available=false;webgl.style.display='none'});
 webgl.addEventListener('webglcontextrestored',()=>{available=!!scene;webgl.style.display=available?'':'none'});
 render=function(){
  if(!available)return baseRender();
  // This is exactly the existing camera update, called once per displayed frame.
  setCamera();
  const recoil=feel.reduced?0:shake;
  try{
   const poses=[player,boss].map(d=>d.attack>0?motionPose(d).blade:d.wind>0?COMBO_POSES[enemyMove(d).motion].ready.blade:IDLE_POSE.blade);
   scene.render({width:W,height:H,camera,forward:basis.f,up:basis.up,player,boss,poses,particles,clock:feel.clock,recoil});
  }catch(error){available=false;failure=String(error);webgl.style.display='none';console.error('Detailed rendering stopped; using original renderer.',error);return baseRender()}
  ctx.clearRect(0,0,W,H);ctx.save();ctx.translate(Math.sin(feel.clock*113)*recoil*14,Math.cos(feel.clock*139)*recoil*8);
  if(mode==='play'&&boss.wind>0)drawAttackTelegraph();
  if(boss.broken>0)floorRing(V(boss.pos.x,.05,boss.pos.z),1.3+Math.sin(feel.clock*7)*.08,'#ffe2a3',2);
  if(player.counter>0)floorRing(V(player.pos.x,.05,player.pos.z),.8,'#99ffee',2);
  for(const r of rings)floorRing(V(r.p.x,.06,r.p.z),(.5-r.life)*7,r.color,Math.max(1,r.life*5));
  if(boss.wind>0&&mode==='play'){const p=project(add(boss.nodes[2].p,V(0,.55,0)));if(p.z>.18){ctx.fillStyle=boss.wind<Math.max(.06,.48-enemyMove().hits[0])?'#ffdc86':'#d48d64';ctx.font='bold 24px system-ui';ctx.textAlign='center';ctx.fillText(boss.wind<Math.max(.06,.48-enemyMove().hits[0])?'◇':'·',p.x,p.y)}}
  drawFeel();ctx.restore();
 };
 window.parryVisualDiagnostics=()=>({available,failure,...(scene?.diagnostics||{})});
})();
