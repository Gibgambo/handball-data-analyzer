import pandas as pd
import numpy as np
import os
from datetime import datetime

class HandballAnalyzer:
    def __init__(self, data_dir="../data/processed"):
        """Initialisiert den Analyzer mit dem Datenverzeichnis"""
        self.data_dir = data_dir
        self.df_games = None
        self.df_players = None
        self.df_events = None
        self.load_data()
    
    def load_data(self):
        """Lädt alle CSV-Dateien aus dem Datenverzeichnis"""
        try:
            games_file = os.path.join(self.data_dir, "spiele.csv")
            players_file = os.path.join(self.data_dir, "spieler_statistiken.csv")
            events_file = os.path.join(self.data_dir, "spielereignisse.csv")
            
            self.df_games = pd.read_csv(games_file, skipinitialspace=True)
            self.df_players = pd.read_csv(players_file, skipinitialspace=True)
            self.df_events = pd.read_csv(events_file, skipinitialspace=True)
            
            # Spalten bereinigen
            self.df_games.columns = self.df_games.columns.str.strip()
            self.df_players.columns = self.df_players.columns.str.strip()
            self.df_events.columns = self.df_events.columns.str.strip()
            
            # Datum konvertieren
            if 'datum' in self.df_games.columns:
                self.df_games['datum'] = pd.to_datetime(
                    self.df_games['datum'], 
                    format='%d.%m.%Y', 
                    errors='coerce'
                )
            
            print(f"✅ Daten geladen: {len(self.df_games)} Spiele, {len(self.df_players)} Spieler-Einträge, {len(self.df_events)} Events")
        except FileNotFoundError as e:
            print(f"❌ Fehler: Dateien nicht gefunden in {self.data_dir}")
            print(f"   Stelle sicher, dass folgende Dateien existieren:")
            print(f"   - spiele.csv")
            print(f"   - spieler_statistiken.csv")
            print(f"   - spielereignisse.csv")
            raise
        except Exception as e:
            print(f"❌ Fehler beim Laden der Daten: {e}")
            raise
    
    def get_top_scorer(self, top_n=10):
        """Gibt die Top-Torschützen zurück"""
        top_scorer = (self.df_players
                      .groupby(['name', 'team'], as_index=False)['tore']
                      .sum()
                      .sort_values('tore', ascending=False)
                      .head(top_n))
        
        return top_scorer
    
    def get_team_statistics(self):
        """Berechnet Team-Statistiken"""
        stats = []
        
        for _, game in self.df_games.iterrows():
            # Heimteam
            stats.append({
                'team': game['heimmannschaft'],
                'tore_geschossen': game['endstand_heim'],
                'tore_kassiert': game['endstand_gast'],
                'sieg': 1 if game['endstand_heim'] > game['endstand_gast'] else 0,
                'unentschieden': 1 if game['endstand_heim'] == game['endstand_gast'] else 0,
                'niederlage': 1 if game['endstand_heim'] < game['endstand_gast'] else 0,
                'ist_heim': True,
                'datum': game['datum']
            })
            
            # Gastteam
            stats.append({
                'team': game['gastmannschaft'],
                'tore_geschossen': game['endstand_gast'],
                'tore_kassiert': game['endstand_heim'],
                'sieg': 1 if game['endstand_gast'] > game['endstand_heim'] else 0,
                'unentschieden': 1 if game['endstand_gast'] == game['endstand_heim'] else 0,
                'niederlage': 1 if game['endstand_gast'] < game['endstand_heim'] else 0,
                'ist_heim': False,
                'datum': game['datum']
            })
        
        df_stats = pd.DataFrame(stats)
        
        # Aggregierte Statistiken pro Team
        team_summary = df_stats.groupby('team').agg({
            'tore_geschossen': ['sum', 'mean'],
            'tore_kassiert': ['sum', 'mean'],
            'sieg': 'sum',
            'unentschieden': 'sum',
            'niederlage': 'sum'
        }).round(2)
        
        team_summary.columns = ['_'.join(col) if col[1] else col[0] 
                                for col in team_summary.columns]
        
        # Spiele zählen und weitere Metriken
        team_summary['spiele'] = (team_summary['sieg_sum'] + 
                                   team_summary['unentschieden_sum'] + 
                                   team_summary['niederlage_sum'])
        team_summary['siegquote'] = (team_summary['sieg_sum'] / 
                                     team_summary['spiele'] * 100).round(1)
        team_summary['tordifferenz'] = (team_summary['tore_geschossen_sum'] - 
                                        team_summary['tore_kassiert_sum'])
        
        team_summary = team_summary.reset_index()
        
        # Umbenennen
        team_summary = team_summary.rename(columns={
            'tore_geschossen_sum': 'tore_geschossen',
            'tore_geschossen_mean': 'tore_pro_spiel',
            'tore_kassiert_sum': 'tore_kassiert',
            'tore_kassiert_mean': 'gegentore_pro_spiel',
            'sieg_sum': 'siege',
            'unentschieden_sum': 'unentschieden',
            'niederlage_sum': 'niederlagen'
        })
        
        # Sortieren nach Siegquote, dann Tordifferenz
        return team_summary.sort_values(['siegquote', 'tordifferenz'], ascending=[False, False])
    
    def get_home_advantage(self):
        """Berechnet Heimvorteil-Statistiken"""
        stats = []
        
        for _, game in self.df_games.iterrows():
            stats.append({
                'ist_heim': True,
                'sieg': 1 if game['endstand_heim'] > game['endstand_gast'] else 0,
                'unentschieden': 1 if game['endstand_heim'] == game['endstand_gast'] else 0
            })
            stats.append({
                'ist_heim': False,
                'sieg': 1 if game['endstand_gast'] > game['endstand_heim'] else 0,
                'unentschieden': 1 if game['endstand_gast'] == game['endstand_heim'] else 0
            })
        
        df_stats = pd.DataFrame(stats)
        home_stats = df_stats.groupby('ist_heim').agg({
            'sieg': ['sum', 'count'],
            'unentschieden': 'sum'
        })
        
        heim_siege = int(home_stats.loc[True, ('sieg', 'sum')]) if True in home_stats.index else 0
        auswaerts_siege = int(home_stats.loc[False, ('sieg', 'sum')]) if False in home_stats.index else 0
        heim_spiele = int(home_stats.loc[True, ('sieg', 'count')]) if True in home_stats.index else 0
        auswaerts_spiele = int(home_stats.loc[False, ('sieg', 'count')]) if False in home_stats.index else 0
        
        return {
            'heim_siegquote': round(heim_siege / heim_spiele * 100, 1) if heim_spiele > 0 else 0,
            'auswaerts_siegquote': round(auswaerts_siege / auswaerts_spiele * 100, 1) if auswaerts_spiele > 0 else 0,
            'heim_siege': heim_siege,
            'auswaerts_siege': auswaerts_siege,
            'gesamt_spiele': len(self.df_games)
        }
    
    def get_average_goals_per_game(self):
        """Berechnet durchschnittliche Tore pro Spiel"""
        if len(self.df_games) == 0:
            return {'gesamt': 0, 'heim': 0, 'gast': 0}
        
        return {
            'gesamt': round((self.df_games['endstand_heim'] + 
                            self.df_games['endstand_gast']).mean(), 2),
            'heim': round(self.df_games['endstand_heim'].mean(), 2),
            'gast': round(self.df_games['endstand_gast'].mean(), 2)
        }
    
    def get_goal_timeline(self, spielnummer=None):
        """Erstellt Torverlauf über die Spielzeit für ein spezifisches Spiel"""
        if spielnummer is None and len(self.df_games) > 0:
            spielnummer = self.df_games['spielnummer'].iloc[0]
        
        tor_events = self.df_events[
            (self.df_events['spielnummer'] == spielnummer) & 
            (self.df_events['ereignis'].isin(['Tor', '7m-Tor']))
        ].copy()
        
        if len(tor_events) == 0:
            return pd.DataFrame()
        
        tor_events['minute'] = tor_events['zeit'].apply(self._time_to_minutes)
        tor_events = tor_events.sort_values('minute')
        
        return tor_events[['minute', 'team', 'stand_heim', 'stand_gast', 
                          'spieler', 'ereignis']]
    
    def get_goals_by_minute(self):
        """Analysiert Torverteilung nach Spielminuten"""
        tor_events = self.df_events[
            self.df_events['ereignis'].isin(['Tor', '7m-Tor'])
        ].copy()
        
        if len(tor_events) == 0:
            return pd.DataFrame()
        
        tor_events['minute'] = tor_events['zeit'].apply(self._time_to_minutes)
        tor_events['intervall'] = (tor_events['minute'] // 5) * 5
        
        heatmap_data = tor_events.groupby(['intervall', 'team']).size().reset_index(name='anzahl_tore')
        
        return heatmap_data
    
    def get_penalty_statistics(self):
        """Analysiert 2-Minuten-Strafen"""
        strafen = self.df_events[self.df_events['ereignis'] == '2-Minuten'].copy()
        
        if len(strafen) == 0:
            return pd.DataFrame()
        
        top_strafen = (strafen.groupby(['spieler', 'team'])
                       .size()
                       .reset_index(name='anzahl_strafen')
                       .sort_values('anzahl_strafen', ascending=False)
                       .head(10))
        
        return top_strafen
    
    def get_7m_efficiency(self):
        """Berechnet 7-Meter-Effizienz aus Event-Daten"""
        siebenmeter = self.df_events[
            self.df_events['ereignis'].str.contains('7m', na=False)
        ].copy()
        
        if len(siebenmeter) == 0:
            return pd.DataFrame()
        
        stats = []
        for (spieler, team), gruppe in siebenmeter.groupby(['spieler', 'team']):
            verwandelt = len(gruppe[gruppe['ereignis'] == '7m-Tor'])
            fehlwuerfe = len(gruppe[gruppe['ereignis'] == '7m-Fehlwurf'])
            gesamt = verwandelt + fehlwuerfe
            
            if gesamt > 0:
                stats.append({
                    'spieler': spieler,
                    'team': team,
                    'verwandelt': verwandelt,
                    'fehlwuerfe': fehlwuerfe,
                    'gesamt': gesamt,
                    'quote': round(verwandelt / gesamt * 100, 1)
                })
        
        df_stats = pd.DataFrame(stats)
        return df_stats.sort_values('gesamt', ascending=False)
    
    def get_game_tempo(self):
        """Analysiert Spieltempo (Tore pro Zeiteinheit)"""
        tempo_data = []
        
        for spielnummer in self.df_events['spielnummer'].unique():
            tor_events = self.df_events[
                (self.df_events['spielnummer'] == spielnummer) & 
                (self.df_events['ereignis'].isin(['Tor', '7m-Tor']))
            ].copy()
            
            if len(tor_events) > 0:
                tor_events['minute'] = tor_events['zeit'].apply(self._time_to_minutes)
                
                erste_halb = tor_events[tor_events['minute'] <= 30]
                zweite_halb = tor_events[tor_events['minute'] > 30]
                
                tempo_data.append({
                    'spielnummer': spielnummer,
                    'tore_1_halbzeit': len(erste_halb),
                    'tore_2_halbzeit': len(zweite_halb),
                    'tempo_1_halbzeit': round(len(erste_halb) / 30, 2),
                    'tempo_2_halbzeit': round(len(zweite_halb) / 30, 2)
                })
        
        return pd.DataFrame(tempo_data)
    
    def get_player_performance(self, min_goals=0):
        """Detaillierte Spieleranalyse mit Events-Daten"""
        # Tore aus Events
        tore_events = self.df_events[
            self.df_events['ereignis'].isin(['Tor', '7m-Tor'])
        ].copy()
        
        tore_pro_spieler = (tore_events.groupby(['spieler', 'team'])
                           .size()
                           .reset_index(name='tore_aus_events'))
        
        # Mit Spieler-Statistiken zusammenführen
        player_stats = self.df_players.groupby(['name', 'team']).agg({
            'tore': 'sum',
            'siebenmeter_tore': 'sum',
            'siebenmeter_versuche': 'sum',
            'zweiminuten_strafen': 'sum',
            'disqualifikation': 'any'
        }).reset_index()
        
        # Merge
        combined = player_stats.merge(
            tore_pro_spieler,
            left_on=['name', 'team'],
            right_on=['spieler', 'team'],
            how='left'
        )
        
        combined['tore_aus_events'] = combined['tore_aus_events'].fillna(0)
        combined['7m_quote'] = np.where(
            combined['siebenmeter_versuche'] > 0,
            (combined['siebenmeter_tore'] / combined['siebenmeter_versuche'] * 100).round(1),
            0
        )
        
        # Filtern
        combined = combined[combined['tore'] >= min_goals]
        
        return combined.sort_values('tore', ascending=False)
    
    def get_disqualifications(self):
        """Analysiert Disqualifikationen"""
        disq_events = self.df_events[
            self.df_events['ereignis'] == 'Disqualifikation'
        ].copy()
        
        if len(disq_events) == 0:
            return pd.DataFrame()
        
        return disq_events[['zeit', 'team', 'spieler', 'spielnummer']]
    
    def _time_to_minutes(self, time_str):
        """Konvertiert Zeit (MM:SS) zu Dezimalminuten"""
        try:
            if pd.isna(time_str):
                return 0
            parts = str(time_str).split(':')
            return int(parts[0]) + int(parts[1]) / 60
        except:
            return 0
    
    def save_all_analyses(self, output_dir="../data/analysis"):
        """Speichert ALLE Analysen als CSV-Dateien"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Speichere Analysen in {output_dir}...\n")
        
        # 1. Top Scorer
        top_scorer = self.get_top_scorer(top_n=50)
        if len(top_scorer) > 0:
            filepath = os.path.join(output_dir, "top_scorer.csv")
            top_scorer.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ top_scorer.csv ({len(top_scorer)} Einträge)")
        
        # 2. Team-Statistiken
        team_stats = self.get_team_statistics()
        if len(team_stats) > 0:
            filepath = os.path.join(output_dir, "team_statistics.csv")
            team_stats.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ team_statistics.csv ({len(team_stats)} Teams)")
        
        # 3. Heimvorteil
        home_adv = self.get_home_advantage()
        filepath = os.path.join(output_dir, "home_advantage.csv")
        pd.DataFrame([home_adv]).to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✅ home_advantage.csv")
        
        # 4. Durchschnittliche Tore
        avg_goals = self.get_average_goals_per_game()
        filepath = os.path.join(output_dir, "average_goals.csv")
        pd.DataFrame([avg_goals]).to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✅ average_goals.csv")
        
        # 5. Tore nach Minute
        goals_minute = self.get_goals_by_minute()
        if len(goals_minute) > 0:
            filepath = os.path.join(output_dir, "goals_by_minute.csv")
            goals_minute.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ goals_by_minute.csv ({len(goals_minute)} Einträge)")
        
        # 6. Strafen
        penalties = self.get_penalty_statistics()
        if len(penalties) > 0:
            filepath = os.path.join(output_dir, "penalty_statistics.csv")
            penalties.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ penalty_statistics.csv ({len(penalties)} Spieler)")
        
        # 7. 7m Effizienz
        siebenmeter = self.get_7m_efficiency()
        if len(siebenmeter) > 0:
            filepath = os.path.join(output_dir, "7m_efficiency.csv")
            siebenmeter.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ 7m_efficiency.csv ({len(siebenmeter)} Spieler)")
        
        # 8. Spieltempo
        tempo = self.get_game_tempo()
        if len(tempo) > 0:
            filepath = os.path.join(output_dir, "game_tempo.csv")
            tempo.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ game_tempo.csv ({len(tempo)} Spiele)")
        
        # 9. Spieler-Performance (alle mit min. 1 Tor)
        performance = self.get_player_performance(min_goals=1)
        if len(performance) > 0:
            filepath = os.path.join(output_dir, "player_performance.csv")
            performance.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ player_performance.csv ({len(performance)} Spieler)")
        
        # 10. Disqualifikationen
        disq = self.get_disqualifications()
        if len(disq) > 0:
            filepath = os.path.join(output_dir, "disqualifications.csv")
            disq.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ disqualifications.csv ({len(disq)} Vorfälle)")
        
        # 11. Spielverläufe für alle Spiele
        for spielnummer in self.df_games['spielnummer'].unique():
            timeline = self.get_goal_timeline(spielnummer)
            if len(timeline) > 0:
                filepath = os.path.join(output_dir, f"game_timeline_{spielnummer}.csv")
                timeline.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✅ game_timeline_*.csv ({len(self.df_games)} Spiele)")
        
        print(f"\n✅ Alle Analysen gespeichert in: {output_dir}\n")
    
    def print_summary(self):
        """Gibt eine umfassende Zusammenfassung aus"""
        print("="*70)
        print("📊 HANDBALL STATISTIKEN - ZUSAMMENFASSUNG")
        print("="*70)
        
        print("\n⚽ DURCHSCHNITTLICHE TORE PRO SPIEL")
        goals = self.get_average_goals_per_game()
        print(f"   Gesamt: {goals['gesamt']} Tore")
        print(f"   Heim: {goals['heim']} Tore | Gast: {goals['gast']} Tore")
        
        print("\n🏠 HEIMVORTEIL")
        home = self.get_home_advantage()
        print(f"   Heim-Siegquote: {home['heim_siegquote']}%")
        print(f"   Auswärts-Siegquote: {home['auswaerts_siegquote']}%")
        print(f"   Gesamt Spiele: {home['gesamt_spiele']}")
        
        print("\n🏆 TOP 10 TORSCHÜTZEN")
        top_scorer = self.get_top_scorer(10)
        for idx, row in top_scorer.iterrows():
            print(f"   {row['name']:35s} ({row['team']:25s}): {int(row['tore'])} Tore")
        
        print("\n📋 TEAM-STATISTIKEN")
        teams = self.get_team_statistics()
        for idx, row in teams.iterrows():
            print(f"\n   {row['team']}")
            print(f"      Spiele: {int(row['spiele'])} (S:{int(row['siege'])} U:{int(row['unentschieden'])} N:{int(row['niederlagen'])})")
            print(f"      Tore: {int(row['tore_geschossen'])}:{int(row['tore_kassiert'])} (Ø {row['tore_pro_spiel']:.1f}:{row['gegentore_pro_spiel']:.1f})")
            print(f"      Tordifferenz: {int(row['tordifferenz']):+d} | Siegquote: {row['siegquote']}%")
        
        print("\n⏱️  SPIELTEMPO")
        tempo = self.get_game_tempo()
        if len(tempo) > 0:
            print(f"   Ø Tore 1. Halbzeit: {tempo['tore_1_halbzeit'].mean():.1f}")
            print(f"   Ø Tore 2. Halbzeit: {tempo['tore_2_halbzeit'].mean():.1f}")
            print(f"   Ø Tempo 1. HZ: {tempo['tempo_1_halbzeit'].mean():.2f} Tore/Min")
            print(f"   Ø Tempo 2. HZ: {tempo['tempo_2_halbzeit'].mean():.2f} Tore/Min")
        
        print("\n⚠️  TOP 5 STRAFEN")
        strafen = self.get_penalty_statistics()
        if len(strafen) > 0:
            for idx, row in strafen.head(5).iterrows():
                print(f"   {row['spieler']:35s} ({row['team']:25s}): {int(row['anzahl_strafen'])} Strafen")
        
        print("\n🎯 7-METER STATISTIK")
        siebenmeter = self.get_7m_efficiency()
        if len(siebenmeter) > 0:
            for idx, row in siebenmeter.head(5).iterrows():
                print(f"   {row['spieler']:35s}: {int(row['verwandelt'])}/{int(row['gesamt'])} ({row['quote']}%)")
        
        print("\n🔴 DISQUALIFIKATIONEN")
        disq = self.get_disqualifications()
        if len(disq) > 0:
            for idx, row in disq.iterrows():
                print(f"   {row['zeit']} - {row['spieler']} ({row['team']})")
        else:
            print("   Keine Disqualifikationen")
        
        print("\n" + "="*70)


# Beispiel-Verwendung
if __name__ == "__main__":
    # Analyzer mit Verzeichnis initialisieren
    analyzer = HandballAnalyzer(data_dir="../data/processed")
    
    # Zusammenfassung ausgeben
    analyzer.print_summary()
    
    # Alle Analysen als CSV speichern
    analyzer.save_all_analyses(output_dir="../data/analysis")