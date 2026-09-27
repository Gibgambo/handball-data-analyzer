from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import staffel
from fake_nuliga import LINK_REGIONALLIGA, LINK_VORRUNDE, FakeNuLiga, staffelseite

DASHBOARD = str(Path(__file__).resolve().parent.parent / "src" / "dashboard.py")


@pytest.fixture
def nuliga(monkeypatch):
    fake = FakeNuLiga({"431976": staffelseite("431976_frueh.html")})
    monkeypatch.setattr(staffel, "HttpNuLiga", lambda: fake)
    return fake


def starten():
    return AppTest.from_file(DASHBOARD, default_timeout=60).run()


def texte(elemente):
    return " ".join(e.value for e in elemente)


def test_ohne_staffel_zeigt_das_dashboard_nur_den_begruessungszustand(nuliga):
    app = starten()

    assert not app.exception
    assert "Noch keine Staffel geladen" in texte(app.info)
    assert len(app.text_input) == 1
    assert len(app.sidebar.radio) == 0


def test_staffel_laden_aus_dem_begruessungszustand(nuliga):
    app = starten()

    app.text_input[0].input(LINK_VORRUNDE).run()
    app.button[0].click().run()

    assert not app.exception
    assert app.title[0].value == "🤾 Verbandsliga Männer Ost"
    assert "HVNB 2025/26 · Stand:" in texte(app.caption)
    sidebar = texte(app.sidebar.info)
    assert "Geladene Staffel" in sidebar
    assert "HVNB 2025/26" in sidebar and "Verbandsliga Männer Ost" in sidebar
    assert "3 Spiele" in sidebar
    assert "3 neue Spielberichte" in texte(app.sidebar.success)


def test_ungueltiger_link_zeigt_meldung(nuliga):
    app = starten()

    app.text_input[0].input("https://example.com/").run()
    app.button[0].click().run()

    assert not app.exception
    assert "kein Staffel-Link" in texte(app.error)
    assert staffel.Staffelverwaltung(nuliga).geladene_staffel() is None


def test_aktualisieren_zeigt_neue_zahlen_ohne_neustart(nuliga):
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)
    app = starten()
    assert "3 Spiele" in texte(app.sidebar.info)
    nuliga.seiten["431976"] = staffelseite("431976_spaeter.html")

    app.sidebar.button[0].click().run()

    assert not app.exception
    assert "5 Spiele" in texte(app.sidebar.info)
    assert "2 neue Spielberichte" in texte(app.sidebar.success)
    assert app.metric[0].value == "5"


@pytest.mark.parametrize("seite", ["📊 Übersicht", "🏆 Top Spieler", "🟨 Strafen", "🏠 Heimvorteil", "⚽ Spielverlauf",
                                   "🎯 7-Meter Analyse", "📈 Team-Vergleich", "⏱️ Zeitanalyse",
                                   "📋 Alle Statistiken"])
def test_analyseseiten_mit_geladener_staffel(nuliga, seite):
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)
    app = starten()

    app.sidebar.radio[0].set_value(seite).run()

    assert not app.exception


def test_uebersicht_nummeriert_ranglisten_ab_platz_eins(nuliga):
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)

    app = starten()

    assert not app.exception
    torschuetzen = [m.value for m in app.markdown if m.value.endswith("Tore")]
    plaetze = [int(t.split(".**")[0].lstrip("*")) for t in torschuetzen]
    assert plaetze[0] == 1
    assert plaetze == sorted(plaetze)


def test_strafen_haben_eine_eigene_seite(nuliga):
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)
    app = starten()

    app.sidebar.radio[0].set_value("🏆 Top Spieler").run()
    assert not any("Strafen" in s.value or "Disqualifikationen" in s.value for s in app.subheader)

    app.sidebar.radio[0].set_value("🟨 Strafen").run()
    assert not app.exception
    assert [s.value for s in app.subheader] == ["🟨 Strafen-Statistik", "🔴 Disqualifikationen"]


def test_staffel_ohne_spiele_zeigt_hinweis_statt_diagrammen(nuliga):
    nuliga.seiten["431976"] = staffelseite("431976_leer.html")
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)

    app = starten()

    assert not app.exception
    assert "Noch keine Spielberichte vorhanden" in texte(app.info)
    assert "0 Spiele" in texte(app.sidebar.info)


def test_daten_verwalten_zeigt_details_des_letzten_imports(nuliga):
    nuliga.seiten["431976"] = staffelseite("431976_problemfaelle.html")
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)
    app = starten()

    app.sidebar.radio[0].set_value("⚙️ Daten verwalten").run()

    assert not app.exception
    uebersprungen, mit_warnung = app.dataframe[0].value, app.dataframe[1].value
    assert sorted(uebersprungen["nuLiga-ID"]) == ["9900001", "9900003"]
    assert list(mit_warnung["Spielnummer"]) == ["999002"]


def test_staffelwechsel_erst_nach_bestaetigung(nuliga):
    nuliga.seiten["432326"] = staffelseite("432326_gesamt.html")
    staffel.Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)
    app = starten()
    app.sidebar.radio[0].set_value("⚙️ Daten verwalten").run()

    app.text_input[0].input(LINK_REGIONALLIGA).run()
    wechseln = next(b for b in app.button if b.label == "Staffel wechseln")
    assert wechseln.disabled

    app.checkbox[0].check().run()
    next(b for b in app.button if b.label == "Staffel wechseln").click().run()

    assert not app.exception
    assert "Regionalliga" in texte(app.sidebar.info)
    assert "2 Spiele" in texte(app.sidebar.info)
