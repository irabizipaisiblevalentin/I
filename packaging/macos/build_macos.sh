#!/usr/bin/env bash
# build_macos.sh — build the I Studio IDE macOS disk image.
#
# Requires: Node.js (npm), Python 3.10+ with pyinstaller + pywebview installed.
#
# Outputs:
#   ide/dist/                                    frontend production build
#   dist/IStudioIDE.app/                         PyInstaller app bundle
#   release/istudio-ide-<version>-macos.dmg      disk image

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

get_version() {
    python -c "import sys; sys.path.insert(0, 'src'); from istudio.ide import __version__; print(__version__)"
}

VERSION="$(get_version)"

echo "[1/4] Frontend build (npm run build)..."
pushd ide >/dev/null
npm run build
popd >/dev/null

echo "[2/4] PyInstaller app bundle..."
python -m PyInstaller packaging/macos/istudio_ide_macos.spec --noconfirm --clean

echo "[3/4] Create disk image..."
mkdir -p release
OUT="release/istudio-ide-${VERSION}-macos.dmg"
DMG_ROOT="dist/dmg"
rm -rf "$DMG_ROOT"
mkdir -p "$DMG_ROOT"
cp -R "dist/IStudioIDE.app" "$DMG_ROOT/"
ln -s /Applications "$DMG_ROOT/Applications"
rm -f "$OUT"
hdiutil create -volname "I Studio IDE ${VERSION}" -srcfolder "$DMG_ROOT" -ov -format UDZO "$OUT"

echo "[4/4] Done: $OUT ($(du -h "$OUT" | cut -f1))"
