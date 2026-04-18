import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
      if(msg.type() === 'error') console.log('BROWSER CONSOLE ERROR:', msg.text());
  });
  page.on('pageerror', err => console.log('BROWSER PAGE ERROR:', err.message, err.stack));

  console.log("Navigating to home...");
  await page.goto('http://localhost:5173/home');
  await page.evaluate(() => localStorage.setItem('yojna_user', 'null'));
  
  console.log("Navigating to chat...");
  await page.goto('http://localhost:5173/chat');
  await page.waitForTimeout(2000);
  console.log("Done.");
  await browser.close();
})();
