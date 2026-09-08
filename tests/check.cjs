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
reset();mode='play';player.pos=V(0,0,1);boss.pos=V();boss.stun=3;playerAttack();if(boss.hp!==70)throw Error('Finisher damage');
reset();mode='play';boss.hp=0;transition=0;step(1/60);if(level!==1)throw Error('Boss progression');
reset(3);mode='play';boss.hp=0;transition=0;step(1/60);if(mode!=='won')throw Error('Ending');
reset();mode='play';player.hp=0;transition=0;step(1/60);if(mode!=='lost')throw Error('Defeat');
console.log('PASS: all four boss attacks, parry, damage, physics stability, joints, finisher, progression, victory and defeat');
`,context);
