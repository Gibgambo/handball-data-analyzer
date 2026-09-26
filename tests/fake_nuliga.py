"""Fake für den nuLiga-Adapter: liefert gespeicherte Staffelseiten und Spielberichte."""
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from nuliga import NuLigaNichtErreichbar, NuLigaSeiteNichtGefunden

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "nuliga"

BASIS = "https://hvnb-handball.liga.nu/cgi-bin/WebObjects/nuLigaHBDE.woa/wa/groupPage"
LINK_VORRUNDE = f"{BASIS}?displayTyp=vorrunde&displayDetail=meetings&championship=HVNB+25%2F26&group=431976"
LINK_REGIONALLIGA = f"{BASIS}?displayTyp=gesamt&displayDetail=meetings&championship=HVNB+25%2F26&group=432326"


def staffelseite(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeNuLiga:
    """Beantwortet Abrufe aus Fixtures und protokolliert sie.

    `seiten` bildet die Staffel (nuLiga-Parameter `group`) auf den HTML-Text ihrer Staffelseite ab.
    Die Staffelseite gibt es nur in der Ansicht `displayTyp=gesamt`, wie in der Spezifikation gefordert.
    """

    def __init__(self, seiten=None):
        self.seiten = dict(seiten or {})
        self.erreichbar = True
        self.abgerufene_seiten = []
        self.abgerufene_spielberichte = []
        self.abgerufene_dokumente = []

    def staffelseite_abrufen(self, url):
        self._pruefe_erreichbar()
        self.abgerufene_seiten.append(url)
        query = parse_qs(urlparse(url).query)
        group = query.get("group", [None])[0]
        if query.get("displayTyp") != ["gesamt"] or query.get("displayDetail") != ["meetings"]:
            raise AssertionError(f"Staffelseite nicht in der Gesamtansicht abgefragt: {url}")
        if group not in self.seiten:
            raise NuLigaSeiteNichtGefunden(url)
        return self.seiten[group]

    def dokument_abrufen(self, url):
        self._pruefe_erreichbar()
        self.abgerufene_dokumente.append(url)
        query = parse_qs(urlparse(url).query)
        meeting = query.get("meeting", [None])[0]
        if query.get("dokument") == ["meetingReportHB"]:
            self.abgerufene_spielberichte.append(meeting)
        pfad = FIXTURES / "spielberichte" / f"{meeting}.pdf"
        if not pfad.is_file():
            raise NuLigaSeiteNichtGefunden(url)
        return pfad.read_bytes()

    def _pruefe_erreichbar(self):
        if not self.erreichbar:
            raise NuLigaNichtErreichbar("Verbindung abgelehnt")
