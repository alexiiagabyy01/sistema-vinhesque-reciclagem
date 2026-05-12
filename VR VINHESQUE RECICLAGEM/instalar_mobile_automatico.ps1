$ErrorActionPreference = "Stop"

$taskName = "Vinhesque Mobile Sync"
$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$starter = Join-Path $baseDir "iniciar_vinhesque_mobile_oculto.ps1"
$userId = "$env:USERDOMAIN\$env:USERNAME"

try {
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$starter`""

    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel LeastPrivilege

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null

    Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$starter`"" `
        -WindowStyle Hidden

    Write-Host ""
    Write-Host "Pronto. O Vinhesque Mobile vai iniciar sozinho quando a cliente entrar no Windows."
    Write-Host "A tarefa criada se chama: $taskName"
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "Nao foi possivel instalar a inicializacao automatica."
    Write-Host "Detalhe: $($_.Exception.Message)"
    Write-Host "Tente executar instalar_mobile_automatico.bat como administrador."
    Write-Host ""
    exit 1
}
