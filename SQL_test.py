import sqlite3

def obtener_estado_pedido(dni):
    # Conectar a la base de datos
    conn = sqlite3.connect('example.db')  # Reemplaza con el nombre del archivo .db creado
    cursor = conn.cursor()
    
    # Ejecutar la consulta
    cursor.execute("SELECT estado_pedido FROM pedidos WHERE DNI = ?", (dni,))
    
    # Obtener el resultado
    resultado = cursor.fetchone()
    
    # Cerrar la conexión
    conn.close()
    
    # Verificar si se obtuvo un resultado
    if resultado:
        return resultado[0]
    else:
        return None  # O podrías devolver un mensaje indicando que el DNI no se encontró

# Ejemplo de uso
dni = '12345678'
estado_pedido = obtener_estado_pedido(dni)
print(f'El estado del pedido para el DNI {dni} es: {estado_pedido}')
