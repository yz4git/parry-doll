from pathlib import Path
p=Path(__file__).resolve().parents[1]/'dist/phase-break.js'
s=p.read_text(encoding='utf-8')
old="shake=Math.max(shake,next===3?.22:.16);feel.flash=Math.max(feel.flash,next===3?.12:.07);feel.pulse=Math.max(feel.pulse,.12);"
new="shake=Math.max(shake,next===3?.22:.16);hitstop=Math.max(hitstop,next===3?.055:.035);feel.slow=Math.max(feel.slow,next===3?.10:.07);feel.flash=Math.max(feel.flash,next===3?.12:.07);feel.pulse=Math.max(feel.pulse,.12);"
if old not in s: raise SystemExit('phase impact target not found')
p.write_text(s.replace(old,new),encoding='utf-8')
print('brief_phase_hitstop_and_slow=ok')
