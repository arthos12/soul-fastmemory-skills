#!/usr/bin/env node
const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) process.exit(1);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 2400 } });
  const requests = [];
  page.on('response', async (resp) => {
    const u = resp.url();
    if (u.includes('/api/') || u.includes('profile') || u.includes('activity') || u.includes('position') || u.includes('market')) {
      requests.push({ url: u, status: resp.status() });
    }
  });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(4000);
  for (const txt of ['Activity', 'Positions', 'Closed', 'Active']) {
    try {
      const loc = page.getByText(txt, { exact: true }).first();
      if (await loc.isVisible({ timeout: 500 })) {
        await loc.click({ timeout: 1000 });
        await page.waitForTimeout(1500);
      }
    } catch {}
  }
  for (let i = 0; i < 6; i++) {
    await page.mouse.wheel(0, 2400);
    await page.waitForTimeout(1200);
  }
  const result = await page.evaluate(() => ({
    title: document.title,
    text: (document.body && document.body.innerText || '').slice(0, 12000)
  }));
  console.log(JSON.stringify({ result, requests }, null, 2));
  await browser.close();
}
main();
