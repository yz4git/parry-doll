from pathlib import Path

root = Path(__file__).resolve().parents[1]

# 1) Phase-break core: phase text must not cancel attacks, stun actors, hitstop, or slow time.
p = root / 'dist/phase-break.js'
s = p.read_text(encoding='utf-8')
old = """function doPhaseBreak(next){\n  pb.phase=next;tuneBoss();boss.wind=0;boss.strike=0;boss.pattern=null;boss.stun=Math.max(boss.stun,next===3?1.22:1.02);boss.ai=Math.max(boss.ai,.85);\n  const p=boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1]?.p||boss.pos;\n  ring(V(boss.pos.x,.05,boss.pos.z),PHASE_COLORS[next-1]);ring(V(boss.pos.x,.05,boss.pos.z),'#fff0bd');burst(p,PHASE_COLORS[next-1],next===3?38:26,next===3?8:6);\n  impact(p,'break',next===3?2.1:1.65);shake=Math.max(shake,next===3?.36:.26);hitstop=Math.max(hitstop,next===3?.09:.06);feel.flash=Math.max(feel.flash,next===3?.15:.09);feel.slow=Math.max(feel.slow,next===3?.24:.14);\n  $('pbDanger')?.classList.remove('show');if($('attackHud'))$('attackHud').textContent='';showBanner(phaseName(next),next===3?'FINAL PHASE':'PHASE BREAK',next===3?1.35:1.05);combatSound('break');updatePhaseUI();\n }"""
new = """function doPhaseBreak(next){\n  // Non-blocking phase transition: the banner is presentation only. Preserve the current\n  // enemy move, player input, velocities, AI timer and simulation speed while it is shown.\n  pb.phase=next;tuneBoss();\n  const p=boss.nodes.find(n=>n.name==='chest')?.p||boss.nodes[1]?.p||boss.pos;\n  ring(V(boss.pos.x,.05,boss.pos.z),PHASE_COLORS[next-1]);ring(V(boss.pos.x,.05,boss.pos.z),'#fff0bd');burst(p,PHASE_COLORS[next-1],next===3?38:26,next===3?8:6);\n  shake=Math.max(shake,next===3?.22:.16);feel.flash=Math.max(feel.flash,next===3?.12:.07);feel.pulse=Math.max(feel.pulse,.12);\n  showBanner(phaseName(next),next===3?'FINAL PHASE':'PHASE BREAK',next===3?1.35:1.05);combatSound('break');updatePhaseUI();\n }"""
if old not in s:
    raise SystemExit('phase-break.js doPhaseBreak target not found')
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')

# 2) Cinematic overlay: remove gameplay freeze/stun/input suppression/slowdown.
p = root / 'dist/phase-break-v2.js'
s = p.read_text(encoding='utf-8')
old = """function beginCinema(duration=2.25,label=phaseName(),sub='PHASE TRANSITION'){state.cineT=state.cineMax=duration;state.cinePhase=diag()?.phase||1;state.cineLevel=level;const c=$('pbCineCaption');if(c){c.querySelector('span').textContent=sub;c.querySelector('b').textContent=label}cine.classList.add('show');player.stun=Math.max(player.stun,duration*.78);boss.stun=Math.max(boss.stun,duration*.82);player.invuln=Math.max(player.invuln,.45);boss.ai=Math.max(boss.ai,duration*.7);player.vel=V();boss.vel=V();attackQueued=parryQueued=false;attackBuffer=parryBuffer=0;feel.slow=Math.max(feel.slow,.28);feel.pulse=Math.max(feel.pulse,.22);shake=Math.max(shake,.12)}"""
new = """function beginCinema(duration=2.25,label=phaseName(),sub='PHASE TRANSITION'){state.cineT=state.cineMax=duration;state.cinePhase=diag()?.phase||1;state.cineLevel=level;const c=$('pbCineCaption');if(c){c.querySelector('span').textContent=sub;c.querySelector('b').textContent=label}cine.classList.add('show');feel.pulse=Math.max(feel.pulse,.16);shake=Math.max(shake,.07)}"""
if old not in s:
    raise SystemExit('phase-break-v2.js beginCinema target not found')
s = s.replace(old, new)
old = """const v2Attack=playerAttack;playerAttack=function(){if(state.cineT>0||state.ultimateT>0)return false;const ok=v2Attack();if(ok)state.attacks++;return ok};"""
new = """const v2Attack=playerAttack;playerAttack=function(){if(state.ultimateT>0)return false;const ok=v2Attack();if(ok)state.attacks++;return ok};"""
if old not in s:
    raise SystemExit('phase-break-v2.js attack gate target not found')
s = s.replace(old, new)
old = """if(state.cineT>0){state.cineT=Math.max(0,state.cineT-dt);player.vel=V();boss.vel=V();player.stun=Math.max(player.stun,state.cineT+.08);boss.stun=Math.max(boss.stun,state.cineT+.1);boss.wind=0;boss.strike=0;attackQueued=parryQueued=false;attackBuffer=parryBuffer=0;if(state.cineT<=0)finishCinema()}"""
new = """if(state.cineT>0){state.cineT=Math.max(0,state.cineT-dt);if(state.cineT<=0)finishCinema()}"""
if old not in s:
    raise SystemExit('phase-break-v2.js cinema step target not found')
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')

# 3) Signature AI should also keep running while the phase title is visible.
p = root / 'dist/phase-break-v3.js'
s = p.read_text(encoding='utf-8')
old = """function canSpecial(){const vv=v2();return mode==='play'&&boss?.hp>0&&player?.hp>0&&boss.stun<=0&&boss.wind<=0&&boss.strike<=0&&boss.broken<=0&&!(vv?.cineT>0)&&!(vv?.ultimateT>0)}"""
new = """function canSpecial(){const vv=v2();return mode==='play'&&boss?.hp>0&&player?.hp>0&&boss.stun<=0&&boss.wind<=0&&boss.strike<=0&&boss.broken<=0&&!(vv?.ultimateT>0)}"""
if old not in s:
    raise SystemExit('phase-break-v3.js canSpecial target not found')
s = s.replace(old, new)
old = """if(mode==='play'&&boss?.hp>0&&player?.hp>0&&!(vv?.cineT>0)){s.specialClock+=dt;"""
new = """if(mode==='play'&&boss?.hp>0&&player?.hp>0){s.specialClock+=dt;"""
if old not in s:
    raise SystemExit('phase-break-v3.js specialClock target not found')
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')

print('phase_text_nonblocking=ok')
