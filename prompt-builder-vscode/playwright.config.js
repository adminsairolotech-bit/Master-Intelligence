const { defineConfig, devices } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:3000',
    actionTimeout: 0,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } }
  ],
  webServer: {
    command: 'npx serve -l 3000 -s .',
    port: 3000,
    timeout: 120000,
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore'
  }
});
