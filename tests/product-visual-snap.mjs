import { chromium } from 'playwright';
const url=process.env.TEST_URL||'https://yz4git.github.io/parry-doll/';
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:932,height:430},isMobile:true,hasTouch:true,deviceScaleFactor:1});
const page=await context.newPage();
await page.goto(`${url}?dodgecheck=${Date.now()}`,{waitUntil:'domcontentloaded',timeout:60000});
await page.waitForTimeout(7000);
await page.screenshot({path:'00-title.png'});
await page.waitForSelector('#dodge',{state:'attached',timeout:20000});
await page.evaluate(()=>document.getElementById('start')?.click());
await page.waitForFunction(()=>window.parryDoll&&window.parryDoll.snapshot().mode==='play'&&window.parryDodgeTest,null,{timeout:20000});
await page.evaluate(()=>window.parryDodgeTest.placeAtCombatRange());
await page.waitForTimeout(300);
await page.screenshot({path:'01-neutral.png'});

async function force(kind){
 for(let i=0;i<100;i++){
  const ok=await page.evaluate(k=>window.parryDodgeTest.forceAttack(k,true),kind);
  if(ok)return;
  await page.waitForTimeout(70);
 }
 throw new Error('force '+kind+' failed');
}
async function waitActionable(kind){
 const limit=kind==='parry'?.30:.12;
 await page.waitForFunction(({kind,limit})=>{
  const s=window.parryDoll.snapshot();
  return s.response===kind&&((s.enemyWind>0&&s.enemyWind<=limit)||s.enemyStrike>0);
 },{kind,limit},{timeout:12000,polling:20});
 return await page.evaluate(()=>({classes:[...document.body.classList],snapshot:window.parryDoll.snapshot()}));
}

// PARRY: wait until the UI says pressing now is valid, then use the actual touch button.
await page.evaluate(()=>window.parryDodgeTest.placeAtCombatRange());
await force('parry');
const parryCue=await waitActionable('parry');
console.log('PARRY_CUE',JSON.stringify(parryCue));
const parryBefore=await page.evaluate(()=>window.parryDoll.snapshot().parries);
await page.screenshot({path:'02-parry-telegraph.png'});
await page.locator('#parry').tap({force:true});
const parryResolved=await page.evaluate(()=>window.parryDodgeTest.resolveTouch('parry'));
console.log('PARRY_RESOLVED',JSON.stringify(parryResolved));
await page.waitForFunction(n=>window.parryDoll.snapshot().parries>n,parryBefore,{timeout:3500,polling:20});
await page.waitForTimeout(120);
await page.screenshot({path:'03-after-parry.png'});

// DODGE: same production touch path, only after the cyan cue enters its real evade window.
await page.evaluate(()=>window.parryDodgeTest.placeAtCombatRange());
await force('dodge');
const dodgeCueState=await waitActionable('dodge');
console.log('DODGE_CUE',JSON.stringify(dodgeCueState));
const dodgeBefore=await page.evaluate(()=>window.parryDoll.snapshot().dodges);
await page.screenshot({path:'04-dodge-telegraph.png'});
await page.locator('#dodge').tap({force:true});
const dodgeResolved=await page.evaluate(()=>window.parryDodgeTest.resolveTouch('dodge'));
console.log('DODGE_RESOLVED',JSON.stringify(dodgeResolved));
await page.waitForFunction(n=>window.parryDoll.snapshot().dodges>n,dodgeBefore,{timeout:3500,polling:20});
await page.waitForTimeout(120);
await page.screenshot({path:'05-after-dodge.png'});

const ui=await page.evaluate(()=>({snapshot:window.parryDoll.snapshot(),classes:[...document.body.classList],rects:Object.fromEntries(['bossHud','playerHud','controls','attack','dodge','parry','responseLegend','pbPhaseStrip','mbBreakHud','mbCores','cue','toast'].map(id=>{const e=document.getElementById(id);if(!e)return [id,null];const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return[id,{x:+r.x.toFixed(1),y:+r.y.toFixed(1),w:+r.width.toFixed(1),h:+r.height.toFixed(1),opacity:cs.opacity,display:cs.display,text:(e.textContent||'').trim().slice(0,120)}]}))}));
console.log(JSON.stringify(ui,null,2));
if(ui.snapshot.parries<1)throw new Error('visual playcheck: parry did not succeed');
if(ui.snapshot.dodges<1)throw new Error('visual playcheck: dodge did not succeed');
console.log(`VISUAL_PLAY_PASS parries=${ui.snapshot.parries} dodges=${ui.snapshot.dodges} hp=${ui.snapshot.playerHP}`);
await browser.close();
