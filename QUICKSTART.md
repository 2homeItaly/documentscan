# Quick Start Guide - Document Scanner

Guida rapida per iniziare a usare Document Scanner in 5 minuti.

## ⚡ Setup Rapido (Automatico)

### Linux/macOS

```bash
# 1. Esegui lo script di setup
chmod +x setup.sh
./setup.sh

# 2. Fine! Il sistema è pronto
```

### Windows

```cmd
# 1. Esegui lo script di setup
setup.bat

# 2. Fine! Il sistema è pronto
```

---

## 🔧 Setup Manuale (se lo script automatico non funziona)

### 1. Crea ambiente virtuale

```bash
python3 -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 3. Crea le directory

```bash
mkdir input processed
```

---

## 🚀 Primo Utilizzo

### 1. Prepara le tue foto

Metti le foto dei documenti nella cartella `input/`:

```
input/
├── fattura1.jpg
├── contratto.png
└── documento.jpg
```

### 2. Esegui lo scanner

**Comando base (crea PDF unico):**

```bash
python document_scanner.py -i input -o processed
```

**Modalità bianco e nero (scanner professionale):**

```bash
python document_scanner.py -i input -o processed --grayscale
```

**PDF separati per ogni documento:**

```bash
python document_scanner.py -i input -o processed --separate-pdfs
```

### 3. Trova i risultati

```
processed/
├── processed_fattura1.jpg      # Immagini processate
├── processed_contratto.png
├── processed_documento.jpg
└── scanned_document.pdf        # PDF finale
```

---

## 📝 Comandi Comuni

### Scansione standard (uso quotidiano)

```bash
python document_scanner.py -i ./documenti -o ./scansioni
```

### Documenti fiscali/legali (massima qualità)

```bash
python document_scanner.py -i ./input -o ./output \
  --grayscale --dpi 600 --quality 100
```

### Processing veloce (bozze)

```bash
python document_scanner.py -i ./input -o ./output \
  --dpi 150 --quality 80
```

### Foto a colori (cataloghi, brochure)

```bash
python document_scanner.py -i ./input -o ./output \
  --dpi 300 --quality 100
```

### Nome PDF personalizzato

```bash
python document_scanner.py -i ./fatture -o ./output \
  --pdf-name "Fatture_Gennaio_2024.pdf"
```

---

## ❓ FAQ Rapide

### Q: Le mie foto sono troppo grandi?

**A:** No problem! Lo script ridimensiona automaticamente le immagini mantenendo la qualità.

### Q: Il documento non viene rilevato correttamente?

**A:** Assicurati che:
- Tutti e 4 gli angoli del documento siano visibili
- Lo sfondo sia diverso dal colore del documento
- Non ci siano riflessi eccessivi di luce

### Q: Il PDF è troppo grande?

**A:** Riduci DPI o qualità:
```bash
python document_scanner.py -i input -o output --dpi 150 --quality 80
```

### Q: Come ottengo il massimo dalla qualità?

**A:** Usa:
```bash
python document_scanner.py -i input -o output --dpi 600 --quality 100
```

### Q: Posso processare centinaia di documenti?

**A:** Sì! Lo script è ottimizzato per batch processing di grandi volumi.

---

## 🎯 Parametri Chiave

| Parametro | Valori | Default | Descrizione |
|-----------|--------|---------|-------------|
| `-i, --input` | percorso | - | Directory input (OBBLIGATORIO) |
| `-o, --output` | percorso | `processed` | Directory output |
| `--grayscale` | flag | off | Converti in B&N |
| `--dpi` | 150/200/300/600 | 300 | Risoluzione output |
| `--quality` | 1-100 | 95 | Qualità JPEG |
| `--separate-pdfs` | flag | off | Un PDF per immagine |
| `--pdf-name` | testo | `scanned_document.pdf` | Nome PDF |

---

## 💡 Tips & Tricks

### 1. Fotografia ottimale

- 📸 Scatta da sopra il documento (perpendicolare)
- 💡 Usa luce naturale uniforme
- 🎯 Includi tutti e 4 gli angoli del foglio
- 📏 Il documento deve occupare almeno 60% del frame
- ⬜ Usa sfondo contrastante (es. documento bianco su tavolo scuro)

### 2. Quando usare --grayscale

✅ **USA per:**
- Documenti di testo (contratti, fatture)
- Massima compressione file
- OCR successivo

❌ **NON usare per:**
- Foto a colori importanti
- Grafici/diagrammi colorati
- Documenti con evidenziazioni colorate

### 3. Scelta del DPI

- **150 DPI**: Bozze, archivio compatto (~200KB/pagina)
- **200 DPI**: Documenti standard (~400KB/pagina)
- **300 DPI**: ⭐ **Raccomandato** - Qualità professionale (~1MB/pagina)
- **600 DPI**: Archivio alta qualità, stampa (~3MB/pagina)

### 4. Automation con Script

Puoi automatizzare con cron (Linux/macOS):

```bash
# Scansiona automaticamente ogni giorno alle 18:00
0 18 * * * /path/to/venv/bin/python /path/to/document_scanner.py -i /path/to/input -o /path/to/output --grayscale
```

O con Task Scheduler (Windows).

---

## 🔥 Esempi Avanzati

### Pipeline completa con organizzazione

```bash
# 1. Processa documenti
python document_scanner.py -i ./raw_photos -o ./scanned --grayscale

# 2. Organizza per tipo
python document_scanner.py -i ./fatture -o ./output/fatture --pdf-name "Fatture_2024.pdf"
python document_scanner.py -i ./contratti -o ./output/contratti --pdf-name "Contratti_2024.pdf"
```

### Batch processing con loop

```bash
# Processa multiple directory
for dir in documenti1 documenti2 documenti3; do
    python document_scanner.py -i "$dir" -o "output_$dir" --grayscale
done
```

### Processing selettivo

```bash
# Solo JPG
python document_scanner.py -i ./input -o ./output

# Copia prima i PNG in un'altra cartella se necessario
```

---

## 🆘 Troubleshooting Rapido

### Errore: "opencv-python not found"

```bash
pip install opencv-python
```

### Errore: "No module named 'PIL'"

```bash
pip install Pillow
```

### Errore: "Permission denied"

```bash
# Linux/macOS
chmod +x document_scanner.py

# Oppure esegui con python esplicito
python document_scanner.py -i input -o output
```

### Warning: "Contorno non rilevato"

**Soluzione:**
- Migliora l'inquadratura della foto
- Assicura buon contrasto con lo sfondo
- Lo script userà comunque il fallback (bordi immagine)

---

## 📚 Risorse Utili

- **README completo**: Vedi `README.md` per documentazione dettagliata
- **Workflow tecnico**: Vedi `WORKFLOW.md` per capire come funziona
- **Esempi programmatici**: Esegui `python example_usage.py`
- **Test sistema**: Esegui `python test_scanner.py`

---

## ✅ Checklist Pre-Scanning

Prima di processare documenti importanti:

- [ ] Ho attivato l'ambiente virtuale (`source venv/bin/activate`)
- [ ] Le foto sono nella directory `input/`
- [ ] Ho verificato che tutti gli angoli del documento siano visibili
- [ ] Ho scelto i parametri giusti (DPI, qualità, grayscale)
- [ ] Ho fatto un test con 1-2 immagini prima del batch completo

---

**🎉 Sei pronto! Buon scanning!**

Per domande o problemi, vedi il README completo o esegui:

```bash
python document_scanner.py --help
```
