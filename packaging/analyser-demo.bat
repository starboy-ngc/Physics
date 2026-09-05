@echo off
REM Analyse en lot, sans interface.
cd /d "%~dp0"
set PY=
py --version >nul 2>nul && set PY=py
if not defined PY python --version >nul 2>nul && set PY=python
if not defined PY (
    echo   Python 3.9 ou superieur est requis. https://www.python.org/downloads/
    pause & exit /b 1
)
%PY% compensation-analytics.pyz analyse population-demo.xlsx ^
    --segment grade --segment business_unit --segment gender ^
    --date-reference 2026-01-01 --titre "Analyse de demonstration" ^
    --sortie resultats
if errorlevel 1 (pause & exit /b 1)
start "" "resultats"
pause
