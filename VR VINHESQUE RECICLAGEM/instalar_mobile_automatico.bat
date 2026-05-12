@echo off
setlocal
cd /d "%~dp0"

echo Instalando inicializacao automatica do Vinhesque Mobile...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_mobile_automatico.ps1"
if errorlevel 1 (
    echo.
    echo Nao foi possivel concluir a instalacao.
    pause
    exit /b 1
)

echo.
echo Pronto. A cliente nao precisa abrir terminal todo dia.
echo O servidor mobile vai iniciar automaticamente quando entrar no Windows.
echo.
pause
