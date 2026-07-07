@echo off

REM Validate command
if /I "%~1"=="s" goto setup
if /I "%~1"=="c" goto consult

echo Options:
echo   s/S - Setup virtual environment and install dependencies
echo   c/C - Consult the certificate of a host
exit /b 1

:setup
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Verifying/Installing dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1

echo Setup complete.
exit /b 0

:consult
if "%~2"=="" (
    echo Usage: cert c ^<host^> [port]
    exit /b 1
)

if not exist ".venv" (
    echo Virtual environment not found.
    echo Run "cert s" first.
    exit /b 1
)

.venv\Scripts\python.exe main.py %2 %3
exit /b %ERRORLEVEL%