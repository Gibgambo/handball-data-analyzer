"""Zentrale Stelle für alle Datenpfade.

Pfade werden relativ zum Projekt aufgelöst, nicht zum Arbeitsverzeichnis.
Das Datenverzeichnis lässt sich über die Umgebungsvariable HANDBALL_DATA_DIR
umkonfigurieren (z. B. auf einen temporären Ordner in Tests).
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR_ENV = "HANDBALL_DATA_DIR"

PROCESSED_FILES = ("spiele.csv", "spieler_statistiken.csv", "spielereignisse.csv")


def data_dir():
    """Wurzel des Datenverzeichnisses (relative Angaben gelten ab Projekt-Root)."""
    return PROJECT_ROOT / os.environ.get(DATA_DIR_ENV, "data")


def _sub_dir(name):
    directory = data_dir() / name
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def raw_dir():
    """Heruntergeladene Spielberichte (PDF)."""
    return _sub_dir("raw")


def processed_dir():
    """Aus den Spielberichten extrahierte CSVs."""
    return _sub_dir("processed")


def analysis_dir():
    """Exportierte Analyseergebnisse (CSV)."""
    return _sub_dir("analysis")


def visualizations_dir():
    """Generierte Plots (PNG)."""
    return _sub_dir("visualizations")


def has_processed_data():
    """True, wenn alle extrahierten CSVs vorliegen."""
    directory = data_dir() / "processed"
    return all((directory / name).is_file() for name in PROCESSED_FILES)
