# build_windows.ps1 — build the I Studio IDE Windows installer end-to-end.
#
# Requires: Node.js (npm), Python with pyinstaller + pywebview installed,
# and Inno Setup 6 (ISCC.exe) on PATH or in the standard install locations.
#
# Outputs:
#   ide/dist/                  — frontend production build
#   dist/istudio-ide/          — PyInstaller onedir app
#   release/IStudioIDE-Setup-<version>.exe — installer

# "Continue" because native tools (npm, python, iscc) write notices to stderr;
# failures are caught by explicit $LASTEXITCODE checks below.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

function Get-Version {
    $init = Join-Path $Root "src\istudio\ide\__init__.py"
    $m = Select-String -Path $init -Pattern '__version__\s*=\s*"([^"]+)"' | Select-Object -First 1
    if (-not $m) { throw "Could not read __version__ from $init" }
    return $m.Matches[0].Groups[1].Value
}

function Copy-IdeDocs {
    param([string]$Root)
    $src = Join-Path $Root "docs\user-guide"
    $spec = Join-Path $Root "docs\specification\LANGUAGE_SPECIFICATION.md"
    $dst = Join-Path $Root "ide\dist\docs"
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    $map = @{
        "getting-started.md"        = "getting-started.md"
        "language-guide.md"         = "language-guide.md"
        "stdlib-reference.md"       = "stdlib-reference.md"
        "error-reference.md"        = "error-reference.md"
        "migration-guide.md"        = "migration-guide.md"
        "faq.md"                    = "faq.md"
        "LANGUAGE_SPECIFICATION.md" = "LANGUAGE_SPECIFICATION.md"
    }
    $missing = @()
    foreach ($key in $map.Keys) {
        if ($key -eq "LANGUAGE_SPECIFICATION.md") {
            if (Test-Path $spec) { Copy-Item -Force $spec (Join-Path $dst $map[$key]) }
            else { $missing += $key }
        } else {
            $f = Join-Path $src $key
            if (Test-Path $f) { Copy-Item -Force $f (Join-Path $dst $map[$key]) }
            else { $missing += $key }
        }
    }
    if ($missing.Count -gt 0) {
        throw "Missing docs to bundle: $($missing -join ', ')"
    }
    Write-Host "  docs bundled into ide/dist/docs" -ForegroundColor Green
}

$Version = Get-Version
Write-Host "[1/4] Frontend build (npm run build)..." -ForegroundColor Cyan
Push-Location (Join-Path $Root "ide")
try {
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
} finally {
    Pop-Location
}
Copy-IdeDocs -Root $Root

Write-Host "[2/4] PyInstaller onedir build..." -ForegroundColor Cyan
# OneDrive/Defender sometimes holds transient locks on freshly written files;
# clean and retry a few times before giving up.
$built = $false
for ($attempt = 1; $attempt -le 4 -and -not $built; $attempt++) {
    if ($attempt -gt 1) {
        Write-Host "  retry $attempt after clearing build artifacts..." -ForegroundColor Yellow
        Get-Process IStudioIDE -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Remove-Item -Recurse -Force (Join-Path $Root "build\istudio_ide"), (Join-Path $Root "dist\istudio-ide") -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    python -m PyInstaller packaging\windows\istudio_ide.spec --noconfirm 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) { $built = $true }
}
if (-not $built) { throw "PyInstaller build failed" }

Write-Host "[3/4] Inno Setup installer..." -ForegroundColor Cyan
$iscc = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { $iscc = Get-Command iscc.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source }
if (-not $iscc) { throw "ISCC.exe not found; install Inno Setup 6" }

Push-Location (Join-Path $Root "packaging\windows")
try {
    & $iscc installer.iss "/dMyAppVersion=$Version"
    if ($LASTEXITCODE -ne 0) { throw "ISCC failed" }
} finally {
    Pop-Location
}

$installer = Join-Path $Root "release\IStudioIDE-Setup-$Version.exe"
if (-not (Test-Path $installer)) { throw "Installer not produced: $installer" }
$size = [math]::Round((Get-Item $installer).Length / 1MB, 1)
Write-Host "[4/5] Portable ZIP..." -ForegroundColor Cyan
$portable = Join-Path $Root "release\istudio-ide-$Version-win-x64.zip"
Remove-Item -Force $portable -ErrorAction SilentlyContinue
Compress-Archive -Path (Join-Path $Root "dist\istudio-ide\*") -DestinationPath $portable
if (-not (Test-Path $portable)) { throw "Portable ZIP not produced: $portable" }
$zipSize = [math]::Round((Get-Item $portable).Length / 1MB, 1)
Write-Host "[5/5] Done: $installer ($size MB) + $portable ($zipSize MB)" -ForegroundColor Green
