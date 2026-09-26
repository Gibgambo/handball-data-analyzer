"""Staffel-Modul: verwaltet die Geladene Staffel (Begriffe siehe CONTEXT.md).

Einzige Nahtstelle für Dashboard und Tests:
- Staffelverwaltung.geladene_staffel() -> GeladeneStaffel oder None
- Staffelverwaltung.staffel_wechseln(staffel_link) -> Importergebnis
- Staffelverwaltung.aktualisieren() -> Importergebnis

Fehler, die dem Nutzer gemeldet werden sollen, sind StaffelFehler; ihr Text ist die Meldung.
Bei jedem StaffelFehler bleibt die bisher geladene Staffel unverändert.
"""
import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

import paths
import pdf_parser
from nuliga import HttpNuLiga, NuLigaNichtErreichbar, NuLigaSeiteNichtGefunden

ZUSTANDSDATEI = "staffel.json"
SPIELBERICHT_DOKUMENT = "meetingReportHB"

# Spieldaten, ohne die ein Spielbericht übersprungen wird: Feld -> Bezeichnung für den Nutzer
PFLICHTFELDER = {
    "spielnummer": "Spielnummer",
    "datum": "Datum",
    "heimmannschaft": "Heimmannschaft",
    "gastmannschaft": "Gastmannschaft",
    "endstand_heim": "Endstand",
    "endstand_gast": "Endstand",
}


class StaffelFehler(Exception):
    """Ein Import konnte nicht durchgeführt werden; der Text ist für den Nutzer bestimmt."""


class UngueltigerStaffelLink(StaffelFehler):
    pass


class NuLigaNichtErreichbarFehler(StaffelFehler):
    pass


@dataclass
class UebersprungenerSpielbericht:
    kennung: str
    grund: str


@dataclass
class SpielberichtMitWarnung:
    kennung: str
    spielnummer: str
    fehlend: list


@dataclass
class Importergebnis:
    neu: list = field(default_factory=list)
    uebersprungen: list = field(default_factory=list)
    mit_warnung: list = field(default_factory=list)

    def kurzmeldung(self):
        if not self.neu:
            teile = ["Keine neuen Spielberichte"]
        elif len(self.neu) == 1:
            teile = ["1 neuer Spielbericht"]
        else:
            teile = [f"{len(self.neu)} neue Spielberichte"]
        if self.mit_warnung:
            teile.append(f"{len(self.mit_warnung)} mit Warnung")
        if self.uebersprungen:
            teile.append(f"{len(self.uebersprungen)} übersprungen")
        return ", ".join(teile)

    @classmethod
    def aus_dict(cls, daten):
        return cls(
            neu=list(daten.get("neu", [])),
            uebersprungen=[UebersprungenerSpielbericht(**u) for u in daten.get("uebersprungen", [])],
            mit_warnung=[SpielberichtMitWarnung(**w) for w in daten.get("mit_warnung", [])],
        )


@dataclass
class GeladeneStaffel:
    staffel_link: str
    saison: str
    staffelname: str
    aktualisiert_am: datetime
    anzahl_spiele: int
    anzahl_spieler: int
    letzter_import: Importergebnis


@dataclass(frozen=True)
class _StaffelAdresse:
    """Die aus einem Staffel-Link gelesene Identität einer Staffel."""
    basis_url: str
    wa_pfad: str
    championship: str
    group: str

    def gesamt_url(self):
        query = urlencode({
            "displayTyp": "gesamt",
            "displayDetail": "meetings",
            "championship": self.championship,
            "group": self.group,
        })
        return f"{self.basis_url}{self.wa_pfad}groupPage?{query}"


def _staffel_adresse(staffel_link):
    link = (staffel_link or "").strip()
    if link and "://" not in link:
        link = "https://" + link
    url = urlparse(link)
    host = (url.hostname or "").lower()
    if not (host == "liga.nu" or host.endswith(".liga.nu")):
        raise UngueltigerStaffelLink(
            "Das ist kein Staffel-Link. Bitte einen Link von einer nuLiga-Staffelseite "
            "(…liga.nu) einfügen."
        )
    query = parse_qs(url.query)
    championship = query.get("championship", [""])[0].strip()
    group = query.get("group", [""])[0].strip()
    if not championship or not group:
        raise UngueltigerStaffelLink(
            "Der Link identifiziert keine Staffel (es fehlen „championship“ oder „group“). "
            "Bitte den Link einer Staffelseite kopieren, z. B. Tabelle oder Spielplan."
        )
    scheme = url.scheme if url.scheme in ("http", "https") else "https"
    match = re.match(r"^(.*/wa/)[^/]*$", url.path)
    wa_pfad = match.group(1) if match else "/cgi-bin/WebObjects/nuLigaHBDE.woa/wa/"
    return _StaffelAdresse(f"{scheme}://{url.netloc}", wa_pfad, championship, group)


def _spielbericht_links(html, seiten_url):
    """Meeting-ID -> URL aller Spielberichte der Staffelseite (andere PDFs werden ignoriert)."""
    links = {}
    for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        query = parse_qs(urlparse(a["href"]).query)
        meeting = query.get("meeting", [None])[0]
        if query.get("dokument") == [SPIELBERICHT_DOKUMENT] and meeting:
            links.setdefault(meeting, urljoin(seiten_url, a["href"]))
    return links


def _saison_und_name(html, adresse):
    h1 = BeautifulSoup(html, "html.parser").find("h1")
    teile = [t.strip() for t in h1.stripped_strings] if h1 else []
    saison = teile[0] if teile else adresse.championship
    # Aufbau der Überschrift: Saison / Staffelname / Ansicht
    staffelname = teile[1] if len(teile) >= 3 else None
    return saison, staffelname


class Staffelverwaltung:
    def __init__(self, nuliga=None):
        self._nuliga = nuliga if nuliga is not None else HttpNuLiga()

    # --- Nahtstelle -------------------------------------------------------

    def geladene_staffel(self):
        datei = self._zustandsdatei()
        if not datei.is_file():
            return None
        daten = json.loads(datei.read_text(encoding="utf-8"))
        return GeladeneStaffel(
            staffel_link=daten["staffel_link"],
            saison=daten["saison"],
            staffelname=daten.get("staffelname"),
            aktualisiert_am=datetime.fromisoformat(daten["aktualisiert_am"]),
            anzahl_spiele=daten["anzahl_spiele"],
            anzahl_spieler=daten["anzahl_spieler"],
            letzter_import=Importergebnis.aus_dict(daten.get("letzter_import", {})),
        )

    def staffel_wechseln(self, staffel_link, fortschritt=None):
        """Verwirft die bisherige Staffel und lädt die Staffel des Links vollständig."""
        adresse = _staffel_adresse(staffel_link)
        return self._importieren(staffel_link, adresse, verwerfen=True, fortschritt=fortschritt)

    def aktualisieren(self, fortschritt=None):
        """Ergänzt die Geladene Staffel um neu erschienene Spielberichte."""
        staffel = self.geladene_staffel()
        if staffel is None:
            raise StaffelFehler("Es ist noch keine Staffel geladen.")
        adresse = _staffel_adresse(staffel.staffel_link)
        return self._importieren(staffel.staffel_link, adresse, verwerfen=False, fortschritt=fortschritt)

    # --- Ablauf -----------------------------------------------------------

    def _importieren(self, staffel_link, adresse, verwerfen, fortschritt):
        melde = fortschritt or (lambda text, anteil: None)

        # Erst alles von nuLiga holen; erst danach wird der Datenbestand verändert.
        melde("Staffelseite wird abgerufen …", 0.0)
        seiten_url = adresse.gesamt_url()
        html = self._abrufen(self._nuliga.staffelseite_abrufen, seiten_url)
        saison, staffelname = _saison_und_name(html, adresse)
        links = _spielbericht_links(html, seiten_url)

        vorhanden = set() if verwerfen else {p.stem for p in paths.raw_dir().glob("*.pdf")}
        neue = [(meeting, url) for meeting, url in links.items() if meeting not in vorhanden]
        downloads = {}
        nicht_abrufbar = []
        for i, (meeting, url) in enumerate(neue):
            melde(f"Spielbericht {i + 1} von {len(neue)} wird heruntergeladen …", 0.1 + 0.6 * i / len(neue))
            try:
                downloads[meeting] = self._abrufen(self._nuliga.dokument_abrufen, url)
            except UngueltigerStaffelLink:
                # Einzelner Spielbericht fehlt bei nuLiga: nicht speichern, beim nächsten Aktualisieren erneut versuchen
                nicht_abrufbar.append(UebersprungenerSpielbericht(meeting, "Spielbericht bei nuLiga nicht abrufbar"))

        if verwerfen:
            self._daten_verwerfen()
        raw_dir = paths.raw_dir()
        for meeting, inhalt in downloads.items():
            (raw_dir / f"{meeting}.pdf").write_bytes(inhalt)

        melde("Spielberichte werden ausgewertet …", 0.7)
        ergebnis, df_games, df_players = self._alle_spielberichte_auswerten()
        ergebnis.neu = list(downloads)
        ergebnis.uebersprungen += nicht_abrufbar

        self._zustand_speichern({
            "staffel_link": staffel_link,
            "saison": saison,
            "staffelname": staffelname,
            "aktualisiert_am": datetime.now().isoformat(timespec="seconds"),
            "anzahl_spiele": len(df_games),
            "anzahl_spieler": len(df_players.groupby(["name", "team"]).size()),
            "letzter_import": asdict(ergebnis),
        })
        melde("Fertig", 1.0)
        return ergebnis

    def _abrufen(self, abruf, url):
        try:
            return abruf(url)
        except NuLigaSeiteNichtGefunden as e:
            raise UngueltigerStaffelLink(
                "nuLiga kennt diese Staffel nicht. Bitte den Staffel-Link prüfen."
            ) from e
        except NuLigaNichtErreichbar as e:
            raise NuLigaNichtErreichbarFehler(
                "nuLiga ist gerade nicht erreichbar. Bitte später erneut versuchen."
            ) from e

    def _alle_spielberichte_auswerten(self):
        ergebnis = Importergebnis()
        berichte = []
        for pdf in sorted(paths.raw_dir().glob("*.pdf")):
            kennung = pdf.stem
            try:
                game_info, players, events = pdf_parser.extract_report(pdf)
            except Exception as e:  # jedes nicht lesbare PDF wird übersprungen, statt den Import abzubrechen
                ergebnis.uebersprungen.append(
                    UebersprungenerSpielbericht(kennung, f"Spielbericht nicht lesbar ({type(e).__name__})"))
                continue

            fehlend = list(dict.fromkeys(
                name for feld, name in PFLICHTFELDER.items() if game_info.get(feld) is None))
            if fehlend:
                ergebnis.uebersprungen.append(UebersprungenerSpielbericht(
                    kennung, "Spieldaten unvollständig, es fehlt: " + ", ".join(fehlend)))
                continue

            luecken = []
            if not players:
                luecken.append("Spielerstatistiken")
            if not events:
                luecken.append("Spielverlauf")
            if luecken:
                ergebnis.mit_warnung.append(
                    SpielberichtMitWarnung(kennung, str(game_info["spielnummer"]), luecken))
            berichte.append((game_info, players, events))

        df_games, df_players, _ = pdf_parser.write_csvs(berichte, paths.processed_dir())
        return ergebnis, df_games, df_players

    # --- Datenverzeichnis ---------------------------------------------------

    def _daten_verwerfen(self):
        for verzeichnis in (paths.raw_dir(), paths.processed_dir(),
                            paths.analysis_dir(), paths.visualizations_dir()):
            shutil.rmtree(verzeichnis)
        self._zustandsdatei().unlink(missing_ok=True)

    def _zustandsdatei(self):
        return paths.data_dir() / ZUSTANDSDATEI

    def _zustand_speichern(self, daten):
        datei = self._zustandsdatei()
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
