# 🤾 Handball Analytics Pipeline

Vollständige Datenanalyse-Pipeline für Handball-Spielberichte (PDF) mit interaktivem Dashboard.

## 📁 Projektstruktur

```
handball-analytics/
├── data/
│   ├── raw/              # PDF-Dateien hier ablegen
│   ├── processed/        # Extrahierte CSVs
│   ├── analysis/         # Analyseergebnisse
│   └── visualizations/   # Generierte Plots
├── src/
|   |── scraper.py        # PDF Extraktion von Nuliga
│   ├── pdf_parser.py     # PDF → CSV Extraktion
│   ├── analyzer.py       # Datenanalyse
│   ├── visualizer.py     # Visualisierungen
│   └── dashboard.py      # Streamlit Dashboard
├── requirements.txt
└── README.md
```

## 🚀 Installation

### 1. Repository klonen oder herunterladen

### 2. Virtual Environment erstellen (empfohlen)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 4. Ordnerstruktur erstellen
```bash
mkdir -p data/raw data/processed data/analysis data/visualizations
```

## 📊 Verwendung

### Schritt 1: PDF-Dateien extrahieren
Handball-Spielbericht-PDFs mit dem scraper von der Nuliga Seite holen.

```bash
python src/scraper.py
```

### Schritt 2: CSV-Dateien extrahieren
```bash
python src/pdf_parser.py
```

**Output:**
- `data/processed/spiele.csv` - Spielinformationen
- `data/processed/spieler_statistiken.csv` - Spielerstatistiken
- `data/processed/spielereignisse.csv` - Chronologischer Spielverlauf

### Schritt 3: Daten analysieren
```bash
python src/analyzer.py
```

**Output:**
- `data/analysis/top_scorer.csv`
- `data/analysis/team_statistics.csv`
- `data/analysis/home_advantage.csv`
- `data/analysis/goals_by_minute.csv`
- `data/analysis/penalty_statistics.csv`
- `data/analysis/7m_efficiency.csv`
- `data/analysis/game_tempo.csv`

### Schritt 4: Visualisierungen erstellen
```bash
python src/visualizer.py
```

**Output:** PNG-Dateien in `data/visualizations/`

### Schritt 5: Dashboard starten
```bash
streamlit run src/dashboard.py
```

**Öffnet automatisch:** `http://localhost:8501`

## 📝 Datenformat

### PDF-Anforderungen
Die Pipeline ist optimiert für HVNB (Handballverband Niedersachsen-Bremen) Spielberichte mit:
- Spielnummer, Datum, Teams
- Spielerstatistiken (Trikot, Name, Tore)
- Spielverlauf mit Zeitstempeln
- 2-Minuten-Strafen
- 7-Meter-Versuche

### CSV-Struktur

**spiele.csv:**
```
spielnummer, datum, heimmannschaft, gastmannschaft, endstand_heim, endstand_gast, ...
```

**spieler_statistiken.csv:**
```
pdf_file, spielnummer, trikotnummer, name, tore, team
```

**spielereignisse.csv:**
```
pdf_file, spielnummer, team, zeit, stand_heim, stand_gast, ereignis, spieler
```

## 📚 Verwendete Libraries

| Library | Zweck | Dokumentation |
|---------|-------|---------------|
| pdfplumber | PDF-Extraktion | [Docs](https://github.com/jsvine/pdfplumber) |
| pandas | Datenverarbeitung | [Docs](https://pandas.pydata.org) |
| matplotlib | Basis-Visualisierung | [Docs](https://matplotlib.org) |
| seaborn | Statistische Plots | [Docs](https://seaborn.pydata.org) |
| streamlit | Dashboard-Framework | [Docs](https://streamlit.io) |

## 📄 Lizenz

MIT License - Frei verwendbar für persönliche und kommerzielle Projekte.

## ⭐ Credits

Entwickelt für die Analyse von HVNB Handball-Spielberichten.

---

**Happy Analyzing! 🤾‍♂️📊**