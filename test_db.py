from app.database.database import get_connection

try:
    connection = get_connection()
    print("Conexión establecida exitosamente.")
    print("Base de datos seleccionada:", connection.db.decode('utf-8'))
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
finally:
    if connection:
        connection.close()
