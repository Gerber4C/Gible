@echo off
setlocal DisableDelayedExpansion
set "GIBLE_ARGS=%*"
set "GIBLE_FOUND="
set "GIBLE_EXIT=1"

if defined GIBLE_PYTHON goto custom_gible_python
if defined PARTNER_PYTHON goto custom_python
if exist "%~dp0.venv\Scripts\python.exe" call :try_python "%~dp0.venv\Scripts\python.exe"
if defined GIBLE_FOUND goto done
if exist "%~dp0venv\Scripts\python.exe" call :try_python "%~dp0venv\Scripts\python.exe"
if defined GIBLE_FOUND goto done
call :try_python py -3
if defined GIBLE_FOUND goto done
call :try_python python
if defined GIBLE_FOUND goto done
call :try_python python3
if defined GIBLE_FOUND goto done
echo Python 3.10 or newer was not found.
echo Install Python from https://www.python.org/downloads/ and enable Add Python to PATH.
echo Or set GIBLE_PYTHON to the full path of your python.exe.
goto done

:custom_gible_python
call :try_python "%GIBLE_PYTHON%"
if defined GIBLE_FOUND goto done
echo GIBLE_PYTHON must point to a working Python 3.10 or newer executable.
goto done

:custom_python
call :try_python "%PARTNER_PYTHON%"
if defined GIBLE_FOUND goto done
echo PARTNER_PYTHON must point to a working Python 3.10 or newer executable.
goto done

:try_python
%* -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 exit /b 1
set "GIBLE_FOUND=1"
%* "%~dp0run_local.py" %GIBLE_ARGS%
set "GIBLE_EXIT=%ERRORLEVEL%"
exit /b 0

:done
if "%GIBLE_EXIT%"=="0" exit /b 0
if /I "%~1"=="--check" exit /b %GIBLE_EXIT%
echo.
pause
exit /b %GIBLE_EXIT%
