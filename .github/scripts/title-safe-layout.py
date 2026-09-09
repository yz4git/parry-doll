from pathlib import Path

css = Path('dist/style.css')
s = css.read_text()
marker = '/* TITLE SAFE LAYOUT v2 */'
if marker not in s:
    s += r'''

/* TITLE SAFE LAYOUT v2 */
html,body{width:100dvw;height:100dvh;min-width:0;min-height:0;max-width:none;max-height:none;overflow:hidden}
#overlay{position:fixed;inset:0;width:100dvw;height:100dvh;padding:max(10px,env(safe-area-inset-top)) max(14px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(14px,env(safe-area-inset-left));display:grid;place-items:center;overflow:hidden}
#overlay .panel{box-sizing:border-box;width:min(510px,calc(100dvw - max(14px,env(safe-area-inset-left)) - max(14px,env(safe-area-inset-right)) - 16px));max-width:100%;margin:0 auto}
#titleActions{display:flex;align-items:stretch;gap:8px;width:100%;margin-top:18px}
#titleActions #start{flex:1 1 auto;width:auto;min-width:0;margin-top:0}
#titleActions #modelViewerOpen{flex:0 0 160px;min-width:0;margin:0;position:static!important;left:auto!important;right:auto!important;bottom:auto!important;top:auto!important;transform:none!important}
@media(max-height:500px) and (orientation:landscape){#overlay .panel{padding:7px 22px}#titleActions{margin-top:9px;gap:7px}#titleActions #modelViewerOpen{flex-basis:148px}}
@media(orientation:portrait){#overlay{align-items:center}#overlay .panel{width:min(510px,calc(100dvw - max(14px,env(safe-area-inset-left)) - max(14px,env(safe-area-inset-right)) - 12px));padding:18px 20px}#titleActions{flex-direction:column;gap:8px;margin-top:14px}#titleActions #modelViewerOpen{flex:0 0 auto;width:100%;min-height:44px}#help p{font-size:12px;line-height:1.45}h1{font-size:clamp(36px,12vw,56px)}}
@media(max-width:390px) and (orientation:portrait){#overlay .panel{padding:14px 16px}.panel p{font-size:13px}#help p{font-size:11px;margin:4px 0}#start{padding:13px 16px;font-size:16px}.panel .foot{margin-top:8px}}
'''
css.write_text(s)

ui = Path('dist/model-viewer.js')
u = ui.read_text()
old_style = "#modelViewerOpen{position:fixed;z-index:60;right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom));width:auto;margin:0;border:1px solid rgba(210,236,246,.38);background:rgba(11,22,31,.72);color:#eaf8ff;padding:10px 14px;font:600 11px/1.05 system-ui;letter-spacing:.16em;border-radius:3px;backdrop-filter:blur(12px);box-shadow:0 8px 26px rgba(0,0,0,.22)}"
new_style = "#modelViewerOpen{position:static;z-index:auto;width:auto;margin:0;border:1px solid rgba(210,236,246,.38);background:rgba(11,22,31,.72);color:#eaf8ff;padding:10px 12px;font:600 11px/1.05 system-ui;letter-spacing:.13em;border-radius:3px;backdrop-filter:blur(12px);box-shadow:0 8px 26px rgba(0,0,0,.22);white-space:nowrap}"
if old_style in u:
    u = u.replace(old_style, new_style)
elif new_style not in u:
    raise SystemExit('model viewer style anchor missing')

old_insert = "const open=document.createElement('button');open.id='modelViewerOpen';open.type='button';open.innerHTML='モデルを見る<small>MODEL VIEWER</small>';start.insertAdjacentElement('afterend',open);"
new_insert = "const open=document.createElement('button');open.id='modelViewerOpen';open.type='button';open.innerHTML='モデルを見る<small>MODEL VIEWER</small>';const titleActions=document.createElement('div');titleActions.id='titleActions';start.parentNode.insertBefore(titleActions,start);titleActions.appendChild(start);titleActions.appendChild(open);"
if old_insert in u:
    u = u.replace(old_insert, new_insert)
elif new_insert not in u:
    raise SystemExit('model viewer insert anchor missing')

old_hidden = "const gesture=$('modelViewerGesture'),hidden=[document.querySelector('header'),...['bossHud','playerHud','controls','cue','toast','parrySuccessHud'].map(id=>$(id))].filter(Boolean);"
new_hidden = "const gesture=$('modelViewerGesture'),hidden=[document.querySelector('header'),...['bossHud','playerHud','controls','cue','toast','parrySuccessHud','pbPhaseStrip','pbResolve','pbChain','pbDanger','pbBanner','pbCineBars','pbResolveBurst'].map(id=>$(id))].filter(Boolean);"
if old_hidden in u:
    u = u.replace(old_hidden, new_hidden)
ui.write_text(u)

# Keep generator source aligned with the deployed UI.
gen = Path('.github/scripts/model-viewer.sh')
g = gen.read_text()
g = g.replace("#modelViewerOpen{margin-top:10px;width:100%;border:1px solid rgba(210,236,246,.34);background:rgba(11,22,31,.58);color:#eaf8ff;padding:12px 16px;font:600 12px/1.1 system-ui;letter-spacing:.18em;border-radius:3px;backdrop-filter:blur(10px)}", new_style)
g = g.replace(old_insert, new_insert)
g = g.replace("const gesture=$('modelViewerGesture'),hidden=['header','bossHud','playerHud','controls','cue','toast'].map(id=>$(id)).filter(Boolean);", new_hidden)
gen.write_text(g)
