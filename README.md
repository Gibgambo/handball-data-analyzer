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
Platziere deine Handball-Spielbericht-PDFs in `data/raw/` und führe aus:

```bash
python src/pdf_parser.py
```

**Output:**
- `data/processed/spiele.csv` - Spielinformationen
- `data/processed/spieler_statistiken.csv` - Spielerstatistiken
- `data/processed/spielereignisse.csv` - Chronologischer Spielverlauf

### Schritt 2: Daten analysieren
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

### Schritt 3: Visualisierungen erstellen
```bash
python src/visualizer.py
```

**Output:** PNG-Dateien in `data/visualizations/`

### Schritt 4: Dashboard starten
```bash
streamlit run src/dashboard.py
```

**Öffnet automatisch:** `http://localhost:8501`

## 📈 Dashboard-Features

### 📊 Übersicht
- Key Performance Indicators
- Top 10 Torschützen
- Team-Übersicht
- Heimvorteil auf einen Blick

### 🏆 Top Spieler
- Top N Torschützen (konfigurierbar)
- Detaillierte Spielerliste
- Strafen-Statistik
- CSV-Export

### 🏠 Heimvorteil
- Heim- vs. Auswärts-Siegquote
- Durchschnittliche Tore
- Pie Chart & Bar Chart Visualisierung

### ⚽ Spielverlauf
- Auswahl eines spezifischen Spiels
- Tor-Timeline (Line Plot)
- Ereignis-Tabelle mit allen Details

### 🎯 7-Meter Analyse
- Gesamtstatistik
- Top 10 Schützen
- Verwandlungsquoten
- Farbcodierte Effizienz-Tabelle

### 📈 Team-Vergleich
- Direktvergleich zweier Teams
- Siegquoten, Tore, Tordifferenz
- 4-Panel Visualisierung
- Ranking-Tabelle

### ⏱️ Zeitanalyse
- Heatmap: Tore nach Spielminuten
- 1. vs. 2. Halbzeit Vergleich
- Spieltempo-Analyse

## 🔧 Erweiterte Konfiguration

### Analyzer anpassen
In `analyzer.py` kannst du folgende Parameter ändern:

```python
analyzer = HandballAnalyzer(data_dir="../data/processed")
top_scorer = analyzer.get_top_scorer(top_n=20)  # Anzahl ändern
```

### Visualisierungen anpassen
In `visualizer.py`:

```python
plt.style.use('seaborn-v0_8-darkgrid')  # Anderen Style wählen
sns.set_palette("husl")  # Farbpalette ändern
```

### Dashboard-Styling
In `dashboard.py` im CSS-Block anpassen:

```python
st.markdown("""
    <style>
    /* Dein Custom CSS */
    </style>
""", unsafe_allow_html=True)
```

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

## 🐛 Troubleshooting

### Problem: "FileNotFoundError"
**Lösung:** Stelle sicher, dass PDFs in `data/raw/` liegen und die Ordnerstruktur existiert.

### Problem: "No module named 'pdfplumber'"
**Lösung:** `pip install -r requirements.txt` ausführen

### Problem: Dashboard startet nicht
**Lösung:** Prüfe ob Port 8501 frei ist oder verwende `streamlit run dashboard.py --server.port 8502`

### Problem: Keine Daten im Dashboard
**Lösung:** 
1. Erst `pdf_parser.py` ausführen
2. Dann `analyzer.py` ausführen
3. Dashboard starten

### Problem: "KeyError" in analyzer.py
**Lösung:** PDF-Struktur weicht ab. Prüfe ob alle erwarteten Felder vorhanden sind.

### Problem: Encoding-Fehler bei deutschen Umlauten
**Lösung:** CSVs verwenden `utf-8-sig` - sollte automatisch funktionieren.

## 🎨 Alternativen zu Streamlit

### Dash (Plotly)
```bash
pip install dash plotly
```
**Vorteile:** Mehr Kontrolle, professionelleres Design, bessere für große Dashboards
**Nachteile:** Steilere Lernkurve

### Gradio
```bash
pip install gradio
```
**Vorteile:** Noch einfacher als Streamlit, ideal für ML-Demos
**Nachteile:** Weniger Layoutoptionen

### Panel (HoloViz)
```bash
pip install panel
```
**Vorteile:** Sehr flexibel, gut mit Jupyter Notebooks
**Nachteile:** Kleinere Community

**Empfehlung:** Streamlit ist ideal für dieses Projekt - schnelle Entwicklung, gute Community, ausreichende Features.

## 📊 Beispiel-Analysen

### 1. Bester Torschütze finden
```python
from analyzer import HandballAnalyzer

analyzer = HandballAnalyzer()
top_scorer = analyzer.get_top_scorer(top_n=1)
print(f"Bester Torschütze: {top_scorer.iloc[0]['name']} mit {top_scorer.iloc[0]['tore']} Toren")
```

### 2. Heimvorteil berechnen
```python
home_stats = analyzer.get_home_advantage()
print(f"Heimvorteil: {home_stats['heim_siegquote'] - home_stats['auswaerts_siegquote']:.1f}%")
```

### 3. Spielverlauf visualisieren
```python
from visualizer import HandballVisualizer

visualizer = HandballVisualizer(analyzer)
visualizer.plot_game_timeline(spielnummer=107009)
```

### 4. Alle Analysen auf einmal
```python
# Alles automatisch
analyzer.save_analysis_results()
visualizer.create_all_visualizations()
```

## 🔬 Erweiterte Analysen (Ideas)

Mögliche Erweiterungen für die Pipeline:

1. **Spieler-Formkurve**: Tore über Zeit pro Spieler
2. **Head-to-Head**: Direkte Duelle zwischen Teams
3. **Vorhersagemodell**: ML für Spielausgänge
4. **Live-Updates**: Automatisches Einlesen neuer PDFs
5. **Export-Funktion**: Berichte als PDF generieren
6. **Vergleich mit Vorjahren**: Saisonvergleiche
7. **Positionsanalyse**: Wenn Positionen in PDFs vorhanden
8. **Torhüter-Statistik**: Paraden, Gegentorquote

## 📚 Verwendete Libraries

| Library | Zweck | Dokumentation |
|---------|-------|---------------|
| pdfplumber | PDF-Extraktion | [Docs](https://github.com/jsvine/pdfplumber) |
| pandas | Datenverarbeitung | [Docs](https://pandas.pydata.org) |
| matplotlib | Basis-Visualisierung | [Docs](https://matplotlib.org) |
| seaborn | Statistische Plots | [Docs](https://seaborn.pydata.org) |
| streamlit | Dashboard-Framework | [Docs](https://streamlit.io) |

## 🤝 Beitragen

Verbesserungsvorschläge sind willkommen!

1. Feature-Ideen als Issue erstellen
2. Code verbessern und Pull Request erstellen
3. Bugs melden mit Beispiel-PDF

## 📄 Lizenz

MIT License - Frei verwendbar für persönliche und kommerzielle Projekte.

## ⭐ Credits

Entwickelt für die Analyse von HVNB Handball-Spielberichten.

---

**Happy Analyzing! 🤾‍♂️📊**