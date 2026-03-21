#!/usr/bin/env node
const { chromium } = require('playwright');

async function main(){
  const url = process.argv[2] || 'https://polymarket.com/';
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 2400 } });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(4000);
  const data = await page.evaluate(() => window.__NEXT_DATA__ || null);
  if (!data) {
    console.log(JSON.stringify({ markets: [] }));
    await browser.close();
    return;
  }
  function collectMarkets(obj, out){
    if (!obj) return;
    if (Array.isArray(obj)) {
      for (const it of obj) collectMarkets(it, out);
    } else if (typeof obj === 'object') {
      if (obj.question && obj.slug && obj.outcomePrices) out.push(obj);
      for (const k of Object.keys(obj)) collectMarkets(obj[k], out);
    }
  }
  const markets = [];
  collectMarkets(data.props, markets);
  const uniq = new Map();
  for (const m of markets) {
    if (!m.slug) continue;
    if (!uniq.has(m.slug)) uniq.set(m.slug, m);
  }
  console.log(JSON.stringify({ markets: [...uniq.values()] }));
  await browser.close();
}

main().catch(err=>{
  console.error(JSON.stringify({ error: String(err) }));
  process.exit(2);
});
