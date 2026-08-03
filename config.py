import os

# Token del bot (Render lo leerá de las variables de entorno)
TOKEN = os.getenv("TOKEN")

# Base de datos PostgreSQL (Render la leerá de las variables de entorno)
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración por defecto
HORAS_TURNO = 8

# Tarifas por defecto (se podrán cambiar desde Telegram)
TARIFA_NORMAL = 721.17
TARIFA_TIME_HALF = TARIFA_NORMAL * 1.5
TARIFA_BH = TARIFA_NORMAL * 0.5

# API OCR gratuita
OCR_API_KEY = "helloworld"
