# NYC Citi Bike Analytics Pipeline 🚲
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://TU_LINK_DE_STREAMLIT.streamlit.app)

Un dashboard interactivo y pipeline de datos (ETL) end-to-end diseñado para analizar la movilidad urbana en la red de bicicletas públicas de Nueva York (Citi Bike). Construido con un enfoque profesional de arquitectura moderna, este proyecto demuestra capacidades avanzadas en ingeniería de datos, optimización de consultas y visualización de alto impacto (estilo SaaS).

## 🌟 Arquitectura y Tecnologías Clave

* **Data Processing & Storage:** DuckDB (OLAP in-process ultrarrápido).
* **Backend & Interfaz:** Python 3.11+, Streamlit (Multi-página).
* **Visualización Geográfica 3D:** PyDeck (deck.gl) con `ScatterplotLayer`, `ArcLayer` y `HeatmapLayer`.
* **Visualización de Negocio:** Plotly Express.
* **Control de Versiones & Deploy:** Git, Streamlit Community Cloud.

---

## 📈 Vistas del Dashboard (Multi-Página)

La aplicación cuenta con tres secciones clave diseñadas para distintos enfoques analíticos:

### 1. Visión General del Negocio
Analiza el comportamiento global de los usuarios (Miembros vs. Casuales), las fluctuaciones de demanda por hora/día y la distribución de los viajes a lo largo de la semana.
![Visión General](urban-mobility-pipeline/assets/vision%20general%20del%20negocio.png)

### 2. Análisis Geográfico Avanzado
Utiliza aceleración GPU (via WebGL) para visualizar casi dos millones de registros geolocalizados.
* **Tab 1 (Rutas y Estaciones):** Muestra el volumen de origen mediante puntos azules vibrantes, y el flujo de los trayectos más populares trazados con arcos.
* **Tab 2 (Mapa de Calor):** Mapeo térmico denso utilizando gradientes desde azul hasta rosa y amarillo, resaltando instantáneamente los epicentros de demanda.
<p float="left">
  <img src="urban-mobility-pipeline/assets/estaciones%20y%20rutas%20(mapa).png" width="49%" />
  <img src="urban-mobility-pipeline/assets/mapa%20de%20calor.png" width="49%" /> 
</p>

### 3. Flujo Neto de Estaciones (Gestión de Rebalanceo)
Un panel operativo enfocado en logística de micro-movilidad. Calcula las entradas (llegadas) y salidas (partidas) de cada estación para revelar:
* **🔴 Fuentes:** Estaciones que se vacían rápidamente.
* **🟢 Sumideros:** Estaciones que se saturan de bicicletas.
![Flujo Neto](urban-mobility-pipeline/assets/flujo%20neto%20de%20estaciones.png)

---

## 📂 Estructura del Proyecto

```text
urban-mobility-pipeline/
├── assets/                 # Screenshots de la interfaz
├── data/
│   ├── bikes.duckdb        # Base de datos local (creada a partir de muestreo)
│   └── *.csv               # Datasets originales de Citi Bike / Clima (ignorados en git)
├── src/
│   ├── pages/
│   │   ├── 1_overview.py   # KPIs y Gráficos de barra
│   │   ├── 2_mapa.py       # Mapas PyDeck (Scatter, Arc, Heatmap)
│   │   └── 3_estaciones.py # Análisis logístico de fuentes y sumideros
│   ├── app.py              # Entrypoint y configuración de menú de Streamlit
│   ├── etl.py              # Script ETL: Ingesta, limpieza y volcado de CSV a DuckDB
│   ├── queries.py          # Centralización de lógica SQL y cacheo (@st.cache_data)
│   └── create_sample_db.py # Script para achicar la base de datos para el deploy
├── .gitignore              # Archivos y cachés a excluir
├── requirements.txt        # Dependencias de Python
└── README.md               # Esta documentación
```

---

## 🚀 Instalación y Uso Local

**1. Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/nyc-bikes.git
cd nyc-bikes
```

**2. Crear un entorno virtual e instalar dependencias**
```bash
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Ejecutar la aplicación**
```bash
# Nota: Streamlit 1.36+ es requerido para la API st.navigation()
streamlit run urban-mobility-pipeline/src/app.py
```

---

## 🔧 Destrezas Técnicas Demostradas

1. **Eficiencia con grandes volúmenes de datos:** Migración del almacenamiento de Pandas en memoria a **DuckDB**, permitiendo ejecutar consultas SQL complejas sobre millones de filas de forma casi instantánea.
2. **Separación de Responsabilidades (MVC):** `queries.py` almacena toda la lógica de obtención y transformación en SQL crudo. Los archivos de vista en `src/pages/` solo consumen DataFrames y los visualizan.
3. **Caché y Performance:** Implementación estratégica de `@st.cache_data` para evitar re-consultar a la base de datos durante el uso de los filtros dinámicos.
4. **Sampling para Visualizaciones:** Uso del comando `USING SAMPLE` en DuckDB para entregar mapas de calor densos sin sobrecargar la memoria de PyDeck (Deck.gl).
5. **Estética de Negocio "SaaS":** Diseño deliberado minimizando el ruido visual (eliminación de barras multicolores, emojis o UI recargada) favoreciendo los contrastes altos oscuros con colores acento modernos (Royal Blue, Rose, Emerald).
