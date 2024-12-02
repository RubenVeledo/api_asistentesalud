# Imagen base de Python
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Archivo de dependencias
COPY requirements.txt /app/requirements.txt

# Instalación de las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Se excluyen archivos sensibles y copia solo lo necesario
COPY . /app
COPY .env.example /app/.env  

# Exponer el puerto en el que se ejecuta Uvicorn
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

