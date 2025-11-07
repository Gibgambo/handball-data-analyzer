import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analyzer import HandballAnalyzer
from visualizer import HandballVisualizer
import os

# Page Config
st.set_page_config(
    page_title="Handball Analytics Dashboard",
    page_icon="🤾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2E86AB;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Cache für Performance
@st.cache_resource
def load_analyzer():
    """Lädt den Analyzer (wird gecacht)"""
    try:
        return HandballAnalyzer()
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return None

@st.cache_resource
def load_visualizer(_analyzer):
    """Lädt den Visualizer (wird gecacht)"""
    return HandballVisualizer(_analyzer)

# Analyzer und Visualizer laden
analyzer = load_analyzer()

if analyzer is None:
    st.stop()

visualizer = load_visualizer(analyzer)

# Sidebar Navigation
st.sidebar.title("🤾 Handball Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Übersicht", "🏆 Top Spieler", "🏠 Heimvorteil", "⚽ Spielverlauf", 
     "🎯 7-Meter Analyse", "📈 Team-Vergleich", "⏱️ Zeitanalyse"]
)

st.sidebar.markdown("---")
st.sidebar.info("Datenstand: " + str(len(analyzer.df_games)) + " Spiele analysiert")

# SEITE: ÜBERSICHT
if page == "📊 Übersicht":
    st.title("🤾 Handball Analytics Dashboard")
    st.markdown("### Willkommen zur Handball-Datenanalyse!")
    
    # Key Metrics in Spalten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Gesamte Spiele",
            value=len(analyzer.df_games)
        )
    
    with col2:
        avg_goals = analyzer.get_average_goals_per_game()
        st.metric(
            label="Ø Tore/Spiel",
            value=f"{avg_goals['gesamt']:.1f}"
        )
    
    with col3:
        home_stats = analyzer.get_home_advantage()
        st.metric(
            label="Heimsiegquote",
            value=f"{home_stats['heim_siegquote']:.1f}%"
        )
    
    with col4:
        total_players = len(analyzer.df_players['name'].unique())
        st.metric(
            label="Spieler gesamt",
            value=total_players
        )
    
    st.markdown("---")
    
    # Zwei-Spalten Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Top 10 Torschützen")
        top_scorer = analyzer.get_top_scorer(10)
        if len(top_scorer) > 0:
            # Formatierte Tabelle
            display_df = top_scorer.copy()
            display_df.columns = ['Spieler', 'Team', 'Tore']
            display_df.index = range(1, len(display_df) + 1)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Keine Torschützen-Daten verfügbar")
    
    with col2:
        st.subheader("📊 Team-Übersicht")
        team_stats = analyzer.get_team_statistics()
        if len(team_stats) > 0:
            display_df = team_stats[['team', 'siegquote', 'tore_geschossen_mean']].copy()
            display_df.columns = ['Team', 'Siegquote (%)', 'Ø Tore']
            display_df = display_df.sort_values('Siegquote (%)', ascending=False)
            display_df.index = range(1, len(display_df) + 1)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Keine Team-Daten verfügbar")
    
    st.markdown("---")
    
    # Heimvorteil Visualisierung
    st.subheader("🏠 Heimvorteil auf einen Blick")
    home_stats = analyzer.get_home_advantage()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Heimsiege", home_stats['heim_siege'])
    with col2:
        st.metric("Auswärtssiege", home_stats['auswaerts_siege'])
    with col3:
        st.metric("Vorteil", f"+{home_stats['heim_siegquote'] - home_stats['auswaerts_siegquote']:.1f}%")

# SEITE: TOP SPIELER
elif page == "🏆 Top Spieler":
    st.title("🏆 Top Spieler Analyse")
    
    # Slider für Anzahl
    top_n = st.slider("Anzahl Top-Spieler", min_value=5, max_value=30, value=15, step=5)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Top {top_n} Torschützen")
        fig = visualizer.plot_top_scorer(top_n, save=False)
        if fig:
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Keine Daten verfügbar")
    
    with col2:
        st.subheader("📋 Detaillierte Liste")
        top_scorer = analyzer.get_top_scorer(top_n)
        if len(top_scorer) > 0:
            display_df = top_scorer.copy()
            display_df.columns = ['Spieler', 'Team', 'Tore']
            display_df['Rang'] = range(1, len(display_df) + 1)
            display_df = display_df[['Rang', 'Spieler', 'Team', 'Tore']]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download Button
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Als CSV herunterladen",
                data=csv,
                file_name="top_scorer.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    # Strafen-Statistik
    st.subheader("🟨 Strafen-Statistik")
    penalties = analyzer.get_penalty_statistics()
    if len(penalties) > 0:
        col1, col2 = st.columns([1, 2])
        with col1:
            display_df = penalties.head(10).copy()
            display_df.columns = ['Spieler', 'Team', 'Strafen']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        with col2:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_penalties = penalties.head(10)
            ax.barh(range(len(top_penalties)), top_penalties['anzahl_strafen'], color='#FF6B6B')
            ax.set_yticks(range(len(top_penalties)))
            ax.set_yticklabels(top_penalties['spieler'])
            ax.set_xlabel('Anzahl 2-Minuten-Strafen', fontweight='bold')
            ax.set_title('Top 10 "Sünder"', fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)
            plt.close()
    else:
        st.info("Keine Strafen-Daten verfügbar")

# SEITE: HEIMVORTEIL
elif page == "🏠 Heimvorteil":
    st.title("🏠 Heimvorteil-Analyse")
    
    home_stats = analyzer.get_home_advantage()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Heimsiege", home_stats['heim_siege'])
    with col2:
        st.metric("Heimsiegquote", f"{home_stats['heim_siegquote']:.1f}%")
    with col3:
        st.metric("Auswärtssiege", home_stats['auswaerts_siege'])
    with col4:
        st.metric("Auswärtssiegquote", f"{home_stats['auswaerts_siegquote']:.1f}%")
    
    st.markdown("---")
    
    # Visualisierung
    fig = visualizer.plot_home_advantage(save=False)
    if fig:
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # Zusätzliche Analyse
    st.subheader("📊 Detaillierte Statistik")
    avg_goals = analyzer.get_average_goals_per_game()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Durchschnitt Heimtore", f"{avg_goals['heim']:.2f}")
        st.metric("Gesamte Spiele", home_stats['gesamt_spiele'])
    with col2:
        st.metric("Durchschnitt Gasttore", f"{avg_goals['gast']:.2f}")
        st.metric("Heimvorteil", f"+{home_stats['heim_siegquote'] - home_stats['auswaerts_siegquote']:.1f}%")
    
    # Erklärung
    st.info("""
    **Interpretation:** Ein Heimvorteil von über 10% gilt als signifikant. 
    Faktoren wie vertraute Umgebung, Publikumsunterstützung und keine Reisestrapazen 
    spielen eine wichtige Rolle.
    """)

# SEITE: SPIELVERLAUF
elif page == "⚽ Spielverlauf":
    st.title("⚽ Spielverlauf-Analyse")
    
    # Spiel auswählen
    spielnummern = analyzer.df_games['spielnummer'].unique()
    
    if len(spielnummern) > 0:
        selected_game = st.selectbox(
            "Wähle ein Spiel:",
            spielnummern,
            format_func=lambda x: f"Spiel #{x}"
        )
        
        # Spielinfo anzeigen
        game_info = analyzer.df_games[analyzer.df_games['spielnummer'] == selected_game].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Heimteam", game_info['heimmannschaft'])
            st.metric("Endstand Heim", int(game_info['endstand_heim']))
        with col2:
            st.metric("Datum", game_info['datum'].strftime('%d.%m.%Y') if pd.notna(game_info['datum']) else "N/A")
            st.metric("Halbzeitstand", f"{int(game_info['halbzeit_heim'])}:{int(game_info['halbzeit_gast'])}")
        with col3:
            st.metric("Gastteam", game_info['gastmannschaft'])
            st.metric("Endstand Gast", int(game_info['endstand_gast']))
        
        st.markdown("---")
        
        # Timeline Plot
        fig = visualizer.plot_game_timeline(selected_game, save=False)
        if fig:
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Keine Timeline-Daten für dieses Spiel verfügbar")
        
        st.markdown("---")
        
        # Ereignis-Tabelle
        st.subheader("📋 Alle Spielereignisse")
        timeline = analyzer.get_goal_timeline(selected_game)
        if len(timeline) > 0:
            display_df = timeline.copy()
            display_df['minute'] = display_df['minute'].round(1)
            display_df.columns = ['Minute', 'Team', 'Stand Heim', 'Stand Gast', 'Spieler', 'Ereignis']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("Keine Ereignis-Daten verfügbar")
    else:
        st.warning("Keine Spiele verfügbar")

# SEITE: 7-METER ANALYSE
elif page == "🎯 7-Meter Analyse":
    st.title("🎯 7-Meter Effizienz-Analyse")
    
    efficiency = analyzer.get_7m_efficiency()
    
    if len(efficiency) > 0:
        # Gesamtstatistik
        total_7m = efficiency['gesamt'].sum()
        total_scored = efficiency['verwandelt'].sum()
        avg_efficiency = (total_scored / total_7m * 100) if total_7m > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamt 7-Meter", int(total_7m))
        with col2:
            st.metric("Verwandelt", int(total_scored))
        with col3:
            st.metric("Durchschnittliche Quote", f"{avg_efficiency:.1f}%")
        
        st.markdown("---")
        
        # Visualisierung
        fig = visualizer.plot_7m_efficiency(save=False)
        if fig:
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        
        # Detaillierte Tabelle
        st.subheader("📊 Alle 7-Meter Schützen")
        
        # Filter nach Mindestanzahl
        min_attempts = st.slider("Mindestanzahl 7-Meter", 1, 10, 3)
        filtered_eff = efficiency[efficiency['gesamt'] >= min_attempts].copy()
        
        if len(filtered_eff) > 0:
            display_df = filtered_eff.copy()
            display_df.columns = ['Spieler', 'Team', 'Verwandelt', 'Gesamt', 'Quote (%)']
            display_df = display_df.sort_values('Quote (%)', ascending=False)
            
            # Farbige Anzeige
            def color_quote(val):
                if val >= 80:
                    return 'background-color: #90EE90'
                elif val >= 60:
                    return 'background-color: #FFD700'
                else:
                    return 'background-color: #FFB6C1'
            
            styled_df = display_df.style.applymap(color_quote, subset=['Quote (%)'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Keine Spieler mit mindestens {min_attempts} 7-Meter-Versuchen")
    else:
        st.warning("Keine 7-Meter-Daten verfügbar")

# SEITE: TEAM-VERGLEICH
elif page == "📈 Team-Vergleich":
    st.title("📈 Team-Vergleich")
    
    team_stats = analyzer.get_team_statistics()
    
    if len(team_stats) > 0:
        # Team-Auswahl für Direktvergleich
        st.subheader("⚔️ Direktvergleich")
        col1, col2 = st.columns(2)
        
        teams = team_stats['team'].tolist()
        with col1:
            team1 = st.selectbox("Team 1", teams, index=0)
        with col2:
            team2 = st.selectbox("Team 2", teams, index=min(1, len(teams)-1))
        
        if team1 != team2:
            t1_stats = team_stats[team_stats['team'] == team1].iloc[0]
            t2_stats = team_stats[team_stats['team'] == team2].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    f"{team1} - Siegquote",
                    f"{t1_stats['siegquote']:.1f}%",
                    delta=f"{t1_stats['siegquote'] - t2_stats['siegquote']:.1f}%"
                )
            with col2:
                st.metric(
                    f"{team1} - Ø Tore",
                    f"{t1_stats['tore_geschossen_mean']:.1f}",
                    delta=f"{t1_stats['tore_geschossen_mean'] - t2_stats['tore_geschossen_mean']:.1f}"
                )
            with col3:
                tordiff1 = t1_stats['tore_geschossen_sum'] - t1_stats['tore_kassiert_sum']
                tordiff2 = t2_stats['tore_geschossen_sum'] - t2_stats['tore_kassiert_sum']
                st.metric(
                    f"{team1} - Tordifferenz",
                    f"{tordiff1:.0f}",
                    delta=f"{tordiff1 - tordiff2:.0f}"
                )
        
        st.markdown("---")
        
        # Gesamtvergleich
        st.subheader("🏆 Alle Teams im Vergleich")
        fig = visualizer.plot_team_comparison(save=False)
        if fig:
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        
        # Ranking-Tabelle
        st.subheader("📊 Team-Rankings")
        display_df = team_stats.copy()
        display_df['tordifferenz'] = (display_df['tore_geschossen_sum'] - 
                                      display_df['tore_kassiert_sum']).round(0)
        display_df = display_df.sort_values('siegquote', ascending=False)
        
        show_df = display_df[['team', 'siegquote', 'tore_geschossen_mean', 
                              'tore_kassiert_mean', 'tordifferenz']].copy()
        show_df.columns = ['Team', 'Siegquote (%)', 'Ø Tore für', 'Ø Tore gegen', 'Tordifferenz']
        show_df.index = range(1, len(show_df) + 1)
        
        st.dataframe(show_df, use_container_width=True)
    else:
        st.warning("Keine Team-Daten verfügbar")

# SEITE: ZEITANALYSE
elif page == "⏱️ Zeitanalyse":
    st.title("⏱️ Zeitanalyse - Tore nach Spielminuten")
    
    st.subheader("🔥 Heatmap: Wann fallen die Tore?")
    fig = visualizer.plot_goals_heatmap(save=False)
    if fig:
        st.pyplot(fig)
        plt.close()
    else:
        st.warning("Keine Heatmap-Daten verfügbar")
    
    st.markdown("---")
    
    # Spieltempo-Analyse
    st.subheader("⚡ Spieltempo - 1. vs. 2. Halbzeit")
    tempo = analyzer.get_game_tempo()
    
    if len(tempo) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            avg_1st = tempo['tore_1_halbzeit'].mean()
            avg_2nd = tempo['tore_2_halbzeit'].mean()
            st.metric("Ø Tore 1. Halbzeit", f"{avg_1st:.1f}")
            st.metric("Ø Tore 2. Halbzeit", f"{avg_2nd:.1f}")
        
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(['1. Halbzeit', '2. Halbzeit'], 
                   [avg_1st, avg_2nd],
                   color=['#2E86AB', '#A23B72'])
            ax.set_ylabel('Durchschnittliche Tore', fontweight='bold')
            ax.set_title('Halbzeitvergleich', fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
            plt.close()
        
        st.markdown("---")
        
        # Detaillierte Tempo-Tabelle
        st.subheader("📋 Spieltempo Details")
        display_tempo = tempo.copy()
        display_tempo.columns = ['Spielnummer', 'Tore 1. HZ', 'Tore 2. HZ', 
                                'Tempo 1. HZ', 'Tempo 2. HZ']
        display_tempo['Tempo 1. HZ'] = display_tempo['Tempo 1. HZ'].round(2)
        display_tempo['Tempo 2. HZ'] = display_tempo['Tempo 2. HZ'].round(2)
        st.dataframe(display_tempo, use_container_width=True, hide_index=True)
    else:
        st.warning("Keine Tempo-Daten verfügbar")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🤾 Handball Analytics Dashboard | Powered by Streamlit</p>
    </div>
""", unsafe_allow_html=True)