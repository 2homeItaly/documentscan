# 🌐 Document Scanner - Web Interface

Interfaccia web user-friendly per il Document Scanner. Usa l'applicazione comodamente dal tuo browser!

---

## 🚀 Quick Start (3 Passi)

### 1. Installa le dipendenze

```bash
# Attiva l'ambiente virtuale (se non già fatto)
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Installa dipendenze (include Flask)
pip install -r requirements.txt
```

### 2. Avvia il server

```bash
python app.py
```

Vedrai un messaggio come questo:

```
============================================================
  Document Scanner - Web Interface
============================================================

🌐 Server in esecuzione su: http://localhost:5000

📝 Apri il browser e vai a: http://localhost:5000

🛑 Premi CTRL+C per fermare il server

============================================================
```

### 3. Apri il browser

Vai su **http://localhost:5000** nel tuo browser preferito!

---

## 📖 Come Usare l'Interfaccia Web

### Step 1: Carica i Documenti

1. **Drag & Drop**: Trascina le tue foto direttamente nella zona di caricamento
2. **Oppure**: Clicca su "Seleziona File" per scegliere dal tuo computer

**Formati supportati**: JPG, PNG, BMP, TIFF

### Step 2: Configura le Impostazioni

#### Profili Rapidi

Clicca su uno dei profili predefiniti per applicare le impostazioni ottimali:

- **📄 Standard**: Configurazione bilanciata per documenti generici (300 DPI, colore)
- **⭐ Alta Qualità**: Massima qualità per archivio (600 DPI, qualità 100%)
- **⬜ Bianco e Nero**: Modalità scanner B&N per documenti di testo
- **📋 Fatture**: Ottimizzato per fatture e documenti fiscali (600 DPI, B&N)

#### Impostazioni Dettagliate

Personalizza ogni parametro:

- **Modalità**: Colore o Bianco e Nero
- **Risoluzione (DPI)**: 150, 200, 300, o 600 DPI
- **Qualità JPEG**: Slider da 1 a 100%
- **Formato PDF**: PDF unico o PDF separati
- **Nome PDF**: Personalizza il nome del file output

### Step 3: Scansiona

Clicca sul pulsante **"Scansiona Documenti"** e attendi il processing!

### Step 4: Scarica i Risultati

- **Anteprima**: Visualizza le immagini processate nel browser
- **Scarica Singolo**: Download di un file specifico
- **Scarica Tutto (ZIP)**: Download di tutti i file in un archivio ZIP
- **Nuova Scansione**: Ricomincia con nuovi documenti

---

## 🎨 Caratteristiche dell'Interfaccia

### ✨ Design Moderno

- Interfaccia pulita e intuitiva
- Design responsive (funziona su mobile, tablet, desktop)
- Animazioni fluide e feedback visivo
- Gradiente moderno e icone SVG

### 🖱️ User-Friendly

- **Drag & Drop**: Trascina i file direttamente nell'area di caricamento
- **Profili Rapidi**: Configurazioni predefinite con un click
- **Preview in Real-Time**: Vedi i tuoi file caricati prima del processing
- **Download Flessibile**: Scarica singoli file o tutto come ZIP

### ⚡ Performance

- **Upload Multipli**: Carica più documenti contemporaneamente
- **Batch Processing**: Processa tutti i documenti in un colpo solo
- **Cleanup Automatico**: Rimuove automaticamente i file vecchi (dopo 1 ora)

### 🔒 Privacy

- **100% Locale**: Tutto il processing avviene sul tuo computer
- **Nessun Cloud**: Nessun dato viene inviato online
- **Sessioni Temporanee**: I file vengono puliti automaticamente

---

## ⚙️ Configurazione Avanzata

### Cambiare Porta del Server

Per default il server gira sulla porta 5000. Per cambiarla:

Modifica l'ultima riga in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambia 8080 con la porta desiderata
```

### Aumentare Limite di Upload

Per default il limite è 50 MB. Per aumentarlo:

Modifica in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### Modalità Produzione

Per uso in produzione (non development), usa un server WSGI come Gunicorn:

```bash
# Installa Gunicorn
pip install gunicorn

# Avvia con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Accesso da Altri Dispositivi sulla Rete

Il server è configurato per accettare connessioni da altri dispositivi sulla stessa rete locale.

1. Avvia il server: `python app.py`
2. Trova il tuo IP locale:
   ```bash
   # Linux/macOS
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```
3. Da un altro dispositivo sulla stessa rete, vai a: `http://TUO_IP:5000`

---

## 📂 Struttura Directories

La web app crea automaticamente queste directory:

```
documentscan/
├── app.py                    # Backend Flask
├── templates/
│   └── index.html           # Template HTML
├── static/
│   ├── style.css            # Stili CSS
│   └── script.js            # JavaScript
├── uploads/                 # File caricati (temporanei)
│   └── [session_id]/        # Una directory per sessione
└── web_output/              # File processati (temporanei)
    └── [session_id]/        # Una directory per sessione
```

**Nota**: Le directory `uploads/` e `web_output/` sono temporanee e vengono pulite automaticamente dopo 1 ora.

---

## 🔧 API Endpoints (per Sviluppatori)

Se vuoi integrare la web app con altri servizi:

### POST /upload
Carica file

**Request**: `multipart/form-data` con field `files[]`

**Response**:
```json
{
  "success": true,
  "session_id": "20241116_123456",
  "files": [...],
  "count": 3
}
```

### POST /process
Processa documenti

**Request**:
```json
{
  "session_id": "20241116_123456",
  "params": {
    "grayscale": false,
    "dpi": 300,
    "quality": 95,
    "single_pdf": true,
    "pdf_name": "output.pdf"
  }
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "20241116_123456",
  "processed_count": 3,
  "output_files": [...]
}
```

### GET /download/{session_id}/{filename}
Download singolo file

### GET /download-all/{session_id}
Download tutti i file come ZIP

### GET /preview/{session_id}/{filename}
Preview immagine

### GET /config-profiles
Ottieni profili di configurazione disponibili

---

## 🐛 Troubleshooting

### Problema: "Address already in use"

**Causa**: La porta 5000 è già occupata.

**Soluzione**:
```bash
# Trova il processo che usa la porta 5000
lsof -i :5000  # Linux/macOS
netstat -ano | findstr :5000  # Windows

# Uccidi il processo o cambia porta in app.py
```

### Problema: File non viene caricato

**Causa**: File troppo grande (> 50 MB).

**Soluzione**: Aumenta `MAX_CONTENT_LENGTH` in `app.py`

### Problema: "Module 'flask' not found"

**Causa**: Flask non installato.

**Soluzione**:
```bash
source venv/bin/activate  # Attiva venv
pip install Flask
```

### Problema: Processing lento

**Causa**: Molti file o alta risoluzione.

**Soluzione**:
- Riduci il DPI (usa 150 o 200 invece di 600)
- Processa meno file alla volta
- Usa modalità Bianco e Nero (più veloce)

### Problema: Browser non apre http://localhost:5000

**Soluzione**:
- Verifica che il server sia in esecuzione
- Prova con `http://127.0.0.1:5000`
- Controlla il firewall

---

## 🎯 Tips & Tricks

### 1. Keyboard Shortcuts

- **Ctrl+Click** sui file nella lista per rimuoverli
- **Drag multipli** per caricare tante foto contemporaneamente

### 2. Organizzazione File

Per evitare confusione, rinomina i tuoi file in modo sequenziale prima di caricarli:
- `documento_01.jpg`
- `documento_02.jpg`
- `documento_03.jpg`

Il PDF finale avrà le pagine nello stesso ordine!

### 3. Qualità vs Dimensione

| Uso | DPI | Qualità | Dimensione File | Tempo Processing |
|-----|-----|---------|-----------------|------------------|
| Bozza | 150 | 75% | Piccola (~200KB) | Veloce (~1s) |
| Standard | 300 | 95% | Media (~1MB) | Normale (~2-3s) |
| Archivio | 600 | 100% | Grande (~3MB) | Lento (~6-8s) |

### 4. Migliori Pratiche per le Foto

Prima di caricare:
- 📸 Scatta da sopra il documento (perpendicolare)
- 💡 Usa luce naturale uniforme
- 🎯 Includi tutti e 4 gli angoli
- ⬜ Usa sfondo contrastante

### 5. Batch Processing Massivo

Per processare centinaia di documenti:
1. Dividi in batch di 20-30 file
2. Processa ogni batch separatamente
3. Usa "PDF Separati" per organizzazione migliore
4. Unisci i PDF dopo con un tool dedicato se necessario

---

## 🔄 Confronto: CLI vs Web App

| Caratteristica | CLI (`document_scanner.py`) | Web App (`app.py`) |
|---------------|----------------------------|-------------------|
| **Interfaccia** | Terminale | Browser |
| **Facilità d'uso** | Richiede conoscenza comandi | User-friendly |
| **Drag & Drop** | ❌ No | ✅ Sì |
| **Preview** | ❌ No | ✅ Sì |
| **Profili Rapidi** | Configurazione JSON | Click sui bottoni |
| **Automazione** | ✅ Eccellente (script, cron) | ❌ Limitata |
| **Batch Massicci** | ✅ Sì (illimitato) | ⚠️ Limitato (50MB) |
| **Accesso Remoto** | ❌ Solo locale | ✅ Rete locale |

**Quando usare la CLI**:
- Automazione con script
- Processing di batch enormi
- Integrazione in pipeline esistenti

**Quando usare la Web App**:
- Utenti non tecnici
- Processing occasionale
- Preview e controllo visivo
- Accesso da mobile/tablet

---

## 🚀 Deployment

### Opzione 1: Server Locale Permanente

Usa `screen` o `tmux` per mantenere il server attivo:

```bash
# Con screen
screen -S document-scanner
python app.py
# Premi Ctrl+A poi D per detach

# Per tornare
screen -r document-scanner
```

### Opzione 2: Servizio Systemd (Linux)

Crea `/etc/systemd/system/document-scanner.service`:

```ini
[Unit]
Description=Document Scanner Web App
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/documentscan
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Attiva:
```bash
sudo systemctl enable document-scanner
sudo systemctl start document-scanner
```

### Opzione 3: Docker

```bash
# Build
docker build -t document-scanner-web .

# Run
docker run -p 5000:5000 document-scanner-web
```

---

## 📞 Supporto

Per problemi con la web app:

1. Controlla i log del server nel terminale
2. Apri la console del browser (F12) per errori JavaScript
3. Verifica che tutte le dipendenze siano installate
4. Consulta la sezione Troubleshooting sopra

---

## ✨ Caratteristiche Future (TODO)

Idee per miglioramenti futuri:

- [ ] Autenticazione utenti
- [ ] Salvataggio sessioni persistenti
- [ ] OCR integrato con output testo
- [ ] Editing avanzato (rotazione manuale, crop)
- [ ] Watermark su PDF
- [ ] Compressione PDF avanzata
- [ ] Supporto multi-lingua
- [ ] Dark mode
- [ ] Notifiche push al completamento

---

**🎉 Buon Scanning con l'interfaccia web!**

Per la documentazione del CLI, vedi `README.md` e `QUICKSTART.md`.
