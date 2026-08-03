import os
import pytesseract
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta
import io

TOKEN = os.getenv("TOKEN") # Lee el token de Render
DB_FILE = "asistencia.xlsx"

# *1. TARIFAS*
TARIFA_NORMAL = 721.17
TARIFA_TIME_HALF = 721.17 * 1.5 # $1,081.76
TARIFA_BH = 721.17 * 0.5 # $360.59
HORAS_TURNO_NORMAL = 8

async def leer_foto(file_path):
    img = Image.open(file_path)
    texto = pytesseract.image_to_string(img, lang='spa+eng')

    datos = {'nombre': '', 'uid': '', 'fecha': '', 'hora': '', 'estado': ''}
    for linea in texto.split('\n'):
        if "Name:" in linea: datos['nombre'] = linea.split("Name:")[1].strip()
        if "User ID:" in linea: datos['uid'] = linea.split("User ID:")[1].strip()
        if "Date:" in linea: datos['fecha'] = linea.split("Date:")[1].strip()
        if "Time:" in linea: datos['hora'] = linea.split("Time:")[1].strip()
        if "Status:" in linea: datos['estado'] = linea.split("Status:")[1].strip()
    return datos

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"temp_{update.effective_user.id}.jpg"
        await photo_file.download_to_drive(file_path)

        datos = await leer_foto(file_path)
        os.remove(file_path) # borra la foto temporal

        # Guardar marcación
        df_nuevo = pd.DataFrame([datos])
        try:
            df = pd.read_excel(DB_FILE)
            df = pd.concat([df, df_nuevo], ignore_index=True)
        except:
            df = df_nuevo
        df.to_excel(DB_FILE, index=False)

        await update.message.reply_text(f"✅ Registrado: {datos['nombre']}\n{datos['estado']} - {datos['fecha']} {datos['hora']}")
    except Exception as e:
        await update.message.reply_text(f"Error leyendo la foto: {e}")

def calcular_pago_semana(uid, df_semana):
    total_normal = 0
    total_extra = 0
    total_bh = 0

    for fecha in df_semana['fecha'].unique():
        marcaciones = df_semana[df_semana['fecha'] == fecha].sort_values('hora')
        if len(marcaciones) >= 2:
            try:
                entrada = datetime.strptime(marcaciones.iloc[0]['hora'], '%I:%M %p')
                salida = datetime.strptime(marcaciones.iloc[-1]['hora'], '%I:%M %p')
                horas_trabajadas = (salida - entrada).seconds / 3600

                if horas_trabajadas > HORAS_TURNO_NORMAL:
                    extra = horas_trabajadas - HORAS_TURNO_NORMAL
                    normal = HORAS_TURNO_NORMAL
                else:
                    normal = horas_trabajadas
                    extra = 0

                if "Overtime" in marcaciones['estado'].values:
                    total_extra += extra
                else:
                    total_normal += normal
            except:
                continue

    pago_normal = total_normal * TARIFA_NORMAL
    pago_extra = total_extra * TARIFA_TIME_HALF
    pago_bh = total_bh * TARIFA_BH

    return {
        'Horas Normales': round(total_normal, 2),
        'Horas Extra 1.5x': round(total_extra, 2),
        'Horas BH 0.5x': round(total_bh, 2),
        'Pago Normal': round(pago_normal, 2),
        'Pago Extra': round(pago_extra, 2),
        'Pago BH': round(pago_bh, 2),
        'TOTAL PAGO': round(pago_normal + pago_extra + pago_bh, 2)
    }

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        df = pd.read_excel(DB_FILE)
        df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y', errors='coerce')

        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)

        df_semana = df[(df['fecha_dt'] >= inicio_semana) & (df['fecha_dt'] <= fin_semana)]

        resumen_final = []
        for uid in df_semana['uid'].unique():
            datos_uid = df_semana[df_semana['uid'] == uid]
            nombre = datos_uid['nombre'].iloc[0]
            pago = calcular_pago_semana(uid, datos_uid)
            pago['Nombre'] = nombre
            pago['UID'] = uid
            resumen_final.append(pago)

        df_resumen = pd.DataFrame(resumen_final)
        df_resumen.to_excel("resumen_semanal.xlsx", index=False)

        await context.bot.send_document(chat_id=update.effective_chat.id, document=open("resumen_semanal.xlsx", "rb"))
        await update.message.reply_text("📊 Aquí tienes el resumen semanal con pagos de todos")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CommandHandler("resumen", resumen))

    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
