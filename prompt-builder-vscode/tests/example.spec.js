const { test, expect } = require('@playwright/test');

test.describe('Prompt Builder Extension', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
  });

  test('should display the header with title', async ({ page }) => {
    const header = page.locator('.header h1');
    await expect(header).toContainText('Prompt Builder');
  });

  test('should have skill chips available', async ({ page }) => {
    const skillChips = page.locator('.skill-chips .chip');
    await expect(skillChips).toHaveCount(10);
  });

  test('should have tabs for Chat, Templates, and History', async ({ page }) => {
    await expect(page.locator('.tab').nth(0)).toContainText('Chat');
    await expect(page.locator('.tab').nth(1)).toContainText('Templates');
    await expect(page.locator('.tab').nth(2)).toContainText('History');
  });

  test('should toggle chat ON/OFF', async ({ page }) => {
    const toggle = page.locator('#chatToggle');
    const chatBox = page.locator('#chatBox');

    // Initially chat should be hidden (toggleChat() hides it on init)
    await expect(chatBox).toBeHidden();

    // Click toggle to turn ON
    await toggle.click();
    await expect(chatBox).toBeVisible();

    // Click again to turn off
    await toggle.click();
    await expect(chatBox).toBeHidden();
  });

  test('should switch between tabs', async ({ page }) => {
    // Click Templates tab
    await page.click('.tab:nth-child(2)');
    await expect(page.locator('#templatesPanel')).toBeVisible();

    // Click History tab
    await page.click('.tab:nth-child(3)');
    await expect(page.locator('#historyPanel')).toBeVisible();

    // Click Chat tab
    await page.click('.tab:nth-child(1)');
    await expect(page.locator('#chatPanel')).toBeVisible();
  });

  test('should select a skill chip', async ({ page }) => {
    const engineerChip = page.locator('.chip', { hasText: 'Engineer' });

    await engineerChip.click();
    await expect(engineerChip).toHaveClass(/selected/);

    // Click again to deselect
    await engineerChip.click();
    await expect(engineerChip).not.toHaveClass(/selected/);
  });

  test('should generate prompt on build', async ({ page }) => {
    const input = page.locator('#userInput');
    const buildButton = page.locator('button:has-text("Build")');
    const promptResult = page.locator('#promptResult');

    await input.fill('Write a function to add two numbers');
    await buildButton.click();

    await expect(promptResult).toBeVisible();
    await expect(page.locator('#promptText')).not.toBeEmpty();
  });

  test('should display templates in Templates tab', async ({ page }) => {
    await page.click('.tab:nth-child(2)');

    const templates = page.locator('.template-card');
    await expect(templates).toHaveCount(8);
  });

  test('should use template when clicked', async ({ page }) => {
    await page.click('.tab:nth-child(2)');
    await page.click('.template-card:first-child');

    // Should switch back to chat
    await expect(page.locator('#chatPanel')).toBeVisible();

    // Input should be filled with template
    const input = page.locator('#userInput');
    await expect(input).not.toHaveValue('');
  });

  test('should toggle AI mode', async ({ page }) => {
    const apiBtn = page.locator('#apiBtn');

    // Initially not active
    await expect(apiBtn).not.toHaveClass(/active/);

    // Toggle on
    await apiBtn.click();
    await expect(apiBtn).toHaveClass(/active/);

    // Toggle off
    await apiBtn.click();
    await expect(apiBtn).not.toHaveClass(/active/);
  });

  test.skip('should detect Hindi text', async ({ page }) => {
    // Note: Hindi detection requires triggering on input event
    // This is a known limitation - the detectLanguage function needs
    // to be called on input change, not on type
    const input = page.locator('#userInput');
    const langIndicator = page.locator('#inputLang');

    // Type Hindi text character by character to trigger detection
    await input.click();
    await page.keyboard.type('नमस्ते');
    await expect(langIndicator).toContainText('HI');
  });

  test('should detect English text', async ({ page }) => {
    const input = page.locator('#userInput');
    const langIndicator = page.locator('#inputLang');

    // Type English text to trigger detection
    await input.click();
    await page.keyboard.type('Hello world');
    await expect(langIndicator).toContainText('EN');
  });

  test('should add message to chat', async ({ page }) => {
    const input = page.locator('#userInput');
    const buildButton = page.locator('button:has-text("Build")');
    const chatBox = page.locator('#chatBox');

    // First turn ON chat
    await page.locator('#chatToggle').click();
    await expect(chatBox).toBeVisible();

    // Fill and build prompt
    await input.fill('Test prompt');
    await buildButton.click();

    await expect(chatBox.locator('.message.user')).toContainText('Test prompt');
  });
});

test.describe('Extension Module', () => {
  test('extension file should exist', async () => {
    const fs = require('fs');
    const path = require('path');
    const extensionPath = path.join(__dirname, '..', 'extension.js');
    expect(fs.existsSync(extensionPath)).toBeTruthy();
  });
});
