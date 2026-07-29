# I Programming Language - Cleanup Script
# This script removes redundant files and folders

$ErrorActionPreference = "Stop"

Write-Host "I Programming Language - Cleanup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Remove redundant files
Write-Host "Removing redundant files..." -ForegroundColor Yellow

$redundantFiles = @(
    "desktop.ini",
    ".black",
    ".pylintrc",
    ".isort.cfg",
    ".flake8",
    ".coveragerc",
    "pytest.ini",
    "mypy.ini"
)

foreach ($file in $redundantFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed: $file" -ForegroundColor Red
    }
}

# Remove Python cache directories
Write-Host "Removing Python cache..." -ForegroundColor Yellow

$cacheDirs = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    "htmlcov",
    ".tox",
    "dist",
    "build",
    "*.egg-info"
)

foreach ($pattern in $cacheDirs) {
    $items = Get-ChildItem -Path "." -Filter $pattern -Recurse -Directory -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed: $($item.FullName)" -ForegroundColor Red
    }
}

# Remove Rust build artifacts
Write-Host "Removing Rust build artifacts..." -ForegroundColor Yellow

$rustArtifacts = @(
    "target",
    "*.rlib",
    "*.rmeta"
)

foreach ($pattern in $rustArtifacts) {
    $items = Get-ChildItem -Path "." -Filter $pattern -Recurse -Directory -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed: $($item.FullName)" -ForegroundColor Red
    }
}

# Remove IDE files
Write-Host "Removing IDE files..." -ForegroundColor Yellow

$ideFiles = @(
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db"
)

foreach ($pattern in $ideFiles) {
    $items = Get-ChildItem -Path "." -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed: $($item.FullName)" -ForegroundColor Red
    }
}

# Remove temporary files
Write-Host "Removing temporary files..." -ForegroundColor Yellow

$tempFiles = @(
    "*.tmp",
    "*.temp",
    "*.log",
    "*.bak",
    "*.old",
    "*.orig"
)

foreach ($pattern in $tempFiles) {
    $items = Get-ChildItem -Path "." -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        Remove-Item -Path $item.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed: $($item.FullName)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  - Removed redundant config files" -ForegroundColor White
Write-Host "  - Removed Python cache" -ForegroundColor White
Write-Host "  - Removed Rust build artifacts" -ForegroundColor White
Write-Host "  - Removed IDE files" -ForegroundColor White
Write-Host "  - Removed temporary files" -ForegroundColor White
