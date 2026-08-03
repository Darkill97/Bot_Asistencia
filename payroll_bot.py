from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import TOKEN
from database import crear_tablas


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Asistencia Bot\n\n"
        "✅ Conectado correctamente.\n"
        "📸 Ya casi estoy listo para recibir fotografías."
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Iniciar bot\n"
        "/ayuda - Mostrar ayuda"
    )


def main():

    print("Conectando a la base de datos...")

    crear_tablas()

    print("Base de datos OK")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))

    print("Bot iniciado")

    app.run_polling()


if __name__ == "__main__":
    main()
