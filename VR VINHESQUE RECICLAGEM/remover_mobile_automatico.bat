@echo off
setlocal
cd /d "%~dp0"

echo Removendo inicializacao automatica do Vinhesque Mobile...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0remover_mobile_automatico.ps1"

echo.
echo Se o servidor estiver rodando agora, reinicie o notebook para encerrar,
echo ou feche pelo Gerenciador de Tarefas procurando por python/pythonw.
echo.
pause
