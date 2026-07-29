# I Programming Language - Project Reorganization Script
# This script reorganizes the project into a clean structure

$ErrorActionPreference = "Stop"

Write-Host "I Programming Language - Project Reorganization" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Create new directory structure
Write-Host "Creating new directory structure..." -ForegroundColor Yellow

$directories = @(
    # Source code
    "src\compiler\lexer",
    "src\compiler\parser",
    "src\compiler\ast",
    "src\compiler\semantic",
    "src\compiler\typechecker",
    "src\compiler\ir",
    "src\compiler\optimizer",
    "src\compiler\codegen",
    "src\vm\core",
    "src\vm\gc",
    "src\vm\instructions",
    "src\stdlib\core",
    "src\stdlib\math",
    "src\stdlib\string",
    "src\stdlib\array",
    "src\stdlib\io",
    "src\stdlib\time",
    
    # Documentation
    "docs\specification",
    "docs\architecture",
    "docs\ecosystem",
    "docs\evolution",
    "docs\implementation",
    "docs\guides",
    "docs\api",
    
    # Tests
    "tests\unit",
    "tests\integration",
    "tests\fuzzing",
    "tests\benchmarks",
    "tests\golden\valid",
    "tests\golden\invalid",
    "tests\snapshots\lexer",
    "tests\snapshots\parser",
    
    # Examples
    "examples\tutorials",
    
    # Tools
    "tools\lsp",
    "tools\formatter",
    "tools\linter",
    "tools\debugger",
    "tools\test-runner",
    "tools\doc-gen",
    "tools\package-manager",
    
    # Frameworks
    "frameworks\web",
    "frameworks\cli",
    "frameworks\mobile",
    "frameworks\ai",
    "frameworks\games",
    "frameworks\iot",
    "frameworks\data",
    
    # Standard Library
    "stdlib\core",
    "stdlib\math",
    "stdlib\string",
    "stdlib\array",
    "stdlib\map",
    "stdlib\io",
    "stdlib\time",
    "stdlib\testing",
    "stdlib\debug",
    
    # Runtime
    "runtime\core",
    "runtime\gc",
    "runtime\libraries",
    
    # Scripts
    "scripts\build",
    "scripts\test",
    "scripts\release",
    "scripts\deploy",
    "scripts\maintenance",
    
    # Config
    "config\rust",
    "config\python",
    "config\tools"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Moving files to new locations..." -ForegroundColor Yellow

# Move compiler files
Write-Host "  Moving compiler files..." -ForegroundColor Cyan
if (Test-Path "compiler\lexer") {
    Move-Item -Path "compiler\lexer\*" -Destination "src\compiler\lexer\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "compiler\parser") {
    Move-Item -Path "compiler\parser\*" -Destination "src\compiler\parser\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "compiler\ast") {
    Move-Item -Path "compiler\ast\*" -Destination "src\compiler\ast\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "compiler\semantic") {
    Move-Item -Path "compiler\semantic\*" -Destination "src\compiler\semantic\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "compiler\compiler.py") {
    Move-Item -Path "compiler\compiler.py" -Destination "src\compiler\" -Force -ErrorAction SilentlyContinue
}

# Move VM files
Write-Host "  Moving VM files..." -ForegroundColor Cyan
if (Test-Path "vm") {
    Move-Item -Path "vm\*" -Destination "src\vm\core\" -Force -ErrorAction SilentlyContinue
}

# Move test files
Write-Host "  Moving test files..." -ForegroundColor Cyan
if (Test-Path "tests\unit") {
    Move-Item -Path "tests\unit\*" -Destination "tests\unit\" -Force -ErrorAction SilentlyContinue
}

# Move example files
Write-Host "  Moving example files..." -ForegroundColor Cyan
if (Test-Path "examples") {
    Get-ChildItem -Path "examples" -File | Move-Item -Destination "examples\" -Force -ErrorAction SilentlyContinue
}

# Move documentation
Write-Host "  Moving documentation..." -ForegroundColor Cyan
if (Test-Path "docs-internals\architecture") {
    Move-Item -Path "docs-internals\architecture\*" -Destination "docs\architecture\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "docs-internals\ecosystem") {
    Move-Item -Path "docs-internals\ecosystem\*" -Destination "docs\ecosystem\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "docs-internals\evolution") {
    Move-Item -Path "docs-internals\evolution\*" -Destination "docs\evolution\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "docs-internals\implementation") {
    Move-Item -Path "docs-internals\implementation\*" -Destination "docs\implementation\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "docs-internals\IPMP") {
    Move-Item -Path "docs-internals\IPMP\*" -Destination "docs\implementation\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "docs-specification") {
    Move-Item -Path "docs-specification\*" -Destination "docs\specification\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path "docs") {
    Get-ChildItem -Path "docs" -File | Move-Item -Destination "docs\guides\" -Force -ErrorAction SilentlyContinue
}

# Move GitHub files
Write-Host "  Moving GitHub files..." -ForegroundColor Cyan
if (Test-Path ".github-workflows") {
    New-Item -ItemType Directory -Path ".github\workflows" -Force | Out-Null
    Move-Item -Path ".github-workflows\*" -Destination ".github\workflows\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path ".github-issue-templates") {
    New-Item -ItemType Directory -Path ".github\issue-templates" -Force | Out-Null
    Move-Item -Path ".github-issue-templates\*" -Destination ".github\issue-templates\" -Force -ErrorAction SilentlyContinue
}
if (Test-Path ".github-pr-templates") {
    New-Item -ItemType Directory -Path ".github\pr-templates" -Force | Out-Null
    Move-Item -Path ".github-pr-templates\*" -Destination ".github\pr-templates\" -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Cleaning up empty directories..." -ForegroundColor Yellow

# Remove empty directories
$emptyDirs = @(
    "compiler",
    "vm",
    "tests\unit",
    "tests\integration",
    "tests\fuzzing",
    "tests\benchmarks",
    "tests\golden",
    "tests\snapshots",
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

foreach ($dir in $emptyDirs) {
    if (Test-Path $dir) {
        $items = Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue
        if ($items.Count -eq 0) {
            Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Removed empty: $dir" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Reorganization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "New structure:" -ForegroundColor Cyan
Write-Host "  src/          - Source code" -ForegroundColor White
Write-Host "  docs/         - Documentation" -ForegroundColor White
Write-Host "  tests/        - Test suite" -ForegroundColor White
Write-Host "  examples/     - Example programs" -ForegroundColor White
Write-Host "  tools/        - Developer tools" -ForegroundColor White
Write-Host "  frameworks/   - Official frameworks" -ForegroundColor White
Write-Host "  stdlib/       - Standard library" -ForegroundColor White
Write-Host "  runtime/      - Runtime system" -ForegroundColor White
Write-Host "  scripts/      - Build scripts" -ForegroundColor White
Write-Host "  config/       - Configuration" -ForegroundColor White
Write-Host "  .github/      - GitHub config" -ForegroundColor White
