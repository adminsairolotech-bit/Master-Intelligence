@echo off
REM OpenClaw Bridge Launcher
REM Config: openclaw-bridge/openclaw.env

cd /d "%~dp0.."

if "%1"=="" (
    python openclaw-bridge/openclaw_bridge.py --cli
) else (
    python openclaw-bridge/openclaw_bridge.py %*
)
