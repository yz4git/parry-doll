from pathlib import Path

p=Path(__file__).resolve().parents[1]/'dist'/'visual-upgrade.js'
s=p.read_text(encoding='utf-8')
marker='// MIRROR_BREAK_ATTACK_READABILITY_V1'
if marker in s:
    print('MIRROR BREAK attack readability already applied')
    raise SystemExit(0)

old="if(d.spec.type==='human'){stabilizeHuman(d,p);if(d.player&&parrySuccessT>0)applyPlayerParrySuccess(d,p)}"
new="if(d.spec.type==='human'){stabilizeHuman(d,p);if(d.player&&d.attack>0)applyPlayerAttackReadability(d,p);if(d.player&&parrySuccessT>0)applyPlayerParrySuccess(d,p)}"
if old not in s:
    raise SystemExit('proxyFor human stabilization anchor missing')
s=s.replace(old,new,1)

anchor=' function applyPlayerParrySuccess(live,proxy){\n'
if anchor not in s:
    raise SystemExit('parry success function anchor missing')
insert=""" // MIRROR_BREAK_ATTACK_READABILITY_V1
 function applyPlayerAttackReadability(live,proxy){
  if(live.attack<=0||live.motion<0||typeof motionPose!=='function')return;
  const pose=motionPose(live);if(!pose)return;
  const s=live.spec.scale,duration=Math.max(.01,live.motionDuration||.42),elapsed=Math.max(0,duration-live.attack),contact=Math.max(.045,live.motionContact||.12),after=clamp((elapsed-contact)/Math.max(.08,duration-contact),0,1),before=clamp(elapsed/contact,0,1);
  const smooth=x=>x*x*(3-2*x),phase=elapsed<contact?smooth(before):1-smooth(after)*.22;
  const toWorld=q=>addv(live.pos,live.local(mulv(q,s))),by=name=>proxy.nodes.find(n=>n.name===name),hand=by('hand'),offhand=by('offhand'),chest=by('chest'),head=by('head'),hip=by('hip');
  // Snap the weapon wrist toward the authored attack arc. Gameplay PBD remains untouched; only the render proxy moves.
  if(hand){const desired=toWorld(pose.hand),weight=live.motion===2?.96:.90;hand.p=mixv(hand.p,desired,weight)}
  if(offhand&&live.motion===2){const q=addv(pose.hand,v(-.18,-.06,-.10)),desired=toWorld(q);offhand.p=mixv(offhand.p,desired,.78)}
  const right=v(Math.cos(live.face),0,-Math.sin(live.face)),forward=v(Math.sin(live.face),0,Math.cos(live.face));
  const swingSide=live.motion===0?(-.16+.34*after):live.motion===1?(.14-.30*after):0;
  const drive=(live.motion===2?.22:.10)*phase*s,lean=Math.max(0,pose.lean||0)*.16*s;
  if(chest)chest.p=addv(chest.p,addv(mulv(right,swingSide*phase*s),mulv(forward,drive+lean)));
  if(head)head.p=addv(head.p,addv(mulv(right,swingSide*phase*s*.42),mulv(forward,(drive+lean)*.45)));
  if(hip)hip.p=addv(hip.p,mulv(forward,drive*.24));
 }
"""
s=s.replace(anchor,insert+anchor,1)
p.write_text(s,encoding='utf-8')
print('Applied MIRROR BREAK visual attack readability v1')
