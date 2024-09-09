from flask import Flask, request, jsonify
import sqlite3
app = Flask(__name__)
""" 
@app.route('/webhook', methods=['POST'])
def webhook():
    # Obtener el mensaje del request
    incoming_msg = request.json.get('Body', '').lower()

    # Verificar si hay un mensaje
    if incoming_msg:
        # Responder pidiendo el DNI
        return jsonify({"response": "Por favor, envíame tu número de DNI."})
    else:
        return jsonify({"response": "No entendí tu mensaje."})

if __name__ == '__main__':
    app.run(debug=True) """

from flask import Flask, request, jsonify
import re  # Para validación de DNI con expresiones regulares

app = Flask(__name__)

# Variable para rastrear si estamos esperando el DNI
waiting_for_dni = False
dni_stored = None

@app.route('/webhook', methods=['POST'])
def webhook():
    global waiting_for_dni

    # Obtener el mensaje del request
    incoming_msg = request.json.get('Body', '').lower()

    if not waiting_for_dni:  # En la primera interacción, siempre pedimos el DNI
        waiting_for_dni = True
        return jsonify({"response": "Hola, por favor envíame tu número de DNI."})

    else:  # Validar si el segundo mensaje es un DNI
        if re.fullmatch(r'\d{8}', incoming_msg):  # Verificar si son 8 dígitos
            dni_stored = incoming_msg  # Almacenar el DNI
            estado_del_pedido = obtener_estado_pedido(dni_stored)
            waiting_for_dni = False  # Reiniciar el ciclo para la próxima interacción

            if estado_del_pedido != False:
                response_message = f"Gracias, tu DNI ({dni_stored}) ha sido recibido. El estado de tu pedido es {estado_del_pedido}."
                return jsonify({"response": response_message})
            else:
                response_message = f"Tu DNI ({dni_stored}) no está registrado o ha sido mal ingresado, ingreselo nuevamente"
                return jsonify({"response": response_message})
        else:
            return jsonify({"response": "El DNI debe ser un número de 8 dígitos. Por favor, inténtalo nuevamente."})

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



if __name__ == '__main__':
    app.run(debug=True)
