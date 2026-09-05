#!/bin/sh
# Analyse en lot, sans interface.
cd "$(dirname "$0")" || exit 1
PY=
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
[ -z "$PY" ] && { echo "Python 3.9+ requis. https://www.python.org/downloads/"; exit 1; }
"$PY" compensation-analytics.pyz analyse population-demo.xlsx \
    --segment grade --segment business_unit --segment gender \
    --date-reference 2026-01-01 --titre "Analyse de demonstration" \
    --sortie resultats
