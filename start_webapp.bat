@echo off
REM Script di avvio rapido per la Web App (Windows)

echo ================================================
echo   Document Scanner - Web Interface
echo ================================================
echo.

REM Verifica ambiente virtuale
if not exist "venv" (
    echo [X] Ambiente virtuale non trovato!
    echo Esegui prima: setup.bat
    pause
    exit /b 1
)

REM Attiva ambiente virtuale
echo [+] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

REM Verifica Flask
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [!] Flask non installato. Installazione in corso...
    pip install Flask Werkzeug
)

echo.
echo [+] Tutto pronto!
echo.
echo [+] Avvio del server web...
echo.

REM Avvia l'app
python app.py

pause
