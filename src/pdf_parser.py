import pdfplumber
import pandas as pd
import os
import re
from datetime import datetime

RAW_DIR = "../data/raw"
PROCESSED_DIR = "../data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def extract_game_info(text):
    """Extrahiert Basisinformationen über das Spiel"""
    info = {}
    
    # Spielnummer
    match = re.search(r"Spielnummer\s+(\d+)", text)
    info['spielnummer'] = match.group(1) if match else None
    
    # Datum und Uhrzeit
    match = re.search(r"Datum\s+(\d{2}\.\d{2}\.\d{4}),\s+Spielbeginn\s+(\d{2}:\d{2})", text)
    if match:
        info['datum'] = match.group(1)
        info['spielbeginn'] = match.group(2)
    
    # Teams
    match = re.search(r"Heimmannschaft\s+(.+?)[\r\n]+Spielort", text)
    info['heimmannschaft'] = match.group(1).strip() if match else None
    
    match = re.search(r"Gastmannschaft\s+(.+?)[\r\n]+Heimmannschaft", text, re.DOTALL)
    if not match:
        match = re.search(r"Gastmannschaft\s+(.+?)[\r\n]", text)
    info['gastmannschaft'] = match.group(1).strip() if match else None
    
    # Endstand
    match = re.search(r"Ergebnis\s+(\d+):(\d+)\s+\((\d+):(\d+)\)", text)
    if match:
        info['endstand_heim'] = int(match.group(1))
        info['endstand_gast'] = int(match.group(2))
        info['halbzeit_heim'] = int(match.group(3))
        info['halbzeit_gast'] = int(match.group(4))
    
    # Spielort
    match = re.search(r"Spielort\s+(.+?)\s+Gastmannschaft", text, re.DOTALL)
    info['spielort'] = match.group(1).strip() if match else None
    
    return info

def extract_player_stats_from_section(section_text, team_name):
    """Extrahiert Spielerstatistiken aus einem bestimmten Textabschnitt"""
    players = []
    lines = section_text.split('\n')
    
    for line in lines:
        # Spielerzeilen extrahieren
        # Format: Trikot Name, Vorname - - [Tore] [7M] [gelbe Karte] [2-Min Zeiten] [Disq]
        match = re.match(r"^(\d+)\s+(.+?)\s+-\s+-\s*(.*)$", line.strip())
        
        if match:
            trikotnummer = match.group(1)
            name = match.group(2).strip()
            stats_part = match.group(3).strip()
            
            # Initialisiere Statistiken
            tore = 0
            siebenmeter = {'versuche': 0, 'tore': 0}
            gelbe_karten = 0
            zweiminuten = 0
            disqualifikation = False
            
            # Parse Statistik-Teil
            if stats_part:
                parts = stats_part.split()
                
                # Erstes Element könnte Tore sein
                if parts and parts[0].isdigit():
                    tore = int(parts[0])
                    parts = parts[1:]
                
                # 7-Meter Format: X/Y oder leer
                if parts and '/' in parts[0]:
                    try:
                        siebenmeter_parts = parts[0].split('/')
                        siebenmeter['tore'] = int(siebenmeter_parts[0])
                        siebenmeter['versuche'] = int(siebenmeter_parts[1])
                        parts = parts[1:]
                    except:
                        pass
                
                # Zähle Zeitstrafen (Format: HH:MM)
                zeitstrafen = [p for p in parts if re.match(r'\d{2}:\d{2}', p)]
                zweiminuten = len(zeitstrafen)
                
                # Prüfe auf "o.B." (ohne Bericht) oder "m.B." (mit Bericht) für Disqualifikation
                if 'o.B.' in stats_part or 'm.B.' in stats_part:
                    disqualifikation = True
            
            player = {
                'trikotnummer': trikotnummer,
                'name': name,
                'tore': tore,
                'siebenmeter_tore': siebenmeter['tore'],
                'siebenmeter_versuche': siebenmeter['versuche'],
                'gelbe_karten': gelbe_karten,
                'zweiminuten_strafen': zweiminuten,
                'disqualifikation': disqualifikation,
                'team': team_name
            }
            players.append(player)
    
    return players

def extract_all_players(text, heim_team, gast_team):
    """Extrahiert Spieler beider Teams aus klar definierten Sektionen"""
    
    # Finde Heimmannschaft-Sektion (von "Heimmannschaft" bis "7-Meter")
    heim_pattern = r"Heimmannschaft\s*\n\s*" + re.escape(heim_team) + r".*?\n(.*?)(?=7-Meter)"
    heim_match = re.search(heim_pattern, text, re.DOTALL)
    
    heim_players = []
    if heim_match:
        heim_section = heim_match.group(1)
        heim_players = extract_player_stats_from_section(heim_section, heim_team)
        print(f"  ✓ Heimmannschaft: {len(heim_players)} Spieler")
    else:
        print(f"  ⚠ Heimmannschaft-Sektion nicht gefunden")
    
    # Finde Gastmannschaft-Sektion (von "Gastmannschaft" bis "7-Meter")
    gast_pattern = r"Gastmannschaft\s*\n\s*" + re.escape(gast_team) + r".*?\n(.*?)(?=7-Meter)"
    gast_match = re.search(gast_pattern, text, re.DOTALL)
    
    gast_players = []
    if gast_match:
        gast_section = gast_match.group(1)
        gast_players = extract_player_stats_from_section(gast_section, gast_team)
        print(f"  ✓ Gastmannschaft: {len(gast_players)} Spieler")
    else:
        print(f"  ⚠ Gastmannschaft-Sektion nicht gefunden")
    
    return heim_players + gast_players

def extract_game_events(text):
    """Extrahiert alle Spielereignisse aus dem Spielverlauf"""
    events = []
    
    # Suche den Spielverlauf-Bereich
    match = re.search(r"Spielverlauf\s*\n(.*?)(?=nu\.Dokument|$)", text, re.DOTALL)
    if not match:
        print("  ⚠ Spielverlauf nicht gefunden")
        return events
    
    spielverlauf = match.group(1)
    
    # Finde alle Events mit finditer (nicht Zeilen-basiert!)
    # Das ist wichtig, weil PDF-Extraktion oft Zeilen falsch umbricht
    
    # Normales Tor: Team Zeit Stand Tor Nummer Name
    # WICHTIG: Nur bis zum nächsten Event oder Zeilenumbruch matchen
    for match in re.finditer(r"(Heim|Gast)\s+(\d{2}:\d{2})\s+(\d+):(\d+)\s+Tor\s+(\d+)\s+([^\n\r]+?)(?=\s+(?:Heim|Gast)\s+\d{2}:\d{2}|\s+\d{2}:\d{2}\s+Auszeit|$)", spielverlauf):
        spieler = match.group(6).strip()
        # Entferne alles nach einem weiteren Team/Zeit Pattern
        spieler = re.sub(r'\s+(Heim|Gast)\s+\d{2}:\d{2}.*', '', spieler)
        
        events.append({
            'team': match.group(1),
            'zeit': match.group(2),
            'stand_heim': int(match.group(3)),
            'stand_gast': int(match.group(4)),
            'ereignis': 'Tor',
            'trikotnummer': match.group(5),
            'spieler': spieler
        })
    
    # 7-Meter mit Tor
    for match in re.finditer(r"(Heim|Gast)\s+(\d{2}:\d{2})\s+(\d+):(\d+)\s+7m\s+mit\s+Tor\s+(\d+)\s+([^\n\r]+?)(?=\s+(?:Heim|Gast)\s+\d{2}:\d{2}|\s+\d{2}:\d{2}\s+Auszeit|$)", spielverlauf):
        spieler = match.group(6).strip()
        spieler = re.sub(r'\s+(Heim|Gast)\s+\d{2}:\d{2}.*', '', spieler)
        
        events.append({
            'team': match.group(1),
            'zeit': match.group(2),
            'stand_heim': int(match.group(3)),
            'stand_gast': int(match.group(4)),
            'ereignis': '7m-Tor',
            'trikotnummer': match.group(5),
            'spieler': spieler
        })
    
    # 7-Meter ohne Tor
    for match in re.finditer(r"(Heim|Gast)\s+(\d{2}:\d{2})\s+(\d+):(\d+)\s+7m\s+ohne\s+Tor\s+(\d+)\s+([^\n\r]+?)(?=\s+(?:Heim|Gast)\s+\d{2}:\d{2}|\s+\d{2}:\d{2}\s+Auszeit|$)", spielverlauf):
        spieler = match.group(6).strip()
        spieler = re.sub(r'\s+(Heim|Gast)\s+\d{2}:\d{2}.*', '', spieler)
        
        events.append({
            'team': match.group(1),
            'zeit': match.group(2),
            'stand_heim': int(match.group(3)),
            'stand_gast': int(match.group(4)),
            'ereignis': '7m-Fehlwurf',
            'trikotnummer': match.group(5),
            'spieler': spieler
        })
    
    # 2-Minuten Strafe
    for match in re.finditer(r"(Heim|Gast)\s+(\d{2}:\d{2})\s+2\s+Minuten\s+(\d+)\s+([^\n\r]+?)(?=\s+(?:Heim|Gast)\s+\d{2}:\d{2}|\s+\d{2}:\d{2}\s+Auszeit|$)", spielverlauf):
        spieler = match.group(4).strip()
        spieler = re.sub(r'\s+(Heim|Gast)\s+\d{2}:\d{2}.*', '', spieler)
        
        events.append({
            'team': match.group(1),
            'zeit': match.group(2),
            'stand_heim': None,
            'stand_gast': None,
            'ereignis': '2-Minuten',
            'trikotnummer': match.group(3),
            'spieler': spieler
        })
    
    # Disqualifikation
    for match in re.finditer(r"(Heim|Gast)\s+(\d{2}:\d{2})\s+ohne\s+Bericht\s+(\d+)\s+([^\n\r]+?)(?=\s+(?:Heim|Gast)\s+\d{2}:\d{2}|\s+\d{2}:\d{2}\s+Auszeit|$)", spielverlauf):
        spieler = match.group(4).strip()
        spieler = re.sub(r'\s+(Heim|Gast)\s+\d{2}:\d{2}.*', '', spieler)
        
        events.append({
            'team': match.group(1),
            'zeit': match.group(2),
            'stand_heim': None,
            'stand_gast': None,
            'ereignis': 'Disqualifikation',
            'trikotnummer': match.group(3),
            'spieler': spieler
        })
    
    # Auszeit
    for match in re.finditer(r"(\d{2}:\d{2})\s+Auszeit\s+(Heim|Gast)", spielverlauf):
        events.append({
            'team': match.group(2),
            'zeit': match.group(1),
            'stand_heim': None,
            'stand_gast': None,
            'ereignis': 'Auszeit',
            'trikotnummer': None,
            'spieler': None
        })
    
    # Sortiere Events nach Zeit
    events.sort(key=lambda x: x['zeit'])
    print(f"  ✓ {len(events)} Ereignisse extrahiert")
    
    return events

# Hauptverarbeitung
all_game_info = []
all_player_stats = []
all_events = []

for pdf_file in os.listdir(RAW_DIR):
    if not pdf_file.endswith(".pdf"):
        continue
    
    pdf_path = os.path.join(RAW_DIR, pdf_file)
    print(f"\n📄 Verarbeite: {pdf_file}")
    
    with pdfplumber.open(pdf_path) as pdf:
        # Gesamten Text extrahieren
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        
        # Spielinformationen
        game_info = extract_game_info(text)
        game_info['pdf_file'] = pdf_file
        all_game_info.append(game_info)
        
        print(f"  ✓ Spiel: {game_info.get('heimmannschaft')} vs {game_info.get('gastmannschaft')}")
        
        # Spielerstatistiken - NEUE METHODE
        players = extract_all_players(
            text, 
            game_info.get('heimmannschaft'),
            game_info.get('gastmannschaft')
        )
        
        for player in players:
            player['pdf_file'] = pdf_file
            player['spielnummer'] = game_info.get('spielnummer')
        all_player_stats.extend(players)
        
        # Spielereignisse
        events = extract_game_events(text)
        for event in events:
            event['pdf_file'] = pdf_file
            event['spielnummer'] = game_info.get('spielnummer')
        all_events.extend(events)

# CSVs erstellen
print(f"\n📊 Erstelle CSVs...")

df_games = pd.DataFrame(all_game_info)
df_players = pd.DataFrame(all_player_stats)
df_events = pd.DataFrame(all_events)

# Datentypen anpassen
df_games = df_games.astype({
    'endstand_heim': 'Int64',
    'endstand_gast': 'Int64',
    'halbzeit_heim': 'Int64',
    'halbzeit_gast': 'Int64'
})

# Spieler-Datentypen
df_players = df_players.astype({
    'tore': 'Int64',
    'siebenmeter_tore': 'Int64',
    'siebenmeter_versuche': 'Int64',
    'zweiminuten_strafen': 'Int64',
    'gelbe_karten': 'Int64'
})

df_events['stand_heim'] = df_events['stand_heim'].astype('Int64')
df_events['stand_gast'] = df_events['stand_gast'].astype('Int64')

# Duplikate entfernen (falls trotzdem welche entstehen)
df_players = df_players.drop_duplicates(subset=['spielnummer', 'team', 'trikotnummer'], keep='first')

print(f"  ✓ {len(df_games)} Spiele")
print(f"  ✓ {len(df_players)} Spieler (nach Duplikat-Entfernung)")
print(f"  ✓ {len(df_events)} Ereignisse")

# Speichern
games_csv = os.path.join(PROCESSED_DIR, "spiele.csv")
players_csv = os.path.join(PROCESSED_DIR, "spieler_statistiken.csv")
events_csv = os.path.join(PROCESSED_DIR, "spielereignisse.csv")

df_games.to_csv(games_csv, index=False, encoding='utf-8-sig')
df_players.to_csv(players_csv, index=False, encoding='utf-8-sig')
df_events.to_csv(events_csv, index=False, encoding='utf-8-sig')

print(f"\n✅ Erfolgreich verarbeitet!")
print(f"📊 {games_csv}")
print(f"👥 {players_csv}")
print(f"⚡ {events_csv}")

# Validierung
print(f"\n🔍 Validierung:")
# Prüfe auf echte Duplikate (gleiche Spielnummer, Team UND Trikotnummer)
duplicates = df_players.groupby(['spielnummer', 'team', 'trikotnummer']).size()
if (duplicates > 1).any():
    print(f"⚠️  WARNUNG: {(duplicates > 1).sum()} Spieler erscheinen mehrfach!")
    dup_mask = df_players.duplicated(subset=['spielnummer', 'team', 'trikotnummer'], keep=False)
    print(df_players[dup_mask][['name', 'team', 'trikotnummer', 'spielnummer']])
else:
    print(f"✅ Keine Duplikate gefunden!")
    
# Prüfe Team-Größen
team_sizes = df_players.groupby(['spielnummer', 'team']).size()
print(f"\n📋 Team-Größen:")
for (spiel, team), count in team_sizes.items():
    print(f"   Spiel {spiel} - {team}: {count} Spieler")