import streamlit as st
import duckdb
import plotly.express as px
from pathlib import Path
from queries import get_station_flow

st.markdown("### Flujo Neto de Estaciones")

if 'user_types_sql' not in st.session_state:
    st.info("Configura los filtros en el menú lateral.")
    st.stop()

# Recuperar filtros
user_types_sql = st.session_state['user_types_sql']
date_filter_sql = st.session_state['date_filter_sql']

@st.cache_resource
def get_db_connection():
    db_path = Path(__file__).parent.parent.parent / "data" / "bikes.duckdb"
    return duckdb.connect(str(db_path), read_only=True)

con = get_db_connection()

st.markdown(
    "<span style='color:#9aa5b4; font-size:0.9rem'>"
    "Este análisis muestra si una estación actúa como <b>fuente</b> (pierde bicis) o "
    "como <b>sumidero</b> (acumula bicis). Esto es clave para las operaciones de rebalanceo manual de la flota.</span><br><br>",
    unsafe_allow_html=True
)

flow_df = get_station_flow(con, user_types_sql, date_filter_sql, limit=50)

if flow_df.empty:
    st.info("No hay datos suficientes para el cálculo.")
    st.stop()

# Separar top fuentes y sumideros
fuentes = flow_df[flow_df['net_flow'] > 0].head(10)
sumideros = flow_df[flow_df['net_flow'] < 0].tail(10).sort_values('net_flow')

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Principales Fuentes (Se vacían)")
    st.markdown("<span style='color:#9aa5b4; font-size:0.8rem'>Salen más bicicletas de las que entran</span>", unsafe_allow_html=True)
    
    fig_f = px.bar(
        fuentes, y='station', x='net_flow',
        orientation='h',
        color_discrete_sequence=['#F43F5E'], # Rose
        text='net_flow'
    )
    fig_f.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Déficit de bicicletas"),
        yaxis=dict(title="", autorange="reversed"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=400
    )
    st.plotly_chart(fig_f, use_container_width=True)

with col2:
    st.markdown("##### Principales Sumideros (Se llenan)")
    st.markdown("<span style='color:#9aa5b4; font-size:0.8rem'>Entran más bicicletas de las que salen</span>", unsafe_allow_html=True)
    
    fig_s = px.bar(
        sumideros, y='station', x='net_flow',
        orientation='h',
        color_discrete_sequence=['#10B981'], # Emerald
        text='net_flow'
    )
    # Convertir a valores absolutos para mostrar
    fig_s.update_traces(texttemplate="%{x}") 
    fig_s.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Exceso de bicicletas"),
        yaxis=dict(title="", autorange="reversed"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=400
    )
    st.plotly_chart(fig_s, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("#### Datos de Operación (Rebalanceo)")
st.dataframe(
    flow_df[['station', 'departures', 'arrivals', 'net_flow', 'net_flow_pct']],
    column_config={
        "station": "Estación",
        "departures": "Salidas (Demanda)",
        "arrivals": "Llegadas (Oferta)",
        "net_flow": "Flujo Neto",
        "net_flow_pct": st.column_config.ProgressColumn(
            "Desbalance (%)",
            format="%f%%",
            min_value=-100,
            max_value=100,
        ),
    },
    hide_index=True,
    use_container_width=True
)
