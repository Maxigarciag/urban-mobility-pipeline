# NYC Citi Bike Analytics

> Pipeline de análisis de movilidad urbana sobre datos reales del sistema de bicicletas compartidas de Nueva York.

## Stack Técnico

| Capa | Tecnología |
|------|------------|
| Ingesta & Transformación | **DuckDB** (SQL analítico sobre CSV) |
| Visualización | **Streamlit** + **Plotly Express** |
| Mapas 3D | **PyDeck** (deck.gl) |
| Lenguaje | **Python 3.11+** |

---

## Arquitectura del Pipeline

```
data/
  └── *citibike-tripdata*.csv   ← Archivos de origen (no versionados)
  └── bikes.duckdb               ← Base de datos local (generada por ETL)

src/
  ├── etl.py                     ← Ingesta, limpieza y carga en DuckDB
  ├── queries.py                 ← Capa de datos: todas las queries SQL cacheadas
  └── app.py                     ← Dashboard interactivo con Streamlit
```

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/nyc-citi-bike-analytics.git
cd nyc-citi-bike-analytics/urban-mobility-pipeline

# 2. Crear y activar entorno virtual (opcional pero recomendado)
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Cómo ejecutar

### Paso 1 — Correr el ETL

Colocá los archivos CSV de Citi Bike dentro de `data/` y ejecutá:

```bash
python src/etl.py
```

Esto genera `data/bikes.duckdb` con la tabla `trips` limpia y lista para análisis.

### Paso 2 — Levantar el Dashboard

```bash
python -m streamlit run src/app.py
```

El dashboard estará disponible en `http://localhost:8501`.

---

## Funcionalidades del Dashboard

- **KPIs en tiempo real**: Total de viajes, duración promedio y estación principal de salida.
- **Filtros interactivos**: Tipo de usuario (`member` / `casual`), rango de fechas y Top N.
- **Viajes por hora del día**: Gráfico de barras agrupado por tipo de usuario.
- **Viajes por día de la semana**: Patrón semanal de uso (días laborables vs. fines de semana).
- **Top N Rutas**: Tabla interactiva con las rutas más frecuentes y duración promedio.
- **Mapa 3D interactivo**:
  - `ScatterplotLayer`: Volumen de viajes por estación de origen.
  - `ArcLayer`: Visualización animada de los flujos entre estaciones más frecuentes.

---

## Datos de Origen

Los datos provienen del programa público de Citi Bike NYC:
- [Citi Bike System Data](https://citibikenyc.com/system-data)
- Formato: CSV mensual con columnas de viajes, estaciones y tipo de usuario.
- Los archivos CSV **no están incluidos** en el repositorio (ver `.gitignore`).

---

## Decisiones de Diseño

- **DuckDB en lugar de pandas**: Procesar 1.9M+ de registros directamente con SQL analítico es más eficiente que cargar DataFrames en memoria.
- **`read_only=True`**: La conexión al dashboard es de solo lectura para evitar corrupciones accidentales y mejorar el rendimiento concurrente.
- **`@st.cache_data`**: Todas las queries están cacheadas con TTL de 1 hora para que los filtros respondan instantáneamente después de la primera carga.
- **`queries.py` separado**: Separa la lógica de datos de la capa de presentación, facilitando el testing y el mantenimiento.

---

## Autor

Desarrollado como proyecto de portfolio por **Maxim**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://linkedin.com/)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/)
