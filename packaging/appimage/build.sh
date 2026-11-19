#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/abulchess-appimage"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/abulchess-appimage.XXXXXX")"
APPDIR="$WORK_DIR/AbulChess.AppDir"
OUTPUT="$ROOT_DIR/dist/AbulChess-x86_64.AppImage"

cleanup() {
  rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

if [[ "$(uname -m)" != x86_64 ]]; then
  echo "This build script currently supports x86_64 Linux only." >&2
  exit 1
fi

for tool in curl tar; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Required build tool not found: $tool" >&2
    exit 1
  fi
done

download() {
  local url="$1"
  local destination="$2"
  if [[ ! -s "$destination" ]]; then
    mkdir -p "$(dirname -- "$destination")"
    curl --fail --location --retry 3 "$url" -o "$destination.part"
    mv -- "$destination.part" "$destination"
  fi
}

PYTHON_ARCHIVE="$CACHE_DIR/cpython-3.12.16-x86_64-install_only.tar.gz"
download \
  'https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.12.16%2B20261110-x86_64-unknown-linux-gnu-install_only.tar.gz' \
  "$PYTHON_ARCHIVE"

APPIMAGETOOL="${APPIMAGETOOL:-}"
if [[ -z "$APPIMAGETOOL" ]]; then
  APPIMAGETOOL="$(command -v appimagetool || true)"
fi
if [[ -z "$APPIMAGETOOL" ]]; then
  APPIMAGETOOL="$CACHE_DIR/appimagetool-x86_64.AppImage"
  download \
    'https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage' \
    "$APPIMAGETOOL"
  chmod +x "$APPIMAGETOOL"
fi

mkdir -p \
  "$APPDIR/usr/bin" \
  "$APPDIR/usr/share/applications" \
  "$APPDIR/usr/share/icons/hicolor/scalable/apps" \
  "$APPDIR/server" \
  "$APPDIR/engines/piper-turkish-tts"
tar -xzf "$PYTHON_ARCHIVE" --strip-components=1 -C "$APPDIR/usr"
cp "$ROOT_DIR/server/satranc.py" "$APPDIR/server/"
cp -a "$ROOT_DIR/assets" "$APPDIR/"
cp "$ROOT_DIR/engines/stockfish-linux-x86-64-universal" "$APPDIR/engines/"
chmod +x "$APPDIR/engines/stockfish-linux-x86-64-universal"
cp "$ROOT_DIR/engines/piper-turkish-tts/config.json" "$APPDIR/engines/piper-turkish-tts/"
cp "$ROOT_DIR/engines/piper-turkish-tts/model.onnx" "$APPDIR/engines/piper-turkish-tts/"

PIP_CACHE_DIR="$CACHE_DIR/pip" \
  "$APPDIR/usr/bin/python3.12" -m pip install \
    --disable-pip-version-check \
    --no-warn-script-location \
    --target "$APPDIR/usr/lib/python3.12/site-packages" \
    'piper-tts==1.8.0'

cp "$SCRIPT_DIR/AppRun" "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"
cp "$SCRIPT_DIR/AbulChess.desktop" "$APPDIR/AbulChess.desktop"
cp "$SCRIPT_DIR/AbulChess.desktop" "$APPDIR/usr/share/applications/AbulChess.desktop"
cp "$SCRIPT_DIR/abulchess.svg" "$APPDIR/abulchess.svg"
cp "$SCRIPT_DIR/abulchess.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/abulchess.svg"
ln -s abulchess.svg "$APPDIR/.DirIcon"

mkdir -p "$ROOT_DIR/dist"
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"
chmod +x "$OUTPUT"
printf 'Created %s\n' "$OUTPUT"
