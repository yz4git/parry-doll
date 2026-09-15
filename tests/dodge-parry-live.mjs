import { chromium } from 'playwright';

const url=process.env.TEST_URL||'https://yz4git.github.io/parry-doll/';
const seconds=Number(process.env.TEST_SECONDS||75);
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:932,height:430},isMobile:true,hasTouch:true,deviceScaleFactor:2});
const page=await context.newPage();
await page.goto(`${url}?dodgecheck=${Date.now()}`,{waitUntil:'networkidle',timeout:60000});
await page.waitForSelector('#dodge',{state:'visible',timeout:10000});
await page.locator('#start').tap();
await page.waitForFunction(()=>window.parryDoll&&window.parryDoll.snapshot().mode==='play',null,{timeout:10000});

const started=Date.now();
let forwardHeld=false,lastParry=0,lastDodge=0,lastAttack=0,nextSample=0,sawDodgeMove=false,sawParryMove=false;
const events=[];

async function setForward(on){
  if(on===forwardHeld)return;
  if(on)await page.keyboard.down('KeyW');else await page.keyboard.up('KeyW');
  forwardHeld=on;
}

while((Date.now()-started)<seconds*1000){
  const now=Date.now(),s=await page.evaluate(()=>window.parryDoll.snapshot());
  if(s.mode==='lost'||s.mode==='won')break;

  // Stay close enough that the response is actually tested, without blindly walking
  // through the opponent during its telegraphed attack.
  if(!s.response){
    if(s.spacing>2.35)await setForward(true);
    else if(s.spacing<2.05)await setForward(false);
  }else await setForward(false);

  if(s.response==='dodge'){
    sawDodgeMove=true;
    // Tap late in the cyan wind-up so the dodge window overlaps the active hit.
    if(s.enemyWind>0&&s.enemyWind<0.12&&s.dodgeCool<=0&&now-lastDodge>450){
      await page.locator('#dodge').tap();lastDodge=now;
    }
  }else if(s.response==='parry'){
    sawParryMove=true;
    // Gold attacks are answered just before commitment. Multi-hit attacks may require
    // another parry after the first active beat, so retry only when the parry is inactive.
    if(s.enemyWind>0&&s.enemyWind<0.15&&s.parryActive<=0.03&&now-lastParry>330){
      await page.locator('#parry').tap();lastParry=now;
    }else if(s.enemyStrike>0&&s.parryActive<=0.03&&now-lastParry>360){
      await page.locator('#parry').tap();lastParry=now;
    }
  }

  // Once both defensive mechanics have been proven, exercise ATTACK too so the three
  // touch buttons are verified together in the live build.
  if(s.parries>0&&s.dodges>0&&!s.response&&now-lastAttack>650){
    await page.locator('#attack').tap();lastAttack=now;
  }

  const t=(now-started)/1000;
  if(t>=nextSample){events.push({t:+t.toFixed(1),...s});nextSample+=1;}
  if(s.parries>=1&&s.dodges>=1&&t>8)break;
  await page.waitForTimeout(35);
}
await setForward(false);
const final=await page.evaluate(()=>window.parryDoll.snapshot());
const result={url,scenario:'iphone-touch-color-coded-parry-and-dodge',sawParryMove,sawDodgeMove,final,events};
console.log(JSON.stringify(result,null,2));
await page.screenshot({path:'dodge-parry-final.png',fullPage:true});
await browser.close();

if(!sawParryMove){console.error('DODGE_MIX_FAIL: no gold parry move appeared');process.exit(2)}
if(!sawDodgeMove){console.error('DODGE_MIX_FAIL: no cyan dodge-only move appeared');process.exit(3)}
if(final.parries<1){console.error(`DODGE_MIX_FAIL: no successful parry, parries=${final.parries}`);process.exit(4)}
if(final.dodges<1){console.error(`DODGE_MIX_FAIL: no successful dodge, dodges=${final.dodges}`);process.exit(5)}
console.log(`DODGE_MIX_PASS parries=${final.parries} dodges=${final.dodges} perfectDodges=${final.perfectDodges} level=${final.level} playerHP=${final.playerHP} bossHP=${final.bossHP}`);
