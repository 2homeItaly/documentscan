# 🚀 Document Scanner - Avvio Rapido

## 📋 Hai 2 Opzioni

### ✨ Opzione 1: Interfaccia Web (RACCOMANDATO - Più Facile!)

**Perfetto per tutti, specialmente se non sei pratico col terminale.**

```bash
# Linux/macOS
./start_webapp.sh

# Windows
start_webapp.bat
```

**Poi apri il browser e vai a:**
```
http://localhost:5000
```

**Cosa puoi fare:**
- ✅ Drag & Drop delle tue foto
- ✅ Vedere l'anteprima dei risultati
- ✅ Scegliere profili predefiniti (Standard, Alta Qualità, Fatture, etc.)
- ✅ Scaricare tutto in un click
- ✅ Interfaccia bellissima e moderna!

📖 **Guida completa**: Vedi [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)

---

### 💻 Opzione 2: Linea di Comando (CLI)

**Per utenti avanzati e automazione.**

```bash
# Metti le tue foto nella cartella "input"
mkdir input
cp /path/to/photos/*.jpg input/

# Esegui lo scanner
python document_scanner.py -i input -o processed

# I risultati saranno in "processed/"
```

📖 **Guida completa**: Vedi [README.md](README.md) e [QUICKSTART.md](QUICKSTART.md)

---

## ⚡ Setup Iniziale (Solo la Prima Volta)

Se non l'hai ancora fatto:

```bash
# Linux/macOS
./setup.sh

# Windows
setup.bat
```

Questo installerà tutto il necessario!

---

## 📚 Documentazione Completa

- **[WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)** - Guida completa interfaccia web
- **[QUICKSTART.md](QUICKSTART.md)** - Guida rapida CLI (5 minuti)
- **[README.md](README.md)** - Documentazione completa e dettagliata
- **[INSTALLATION.md](INSTALLATION.md)** - Installazione per tutti i sistemi operativi
- **[WORKFLOW.md](WORKFLOW.md)** - Come funziona tecnicamente
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Panoramica del progetto

---

## 🎯 Quale Modalità Usare?

| Caratteristica | Web Interface | CLI |
|---------------|---------------|-----|
| **Facilità** | ⭐⭐⭐⭐⭐ Semplicissima | ⭐⭐⭐ Richiede pratica terminale |
| **Preview** | ✅ Sì | ❌ No |
| **Drag & Drop** | ✅ Sì | ❌ No |
| **Automazione** | ❌ No | ✅ Eccellente |
| **Batch Grandi** | ⚠️ Limitato (50MB) | ✅ Illimitato |

**Consiglio**: Inizia con la **Web Interface** per vedere cosa può fare, poi passa alla CLI se ti serve automazione!

---

## ❓ Problemi?

1. **Non si avvia?** Esegui prima `./setup.sh` (o `setup.bat` su Windows)
2. **Errori di dipendenze?** Attiva l'ambiente virtuale: `source venv/bin/activate`
3. **Porta già in uso?** Qualcun altro sta usando la porta 5000, chiudi altre applicazioni
4. **Altri problemi?** Vedi la sezione Troubleshooting in [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)

---

## 🎉 Pronto!

**Per la Web Interface:**
```bash
./start_webapp.sh    # Linux/macOS
start_webapp.bat     # Windows
```

**Per la CLI:**
```bash
python document_scanner.py -i input -o output
```

**Buon scanning! 📄✨**
