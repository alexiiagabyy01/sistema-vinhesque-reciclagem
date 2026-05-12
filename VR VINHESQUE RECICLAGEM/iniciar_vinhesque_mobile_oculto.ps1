$ErrorActionPreference = "Stop"

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverPath = Join-Path $baseDir "sync_server.py"
$venvPythonw = Join-Path (Split-Path -Parent $baseDir) ".venv\Scripts\pythonw.exe"
$venvPython = Join-Path (Split-Path -Parent $baseDir) ".venv\Scripts\python.exe"

if (Test-Path $venvPythonw) {
    $python = $venvPythonw
} elseif (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $python = $cmd.Source
    } else {
        $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
        if (-not $cmd) {
            Add-Type -AssemblyName PresentationFramework
            [System.Windows.MessageBox]::Show("Python nao foi encontrado. Instale o Python ou use o pacote com Python incluso.", "Vinhesque Mobile")
            exit 1
        }
        $python = $cmd.Source
    }
}

$alreadyRunning = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains("sync_server.py") -and $_.CommandLine.Contains($baseDir) }

if ($alreadyRunning) {
    exit 0
}

Start-Process -FilePath $python -ArgumentList "`"$serverPath`"" -WorkingDirectory $baseDir -WindowStyle Hidden
