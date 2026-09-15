import { chromium } from 'playwright';

const base=process.env.TEST_URL||'https://yz4git.github.io/parry-doll/';
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:844,height:390},isMobile:true,hasTouch:true,deviceScaleFactor:1});
const page=await context.newPage();
await page.goto(`${base}?safetycheck=${Date.now()}`,{waitUntil:'networkidle',timeout:60000});
await page.waitForSelector('#start',{state:'visible',timeout:15000});
await page.locator('#start').tap();
await page.waitForFunction(()=>window.parryDoll&&window.parryDoll.snapshot().mode==='play'&&window.parrySafetyTest,null,{timeout:15000});

const hp=[];
hp.push((await page.evaluate(()=>window.parryDoll.snapshot())).playerHP);
for(let i=0;i<4;i++){
  await page.evaluate(()=>window.parrySafetyTest.takeHit(999));
  await page.waitForTimeout(40);
  hp.push((await page.evaluate(()=>window.parryDoll.snapshot())).playerHP);
}
const lethalState=await page.evaluate(()=>window.parryDoll.snapshot());

await page.evaluate(()=>window.parrySafetyTest.stress(350));
await page.evaluate(()=>window.parrySafetyTest.corruptVelocity());
await page.waitForTimeout(1200);
const final=await page.evaluate(()=>({snapshot:window.parryDoll.snapshot(),stats:window.parrySafetyTest.stats()}));
await page.screenshot({path:'combat-safety-final.png',fullPage:true});
await browser.close();

const result={hp,lethalState,final};
console.log(JSON.stringify(result,null,2));

const expected=[100,72,44,16,1];
if(hp.length!==expected.length||hp.some((v,i)=>v!==expected[i])){
  console.error(`SAFETY_FAIL damage ladder=${JSON.stringify(hp)} expected=${JSON.stringify(expected)}`);process.exit(2);
}
if(lethalState.mode!=='play'||lethalState.playerHP!==1){
  console.error(`SAFETY_FAIL lethal protection mode=${lethalState.mode} hp=${lethalState.playerHP}`);process.exit(3);
}
if(final.snapshot.mode!=='play'||!final.snapshot.finite){
  console.error(`SAFETY_FAIL loop/physics mode=${final.snapshot.mode} finite=${final.snapshot.finite}`);process.exit(4);
}
if(final.stats.particles>220||final.stats.rings>20||final.stats.shapes>320){
  console.error(`SAFETY_FAIL effect caps ${JSON.stringify(final.stats)}`);process.exit(5);
}
console.log(`SAFETY_PASS hp=${hp.join('>')} particles=${final.stats.particles} rings=${final.stats.rings} shapes=${final.stats.shapes} recoveries=${final.stats.frameRecoveries}`);
