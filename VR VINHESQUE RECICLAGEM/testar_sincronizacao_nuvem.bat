@echo off
cd /d "%~dp0"
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" testar_sincronizacao_nuvem.py
) else (
    python testar_sincronizacao_nuvem.py
)
echo.
pause
