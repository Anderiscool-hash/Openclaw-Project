import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const root = process.cwd();
const logsDir = path.join(root, 'logs');
const artDir = path.join(root, 'artifacts');
fs.mkdirSync(logsDir, { recursive: true });
fs.mkdirSync(artDir, { recursive: true });
const logFile = path.join(logsDir, 'actions.jsonl');

const MODE = process.argv.includes('--multi') ? 'multi' : 'single';
const ACCOUNTS_FILE = path.join(root, 'accounts_demo.json');

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

async function runFlow(page, accountLabel = 'default') {
  log('open_site', { accountLabel, url: 'https://www.saucedemo.com/' });
  await page.goto('https://www.saucedemo.com/', { waitUntil: 'domcontentloaded' });
  await shot(page, `${accountLabel}_login_page`);

  await page.fill('#user-name', 'standard_user');
  await page.fill('#password', 'secret_sauce');
  log('login_fill', { accountLabel });
  await page.click('#login-button');
  await page.waitForURL('**/inventory.html');
  log('login_success', { accountLabel });
  await shot(page, `${accountLabel}_inventory`);

  const addButtons = page.locator('button:has-text("Add to cart")');
  const count = await addButtons.count();
  for (let i = 0; i < Math.min(2, count); i++) {
    await addButtons.nth(i).click();
    log('add_to_cart', { accountLabel, index: i });
  }
  await shot(page, `${accountLabel}_after_add`);

  await page.click('.shopping_cart_link');
  await page.waitForURL('**/cart.html');
  log('open_cart', { accountLabel });
  await shot(page, `${accountLabel}_cart_view`);

  const removeBtns = page.locator('button:has-text("Remove")');
  if (await removeBtns.count()) {
    await removeBtns.first().click();
    log('remove_from_cart', { accountLabel, index: 0 });
  }
  await shot(page, `${accountLabel}_after_remove`);

  log('flow_complete', { accountLabel });
}

(async () => {
  const browser = await chromium.launch({ headless: false });

  try {
    if (MODE === 'single') {
      const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
      const page = await context.newPage();
      await runFlow(page, 'single');
      await context.close();
    } else {
      const accounts = JSON.parse(fs.readFileSync(ACCOUNTS_FILE, 'utf8'));
      for (const acct of accounts) {
        const label = acct.label || 'acct';
        const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
        const page = await context.newPage();
        await runFlow(page, label);
        await context.close();
      }
      log('multi_complete', { count: accounts.length });
    }
  } catch (e) {
    log('error', { message: String(e) });
  } finally {
    await browser.close();
  }
})();
