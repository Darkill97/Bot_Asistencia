import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

def conectar():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    # Tabla de empleados
    cur.execute("""
    CREATE TABLE IF NOT EXISTS empleados(
        id SERIAL PRIMARY KEY,
        uid TEXT UNIQUE,
        nombre TEXT,
        tarifa NUMERIC DEFAULT 721.17,
        activo BOOLEAN DEFAULT TRUE
    );
    """)

    # Tabla de asistencias
    cur.execute("""
    CREATE TABLE IF NOT EXISTS asistencias(
        id SERIAL PRIMARY KEY,
        uid TEXT,
        nombre TEXT,
        fecha DATE,
        hora TIME,
        estado TEXT,
        creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Tablas creadas correctamente")
