@echo off
cd /d "%~dp0"
python scripts\setup.py
if errorlevel 1 (
    echo.
    echo Setup failed. Make sure Python 3.10+ is installed: https://python.org
    pause
)
