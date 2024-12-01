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

# Creamos la tabla supplements con ENUM para budget
create_table_supplements = '''
CREATE TABLE IF NOT EXISTS supplements (
    id INT NOT NULL AUTO_INCREMENT,
    goal TEXT NOT NULL,
    diet_type TEXT NOT NULL,
    activity_level TEXT NOT NULL,
    restrictions TEXT NOT NULL,
    budget ENUM('Bajo', 'Moderado', 'Alto') NOT NULL,
    recommendations TEXT NOT NULL,
    PRIMARY KEY (id)
);
'''

# Conexión y ejecución
connection = None
try:
    connection = get_connection()
    with connection.cursor() as cursor:
        # Crear la base de datos
        print("Creando base de datos 'database_api_llm'...")
        cursor.execute(create_database)
        print("Base de datos 'database_api_llm' creada o ya existía.")

        # Seleccionar la base de datos
        connection.select_db("database_api_llm")

        # Crear la tabla `routines`
        print("Creando tabla 'routines'...")
        cursor.execute(create_table_routines)
        connection.commit()
        print("Tabla 'routines' creada o ya existía.")

        # Crear la tabla `diets`
        print("Creando tabla 'diets'...")
        cursor.execute(create_table_diets)
        connection.commit()
        print("Tabla 'diets' creada o ya existía.")

        # Crear la tabla `supplements`
        print("Creando tabla 'supplements'...")
        cursor.execute(create_table_supplements)
        connection.commit()
        print("Tabla 'supplements' creada o ya existía.")
        print("¡Todas las tablas han sido creadas correctamente!")
except Exception as e:
    print(f"Error al crear las tablas: {e}")
finally:
    if connection:
        connection.close()



