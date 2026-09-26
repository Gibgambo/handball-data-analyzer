import pytest

import kommandozeile
from fake_nuliga import LINK_VORRUNDE, FakeNuLiga, staffelseite
from staffel import Staffelverwaltung


@pytest.fixture
def verwaltung():
    return Staffelverwaltung(FakeNuLiga({"431976": staffelseite("431976_frueh.html")}))


def test_mit_staffel_link_wird_die_staffel_geladen(verwaltung, capsys):
    assert kommandozeile.main([LINK_VORRUNDE], verwaltung) == 0

    staffel = verwaltung.geladene_staffel()
    assert staffel.staffel_link == LINK_VORRUNDE
    assert staffel.anzahl_spiele == 3
    ausgabe = capsys.readouterr().out
    assert "3 neue Spielberichte" in ausgabe
    assert "HVNB 2025/26" in ausgabe


def test_ohne_staffel_link_wird_die_geladene_staffel_aktualisiert(verwaltung, capsys):
    kommandozeile.main([LINK_VORRUNDE], verwaltung)
    capsys.readouterr()

    assert kommandozeile.main([], verwaltung) == 0

    assert "Keine neuen Spielberichte" in capsys.readouterr().out


def test_aktualisieren_ohne_geladene_staffel_scheitert(verwaltung, capsys):
    assert kommandozeile.main([], verwaltung) == 1

    assert "noch keine Staffel geladen" in capsys.readouterr().err


def test_ungueltiger_staffel_link_wird_gemeldet(verwaltung, capsys):
    assert kommandozeile.main(["https://example.com/staffel"], verwaltung) == 1

    assert "kein nuLiga-Link" in capsys.readouterr().err
    assert verwaltung.geladene_staffel() is None


def test_problemfaelle_werden_mit_grund_aufgelistet(capsys):
    verwaltung = Staffelverwaltung(FakeNuLiga({"431976": staffelseite("431976_problemfaelle.html")}))

    assert kommandozeile.main([LINK_VORRUNDE], verwaltung) == 0

    ausgabe = capsys.readouterr().out
    assert "9900001" in ausgabe and "nicht lesbar" in ausgabe
    assert "9900003" in ausgabe and "Endstand" in ausgabe
    assert "9900002 (Spiel 999002): es fehlt Spielverlauf" in ausgabe


def test_staffelwechsel_bei_geladener_staffel_braucht_verwerfen(verwaltung, capsys):
    kommandozeile.main([LINK_VORRUNDE], verwaltung)
    stand = verwaltung.geladene_staffel().aktualisiert_am
    capsys.readouterr()

    assert kommandozeile.main([LINK_VORRUNDE], verwaltung) == 1

    assert "--verwerfen" in capsys.readouterr().err
    assert verwaltung.geladene_staffel().aktualisiert_am == stand


def test_staffelwechsel_mit_verwerfen_laedt_die_staffel_neu(verwaltung, capsys):
    kommandozeile.main([LINK_VORRUNDE], verwaltung)

    assert kommandozeile.main([LINK_VORRUNDE, "--verwerfen"], verwaltung) == 0

    assert "3 neue Spielberichte" in capsys.readouterr().out
