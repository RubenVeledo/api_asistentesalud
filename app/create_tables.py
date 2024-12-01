from app.database.database import get_connection

# Creamos la base de datos
create_database = '''
CREATE DATABASE IF NOT EXISTS database_api_llm;
'''

# Creamos la tabla routines
create_table_routines = '''
CREATE TABLE IF NOT EXISTS routines (
    id INT NOT NULL AUTO_INCREMENT,
    level TEXT NOT NULL,
    time INT NOT NULL,
    equipment TEXT NOT NULL,
    goal TEXT NOT NULL,
    routine TEXT NOT NULL,
    PRIMARY KEY (id)
);
'''

# Creamos la tabla diets
create_table_diets = '''
CREATE TABLE IF NOT EXISTS diets (
    id INT NOT NULL AUTO_INCREMENT,
    level TEXT NOT NULL,
    goal TEXT NOT NULL,
    preferences TEXT NOT NULL,
    duration INT NOT NULL,
    diet TEXT NOT NULL,
    PRIMARY KEY (id)
);
'''

# Conexión y ejecución
connection = None
try:
    connection = get_connection()
    with connection.cursor() as cursor:
        
        print("Creando base de datos 'database_api_llm'...")
        cursor.execute(create_database)
        print("Base de datos 'database_api_llm' creada o ya existía.")

        connection.select_db("database_api_llm")

        print("Creando tabla 'routines' en la base de datos...")
        cursor.execute(create_table_routines)
        print("Tabla 'routines' creada con éxito.")

        print("Creando tabla 'diets' en la base de datos...")
        cursor.execute(create_table_diets)
        print("Tabla 'diets' creada con éxito.")

        connection.commit()
except Exception as e:
    print(f"Error al crear las tablas: {e}")
finally:
    if connection:
        connection.close()

