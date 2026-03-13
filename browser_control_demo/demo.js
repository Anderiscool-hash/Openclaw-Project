import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const root = process.cwd();
const logsDir = path.join(root, 'logs');
const artDir = path.join(root, 'artifacts');
fs.mkdirSync(logsDir, { recursive: true });
fs.mkdirSync(artDir, { recursive: true });
const logFile = path.join(logsDir, 'actions.jsonl');

function log(step, detail = {}) {
  const row = { ts: new Date().toISOString(), step, ...detail };
  fs.appendFileSync(logFile, JSON.stringify(row) + '\n');
  console.log(step, detail);
}

async function shot(page, name) {
  const p = path.join(artDir, `${Date.now()}_${name}.png`);
  await page.screenshot({ path: p, fullPage: true });
  log('screenshot', { path: p });
}

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  const page = await context.newPage();

  try {
    log('open_site', { url: 'https://www.saucedemo.com/' });
    await page.goto('https://www.saucedemo.com/', { waitUntil: 'domcontentloaded' });
    await shot(page, 'login_page');

    // Public demo creds from page: standard_user / secret_sauce
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    log('login_fill');
    await page.click('#login-button');
    await page.waitForURL('**/inventory.html');
    log('login_success');
    await shot(page, 'inventory');

    // Add first 2 products
    const addButtons = page.locator('button:has-text("Add to cart")');
    const count = await addButtons.count();
    for (let i = 0; i < Math.min(2, count); i++) {
      await addButtons.nth(i).click();
      log('add_to_cart', { index: i });
    }
    await shot(page, 'after_add');

    // Open cart
    await page.click('.shopping_cart_link');
    await page.waitForURL('**/cart.html');
    log('open_cart');
    await shot(page, 'cart_view');

    // Remove one item
    const removeBtns = page.locator('button:has-text("Remove")');
    if (await removeBtns.count()) {
      await removeBtns.first().click();
      log('remove_from_cart', { index: 0 });
    }
    await shot(page, 'after_remove');

    log('demo_complete');
  } catch (e) {
    log('error', { message: String(e) });
  } finally {
    await context.close();
    await browser.close();
  }
})();
