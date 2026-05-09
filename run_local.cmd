@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "NODE_EXE=C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
set "BACKEND_URL=http://127.0.0.1:8765/api/profiles"
set "FRONTEND_URL=http://127.0.0.1:5173"

if not exist "%PYTHON_EXE%" (
  echo Python runtime was not found:
  echo %PYTHON_EXE%
  exit /b 1
)

if not exist "%NODE_EXE%" (
  echo Node runtime was not found:
  echo %NODE_EXE%
  exit /b 1
)

if /I "%~1"=="--check" (
  echo Runtime paths are available.
  exit /b 0
)

echo Starting Partner local workspace...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri '%BACKEND_URL%' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  echo Starting backend at http://127.0.0.1:8765
  start "Partner Backend" /B "%PYTHON_EXE%" backend\server.py
) else (
  echo Backend is already running at http://127.0.0.1:8765
)

timeout /t 1 /nobreak >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri '%FRONTEND_URL%' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  echo Starting frontend at http://127.0.0.1:5173
  start "Partner Frontend" /B "%NODE_EXE%" frontend\server.mjs
) else (
  echo Frontend is already running at http://127.0.0.1:5173
)

echo.
echo Open this in your browser:
echo %FRONTEND_URL%
echo.
echo Keep this CMD window open while using Partner.
echo Close the window when you are done.
echo.

:keep_alive
timeout /t 3600 /nobreak >nul
goto keep_alive
