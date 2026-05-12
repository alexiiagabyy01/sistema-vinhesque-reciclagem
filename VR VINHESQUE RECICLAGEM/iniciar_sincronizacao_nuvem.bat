@echo off
cd /d "%~dp0"
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" desktop_cloud_sync.py
) else (
    python desktop_cloud_sync.py
)
pause
