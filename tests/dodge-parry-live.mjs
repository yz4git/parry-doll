import { chromium } from 'playwright';

const url=process.env.TEST_URL||'https://yz4git.github.io/parry-doll/';
const seconds=Number(process.env.TEST_SECONDS||30);
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:844,height:390},isMobile:true,hasTouch:true,deviceScaleFactor:1});
// The live game uses a fixed 60 Hz simulation, but heavy headless canvas rendering can
// throttle requestAnimationFrame to a few frames per second. Feed deterministic 33 ms
// frame timestamps so several real boss attacks can be exercised while still using the
// production code and the real touch handlers.
await context.addInitScript(()=>{
  let virtualNow=0;
  window.requestAnimationFrame=cb=>setTimeout(()=>{virtualNow+=33;cb(virtualNow)},4);
  window.cancelAnimationFrame=id=>clearTimeout(id);
});
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

  if(!s.response){
    if(s.spacing>2.35)await setForward(true);
    else if(s.spacing<2.05)await setForward(false);
  }else await setForward(false);

  if(s.response==='dodge'){
    sawDodgeMove=true;
    if(s.enemyWind>0&&s.enemyWind<0.12&&s.dodgeCool<=0&&now-lastDodge>350){
      await page.locator('#dodge').tap();lastDodge=now;
    }else if(s.enemyStrike>0&&s.dodgeCool<=0&&s.dodgeTimer<=0&&now-lastDodge>420){
      await page.locator('#dodge').tap();lastDodge=now;
    }
  }else if(s.response==='parry'){
    sawParryMove=true;
    if(s.enemyWind>0&&s.enemyWind<0.15&&s.parryActive<=0.03&&now-lastParry>260){
      await page.locator('#parry').tap();lastParry=now;
    }else if(s.enemyStrike>0&&s.parryActive<=0.03&&now-lastParry>300){
      await page.locator('#parry').tap();lastParry=now;
    }
  }

  if(s.parries>0&&s.dodges>0&&!s.response&&now-lastAttack>500){
    await page.locator('#attack').tap();lastAttack=now;
  }

  const t=(now-started)/1000;
  if(t>=nextSample){events.push({t:+t.toFixed(1),...s});nextSample+=.5;}
  if(s.parries>=1&&s.dodges>=1&&sawParryMove&&sawDodgeMove)break;
  await page.waitForTimeout(20);
}
await setForward(false);
const final=await page.evaluate(()=>window.parryDoll.snapshot());
const result={url,scenario:'iphone-touch-color-coded-parry-and-dodge-accelerated-fixed-step',sawParryMove,sawDodgeMove,final,events};
console.log(JSON.stringify(result,null,2));
await page.screenshot({path:'dodge-parry-final.png',fullPage:true});
await browser.close();

if(!sawParryMove){console.error('DODGE_MIX_FAIL: no gold parry move appeared');process.exit(2)}
if(!sawDodgeMove){console.error('DODGE_MIX_FAIL: no cyan dodge-only move appeared');process.exit(3)}
if(final.parries<1){console.error(`DODGE_MIX_FAIL: no successful parry, parries=${final.parries}`);process.exit(4)}
if(final.dodges<1){console.error(`DODGE_MIX_FAIL: no successful dodge, dodges=${final.dodges}`);process.exit(5)}
console.log(`DODGE_MIX_PASS parries=${final.parries} dodges=${final.dodges} perfectDodges=${final.perfectDodges} level=${final.level} playerHP=${final.playerHP} bossHP=${final.bossHP}`);
