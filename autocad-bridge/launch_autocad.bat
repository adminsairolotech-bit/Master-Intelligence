@echo off
REM AutoCAD Bridge Launcher for Roll Forming Drawings
REM Connects AI (Opus 4.7) to AutoCAD

echo.
echo ========================================
echo    AUTOCAD BRIDGE - ROLL FORMING
echo ========================================
echo.

cd /d "%~dp0.."

REM Check if AutoCAD is running
echo [1/4] Checking AutoCAD...
python -c "import win32com.client" 2>nul
if errorlevel 1 (
    echo ERROR: pywin32 not installed
    echo Run: pip install pywin32
    pause
    exit /b 1
)

REM Show menu
echo.
echo Select option:
echo.
echo  [1] Draw C-Channel Profile (C-150)
echo  [2] Draw Z-Purlin Profile (Z-200)
echo  [3] Draw Flower Pattern (7 Passes)
echo  [4] Draw Roll Assembly (6 Passes)
echo  [5] Draw Shaft Detail (Ø50mm)
echo  [6] Draw Bearing Mount
echo  [7] Draw COMPLETE SET (All)
echo  [8] Start AutoCAD with New Drawing
echo.
echo  [Q] Quit
echo.

set /p choice="Enter choice (1-8): "

if "%choice%"=="1" goto c_channel
if "%choice%"=="2" goto z_purlin
if "%choice%"=="3" goto flower
if "%choice%"=="4" goto rolls
if "%choice%"=="5" goto shaft
if "%choice%"=="6" goto bearing
if "%choice%"=="7" goto all
if "%choice%"=="8" goto new_drawing
if "%choice%"=="q" goto end
if "%choice%"=="Q" goto end

:c_channel
echo.
echo Drawing C-Channel Profile...
python autocad-bridge\autocad_bridge.py --draw c-channel --new
goto end

:z_purlin
echo.
echo Drawing Z-Purlin Profile...
python autocad-bridge\autocad_bridge.py --draw z-purlin --new
goto end

:flower
echo.
echo Drawing Flower Pattern (7 passes)...
python autocad-bridge\autocad_bridge.py --flower 7 --new
goto end

:rolls
echo.
echo Drawing Roll Assembly...
python autocad-bridge\autocad_bridge.py --rolls --new
goto end

:shaft
echo.
echo Drawing Shaft Detail...
python autocad-bridge\autocad_bridge.py --shaft --new
goto end

:bearing
echo.
echo Drawing Bearing Mount...
python autocad-bridge\autocad_bridge.py --bearing --new
goto end

:all
echo.
echo Drawing Complete Set...
python autocad-bridge\autocad_bridge.py --all
goto end

:new_drawing
echo.
echo Starting AutoCAD with new drawing...
python autocad-bridge\autocad_bridge.py --new
goto end

:end
echo.
echo Done!
pause
