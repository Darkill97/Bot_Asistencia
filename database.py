import psycopg2
from config import DATABASE_URL

def conectar():
    return psycopg2.connect(DATABASE_URL)

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        id SERIAL PRIMARY KEY,
        uid VARCHAR(50) UNIQUE,
        nombre VARCHAR(100),
        tarifa_normal DECIMAL(10,2),
        tarifa_timehalf DECIMAL(10,2),
        tarifa_bh DECIMAL(10,2)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id SERIAL PRIMARY KEY,
        uid VARCHAR(50),
        nombre VARCHAR(100),
        fecha DATE,
        hora TIME,
        estado VARCHAR(50)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
