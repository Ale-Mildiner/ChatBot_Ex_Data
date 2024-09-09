import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import re
import sqlite3

# Reemplaza 'YOUR_TOKEN' con el token de tu bot
TOKEN = '6949294693:AAHlzu6OutvtW98MAVhWilgCxhwlgkUgxuY'

# Definir estados de conversación
REQUESTING_DNI = 1
FINISHED = 2

# Variable global para almacenar el DNI
user_dni = {}

# Función para manejar cualquier mensaje
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id

    # Si el DNI ya ha sido registrado, confirmar y reiniciar
    if user_id in user_dni:
        await update.message.reply_text(f'Gracias, ya tenemos tu DNI: {user_dni[user_id]}. Puedes enviar cualquier mensaje para empezar de nuevo.')
        return FINISHED

    # Si no se ha registrado el DNI, pedirlo
    await update.message.reply_text('Por favor, envíame tu número de DNI.')
    return REQUESTING_DNI

# Función para manejar el DNI
async def handle_dni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    dni = update.message.text.strip()

    # Validar el formato del DNI (por ejemplo, solo números y longitud de 8 dígitos)
    if re.fullmatch(r'\d{8}', dni):
        user_dni[user_id] = dni
        estado = obtener_estado_pedido(dni)
        if estado != False:
            response_message = f"Muchas gracias, tu DNI ({dni}) ha sido recibido. El estado de tu pedido es <i><b>{estado}</b></i>."
            await update.message.reply_text(response_message, parse_mode='HTML')
            return FINISHED
        
        else:
            response_message = f"Tu DNI ({dni}) no está registrado o ha sido mal ingresado, ingreselo nuevamente"
            await update.message.reply_text(response_message)
            return REQUESTING_DNI
    else:
        await update.message.reply_text('Número de DNI incorrecto. Por favor, ingréselo nuevamente.')
        return REQUESTING_DNI

# Función para reiniciar la conversación
async def reset_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    # Limpiar el DNI registrado para el usuario
    if user_id in user_dni:
        del user_dni[user_id]
    await update.message.reply_text('Por favor, envíame tu número de DNI.')
    return REQUESTING_DNI

def obtener_estado_pedido(dni):
    # Conectar a la base de datos SQLite (ajusta el nombre de la base de datos si es necesario)
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # Consulta SQL para obtener el estado del pedido basado en el DNI
    query = "SELECT estado_pedido FROM pedidos WHERE DNI = ?"
    
    state = False
    try:
        # Ejecutar la consulta
        cursor.execute(query, (dni,))
        
        # Obtener el resultado
        resultado = cursor.fetchone()
        
        if resultado:
            estado_pedido = resultado[0]
            state = estado_pedido
            print(f"El estado del pedido para el DNI {dni} es: {state}")
            print(estado_pedido)
        else:
            state = False
            print(f"No se encontró un pedido para el DNI {dni}.")
    
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
    
    finally:
        # Cerrar la conexión a la base de datos
        conn.close()
    return state





def main() -> None:
    # Crea la instancia de Application en lugar de Updater
    application = Application.builder().token(TOKEN).build()

    # Crea el ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            REQUESTING_DNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dni)],
            FINISHED: [MessageHandler(filters.TEXT & ~filters.COMMAND, reset_conversation)],
        },
        fallbacks=[],
    )

    # Agrega el ConversationHandler a la aplicación
    application.add_handler(conversation_handler)

    # Empieza a recibir actualizaciones
    application.run_polling()

if __name__ == '__main__':
    main()
