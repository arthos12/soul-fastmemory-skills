# Polymarket 数据工具文档

## 量化业务数据主入口

**主目录**: `data/polymarket/`

### 子目录结构

| 目录 | 内容 |
|------|------|
| `br/` | BR(BoneReader)真实数据 |
| `top_traders/` | Top Trader数据 |
| `ours/` | 我们的模拟交易数据 |
| `reports/` | 分析报告 |
| `runtime/` | 运行时数据 |

---

## 浏览器工具

### 脚本位置

| 脚本 | 用途 |
|------|------|
| `scripts/openclaw_browser.js` | 基础浏览器抓取 |
| `scripts/openclaw_browser_expand.js` | 增强版+自动滚动 |
| `scripts/scrape_top_traders.js` | Top Trader专用抓取 |

### 使用方法

```bash
# 基础抓取
node scripts/openclaw_browser.js "https://polymarket.com/profile/%40BoneReader"

# 增强版滚动抓取
node scripts/openclaw_browser_expand.js "https://polymarket.com/profile/%40BoneReader"

# Top Trader抓取 (需要@用户名格式)
node scripts/scrape_top_traders.js "URL" "输出文件.html" 滚动次数
```

---

## PM数据提取方法

### 1. 获取用户数据 (核心方法)

```python
import requests, re, json

def extract_pm_user_data(username):
    # 使用@用户名格式
    url = f'https://polymarket.com/profile/%40{username}'
    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20).text
    
    # 提取__NEXT_DATA__中的内嵌JSON
    m = re.search(r'__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    obj = json.loads(m.group(1))
    
    # 获取queries中的数据
    queries = obj['props']['pageProps']['dehydratedState']['queries']
    
    return queries
```

### 2. 提取关键数据

| 数据 | Query Key |
|------|-----------|
| 用户统计 | `user-stats` |
| PnL曲线 | `portfolio-pnl` |
| 交易历史 | `marketsTraded` |
| 交易量 | `profile/volume` |

### 3. 完整提取脚本

```python
# scripts/bone_reader_extract.py 的核心逻辑
import requests, re, json, datetime

URL = 'https://polymarket.com/profile/%40BoneReader'
html = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20).text
m = re.search(r'__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
obj = json.loads(m.group(1))
queries = obj['props']['pageProps']['dehydratedState']['queries']

# 遍历queries提取数据
for q in queries:
    key = q.get('queryKey')
    state = q.get('state', {})
    data = state.get('data')
    print(f"{key}: {data}")
```

---

## URL格式区别

| 格式 | 示例 | 需登录 |
|------|------|--------|
| **@用户名** | `/profile/%40BoneReader` | ❌ 不需要 |
| 钱包地址 | `/profile/0x02227...` | ✅ 需要 |

**重要**: 必须使用 `@用户名` 格式才能获取公开数据！

---

## 数据标记系统

为避免数据混淆，使用以下标记:

- `source: "ours"` - 我们的模拟交易
- `source: "br"` - BR真实数据  
- `source: "top_trader"` - Top Trader数据

每个结果文件必须包含source字段。

---

## 常用命令

```bash
# 抓取BR数据
node scripts/openclaw_browser.js "https://polymarket.com/profile/%40BoneReader" > data/pm_br.html

# 抓取Top Trader
node scripts/scrape_top_traders.js "https://polymarket.com/profile/%40HorizonSplendidView" data/top_traders/
```

---

## 浏览器实现原理

### 1. 基础版 (openclaw_browser.js)

使用 Playwright + Chromium 无头浏览器:

```javascript
const { chromium } = require('playwright');

async function main() {
  // 启动浏览器
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 2200 } });
  
  // 访问URL
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(5000);
  
  // 尝试关闭弹窗
  const dismissTexts = ['Not now', 'Maybe later', 'Close', 'Accept all cookies'];
  for (const txt of dismissTexts) {
    try {
      const loc = page.getByText(txt, { exact: true }).first();
      if (await loc.isVisible({ timeout: 500 })) {
        await loc.click({ timeout: 1000 });
      }
    } catch {}
  }
  
  // 提取页面内容
  const result = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    bodyPreview: document.body.innerText.slice(0, 5000),
  }));
  
  console.log(JSON.stringify(result));
  await browser.close();
}
```

**关键点:**
- 使用 `waitUntil: 'domcontentloaded'` 等待DOM加载
- 尝试关闭弹窗/cookie提示
- 提取 `document.body.innerText`

---

### 2. 增强版 (openclaw_browser_expand.js)

增强功能:
- 监听API请求 (page.on('response'))
- 自动切换Tab (Activity/Positions/Closed/Active)
- 滚动加载更多内容

```javascript
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 2400 } });
  
  // 监听API请求
  const requests = [];
  page.on('response', async (resp) => {
    const u = resp.url();
    if (u.includes('/api/') || u.includes('profile')) {
      requests.push({ url: u, status: resp.status() });
    }
  });
  
  // 访问页面
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(4000);
  
  // 切换Tab
  for (const txt of ['Activity', 'Positions', 'Closed', 'Active']) {
    try {
      const loc = page.getByText(txt, { exact: true }).first();
      if (await loc.isVisible({ timeout: 500 })) {
        await loc.click();
        await page.waitForTimeout(1500);
      }
    } catch {}
  }
  
  // 滚动加载
  for (let i = 0; i < 6; i++) {
    await page.mouse.wheel(0, 2400);
    await page.waitForTimeout(1200);
  }
  
  // 输出
  const result = await page.evaluate(() => ({
    title: document.title,
    text: document.body.innerText.slice(0, 12000)
  }));
  
  console.log(JSON.stringify({ result, requests }));
  await browser.close();
}
```

### 3. 滚动抓取版 (scrape_top_traders.js)

专用脚本，可自定义滚动次数和等待时间:

```javascript
async function scrapeWithScroll(url, filename, scrolls = 30, waitMs = 2000) {
  const browser = await chromium.launch({ 
    headless: true, 
    args: ['--no-sandbox'] 
  });
  
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  
  // 滚动加载
  for (let i = 0; i < scrolls; i++) {
    await page.evaluate((pos) => window.scrollTo(0, pos), i * 400);
    await page.waitForTimeout(waitMs);
  }
  
  const content = await page.content();
  // 保存
}
```

---

## 核心原理

1. **Playwright + Chromium**: 无头浏览器，支持JS渲染
2. **等待DOM**: 使用 `waitUntil: 'domcontentloaded'`
3. **滚动加载**: 模拟用户滚动触发懒加载
4. **Tab切换**: 点击不同Tab获取不同数据
5. **API监听**: 捕获页面发出的API请求

---

## 依赖安装

```bash
npm install playwright
npx playwright install chromium
```
