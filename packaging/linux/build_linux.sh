#!/usr/bin/env bash
# build_linux.sh — build the I Studio IDE Linux portable tarball.
#
# Requires: Node.js (npm), Python 3.10+ with pyinstaller + pywebview installed.
#
# Outputs:
#   ide/dist/                                    frontend production build
#   dist/istudio-ide/                            PyInstaller onedir app
#   release/istudio-ide-<version>-linux-x86_64.tar.gz  portable tarball

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

get_version() {
    python -c "import sys; sys.path.insert(0, 'src'); from istudio.ide import __version__; print(__version__)"
}

VERSION="$(get_version)"
ARCH="$(uname -m)"
case "$ARCH" in
    x86_64) PLATFORM="x86_64" ;;
    aarch64|arm64) PLATFORM="aarch64" ;;
    *) PLATFORM="$ARCH" ;;
esac

echo "[1/4] Frontend build (npm run build)..."
pushd ide >/dev/null
npm run build
popd >/dev/null

echo "[2/4] PyInstaller onedir build..."
python -m PyInstaller packaging/linux/istudio_ide_linux.spec --noconfirm --clean

echo "[3/4] Package portable tarball..."
OUT="release/istudio-ide-${VERSION}-linux-${PLATFORM}.tar.gz"
mkdir -p release
rm -f "$OUT"
tar -czf "$OUT" -C dist istudio-ide

echo "[4/4] Done: $OUT ($(du -h "$OUT" | cut -f1))"
