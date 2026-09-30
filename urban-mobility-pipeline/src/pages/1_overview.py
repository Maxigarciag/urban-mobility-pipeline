import streamlit as st
import duckdb
import plotly.express as px
from pathlib import Path

from queries import (
    get_date_range,
    get_kpis,
    get_hourly_trips,
    get_weekly_trips,
    get_top_routes,
)

# ──────────────────────────────────────────────
# Conexión a DuckDB
# ──────────────────────────────────────────────
@st.cache_resource
def get_db_connection():
    # Use parent.parent since we are now in src/pages/
    db_path = Path(__file__).parent.parent.parent / "data" / "bikes.duckdb"
    return duckdb.connect(str(db_path), read_only=True)

con = get_db_connection()

# ──────────────────────────────────────────────
# Sidebar — Filtros
# ──────────────────────────────────────────────
st.sidebar.markdown("### Filtros Generales")

user_types_df = con.execute(
    "SELECT DISTINCT member_casual FROM trips WHERE member_casual IS NOT NULL"
).df()
user_types_list = user_types_df['member_casual'].tolist()

selected_user_types = st.sidebar.multiselect(
    "Tipo de usuario",
    options=user_types_list,
    default=user_types_list
)

min_date, max_date = get_date_range(con)
date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

top_n = st.sidebar.slider("Top N Rutas", min_value=5, max_value=20, value=10)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<span style='color:#9aa5b4; font-size:0.8rem'>Datos disponibles:<br>"
    f"{min_date} a {max_date}</span>",
    unsafe_allow_html=True
)

if not selected_user_types:
    st.warning("Selecciona al menos un tipo de usuario.")
    st.stop()

if len(date_range) != 2:
    st.warning("Selecciona un rango de fechas completo.")
    st.stop()

user_types_sql = ", ".join([f"'{u}'" for u in selected_user_types])
start_date, end_date = date_range
date_filter_sql = f"AND started_at::DATE BETWEEN '{start_date}' AND '{end_date}'"

# Almacenar en session_state para compartir con otras páginas
st.session_state['user_types_sql'] = user_types_sql
st.session_state['date_filter_sql'] = date_filter_sql
st.session_state['top_n'] = top_n

# ──────────────────────────────────────────────
# Contenido de la página
# ──────────────────────────────────────────────
st.markdown("### Visión General del Negocio")

kpis = get_kpis(con, user_types_sql, date_filter_sql)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Viajes", f"{kpis['total_trips']:,}".replace(",", "."))
with col2:
    st.metric("Duración Promedio (min)", kpis['avg_duration'])
with col3:
    st.metric("Estación Principal de Salida", kpis['top_station'])

st.markdown("<hr>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Fila 2 — Viajes por hora + Top N rutas
# ──────────────────────────────────────────────
COLOR_MAP = {"member": "#2563EB", "casual": "#38BDF8"} # Royal Blue & Sky Blue

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Viajes por hora del día")
    hourly_df = get_hourly_trips(con, user_types_sql, date_filter_sql)
    if not hourly_df.empty:
        fig = px.bar(
            hourly_df, x='hour_of_day', y='trip_count',
            color='member_casual', barmode='group',
            color_discrete_map=COLOR_MAP,
            labels={'hour_of_day': '', 'trip_count': '', 'member_casual': ''}
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(dtick=1, showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#222"),
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos.")

with col_b:
    st.markdown(f"#### Top {top_n} Rutas más transitadas")
    routes_df = get_top_routes(con, user_types_sql, date_filter_sql, top_n)
    if not routes_df.empty:
        st.dataframe(routes_df, use_container_width=True, hide_index=True)
    else:
        st.info("Sin datos.")

st.markdown("<hr>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Fila 3 — Viajes por día de la semana
# ──────────────────────────────────────────────
st.markdown("#### Viajes por día de la semana")
weekly_df = get_weekly_trips(con, user_types_sql, date_filter_sql)
if not weekly_df.empty:
    fig_w = px.bar(
        weekly_df, x='day_name', y='trip_count',
        color='member_casual', barmode='group',
        color_discrete_map=COLOR_MAP,
        labels={'day_name': '', 'trip_count': '', 'member_casual': ''}
    )
    fig_w.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#222"),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="")
    )
    st.plotly_chart(fig_w, use_container_width=True)
else:
    st.info("Sin datos.")
