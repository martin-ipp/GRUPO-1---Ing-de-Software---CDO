import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text

DB_URL = "postgresql://airflow:airflow@postgres:5432/pipeline_db"

def crear_tablas():
    # Crear pipeline_db si no existe
    conn = psycopg2.connect(
        host="postgres", port=5432,
        user="airflow", password="airflow", dbname="airflow"
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

    # Recrear tablas desde cero
    engine = create_engine(DB_URL)
    with engine.begin() as conn:

        conn.execute(text("DROP TABLE IF EXISTS ft_sales_daily"))
        conn.execute(text("""
            CREATE TABLE ft_sales_daily (
                date                 DATE,
                total_sales_revenue  FLOAT,
                total_sales_volume   FLOAT,
                active_cities        INTEGER,
                unit_revenue         FLOAT
            );
        """))

        conn.execute(text("DROP TABLE IF EXISTS ft_deep_dive"))
        conn.execute(text("""
            CREATE TABLE ft_deep_dive (
                date             DATE,
                country          VARCHAR(100),
                city             VARCHAR(100),
                product_family   VARCHAR(50),
                product_category VARCHAR(100),
                number_id        VARCHAR(50),
                sales_revenue    FLOAT,
                sales_volume     FLOAT
            );
        """))

        conn.execute(text("DROP TABLE IF EXISTS ft_geo_summary"))
        conn.execute(text("""
            CREATE TABLE ft_geo_summary (
                year          INTEGER,
                metric        VARCHAR(20),
                loc_type      VARCHAR(20),
                loc_name      VARCHAR(100),
                avg_val       FLOAT,
                best_family   TEXT,
                best_category TEXT
            );
        """))

        conn.execute(text("DROP TABLE IF EXISTS ft_scorecard"))
        conn.execute(text("""
            CREATE TABLE ft_scorecard (
                metrica      VARCHAR(20),
                resolucion   VARCHAR(20),
                periodo      TEXT,
                dimension    VARCHAR(20),
                top_abs_name TEXT,
                top_abs_val  FLOAT,
                bot_abs_name TEXT,
                bot_abs_val  FLOAT,
                top_g_name   TEXT,
                top_g_val    FLOAT,
                bot_g_name   TEXT,
                bot_g_val    FLOAT
            );
        """))

    print("Tablas creadas OK")

if __name__ == "__main__":
    crear_tablas()