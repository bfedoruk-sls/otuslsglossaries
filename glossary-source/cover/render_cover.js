const { chromium } = require('playwright');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 2 });
  await p.goto('file://' + dir + '/cover.html'); await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.pdf({ path: dir + '/cover.pdf', width: '8.5in', height: '11in', printBackground: true, pageRanges: '1' });
  await p.screenshot({ path: dir + '/cover.png' });
  await b.close();
})();
