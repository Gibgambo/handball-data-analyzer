# nuLiga-Fixtures

Grundlage ist die abgeschlossene (und damit unveränderliche) Staffel HVNB 25/26,
Verbandsliga Männer Ost (Gruppe 431976), abgerufen mit `displayTyp=gesamt&displayDetail=meetings`.
Die Staffelseiten sind gekürzte Originale: Seitenrahmen unverändert, in der Spielplan-Tabelle nur ausgewählte Zeilen.

| Datei | Inhalt |
|---|---|
| `431976_frueh.html` | 3 Spielberichte (107001, 107003, 107004) + ein Nicht-Spielbericht-PDF |
| `431976_spaeter.html` | wie `frueh`, zusätzlich 107005 und 107002 (für Aktualisieren) |
| `431976_leer.html` | Staffelseite ohne Spiele |
| `431976_problemfaelle.html` | 107001, 107003 und die drei synthetischen Spielberichte 99000xx |
| `432326_gesamt.html` | andere Staffel (Regionalliga, 101001, 101002) für den Staffelwechsel |

`spielberichte/<Meeting-ID>.pdf` sind echte Spielberichte, bis auf:

- `9900001.pdf` – kein PDF (nicht lesbar → übersprungen)
- `9900002.pdf` – Text eines echten Berichts ohne Spielverlauf-Seite, Spielnummer 999002 (→ mit Warnung)
- `9900003.pdf` – Text eines echten Berichts ohne „Ergebnis“-Zeile, Spielnummer 999003 (→ übersprungen)
