#!/usr/bin/env node
const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node scripts/x_browser_reader.js <url>');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 2200 } });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(5000);

    // Try common dismiss buttons / dialogs.
    const dismissTexts = ['Not now', 'Maybe later', 'Close', 'Accept all cookies', 'Accept all'];
    for (const txt of dismissTexts) {
      const loc = page.getByText(txt, { exact: true }).first();
      try { if (await loc.isVisible({ timeout: 500 })) await loc.click({ timeout: 1000 }); } catch {}
    }

    await page.waitForTimeout(1500);

    const result = await page.evaluate(() => {
      const pickText = (el) => (el && el.innerText ? el.innerText.trim() : null);
      const metaDesc = document.querySelector('meta[property="og:description"]')?.content || null;
      const title = document.title || null;
      const articleTexts = Array.from(document.querySelectorAll('article')).map(a => a.innerText.trim()).filter(Boolean);
      const mainText = articleTexts[0] || null;
      const bodyText = document.body ? document.body.innerText.slice(0, 5000) : null;
      return {
        url: location.href,
        title,
        metaDesc,
        articleCount: articleTexts.length,
        articleText: mainText,
        bodyPreview: bodyText,
      };
    });

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error(JSON.stringify({ error: String(err), url }, null, 2));
    process.exitCode = 2;
  } finally {
    await browser.close();
  }
}

main();
