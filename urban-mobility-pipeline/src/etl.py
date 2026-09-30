"""
etl.py
Este script se encarga de la ingesta y limpieza de los datos de viajes de Citi Bike.
Crea o se conecta a una base de datos local en DuckDB y procesa los archivos CSV de viajes.
"""

# pyrefly: ignore [missing-import]
import duckdb
from pathlib import Path

# Definimos las rutas relativas a la ubicación del script
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "bikes.duckdb"
# El comodín permite procesar todos los archivos CSV de viajes mensuales
CSV_PATH = DATA_DIR / "*citibike-tripdata*.csv"

def run_etl():
    """
    Ejecuta el proceso ETL:
    1. Conecta a la base de datos DuckDB (la crea si no existe).
    2. Ingiere los datos CSV limpiando y transformando según los requerimientos.
    3. Verifica el resultado imprimiendo el total de registros y las primeras 5 filas.
    """
    print(f"Iniciando proceso ETL...")
    print(f"Base de datos: {DB_PATH}")
    print(f"Archivos origen: {CSV_PATH}")

    # 1. Conectarse a la base de datos local
    con = duckdb.connect(str(DB_PATH))

    # 2. Ingesta, transformación y limpieza de datos usando SQL
    # - date_diff calcula la diferencia en minutos
    # - Filtramos nombres nulos y duraciones inválidas
    query_create_table = f"""
    CREATE OR REPLACE TABLE trips AS
    WITH raw_data AS (
        SELECT 
            *,
            date_diff('minute', TRY_CAST(started_at AS TIMESTAMP), TRY_CAST(ended_at AS TIMESTAMP)) AS duration_minutes
        FROM read_csv_auto('{CSV_PATH}', types={{'start_station_id': 'VARCHAR', 'end_station_id': 'VARCHAR'}})
    )
    SELECT *
    FROM raw_data
    WHERE 
        start_station_name IS NOT NULL 
        AND end_station_name IS NOT NULL
        AND duration_minutes > 0 
        AND duration_minutes <= 240;
    """
    
    print("Ejecutando consulta de ingesta y limpieza. Esto puede tardar unos momentos...")
    try:
        con.execute(query_create_table)
    except Exception as e:
        print(f"Error durante la ejecución de la consulta: {e}")
        con.close()
        return
    
    # 3. Verificación de los datos
    # Contar la cantidad total de registros procesados
    count_result = con.execute("SELECT COUNT(*) FROM trips").fetchone()
    total_records = count_result[0] if count_result else 0
    
    print(f"\n✅ ETL completado con éxito.")
    print(f"Total de registros procesados e insertados en la tabla 'trips': {total_records}")
    
    print("\nPrimeras 5 filas de la tabla 'trips':")
    # Intentar mostrar como DataFrame (si pandas está instalado), sino como tuplas
    try:
        sample_df = con.execute("SELECT * FROM trips LIMIT 5").df()
        print(sample_df)
    except ImportError:
        sample_rows = con.execute("SELECT * FROM trips LIMIT 5").fetchall()
        columns = [desc[0] for desc in con.description]
        print(f"Columnas: {columns}")
        for row in sample_rows:
            print(row)
            
    # Cerrar la conexión
    con.close()

if __name__ == "__main__":
    # Asegurarnos de que el directorio data/ existe (en un entorno real podría no estar creado)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    run_etl()
