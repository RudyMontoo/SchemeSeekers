import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err));
  
  await page.goto('http://localhost:5173/home');
  // Click on guest
  // Wait, no need since local storage is empty by default
  await page.goto('http://localhost:5173/chat');
  await page.waitForTimeout(2000);
  await browser.close();
})();
