// Renderiza los HTML de diseño a PNG con Chromium (Playwright).
// Uso: node render.js <archivo.html> <salida.png> <ancho> <alto> [selectorRecorte=nombreSalida...]
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const FONT_DIR = '/root/.claude/skills/canvas-design/canvas-fonts';

function fontFace(family, file, weight = 400, style = 'normal') {
  const b64 = fs.readFileSync(path.join(FONT_DIR, file)).toString('base64');
  return `@font-face{font-family:'${family}';font-style:${style};font-weight:${weight};` +
    `src:url(data:font/ttf;base64,${b64}) format('truetype');}`;
}

const FONTS = [
  fontFace('Italiana', 'Italiana-Regular.ttf'),
  fontFace('Poiret', 'PoiretOne-Regular.ttf'),
  fontFace('Nothing', 'NothingYouCouldDo-Regular.ttf'),
  fontFace('Jura', 'Jura-Light.ttf', 300),
  fontFace('Jura', 'Jura-Medium.ttf', 500),
  fontFace('Outfit', 'Outfit-Regular.ttf', 400),
  fontFace('Outfit', 'Outfit-Bold.ttf', 700),
  fontFace('Gloock', 'Gloock-Regular.ttf'),
].join('\n');

(async () => {
  const [htmlPath, outPath, w, h, ...crops] = process.argv.slice(2);
  const html = fs.readFileSync(htmlPath, 'utf8').replace('/*@FONTS@*/', FONTS);
  const tmp = path.join(path.dirname(outPath), '.build-' + path.basename(htmlPath));
  fs.writeFileSync(tmp, html);

  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({
    viewport: { width: Number(w), height: Number(h) },
    deviceScaleFactor: 2,
  });
  page.on('pageerror', (e) => console.error('✗ error en la página:', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.error('✗ consola:', m.text()); });
  await page.goto('file://' + path.resolve(tmp));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  // .jpg → archivo ligero para WhatsApp; .png → original sin pérdida
  const opts = (f) => f.endsWith('.jpg')
    ? { path: f, type: 'jpeg', quality: 92 }
    : { path: f };

  await page.screenshot(opts(outPath));
  console.log('→', outPath);

  for (const crop of crops) {
    const [sel, file] = crop.split('=');
    const el = await page.$(sel);
    if (el) { await el.screenshot(opts(file)); console.log('→', file); }
  }
  fs.unlinkSync(tmp);
  await browser.close();
})();
