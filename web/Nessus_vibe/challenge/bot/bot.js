const puppeteer = require('puppeteer-core');
const url = require('url');

const TARGET_URL   = process.env.TARGET_URL || 'http://web:8000/';
const FLAG         = process.env.FLAG       || 'DCTF{fake_flag}';
const INTERVAL_MS  = 30 * 1000; // 120 seconds

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function visitPage() {
    let browser;
    try {
        browser = await puppeteer.launch({
            executablePath: '/usr/bin/chromium',
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ],
        });

        const page = await browser.newPage();

        // Set the FLAG as a session cookie before visiting
        await page.setCookie({
            name: 'flag',
            value: FLAG,
            domain: url.parse(TARGET_URL).host,
            path: '/',
            httpOnly: false,
            secure: false,
        });

        console.log(`[${new Date().toISOString()}] Navigating to ${TARGET_URL}`);
        await page.goto(TARGET_URL, { waitUntil: 'networkidle2', timeout: 30000 });

        // ── Step 1: type search term ──────────────────────────────────────────
        const SEARCH_TERM = 'Browsable Web Directories';
        console.log(`[${new Date().toISOString()}] Searching for "${SEARCH_TERM}"`);
        await page.waitForSelector('#searchBox', { timeout: 10000 });
        await page.click('#searchBox', { clickCount: 3 });
        await page.type('#searchBox', SEARCH_TERM);
        await sleep(600); // let filterVulnerabilities() run

        // ── Step 2: collect all visible vuln-list-item data-vuln-id values ────
        const vulnIds = await page.evaluate(() =>
            Array.from(
                document.querySelectorAll('.vuln-list-item:not(.hidden)')
            ).map(el => el.getAttribute('data-vuln-id'))
        );

        console.log(`[${new Date().toISOString()}] Found ${vulnIds.length} visible item(s) matching search`);

        // ── Step 3: click each item one by one ───────────────────────────────
        // Each click calls toggleVulnSelection → updateVulnDetailsDropdown
        for (const id of vulnIds) {
            await page.evaluate((vulnId) => {
                const item = document.querySelector(`[data-vuln-id="${vulnId}"]`);
                if (item) item.click();
            }, id);
            await sleep(200);
            console.log(`[${new Date().toISOString()}] Selected item vuln-id=${id}`);
        }

        await sleep(300);

        // ── Step 4: iterate every option in the detail dropdown ───────────────
        // Detail dropdown is now populated via updateVulnDetailsDropdown()
        const optionValues = await page.evaluate(() =>
            Array.from(document.querySelectorAll('#vuln-details-select option'))
                .map(o => o.value)
                .filter(v => v !== '')
        );

        console.log(`[${new Date().toISOString()}] Detail dropdown has ${optionValues.length} option(s)`);

        for (const val of optionValues) {
            await page.evaluate((v) => {
                const sel = document.getElementById('vuln-details-select');
                sel.value = v;
                sel.dispatchEvent(new Event('change'));
            }, val);
            await sleep(400); // let displayVulnDetails() render
            console.log(`[${new Date().toISOString()}] Viewed details for vuln id=${val}`);
        }

        console.log(`[${new Date().toISOString()}] Bot run complete.`);

    } catch (err) {
        console.error(`[${new Date().toISOString()}] Error: ${err.message}`);
    } finally {
        if (browser) await browser.close();
    }
}

// Run immediately on start, then every 120 seconds
(async () => {
    console.log(`[BOT] Starting. Will run every ${INTERVAL_MS / 1000}s with FLAG cookie.`);
    await visitPage();
    setInterval(visitPage, INTERVAL_MS);
})();
