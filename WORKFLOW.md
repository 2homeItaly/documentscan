# Document Scanner - Workflow Dettagliato

## Schema Generale della Pipeline

```
INPUT FOLDER
    │
    ├── foto1.jpg (documento A4 fotografato con smartphone)
    ├── foto2.png (prospettiva distorta, ombre, sfondo)
    └── foto3.jpg (documento inclinato)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT SCANNER PIPELINE                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 1: PREPROCESSING                                       │
│  ────────────────────────────────────────────────────────    │
│  ► Caricamento immagine                                      │
│  ► Ridimensionamento per processing (500px height)           │
│  ► Conversione in grayscale                                  │
│  ► Gaussian Blur (5x5) per riduzione rumore                  │
│                                                              │
│  Tecniche: cv2.resize, cv2.cvtColor, cv2.GaussianBlur       │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 2: EDGE DETECTION E CONTOUR FINDING                   │
│  ────────────────────────────────────────────────────────    │
│  ► Canny Edge Detection (threshold: 75, 200)                │
│  ► Dilatazione morfologica (kernel 5x5)                     │
│  ► Ricerca contorni (RETR_LIST, CHAIN_APPROX_SIMPLE)        │
│  ► Selezione contorno a 4 vertici più grande                │
│  ► Ordinamento punti: TL, TR, BR, BL                        │
│                                                              │
│  Output: Coordinate dei 4 angoli del documento              │
│  Fallback: Se non trovato, usa bordi immagine               │
│                                                              │
│  Tecniche: cv2.Canny, cv2.dilate, cv2.findContours,         │
│            cv2.approxPolyDP                                  │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 3: PERSPECTIVE TRANSFORM (4-POINT TRANSFORM)           │
│  ────────────────────────────────────────────────────────    │
│  ► Ordinamento punti angoli                                  │
│  ► Calcolo dimensioni target del documento                  │
│  ► Applicazione rapporto A4 (1:1.414)                       │
│  ► Costruzione matrice di trasformazione prospettica        │
│  ► Warping dell'immagine                                     │
│                                                              │
│  Algoritmo:                                                  │
│  1. Calcola larghezza: max(dist(BR,BL), dist(TR,TL))       │
│  2. Calcola altezza: max(dist(TR,BR), dist(TL,BL))         │
│  3. Correggi per rapporto A4                                │
│  4. getPerspectiveTransform(src_points, dst_points)         │
│  5. warpPerspective                                          │
│                                                              │
│  Tecniche: cv2.getPerspectiveTransform,                     │
│            cv2.warpPerspective                               │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 4: DESKEW (CORREZIONE INCLINAZIONE)                   │
│  ────────────────────────────────────────────────────────    │
│  ► Inversione colori per rilevamento testo                  │
│  ► Calcolo minAreaRect sui pixel di testo                   │
│  ► Estrazione angolo di rotazione                           │
│  ► Correzione angolo (se < -45°: -(90+angle))              │
│  ► Rotazione immagine se |angle| > 0.5°                     │
│                                                              │
│  Algoritmo minAreaRect:                                      │
│  - Trova il rettangolo di area minima che racchiude i pixel │
│  - L'angolo di questo rettangolo = inclinazione del testo   │
│  - Ruota l'immagine dell'angolo opposto                     │
│                                                              │
│  Tecniche: cv2.minAreaRect, cv2.getRotationMatrix2D,        │
│            cv2.warpAffine                                    │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 5: SHADOW REMOVAL & ENHANCEMENT                       │
│  ────────────────────────────────────────────────────────    │
│  ► Conversione in LAB color space                           │
│  ► Split nei canali L, A, B                                 │
│  ► Applicazione CLAHE al canale L (luminosità)              │
│  │  - clipLimit: 3.0                                        │
│  │  - tileGridSize: 8x8                                     │
│  ► Merge canali e riconversione in BGR                      │
│  ► Sharpening con kernel di convoluzione                    │
│  ► Blend con immagine originale (70% orig + 30% sharp)      │
│  ► Aumento saturazione (HSV, S-channel * 1.2)               │
│                                                              │
│  CLAHE (Contrast Limited Adaptive Histogram Equalization):  │
│  - Equalizza l'istogramma localmente (8x8 tiles)           │
│  - Previene over-amplificazione del rumore                  │
│  - Rimuove ombre mantenendo dettagli                        │
│                                                              │
│  Tecniche: cv2.cvtColor(LAB), cv2.createCLAHE,              │
│            cv2.filter2D, cv2.addWeighted                     │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 5B: ADAPTIVE THRESHOLDING (se --grayscale)            │
│  ────────────────────────────────────────────────────────    │
│  ► Conversione in grayscale                                  │
│  ► Adaptive Thresholding Gaussiano                          │
│  │  - blockSize: 11                                         │
│  │  - C: 10                                                 │
│  ► Output: immagine binaria (scanner B&N)                   │
│                                                              │
│  Adaptive Thresholding:                                      │
│  - Binarizzazione con soglia variabile localmente          │
│  - Si adatta alle variazioni di illuminazione               │
│  - Risultato: testo nero su sfondo bianco uniforme          │
│                                                              │
│  Tecniche: cv2.adaptiveThreshold                            │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 6: RESIZE TO A4                                        │
│  ────────────────────────────────────────────────────────    │
│  ► Calcolo dimensioni A4 in base al DPI:                    │
│  │  - 150 DPI: 1240 × 1754 px                               │
│  │  - 200 DPI: 1654 × 2339 px                               │
│  │  - 300 DPI: 2480 × 3508 px (DEFAULT)                     │
│  │  - 600 DPI: 4960 × 7016 px                               │
│  ► Ridimensionamento con interpolazione LANCZOS4            │
│  ► Mantiene rapporto esatto 1:1.414                         │
│                                                              │
│  LANCZOS4:                                                   │
│  - Interpolazione di massima qualità                        │
│  - Preserva dettagli fini e bordi                           │
│  - Ideale per upscaling e downscaling                       │
│                                                              │
│  Tecniche: cv2.resize(INTER_LANCZOS4)                       │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 7: SALVATAGGIO                                         │
│  ────────────────────────────────────────────────────────    │
│  ► Salvataggio JPEG con qualità specificata                 │
│  ► Nome file: processed_[originale].jpg                     │
│  ► Directory: output_dir/                                    │
│                                                              │
│  Tecniche: cv2.imwrite(IMWRITE_JPEG_QUALITY)                │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
OUTPUT FOLDER
    │
    ├── processed_foto1.jpg (documento A4 perfetto)
    ├── processed_foto2.jpg (prospettiva corretta, no ombre)
    └── processed_foto3.jpg (raddrizzato e pulito)
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  FASE 8: PDF GENERATION                                      │
│  ────────────────────────────────────────────────────────    │
│  ► Conversione BGR → RGB (OpenCV → PIL)                     │
│  ► Creazione oggetti PIL Image                              │
│  │                                                            │
│  ► Se SINGLE PDF:                                            │
│  │  ├─ Salva primo come PDF                                 │
│  │  ├─ Append altri come pagine (save_all=True)             │
│  │  └─ Output: singolo PDF multi-pagina                     │
│  │                                                            │
│  ► Se SEPARATE PDFs:                                         │
│  │  ├─ Loop su ogni immagine                                │
│  │  ├─ Salva ciascuna come PDF individuale                  │
│  │  └─ Output: un PDF per ogni documento                    │
│  │                                                            │
│  ► Impostazioni PDF:                                         │
│    - Resolution: DPI specificato                             │
│    - Format: PDF/A compatibile                               │
│    - Compression: JPEG (qualità specificata)                 │
│                                                              │
│  Tecniche: PIL.Image.save(format="PDF")                     │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
FINAL OUTPUT
    │
    ├── scanned_document.pdf (tutte le pagine)
    │   o
    ├── foto1.pdf (pagina 1)
    ├── foto2.pdf (pagina 2)
    └── foto3.pdf (pagina 3)
```

---

## Dettaglio Algoritmi ML/CV

### 1. Canny Edge Detection

**Algoritmo Multi-Stage:**

```
Input Image
    ↓
[Gaussian Filtering] → Riduce rumore
    ↓
[Gradient Calculation] → Calcola intensità e direzione gradiente (Sobel)
    ↓
[Non-Maximum Suppression] → Assottiglia i bordi a 1 pixel
    ↓
[Double Thresholding] → Classifica bordi (forte/debole/non-bordo)
    ↓
[Edge Tracking by Hysteresis] → Connette bordi deboli a forti
    ↓
Edge Map (bordi binari)
```

**Parametri Utilizzati:**
- `threshold1 = 75`: Soglia bassa
- `threshold2 = 200`: Soglia alta
- Ratio 1:2.67 (raccomandato 1:2 o 1:3)

---

### 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)

**Funzionamento:**

```
Input: Immagine in canale L (LAB)
    ↓
[Suddivisione in tiles 8×8] → Processa localmente
    ↓
[Histogram Equalization per tile] → Equalizza contrasto
    ↓
[Clip Histogram] → Limita amplificazione (clipLimit=3.0)
    ↓
[Bilinear Interpolation] → Smooth tra tiles
    ↓
Output: Immagine con contrasto uniforme
```

**Vantaggi rispetto a HE globale:**
- Adattivo alle variazioni locali di illuminazione
- Non amplifica eccessivamente il rumore
- Rimuove ombre mantenendo dettagli

---

### 3. Perspective Transform (Homography)

**Matematica:**

Data una matrice di omografia `H` (3×3):

```
| x' |   | h11  h12  h13 | | x |
| y' | = | h21  h22  h23 | | y |
| w' |   | h31  h32  h33 | | 1 |

Coordinate finali:
x_final = x' / w'
y_final = y' / w'
```

**Pipeline:**
1. Identifica 4 punti sorgente (angoli documento nell'immagine originale)
2. Definisce 4 punti destinazione (angoli rettangolo A4)
3. Calcola matrice H con `cv2.getPerspectiveTransform`
4. Applica trasformazione con `cv2.warpPerspective`

**Risultato:** Documento perfettamente rettangolare, vista frontale

---

### 4. Adaptive Thresholding

**Algoritmo Gaussiano:**

```
Per ogni pixel (x,y):
    ↓
Calcola media pesata gaussiana in neighborhood (blockSize=11)
    ↓
Threshold(x,y) = GaussianMean(x,y) - C
    ↓
Se Pixel(x,y) > Threshold(x,y):
    Output(x,y) = 255 (bianco)
Altrimenti:
    Output(x,y) = 0 (nero)
```

**Parametri:**
- `blockSize = 11`: Dimensione neighborhood
- `C = 10`: Costante sottratta alla media
- `ADAPTIVE_THRESH_GAUSSIAN_C`: Usa peso gaussiano

**Uso:** Converte documento in B&N puro, ideale per testo

---

## Confronto DPI e Qualità

| DPI | Dimensioni A4 (px) | Dimensione File | Uso Consigliato |
|-----|-------------------|-----------------|-----------------|
| 150 | 1240 × 1754       | ~200-400 KB     | Bozze, archivio compatto |
| 200 | 1654 × 2339       | ~400-700 KB     | Documenti standard |
| 300 | 2480 × 3508       | ~800-1.5 MB     | **Qualità professionale** (DEFAULT) |
| 600 | 4960 × 7016       | ~2-4 MB         | Archivio alta qualità, stampa |

---

## Parametri di Qualità JPEG

| Qualità | Compressione | Dimensione | Artefatti | Uso |
|---------|--------------|------------|-----------|-----|
| 70-80   | Alta         | Piccola    | Visibili  | Bozze |
| 85-90   | Media        | Media      | Minimi    | Standard |
| 95      | Bassa        | Grande     | Quasi zero| **Professionale** (DEFAULT) |
| 100     | Minima       | Massima    | Zero      | Archivio |

---

## Flow Control e Error Handling

```python
try:
    # Carica immagine
    image = cv2.imread(path)
    if image is None:
        raise ValueError("Immagine non valida")

    # Rileva contorni
    contour = detect_document_contour(image)
    if contour is None:
        logger.warning("Contorno non trovato, uso fallback")
        # Fallback: usa bordi immagine

    # Trasformazione prospettica
    warped = four_point_transform(image, contour)

    # Deskew
    deskewed = deskew_image(warped)

    # Enhancement
    enhanced = enhance_document(deskewed)

    # Resize
    final = resize_to_a4(enhanced)

    # Salva
    cv2.imwrite(output_path, final)

except Exception as e:
    logger.error(f"Errore: {e}")
    # Skip immagine e continua con la prossima
```

**Strategie di Fallback:**
- Se edge detection fallisce → usa bordi immagine
- Se deskew fallisce → skip rotazione
- Se singola immagine fallisce → continua batch
- Logging completo di ogni step

---

## Performance Optimization

**Tecniche Implementate:**

1. **Ridimensionamento per processing**
   - Riduce immagine a 500px height per edge detection
   - 10x più veloce su immagini 4K
   - Scala contorni a dimensione originale

2. **Interpolazione adattiva**
   - LANCZOS4 solo per resize finale
   - INTER_CUBIC per rotazioni (più veloce)

3. **Memory efficiency**
   - Processing per batch con pulizia memoria
   - Evita duplicazione array numpy inutili

4. **Algoritmi ottimizzati**
   - CLAHE con tileGridSize 8×8 (bilanciamento qualità/velocità)
   - Contour finding su primi 5 contorni (sorted by area)

---

## Validazione Output

**Checklist Qualità:**

- ✅ Rapporto dimensioni esatto 1:1.414
- ✅ Bordi documento dritti e paralleli
- ✅ Nessuna distorsione prospettica
- ✅ Sfondo uniforme senza ombre
- ✅ Testo leggibile e nitido
- ✅ Colori naturali (se colore) o B&N puro (se grayscale)
- ✅ Dimensioni file appropriate per DPI/qualità
- ✅ PDF valido e apribile

---

**Fine Workflow**
