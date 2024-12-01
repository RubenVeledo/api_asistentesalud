from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

# Cargar variables de entorno
load_dotenv()

# Configuración de Hugging Face
HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("HF_API_KEY no está configurada. Verifica el archivo .env.")

client = InferenceClient(api_key=HF_API_KEY)

# Configuración de la base de datos
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_DB = os.getenv("MYSQL_DB")

if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB]):
    raise ValueError("Faltan configuraciones para la base de datos en el archivo .env.")
