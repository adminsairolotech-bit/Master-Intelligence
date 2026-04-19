const { test, expect } = require('@playwright/test');

test.describe('🔍 Auto Bug Hunter', () => {
  
  test('should detect console errors automatically', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    
    await page.goto('/');
    await page.waitForTimeout;
    
    // Auto-report any JS errors
    if (consoleErrors.length > 0) {
      console.log('🐛 BUGS FOUND:', consoleErrors);
    }
    expect(consoleErrors).toHaveLength(0);
  });

  test('should detect failed network requests', async ({ page }) => {
    const failedRequests = [];
    page.on('response', response => {
      if (response.status() >= 400) {
        failedRequests.push(`${response.status()} - ${response.url()}`);
      }
    });
    
    await page.goto('/');
    await page.waitForTimeout;
    
    if (failedRequests.length > 0) {
      console.log('🐛 FAILED REQUESTS:', failedRequests);
    }
    expect(failedRequests).toHaveLength(0);
  });

  test('should detect missing UI elements', async ({ page }) => {
    await page.goto('/');
    
    // Check all required elements exist
    const elements = {
      'Header': 'h1',
      'Chat Toggle': '.toggle-btn, [class*="toggle"]',
      'Skill Chips': '.skill-chip, [class*="skill"]',
      'Tabs': '.tab, [class*="tab"]',
    };
    
    const missing = [];
    for (const [name, selector] of Object.entries(elements)) {
      const el = page.locator(selector).first();
      if (!(await el.count())) {
        missing.push(name);
      }
    }
    
    if (missing.length > 0) {
      console.log('🐛 MISSING ELEMENTS:', missing);
    }
    expect(missing).toHaveLength(0);
  });

  test('should detect broken buttons/links', async ({ page }) => {
    await page.goto('/');
    
    const brokenButtons = [];
    const buttons = page.locator('button');
    const count = await buttons.count();
    
    for (let i = 0; i < count; i++) {
      const btn = buttons.nth(i);
      const isDisabled = await btn.isDisabled();
      const hasHandler = await btn.evaluate(el => el.onclick !== null || el.classList.contains('clickable'));
      
      if (isDisabled) {
        brokenButtons.push(`Disabled button: ${await btn.textContent()}`);
      }
    }
    
    if (brokenButtons.length > 0) {
      console.log('🐛 BROKEN BUTTONS:', brokenButtons);
    }
  });
});
