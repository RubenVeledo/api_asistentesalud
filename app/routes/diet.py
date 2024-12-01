from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from app.database.database import get_connection
from app.config import client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")  # Configuración de templates

# Configurar memoria conversacional
memory = ConversationBufferMemory()

# PromptTemplate simplificado
diet_prompt_template = PromptTemplate(
    input_variables=["goal", "preferences"],
    template=(
        "Soy un experto en nutrición de fitness. Genera un plan de comidas para un día enfocado en {goal} y respetando las "
        "siguientes preferencias alimenticias: {preferences}. Incluye únicamente las siguientes comidas:\n\n"
        "1. Desayuno: Nombre del plato\n"
        "2. Almuerzo: Nombre del plato\n"
        "3. Comida: Nombre del plato\n"
        "4. Cena: Nombre del plato\n\n"
        "No incluyas demasiados detalles ni información sobre suplementos."
        "En idioma español de España."
    )
)

# Función para evaluar la calidad de la dieta generada
def evaluate_diet(response: str) -> dict:
    """
    Evalúa la calidad de la dieta generada por el modelo.
    Retorna un diccionario con los resultados de la evaluación.
    """
    evaluation = {
        "coherencia": "Desayuno" in response and "Cena" in response,
        "claridad": len(response.splitlines()) >= 4,  # Debe tener al menos 4 líneas
        "completitud": len(response) > 50  # Mínimo de caracteres en la respuesta
    }
    evaluation["aprobado"] = all(evaluation.values())  # Aprueba solo si todos los criterios se cumplen
    return evaluation

# Ruta GET para renderizar el formulario
@router.get("/dieta", response_class=HTMLResponse)
async def get_diet_page(request: Request):
    """
    Renderiza la página HTML para solicitar los datos de la dieta.
    """
    return templates.TemplateResponse("diet.html", {"request": request})

# Ruta POST para procesar los datos y mostrar el resultado
@router.post("/dieta", response_class=HTMLResponse)
async def post_diet(request: Request, goal: str = Form(...), preferences: str = Form(...)):
    """
    Genera un plan de comidas personalizado para un solo día.
    Guarda la dieta generada en la base de datos y la muestra al usuario.
    """
    try:
        # Inicializar variables
        retries = 0
        max_retries = 3
        diet = ""
        evaluation = {"aprobado": False}

        # Generar la dieta con reintentos si es necesario
        while not evaluation["aprobado"] and retries < max_retries:
            # Generar el contenido del prompt
            prompt_content = diet_prompt_template.format(goal=goal, preferences=preferences)
            messages = [{"role": "user", "content": prompt_content}]

            # Solicitar al modelo
            completion = client.chat.completions.create(
                model="microsoft/Phi-3.5-mini-instruct",
                messages=messages,
                max_tokens=700
            )
            response = completion.choices[0].message.content

            # Evaluar la calidad de la respuesta
            evaluation = evaluate_diet(response)
            retries += 1

            if evaluation["aprobado"]:
                diet = response
            else:
                print(f"Reintento {retries}: Evaluación de calidad fallida. Solicitando nueva respuesta...")

        # Si no se logró una respuesta válida
        if not diet:
            raise HTTPException(status_code=500, detail="No se pudo generar una dieta válida tras varios intentos.")

        # Guardar la interacción en memoria
        memory.save_context(
            {"input": f"Objetivo: {goal}, Preferencias: {preferences}"},
            {"output": diet}
        )

        # Guardar la dieta generada en la base de datos
        connection = get_connection()
        with connection.cursor() as cursor:
            insert_query = '''
            INSERT INTO diets (goal, preferences, duration, diet)
            VALUES (%s, %s, %s, %s);
            '''
            cursor.execute(insert_query, (goal, preferences, 1, diet))  # Duración siempre 1
            connection.commit()

        # Mensaje motivacional
        user_message = (
            f"¡Aquí tienes tu plan de comidas personalizado para un día! Diseñado para ayudarte a alcanzar tu objetivo de {goal.lower()} "
            f"y adaptado a tus preferencias: {preferences.lower()}."
        )

        # Responder al usuario con la dieta en el template
        return templates.TemplateResponse("diet.html", {
            "request": request,
            "diet": diet,
            "message": user_message,  # Enviar el mensaje motivacional al template
            "goal": goal,
            "preferences": preferences
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar dieta: {e}")

    finally:
        if connection:
            connection.close()







