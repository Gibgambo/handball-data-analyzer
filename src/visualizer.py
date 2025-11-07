import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class HandballVisualizer:
    def __init__(self, analyzer=None, data_dir="../data/processed"):
        """Initialisiert den Visualizer mit einem Analyzer"""
        if analyzer is None:
            from analyzer import HandballAnalyzer
            self.analyzer = HandballAnalyzer(data_dir=data_dir)
        else:
            self.analyzer = analyzer
            
        self.output_dir = "../data/visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def plot_top_scorer(self, top_n=15, save=True):
        """Barplot: Top Torschützen"""
        top_scorer = self.analyzer.get_top_scorer(top_n)
        
        if len(top_scorer) == 0:
            print("⚠️  Keine Torschützen-Daten verfügbar")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Horizontaler Barplot
        bars = ax.barh(range(len(top_scorer)), top_scorer['tore'], color='steelblue')
        
        # Labels mit Team
        labels = [f"{row['name']}\n({row['team']})" for _, row in top_scorer.iterrows()]
        ax.set_yticks(range(len(top_scorer)))
        ax.set_yticklabels(labels, fontsize=10)
        
        # Werte auf Balken
        for i, (bar, tore) in enumerate(zip(bars, top_scorer['tore'])):
            ax.text(tore + 0.3, i, str(int(tore)), va='center', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Anzahl Tore', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Torschützen', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()  # Höchste oben
        
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, 'top_scorer.png'), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: top_scorer.png")
            plt.close(fig)  # Figur schließen um Speicher freizugeben
        
        return fig
    
    def plot_game_timeline(self, spielnummer=None, save=True):
        """Lineplot: Spielverlauf über Zeit"""
        timeline = self.analyzer.get_goal_timeline(spielnummer)
        
        if len(timeline) == 0:
            print("⚠️  Keine Timeline-Daten verfügbar")
            return None
        
        # Spielinfo holen
        game_info = self.analyzer.df_games[
            self.analyzer.df_games['spielnummer'] == spielnummer
        ].iloc[0]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Heim- und Gasttore plotten
        ax.plot(timeline['minute'], timeline['stand_heim'], 
                marker='o', linewidth=2.5, markersize=8, 
                label=game_info['heimmannschaft'], color='#2E86AB')
        
        ax.plot(timeline['minute'], timeline['stand_gast'], 
                marker='s', linewidth=2.5, markersize=8, 
                label=game_info['gastmannschaft'], color='#A23B72')
        
        # Halbzeitlinie
        ax.axvline(x=30, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Halbzeit')
        
        ax.set_xlabel('Spielminute', fontsize=12, fontweight='bold')
        ax.set_ylabel('Tore', fontsize=12, fontweight='bold')
        ax.set_title(f'Spielverlauf - {game_info["heimmannschaft"]} vs {game_info["gastmannschaft"]}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = f'game_timeline_{spielnummer}.png'
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: {filename}")
            plt.close(fig)  # Figur schließen
        
        return fig
    
    def plot_goals_heatmap(self, save=True):
        """Heatmap: Tore nach Spielminuten-Intervallen"""
        heatmap_data = self.analyzer.get_goals_by_minute()
        
        if len(heatmap_data) == 0:
            print("⚠️  Keine Heatmap-Daten verfügbar")
            return None
        
        # Pivot für Heatmap
        pivot = heatmap_data.pivot_table(
            index='team', 
            columns='intervall', 
            values='anzahl_tore', 
            fill_value=0
        )
        
        fig, ax = plt.subplots(figsize=(16, 6))
        
        # Heatmap
        sns.heatmap(pivot, annot=True, fmt='g', cmap='YlOrRd', 
                    cbar_kws={'label': 'Anzahl Tore'},
                    linewidths=0.5, linecolor='white',
                    ax=ax)
        
        ax.set_xlabel('Spielminute (Intervall)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Team', fontsize=12, fontweight='bold')
        ax.set_title('Torverteilung nach Spielzeit', fontsize=16, fontweight='bold', pad=20)
        
        # X-Achsen-Labels formatieren
        current_labels = [int(col) for col in pivot.columns]
        new_labels = [f"{min}-{min+5}'" for min in current_labels]
        ax.set_xticklabels(new_labels, rotation=45)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, 'goals_heatmap.png'), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: goals_heatmap.png")
            plt.close(fig)  # Figur schließen
        
        return fig
    
    def plot_home_advantage(self, save=True):
        """Pie Chart: Heimvorteil"""
        home_stats = self.analyzer.get_home_advantage()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie Chart
        sizes = [home_stats['heim_siege'], home_stats['auswaerts_siege']]
        labels = [f"Heimsiege\n({home_stats['heim_siegquote']}%)", 
                  f"Auswärtssiege\n({home_stats['auswaerts_siegquote']}%)"]
        colors = ['#2E86AB', '#A23B72']
        explode = (0.05, 0.05)
        
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.0f%%',
                shadow=True, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Siegverteilung Heim vs. Auswärts', fontsize=14, fontweight='bold', pad=20)
        
        # Bar Chart
        categories = ['Heim', 'Auswärts']
        siegquoten = [home_stats['heim_siegquote'], home_stats['auswaerts_siegquote']]
        
        bars = ax2.bar(categories, siegquoten, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Werte auf Balken
        for bar, quote in zip(bars, siegquoten):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{quote:.1f}%', ha='center', va='bottom', 
                    fontsize=12, fontweight='bold')
        
        ax2.set_ylabel('Siegquote (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Heimvorteil-Statistik', fontsize=14, fontweight='bold', pad=20)
        ax2.set_ylim(0, 100)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, 'home_advantage.png'), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: home_advantage.png")
            plt.close(fig)  # Figur schließen
        
        return fig
    
    def plot_team_comparison(self, save=True):
        """Vergleich Team-Statistiken"""
        team_stats = self.analyzer.get_team_statistics()
        
        if len(team_stats) == 0:
            print("⚠️  Keine Team-Daten verfügbar")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        teams = team_stats['team']
        
        # 1. Durchschnittliche Tore geschossen (KORRIGIERT!)
        ax1 = axes[0, 0]
        avg_scored = team_stats['tore_pro_spiel']  # NICHT tore_geschossen_mean!
        ax1.barh(teams, avg_scored, color='forestgreen', alpha=0.7)
        ax1.set_xlabel('Ø Tore geschossen', fontweight='bold')
        ax1.set_title('Durchschnittliche Tore pro Spiel', fontweight='bold', fontsize=12)
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()
        
        # 2. Durchschnittliche Tore kassiert (KORRIGIERT!)
        ax2 = axes[0, 1]
        avg_conceded = team_stats['gegentore_pro_spiel']  # NICHT tore_kassiert_mean!
        ax2.barh(teams, avg_conceded, color='crimson', alpha=0.7)
        ax2.set_xlabel('Ø Tore kassiert', fontweight='bold')
        ax2.set_title('Durchschnittliche Gegentore pro Spiel', fontweight='bold', fontsize=12)
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()
        
        # 3. Siegquote
        ax3 = axes[1, 0]
        siegquote = team_stats['siegquote']
        ax3.barh(teams, siegquote, color='gold', alpha=0.7)
        ax3.set_xlabel('Siegquote (%)', fontweight='bold')
        ax3.set_title('Siegquote nach Team', fontweight='bold', fontsize=12)
        ax3.set_xlim(0, 100)
        ax3.grid(axis='x', alpha=0.3)
        ax3.invert_yaxis()
        
        # 4. Tordifferenz (KORRIGIERT!)
        ax4 = axes[1, 1]
        tordiff = team_stats['tordifferenz']  # Direkt verwenden!
        colors = ['green' if x > 0 else 'red' for x in tordiff]
        ax4.barh(teams, tordiff, color=colors, alpha=0.7)
        ax4.axvline(x=0, color='black', linewidth=0.8)
        ax4.set_xlabel('Tordifferenz', fontweight='bold')
        ax4.set_title('Gesamt-Tordifferenz', fontweight='bold', fontsize=12)
        ax4.grid(axis='x', alpha=0.3)
        ax4.invert_yaxis()
        
        plt.suptitle('Team-Vergleich', fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, 'team_comparison.png'), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: team_comparison.png")
            plt.close(fig)  # Figur schließen
        
        return fig
    
    def plot_7m_efficiency(self, save=True):
        """7-Meter Effizienz"""
        efficiency = self.analyzer.get_7m_efficiency()
        
        if len(efficiency) == 0:
            print("⚠️  Keine 7m-Daten verfügbar")
            return None
        
        # Top 10
        top_efficiency = efficiency.head(10)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = range(len(top_efficiency))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], top_efficiency['verwandelt'], 
               width, label='Verwandelt', color='seagreen', alpha=0.8)
        
        # KORRIGIERT: fehlwuerfe Spalte direkt verwenden!
        fehlwuerfe = top_efficiency['fehlwuerfe']
        ax.bar([i + width/2 for i in x], fehlwuerfe, 
               width, label='Fehlversuche', color='lightcoral', alpha=0.8)
        
        # Labels
        labels = [f"{row['spieler']}\n{row['quote']:.0f}%" 
                 for _, row in top_efficiency.iterrows()]
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        
        ax.set_ylabel('Anzahl 7-Meter', fontweight='bold')
        ax.set_title('7-Meter Effizienz - Top Schützen', fontsize=14, fontweight='bold', pad=20)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, '7m_efficiency.png'), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: 7m_efficiency.png")
        
        return fig
    
    def plot_penalty_statistics(self, save=True):
        """Strafen-Visualisierung"""
        penalties = self.analyzer.get_penalty_statistics()
        
        if len(penalties) == 0:
            print("⚠️  Keine Strafen-Daten verfügbar")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        top_penalties = penalties.head(10)
        
        bars = ax.barh(range(len(top_penalties)), top_penalties['anzahl_strafen'], 
                      color='#FF6B6B', alpha=0.7)
        
        # Labels
        labels = [f"{row['spieler']}\n({row['team']})" 
                 for _, row in top_penalties.iterrows()]
        ax.set_yticks(range(len(top_penalties)))
        ax.set_yticklabels(labels, fontsize=10)
        
        # Werte
        for i, (bar, strafen) in enumerate(zip(bars, top_penalties['anzahl_strafen'])):
            ax.text(strafen + 0.1, i, str(int(strafen)), 
                   va='center', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Anzahl 2-Minuten-Strafen', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 "Sünder" - 2-Minuten-Strafen', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()
        
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, 'penalty_statistics.png'), 
                       dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: penalty_statistics.png")
        
        return fig
    
    def plot_game_tempo(self, save=True):
        """Spieltempo visualisieren"""
        tempo = self.analyzer.get_game_tempo()
        
        if len(tempo) == 0:
            print("⚠️  Keine Tempo-Daten verfügbar")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. Tore pro Halbzeit
        avg_1st = tempo['tore_1_halbzeit'].mean()
        avg_2nd = tempo['tore_2_halbzeit'].mean()
        
        bars = ax1.bar(['1. Halbzeit', '2. Halbzeit'], 
                      [avg_1st, avg_2nd],
                      color=['#2E86AB', '#A23B72'], alpha=0.8)
        
        for bar, val in zip(bars, [avg_1st, avg_2nd]):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}', ha='center', va='bottom', 
                    fontsize=12, fontweight='bold')
        
        ax1.set_ylabel('Durchschnittliche Tore', fontweight='bold')
        ax1.set_title('Tore pro Halbzeit', fontweight='bold', fontsize=14)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Tempo (Tore/Minute)
        tempo_1st = tempo['tempo_1_halbzeit'].mean()
        tempo_2nd = tempo['tempo_2_halbzeit'].mean()
        
        bars = ax2.bar(['1. Halbzeit', '2. Halbzeit'], 
                      [tempo_1st, tempo_2nd],
                      color=['#2E86AB', '#A23B72'], alpha=0.8)
        
        for bar, val in zip(bars, [tempo_1st, tempo_2nd]):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.2f}', ha='center', va='bottom', 
                    fontsize=12, fontweight='bold')
        
        ax2.set_ylabel('Tore pro Minute', fontweight='bold')
        ax2.set_title('Spieltempo', fontweight='bold', fontsize=14)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.suptitle('Spieltempo-Analyse', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(self.output_dir, 'game_tempo.png'), dpi=300, bbox_inches='tight')
            print(f"✅ Gespeichert: game_tempo.png")
        
        return fig
    
    def create_all_visualizations(self):
        """Erstellt alle Visualisierungen auf einmal"""
        print("\n🎨 Erstelle Visualisierungen...\n")
        
        self.plot_top_scorer()
        self.plot_home_advantage()
        self.plot_team_comparison()
        self.plot_7m_efficiency()
        self.plot_penalty_statistics()
        self.plot_game_tempo()
        
        # Heatmap nur wenn Daten vorhanden
        heatmap_data = self.analyzer.get_goals_by_minute()
        if len(heatmap_data) > 0:
            self.plot_goals_heatmap()
        
        # Timeline für alle Spiele
        for spielnummer in self.analyzer.df_games['spielnummer'].unique():
            self.plot_game_timeline(spielnummer)
        
        print(f"\n✅ Alle Visualisierungen erstellt in {self.output_dir}")


if __name__ == "__main__":
    # Visualizer mit Standard-Datenverzeichnis
    visualizer = HandballVisualizer(data_dir="../data/processed")
    visualizer.create_all_visualizations()
    
    # Optional: Plots anzeigen
    # plt.show()