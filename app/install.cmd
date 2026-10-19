@echo off
rem Installeert Prompt in %LOCALAPPDATA%\Programs\Prompt. Het echte werk staat in install.ps1.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
  echo.
  echo Installatie mislukt.
  pause
  exit /b 1
)
exit /b 0
