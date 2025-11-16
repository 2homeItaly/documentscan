# Guida Installazione Completa - Document Scanner

Istruzioni dettagliate per l'installazione su diversi sistemi operativi.

---

## 📋 Requisiti di Sistema

### Requisiti Minimi
- **Python**: 3.10 o superiore
- **RAM**: 2 GB (4 GB raccomandati per immagini ad alta risoluzione)
- **Spazio Disco**: 500 MB per dipendenze + spazio per documenti
- **Sistema Operativo**: Linux, macOS, Windows 10/11

### Dipendenze Python
- `opencv-python >= 4.8.0`
- `opencv-contrib-python >= 4.8.0`
- `numpy >= 1.24.0`
- `Pillow >= 10.0.0`

---

## 🐧 Installazione su Linux

### Ubuntu / Debian

```bash
# 1. Aggiorna il sistema
sudo apt update && sudo apt upgrade -y

# 2. Installa Python 3.10+ (se non presente)
sudo apt install python3 python3-pip python3-venv -y

# 3. Installa dipendenze di sistema per OpenCV
sudo apt install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0

# 4. Clone o scarica il progetto
git clone <repository-url>
cd documentscan

# 5. Esegui lo script di setup automatico
chmod +x setup.sh
./setup.sh

# 6. Attiva l'ambiente virtuale
source venv/bin/activate

# 7. Verifica l'installazione
python test_scanner.py
```

### Fedora / CentOS / RHEL

```bash
# 1. Installa Python 3.10+
sudo dnf install python3 python3-pip python3-virtualenv -y

# 2. Installa dipendenze sistema
sudo dnf install -y \
    libSM \
    libXext \
    libXrender

# 3. Segui gli step 4-7 come per Ubuntu
cd documentscan
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python test_scanner.py
```

### Arch Linux

```bash
# 1. Installa Python
sudo pacman -S python python-pip python-virtualenv

# 2. Installa dipendenze
sudo pacman -S libsm libxext libxrender

# 3. Setup
cd documentscan
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

---

## 🍎 Installazione su macOS

### Con Homebrew (raccomandato)

```bash
# 1. Installa Homebrew (se non installato)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Installa Python 3.10+
brew install python@3.10

# 3. Verifica versione Python
python3 --version

# 4. Clone il progetto
git clone <repository-url>
cd documentscan

# 5. Esegui setup
chmod +x setup.sh
./setup.sh

# 6. Attiva ambiente virtuale
source venv/bin/activate

# 7. Test
python test_scanner.py
```

### macOS con Apple Silicon (M1/M2/M3)

Se riscontri problemi con OpenCV su Apple Silicon:

```bash
# Installazione specifica per Apple Silicon
python3 -m venv venv
source venv/bin/activate

# Installa con architettura corretta
pip install --upgrade pip
pip install numpy
SYSTEM_VERSION_COMPAT=0 pip install opencv-python opencv-contrib-python
pip install Pillow

# Verifica
python -c "import cv2; print(cv2.__version__)"
```

---

## 🪟 Installazione su Windows

### Metodo 1: Script Automatico (raccomandato)

```cmd
REM 1. Scarica e installa Python da python.org (versione 3.10+)
REM    IMPORTANTE: Seleziona "Add Python to PATH" durante l'installazione

REM 2. Apri Command Prompt (cmd) o PowerShell

REM 3. Naviga alla directory del progetto
cd C:\path\to\documentscan

REM 4. Esegui lo script di setup
setup.bat

REM 5. Attiva ambiente virtuale
venv\Scripts\activate

REM 6. Test
python test_scanner.py
```

### Metodo 2: Setup Manuale

```cmd
REM 1. Verifica Python
python --version

REM 2. Crea ambiente virtuale
python -m venv venv

REM 3. Attiva ambiente virtuale
venv\Scripts\activate

REM 4. Aggiorna pip
python -m pip install --upgrade pip

REM 5. Installa dipendenze
pip install -r requirements.txt

REM 6. Crea directory
mkdir input
mkdir processed

REM 7. Test
python test_scanner.py
```

### Windows con Visual Studio Build Tools

Se ricevi errori di compilazione durante l'installazione di OpenCV:

```cmd
REM 1. Scarica e installa "Build Tools for Visual Studio"
REM    https://visualstudio.microsoft.com/downloads/
REM    Seleziona "Desktop development with C++"

REM 2. Riprova l'installazione
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## 🐍 Installazione con Conda/Anaconda

Se preferisci usare Conda:

```bash
# 1. Crea ambiente conda
conda create -n docscanner python=3.10 -y
conda activate docscanner

# 2. Installa dipendenze
conda install -c conda-forge opencv numpy pillow -y

# Oppure usa pip all'interno dell'ambiente conda
pip install -r requirements.txt

# 3. Test
python test_scanner.py
```

---

## 🐳 Installazione con Docker (Opzionale)

Se preferisci usare Docker:

```dockerfile
# Crea Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice
COPY . .

# Volume per input/output
VOLUME ["/app/input", "/app/processed"]

CMD ["python", "document_scanner.py", "-i", "input", "-o", "processed"]
```

```bash
# Build immagine
docker build -t document-scanner .

# Esegui
docker run -v ./input:/app/input -v ./processed:/app/processed document-scanner
```

---

## ✅ Verifica Installazione

Dopo l'installazione, verifica che tutto funzioni:

### Test Rapido

```bash
# Attiva ambiente virtuale (se non già attivo)
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Test import librerie
python -c "import cv2, numpy, PIL; print('✓ Tutte le librerie OK')"

# Test DocumentScanner
python -c "from document_scanner import DocumentScanner; print('✓ DocumentScanner OK')"

# Verifica versioni
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import PIL; print(f'Pillow: {PIL.__version__}')"
```

### Test Completo

```bash
# Esegui la suite di test completa
python test_scanner.py

# Se tutti i test passano, sei pronto!
```

### Demo con Documenti Sintetici

```bash
# Genera documenti di esempio e processali
python demo.py

# Questo creerà:
# - demo_input/ con documenti sintetici
# - demo_output/ con risultati processati
```

---

## 🔧 Risoluzione Problemi Comuni

### Problema: "Python non trovato" o "python: command not found"

**Soluzione:**
```bash
# Linux/macOS: Prova con python3
python3 --version
# Se funziona, usa python3 invece di python

# Windows: Reinstalla Python e seleziona "Add to PATH"
# Oppure aggiungi manualmente Python al PATH
```

### Problema: "No module named 'cv2'"

**Soluzione:**
```bash
# Assicurati di aver attivato l'ambiente virtuale
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstalla opencv
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python opencv-contrib-python
```

### Problema: Errore durante installazione OpenCV su macOS

**Soluzione:**
```bash
# Per macOS con Apple Silicon
SYSTEM_VERSION_COMPAT=0 pip install opencv-python

# Oppure prova opencv-python-headless
pip install opencv-python-headless
```

### Problema: "Microsoft Visual C++ 14.0 is required" (Windows)

**Soluzione:**
1. Scarica "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Installa con opzione "Desktop development with C++"
3. Riavvia computer
4. Riprova: `pip install -r requirements.txt`

### Problema: ImportError con PIL/Pillow

**Soluzione:**
```bash
pip uninstall PIL Pillow
pip install Pillow
```

### Problema: Permessi negati (Linux/macOS)

**Soluzione:**
```bash
# NON usare sudo pip install
# Invece usa ambiente virtuale:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔄 Aggiornamento

Per aggiornare il Document Scanner:

```bash
# 1. Attiva ambiente virtuale
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 2. Aggiorna dipendenze
pip install --upgrade -r requirements.txt

# 3. Verifica
python test_scanner.py
```

---

## 🗑️ Disinstallazione

Per rimuovere completamente:

```bash
# 1. Disattiva ambiente virtuale (se attivo)
deactivate

# 2. Rimuovi ambiente virtuale
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 3. Rimuovi directory di output (opzionale)
rm -rf processed demo_input demo_output test_input test_output

# 4. Rimuovi il progetto
cd ..
rm -rf documentscan
```

---

## 📞 Supporto

Se riscontri problemi durante l'installazione:

1. **Verifica requisiti di sistema**: Python 3.10+
2. **Controlla log di errore**: Salva l'output completo dell'errore
3. **Prova setup manuale**: Invece dello script automatico
4. **Consulta issue GitHub**: Qualcun altro potrebbe aver avuto lo stesso problema
5. **Crea nuova issue**: Con dettagli sistema operativo, versione Python, e log errore

---

## ✨ Installazione Riuscita?

Se tutto è andato bene, dovresti poter eseguire:

```bash
python document_scanner.py --help
```

E vedere l'help del programma!

**Prossimi passi:**
- Leggi `QUICKSTART.md` per iniziare subito
- Esegui `python demo.py` per vedere una demo
- Leggi `README.md` per documentazione completa

**Buon scanning! 📄✨**
