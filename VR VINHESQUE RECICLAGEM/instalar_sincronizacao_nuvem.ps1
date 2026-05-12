$ErrorActionPreference = "Stop"

$taskName = "Vinhesque Cloud Sync"
$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$starter = Join-Path $baseDir "iniciar_sincronizacao_nuvem_oculto.ps1"
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
    Write-Host "Pronto. O notebook vai puxar lancamentos da nuvem automaticamente."
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "Nao foi possivel instalar a sincronizacao da nuvem."
    Write-Host "Detalhe: $($_.Exception.Message)"
    Write-Host ""
    exit 1
}
