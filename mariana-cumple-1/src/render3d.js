// Renderiza la escena three.js a PNG/JPG. Uso: node render3d.js <html> <salida> <w> <h>
const fs=require('fs'), path=require('path'), http=require('http');
const { chromium }=require('/opt/node22/lib/node_modules/playwright');

function servir(dir){
  const tipos={'.html':'text/html','.js':'text/javascript'};
  const srv=http.createServer((req,res)=>{
    const f=path.join(dir,decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(f,(e,d)=>{
      if(e){res.writeHead(404);res.end();return;}
      res.writeHead(200,{'Content-Type':tipos[path.extname(f)]||'application/octet-stream'});
      res.end(d);
    });
  });
  return new Promise(r=>srv.listen(0,()=>r({srv,port:srv.address().port})));
}
const FONT_DIR='/root/.claude/skills/canvas-design/canvas-fonts';

function fontFace(family,file,style='normal',weight=400){
  const b64=fs.readFileSync(path.join(FONT_DIR,file)).toString('base64');
  return `@font-face{font-family:'${family}';font-style:${style};font-weight:${weight};`+
    `src:url(data:font/ttf;base64,${b64}) format('truetype');}`;
}
const FONTS=[
  fontFace('Nothing','NothingYouCouldDo-Regular.ttf'),
  fontFace('Italiana','Italiana-Regular.ttf'),
].join('\n');

(async()=>{
  const [htmlArg,out,w,h]=process.argv.slice(2);
  const [html,query]=htmlArg.split('?');
  const {srv,port}=await servir(path.dirname(path.resolve(html)));
  const url=`http://127.0.0.1:${port}/${path.basename(html)}`+(query?`?${query}`:'');
  const browser=await chromium.launch({
    executablePath:'/opt/pw-browsers/chromium',
    args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],
  });
  const page=await browser.newPage({viewport:{width:Number(w),height:Number(h)},deviceScaleFactor:1});
  page.on('pageerror',e=>console.error('✗',e.message));
  page.on('console',m=>{if(m.type()==='error')console.error('✗ consola:',m.text())});
  // inyecta las fuentes como hoja de estilo antes de cargar el módulo
  await page.addInitScript((css)=>{
    const add=()=>{const s=document.createElement('style');s.textContent=css;
      (document.head||document.documentElement).appendChild(s);};
    if(document.head||document.documentElement) add();
    else document.addEventListener('readystatechange',add,{once:true});
  }, FONTS);
  await page.goto(url);
  await page.waitForFunction('window.__ready===true',{timeout:30000}).catch(()=>console.error('✗ timeout __ready'));
  await page.waitForTimeout(500);
  const opts=out.endsWith('.jpg')?{path:out,type:'jpeg',quality:93}:{path:out};
  const app=await page.$('#app');
  await (app?app.screenshot(opts):page.screenshot(opts));
  console.log('→',out);
  await browser.close();
  srv.close();
})();
