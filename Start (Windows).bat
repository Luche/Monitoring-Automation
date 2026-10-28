@echo off
rem Double-click this file on Windows to start the automation.
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

where uv >nul 2>nul
if errorlevel 1 (
    echo First run: installing uv ^(one time only, no admin needed^)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if errorlevel 1 goto error
)

echo Checking Python and packages...
uv sync
if errorlevel 1 goto error

echo Checking WebKit browser...
uv run playwright install webkit
if errorlevel 1 goto error

uv run binus_automation.py
if errorlevel 1 goto error
exit /b 0

:error
echo.
echo Something went wrong (see the message above).
pause
exit /b 1
