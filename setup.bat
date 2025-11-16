@echo off
REM Setup script per Document Scanner Pipeline (Windows)

echo ================================================
echo   Document Scanner - Setup Automatico (Windows)
echo ================================================
echo.

REM 1. Verifica Python
echo Step 1: Verifica versione Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python non trovato. Installa Python 3.10+ da python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [+] Python %PYTHON_VERSION% trovato

REM 2. Crea ambiente virtuale
echo.
echo Step 2: Creazione ambiente virtuale...
if not exist "venv" (
    python -m venv venv
    echo [+] Ambiente virtuale creato
) else (
    echo [i] Ambiente virtuale gia esistente
)

REM 3. Attiva ambiente virtuale
echo.
echo Step 3: Attivazione ambiente virtuale...
call venv\Scripts\activate.bat
echo [+] Ambiente virtuale attivato

REM 4. Aggiorna pip
echo.
echo Step 4: Aggiornamento pip...
python -m pip install --upgrade pip >nul 2>&1
echo [+] pip aggiornato

REM 5. Installa dipendenze
echo.
echo Step 5: Installazione dipendenze...
echo [i] Installazione di OpenCV, NumPy, Pillow...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo [X] Errore nell'installazione delle dipendenze
    pause
    exit /b 1
)

echo [+] Tutte le dipendenze installate con successo

REM 6. Crea directory necessarie
echo.
echo Step 6: Creazione directory...
if not exist "input" mkdir input
if not exist "processed" mkdir processed
echo [+] Directory create: input\, processed\

REM 7. Test installazione
echo.
echo Step 7: Test installazione...
python -c "import cv2; import numpy; from PIL import Image; print('Tutte le librerie importate con successo')" 2>&1

if errorlevel 1 (
    echo [X] Errore nell'importazione delle librerie
    pause
    exit /b 1
)

echo [+] Test importazione librerie OK

REM 8. Informazioni finali
echo.
echo ================================================
echo   Setup Completato!
echo ================================================
echo.
echo Per utilizzare il Document Scanner:
echo.
echo 1. Attiva l'ambiente virtuale:
echo    venv\Scripts\activate
echo.
echo 2. Metti le tue immagini nella cartella 'input\'
echo.
echo 3. Esegui lo scanner:
echo    python document_scanner.py -i input -o processed
echo.
echo 4. Per aiuto e opzioni:
echo    python document_scanner.py --help
echo.
echo Per esempi avanzati:
echo    python example_usage.py
echo.
echo Per eseguire i test completi:
echo    python test_scanner.py
echo.
echo [+] Buon scanning!
echo.
pause
