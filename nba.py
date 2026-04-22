import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="NBA Dashboard", layout="wide")

# Carga de datos (ajusta el nombre del archivo)
@st.cache_data
def load_data():
    df = pd.read_csv("nba_all_elo.csv")
    return df

df = load_data()

# --- SIDEBAR (Barra Lateral) ---
st.sidebar.header("Filtros")

# 1. Selector de Año
years = sorted(df['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Selecciona un año", years)

# --- SIDEBAR (Barra Lateral) ---
st.sidebar.header("Filtros")

# 1. Selector de Año (Usando 'year_id')
years = sorted(df['year_id'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Selecciona un año", years)

# 2. Selector de Equipo (Usando 'team_id')
teams = sorted(df['team_id'].unique())
selected_team = st.sidebar.selectbox("Selecciona un equipo", teams)

# 3. Elemento Pills (Usando 'is_playoffs')
# En tu dataset, 0 es temporada regular y 1 es playoffs
game_category = st.sidebar.pills(
    "Tipo de juego", 
    options=["Temporada Regular", "Playoffs", "Ambos"], 
    default="Ambos"
)

# --- FILTRADO DE DATOS ---
df_filtered = df[(df['year_id'] == selected_year) & (df['team_id'] == selected_team)]

# Ajuste para el filtro de playoffs
if game_category == "Temporada Regular":
    df_filtered = df_filtered[df_filtered['is_playoffs'] == 0]
elif game_category == "Playoffs":
    df_filtered = df_filtered[df_filtered['is_playoffs'] == 1]

# --- LÓGICA DE CÁLCULO ---
# Ordenamos por 'gameorder' o 'date_game' para que el acumulado sea correcto
df_filtered = df_filtered.sort_values('gameorder') 
df_filtered['win_count'] = (df_filtered['game_result'] == 'W').cumsum()
df_filtered['loss_count'] = (df_filtered['game_result'] == 'L').cumsum()

# --- VISUALIZACIONES ---
st.title(f"Dashboard: {selected_team} ({selected_year})")