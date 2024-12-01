from fastapi import FastAPI
from app.routes import routine, diet
from app.config import client

# Crear la instancia de la aplicación FastAPI
app = FastAPI()

# Incluir los routers (endpoints)
app.include_router(routine.router)
app.include_router(diet.router)

# Endpoint raíz
@app.get("/")
async def root():
    return {"message": "Bienvenido al Asesor Personal para Ejercicio y Salud"}


#uvicorn app.main:app --reload
#env\Scripts\activate
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#deactivate

