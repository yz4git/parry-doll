const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const noop=()=>{},elements=new Map();const context2d=new Proxy({createLinearGradient:()=>({addColorStop:noop})},{get:(o,k)=>o[k]||noop});
function el(id){if(!elements.has(id))elements.set(id,{style:{},classList:{add:noop,remove:noop},addEventListener:noop,getContext:()=>context2d,getBoundingClientRect:()=>({left:0,top:0,width:130}),setPointerCapture:noop});return elements.get(id)}
const context={console,Math,Number,Set,innerWidth:844,innerHeight:390,devicePixelRatio:2,document:{getElementById:el,addEventListener:noop,querySelectorAll:()=>[]},window:{},addEventListener:noop,requestAnimationFrame:noop};vm.createContext(context);vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'../dist/game.js'),'utf8'),context);
vm.runInContext(`
for(let l=0;l<4;l++){
 reset(l);mode='play';for(let k=0;k<600;k++)step(1/60);
 if(!window.parryDoll.snapshot().finite)throw Error('Non-finite physics '+l);
 if(player.hp>=100)throw Error('Enemy cannot hit '+l);
 reset(l);mode='play';boss.pos=V(0,0,0);player.pos=V(0,0,2);player.parry=.45;enemyImpact();if(parries!==1||player.hp!==100)throw Error('Parry failure '+l);
 boss.stun=0;player.parry=0;player.invuln=0;enemyImpact();if(player.hp>=100)throw Error('Damage failure '+l);
 for(let k=0;k<120;k++){player.physics(1/60);boss.physics(1/60)}
 if(!window.parryDoll.snapshot().finite)throw Error('Impulse instability '+l);
 for(const d of [player,boss])for(const link of d.links){const error=Math.abs(len(sub(d.nodes[link.a].p,d.nodes[link.b].p))-link.length);if(error>.15)throw Error('Joint stretch '+error)}
 render();
}
reset();mode='play';player.pos=V(0,0,1);boss.pos=V();boss.stun=3;boss.broken=3;playerAttack();for(let i=0;i<12;i++)step(1/60);if(boss.hp!==70)throw Error('Finisher damage');
reset();mode='play';boss.hp=0;transition=0;step(1/60);if(level!==1)throw Error('Boss progression');
reset(3);mode='play';boss.hp=0;transition=0;step(1/60);if(mode!=='won')throw Error('Ending');
reset();mode='play';player.hp=0;transition=0;step(1/60);if(mode!=='lost')throw Error('Defeat');
console.log('PASS: all four boss attacks, parry, damage, physics stability, joints, finisher, progression, victory and defeat');
`,context);

vm.runInContext(`
function tick(n){for(let i=0;i<n;i++){updateFeel(1/60);step(1/60)}}
function near(l=0){reset(l);mode='play';player.pos=V(0,0,1.8);boss.pos=V();boss.ai=99;tick(20)}
// A buffered press near recovery must produce the second swing, not disappear.
near();attackQueued=true;tick(9);const afterFirst=boss.hp;attackQueued=true;tick(17);
if(combo!==1||boss.hp>=afterFirst)throw Error('Buffered combo was dropped');
// Input priority: parry cancels an uncommitted swing and never damages during the cancel.
near();playerAttack();parryQueued=true;tick(12);if(boss.hp!==boss.spec.hp)throw Error('Cancelled swing dealt damage');
// Timed counter is consumed by one attack and adds actual damage.
near();player.parry=.45;enemyImpact();playerAttack();tick(9);if(boss.hp!==boss.spec.hp-27)throw Error('Counter damage');if(player.counter!==0)throw Error('Counter reused');
// Missing should create a trail but never deal damage at distance.
reset();mode='play';player.pos=V(0,0,8);boss.pos=V(0,0,-8);boss.ai=99;playerAttack();tick(12);if(boss.hp!==boss.spec.hp)throw Error('Out of range damage');
// A light strike must not erase an enemy wind-up.
near();boss.wind=.7;playerAttack();tick(8);if(boss.wind<=0)throw Error('Light hit erased windup');
// A knockdown recovers at the fallen hip without non-finite values or floor penetration.
for(let l=0;l<4;l++){
 near(l);hurt(boss,25,V(32,12,0),boss.nodes[1].p);tick(240);
 if(!window.parryDoll.snapshot().finite)throw Error('Knockdown numerical failure');
 if(boss.down!==0)throw Error('Never stood up');
 if(boss.nodes.some(n=>n.p.y<n.r-.001))throw Error('Floor penetration');
}
// The first gold cue must still allow a successful parry when pressed immediately.
for(let l=0;l<4;l++){
 near(l);boss.wind=.35;playerParry();tick(33);if(parries!==1)throw Error('Gold cue too early '+l);
}
// Effects are bounded and decay even while the simulation is frozen.
near();for(let i=0;i<100;i++){impact(player.pos,'parry');slash(player,{combo:1});burst(player.pos,'#fff',10)}
if(feel.impacts.length>12||feel.slashes.length>8||particles.length>260)throw Error('Unbounded effects');
for(let i=0;i<90;i++)updateFeel(1/60);if(feel.impacts.length||feel.slashes.length||feel.flash>0)throw Error('Effects did not expire');
// Smoke-render landscape and portrait, including every boss and reduced motion.
for(const size of [[844,390],[390,844]]){W=size[0];H=size[1];for(let l=0;l<4;l++){reset(l);for(let i=0;i<40;i++){updateFeel(1/60);render()}for(const d of [player,boss]){const p=project(d.nodes[2].p);if(p.x<0||p.x>W||p.y<0||p.y>H)throw Error('Fighter outside viewport')}}}
feel.reduced=true;render();console.log('PASS: buffering, cancel, counter, whiff, windup, knockdowns, cue timing, effects and portrait/landscape projection');
`,context);
vm.runInContext(`
reset();mode='play';let cleared=false;
for(let i=0;i<24000;i++){
 if(mode==='won'){cleared=true;break}if(mode==='lost')throw Error('Assisted full run died');
 const v=sub(boss.pos,player.pos),d=len(v);input.x=d>2?v.x/d:0;input.z=d>2?v.z/d:0;
 if(boss.wind>0&&boss.wind<.3&&player.parryCool===0)parryQueued=true;
 else if(boss.wind===0&&player.parry===0&&i%17===0)attackQueued=true;
 updateFeel(1/60);step(1/60);
 if(!window.parryDoll.snapshot().finite)throw Error('Full-run physics failed');
}
if(!cleared)throw Error('Full run stalled');
console.log('PASS: complete four-boss run via movement, attack and parry inputs');
`,context);
