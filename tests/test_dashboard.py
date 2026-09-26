from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import paths

DASHBOARD = str(Path(__file__).resolve().parent.parent / "src" / "dashboard.py")


def test_dashboard_without_data_shows_hint(monkeypatch, tmp_path):
    monkeypatch.setenv(paths.DATA_DIR_ENV, str(tmp_path))
    app = AppTest.from_file(DASHBOARD, default_timeout=30).run()
    assert not app.exception
    assert any("Noch keine Daten" in info.value for info in app.info)


@pytest.mark.skipif(not paths.has_processed_data(), reason="keine lokalen Daten vorhanden")
def test_dashboard_with_data_shows_overview(monkeypatch):
    monkeypatch.delenv(paths.DATA_DIR_ENV, raising=False)
    app = AppTest.from_file(DASHBOARD, default_timeout=60).run()
    assert not app.exception
    assert app.title[0].value == "🤾 Handball Analytics Dashboard"
    assert len(app.metric) >= 4
