import { chromium } from 'playwright';

const url = process.env.TEST_URL || 'https://yz4git.github.io/parry-doll/';
const seconds = Number(process.env.MASH_SECONDS || 70);
const interval = Number(process.env.MASH_INTERVAL_MS || 110);
const browser = await chromium.launch({headless:true});
const context = await browser.newContext({
  viewport: { width: 932, height: 430 },
  isMobile: true,
  hasTouch: true,
  deviceScaleFactor: 2,
});
const page = await context.newPage();
const events = [];
await page.goto(`${url}?mashcheck=${Date.now()}`, {waitUntil:'networkidle', timeout:60000});
await page.locator('#start').click();
await page.waitForFunction(() => window.parryDoll && window.parryDoll.snapshot().mode === 'play', null, {timeout:10000});

const started = Date.now();
let nextSample = 0;
while ((Date.now()-started) < seconds*1000) {
  await page.keyboard.press('Space');
  await page.waitForTimeout(interval);
  const t=(Date.now()-started)/1000;
  if(t>=nextSample){
    const s=await page.evaluate(()=>window.parryDoll.snapshot());
    events.push({t:Number(t.toFixed(1)),...s});
    nextSample += 2;
    if(s.mode==='won'||s.mode==='lost') break;
  }
}
const final=await page.evaluate(()=>window.parryDoll.snapshot());
const result={url,seconds,interval,final,events};
console.log(JSON.stringify(result,null,2));
await page.screenshot({path:'attack-mash-final.png', fullPage:true});
await browser.close();

// This reproducer is intentionally strict: attack-only play must never win or advance deep into the run.
if(final.mode==='won' || final.level>=2){
  console.error(`ANTI_MASH_FAIL: attack-only reached mode=${final.mode} level=${final.level}`);
  process.exit(2);
}
if(final.parries!==0){
  console.error(`TEST_INVALID: expected zero parries, got ${final.parries}`);
  process.exit(3);
}
console.log(`ANTI_MASH_PASS mode=${final.mode} level=${final.level} playerHP=${final.playerHP} bossHP=${final.bossHP}`);
