from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import routine, diet

app = FastAPI()

# Carpeta de templates
templates = Jinja2Templates(directory="app/templates")

# Archivos estáticos (opcional, para CSS o JS si se quisiera implementar)
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoints
app.include_router(routine.router)
app.include_router(diet.router)

# Renderizar la página principal
@app.get("/", response_class=HTMLResponse)
async def root(request):
    return templates.TemplateResponse("index.html", {"request": request})



#uvicorn app.main:app --reload
#env\Scripts\activate
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#deactivate

