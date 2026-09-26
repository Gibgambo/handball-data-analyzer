# Gemeinsame Anzeigetexte für Dashboard und Kommandozeile

Dashboard und Kommandozeile bereiten die Geladene Staffel und das Importergebnis jeweils selbst für ihr Medium auf. Das Staffel-Modul liefert dafür nur Daten, keine fertigen Anzeigetexte (Ausnahme: `Importergebnis.kurzmeldung()`, die beide Oberflächen wortgleich als Zusammenfassung zeigen).

## Warum das so bleibt

Die Darstellung unterscheidet sich bewusst je Medium:

- **Staffel-Bezeichnung:** Das Dashboard zeigt Saison und Staffelname als getrennte Zeilen (Sidebar) bzw. getrennte Felder („Daten verwalten“); nur die Kommandozeile fügt sie zu „Saison – Staffelname“ zusammen. Eine `GeladeneStaffel.bezeichnung()` hätte genau einen Nutzer.
- **Übersprungene Spielberichte / Spielberichte mit Warnung:** Das Dashboard zeigt Tabellen mit eigenen Spaltenköpfen („nuLiga-ID“, „Grund“, „Fehlt“), die Kommandozeile Fließtext-Zeilen („`<Kennung> (Spiel <Spielnummer>): es fehlt …`“). Die Formulierung „es fehlt …“ existiert nur in der Kommandozeile.

Tatsächlich geteilt ist nur Triviales wie das Verbinden der fehlenden Teile mit Komma. Beschreibungstexte ins Staffel-Modul zu verlegen würde entweder ungenutzt bleiben oder das Dashboard zwingen, seine Tabellen gegen Terminal-Formulierungen zu tauschen — das Staffel-Modul soll aber Fachlogik kapseln, nicht die Präsentation beider Oberflächen.

Anders zu bewerten wäre ein Text, den **beide** Oberflächen wortgleich zeigen (wie `kurzmeldung()`): Der gehört ins Staffel-Modul.

## Prior requests

- #14 — „Anzeige von Importergebnis und Geladener Staffel doppelt in Dashboard und Kommandozeile“
