#!/bin/bash
# Script di avvio rapido per la Web App

echo "================================================"
echo "  Document Scanner - Web Interface"
echo "================================================"
echo ""

# Verifica ambiente virtuale
if [ ! -d "venv" ]; then
    echo "⚠ Ambiente virtuale non trovato!"
    echo "Esegui prima: ./setup.sh"
    exit 1
fi

# Attiva ambiente virtuale
echo "🔧 Attivazione ambiente virtuale..."
source venv/bin/activate

# Verifica Flask
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Flask non installato. Installazione in corso..."
    pip install Flask Werkzeug
fi

echo ""
echo "✅ Tutto pronto!"
echo ""
echo "🚀 Avvio del server web..."
echo ""

# Avvia l'app
python app.py
