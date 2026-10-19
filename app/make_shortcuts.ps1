# Maakt snelkoppelingen naar Prompt.exe op het bureaublad en in het Startmenu, en ruimt oude op.
$dir = Join-Path $env:LOCALAPPDATA 'Programs\Prompt'
$exe = Join-Path $dir 'bin\Prompt.exe'
$icon = Join-Path $dir 'icon.ico'
if (-not (Test-Path $exe)) { Write-Error "Niet gevonden: $exe (eerst install.cmd draaien)"; exit 1 }

$desktop = [Environment]::GetFolderPath('Desktop')
$programs = [Environment]::GetFolderPath('Programs')
foreach ($old in @((Join-Path $desktop 'Claude Commands.lnk'), (Join-Path $programs 'Claude Commands.lnk'))) {
    if (Test-Path $old) { Remove-Item $old -Force; Write-Output "oude snelkoppeling verwijderd: $old" }
}

$ws = New-Object -ComObject WScript.Shell
foreach ($path in @((Join-Path $desktop 'Prompt.lnk'), (Join-Path $programs 'Prompt.lnk'))) {
    $lnk = $ws.CreateShortcut($path)
    $lnk.TargetPath = $exe
    $lnk.Arguments = '-X detach'
    $lnk.WorkingDirectory = $dir
    $lnk.IconLocation = "$icon,0"
    $lnk.Description = 'Prompt: alle Claude Code slash-commands, met 1 klik te kopieren'
    $lnk.WindowStyle = 1
    $lnk.Save()
    Write-Output "snelkoppeling: $path"
}
