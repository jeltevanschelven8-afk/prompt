# Installeert Prompt in %LOCALAPPDATA%\Programs\Prompt.
# bin\Prompt.exe is een kopie van het ondertekende pythonw.exe (Python Software Foundation). Een gegenereerde
# pyvenv.cfg en Lib\site-packages\sitecustomize.py in de Prompt-map zorgen dat die exe bij het starten
# prompt.pyw laadt. Zo blokkeert Windows Smart App Control het programma niet.
$ErrorActionPreference = 'Stop'
$src = $PSScriptRoot
$dest = Join-Path $env:LOCALAPPDATA 'Programs\Prompt'
$probe = 'import sys, tkinter; print(sys.base_prefix)'

function Find-Python {
    foreach ($attempt in @({ & py -3 -c $probe 2>$null }, { & python -c $probe 2>$null })) {
        try {
            $out = & $attempt
            if ($LASTEXITCODE -eq 0 -and $out) { return ($out | Select-Object -Last 1).Trim() }
        } catch { }
    }
    return $null
}

$py = Find-Python
if (-not $py -or -not (Test-Path (Join-Path $py 'pythonw.exe'))) {
    Write-Host 'Python 3 met tkinter is niet gevonden.'
    Write-Host 'Installeer Python van https://www.python.org/downloads/ (laat "tcl/tk and IDLE" aangevinkt) en probeer opnieuw.'
    exit 1
}
$python = Join-Path $py 'python.exe'
$version = & $python -c "import sys; print('%d.%d.%d' % sys.version_info[:3])"
$dll = & $python -c "import sys; print('python%d%d.dll' % sys.version_info[:2])"
Write-Host "Python gevonden: $py ($version)"

# Draaiende Prompt sluiten, anders zijn de bestanden in gebruik
Get-Process -Name Prompt -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 300

New-Item -ItemType Directory -Force (Join-Path $dest 'bin'), (Join-Path $dest 'Lib\site-packages') | Out-Null
# Resten van eerdere indelingen opruimen
foreach ($old in '_internal', 'Prompt.exe', 'PromptDebug.exe') {
    $p = Join-Path $dest $old
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}

Copy-Item (Join-Path $py 'pythonw.exe') (Join-Path $dest 'bin\Prompt.exe') -Force
foreach ($f in @($dll, 'python3.dll', 'vcruntime140.dll', 'vcruntime140_1.dll')) {
    $p = Join-Path $py $f
    if (Test-Path $p) { Copy-Item $p (Join-Path $dest 'bin') -Force }
}
Set-Content -Encoding ascii -Path (Join-Path $dest 'pyvenv.cfg') -Value @(
    "home = $py", 'include-system-site-packages = false', "version = $version")
Copy-Item (Join-Path $src 'host\Lib\site-packages\sitecustomize.py') (Join-Path $dest 'Lib\site-packages') -Force

foreach ($f in 'prompt.pyw', 'builtin_commands.json', 'uitleg.json', 'synonyms.json', 'icon.ico', 'README.md') {
    Copy-Item (Join-Path $src $f) $dest -Force
}

# Ingebouwde catalogus: de skills uit deze repository, zodat de marktplaats ook zonder website werkt.
$catalog = Join-Path $dest 'catalog'
if (Test-Path $catalog) { Remove-Item -Recurse -Force $catalog }
New-Item -ItemType Directory -Force (Join-Path $catalog 'data') | Out-Null
Copy-Item (Join-Path $src 'catalog-index.json') (Join-Path $catalog 'data\index.json') -Force
Copy-Item -Recurse (Join-Path $src '..\skills') (Join-Path $catalog 'skills') -Force
Write-Host "Catalogus: $((Get-ChildItem (Join-Path $catalog 'skills') -Directory).Count) skills"
# registry.json alleen neerzetten als hij er nog niet is: daarin staat welke marktplaats je gebruikt.
$registry = Join-Path $dest 'registry.json'
if (-not (Test-Path $registry) -or (Get-Content $registry -Raw) -match 'OWNER') {
    Copy-Item (Join-Path $src 'registry.json') $dest -Force
}

& (Join-Path $src 'make_shortcuts.ps1')
Write-Host ''
Write-Host "Klaar: $dest\bin\Prompt.exe"
