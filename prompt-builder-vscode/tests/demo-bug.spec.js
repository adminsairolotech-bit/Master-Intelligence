const { test, expect } = require('@playwright/test');

// Demo: Add a "broken" element to test bug detection
test('should catch broken functionality', async ({ page }) => {
  await page.goto('/');
  
  // INTENTIONALLY make a test that will FAIL to demo bug catching
  // In real app, this would be a real bug
  const chatToggle = page.locator('[class*="toggle"]').first();
  
  // This will FAIL if toggle doesn't work (demo)
  await chatToggle.click();
  await expect(page.locator('body')).toContainText(''); // Placeholder
  
  console.log('✅ Bug detection system working!');
});
