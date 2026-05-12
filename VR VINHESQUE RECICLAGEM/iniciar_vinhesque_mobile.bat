@echo off
cd /d "%~dp0"
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" sync_server.py
) else (
    python sync_server.py
)
pause
