@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0kill_local.ps1" %*
exit /b %ERRORLEVEL%
