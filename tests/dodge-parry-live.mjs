import { chromium } from 'playwright';

const url=process.env.TEST_URL||'https://yz4git.github.io/parry-doll/';
const seconds=Number(process.env.TEST_SECONDS||60);
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:932,height:430},isMobile:true,hasTouch:true,deviceScaleFactor:2});
const page=await context.newPage();
await page.goto(`${url}?dodgecheck=${Date.now()}`,{waitUntil:'networkidle',timeout:60000});
await page.waitForSelector('#dodge',{state:'visible',timeout:10000});
await page.locator('#start').tap();
await page.waitForFunction(()=>window.parryDoll&&window.parryDoll.snapshot().mode==='play',null,{timeout:10000});

await page.keyboard.down('KeyW');
const started=Date.now();
let handledThreat=false,lastAttack=0,nextSample=0;
const events=[];
while((Date.now()-started)<seconds*1000){
  const now=Date.now(),s=await page.evaluate(()=>window.parryDoll.snapshot());
  if(s.mode==='lost'||s.mode==='won')break;
  const threat=(s.enemyWind>0||s.enemyStrike>0)&&s.response;
  if(!threat)handledThreat=false;

  if(!handledThreat&&s.enemyWind>0){
    if(s.response==='dodge'&&s.enemyWind<0.34&&s.dodgeCool<=0){
      await page.locator('#dodge').tap();
      handledThreat=true;
    }else if(s.response==='parry'&&s.enemyWind<0.32){
      await page.locator('#parry').tap();
      handledThreat=true;
    }
  }

  if(!threat&&now-lastAttack>520){
    await page.locator('#attack').tap();
    lastAttack=now;
  }

  const t=(now-started)/1000;
  if(t>=nextSample){events.push({t:+t.toFixed(1),...s});nextSample+=2;}
  await page.waitForTimeout(65);
}
await page.keyboard.up('KeyW');
const final=await page.evaluate(()=>window.parryDoll.snapshot());
const result={url,scenario:'iphone-touch-attack-plus-color-coded-parry-and-dodge',final,events};
console.log(JSON.stringify(result,null,2));
await page.screenshot({path:'dodge-parry-final.png',fullPage:true});
await browser.close();

if(final.parries<1){console.error(`DODGE_MIX_FAIL: no successful parry, parries=${final.parries}`);process.exit(2)}
if(final.dodges<1){console.error(`DODGE_MIX_FAIL: no successful dodge, dodges=${final.dodges}`);process.exit(3)}
if(events.some(e=>e.response==='dodge')===false){console.error('DODGE_MIX_FAIL: dodge-only move never appeared');process.exit(4)}
console.log(`DODGE_MIX_PASS parries=${final.parries} dodges=${final.dodges} perfectDodges=${final.perfectDodges} level=${final.level} playerHP=${final.playerHP} bossHP=${final.bossHP}`);
