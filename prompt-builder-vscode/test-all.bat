@echo off
REM Desktop App Test Runner
REM ==============================

echo ========================================
echo    DESKTOP TEST SUITE
echo ========================================
echo.

echo [1/4] Installing PyAutoGUI...
pip install pyautogui 2>nul
if errorlevel 1 echo   Already installed or pip not found

echo.
echo [2/4] Running Playwright Tests...
cd /d "%~dp0"
call npx playwright test --project=chromium
echo.

echo [3/4] Running Electron Tests...
call npx playwright test tests/electron.spec.js
echo.

echo [4/4] Python Desktop Tests...
python tests/desktop_automation.py
echo.

echo ========================================
echo    ALL TESTS COMPLETED
echo ========================================
pause
