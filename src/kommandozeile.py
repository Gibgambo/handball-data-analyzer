"""Kommandozeile für die Geladene Staffel (Begriffe siehe CONTEXT.md).

    python src/kommandozeile.py                              Aktualisieren: neu erschienene Spielberichte ergänzen
    python src/kommandozeile.py <Staffel-Link>               Erste Staffel laden
    python src/kommandozeile.py <Staffel-Link> --verwerfen   Staffelwechsel bei bereits Geladener Staffel

Dieselben Abläufe wie im Dashboard; die Arbeit erledigt das Staffel-Modul.
"""
import argparse
import sys

from staffel import StaffelFehler, Staffelverwaltung


def _argumente(argv):
    parser = argparse.ArgumentParser(
        prog="kommandozeile.py",
        description="Ohne Staffel-Link wird die Geladene Staffel aktualisiert, "
                    "mit Staffel-Link wird die Staffel des Links vollständig geladen.",
    )
    parser.add_argument("staffel_link", nargs="?", help="Link einer nuLiga-Staffelseite (beliebige Ansicht)")
    parser.add_argument("--verwerfen", action="store_true",
                        help="Staffelwechsel bestätigen: alle Daten der bisherigen Staffel werden verworfen")
    return parser.parse_args(argv)


def main(argv=None, verwaltung=None):
    """Führt Staffelwechsel (mit Staffel-Link) oder Aktualisieren (ohne) aus; liefert den Exit-Code."""
    argumente = _argumente(sys.argv[1:] if argv is None else argv)
    verwaltung = verwaltung if verwaltung is not None else Staffelverwaltung()

    def fortschritt(text, anteil):
        print(f"[{anteil:4.0%}] {text}")

    if argumente.staffel_link and not argumente.verwerfen and verwaltung.geladene_staffel() is not None:
        print("Es ist bereits eine Staffel geladen. Ein Staffelwechsel verwirft alle ihre Daten "
              "(Spielberichte, Auswertungen und Exporte); zum Bestätigen --verwerfen angeben.",
              file=sys.stderr)
        return 1

    try:
        if argumente.staffel_link:
            ergebnis = verwaltung.staffel_wechseln(argumente.staffel_link, fortschritt)
        else:
            ergebnis = verwaltung.aktualisieren(fortschritt)
    except StaffelFehler as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1

    staffel = verwaltung.geladene_staffel()
    print(f"\n{ergebnis.kurzmeldung()}")
    print(f"Geladene Staffel: {staffel.saison}" + (f" – {staffel.staffelname}" if staffel.staffelname else ""))
    print(f"{staffel.anzahl_spiele} Spiele · {staffel.anzahl_spieler} Spieler")

    if ergebnis.uebersprungen:
        print("\nÜbersprungene Spielberichte (fließen in keine Auswertung ein):")
        for bericht in ergebnis.uebersprungen:
            print(f"  {bericht.kennung}: {bericht.grund}")
    if ergebnis.mit_warnung:
        print("\nSpielberichte mit Warnung:")
        for bericht in ergebnis.mit_warnung:
            print(f"  {bericht.kennung} (Spiel {bericht.spielnummer}): es fehlt {', '.join(bericht.fehlend)}")
    return 0


if __name__ == "__main__":
    # Umgeleitete Ausgaben nutzen unter Windows die Codepage (z. B. cp1252); dort nicht darstellbare
    # Zeichen (auch aus dem pdf_parser) werden ersetzt statt einen UnicodeEncodeError auszulösen
    for strom in (sys.stdout, sys.stderr):
        strom.reconfigure(errors="replace")
    sys.exit(main())
