// 改进的抓取脚本 - 自动滚动加载
const { chromium } = require('playwright');

async function scrapeWithScroll(url, filename, scrolls = 30, waitMs = 2000) {
    const browser = await chromium.launch({ 
        headless: true, 
        args: ['--no-sandbox', '--disable-dev-shm-usage'] 
    });
    
    const page = await browser.newPage({ 
        viewport: { width: 1920, height: 1080 } 
    });
    
    page.setDefaultTimeout(120000);
    
    try {
        console.log(`访问: ${url}`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
        await page.waitForTimeout(5000);
        
        console.log(`滚动 ${scrolls} 次加载数据...`);
        
        for (let i = 0; i < scrolls; i++) {
            // 滚动到不同位置
            await page.evaluate((pos) => window.scrollTo(0, pos), i * 400);
            await page.waitForTimeout(waitMs);
            
            // 尝试点击加载更多
            try {
                await page.click('button:has-text("Load More"), button:has-text("Show More")', { timeout: 500 });
                await page.waitForTimeout(1000);
            } catch(e) {}
            
            if (i % 10 === 0) console.log(`  进度: ${i}/${scrolls}`);
        }
        
        // 最后滚动到顶部和底部确保加载
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(1000);
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);
        
        // 保存
        const content = await page.content();
        const fs = require('fs');
        fs.writeFileSync(filename, content);
        
        console.log(`完成: ${filename} (${content.length} chars)`);
        
    } catch(e) {
        console.error(`错误: ${e.message}`);
    } finally {
        await browser.close();
    }
}

// 主程序
const args = process.argv.slice(2);
if (args.length >= 2) {
    scrapeWithScroll(args[0], args[1], parseInt(args[2]) || 30, parseInt(args[3]) || 2000);
} else {
    console.log('用法: node scrape_top_traders.js <URL> <输出文件> [滚动次数] [等待ms]');
}
