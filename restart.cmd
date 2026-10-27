@echo off
call "%~dp0kill.cmd"
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~dp0gible.cmd" %*
exit /b %ERRORLEVEL%
