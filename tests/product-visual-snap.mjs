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
 for(let i=0;i<80;i++){
  const ok=await page.evaluate(k=>window.parryDodgeTest.forceAttack(k),kind);
  if(ok)return;
  await page.waitForTimeout(80);
 }
 throw new Error('force '+kind+' failed');
}
async function waitWind(kind){
 await page.waitForFunction(k=>{const s=window.parryDoll.snapshot();return s.response===k&&s.enemyWind>0},kind,{timeout:12000});
}
await force('parry'); await waitWind('parry'); await page.waitForTimeout(120); await page.screenshot({path:'02-parry-telegraph.png'});
await page.evaluate(()=>document.getElementById('parry')?.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:7,pointerType:'touch'}))); await page.waitForTimeout(750);
await page.screenshot({path:'03-after-parry.png'});
await force('dodge'); await waitWind('dodge'); await page.waitForTimeout(120); await page.screenshot({path:'04-dodge-telegraph.png'});
await page.evaluate(()=>document.getElementById('dodge')?.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:8,pointerType:'touch'}))); await page.waitForTimeout(450);
await page.screenshot({path:'05-after-dodge.png'});
const ui=await page.evaluate(()=>({snapshot:window.parryDoll.snapshot(),rects:Object.fromEntries(['bossHud','playerHud','controls','attack','dodge','parry','responseLegend','pbPhaseStrip','mbBreakHud','mbCores','cue','toast'].map(id=>{const e=document.getElementById(id);if(!e)return [id,null];const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return[id,{x:+r.x.toFixed(1),y:+r.y.toFixed(1),w:+r.width.toFixed(1),h:+r.height.toFixed(1),opacity:cs.opacity,display:cs.display,text:(e.textContent||'').trim().slice(0,120)}]}))}));
console.log(JSON.stringify(ui,null,2));
await browser.close();
