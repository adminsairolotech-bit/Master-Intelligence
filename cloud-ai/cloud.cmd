@echo off
REM Cloud AI Bridge Launcher
REM Config: cloud-ai/cloud.env

cd /d "%~dp0.."

if "%1"=="" (
    python cloud-ai/cloud_bridge.py --cli
) else (
    python cloud-ai/cloud_bridge.py %*
)
