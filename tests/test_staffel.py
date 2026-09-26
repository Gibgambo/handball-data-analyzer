import pytest

import paths
from analyzer import HandballAnalyzer
from fake_nuliga import BASIS, LINK_REGIONALLIGA, LINK_VORRUNDE, FakeNuLiga, staffelseite
from staffel import NuLigaNichtErreichbarFehler, StaffelFehler, Staffelverwaltung, UngueltigerStaffelLink


@pytest.fixture
def nuliga():
    return FakeNuLiga({"431976": staffelseite("431976_frueh.html")})


def spielnummern():
    return sorted(str(n) for n in HandballAnalyzer().df_games["spielnummer"])


def test_ohne_staffelwechsel_ist_keine_staffel_geladen(nuliga):
    assert Staffelverwaltung(nuliga).geladene_staffel() is None


def test_erster_staffelwechsel_laedt_die_staffel(nuliga):
    verwaltung = Staffelverwaltung(nuliga)

    ergebnis = verwaltung.staffel_wechseln(LINK_VORRUNDE)

    assert sorted(ergebnis.neu) == ["7978832", "7978834", "7978847"]
    assert spielnummern() == ["107001", "107003", "107004"]
    staffel = verwaltung.geladene_staffel()
    assert staffel.staffel_link == LINK_VORRUNDE
    assert staffel.saison == "HVNB 2025/26"
    assert staffel.staffelname == "Verbandsliga Männer Ost"
    assert staffel.anzahl_spiele == 3
    assert staffel.anzahl_spieler > 0
    assert staffel.aktualisiert_am is not None


@pytest.mark.parametrize("link", [
    f"{BASIS}?displayTyp=gesamt&displayDetail=meetings&championship=HVNB+25%2F26&group=431976",
    f"{BASIS}?championship=HVNB+25%2F26&group=431976",
    f"{BASIS}?displayTyp=rueckrunde&displayDetail=table&championship=HVNB+25%2F26&group=431976",
    "hvnb-handball.liga.nu/cgi-bin/WebObjects/nuLigaHBDE.woa/wa/groupMeetingReport"
    "?meeting=7978847&championship=HVNB+25%2F26&group=431976",
])
def test_jede_ansicht_der_staffel_fuehrt_zum_gleichen_ergebnis(nuliga, link):
    Staffelverwaltung(nuliga).staffel_wechseln(link)

    assert spielnummern() == ["107001", "107003", "107004"]
    assert nuliga.abgerufene_seiten == [
        f"{BASIS}?displayTyp=gesamt&displayDetail=meetings&championship=HVNB+25%2F26&group=431976"
    ]


def test_basis_url_kommt_aus_dem_host_des_links(nuliga):
    link = ("https://bhv-handball.liga.nu/cgi-bin/WebObjects/nuLigaHBDE.woa/wa/groupPage"
            "?championship=HVNB+25%2F26&group=431976")

    Staffelverwaltung(nuliga).staffel_wechseln(link)

    abrufe = nuliga.abgerufene_seiten + nuliga.abgerufene_dokumente
    assert abrufe and all(url.startswith("https://bhv-handball.liga.nu/") for url in abrufe)


def test_andere_pdfs_der_staffelseite_werden_ignoriert(nuliga):
    Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)

    assert sorted(nuliga.abgerufene_spielberichte) == ["7978832", "7978834", "7978847"]
    assert len(nuliga.abgerufene_dokumente) == 3


@pytest.mark.parametrize("link", [
    "",
    "kein Link",
    "https://example.com/groupPage?championship=HVNB+25%2F26&group=431976",
    f"{BASIS}?championship=HVNB+25%2F26",
    f"{BASIS}?group=431976",
])
def test_ungueltiger_link_wird_abgelehnt_und_alte_staffel_bleibt(nuliga, link):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    vorher = verwaltung.geladene_staffel()

    with pytest.raises(UngueltigerStaffelLink):
        verwaltung.staffel_wechseln(link)

    assert verwaltung.geladene_staffel() == vorher
    assert spielnummern() == ["107001", "107003", "107004"]


def test_unbekannte_staffel_wird_abgelehnt(nuliga):
    with pytest.raises(UngueltigerStaffelLink):
        Staffelverwaltung(nuliga).staffel_wechseln(f"{BASIS}?championship=HVNB+25%2F26&group=1")

    assert Staffelverwaltung(nuliga).geladene_staffel() is None


def test_nicht_erreichbares_nuliga_laesst_alte_staffel_unveraendert(nuliga):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    vorher = verwaltung.geladene_staffel()
    nuliga.erreichbar = False

    with pytest.raises(NuLigaNichtErreichbarFehler):
        verwaltung.staffel_wechseln(LINK_REGIONALLIGA)

    assert verwaltung.geladene_staffel() == vorher
    assert spielnummern() == ["107001", "107003", "107004"]


def test_ohne_netzwerk_scheitert_auch_der_erste_staffelwechsel_sauber(nuliga):
    nuliga.erreichbar = False

    with pytest.raises(NuLigaNichtErreichbarFehler):
        Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)

    assert Staffelverwaltung(nuliga).geladene_staffel() is None


def test_geladene_staffel_uebersteht_neustart(nuliga):
    Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)
    vorher = Staffelverwaltung(nuliga).geladene_staffel()

    nach_neustart = Staffelverwaltung(FakeNuLiga()).geladene_staffel()

    assert nach_neustart == vorher
    assert nach_neustart.staffel_link == LINK_VORRUNDE


def test_staffel_ohne_spielberichte_ist_gueltig(nuliga):
    nuliga.seiten["431976"] = staffelseite("431976_leer.html")
    verwaltung = Staffelverwaltung(nuliga)

    ergebnis = verwaltung.staffel_wechseln(LINK_VORRUNDE)

    assert ergebnis.neu == []
    assert verwaltung.geladene_staffel().anzahl_spiele == 0
    assert verwaltung.geladene_staffel().anzahl_spieler == 0
    assert spielnummern() == []


# --- Aktualisieren ----------------------------------------------------------

def test_aktualisieren_laedt_nur_neue_spielberichte(nuliga):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    stand_vorher = verwaltung.geladene_staffel().aktualisiert_am
    nuliga.seiten["431976"] = staffelseite("431976_spaeter.html")
    nuliga.abgerufene_spielberichte.clear()

    ergebnis = Staffelverwaltung(nuliga).aktualisieren()

    assert sorted(ergebnis.neu) == ["7978758", "7978782"]
    assert sorted(nuliga.abgerufene_spielberichte) == ["7978758", "7978782"]
    assert spielnummern() == ["107001", "107002", "107003", "107004", "107005"]
    staffel = verwaltung.geladene_staffel()
    assert staffel.anzahl_spiele == 5
    assert staffel.aktualisiert_am >= stand_vorher
    assert staffel.staffel_link == LINK_VORRUNDE


def test_aktualisieren_ohne_neue_spielberichte_laedt_nichts(nuliga):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    nuliga.abgerufene_spielberichte.clear()

    ergebnis = verwaltung.aktualisieren()

    assert ergebnis.neu == []
    assert ergebnis.kurzmeldung() == "Keine neuen Spielberichte"
    assert nuliga.abgerufene_spielberichte == []
    assert spielnummern() == ["107001", "107003", "107004"]


def test_aktualisieren_bei_nicht_erreichbarem_nuliga_laesst_datenbestand_unveraendert(nuliga):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    vorher = verwaltung.geladene_staffel()
    nuliga.seiten["431976"] = staffelseite("431976_spaeter.html")
    nuliga.erreichbar = False

    with pytest.raises(NuLigaNichtErreichbarFehler):
        verwaltung.aktualisieren()

    assert verwaltung.geladene_staffel() == vorher
    assert spielnummern() == ["107001", "107003", "107004"]


def test_aktualisieren_ohne_geladene_staffel_wird_abgelehnt(nuliga):
    with pytest.raises(StaffelFehler):
        Staffelverwaltung(nuliga).aktualisieren()


def test_aktualisieren_erzeugt_keine_exporte(nuliga):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    verwaltung.aktualisieren()

    assert not any(paths.analysis_dir().iterdir())
    assert not any(paths.visualizations_dir().iterdir())


# --- Staffelwechsel bei geladener Staffel ------------------------------------

def test_staffelwechsel_verwirft_alte_staffel_vollstaendig(nuliga):
    nuliga.seiten["432326"] = staffelseite("432326_gesamt.html")
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    (paths.analysis_dir() / "top_scorer.csv").write_text("alt")
    (paths.visualizations_dir() / "top_scorer.png").write_bytes(b"alt")

    verwaltung.staffel_wechseln(LINK_REGIONALLIGA)

    assert spielnummern() == ["101001", "101002"]
    assert sorted(p.name for p in paths.raw_dir().iterdir()) == ["7977978.pdf", "7978021.pdf"]
    assert not any(paths.analysis_dir().iterdir())
    assert not any(paths.visualizations_dir().iterdir())
    staffel = verwaltung.geladene_staffel()
    assert staffel.staffel_link == LINK_REGIONALLIGA
    assert staffel.staffelname == "Solarservice Norddeutschland Handball-Regionalliga M"
    assert staffel.anzahl_spiele == 2


def test_staffelwechsel_auf_denselben_link_laedt_alles_neu(nuliga):
    verwaltung = Staffelverwaltung(nuliga)
    verwaltung.staffel_wechseln(LINK_VORRUNDE)
    nuliga.abgerufene_spielberichte.clear()

    ergebnis = verwaltung.staffel_wechseln(LINK_VORRUNDE)

    assert sorted(ergebnis.neu) == ["7978832", "7978834", "7978847"]
    assert sorted(nuliga.abgerufene_spielberichte) == ["7978832", "7978834", "7978847"]
    assert spielnummern() == ["107001", "107003", "107004"]


# --- Übersprungene Spielberichte und Spielberichte mit Warnung ---------------

@pytest.fixture
def nuliga_mit_problemfaellen():
    return FakeNuLiga({"431976": staffelseite("431976_problemfaelle.html")})


def test_problemfaelle_brechen_den_import_nicht_ab(nuliga_mit_problemfaellen):
    verwaltung = Staffelverwaltung(nuliga_mit_problemfaellen)

    ergebnis = verwaltung.staffel_wechseln(LINK_VORRUNDE)

    uebersprungen = {u.kennung: u.grund for u in ergebnis.uebersprungen}
    assert set(uebersprungen) == {"9900001", "9900003"}
    assert "nicht lesbar" in uebersprungen["9900001"]
    assert "Endstand" in uebersprungen["9900003"]
    assert [(w.kennung, w.spielnummer, w.fehlend) for w in ergebnis.mit_warnung] == [
        ("9900002", "999002", ["Spielverlauf"])
    ]
    # Übersprungene fließen in keine Auswertung ein, solche mit Warnung schon
    assert spielnummern() == ["107001", "107003", "999002"]
    assert verwaltung.geladene_staffel().anzahl_spiele == 3
    assert ergebnis.kurzmeldung() == "5 neue Spielberichte, 1 mit Warnung, 2 übersprungen"


def test_details_des_letzten_imports_ueberstehen_neustart(nuliga_mit_problemfaellen):
    ergebnis = Staffelverwaltung(nuliga_mit_problemfaellen).staffel_wechseln(LINK_VORRUNDE)

    letzter_import = Staffelverwaltung(FakeNuLiga()).geladene_staffel().letzter_import

    assert letzter_import == ergebnis


def test_problemfaelle_werden_auch_beim_aktualisieren_gemeldet(nuliga, nuliga_mit_problemfaellen):
    Staffelverwaltung(nuliga).staffel_wechseln(LINK_VORRUNDE)

    ergebnis = Staffelverwaltung(nuliga_mit_problemfaellen).aktualisieren()

    assert sorted(ergebnis.neu) == ["9900001", "9900002", "9900003"]
    assert {u.kennung for u in ergebnis.uebersprungen} == {"9900001", "9900003"}
    assert [w.kennung for w in ergebnis.mit_warnung] == ["9900002"]
    assert spielnummern() == ["107001", "107003", "107004", "999002"]


def test_nicht_abrufbarer_spielbericht_wird_uebersprungen_und_spaeter_erneut_versucht(nuliga):
    nuliga.seiten["431976"] = staffelseite("431976_frueh.html").replace("meeting=7978834", "meeting=9999999")
    verwaltung = Staffelverwaltung(nuliga)

    ergebnis = verwaltung.staffel_wechseln(LINK_VORRUNDE)

    assert [u.kennung for u in ergebnis.uebersprungen] == ["9999999"]
    assert "nicht abrufbar" in ergebnis.uebersprungen[0].grund
    assert spielnummern() == ["107001", "107003"]
    nuliga.abgerufene_spielberichte.clear()

    verwaltung.aktualisieren()

    assert nuliga.abgerufene_spielberichte == ["9999999"]
