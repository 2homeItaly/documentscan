# Document Scanner Pipeline

Pipeline automatizzata per il processing di documenti A4 fotografati con smartphone. Trasforma foto di documenti in scansioni professionali di qualità scanner.

## 🚀 Caratteristiche

- ✅ **Rilevamento automatico bordi** del foglio A4
- ✅ **Auto-crop intelligente** del documento
- ✅ **Correzione prospettiva** (perspective transform)
- ✅ **Deskew automatico** (correzione inclinazione)
- ✅ **Rimozione ombre e distorsioni** usando CLAHE
- ✅ **Enhancement qualità** simile a scanner professionale
- ✅ **Ridimensionamento preciso A4** (rapporto 1:1.414)
- ✅ **Processing batch** di multiple immagini
- ✅ **Generazione PDF** (singolo o multipli)
- ✅ **Modalità colore e bianco/nero**
- ✅ **DPI personalizzabili** (150, 200, 300, 600)
- ✅ **CLI completa** per automazione

## 📋 Requisiti

- Python 3.10 o superiore
- Sistema operativo: Linux, macOS, Windows
- RAM: minimo 2GB (4GB raccomandati per immagini ad alta risoluzione)

## 🔧 Installazione

### 1. Clona o scarica il repository

```bash
git clone <repository-url>
cd documentscan
```

### 2. Crea ambiente virtuale (raccomandato)

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### Verifica installazione

```bash
python document_scanner.py --help
```

Se vedi l'help del programma, l'installazione è andata a buon fine!

## 📖 Utilizzo

### Utilizzo base

```bash
python document_scanner.py -i ./input -o ./output
```

Questo comando:
- Processa tutte le immagini nella cartella `./input`
- Salva i risultati in `./output`
- Crea un singolo PDF con tutte le pagine

### Esempi d'uso

#### 1. Conversione in bianco e nero (effetto scanner)

```bash
python document_scanner.py -i ./documenti -o ./scansioni --grayscale
```

#### 2. PDF separati per ogni documento

```bash
python document_scanner.py -i ./input -o ./output --separate-pdfs
```

#### 3. Alta qualità con 600 DPI

```bash
python document_scanner.py -i ./input -o ./output --dpi 600 --quality 100
```

#### 4. Processing veloce con qualità standard

```bash
python document_scanner.py -i ./input -o ./output --dpi 150 --quality 85
```

#### 5. Nome PDF personalizzato

```bash
python document_scanner.py -i ./fatture -o ./output --pdf-name "Fatture_2024.pdf"
```

#### 6. Senza enhancement automatico

```bash
python document_scanner.py -i ./input -o ./output --no-enhance
```

#### 7. Modalità verbose per debugging

```bash
python document_scanner.py -i ./input -o ./output -v
```

### Parametri CLI completi

```
usage: document_scanner.py [-h] -i INPUT [-o OUTPUT] [--grayscale]
                           [--no-enhance] [--dpi {150,200,300,600}]
                           [--quality [1-100]] [--separate-pdfs]
                           [--pdf-name PDF_NAME] [-v]

Argomenti:
  -i, --input INPUT         Directory contenente le immagini da processare (OBBLIGATORIO)
  -o, --output OUTPUT       Directory di output (default: processed)
  --grayscale              Converti in bianco e nero (modalità scanner)
  --no-enhance             Disabilita enhancement automatico della qualità
  --dpi {150,200,300,600}  DPI del documento finale (default: 300)
  --quality [1-100]        Qualità JPEG 1-100 (default: 95)
  --separate-pdfs          Crea un PDF separato per ogni immagine
  --pdf-name PDF_NAME      Nome del PDF di output (default: scanned_document.pdf)
  -v, --verbose            Output verboso per debugging
```

## 📂 Struttura Directory

### Input

Organizza le tue foto di documenti in una cartella:

```
input/
├── documento1.jpg
├── documento2.png
├── fattura.jpg
└── contratto.jpeg
```

Formati supportati: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

### Output

Dopo il processing, troverai:

```
output/
├── processed_documento1.jpg    # Immagini processate
├── processed_documento2.png
├── processed_fattura.jpg
├── processed_contratto.jpeg
└── scanned_document.pdf        # PDF finale
```

## 🔬 Come Funziona: Workflow Tecnico

### Pipeline di Processing

```
┌─────────────────────┐
│  Input Image (JPG)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  1. Edge Detection          │
│  - Gaussian Blur            │
│  - Canny Edge Detection     │
│  - Contour Finding          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. Document Extraction     │
│  - 4-point detection        │
│  - Perspective Transform    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. Deskew                  │
│  - Angle detection          │
│  - Rotation correction      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  4. Enhancement             │
│  - Shadow removal (CLAHE)   │
│  - Contrast enhancement     │
│  - Sharpening               │
│  - Adaptive Thresholding    │
│    (se grayscale)           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  5. A4 Resize               │
│  - Ratio correction 1:1.414 │
│  - Interpolazione LANCZOS4  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Output Image (A4)          │
│  + PDF Generation           │
└─────────────────────────────┘
```

### Spiegazione degli Algoritmi

#### 1. **Edge Detection e Contour Finding**
- Usa **Canny Edge Detection** per rilevare i bordi
- **Gaussian Blur** per ridurre il rumore
- **Dilatazione morfologica** per chiudere gap nei bordi
- Trova i **contorni** e seleziona il più grande con 4 vertici (il documento)

#### 2. **Perspective Transform (4-Point Transform)**
- Identifica i 4 angoli del documento
- Calcola la **matrice di trasformazione prospettica**
- Applica **warpPerspective** per raddrizzare il documento
- Mantiene il rapporto A4 (1:1.414)

#### 3. **Deskew (Correzione Inclinazione)**
- Usa **minAreaRect** per trovare l'angolo di rotazione minimo
- Calcola l'angolo di correzione
- Applica **rotazione affine** se l'angolo > 0.5°

#### 4. **Shadow Removal**
- Converte in **LAB color space**
- Applica **CLAHE** (Contrast Limited Adaptive Histogram Equalization) al canale L
- Equalizza l'illuminazione rimuovendo ombre

#### 5. **Enhancement**
- **Sharpening** con kernel di convoluzione
- Aumento **contrasto e saturazione**
- Se grayscale: **Adaptive Thresholding** per effetto scanner B&N

#### 6. **A4 Resize**
- Ridimensiona a dimensioni esatte A4 in base al DPI:
  - 300 DPI: 2480 × 3508 px
  - 600 DPI: 4960 × 7016 px
- Usa **interpolazione LANCZOS4** per massima qualità

## 🎯 Parametri Raccomandati per Casi d'Uso

### Documenti Fiscali / Contratti (massima qualità)
```bash
python document_scanner.py -i ./input -o ./output \
  --grayscale --dpi 600 --quality 100
```

### Documenti generali (bilanciato)
```bash
python document_scanner.py -i ./input -o ./output \
  --dpi 300 --quality 95
```

### Processing veloce / Bozze
```bash
python document_scanner.py -i ./input -o ./output \
  --dpi 150 --quality 80
```

### Foto a colori (brochure, cataloghi)
```bash
python document_scanner.py -i ./input -o ./output \
  --dpi 300 --quality 100
```

## 🐛 Troubleshooting

### Problema: "Contorno documento non rilevato"

**Soluzione**:
- Assicurati che il documento sia ben visibile
- Lo sfondo dovrebbe contrastare col documento
- Evita ombre eccessive
- Se necessario, usa `--no-enhance` e processa manualmente

### Problema: Documento storto o tagliato male

**Soluzione**:
- Verifica che tutti e 4 gli angoli del documento siano visibili nella foto
- Evita riflessi di luce che possono confondere l'edge detection
- Scatta la foto da una distanza adeguata (documento deve occupare almeno 60% del frame)

### Problema: Output troppo scuro o troppo chiaro

**Soluzione**:
- Usa la modalità `--grayscale` per documenti di testo
- Regola la qualità con `--quality`
- Se troppo aggressivo, usa `--no-enhance`

### Problema: PDF troppo grande

**Soluzione**:
- Riduci il DPI: `--dpi 150` o `--dpi 200`
- Riduci la qualità: `--quality 80`
- Usa `--grayscale` (riduce significativamente la dimensione)

### Problema: Installazione OpenCV fallita

**Soluzione**:
```bash
# Prova prima a installare opencv-python-headless
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python-headless

# Su macOS con Apple Silicon
pip install opencv-python --no-binary opencv-python

# Su Linux, installa dipendenze sistema
sudo apt-get install python3-opencv  # Debian/Ubuntu
sudo yum install python3-opencv      # Fedora/CentOS
```

## 📊 Performance

### Benchmarks (hardware medio: i5, 8GB RAM)

| Risoluzione Input | DPI Output | Tempo/Immagine | Dimensione PDF |
|-------------------|------------|----------------|----------------|
| 3000×4000 px      | 300        | ~2-3s          | ~500KB (B&N)   |
| 3000×4000 px      | 300        | ~2-3s          | ~1.5MB (colore)|
| 3000×4000 px      | 600        | ~4-5s          | ~2MB (B&N)     |
| 4000×6000 px      | 600        | ~6-8s          | ~3MB (colore)  |

## 🔐 Privacy e Sicurezza

- ✅ Processing **100% locale** (no cloud, no API esterne)
- ✅ Nessun dato inviato online
- ✅ Ideale per documenti sensibili e riservati

## 🤝 Contribuire

Contributi sono benvenuti! Per favore:

1. Fork il repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## ⚙️ Tecnologie Utilizzate

- **OpenCV**: Computer vision e image processing
- **NumPy**: Operazioni numeriche e matriciali
- **Pillow (PIL)**: Generazione PDF e manipolazione immagini
- **Python 3.10+**: Linguaggio di programmazione

## 🎓 Algoritmi ML/AI

Lo script utilizza tecniche di **Computer Vision** e **Image Processing**:

1. **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Algoritmo di enhancement locale che migliora il contrasto senza amplificare il rumore

2. **Canny Edge Detection**: Algoritmo multi-stage per rilevamento bordi ottimale

3. **Adaptive Thresholding**: Binarizzazione locale che si adatta alle variazioni di illuminazione

4. **Perspective Transformation**: Algebra lineare per correzione prospettiva geometrica

5. **Morphological Operations**: Operazioni morfologiche (dilatazione) per processing strutturale

Questi algoritmi combinati forniscono risultati equivalenti o superiori a scanner hardware commerciali.

## 📧 Supporto

Per problemi, domande o suggerimenti, apri una issue su GitHub.

---

**Made with ❤️ for document digitalization**
