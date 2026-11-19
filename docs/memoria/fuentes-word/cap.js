const {chromium,devices}=require('playwright');
const U='https://rpi-lora.tailc40e5c.ts.net/';
(async()=>{
  const b=await chromium.launch();
  for(const tema of ['claro','oscuro']){
    const c=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,locale:'es-ES',timezoneId:'Europe/Madrid',colorScheme:tema==='oscuro'?'dark':'light',ignoreHTTPSErrors:false});
    const p=await c.newPage();
    await p.goto(U,{waitUntil:'load',timeout:60000});
    await p.waitForSelector('#tarjetas > *',{timeout:30000});
    await p.waitForTimeout(5000);
    await p.screenshot({path:`web/web-pc-${tema}.png`,fullPage:true});
    if(tema==='claro'){ await p.screenshot({path:'web/web-pc-arriba.png'}); 
      await p.click('button[data-horas="168"]'); await p.waitForTimeout(4000);
      const g=await p.$('#graficas'); await p.evaluate(()=>document.querySelector('.rangos').scrollIntoView({block:'start'})); await p.evaluate(()=>window.scrollBy(0,-90)); await p.waitForTimeout(800);
      await p.screenshot({path:'web/web-pc-historico-semana.png'}); }
    await c.close();
  }
  const m=await b.newContext({...devices['iPhone 13'],locale:'es-ES',timezoneId:'Europe/Madrid'});
  const p=await m.newPage();
  await p.goto(U,{waitUntil:'load',timeout:60000});
  await p.waitForSelector('#tarjetas > *',{timeout:30000});
  await p.waitForTimeout(5000);
  await p.screenshot({path:'web/web-movil-arriba.png'});
  await p.evaluate(()=>document.querySelector('#tarjetas').scrollIntoView({block:'start'})); await p.evaluate(()=>window.scrollBy(0,-70)); await p.waitForTimeout(800);
  await p.screenshot({path:'web/web-movil-tarjetas.png'});
  await p.evaluate(()=>document.querySelector('.rangos').scrollIntoView({block:'start'})); await p.evaluate(()=>window.scrollBy(0,-110)); await p.waitForTimeout(1500);
  await p.screenshot({path:'web/web-movil-historico.png'});
  console.log(await p.evaluate(()=>[document.querySelector('#ultima-recepcion').innerText,document.querySelector('#estado').innerText,document.querySelector('#radio').innerText,document.querySelector('#info-historico').innerText].join(' | ')));
  await b.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
