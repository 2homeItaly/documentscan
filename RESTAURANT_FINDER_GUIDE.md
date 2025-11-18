# 🍕 Restaurant Finder - Guida Completa

## 📋 Indice
1. [Panoramica](#panoramica)
2. [Struttura del Progetto](#struttura-del-progetto)
3. [Spiegazione File per File](#spiegazione-file-per-file)
4. [Setup Locale](#setup-locale)
5. [Deploy su Netlify](#deploy-su-netlify)
6. [Utilizzo dell'API](#utilizzo-dellapi)
7. [Troubleshooting](#troubleshooting)
8. [Limitazioni e Best Practices](#limitazioni-e-best-practices)

---

## 🎯 Panoramica

Questo progetto fornisce un **backend serverless completamente gratuito** che trova e classifica i migliori ristoranti vicino a un indirizzo dato.

### Caratteristiche

✅ **100% Gratuito** - Nessuna API a pagamento
✅ **Serverless** - Funziona su Netlify Functions
✅ **Geocoding** - Usa Nominatim di OpenStreetMap
✅ **Ricerca POI** - Usa Overpass API
✅ **Classificazione Intelligente** - 5 categorie automatiche
✅ **CORS Enabled** - Utilizzabile da qualsiasi frontend
✅ **Error Handling** - Gestione completa degli errori

### API Utilizzate (Gratuite)

- **Nominatim** ([nominatim.openstreetmap.org](https://nominatim.openstreetmap.org)) - Geocoding
- **Overpass API** ([overpass-api.de](https://overpass-api.de)) - Query OpenStreetMap

---

## 📁 Struttura del Progetto

```
documentscan/
├── netlify/
│   └── functions/
│       └── places.js              # Funzione serverless principale
├── netlify.toml                   # Configurazione Netlify
├── package.json                   # Dipendenze Node.js
├── test-restaurant-finder.html    # File HTML di test
└── RESTAURANT_FINDER_GUIDE.md     # Questa guida
```

---

## 📝 Spiegazione File per File

### 1. `netlify/functions/places.js`

**Funzione serverless principale** che gestisce l'intera logica.

#### Flusso di Esecuzione

```
Request → Validazione → Geocoding → Overpass Query → Classificazione → Response
```

#### Funzioni Principali

1. **`handler(event, context)`**
   - Entry point della funzione Netlify
   - Gestisce CORS, validazione parametri, errori

2. **`geocodeAddress(address)`**
   - Converte l'indirizzo in coordinate (lat, lon)
   - Usa Nominatim API

3. **`findNearbyRestaurants(lat, lon, radius)`**
   - Cerca POI OpenStreetMap nel raggio specificato
   - Query Overpass per amenity: restaurant, cafe, bar, fast_food

4. **`categorizeRestaurants(restaurants)`**
   - Classifica i ristoranti in 5 categorie
   - Sistema di scoring basato su keywords, cuisine tags, e nomi

5. **`calculateCategoryScore(restaurant, category)`**
   - Calcola punteggio per ogni ristorante/categoria
   - Fattori: nome (x3), cuisine (x5), description (x2), special tags (x4)

#### Categorie

```javascript
{
  pasta: [],    // Cucina italiana, trattorie, osterie
  fish: [],     // Pesce, seafood
  meat: [],     // Carne, steakhouse, BBQ
  pizza: [],    // Pizzerie
  other: []     // Americano, messicano, vegetariano, asiatico, etc.
}
```

#### Esempio Response

```json
{
  "address": "Via Sparano, Bari",
  "geocoded_address": "Via Sparano, Bari, Puglia, Italia",
  "center": {
    "lat": 41.1177,
    "lon": 16.8719
  },
  "search_radius_meters": 1500,
  "total_found": 45,
  "pasta": [
    {
      "name": "Trattoria da Mimi",
      "cuisine": "italian",
      "amenity": "restaurant",
      "address": "Via delle Murge 13, Bari",
      "lat": 41.1180,
      "lon": 16.8722,
      "score": 8
    }
  ],
  "fish": [...],
  "meat": [...],
  "pizza": [...],
  "other": [...]
}
```

---

### 2. `netlify.toml`

**File di configurazione Netlify**

```toml
[functions]
  directory = "netlify/functions"
  node_bundler = "esbuild"
```

- `directory`: Dove Netlify cerca le funzioni serverless
- `node_bundler`: Usa esbuild (più veloce di webpack)

**Redirect opzionale**:
```toml
[[redirects]]
  from = "/api/places"
  to = "/.netlify/functions/places"
```
Permette di usare `/api/places` invece di `/.netlify/functions/places`

---

### 3. `package.json`

**Dipendenze del progetto**

```json
{
  "type": "module",
  "dependencies": {
    "node-fetch": "^3.3.2"
  }
}
```

- `"type": "module"` - Abilita ES Modules (import/export)
- `node-fetch` - Fetch API per Node.js (necessario per Node < 18)

---

### 4. `test-restaurant-finder.html`

**Pagina HTML di test** con interfaccia grafica.

#### Come Usarlo

1. **Locale** (con Netlify CLI):
   - URL: `http://localhost:8888/.netlify/functions/places`
   - Lascia `API_URL` com'è

2. **Production** (dopo deploy):
   - Modifica la riga:
     ```javascript
     const API_URL = 'https://YOUR-SITE.netlify.app/.netlify/functions/places';
     ```

#### Features

- Input per indirizzo
- Loading spinner
- Gestione errori
- Visualizzazione risultati categorizzati
- Design responsive
- Supporto tasto Enter

---

## 🛠 Setup Locale

### Prerequisiti

- Node.js 18+ ([nodejs.org](https://nodejs.org))
- npm (incluso con Node.js)
- Git ([git-scm.com](https://git-scm.com))

### Installazione

```bash
# 1. Clona il repository (se non l'hai già fatto)
cd documentscan

# 2. Installa le dipendenze
npm install

# 3. Installa Netlify CLI (globalmente)
npm install -g netlify-cli

# 4. Testa in locale
netlify dev
```

### Test Locale

Dopo aver avviato `netlify dev`:

1. Apri browser: `http://localhost:8888`
2. Apri il file HTML di test
3. Oppure testa direttamente l'endpoint:
   ```
   http://localhost:8888/.netlify/functions/places?address=Via+Sparano+Bari
   ```

### Test con curl

```bash
curl "http://localhost:8888/.netlify/functions/places?address=Via%20Sparano%20Bari"
```

---

## 🚀 Deploy su Netlify

### Opzione 1: Deploy tramite GitHub (CONSIGLIATO)

#### Step 1: Push su GitHub

```bash
# 1. Assicurati di essere nel branch corretto
git status

# 2. Aggiungi i nuovi file
git add netlify/
git add netlify.toml
git add package.json
git add test-restaurant-finder.html
git add RESTAURANT_FINDER_GUIDE.md

# 3. Commit
git commit -m "Add Restaurant Finder serverless function

- Add Netlify Functions setup
- Implement places.js with Nominatim and Overpass API
- Add restaurant categorization system
- Include test HTML page and documentation"

# 4. Push al branch remoto
git push -u origin claude/review-chatgpt-session-01TGf3WugMernsT2wpYAThZ7
```

#### Step 2: Setup Netlify

1. **Vai su [netlify.com](https://www.netlify.com)**
2. **Accedi** o crea un account (gratuito)
3. **Click "Add new site" → "Import an existing project"**
4. **Connetti GitHub**:
   - Autorizza Netlify ad accedere a GitHub
   - Seleziona il repository `documentscan`
5. **Configurazione Build**:
   ```
   Branch to deploy: claude/review-chatgpt-session-01TGf3WugMernsT2wpYAThZ7
   Build command: (lascia vuoto o "npm install")
   Publish directory: .
   Functions directory: netlify/functions
   ```
6. **Click "Deploy site"**

#### Step 3: Attendi il Deploy

- Il primo deploy richiede 1-3 minuti
- Netlify installerà automaticamente le dipendenze
- Una volta completato, riceverai un URL tipo: `https://random-name-123.netlify.app`

---

### Opzione 2: Deploy tramite Netlify CLI

```bash
# 1. Login a Netlify
netlify login

# 2. Inizializza il sito
netlify init

# 3. Deploy
netlify deploy --prod
```

---

## 🔗 Utilizzo dell'API

### Endpoint

```
GET /.netlify/functions/places?address=INDIRIZZO
```

### Parametri Query

| Parametro | Tipo   | Required | Descrizione                    |
|-----------|--------|----------|--------------------------------|
| address   | string | ✅ Sì    | Indirizzo da cercare          |

### Esempi di Request

**JavaScript (Fetch)**:
```javascript
const address = 'Via Sparano, Bari';
const url = `https://YOUR-SITE.netlify.app/.netlify/functions/places?address=${encodeURIComponent(address)}`;

const response = await fetch(url);
const data = await response.json();
console.log(data);
```

**curl**:
```bash
curl "https://YOUR-SITE.netlify.app/.netlify/functions/places?address=Via%20Sparano%20Bari"
```

**Python**:
```python
import requests
import urllib.parse

address = "Via Sparano, Bari"
url = f"https://YOUR-SITE.netlify.app/.netlify/functions/places?address={urllib.parse.quote(address)}"

response = requests.get(url)
data = response.json()
print(data)
```

### Response Format

```json
{
  "address": "Via Sparano, Bari",
  "geocoded_address": "Via Sparano, Bari, Puglia, Italia",
  "center": {
    "lat": 41.1177,
    "lon": 16.8719
  },
  "search_radius_meters": 1500,
  "total_found": 45,
  "categories": {
    "pasta": [...],
    "fish": [...],
    "meat": [...],
    "pizza": [...],
    "other": [...]
  },
  "pasta": [...],
  "fish": [...],
  "meat": [...],
  "pizza": [...],
  "other": [...]
}
```

### Error Response

```json
{
  "error": "Address not found",
  "timestamp": "2025-11-18T15:30:00.000Z"
}
```

### Status Codes

- `200` - Success
- `400` - Bad Request (parametro mancante)
- `404` - Address not found
- `500` - Internal Server Error
- `502` - External API error (Nominatim/Overpass)

---

## 🐛 Troubleshooting

### Problema: 404 - Function not found

**Sintomi**:
```json
{"error": "Function not found"}
```

**Soluzioni**:

1. **Verifica struttura cartelle**:
   ```bash
   ls -la netlify/functions/
   # Deve contenere places.js
   ```

2. **Verifica netlify.toml**:
   ```toml
   [functions]
     directory = "netlify/functions"
   ```

3. **Re-deploy**:
   ```bash
   git add netlify/
   git commit -m "Fix functions directory"
   git push
   ```

4. **Cancella cache Netlify**:
   - Dashboard Netlify → Site settings → Build & deploy → Clear cache and retry deploy

---

### Problema: Module not found 'node-fetch'

**Sintomi**:
```
Error: Cannot find module 'node-fetch'
```

**Soluzioni**:

1. **Verifica package.json esista**:
   ```bash
   ls -la package.json
   ```

2. **Verifica contenuto**:
   ```json
   {
     "type": "module",
     "dependencies": {
       "node-fetch": "^3.3.2"
     }
   }
   ```

3. **Re-install locale**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Commit e push**:
   ```bash
   git add package.json package-lock.json
   git commit -m "Fix dependencies"
   git push
   ```

---

### Problema: CORS Error

**Sintomi**:
```
Access to fetch blocked by CORS policy
```

**Soluzioni**:

1. **Verifica headers in places.js**:
   ```javascript
   const headers = {
     'Access-Control-Allow-Origin': '*',
     'Access-Control-Allow-Headers': 'Content-Type',
     'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
   };
   ```

2. **Testa con curl** invece del browser per verificare che la funzione funzioni:
   ```bash
   curl "https://YOUR-SITE.netlify.app/.netlify/functions/places?address=Bari"
   ```

---

### Problema: Address not found

**Sintomi**:
```json
{"error": "Address not found"}
```

**Cause**:
- Indirizzo troppo generico o errato
- Nominatim non ha trovato risultati

**Soluzioni**:

1. **Usa indirizzi più specifici**:
   - ❌ "Bari"
   - ✅ "Via Sparano, Bari, Italia"

2. **Prova prima su Nominatim direttamente**:
   ```
   https://nominatim.openstreetmap.org/search?q=Via+Sparano+Bari&format=json
   ```

---

### Problema: Overpass API timeout

**Sintomi**:
```json
{"error": "Overpass API error: 502"}
```

**Cause**:
- Overpass API sovraccarico
- Raggio di ricerca troppo grande
- Query troppo complessa

**Soluzioni**:

1. **Riduci il raggio** in `places.js`:
   ```javascript
   const SEARCH_RADIUS = 1000; // invece di 1500
   ```

2. **Riprova dopo qualche minuto**

3. **Usa server Overpass alternativi** (modifica in places.js):
   ```javascript
   const OVERPASS_URL = 'https://overpass.kumi.systems/api/interpreter';
   ```

---

### Problema: Nessun ristorante trovato

**Sintomi**:
- L'API risponde correttamente
- Ma tutte le categorie sono vuote

**Cause**:
- L'area cercata non ha molti dati su OpenStreetMap
- Tags OSM incompleti

**Soluzioni**:

1. **Aumenta il raggio**:
   ```javascript
   const SEARCH_RADIUS = 3000; // 3km
   ```

2. **Verifica dati su OpenStreetMap**:
   - Vai su [openstreetmap.org](https://www.openstreetmap.org)
   - Cerca l'area
   - Verifica che ci siano POI

3. **Contribuisci a OSM**:
   - Aggiungi i ristoranti mancanti su OpenStreetMap
   - Aspetta qualche ora perché Overpass si aggiorni

---

### Problema: Funzione lenta (>10 secondi)

**Cause**:
- Overpass query complessa
- Molti risultati da elaborare

**Soluzioni**:

1. **Riduci il raggio**:
   ```javascript
   const SEARCH_RADIUS = 1000;
   ```

2. **Limita risultati** per categoria (modifica in `categorizeRestaurants`):
   ```javascript
   .slice(0, 3) // Già implementato, aumenta se necessario
   ```

3. **Usa caching** (avanzato):
   - Implementa cache con Netlify Edge Functions
   - Oppure usa un database esterno (es: Redis)

---

## ⚠️ Limitazioni e Best Practices

### Rate Limits

#### Nominatim
- **Limite**: 1 request/secondo
- **Best Practice**:
  - Non fare richieste in parallelo
  - Usa User-Agent personalizzato
  - Considera caching dei risultati

#### Overpass API
- **Limite**: ~2 request/secondo (non ufficiale)
- **Timeout**: 25 secondi per query
- **Best Practice**:
  - Mantieni query semplici
  - Usa raggi ragionevoli (<3km)
  - Non fare richieste massicce

### Netlify Functions Limits (Free Tier)

- **Invocazioni**: 125.000/mese
- **Runtime**: 10 secondi max
- **Dimensione**: 50MB max

**Considerazioni**:
- Ogni ricerca = 1 invocazione
- ~4000 ricerche/giorno gratis
- Abbastanza per progetti piccoli/medi

### Miglioramenti Futuri

1. **Caching**:
   - Cache risultati per indirizzo (es: 1 ora)
   - Usa Netlify Blob Storage o Redis

2. **Paginazione**:
   - Restituisci solo N risultati per categoria
   - Aggiungi parametro `offset`

3. **Filtri Aggiuntivi**:
   - Distanza massima
   - Prezzo
   - Rating (se disponibili)

4. **Multiple Languages**:
   - Supporto per query in diverse lingue
   - Traduzione categorie

5. **Geolocation**:
   - Usa coordinate dirette invece di indirizzo
   - Risparmia una chiamata Nominatim

### Best Practices per Production

1. **Monitoring**:
   - Configura alert su Netlify
   - Monitora invocazioni mensili

2. **Error Tracking**:
   - Integra Sentry o simili
   - Log dettagliati

3. **Security**:
   - Aggiungi rate limiting
   - Valida input utente
   - Sanitizza output

4. **Performance**:
   - Implementa caching
   - Ottimizza query Overpass
   - Comprimi response (gzip)

---

## 📞 Supporto

### Risorse Utili

- [Netlify Functions Docs](https://docs.netlify.com/functions/overview/)
- [Nominatim API](https://nominatim.org/release-docs/develop/api/Overview/)
- [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/)

### Contatti

Per problemi specifici del codice, apri una issue nel repository GitHub.

---

## ✅ Checklist Deploy

- [ ] File `netlify/functions/places.js` creato
- [ ] File `netlify.toml` configurato
- [ ] File `package.json` con dipendenze
- [ ] Codice pushato su GitHub
- [ ] Account Netlify creato
- [ ] Repository connesso a Netlify
- [ ] Primo deploy completato con successo
- [ ] Funzione testata con curl o browser
- [ ] URL della funzione aggiunto al file HTML di test
- [ ] Test HTML funzionante

---

## 🎉 Fine

Il tuo backend serverless è pronto!

**URL finale**:
```
https://YOUR-SITE.netlify.app/.netlify/functions/places?address=INDIRIZZO
```

Buon coding! 🚀
