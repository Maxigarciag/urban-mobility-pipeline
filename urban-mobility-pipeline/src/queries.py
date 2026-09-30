"""
queries.py
Centraliza todas las consultas SQL al a base de datos DuckDB.
Cada función recibe la conexión y los parámetros de filtro necesarios,
y retorna un DataFrame de pandas listo para ser consumido por app.py.
Se usa @st.cache_data para evitar re-ejecución en cada interacción del usuario.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Ruta al CSV de clima (relativa a queries.py en src/)
WEATHER_CSV = Path(__file__).parent.parent / "data" / "daily_citi_bike_trip_counts_and_weather.csv"


# ──────────────────────────────────────────────
# Utilidades de fecha
# ──────────────────────────────────────────────

def get_date_range(_con):
    """Retorna la fecha mínima y máxima presentes en la tabla trips."""
    result = _con.execute(
        "SELECT MIN(started_at)::DATE, MAX(started_at)::DATE FROM trips"
    ).fetchone()
    return result[0], result[1]


def build_where(user_types_sql: str, date_filter_sql: str) -> str:
    """Construye la cláusula WHERE reutilizable para todos los queries."""
    return f"WHERE member_casual IN ({user_types_sql}) {date_filter_sql}"


# ──────────────────────────────────────────────
# KPIs
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_kpis(_con, user_types_sql: str, date_filter_sql: str) -> dict:
    """Total de viajes, duración promedio y estación principal de salida."""
    where = build_where(user_types_sql, date_filter_sql)

    totals = _con.execute(f"""
        SELECT COUNT(*) as total_trips,
               ROUND(AVG(duration_minutes), 1) as avg_duration
        FROM trips
        {where}
    """).fetchone()

    top_station = _con.execute(f"""
        SELECT start_station_name
        FROM trips
        {where}
        GROUP BY start_station_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """).fetchone()

    return {
        "total_trips": totals[0],
        "avg_duration": totals[1],
        "top_station": top_station[0] if top_station else "N/A",
    }


# ──────────────────────────────────────────────
# Viajes por hora del día
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_hourly_trips(_con, user_types_sql: str, date_filter_sql: str) -> pd.DataFrame:
    where = build_where(user_types_sql, date_filter_sql)
    return _con.execute(f"""
        SELECT
            EXTRACT(HOUR FROM started_at)::INTEGER AS hour_of_day,
            member_casual,
            COUNT(*) AS trip_count
        FROM trips
        {where}
        GROUP BY hour_of_day, member_casual
        ORDER BY hour_of_day
    """).df()


# ──────────────────────────────────────────────
# Viajes por día de la semana
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_weekly_trips(_con, user_types_sql: str, date_filter_sql: str) -> pd.DataFrame:
    where = build_where(user_types_sql, date_filter_sql)
    df = _con.execute(f"""
        SELECT
            DAYOFWEEK(started_at) AS day_num,
            CASE DAYOFWEEK(started_at)
                WHEN 0 THEN 'Dom'
                WHEN 1 THEN 'Lun'
                WHEN 2 THEN 'Mar'
                WHEN 3 THEN 'Mié'
                WHEN 4 THEN 'Jue'
                WHEN 5 THEN 'Vie'
                WHEN 6 THEN 'Sáb'
            END AS day_name,
            member_casual,
            COUNT(*) AS trip_count
        FROM trips
        {where}
        GROUP BY day_num, day_name, member_casual
        ORDER BY day_num
    """).df()
    return df


# ──────────────────────────────────────────────
# Top N Rutas
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_top_routes(_con, user_types_sql: str, date_filter_sql: str, top_n: int) -> pd.DataFrame:
    where = build_where(user_types_sql, date_filter_sql)
    return _con.execute(f"""
        SELECT
            start_station_name || ' → ' || end_station_name AS Ruta,
            COUNT(*)                                         AS "Total de Viajes",
            ROUND(AVG(duration_minutes), 1)                 AS "Duración Promedio (min)"
        FROM trips
        {where}
          AND start_station_name != end_station_name
        GROUP BY Ruta
        ORDER BY "Total de Viajes" DESC
        LIMIT {top_n}
    """).df()


# ──────────────────────────────────────────────
# Mapa — ScatterplotLayer (volumen por estación)
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_map_data(_con, user_types_sql: str, date_filter_sql: str, limit: int) -> pd.DataFrame:
    where = build_where(user_types_sql, date_filter_sql)
    return _con.execute(f"""
        SELECT
            start_station_name,
            AVG(start_lat) AS lat,
            AVG(start_lng) AS lon,
            COUNT(*)       AS total_trips
        FROM trips
        {where}
          AND start_lat IS NOT NULL
          AND start_lng IS NOT NULL
        GROUP BY start_station_name
        ORDER BY total_trips DESC
        LIMIT {limit}
    """).df()


# ──────────────────────────────────────────────
# Mapa — ArcLayer (top rutas con coordenadas)
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_arc_data(_con, user_types_sql: str, date_filter_sql: str, top_n: int) -> pd.DataFrame:
    where = build_where(user_types_sql, date_filter_sql)
    # Filtramos rutas donde las estaciones estén a >500m de distancia (haversine simplificado)
    # para que los arcos sean visualmente significativos en el mapa
    return _con.execute(f"""
        WITH raw AS (
            SELECT
                start_station_name,
                end_station_name,
                AVG(start_lat)  AS start_lat,
                AVG(start_lng)  AS start_lng,
                AVG(end_lat)    AS end_lat,
                AVG(end_lng)    AS end_lng,
                COUNT(*)        AS total_trips
            FROM trips
            {where}
              AND start_station_name != end_station_name
              AND start_lat IS NOT NULL
              AND end_lat   IS NOT NULL
              AND end_lng   IS NOT NULL
            GROUP BY start_station_name, end_station_name
        )
        SELECT *
        FROM raw
        WHERE
            -- Distancia euclidiana mínima ~0.01 grados ≈ 1.1 km
            SQRT(
                POWER(end_lat - start_lat, 2) +
                POWER(end_lng - start_lng, 2)
            ) > 0.01
        ORDER BY total_trips DESC
        LIMIT {top_n}
    """).df()


# ──────────────────────────────────────────────
# Mapa — HexagonLayer (densidad de origen de viajes)
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_hex_data(_con, user_types_sql: str, date_filter_sql: str) -> pd.DataFrame:
    """
    Retorna una muestra de coordenadas de origen para el HexagonLayer.
    Usamos USING SAMPLE para limitar el volumen enviado a PyDeck sin perder representatividad.
    """
    where = build_where(user_types_sql, date_filter_sql)
    return _con.execute(f"""
        SELECT
            start_lat AS lat,
            start_lng AS lon
        FROM trips
        {where}
          AND start_lat IS NOT NULL
          AND start_lng IS NOT NULL
        USING SAMPLE 60000 ROWS
    """).df()


# ──────────────────────────────────────────────
# Análisis de Estaciones — Flujo neto
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_station_flow(_con, user_types_sql: str, date_filter_sql: str, limit: int = 80) -> pd.DataFrame:
    """
    Calcula el flujo neto por estación: departures - arrivals.
    Positivo = la estación pierde bicicletas (fuente).
    Negativo = la estación acumula bicicletas (sumidero).
    """
    return _con.execute(f"""
        WITH departures AS (
            SELECT
                start_station_name  AS station,
                AVG(start_lat)      AS lat,
                AVG(start_lng)      AS lon,
                COUNT(*)            AS departures
            FROM trips
            WHERE member_casual IN ({user_types_sql}) {date_filter_sql}
              AND start_lat IS NOT NULL
            GROUP BY start_station_name
        ),
        arrivals AS (
            SELECT
                end_station_name    AS station,
                COUNT(*)            AS arrivals
            FROM trips
            WHERE member_casual IN ({user_types_sql}) {date_filter_sql}
              AND end_station_name IS NOT NULL
            GROUP BY end_station_name
        )
        SELECT
            d.station,
            d.lat,
            d.lon,
            d.departures,
            COALESCE(a.arrivals, 0)                          AS arrivals,
            d.departures - COALESCE(a.arrivals, 0)           AS net_flow,
            ROUND(
                100.0 * (d.departures - COALESCE(a.arrivals, 0))
                / NULLIF(d.departures + COALESCE(a.arrivals, 0), 0),
                1
            )                                                AS net_flow_pct
        FROM departures d
        LEFT JOIN arrivals a ON d.station = a.station
        WHERE d.lat IS NOT NULL AND d.lon IS NOT NULL
        ORDER BY ABS(d.departures - COALESCE(a.arrivals, 0)) DESC
        LIMIT {limit}
    """).df()
