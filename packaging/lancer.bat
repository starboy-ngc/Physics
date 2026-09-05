@echo off
REM Ouvre l'interface graphique.
cd /d "%~dp0"
set PY=
pyw --version >nul 2>nul && set PY=pyw
if not defined PY pythonw --version >nul 2>nul && set PY=pythonw
if not defined PY py --version >nul 2>nul && set PY=py
if not defined PY python --version >nul 2>nul && set PY=python
if not defined PY (
    echo.
    echo   Python 3.9 ou superieur est requis sur ce poste.
    echo   Telechargement : https://www.python.org/downloads/
    echo   Cochez "Add Python to PATH" pendant l'installation.
    echo.
    pause
    exit /b 1
)
start "" %PY% compensation-analytics.pyz
