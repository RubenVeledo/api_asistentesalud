from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from app.routes import routine, diet, supplements

# Crear instancia de la aplicación FastAPI
app = FastAPI()

# Configurar rutas y plantillas
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(routine.router)
app.include_router(diet.router)
app.include_router(supplements.router)

# Endpoint raíz que renderiza la página principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})




#uvicorn app.main:app --reload
#env\Scripts\activate
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#deactivate

