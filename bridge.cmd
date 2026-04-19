@echo off
REM Universal Bridge CLI
REM Usage: bridge "your message" or just "bridge" for interactive mode

cd /d "%~dp0"

if "%1"=="" (
    python universal_bridge.py --cli
) else (
    python universal_bridge.py %*
)
