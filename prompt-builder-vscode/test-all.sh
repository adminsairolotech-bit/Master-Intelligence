#!/bin/bash
# Desktop App Test Runner

echo "========================================"
echo "   DESKTOP TEST SUITE"
echo "========================================"
echo ""

echo "[1/4] Installing dependencies..."
pip install pyautogui 2>/dev/null || echo "PyAutoGUI already installed"

echo ""
echo "[2/4] Running Playwright Tests..."
npx playwright test --project=chromium

echo ""
echo "[3/4] Running Electron Tests..."
npx playwright test tests/electron.spec.js

echo ""
echo "[4/4] Python Desktop Tests..."
python tests/desktop_automation.py

echo ""
echo "========================================"
echo "   ALL TESTS COMPLETED"
echo "========================================"
