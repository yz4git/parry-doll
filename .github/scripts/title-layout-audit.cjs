const { chromium } = require('playwright');
const fs = require('fs');
const { execFileSync } = require('child_process');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async()=>{
  const browser = await chromium.launch({
    headless:false,
    args:['--enable-webgl','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader-webgl','--disable-dev-shm-usage']
  });
  fs.mkdirSync('title-layout-audit',{recursive:true});
  const cases = [
    {name:'landscape', width:852, height:393},
    {name:'portrait', width:393, height:852}
  ];
  const results=[];
  for(const c of cases){
    const context=await browser.newContext({
      viewport:{width:c.width,height:c.height},
      deviceScaleFactor:1,
      isMobile:true,
      hasTouch:true,
      userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1'
    });
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push('pageerror: '+e.message));
    page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('version.json')) errors.push('console: '+m.text())});
    await page.goto('http://127.0.0.1:4173/',{waitUntil:'domcontentloaded'});
    await page.waitForSelector('#modelViewerOpen',{timeout:15000});
    await page.waitForFunction(()=>window.ParryModelViewer?.isAvailable?.(),{timeout:15000});
    await sleep(500);
    const before=await page.evaluate(()=>{
      const rect=id=>{const e=document.getElementById(id),r=e?.getBoundingClientRect();return r?{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}:null};
      return {w:innerWidth,h:innerHeight,button:rect('modelViewerOpen'),panel:document.querySelector('#overlay .panel')?(()=>{const r=document.querySelector('#overlay .panel').getBoundingClientRect();return{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}})():null};
    });
    const inViewport=r=>!!r&&r.left>=-1&&r.top>=-1&&r.right<=c.width+1&&r.bottom<=c.height+1;
    const buttonVisible=inViewport(before.button), panelVisible=inViewport(before.panel);
    await page.screenshot({path:`title-layout-audit/${c.name}-title.png`});
    await page.locator('#modelViewerOpen').click();
    await page.waitForSelector('#modelViewerUI.show',{timeout:5000});
    const viewerOpen=await page.evaluate(()=>window.parryModelViewerUI?.isOpen?.()===true&&window.ParryModelViewer?.state?.().active===true);
    await page.screenshot({path:`title-layout-audit/${c.name}-viewer.png`});
    await page.locator('#mvClose').click();
    const viewerClosed=await page.evaluate(()=>window.parryModelViewerUI?.isOpen?.()===false&&window.ParryModelViewer?.state?.().active===false);
    results.push({case:c.name,before,buttonVisible,panelVisible,viewerOpen,viewerClosed,errors,pass:buttonVisible&&panelVisible&&viewerOpen&&viewerClosed&&errors.length===0});
    await context.close();
  }
  const pass=results.every(r=>r.pass);
  fs.writeFileSync('title-layout-audit/audit.json',JSON.stringify({pass,results},null,2));
  console.log(JSON.stringify({pass,results},null,2));
  await browser.close();
  if(!pass) process.exit(2);
})().catch(e=>{console.error(e);process.exit(1)});
