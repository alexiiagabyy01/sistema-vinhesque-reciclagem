@echo off
setlocal

schtasks /Delete /TN "Vinhesque Cloud Sync" /F
pause
