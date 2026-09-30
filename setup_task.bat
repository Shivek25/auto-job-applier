@echo off
REM AutoJobForge Windows Task Scheduler Setup
echo Setting up daily AutoJobForge scheduled task at 09:30 AM...
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" set PYTHON_EXE=python.exe

schtasks /create /tn "AutoJobForge_Daily_Apply" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_DIR%run.py\"" /sc daily /st 09:30 /f
echo Task AutoJobForge_Daily_Apply registered successfully!
pause
