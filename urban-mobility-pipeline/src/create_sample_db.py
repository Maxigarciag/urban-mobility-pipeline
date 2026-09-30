import duckdb
from pathlib import Path
import os

def create_sample_db():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    original_db = data_dir / "bikes.duckdb"
    sample_db = data_dir / "bikes_sample.duckdb"

    if not original_db.exists():
        print(f"Error: No se encontró la base de datos original en {original_db}")
        return

    print("Conectando a la base original...")
    con_in = duckdb.connect(str(original_db), read_only=True)
    
    # Check total rows
    total_rows = con_in.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
    print(f"La base original tiene {total_rows:,} registros.")

    if sample_db.exists():
        print("Eliminando sample anterior...")
        os.remove(sample_db)

    print("Creando base de datos de muestra (50,000 registros para GitHub/Streamlit Cloud)...")
    con_out = duckdb.connect(str(sample_db))
    
    # Copiar una muestra representativa (usando ATTACH)
    con_out.execute(f"ATTACH '{original_db}' AS db_in (READ_ONLY)")
    con_out.execute("""
        CREATE TABLE trips AS 
        SELECT * FROM db_in.trips
        USING SAMPLE 50000 ROWS
    """)
    con_out.execute("DETACH db_in")
    
    con_out.close()
    con_in.close()

    size_mb = os.path.getsize(sample_db) / (1024 * 1024)
    print(f"¡Listo! Archivo creado en: {sample_db}")
    print(f"Tamaño: {size_mb:.2f} MB")
    print("\nPara el deploy en Streamlit Cloud:")
    print("1. Renombrá 'bikes_sample.duckdb' a 'bikes.duckdb' justo antes de subir a GitHub (o cambialo en el código).")
    print("2. Asegurate de que el .gitignore permita subir ESE archivo pequeño (el actual ignora todos los *.duckdb).")

if __name__ == "__main__":
    create_sample_db()
