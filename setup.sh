#!/bin/bash
# Setup script per Document Scanner Pipeline

echo "================================================"
echo "  Document Scanner - Setup Automatico"
echo "================================================"
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# 1. Verifica Python
echo "Step 1: Verifica versione Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        print_success "Python $PYTHON_VERSION trovato"
    else
        print_error "Python 3.10+ richiesto, trovato $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 non trovato. Installa Python 3.10+"
    exit 1
fi

# 2. Crea ambiente virtuale
echo ""
echo "Step 2: Creazione ambiente virtuale..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Ambiente virtuale creato"
else
    print_info "Ambiente virtuale già esistente"
fi

# 3. Attiva ambiente virtuale
echo ""
echo "Step 3: Attivazione ambiente virtuale..."
source venv/bin/activate
print_success "Ambiente virtuale attivato"

# 4. Aggiorna pip
echo ""
echo "Step 4: Aggiornamento pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip aggiornato"

# 5. Installa dipendenze
echo ""
echo "Step 5: Installazione dipendenze..."
print_info "Installazione di OpenCV, NumPy, Pillow..."
echo ""

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Tutte le dipendenze installate con successo"
else
    print_error "Errore nell'installazione delle dipendenze"
    exit 1
fi

# 6. Crea directory necessarie
echo ""
echo "Step 6: Creazione directory..."
mkdir -p input processed
print_success "Directory create: input/, processed/"

# 7. Test installazione
echo ""
echo "Step 7: Test installazione..."
python3 -c "import cv2; import numpy; from PIL import Image; print('Tutte le librerie importate con successo')" 2>&1

if [ $? -eq 0 ]; then
    print_success "Test importazione librerie OK"
else
    print_error "Errore nell'importazione delle librerie"
    exit 1
fi

# 8. Test DocumentScanner
echo ""
echo "Step 8: Test DocumentScanner..."
python3 test_scanner.py > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Test DocumentScanner completati con successo"
else
    print_info "Alcuni test potrebbero essere falliti (normale se non ci sono immagini)"
fi

# 9. Informazioni finali
echo ""
echo "================================================"
echo "  Setup Completato!"
echo "================================================"
echo ""
echo "Per utilizzare il Document Scanner:"
echo ""
echo "1. Attiva l'ambiente virtuale:"
echo "   $ source venv/bin/activate"
echo ""
echo "2. Metti le tue immagini nella cartella 'input/'"
echo ""
echo "3. Esegui lo scanner:"
echo "   $ python document_scanner.py -i input -o processed"
echo ""
echo "4. Per aiuto e opzioni:"
echo "   $ python document_scanner.py --help"
echo ""
echo "Per esempi avanzati:"
echo "   $ python example_usage.py"
echo ""
echo "Per eseguire i test completi:"
echo "   $ python test_scanner.py"
echo ""
print_success "Buon scanning!"
echo ""
