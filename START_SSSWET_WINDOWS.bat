@echo off
setlocal
title SSSWET Local Research Engine
cd /d "%~dp0core"

echo.
echo  SSSWET - Local Research Engine + Research Bots
echo  Installing or updating the local package...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install -e .
  if errorlevel 1 goto install_failed
  echo.
  echo  Starting continuous research bots in a separate window...
  start "SSSWET Research Bots" cmd /k "cd /d "%~dp0core" && py -m ssswet_core.research_daemon"
  echo  Starting the local interface...
  py -m ssswet_core.server
) else (
  python -m pip install -e .
  if errorlevel 1 goto install_failed
  echo.
  echo  Starting continuous research bots in a separate window...
  start "SSSWET Research Bots" cmd /k "cd /d "%~dp0core" && python -m ssswet_core.research_daemon"
  echo  Starting the local interface...
  python -m ssswet_core.server
)

echo.
echo  The SSSWET local engine has stopped.
pause
exit /b 0

:install_failed
echo.
echo  Installation failed. Check that Python 3.11 or newer is installed
echo  and that this computer has an internet connection for the first setup.
pause
exit /b 1
