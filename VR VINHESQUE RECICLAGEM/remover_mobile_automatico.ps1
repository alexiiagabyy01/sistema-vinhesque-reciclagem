$ErrorActionPreference = "Stop"

$taskName = "Vinhesque Mobile Sync"

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host ""
    Write-Host "Inicializacao automatica removida."
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "Nao foi possivel remover a tarefa, ou ela ja nao existe."
    Write-Host "Detalhe: $($_.Exception.Message)"
    Write-Host ""
}
