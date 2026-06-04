import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:postgres@postgres:5432/pipeline_db"

def crear_tablas():
    # Crear pipeline_db si no existe usando psycopg2 directamente
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'pipeline_db'")
    if not cursor.fetchone():
        cursor.execute("CREATE DATABASE pipeline_db")
        print("Base de datos pipeline_db creada")
    else:
        print("Base de datos pipeline_db ya existe")
    cursor.close()
    conn.close()

    # Crear tablas con SQLAlchemy
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales_by_category (
                product_category VARCHAR(100),
                total_revenue    FLOAT,
                total_volume     FLOAT,
                num_transactions INTEGER
            );
        """))
        conn.commit()
    print("Tablas creadas OK")

if __name__ == "__main__":
    crear_tablas()