import { chromium } from 'playwright';

const url=process.env.TEST_URL||'https://yz4git.github.io/parry-doll/';
const timeoutMs=Number(process.env.TEST_TIMEOUT_MS||150000);
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:932,height:430},isMobile:true,hasTouch:true,deviceScaleFactor:1});
const page=await context.newPage();
await page.goto(`${url}?dodgecheck=${Date.now()}`,{waitUntil:'networkidle',timeout:60000});
await page.waitForSelector('#dodge',{state:'visible',timeout:10000});
await page.locator('#start').tap();
await page.waitForFunction(()=>window.parryDoll&&window.parryDoll.snapshot().mode==='play'&&window.parryDodgeTest,null,{timeout:10000});

const catalog=await page.evaluate(()=>window.parryDodgeTest.catalog());
if(catalog.length!==4||catalog.some(group=>group.length<2||group.some(m=>m.response!=='dodge'))){
  console.error('DODGE_MIX_FAIL: expected two dodge-only attacks for every boss',JSON.stringify(catalog));
  process.exit(6);
}
await page.evaluate(()=>window.parryDodgeTest.placeAtCombatRange());

const started=Date.now(),events=[];
let parryShot=false,dodgeShot=false;
async function snap(tag){const s=await page.evaluate(()=>window.parryDoll.snapshot());events.push({tag,t:+((Date.now()-started)/1000).toFixed(2),...s});return s}
async function forceWhenReady(kind){
  while(Date.now()-started<timeoutMs){
    const ok=await page.evaluate(k=>window.parryDodgeTest.forceAttack(k),kind);
    if(ok)return;
    await page.waitForTimeout(120);
  }
  throw new Error(`timeout forcing ${kind}`);
}
async function waitResponse(kind){
  while(Date.now()-started<timeoutMs){
    const s=await snap(`wait-${kind}`);
    if(s.response===kind&&s.enemyWind>0)return s;
    await page.waitForTimeout(90);
  }
  throw new Error(`timeout seeing ${kind}`);
}

// GOLD: actual production attack + actual PARRY touch button.
await forceWhenReady('parry');
await waitResponse('parry');
await page.screenshot({path:'parry-telegraph.png',fullPage:true});parryShot=true;
while(Date.now()-started<timeoutMs){
  const s=await snap('parry-window');
  if(s.parries>=1)break;
  if(s.response==='parry'&&s.enemyWind>0&&s.enemyWind<.26&&s.parryActive<=.03){await page.locator('#parry').tap()}
  else if(s.response==='parry'&&s.enemyStrike>0&&s.parryActive<=.03){await page.locator('#parry').tap()}
  await page.waitForTimeout(75);
}
let afterParry=await snap('after-parry');
if(afterParry.parries<1){console.error('DODGE_MIX_FAIL: gold attack was not parried');process.exit(4)}

// CYAN: wait until the first attack has fully released, then force a real dodge-only move.
await forceWhenReady('dodge');
await waitResponse('dodge');
await page.screenshot({path:'dodge-telegraph.png',fullPage:true});dodgeShot=true;
while(Date.now()-started<timeoutMs){
  const s=await snap('dodge-window');
  if(s.dodges>=1)break;
  if(s.response==='dodge'&&s.enemyWind>0&&s.enemyWind<.14&&s.dodgeCool<=0){await page.locator('#dodge').tap()}
  else if(s.response==='dodge'&&s.enemyStrike>0&&s.dodgeCool<=0&&s.dodgeTimer<=0){await page.locator('#dodge').tap()}
  await page.waitForTimeout(75);
}
const final=await snap('final');
await page.screenshot({path:'dodge-parry-final.png',fullPage:true});
const result={url,scenario:'iphone-touch-forced-real-gold-then-cyan',catalog,parryShot,dodgeShot,final,events};
console.log(JSON.stringify(result,null,2));
await browser.close();

if(final.parries<1){console.error(`DODGE_MIX_FAIL: parries=${final.parries}`);process.exit(4)}
if(final.dodges<1){console.error(`DODGE_MIX_FAIL: dodges=${final.dodges}`);process.exit(5)}
console.log(`DODGE_MIX_PASS bosses=${catalog.length} dodgeMoves=${catalog.reduce((n,g)=>n+g.length,0)} parries=${final.parries} dodges=${final.dodges} perfectDodges=${final.perfectDodges}`);
