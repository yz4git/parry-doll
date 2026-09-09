from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def patch(path,old,new,marker=None):
    p=ROOT/path
    text=p.read_text()
    if marker and marker in text:
        return False
    if old not in text:
        raise SystemExit(f'Expected patch anchor not found in {path}: {old[:80]!r}')
    p.write_text(text.replace(old,new,1))
    return True

engine=ROOT/'visual-src/engine.js'
text=engine.read_text()
if "./blender-heroine.js" not in text:
    text=text.replace("import {Heroine} from './heroine.js';", "import {Heroine} from './heroine.js';\nimport {BlenderHeroine} from './blender-heroine.js';",1)

old="export class Actor {\n constructor(d,scene,mats){if(d.player)return new Heroine(d,scene,mats,{Assembly,frame});"
if 'class HeroineSwitcher' not in text:
    block=r'''const HEROINE_APPEARANCE_KEY='parry-doll.heroineAppearance';
const heroineSwitchers=new Set();
const normalizeHeroineAppearance=value=>value==='blender'?'blender':'classic';
function readHeroineAppearance(){try{return normalizeHeroineAppearance(localStorage.getItem(HEROINE_APPEARANCE_KEY))}catch(_){return'classic'}}
let heroineAppearance=readHeroineAppearance();
function heroineAppearanceState(){const all=[...heroineSwitchers],ready=all.some(s=>s.blenderReady),active=heroineAppearance==='blender'&&ready?'blender':'classic';return{selected:heroineAppearance,active,blenderReady:ready}}
function setHeroineAppearance(value){heroineAppearance=normalizeHeroineAppearance(value);try{localStorage.setItem(HEROINE_APPEARANCE_KEY,heroineAppearance)}catch(_){}for(const s of heroineSwitchers)s.setAppearance(heroineAppearance);return heroineAppearanceState()}
class HeroineSwitcher{
 constructor(d,scene,mats,tools){this.root=new THREE.Group();this.root.name='heroine-appearance-switcher';scene.add(this.root);this.classic=new Heroine(d,this.root,mats,tools);this.blender=new BlenderHeroine(d,this.root,{assetBase:ASSET_BASE});this.appearance=heroineAppearance;this.weaponVisible=true;this.weaponProxy={};Object.defineProperty(this.weaponProxy,'visible',{get:()=>this.weaponVisible,set:value=>this.setWeaponVisible(value)});heroineSwitchers.add(this);this.updateVisibility()}
 get blenderReady(){return this.blender?.ready===true}
 get activeKind(){return this.appearance==='blender'&&this.blenderReady?'blender':'classic'}
 get weapon(){return this.weaponProxy}
 setAppearance(value){this.appearance=normalizeHeroineAppearance(value);this.updateVisibility();return this.activeKind}
 setWeaponVisible(value){this.weaponVisible=!!value;if(this.classic?.weapon)this.classic.weapon.visible=this.weaponVisible;this.blender?.setWeaponVisible?.(this.weaponVisible)}
 updateVisibility(){const blender=this.activeKind==='blender';if(this.classic?.root)this.classic.root.visible=!blender;if(this.blender?.root)this.blender.root.visible=blender;this.setWeaponVisible(this.weaponVisible)}
 update(d,pose,clock=0){this.appearance=heroineAppearance;if(this.activeKind==='blender')this.blender.update(d,pose,clock);else this.classic.update(d,pose,clock);this.updateVisibility()}
 dispose(){heroineSwitchers.delete(this);this.classic.dispose();this.blender.dispose();this.root.removeFromParent()}
}
window.ParryHeroineAppearance={get:()=>heroineAppearance,set:setHeroineAppearance,toggle:()=>setHeroineAppearance(heroineAppearance==='classic'?'blender':'classic'),state:heroineAppearanceState};
export class Actor {
 constructor(d,scene,mats){if(d.player)return new HeroineSwitcher(d,scene,mats,{Assembly,frame});'''
    if old not in text: raise SystemExit('Actor constructor anchor missing')
    text=text.replace(old,block,1)
engine.write_text(text)

viewer=ROOT/'dist/model-viewer.js'
v=viewer.read_text()
if 'heroineModelToggle' not in v:
    v=v.replace("#modelViewerOpen{position:static", "#modelViewerOpen,#heroineModelToggle{position:static",1)
    v=v.replace("#modelViewerOpen small{display:block", "#modelViewerOpen small,#heroineModelToggle small{display:block",1)
    old="const open=document.createElement('button');open.id='modelViewerOpen';open.type='button';open.innerHTML='モデルを見る<small>MODEL VIEWER</small>';const titleActions=document.createElement('div');titleActions.id='titleActions';start.parentNode.insertBefore(titleActions,start);titleActions.appendChild(start);titleActions.appendChild(open);"
    new="const open=document.createElement('button');open.id='modelViewerOpen';open.type='button';open.innerHTML='モデルを見る<small>MODEL VIEWER</small>';const modelToggle=document.createElement('button');modelToggle.id='heroineModelToggle';modelToggle.type='button';modelToggle.innerHTML='MODEL CLASSIC<small>HEROINE</small>';const titleActions=document.createElement('div');titleActions.id='titleActions';start.parentNode.insertBefore(titleActions,start);titleActions.appendChild(start);titleActions.appendChild(open);titleActions.appendChild(modelToggle);"
    if old not in v: raise SystemExit('model viewer title action anchor missing')
    v=v.replace(old,new,1)
    v=v.replace('<button class="mv-chip active" id="mvWeapon">武器</button><button class="mv-chip" id="mvReset">RESET</button>', '<button class="mv-chip active" id="mvWeapon">武器</button><button class="mv-chip" id="mvModel">MODEL CLASSIC</button><button class="mv-chip" id="mvReset">RESET</button>',1)
    oldsync="function sync(){const a=api(),state=a?.state?.();if(!state)return;ui.querySelectorAll('[data-preset]').forEach(b=>b.classList.toggle('active',b.dataset.preset===state.preset));$('mvAuto').classList.toggle('active',state.auto);$('mvAuto').textContent=state.auto?'AUTO':'MANUAL';$('mvWeapon').classList.toggle('active',state.weapon)}"
    newsync="function sync(){const a=api(),state=a?.state?.(),appearance=window.ParryHeroineAppearance?.state?.();if(state){ui.querySelectorAll('[data-preset]').forEach(b=>b.classList.toggle('active',b.dataset.preset===state.preset));$('mvAuto').classList.toggle('active',state.auto);$('mvAuto').textContent=state.auto?'AUTO':'MANUAL';$('mvWeapon').classList.toggle('active',state.weapon)}const selected=appearance?.selected==='blender'?'BLENDER':'CLASSIC',active=appearance?.active||'classic';$('mvModel').textContent='MODEL '+selected+(appearance?.selected==='blender'&&!appearance?.blenderReady?' …':'');$('mvModel').classList.toggle('active',active==='blender');modelToggle.innerHTML='MODEL '+selected+'<small>'+((appearance?.selected==='blender'&&!appearance?.blenderReady)?'LOADING':'HEROINE')+'</small>'}"
    if oldsync not in v: raise SystemExit('model viewer sync anchor missing')
    v=v.replace(oldsync,newsync,1)
    oldhandlers="open.addEventListener('click',enter);$('mvClose').addEventListener('click',leave);$('mvReset').addEventListener('click',()=>{api()?.reset?.();sync()});$('mvAuto').addEventListener('click',()=>{api()?.toggleAuto?.();sync()});$('mvWeapon').addEventListener('click',()=>{api()?.toggleWeapon?.();sync()});ui.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{api()?.preset?.(b.dataset.preset);sync()}));"
    newhandlers="open.addEventListener('click',enter);modelToggle.addEventListener('click',()=>{window.ParryHeroineAppearance?.toggle?.();sync()});$('mvClose').addEventListener('click',leave);$('mvReset').addEventListener('click',()=>{api()?.reset?.();sync()});$('mvAuto').addEventListener('click',()=>{api()?.toggleAuto?.();sync()});$('mvWeapon').addEventListener('click',()=>{api()?.toggleWeapon?.();sync()});$('mvModel').addEventListener('click',()=>{window.ParryHeroineAppearance?.toggle?.();sync();setTimeout(sync,250)});ui.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{api()?.preset?.(b.dataset.preset);sync()}));"
    if oldhandlers not in v: raise SystemExit('model viewer handlers anchor missing')
    v=v.replace(oldhandlers,newhandlers,1)
    v=v.replace("window.parryModelViewerUI={open:enter,close:leave,isOpen:()=>ui.classList.contains('show')};", "sync();setInterval(()=>{if(ui.classList.contains('show'))sync()},500);window.parryModelViewerUI={open:enter,close:leave,isOpen:()=>ui.classList.contains('show')};",1)
viewer.write_text(v)

style=ROOT/'dist/style.css'
s=style.read_text()
if '#titleActions #heroineModelToggle' not in s:
    s=s.replace("#titleActions #modelViewerOpen{flex:0 0 160px;min-width:0;margin:0;position:static!important;left:auto!important;right:auto!important;bottom:auto!important;top:auto!important;transform:none!important}", "#titleActions #modelViewerOpen{flex:0 0 145px;min-width:0;margin:0;position:static!important;left:auto!important;right:auto!important;bottom:auto!important;top:auto!important;transform:none!important}#titleActions #heroineModelToggle{flex:0 0 118px;min-width:0;margin:0;position:static!important;transform:none!important}",1)
    s=s.replace("#titleActions #modelViewerOpen{flex-basis:148px}", "#titleActions #modelViewerOpen{flex-basis:132px}#titleActions #heroineModelToggle{flex-basis:106px}",1)
    s=s.replace("#titleActions #modelViewerOpen{flex:0 0 auto;width:100%;min-height:44px}", "#titleActions #modelViewerOpen,#titleActions #heroineModelToggle{flex:0 0 auto;width:100%;min-height:44px}",1)
style.write_text(s)

print('Blender heroine integration enabled')
