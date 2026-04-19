/**
 * Run VS Code Extension Tests
 * This script uses the VS Code Test Electron API
 */
const { runTests } = require('@vscode/test-electron');
const path = require('path');

async function main() {
  try {
    const extensionPath = path.resolve(__dirname);

    console.log('Starting VS Code Extension tests...');
    console.log(`Extension path: ${extensionPath}`);

    await runTests({
      extensionPath,
      testPath: path.join(__dirname, 'tests', 'extension.spec.js'),
      launchArgs: ['--disable-extensions']
    });

    console.log('VS Code Extension tests completed successfully!');
    process.exit(0);
  } catch (error) {
    console.error('VS Code Extension tests failed:', error);
    process.exit(1);
  }
}

main();
