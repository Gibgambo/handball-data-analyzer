"""Adapter für den einzigen Zugriff nach außen: HTTP-Abrufe bei nuLiga.

In Produktion wird HttpNuLiga verwendet, in Tests ein Fake mit derselben Schnittstelle:
- staffelseite_abrufen(url) -> str (HTML)
- dokument_abrufen(url) -> bytes (PDF)
"""
import requests

TIMEOUT_SEKUNDEN = 30


class NuLigaFehler(Exception):
    """Basisklasse für Fehler beim Abruf von nuLiga."""


class NuLigaNichtErreichbar(NuLigaFehler):
    """nuLiga hat nicht (oder mit einem Serverfehler) geantwortet."""


class NuLigaSeiteNichtGefunden(NuLigaFehler):
    """nuLiga kennt die angefragte Seite nicht (HTTP 404)."""


class HttpNuLiga:
    def __init__(self):
        self._session = requests.Session()

    def staffelseite_abrufen(self, url):
        return self._get(url).text

    def dokument_abrufen(self, url):
        return self._get(url).content

    def _get(self, url):
        try:
            response = self._session.get(url, timeout=TIMEOUT_SEKUNDEN)
        except requests.RequestException as e:
            raise NuLigaNichtErreichbar(str(e)) from e
        if response.status_code == 404:
            raise NuLigaSeiteNichtGefunden(url)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise NuLigaNichtErreichbar(str(e)) from e
        return response
