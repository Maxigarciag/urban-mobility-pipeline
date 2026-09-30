import streamlit as st
import duckdb
import pydeck as pdk
from pathlib import Path
from queries import get_map_data, get_arc_data, get_hex_data

st.markdown("### Análisis Geográfico")

if 'user_types_sql' not in st.session_state:
    st.info("Configura los filtros en el menú lateral.")
    st.stop()

# Recuperar filtros
user_types_sql = st.session_state['user_types_sql']
date_filter_sql = st.session_state['date_filter_sql']
top_n = st.session_state['top_n']

@st.cache_resource
def get_db_connection():
    db_path = Path(__file__).parent.parent.parent / "data" / "bikes.duckdb"
    return duckdb.connect(str(db_path), read_only=True)

con = get_db_connection()

tab_scatter, tab_hex = st.tabs(["Estaciones & Rutas", "Mapa de Calor"])

# ── Tab 1: ScatterplotLayer + ArcLayer ──
with tab_scatter:
    st.markdown(
        "<span style='color:#9aa5b4; font-size:0.8rem'>"
        "Puntos: volumen por estación de origen &nbsp;|&nbsp;"
        "Arcos: top rutas largas (azul royal = origen, celeste = destino)</span>",
        unsafe_allow_html=True
    )

    map_df = get_map_data(con, user_types_sql, date_filter_sql, top_n * 10)
    arc_df = get_arc_data(con, user_types_sql, date_filter_sql, top_n)

    layers = []
    if not map_df.empty:
        _max = map_df['total_trips'].max()
        _min = map_df['total_trips'].min()
        rng  = _max - _min if _max != _min else 1
        map_df['radius'] = map_df['total_trips'].apply(
            lambda t: 50 + ((t - _min) / rng) * 180
        )
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_radius='radius',
            get_fill_color='[37, 99, 235, 170]',   # Royal Blue
            get_line_color='[56, 189, 248, 80]',   # Sky Blue
            stroked=True,
            line_width_min_pixels=1,
            pickable=True,
        ))

    if not arc_df.empty:
        layers.append(pdk.Layer(
            "ArcLayer",
            data=arc_df,
            get_source_position='[start_lng, start_lat]',
            get_target_position='[end_lng, end_lat]',
            get_width=5,
            width_min_pixels=3,
            get_source_color='[37, 99, 235, 220]', # Royal Blue
            get_target_color='[56, 189, 248, 220]', # Sky Blue
            great_circle=True,
            pickable=True,
            auto_highlight=True,
        ))

    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=40.7300, longitude=-73.9800, zoom=12.5, pitch=40
        ),
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={
            "html": "<b>{start_station_name}</b><br>Viajes: {total_trips}",
            "style": {
                "backgroundColor": "#0E1117",
                "color": "#FFFFFF",
                "border": "1px solid #FFFFFF",
                "fontFamily": "Inter, sans-serif",
                "fontSize": "12px"
            }
        }
    ))

# ── Tab 2: HeatmapLayer ──
with tab_hex:
    st.markdown(
        "<span style='color:#9aa5b4; font-size:0.8rem'>"
        "Mapa de calor: la intensidad del color representa la densidad de viajes iniciados en cada zona.</span>",
        unsafe_allow_html=True
    )

    hex_df = get_hex_data(con, user_types_sql, date_filter_sql)

    if not hex_df.empty:
        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=hex_df,
            get_position='[lon, lat]',
            get_weight=1,
            radius_pixels=40,
            intensity=1,
            threshold=0.03,
            color_range=[
                [15,  23,  42,   20],   # Deep background blue
                [37,  99,  235,  80],   # Royal Blue
                [168, 85,  247, 160],   # Purple
                [236, 72,  153, 200],   # Pink
                [244, 63,  94,  230],   # Rose
                [250, 204, 21,  255],   # Yellow
            ]
        )

        st.pydeck_chart(pdk.Deck(
            layers=[heatmap_layer],
            initial_view_state=pdk.ViewState(
                latitude=40.7300,
                longitude=-73.9800,
                zoom=12.5,
                pitch=0
            ),
            map_style="mapbox://styles/mapbox/dark-v10",
        ))
    else:
        st.info("Sin datos para el mapa de calor.")
