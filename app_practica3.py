import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="NBA Dashboard", 
    page_icon="🏀", 
    layout="wide"
)

# --- 2. ENCABEZADO DE LA PRÁCTICA ---
st.title("🏀 Dashboard de Rendimiento NBA")
st.markdown(f"**Práctica desarrollada por: García Juaréz Dayanara y Munguia Aguilera César Raúl**")
st.markdown("---")

# --- 3. CARGA DE DATOS ---
@st.cache_data
def load_nba_data():
    """Carga y prepara el dataset de la NBA."""
    raw_data = pd.read_csv("nba_all_elo.csv")
    raw_data['date_game'] = pd.to_datetime(raw_data['date_game'])
    return raw_data

nba_data = load_nba_data()

# --- 4. BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Búsqueda")

# Filtro de Año
available_years = sorted(nba_data['year_id'].unique(), reverse=True)
target_year = st.sidebar.selectbox("📅 Selecciona el Año:", available_years)

# Filtro de Equipo (Dependiente del año)
teams_in_year = nba_data[nba_data['year_id'] == target_year]['team_id'].unique()
available_teams = sorted(teams_in_year)
target_team = st.sidebar.selectbox("🏀 Selecciona el Equipo:", available_teams)

# Filtro de Tipo de Juego
game_type_options = ["Temporada Regular", "Playoffs", "Ambos"]
target_game_type = st.sidebar.pills("🏆 Tipo de juegos:", game_type_options, default="Ambos")

# --- 5. LÓGICA DE PROCESAMIENTO ---
# Construcción de la condición de filtrado
filter_condition = (nba_data['year_id'] == target_year) & (nba_data['team_id'] == target_team)

if target_game_type == "Temporada Regular":
    filter_condition &= (nba_data['is_playoffs'] == 0)
elif target_game_type == "Playoffs":
    filter_condition &= (nba_data['is_playoffs'] == 1)

# Aplicar filtros y ordenar cronológicamente
team_season_data = nba_data[filter_condition].sort_values('date_game').copy()

# Cálculo de métricas acumuladas
team_season_data['win_indicator'] = (team_season_data['game_result'] == 'W').astype(int)
team_season_data['loss_indicator'] = (team_season_data['game_result'] == 'L').astype(int)

team_season_data['cumulative_wins'] = team_season_data['win_indicator'].cumsum()
team_season_data['cumulative_losses'] = team_season_data['loss_indicator'].cumsum()

# Generar el número de juego consecutivo
team_season_data = team_season_data.reset_index(drop=True)
team_season_data['game_number'] = team_season_data.index + 1

# --- 6. VISUALIZACIONES ---
st.subheader(f"Análisis de Temporada: {target_team} ({target_year})")

COLOR_WIN = "#2E7D32"
COLOR_LOSS = "#D32F2F"

col_chart, col_pie = st.columns([2, 1])

with col_chart:
    st.markdown("##### Progreso de la Temporada")
    
    line_chart = go.Figure()
    
    # Serie de Victorias
    line_chart.add_trace(go.Scatter(
        x=team_season_data['game_number'], 
        y=team_season_data['cumulative_wins'],
        mode='lines+markers',
        name='Victorias (W)',
        line=dict(color=COLOR_WIN, width=3),
        marker=dict(size=6)
    ))
    
    # Serie de Derrotas
    line_chart.add_trace(go.Scatter(
        x=team_season_data['game_number'], 
        y=team_season_data['cumulative_losses'],
        mode='lines+markers',
        name='Derrotas (L)',
        line=dict(color=COLOR_LOSS, width=3),
        marker=dict(size=6)
    ))

    # Diseño limpio y sin bordes pesados
    line_chart.update_layout(
        template="plotly_white",
        xaxis_title="Número de Juego",
        yaxis_title="Partidos Acumulados",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(line_chart, use_container_width=True)

with col_pie:
    st.markdown("##### Distribución Global")
    results_distribution = team_season_data['game_result'].value_counts()
    
    if not results_distribution.empty:
        pie_chart = px.pie(
            names=results_distribution.index,
            values=results_distribution.values,
            color=results_distribution.index,
            color_discrete_map={'W': COLOR_WIN, 'L': COLOR_LOSS},
            hole=0.4 # Aspecto de dona, más moderno
        )
        
        pie_chart.update_traces(textposition='inside', textinfo='percent+label')
        pie_chart.update_layout(
            template="plotly_white",
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(pie_chart, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para generar gráficas con esta selección.")