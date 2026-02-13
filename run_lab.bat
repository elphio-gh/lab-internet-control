@echo off
REM Script di avvio per Lab Internet Control
REM Usa l'interprete Python nel virtual environment per garantire che le dipendenze siano trovate.

cd /d "%~dp0"

IF EXIST "venv\Scripts\python.exe" (
    echo Avvio applicazione con ambiente virtuale...
    start "" "venv\Scripts\pythonw.exe" "src\main.py"
) ELSE (
    echo ERRORE: Virtual environment 'venv' non trovato.
    echo Assicurati di aver installato correttamente il progetto.
    pause
)
