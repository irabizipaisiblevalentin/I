# I Programming Language - Verify Structure Script
# This script verifies the new project structure

$ErrorActionPreference = "Stop"

Write-Host "I Programming Language - Structure Verification" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check required directories
Write-Host "Checking required directories..." -ForegroundColor Yellow

$requiredDirs = @(
    "src\compiler",
    "src\vm",
    "src\stdlib",
    "docs\specification",
    "docs\architecture",
    "docs\ecosystem",
    "docs\evolution",
    "docs\implementation",
    "docs\guides",
    "docs\api",
    "tests\unit",
    "tests\integration",
    "tests\fuzzing",
    "tests\benchmarks",
    "tests\golden",
    "tests\snapshots",
    "examples",
    "tools\lsp",
    "tools\formatter",
    "tools\linter",
    "tools\debugger",
    "tools\test-runner",
    "tools\doc-gen",
    "tools\package-manager",
    "frameworks\web",
    "frameworks\cli",
    "frameworks\mobile",
    "frameworks\ai",
    "frameworks\games",
    "frameworks\iot",
    "frameworks\data",
    "stdlib\core",
    "stdlib\math",
    "stdlib\string",
    "stdlib\array",
    "stdlib\map",
    "stdlib\io",
    "stdlib\time",
    "stdlib\testing",
    "stdlib\debug",
    "runtime\core",
    "runtime\gc",
    "runtime\libraries",
    "scripts\build",
    "scripts\test",
    "scripts\release",
    "scripts\deploy",
    "scripts\maintenance",
    "config\rust",
    "config\python",
    "config\tools",
    ".github\workflows",
    ".github\issue-templates",
    ".github\pr-templates"
)

$missingDirs = @()
foreach ($dir in $requiredDirs) {
    if (!(Test-Path $dir)) {
        $missingDirs += $dir
    }
}

if ($missingDirs.Count -gt 0) {
    Write-Host "  Missing directories:" -ForegroundColor Red
    foreach ($dir in $missingDirs) {
        Write-Host "    - $dir" -ForegroundColor Red
    }
} else {
    Write-Host "  All required directories exist" -ForegroundColor Green
}

# Check required files
Write-Host ""
Write-Host "Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "README.md",
    "ARCHITECTURE.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "LICENSE",
    "GOVERNANCE.md",
    "SECURITY.md",
    "TESTING_GUIDE.md",
    "STYLE_GUIDE.md",
    "API_GUIDELINES.md",
    "VERSIONING.md",
    "RELEASE_PROCESS.md",
    "ROADMAP.md",
    "PROJECT_STRUCTURE.md",
    "docs\specification\LANGUAGE_SPECIFICATION.md",
    "docs\implementation\IPMP.md",
    "config\rust\Cargo.toml",
    "config\python\pyproject.toml",
    "config\tools\.pre-commit-config.yaml"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "  Missing files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "    - $file" -ForegroundColor Red
    }
} else {
    Write-Host "  All required files exist" -ForegroundColor Green
}

# Check for redundant directories
Write-Host ""
Write-Host "Checking for redundant directories..." -ForegroundColor Yellow

$redundantDirs = @(
    "compiler",
    "vm",
    "docs-internals",
    "docs-specification",
    ".github-workflows",
    ".github-issue-templates",
    ".github-pr-templates",
    "frameworks-ai",
    "frameworks-cloud",
    "frameworks-core",
    "frameworks-data",
    "frameworks-desktop",
    "frameworks-games",
    "frameworks-mobile",
    "frameworks-networking",
    "frameworks-robotics",
    "frameworks-systems",
    "frameworks-web",
    "ide-build-system",
    "ide-core",
    "ide-debugger",
    "ide-editor",
    "ide-intellisense",
    "ide-plugins",
    "ide-project-management",
    "ide-terminal",
    "ide-themes",
    "ide-version-control",
    "infrastructure-cd",
    "infrastructure-ci",
    "infrastructure-monitoring",
    "infrastructure-security",
    "runtime-core",
    "runtime-libraries",
    "scripts-build",
    "scripts-deploy",
    "scripts-development",
    "scripts-maintenance",
    "scripts-release",
    "scripts-test",
    "self-hosting-compiler",
    "stdlib-core",
    "stdlib-platform",
    "tests-fuzzing",
    "tests-integration",
    "tests-performance",
    "tests-property",
    "tests-regression",
    "tests-unit",
    "tools-benchmarking",
    "tools-core",
    "tools-debugger",
    "tools-documentation",
    "tools-formatter",
    "tools-linter",
    "tools-package-manager",
    "tools-testing",
    "vm-core",
    "vm-optimizations",
    "benchmarks-compiler",
    "benchmarks-frameworks",
    "benchmarks-runtime",
    "benchmarks-stdlib",
    "bootstrap-compiler",
    "compiler-backends",
    "compiler-core",
    "compiler-frontends",
    "docs-api",
    "docs-faq",
    "docs-glossary",
    "docs-guides",
    "docs-tutorials",
    "examples-benchmarks",
    "examples-migration",
    "examples-real-world",
    "examples-tutorials",
    "governance-committees",
    "governance-policies",
    "governance-processes"
)

$foundRedundant = @()
foreach ($dir in $redundantDirs) {
    if (Test-Path $dir) {
        $foundRedundant += $dir
    }
}

if ($foundRedundant.Count -gt 0) {
    Write-Host "  Found redundant directories:" -ForegroundColor Yellow
    foreach ($dir in $foundRedundant) {
        Write-Host "    - $dir" -ForegroundColor Yellow
    }
} else {
    Write-Host "  No redundant directories found" -ForegroundColor Green
}

# Check for redundant files
Write-Host ""
Write-Host "Checking for redundant files..." -ForegroundColor Yellow

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

$foundRedundantFiles = @()
foreach ($file in $redundantFiles) {
    if (Test-Path $file) {
        $foundRedundantFiles += $file
    }
}

if ($foundRedundantFiles.Count -gt 0) {
    Write-Host "  Found redundant files:" -ForegroundColor Yellow
    foreach ($file in $foundRedundantFiles) {
        Write-Host "    - $file" -ForegroundColor Yellow
    }
} else {
    Write-Host "  No redundant files found" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "Verification Summary:" -ForegroundColor Cyan
Write-Host "  Missing directories: $($missingDirs.Count)" -ForegroundColor $(if ($missingDirs.Count -gt 0) { "Red" } else { "Green" })
Write-Host "  Missing files: $($missingFiles.Count)" -ForegroundColor $(if ($missingFiles.Count -gt 0) { "Red" } else { "Green" })
Write-Host "  Redundant directories: $($foundRedundant.Count)" -ForegroundColor $(if ($foundRedundant.Count -gt 0) { "Yellow" } else { "Green" })
Write-Host "  Redundant files: $($foundRedundantFiles.Count)" -ForegroundColor $(if ($foundRedundantFiles.Count -gt 0) { "Yellow" } else { "Green" })

if ($missingDirs.Count -eq 0 -and $missingFiles.Count -eq 0 -and $foundRedundant.Count -eq 0 -and $foundRedundantFiles.Count -eq 0) {
    Write-Host ""
    Write-Host "Project structure is clean and organized!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Please fix the issues above." -ForegroundColor Yellow
}
