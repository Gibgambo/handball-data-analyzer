# 🤾 Handball Analytics Pipeline

Analysiert die Spielberichte einer Handball-Staffel aus nuLiga und stellt sie in einem interaktiven Dashboard dar.

## 📁 Projektstruktur

```
handball-data-analyzer/
├── data/                   # nicht versioniert, wird automatisch angelegt
│   ├── staffel.json        # Geladene Staffel: Staffel-Link, Stand, letzter Import
│   ├── raw/                # Spielberichte (PDF) der Geladenen Staffel
│   ├── processed/          # Extrahierte CSVs
│   ├── analysis/           # Exportierte Analyseergebnisse
│   └── visualizations/     # Generierte Plots
├── src/
│   ├── dashboard.py        # Streamlit Dashboard (Einstiegspunkt)
│   ├── staffel.py          # Staffel laden, Aktualisieren, Staffelwechsel
│   ├── nuliga.py           # Zugriff auf nuLiga
│   ├── pdf_parser.py       # Spielbericht (PDF) → CSV
│   ├── analyzer.py         # Datenanalyse
│   ├── visualizer.py       # Visualisierungen
│   ├── paths.py            # Zentrale Datenpfade
│   └── scraper.py          # Kommandozeile: Staffel laden / Aktualisieren
├── tests/                  # pytest, ohne Netzwerk (Fake-nuLiga + Fixtures)
├── requirements.txt
├── requirements-dev.txt
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

Für die Tests zusätzlich:
```bash
pip install -r requirements-dev.txt
```

### 4. Datenverzeichnis
Das Datenverzeichnis `data/` wird nicht im Repository versioniert und bei Bedarf automatisch angelegt
(relativ zum Projekt, unabhängig vom Arbeitsverzeichnis, siehe `src/paths.py`).

Über die Umgebungsvariable `HANDBALL_DATA_DIR` lässt sich ein anderes Datenverzeichnis verwenden.

## 📊 Verwendung

Alles läuft über das Dashboard – Skripte müssen nicht mehr einzeln ausgeführt werden.

### Dashboard starten
```bash
streamlit run src/dashboard.py
```

**Öffnet automatisch:** `http://localhost:8501`

### Staffel laden
Beim ersten Start ist noch keine Staffel geladen. Füge einen **Staffel-Link** aus nuLiga ein und klicke
auf **„Staffel laden“**. Welche Ansicht der Link zeigt (Tabelle, Spielplan, Vorrunde, Rückrunde …), ist egal:
Die App lädt immer alle Spielberichte der Staffel (Vorrunde und Rückrunde) und wertet sie aus.

Das Dashboard zeigt immer genau eine Staffel, die **Geladene Staffel**. Saison, Staffel, Stand sowie Anzahl
der Spiele und Spieler stehen in der Sidebar.

### Aktualisieren
Im Laufe der Saison erscheinen neue Spielberichte. **„🔄 Aktualisieren“** in der Sidebar ergänzt die
Geladene Staffel um neu erschienene Spielberichte; bereits vorhandene werden nicht erneut geladen.

### Staffelwechsel
Auf der Seite **„⚙️ Daten verwalten“** lässt sich unter „Staffel wechseln“ ein neuer Staffel-Link setzen.
Dabei werden alle Daten der bisherigen Staffel verworfen (Spielberichte, Auswertungen, Exporte) und die
neue Staffel vollständig geladen. Mit demselben Link lässt sich die Staffel auch komplett neu laden,
z. B. nachdem der Verband einen Spielbericht korrigiert hat.

### Import-Meldungen
Nach jedem Import zeigt die Sidebar eine Kurzmeldung; Details stehen unter **„⚙️ Daten verwalten“**:
- **Übersprungene Spielberichte** – Spieldaten (Spielnummer, Datum, Mannschaften, Endstand) waren nicht
  vollständig lesbar; sie fließen in keine Auswertung ein.
- **Spielberichte mit Warnung** – Spielerstatistiken oder Spielverlauf fehlen; das Spiel zählt für
  Ergebnis-Auswertungen, Torschützen- und Spielverlaufs-Auswertungen haben dort Lücken.

### Ohne Dashboard (Kommandozeile)
Staffel laden und Aktualisieren gehen auch ohne Dashboard:
```bash
python src/scraper.py                                  # Aktualisieren der geladenen Staffel
python src/scraper.py "<Staffel-Link>"                 # erste Staffel laden
python src/scraper.py "<Staffel-Link>" --verwerfen     # Staffelwechsel (verwirft alle bisherigen Daten)
```
Für einen regelmäßigen Abruf (z. B. per Aufgabenplanung) den Aufruf ohne Staffel-Link verwenden.
Übersprungene Spielberichte und Spielberichte mit Warnung werden direkt aufgelistet.

### Analysen exportieren
Auf der Seite **„📋 Alle Statistiken“** lassen sich einzelne Analysen als CSV herunterladen oder alle
nach `data/analysis/` speichern.

### Tests ausführen
```bash
pytest
```

## 📝 Datenformat

### Anforderungen an Spielberichte
Die Auswertung ist optimiert für Spielberichte des HVNB (Handballverband Niedersachsen-Bremen) mit:
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