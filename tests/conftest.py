import sys
from pathlib import Path

import pytest

# Die Module in src/ importieren sich gegenseitig ohne Paketpräfix
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import paths  # noqa: E402  (erst nach der sys.path-Einrichtung importierbar)


@pytest.fixture(autouse=True)
def datenverzeichnis(monkeypatch, tmp_path):
    """Jeder Test arbeitet in einem eigenen, leeren Datenverzeichnis."""
    monkeypatch.setenv(paths.DATA_DIR_ENV, str(tmp_path / "data"))
