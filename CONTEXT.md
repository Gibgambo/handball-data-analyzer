# Handball Data Analyzer

Analysiert die Spielberichte einer Handball-Staffel aus nuLiga und stellt sie in einem Dashboard dar.

## Language

**Staffel**:
Eine Liga innerhalb einer Saison bei nuLiga (z. B. HVNB 25/26, Gruppe 431976) mit all ihren Mannschaften und Spielen. Das Dashboard zeigt immer genau eine Staffel.
_Avoid_: Liga, Gruppe, Saison (wenn die Staffel gemeint ist)

**Saison**:
Der Meisterschaftszeitraum eines Verbands (z. B. HVNB 25/26), in dem es viele Staffeln gibt.
_Avoid_: Championship, Meisterschaft

**Staffel-Link**:
Eine beliebige nuLiga-URL, die eine Staffel identifiziert; welche Ansicht (Vorrunde, Rückrunde, Tabelle …) sie zeigt, ist unerheblich.
_Avoid_: Liga-Link, Saison-Link, nuLiga-Link

**Geladene Staffel**:
Die eine Staffel, deren Spielberichte aktuell lokal vorliegen und im Dashboard ausgewertet werden, samt ihrem Staffel-Link und dem Zeitpunkt der letzten Aktualisierung.

**Spielbericht**:
Das offizielle PDF eines gespielten Spiels, das nuLiga zur Staffel veröffentlicht; die einzige Datenquelle der Analyse.
_Avoid_: PDF, Report

**Spieldaten**:
Der Kern eines Spielberichts: Spielnummer, Datum, Heim- und Gastmannschaft, Endstand. Ohne vollständige Spieldaten ist ein Spielbericht unbrauchbar.

**Übersprungener Spielbericht**:
Ein Spielbericht, dessen Spieldaten nicht vollständig gelesen werden konnten; er fließt in keine Auswertung ein und wird dem Nutzer gemeldet.

**Spielbericht mit Warnung**:
Ein Spielbericht mit vollständigen Spieldaten, aber fehlenden Spielerstatistiken oder fehlendem Spielverlauf; er zählt für Ergebnis-Auswertungen, die Lücken werden dem Nutzer gemeldet.

**Aktualisieren**:
Die geladene Staffel um neu erschienene Spielberichte ergänzen; bereits vorhandene Spielberichte werden nicht erneut geladen.
_Avoid_: Refresh, Neu scrapen

**Staffelwechsel**:
Einen neuen Staffel-Link setzen; alle Daten der bisherigen Staffel werden verworfen und die neue Staffel vollständig geladen.
_Avoid_: Saisonwechsel, Reset

**Import**:
Oberbegriff für Staffelwechsel und Aktualisieren: Spielberichte der Staffel von nuLiga laden und auswerten. Sein Ergebnis – neue Spielberichte, Übersprungene Spielberichte und Spielberichte mit Warnung – wird zur Geladenen Staffel als letzter Import gemeldet.
_Avoid_: Scrapen, Download

**Vorrunde / Rückrunde**:
Die beiden Hälften einer Staffel; eine Staffel umfasst immer beide.
_Avoid_: Hinrunde
