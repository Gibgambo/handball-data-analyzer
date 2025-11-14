import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Handball Analytics Dashboard",
    page_icon="🤾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verbessertes Custom CSS
st.markdown("""
    <style>
    /* Hauptbereich */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Metric Cards mit Gradient und besserer Lesbarkeit */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetric"] label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #e0e0e0 !important;
    }
    
    /* Alternative: Verschiedene Farben für verschiedene Metrics */
    div[data-testid="column"]:nth-child(1) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    div[data-testid="column"]:nth-child(2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    div[data-testid="column"]:nth-child(3) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    div[data-testid="column"]:nth-child(4) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    /* Überschriften */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        color: #2E86AB;
        border-bottom: 3px solid #2E86AB;
        padding-bottom: 10px;
        margin-top: 2rem;
    }
    
    h3 {
        color: #444;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        transition: all 0.3s;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    /* Tabellen */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Info-Boxen */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Download Buttons */
    .stDownloadButton button {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Slider */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        border-radius: 8px;
    }
    
    /* Trennlinien */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Card-Style für Markdown-Bereiche */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Animation für Hover-Effekte */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    [data-testid="stMetric"]:hover {
        animation: pulse 0.5s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

# Cache für Performance
@st.cache_resource
def load_analyzer(data_dir=None):
    if data_dir is None:
        # Versuche verschiedene Pfade
        possible_paths = [
            Path("data/processed"),  # Streamlit Cloud
            Path("../data/processed"),  # Lokal
            Path(__file__).parent.parent / "data" / "processed"  # Absolut
        ]
        
        for path in possible_paths:
            if path.exists():
                data_dir = str(path)
                break
        else:
            data_dir = "data/processed"  # Fallback
    
    try:
        from analyzer import HandballAnalyzer
        return HandballAnalyzer(data_dir=data_dir)
    except FileNotFoundError:
        st.error(f"❌ Daten nicht gefunden in: {data_dir}")
        return None

@st.cache_resource
def load_visualizer(_analyzer):
    """Lädt den Visualizer (wird gecacht)"""
    from visualizer import HandballVisualizer
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
     "🎯 7-Meter Analyse", "📈 Team-Vergleich", "⏱️ Zeitanalyse", "📋 Alle Statistiken"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"📊 **Datenstand**\n\n{len(analyzer.df_games)} Spiele analysiert\n\n{len(analyzer.df_players.groupby(['name', 'team']).size())} Spieler")

# SEITE: ÜBERSICHT
if page == "📊 Übersicht":
    st.title("🤾 Handball Analytics Dashboard")
    st.markdown("### Willkommen zur umfassenden Handball-Datenanalyse!")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎮 Gesamte Spiele", len(analyzer.df_games))
    
    with col2:
        avg_goals = analyzer.get_average_goals_per_game()
        st.metric("⚽ Ø Tore/Spiel", f"{avg_goals['gesamt']:.1f}")
    
    with col3:
        home_stats = analyzer.get_home_advantage()
        st.metric("🏠 Heimsiegquote", f"{home_stats['heim_siegquote']:.1f}%")
    
    with col4:
        total_players = len(analyzer.df_players.groupby(['name', 'team']).size())
        st.metric("👥 Spieler gesamt", total_players)
    
    st.markdown("---")
    
    # Drei-Spalten Layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎯 Top 5 Torschützen")
        top_scorer = analyzer.get_top_scorer(5)
        if len(top_scorer) > 0:
            for idx, row in top_scorer.iterrows():
                st.markdown(f"**{idx+1}.** {row['name']} ({row['team'][:20]}...) - **{int(row['tore'])}** Tore")
        else:
            st.warning("Keine Daten verfügbar")
    
    with col2:
        st.subheader("🏆 Team-Rankings")
        team_stats = analyzer.get_team_statistics()
        if len(team_stats) > 0:
            for idx, row in team_stats.head(5).iterrows():
                st.markdown(f"**{idx+1}.** {row['team'][:20]}... - **{row['siegquote']:.1f}%** Siegquote")
        else:
            st.warning("Keine Team-Daten verfügbar")
    
    with col3:
        st.subheader("⚠️ Top 5 Strafen")
        penalties = analyzer.get_penalty_statistics()
        if len(penalties) > 0:
            for idx, row in penalties.head(5).iterrows():
                st.markdown(f"**{idx+1}.** {row['spieler'][:20]}... - **{int(row['anzahl_strafen'])}** Strafen")
        else:
            st.info("Keine Strafen")
    
    st.markdown("---")
    
    # Heimvorteil auf einen Blick
    st.subheader("🏠 Heimvorteil auf einen Blick")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Heimsiege", home_stats['heim_siege'])
    with col2:
        st.metric("Heimsiegquote", f"{home_stats['heim_siegquote']:.1f}%")
    with col3:
        st.metric("Auswärtssiege", home_stats['auswaerts_siege'])
    with col4:
        vorteil = home_stats['heim_siegquote'] - home_stats['auswaerts_siegquote']
        st.metric("Vorteil", f"{vorteil:+.1f}%", delta=f"{vorteil:.1f}%")
    
    st.markdown("---")
    
    # Visualisierung
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Heimvorteil")
        fig = visualizer.plot_home_advantage(save=False)
        if fig:
            st.pyplot(fig)
            plt.close(fig)
    
    with col2:
        st.subheader("⏱️ Spieltempo")
        fig = visualizer.plot_game_tempo(save=False)
        if fig:
            st.pyplot(fig)
            plt.close(fig)

# SEITE: TOP SPIELER
elif page == "🏆 Top Spieler":
    st.title("🏆 Top Spieler Analyse")
    
    top_n = st.slider("Anzahl Top-Spieler", min_value=5, max_value=50, value=15, step=5)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🎯 Top {top_n} Torschützen")
        fig = visualizer.plot_top_scorer(top_n, save=False)
        if fig:
            st.pyplot(fig)
            plt.close(fig)
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
            st.dataframe(display_df, width='stretch', hide_index=True)
            
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
            st.dataframe(display_df, width='stretch', hide_index=True)
        with col2:
            fig = visualizer.plot_penalty_statistics(save=False)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
    else:
        st.info("Keine Strafen-Daten verfügbar")
    
    st.markdown("---")
    
    # Disqualifikationen
    st.subheader("🔴 Disqualifikationen")
    disq = analyzer.get_disqualifications()
    if len(disq) > 0:
        display_df = disq.copy()
        display_df.columns = ['Zeit', 'Team', 'Spieler', 'Spielnummer']
        st.dataframe(display_df, width='stretch', hide_index=True)
    else:
        st.success("✅ Keine Disqualifikationen - Faire Spiele!")

# SEITE: HEIMVORTEIL
elif page == "🏠 Heimvorteil":
    st.title("🏠 Heimvorteil-Analyse")
    
    home_stats = analyzer.get_home_advantage()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏠 Heimsiege", home_stats['heim_siege'])
    with col2:
        st.metric("📊 Heimsiegquote", f"{home_stats['heim_siegquote']:.1f}%")
    with col3:
        st.metric("✈️ Auswärtssiege", home_stats['auswaerts_siege'])
    with col4:
        st.metric("📈 Auswärtssiegquote", f"{home_stats['auswaerts_siegquote']:.1f}%")
    
    st.markdown("---")
    
    fig = visualizer.plot_home_advantage(save=False)
    if fig:
        st.pyplot(fig)
        plt.close(fig)
    
    st.markdown("---")
    
    st.subheader("📊 Detaillierte Statistik")
    avg_goals = analyzer.get_average_goals_per_game()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⚽ Durchschnitt Heimtore", f"{avg_goals['heim']:.2f}")
    with col2:
        st.metric("🎯 Durchschnitt Gasttore", f"{avg_goals['gast']:.2f}")
    with col3:
        vorteil = home_stats['heim_siegquote'] - home_stats['auswaerts_siegquote']
        st.metric("📈 Heimvorteil", f"{vorteil:+.1f}%")
    
    st.info("""
    **💡 Interpretation:** Ein Heimvorteil von über 10% gilt als signifikant. 
    Faktoren wie vertraute Umgebung, Publikumsunterstützung und keine Reisestrapazen 
    spielen eine wichtige Rolle.
    """)

# SEITE: SPIELVERLAUF
elif page == "⚽ Spielverlauf":
    st.title("⚽ Spielverlauf-Analyse")
    
    spielnummern = analyzer.df_games['spielnummer'].unique()
    
    if len(spielnummern) > 0:
        # Spiel-Selector mit mehr Infos
        game_options = {}
        for spielnr in spielnummern:
            game = analyzer.df_games[analyzer.df_games['spielnummer'] == spielnr].iloc[0]
            label = f"Spiel #{spielnr}: {game['heimmannschaft']} vs {game['gastmannschaft']} ({game['endstand_heim']}:{game['endstand_gast']})"
            game_options[label] = spielnr
        
        selected_label = st.selectbox("🎮 Wähle ein Spiel:", list(game_options.keys()))
        selected_game = game_options[selected_label]
        
        # Spielinfo
        game_info = analyzer.df_games[analyzer.df_games['spielnummer'] == selected_game].iloc[0]
        
        # Info-Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🏠 Heimteam")
            st.metric(game_info['heimmannschaft'], f"{int(game_info['endstand_heim'])} Tore")
            st.caption(f"Halbzeit: {int(game_info['halbzeit_heim'])}")
        
        with col2:
            st.markdown("### 📅 Spielinfo")
            datum_str = game_info['datum'].strftime('%d.%m.%Y') if pd.notna(game_info['datum']) else "N/A"
            st.metric("Datum", datum_str)
            st.caption(f"📍 {game_info['spielort']}")
        
        with col3:
            st.markdown("### ✈️ Gastteam")
            st.metric(game_info['gastmannschaft'], f"{int(game_info['endstand_gast'])} Tore")
            st.caption(f"Halbzeit: {int(game_info['halbzeit_gast'])}")
        
        st.markdown("---")
        
        # Timeline
        st.subheader("📈 Spielverlauf")
        fig = visualizer.plot_game_timeline(selected_game, save=False)
        if fig:
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("Keine Timeline-Daten verfügbar")
        
        st.markdown("---")
        
        # Ereignis-Tabelle
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Spielereignisse - Tore")
            timeline = analyzer.get_goal_timeline(selected_game)
            if len(timeline) > 0:
                display_df = timeline.copy()
                display_df['minute'] = display_df['minute'].round(1)
                display_df.columns = ['Minute', 'Team', 'Stand Heim', 'Stand Gast', 'Spieler', 'Ereignis']
                st.dataframe(display_df, width='stretch', hide_index=True, height=400)
            else:
                st.info("Keine Ereignis-Daten verfügbar")
        
        with col2:
            st.subheader("⚠️ Strafen & Auszeiten")
            # Alle Events für dieses Spiel
            game_events = analyzer.df_events[analyzer.df_events['spielnummer'] == selected_game].copy()
            penalties_disq = game_events[game_events['ereignis'].isin(['2-Minuten', 'Disqualifikation', 'Auszeit'])]
            
            if len(penalties_disq) > 0:
                display_df = penalties_disq[['zeit', 'team', 'ereignis', 'spieler']].copy()
                display_df.columns = ['Zeit', 'Team', 'Ereignis', 'Spieler']
                display_df['Spieler'] = display_df['Spieler'].fillna('-')
                st.dataframe(display_df, width='stretch', hide_index=True, height=400)
            else:
                st.info("Keine Strafen oder Auszeiten")
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
        total_missed = efficiency['fehlwuerfe'].sum()
        avg_efficiency = (total_scored / total_7m * 100) if total_7m > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Gesamt 7-Meter", int(total_7m))
        with col2:
            st.metric("✅ Verwandelt", int(total_scored))
        with col3:
            st.metric("❌ Fehlwürfe", int(total_missed))
        with col4:
            st.metric("📊 Durchschnitt", f"{avg_efficiency:.1f}%")
        
        st.markdown("---")
        
        # Visualisierung
        fig = visualizer.plot_7m_efficiency(save=False)
        if fig:
            st.pyplot(fig)
            plt.close(fig)
        
        st.markdown("---")
        
        # Tabelle mit Filter
        st.subheader("📊 Alle 7-Meter Schützen")
        min_attempts = st.slider("Mindestanzahl 7-Meter", 1, 10, 1)
        filtered_eff = efficiency[efficiency['gesamt'] >= min_attempts].copy()
        
        if len(filtered_eff) > 0:
            display_df = filtered_eff.copy()
            display_df.columns = ['Spieler', 'Team', 'Verwandelt', 'Fehlwürfe', 'Gesamt', 'Quote (%)']
            display_df = display_df.sort_values('Quote (%)', ascending=False)
            
            # Styling
            def color_quote(val):
                if val >= 80:
                    return 'background-color: #90EE90'
                elif val >= 60:
                    return 'background-color: #FFD700'
                else:
                    return 'background-color: #FFB6C1'
            
            styled_df = display_df.style.applymap(color_quote, subset=['Quote (%)'])
            st.dataframe(styled_df, width='stretch', hide_index=True)
        else:
            st.warning(f"Keine Spieler mit mindestens {min_attempts} 7-Meter-Versuchen")
    else:
        st.warning("Keine 7-Meter-Daten verfügbar")

# SEITE: TEAM-VERGLEICH
elif page == "📈 Team-Vergleich":
    st.title("📈 Team-Vergleich")
    
    team_stats = analyzer.get_team_statistics()
    
    if len(team_stats) > 0:
        # Direktvergleich
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
                delta = t1_stats['siegquote'] - t2_stats['siegquote']
                st.metric(
                    f"{team1[:15]}... - Siegquote",
                    f"{t1_stats['siegquote']:.1f}%",
                    delta=f"{delta:.1f}%"
                )
            with col2:
                delta = t1_stats['tore_pro_spiel'] - t2_stats['tore_pro_spiel']
                st.metric(
                    f"{team1[:15]}... - Ø Tore",
                    f"{t1_stats['tore_pro_spiel']:.1f}",
                    delta=f"{delta:.1f}"
                )
            with col3:
                delta = t1_stats['tordifferenz'] - t2_stats['tordifferenz']
                st.metric(
                    f"{team1[:15]}... - Tordifferenz",
                    f"{int(t1_stats['tordifferenz'])}",
                    delta=f"{int(delta)}"
                )
        
        st.markdown("---")
        
        # Gesamtvergleich
        st.subheader("🏆 Alle Teams im Vergleich")
        fig = visualizer.plot_team_comparison(save=False)
        if fig:
            st.pyplot(fig)
            plt.close(fig)
        
        st.markdown("---")
        
        # Ranking
        st.subheader("📊 Team-Rankings")
        display_df = team_stats.copy()
        display_df = display_df.sort_values('siegquote', ascending=False)
        
        show_df = display_df[['team', 'spiele', 'siege', 'niederlagen', 'siegquote', 
                              'tore_pro_spiel', 'gegentore_pro_spiel', 'tordifferenz']].copy()
        show_df.columns = ['Team', 'Spiele', 'Siege', 'Niederlagen', 'Siegquote (%)', 
                          'Ø Tore für', 'Ø Tore gegen', 'Tordifferenz']
        show_df['Tordifferenz'] = show_df['Tordifferenz'].astype(int)
        show_df.index = range(1, len(show_df) + 1)
        
        st.dataframe(show_df, width='stretch')
    else:
        st.warning("Keine Team-Daten verfügbar")

# SEITE: ZEITANALYSE
elif page == "⏱️ Zeitanalyse":
    st.title("⏱️ Zeitanalyse - Tore nach Spielminuten")
    
    st.subheader("🔥 Heatmap: Wann fallen die Tore?")
    fig = visualizer.plot_goals_heatmap(save=False)
    if fig:
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("Keine Heatmap-Daten verfügbar")
    
    st.markdown("---")
    
    # Spieltempo
    st.subheader("⚡ Spieltempo - 1. vs. 2. Halbzeit")
    tempo = analyzer.get_game_tempo()
    
    if len(tempo) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            avg_1st = tempo['tore_1_halbzeit'].mean()
            avg_2nd = tempo['tore_2_halbzeit'].mean()
            st.metric("Ø Tore 1. Halbzeit", f"{avg_1st:.1f}")
            st.metric("Ø Tore 2. Halbzeit", f"{avg_2nd:.1f}")
            
            diff = avg_2nd - avg_1st
            if diff > 0:
                st.success(f"✅ 2. Halbzeit ist torreichter (+{diff:.1f} Tore)")
            elif diff < 0:
                st.info(f"📊 1. Halbzeit ist torreichter ({diff:.1f} Tore)")
            else:
                st.warning("⚖️ Beide Halbzeiten gleich torreich")
        
        with col2:
            fig = visualizer.plot_game_tempo(save=False)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
        
        st.markdown("---")
        
        # Tempo-Tabelle
        st.subheader("📋 Spieltempo Details")
        display_tempo = tempo.copy()
        display_tempo.columns = ['Spielnummer', 'Tore 1. HZ', 'Tore 2. HZ', 
                                'Tempo 1. HZ', 'Tempo 2. HZ']
        st.dataframe(display_tempo, width='stretch', hide_index=True)
    else:
        st.warning("Keine Tempo-Daten verfügbar")

# SEITE: ALLE STATISTIKEN
elif page == "📋 Alle Statistiken":
    st.title("📋 Alle Statistiken im Überblick")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Übersicht", "👥 Spieler", "🏆 Teams", "📈 Export"])
    
    with tab1:
        st.subheader("Wichtigste Kennzahlen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚽ Tor-Statistiken")
            avg_goals = analyzer.get_average_goals_per_game()
            st.write(f"- Ø Tore gesamt: **{avg_goals['gesamt']:.1f}**")
            st.write(f"- Ø Heimtore: **{avg_goals['heim']:.1f}**")
            st.write(f"- Ø Gasttore: **{avg_goals['gast']:.1f}**")
            
            st.markdown("### 🏠 Heimvorteil")
            home_stats = analyzer.get_home_advantage()
            st.write(f"- Heimsiegquote: **{home_stats['heim_siegquote']:.1f}%**")
            st.write(f"- Auswärtssiegquote: **{home_stats['auswaerts_siegquote']:.1f}%**")
            st.write(f"- Vorteil: **{home_stats['heim_siegquote'] - home_stats['auswaerts_siegquote']:+.1f}%**")
        
        with col2:
            st.markdown("### ⏱️ Spieltempo")
            tempo = analyzer.get_game_tempo()
            if len(tempo) > 0:
                st.write(f"- Ø Tore 1. HZ: **{tempo['tore_1_halbzeit'].mean():.1f}**")
                st.write(f"- Ø Tore 2. HZ: **{tempo['tore_2_halbzeit'].mean():.1f}**")
                st.write(f"- Tempo 1. HZ: **{tempo['tempo_1_halbzeit'].mean():.2f}** Tore/Min")
                st.write(f"- Tempo 2. HZ: **{tempo['tempo_2_halbzeit'].mean():.2f}** Tore/Min")
            
            st.markdown("### 🎯 7-Meter")
            efficiency = analyzer.get_7m_efficiency()
            if len(efficiency) > 0:
                total_7m = efficiency['gesamt'].sum()
                total_scored = efficiency['verwandelt'].sum()
                avg_eff = (total_scored / total_7m * 100) if total_7m > 0 else 0
                st.write(f"- Gesamt: **{int(total_7m)}**")
                st.write(f"- Verwandelt: **{int(total_scored)}**")
                st.write(f"- Quote: **{avg_eff:.1f}%**")
    
    with tab2:
        st.subheader("Spieler-Statistiken")
        
        # Top Scorer
        st.markdown("### 🎯 Top 20 Torschützen")
        top_scorer = analyzer.get_top_scorer(20)
        if len(top_scorer) > 0:
            display_df = top_scorer.copy()
            display_df.columns = ['Spieler', 'Team', 'Tore']
            st.dataframe(display_df, width='stretch', hide_index=True)
        
        # Strafen
        st.markdown("### ⚠️ Strafen-Statistik")
        penalties = analyzer.get_penalty_statistics()
        if len(penalties) > 0:
            display_df = penalties.copy()
            display_df.columns = ['Spieler', 'Team', 'Strafen']
            st.dataframe(display_df, width='stretch', hide_index=True)
    
    with tab3:
        st.subheader("Team-Statistiken")
        team_stats = analyzer.get_team_statistics()
        if len(team_stats) > 0:
            show_df = team_stats[['team', 'spiele', 'siege', 'unentschieden', 'niederlagen', 
                                  'siegquote', 'tore_pro_spiel', 'gegentore_pro_spiel', 'tordifferenz']].copy()
            show_df.columns = ['Team', 'Spiele', 'S', 'U', 'N', 'Quote (%)', 
                              'Ø Tore', 'Ø Gegen', 'Diff']
            show_df['Diff'] = show_df['Diff'].astype(int)
            st.dataframe(show_df, width='stretch', hide_index=True)
    
    with tab4:
        st.subheader("📥 Daten exportieren")
        st.markdown("Lade alle Analysen als CSV-Dateien herunter:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Scorer Export
            top_scorer = analyzer.get_top_scorer(50)
            if len(top_scorer) > 0:
                csv = top_scorer.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Top Scorer (CSV)",
                    data=csv,
                    file_name="top_scorer.csv",
                    mime="text/csv"
                )
            
            # Team Stats Export
            if len(team_stats) > 0:
                csv = team_stats.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Team-Statistiken (CSV)",
                    data=csv,
                    file_name="team_statistics.csv",
                    mime="text/csv"
                )
            
            # 7m Efficiency Export
            efficiency = analyzer.get_7m_efficiency()
            if len(efficiency) > 0:
                csv = efficiency.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 7-Meter Effizienz (CSV)",
                    data=csv,
                    file_name="7m_efficiency.csv",
                    mime="text/csv"
                )
        
        with col2:
            # Penalties Export
            penalties = analyzer.get_penalty_statistics()
            if len(penalties) > 0:
                csv = penalties.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Strafen-Statistik (CSV)",
                    data=csv,
                    file_name="penalty_statistics.csv",
                    mime="text/csv"
                )
            
            # Game Tempo Export
            tempo = analyzer.get_game_tempo()
            if len(tempo) > 0:
                csv = tempo.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Spieltempo (CSV)",
                    data=csv,
                    file_name="game_tempo.csv",
                    mime="text/csv"
                )
        
        st.markdown("---")
        
        # Alle Analysen auf einmal speichern
        if st.button("💾 Alle Analysen lokal speichern", type="primary"):
            with st.spinner("Speichere Analysen..."):
                analyzer.save_all_analyses(output_dir="../data/analysis")
                st.success("✅ Alle Analysen wurden in ../data/analysis/ gespeichert!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p><strong>🤾 Handball Analytics Dashboard</strong></p>
        <p>Powered by Streamlit • Made with ❤️ for Handball</p>
    </div>
""", unsafe_allow_html=True)