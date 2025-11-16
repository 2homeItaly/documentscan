# 📄 Document Scanner Pipeline - Riepilogo Completo del Progetto

## 🎯 Panoramica

**Document Scanner Pipeline** è uno script Python completo che automatizza il processing di documenti A4 fotografati con smartphone, trasformandoli in scansioni professionali di qualità scanner.

---

## 📁 Struttura del Progetto

```
documentscan/
│
├── 🚀 SCRIPT PRINCIPALI
│   ├── document_scanner.py          # Script principale con CLI completa
│   ├── scanner_with_config.py       # Versione con supporto configurazione JSON
│   ├── example_usage.py             # Esempi di utilizzo programmatico
│   ├── demo.py                      # Demo con documenti sintetici
│   └── test_scanner.py              # Suite di test completa
│
├── ⚙️ CONFIGURAZIONE
│   ├── requirements.txt             # Dipendenze Python
│   ├── config_example.json          # File di configurazione esempio
│   ├── .gitignore                   # Git ignore file
│   └── LICENSE                      # Licenza MIT
│
├── 📖 DOCUMENTAZIONE
│   ├── README.md                    # Documentazione completa
│   ├── QUICKSTART.md                # Guida avvio rapido (5 minuti)
│   ├── INSTALLATION.md              # Guida installazione dettagliata
│   ├── WORKFLOW.md                  # Schema tecnico della pipeline
│   └── PROJECT_SUMMARY.md           # Questo file
│
├── 🛠️ SCRIPT DI SETUP
│   ├── setup.sh                     # Setup automatico Linux/macOS
│   └── setup.bat                    # Setup automatico Windows
│
└── 📂 DIRECTORY (create automaticamente)
    ├── input/                       # Directory per immagini da processare
    ├── processed/                   # Directory output default
    ├── demo_input/                  # Generata da demo.py
    └── demo_output/                 # Generata da demo.py
```

---

## 🚀 Script Principali - Guida d'Uso

### 1. **document_scanner.py** - Script Principale

**Cosa fa:**
- Processing completo di documenti A4
- CLI con argparse per uso da terminale
- Batch processing automatico
- Generazione PDF (singolo o multipli)

**Utilizzo base:**
```bash
python document_scanner.py -i input -o processed
```

**Opzioni principali:**
```bash
-i, --input DIR           # Directory input (OBBLIGATORIO)
-o, --output DIR          # Directory output (default: processed)
--grayscale               # Modalità bianco e nero
--dpi {150,200,300,600}   # Risoluzione (default: 300)
--quality 1-100           # Qualità JPEG (default: 95)
--separate-pdfs           # Un PDF per immagine
--pdf-name NAME           # Nome PDF output
--no-enhance              # Disabilita enhancement
-v, --verbose             # Output dettagliato
```

**Esempi:**
```bash
# Scansione standard
python document_scanner.py -i ./documenti -o ./scansioni

# Bianco e nero alta qualità
python document_scanner.py -i ./input --grayscale --dpi 600 --quality 100

# PDF separati
python document_scanner.py -i ./input --separate-pdfs
```

---

### 2. **scanner_with_config.py** - Versione con Configurazione

**Cosa fa:**
- Utilizza file JSON per configurazioni predefinite
- Profili per diversi tipi di documenti
- Gestione parametri centralizzata

**Profili disponibili:**
- `default`: Configurazione standard
- `high_quality`: Massima qualità (600 DPI)
- `bw_scanner`: Scanner B&N
- `fast_draft`: Processing veloce
- `color_photos`: Foto a colori
- `invoices`: Fatture e documenti fiscali
- `contracts`: Contratti e documenti legali

**Utilizzo:**
```bash
# Lista profili disponibili
python scanner_with_config.py --list-profiles

# Usa profilo specifico
python scanner_with_config.py -i ./input --profile invoices

# Usa configurazione personalizzata
python scanner_with_config.py -i ./input --config my_config.json --profile custom
```

---

### 3. **example_usage.py** - Esempi Programmatici

**Cosa fa:**
- 7 esempi di utilizzo programmatico
- Dimostra come integrare il DocumentScanner nel tuo codice
- Mostra pipeline personalizzate

**Esempi inclusi:**
1. Utilizzo base
2. Bianco e nero con PDF separati
3. Processing singola immagine
4. Processing veloce
5. Qualità archivio
6. Pipeline personalizzata con controllo granulare
7. Batch processing con error handling avanzato

**Utilizzo:**
```bash
# Esegui in modalità interattiva
python example_usage.py

# Oppure importa nel tuo codice
from document_scanner import DocumentScanner
scanner = DocumentScanner()
processed = scanner.process_batch(Path("input"))
```

---

### 4. **demo.py** - Demonstration con Documenti Sintetici

**Cosa fa:**
- Genera documenti A4 sintetici realistici
- Applica distorsioni (prospettiva, rotazione)
- Processa con 3 configurazioni diverse
- Perfetto per testare senza foto reali

**Utilizzo:**
```bash
python demo.py
```

**Output:**
- `demo_input/`: Documenti sintetici generati
- `demo_output/color/`: Processing a colori
- `demo_output/bw/`: Processing bianco e nero
- `demo_output/high_quality/`: Processing alta qualità (600 DPI)

---

### 5. **test_scanner.py** - Suite di Test

**Cosa fa:**
- 13 test automatici
- Verifica installazione dipendenze
- Testa ogni componente della pipeline
- Report dettagliato

**Utilizzo:**
```bash
python test_scanner.py
```

**Test eseguiti:**
1. Installazione OpenCV
2. NumPy
3. Pillow
4. Import DocumentScanner
5. Documento sintetico
6. Edge detection
7. Perspective transform
8. Deskew
9. Enhancement
10. Resize A4
11. Pipeline completa
12. Creazione PDF
13. Batch processing

---

## ⚙️ Pipeline Tecnica - Come Funziona

### Step della Pipeline

```
INPUT → Edge Detection → Perspective Transform → Deskew →
Enhancement → Resize A4 → OUTPUT → PDF Generation
```

### 1. **Edge Detection**
- Gaussian Blur per riduzione rumore
- Canny Edge Detection (threshold: 75, 200)
- Ricerca contorni con 4 vertici
- Fallback: bordi immagine se non rilevato

### 2. **Perspective Transform**
- Ordinamento punti angoli (TL, TR, BR, BL)
- Calcolo matrice di trasformazione prospettica
- warpPerspective per raddrizzare
- Mantiene rapporto A4 (1:1.414)

### 3. **Deskew**
- Rilevamento angolo con minAreaRect
- Correzione rotazione se |angolo| > 0.5°
- Rotazione affine

### 4. **Enhancement**
- **Shadow Removal**: CLAHE su canale L (LAB color space)
- **Sharpening**: Kernel di convoluzione + blend
- **Adaptive Thresholding**: Se grayscale (effetto scanner B&N)
- **Saturation**: Aumento leggero per colori

### 5. **Resize A4**
- Ridimensionamento esatto in base al DPI
- Interpolazione LANCZOS4 (massima qualità)
- Rapporto fisso 1:1.414

### 6. **PDF Generation**
- Conversione BGR → RGB
- PIL Image save con parametri DPI
- Singolo PDF multi-pagina o PDF separati

---

## 📦 Dipendenze e Tecnologie

### Librerie Python

| Libreria | Versione | Utilizzo |
|----------|----------|----------|
| **OpenCV** | >= 4.8.0 | Computer vision, image processing |
| **NumPy** | >= 1.24.0 | Operazioni numeriche e array |
| **Pillow** | >= 10.0.0 | Generazione PDF e manipolazione immagini |

### Algoritmi e Tecniche

- **Canny Edge Detection**: Rilevamento bordi multi-stage
- **CLAHE**: Contrast Limited Adaptive Histogram Equalization
- **Perspective Transform**: Algebra lineare per correzione prospettiva
- **Adaptive Thresholding**: Binarizzazione locale adattiva
- **Morphological Operations**: Dilatazione per processing strutturale

---

## 📊 Performance e Dimensioni File

### Benchmarks Tipici (hardware medio)

| Input Resolution | DPI | Tempo/Immagine | Dimensione PDF |
|-----------------|-----|----------------|----------------|
| 3000×4000 px    | 150 | ~1-2s          | ~200 KB (B&N)  |
| 3000×4000 px    | 300 | ~2-3s          | ~500 KB (B&N)  |
| 3000×4000 px    | 300 | ~2-3s          | ~1.5 MB (colore) |
| 4000×6000 px    | 600 | ~6-8s          | ~3 MB (colore) |

### Dimensioni Output A4 in Base al DPI

| DPI | Dimensioni (px) | Uso Consigliato |
|-----|----------------|-----------------|
| 150 | 1240 × 1754    | Bozze, archivio compatto |
| 200 | 1654 × 2339    | Documenti standard |
| 300 | 2480 × 3508    | **Qualità professionale** (DEFAULT) |
| 600 | 4960 × 7016    | Archivio alta qualità, stampa |

---

## 🎯 Casi d'Uso e Configurazioni Consigliate

### 1. Documenti Fiscali / Fatture

```bash
python document_scanner.py -i ./fatture -o ./output \
  --grayscale --dpi 600 --quality 100 \
  --pdf-name "Fatture_2024.pdf"
```

**Perché:**
- B&N per massima compressione e OCR
- 600 DPI per leggibilità perfetta
- Qualità 100 per archiviazione legale

### 2. Contratti e Documenti Legali

```bash
python document_scanner.py -i ./contratti -o ./output \
  --dpi 600 --quality 100 --separate-pdfs
```

**Perché:**
- Colore per evidenziazioni e firme
- 600 DPI per stampa certificata
- PDF separati per organizzazione

### 3. Documenti Generici (Uso Quotidiano)

```bash
python document_scanner.py -i ./documenti -o ./output
```

**Perché:**
- Parametri default ottimizzati (300 DPI, qualità 95)
- Bilanciamento qualità/dimensione
- PDF unico per facilità

### 4. Bozze e Appunti

```bash
python document_scanner.py -i ./appunti -o ./output \
  --grayscale --dpi 150 --quality 75
```

**Perché:**
- Processing veloce
- File piccoli
- Sufficiente per consultazione

### 5. Foto a Colori (Cataloghi, Brochure)

```bash
python document_scanner.py -i ./cataloghi -o ./output \
  --dpi 300 --quality 100
```

**Perché:**
- Colore per fedeltà visiva
- Alta qualità per dettagli
- 300 DPI adeguato per visualizzazione

---

## 🛠️ Setup e Installazione

### Setup Rapido (Automatico)

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

**Windows:**
```cmd
setup.bat
venv\Scripts\activate
```

### Setup Manuale

```bash
# 1. Crea ambiente virtuale
python3 -m venv venv

# 2. Attiva ambiente virtuale
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Crea directory
mkdir input processed

# 5. Test
python test_scanner.py
```

---

## 📖 Documentazione Disponibile

| File | Contenuto |
|------|-----------|
| **README.md** | Documentazione completa e dettagliata |
| **QUICKSTART.md** | Guida rapida per iniziare in 5 minuti |
| **INSTALLATION.md** | Istruzioni installazione per ogni OS |
| **WORKFLOW.md** | Schema tecnico della pipeline e algoritmi |
| **PROJECT_SUMMARY.md** | Questo file - panoramica generale |

---

## 🔧 Configurazione Avanzata

### File config_example.json

Contiene profili predefiniti e parametri personalizzabili:

- **Profili**: 7 profili predefiniti per casi d'uso comuni
- **Parametri Edge Detection**: Threshold Canny, Gaussian blur
- **Parametri Enhancement**: CLAHE, adaptive threshold, sharpening
- **Dimensioni A4**: Configurabili in base al DPI

**Utilizzo:**
```bash
python scanner_with_config.py -i ./input --profile invoices
```

---

## 🧪 Testing e Validazione

### Test Automatici
```bash
python test_scanner.py
```

### Demo Completa
```bash
python demo.py
```

### Test Manuale con Tue Foto
```bash
# 1. Metti foto in input/
cp ~/Downloads/*.jpg input/

# 2. Processa
python document_scanner.py -i input -o processed

# 3. Verifica output
ls -lh processed/
```

---

## 🎓 Esempi di Integrazione nel Codice

### Esempio Base

```python
from document_scanner import DocumentScanner
from pathlib import Path

scanner = DocumentScanner(
    output_dir="output",
    grayscale=True,
    dpi=300
)

processed = scanner.process_batch(Path("input"))
scanner.create_pdf(processed, output_name="output.pdf")
```

### Esempio con Controllo Granulare

```python
from document_scanner import DocumentScanner
import cv2

scanner = DocumentScanner()
img = cv2.imread("documento.jpg")

# Step individuali
contour = scanner.detect_document_contour(img)
warped = scanner.four_point_transform(img, contour)
deskewed = scanner.deskew_image(warped)
enhanced = scanner.enhance_document(deskewed)
final = scanner.resize_to_a4(enhanced)

cv2.imwrite("output.jpg", final)
```

---

## 🔐 Privacy e Sicurezza

✅ **Processing 100% locale**
- Nessun dato inviato a server esterni
- Nessuna API cloud utilizzata
- Ideale per documenti sensibili e riservati

✅ **Open Source**
- Codice completamente ispezionabile
- Licenza MIT
- Nessuna telemetria o tracking

---

## 🚀 Roadmap Future (Idee)

Possibili miglioramenti futuri:

- [ ] OCR integrato (Tesseract)
- [ ] GUI desktop (tkinter/PyQt)
- [ ] Web interface (Flask/FastAPI)
- [ ] Batch OCR con output txt/searchable PDF
- [ ] Riconoscimento automatico tipo documento
- [ ] Multi-page scanning da video/fotocamera
- [ ] Cloud sync opzionale (Drive, Dropbox)
- [ ] Mobile app (Android/iOS)

---

## 📞 Supporto e Contributi

### Problemi?
1. Leggi `INSTALLATION.md` per problemi di setup
2. Esegui `python test_scanner.py` per diagnostica
3. Controlla gli esempi in `example_usage.py`
4. Consulta issue GitHub

### Contribuire?
- Fork il repository
- Crea branch feature
- Commit con messaggi descrittivi
- Apri Pull Request

---

## 📝 Licenza

**MIT License** - Vedi file `LICENSE`

Libero di usare, modificare, distribuire per scopi personali e commerciali.

---

## ✨ Quick Reference

### Comandi Essenziali

```bash
# Setup
./setup.sh && source venv/bin/activate

# Uso base
python document_scanner.py -i input -o processed

# Bianco e nero
python document_scanner.py -i input -o output --grayscale

# Alta qualità
python document_scanner.py -i input -o output --dpi 600 --quality 100

# PDF separati
python document_scanner.py -i input -o output --separate-pdfs

# Demo
python demo.py

# Test
python test_scanner.py

# Help
python document_scanner.py --help
```

---

## 🎉 Conclusione

Hai a disposizione un **sistema completo di document scanning** professionale:

✅ Script principale con CLI completa
✅ Sistema di configurazione con profili
✅ Suite di test automatici
✅ Demo con documenti sintetici
✅ Documentazione dettagliata
✅ Setup automatizzato per tutti i sistemi operativi
✅ Esempi programmatici
✅ Performance ottimizzate
✅ Privacy garantita (100% locale)

**Pronto all'uso, facile da estendere, totalmente gratuito e open source!**

---

**📄 Document Scanner Pipeline**
*Trasforma le tue foto in scansioni professionali* ✨

---

**Prossimi passi:**
1. Esegui `python demo.py` per vedere il sistema in azione
2. Leggi `QUICKSTART.md` per iniziare con le tue foto
3. Consulta `README.md` per documentazione completa

**Buon scanning! 🚀**
