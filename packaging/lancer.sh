#!/bin/sh
# Ouvre l'interface graphique.
cd "$(dirname "$0")" || exit 1
PY=
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -z "$PY" ]; then
    echo "Python 3.9 ou superieur est requis. https://www.python.org/downloads/"
    exit 1
fi
exec "$PY" compensation-analytics.pyz
