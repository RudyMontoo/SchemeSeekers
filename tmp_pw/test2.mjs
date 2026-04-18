import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ permissions: ['microphone'] });
  const page = await context.newPage();
  
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  page.on('pageerror', err => console.log('ERROR:', err.message, err.stack));

  // Forward network requests to see if fetch fails
  page.on('response', resp => {
    if(resp.url().includes('/voice/')) {
       console.log("NET RESPONSE:", resp.url(), resp.status());
    }
  });

  await page.goto('http://localhost:5173/chat');
  await page.waitForTimeout(1000);
  
  // Click the mic button
  console.log("Clicking mic...");
  const handles = await page.$$('.chat-mic-btn');
  // There are three chat mic buttons (attach, start/stop, playing audio).
  // The first one is attach, second is mic.
  for(let handle of handles) {
     const title = await handle.getAttribute('title');
     if(title && title.includes('voice session')) {
        await handle.click();
        console.log("Clicked:", title);
     }
  }

  await page.waitForTimeout(6000); // wait for TTS
  
  console.log("Done.");
  await browser.close();
})();
