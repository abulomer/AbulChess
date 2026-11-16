#!/usr/bin/env bash
# ==============================================================================
# Satranç Pro — Linux / macOS Başlatıcı
# Gereksinim: Python 3.8+
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1) Venv içindeki Python'u kontrol et (server/venv veya root venv)
if [ -x "$DIR/server/venv/bin/python" ]; then
    PY="$DIR/server/venv/bin/python"
elif [ -x "$DIR/venv/bin/python" ]; then
    PY="$DIR/venv/bin/python"
elif [ -x "$DIR/server/venv/bin/python3" ]; then
    PY="$DIR/server/venv/bin/python3"
elif [ -x "$DIR/venv/bin/python3" ]; then
    PY="$DIR/venv/bin/python3"
else
    # 2) Sistem Python'u
    PY=$(command -v python3 || command -v python)
fi

if [ -z "$PY" ]; then
    echo "Hata: python3 bulunamadı. Lütfen Python 3.8+ yükleyin."
    exit 1
fi

# Python 3.8+ sürüm kontrolü
if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    echo "Hata: Python 3.8 veya üzeri gereklidir."
    exit 1
fi

# Terminali temizle ve uygulamayı çalıştır
clear
exec "$PY" "$DIR/server/satranc.py" "$@"
