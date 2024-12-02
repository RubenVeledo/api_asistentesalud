from fastapi import APIRouter, HTTPException, Request, Form
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from app.database.database import get_connection
from app.config import client
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

memory = ConversationBufferMemory(return_messages=True, memory_key="history", input_key="input")

templates = Jinja2Templates(directory="app/templates") 

# Configurar memoria conversacional
memory = ConversationBufferMemory()

# PromptTemplate
supplements_prompt_template = PromptTemplate(
    input_variables=["goal", "diet_type", "activity_level", "restrictions", "budget"],
    template=(
        "Eres un nutricionista y entrenador personal altamente calificado. Genera una lista personalizada de máximo 3 suplementos "
        "alimenticios para una persona con el siguiente perfil:\n\n"
        "- Objetivo principal: {goal}\n"
        "- Tipo de dieta: {diet_type}\n"
        "- Nivel de actividad física: {activity_level}\n"
        "- Restricciones alimenticias o intolerancias: {restrictions}\n"
        "- Presupuesto: {budget}\n\n"
        "Asegúrate de que las recomendaciones sean claras, justificadas y accesibles. Incluye lo siguiente para cada suplemento:\n\n"
        "1. Nombre del suplemento.\n"
        "2. Beneficios clave para alcanzar el objetivo.\n"
        "3. Cómo y cuándo tomarlo (opcional).\n\n"
        "Proporciona sugerencias organizadas y evita recomendaciones médicas específicas. Recuerda mencionar que el usuario "
        "debe leer las instrucciones del suplemento y consultar con un profesional si tiene dudas. Se conciso no te extiendas demasiado en las explicaciones."
    )
)

# Función para evaluar la calidad de la respuesta
def evaluate_supplements(response: str) -> dict:
    """
    Evalúa la calidad de la respuesta generada por el modelo.
    Retorna un diccionario con los resultados de la evaluación.
    """
    evaluation = {
        "coherencia": "suplemento" in response.lower(),
        "claridad": len(response.splitlines()) >= 3,  
        "completitud": len(response) > 100 
    }
    evaluation["aprobado"] = all(evaluation.values()) 
    return evaluation


# Ruta GET para renderizar el formulario
@router.get("/suplementos", response_class=HTMLResponse)
async def get_supplements_form(request: Request):
    """
    Renderiza el formulario de generación de suplementos.
    """
    return templates.TemplateResponse("supplements.html", {"request": request})

# Ruta POST para procesar los datos y mostrar el resultado
@router.post("/suplementos", response_class=HTMLResponse)
async def generate_supplements(
    request: Request,
    goal: str = Form(...),
    diet_type: str = Form(...),
    activity_level: str = Form(...),
    restrictions: str = Form(...),
    budget: str = Form(...),
):
    """
    Genera una lista personalizada de suplementos alimenticios.
    Guarda la lista generada en la base de datos y devuelve el resultado en una plantilla HTML.
    """
    # Rangos predefinidos para el presupuesto
    valid_budgets = ["Bajo", "Moderado", "Alto"]

    # Validación del presupuesto
    if budget not in valid_budgets:
        raise HTTPException(status_code=400, detail="Presupuesto inválido. Debe ser 'Bajo', 'Moderado' o 'Alto'.")

    try:
        # Se inicializan las variables variables y le damos un máximo de 3 intentos para generar una respuesta válida
        retries = 0
        max_retries = 3
        supplements = ""
        evaluation = {"aprobado": False}

        # Generar recomendaciones con reintentos si es necesario
        while not evaluation["aprobado"] and retries < max_retries:
            # Se tiene en cuenta el contenido del prompt
            prompt_content = supplements_prompt_template.format(
                goal=goal,
                diet_type=diet_type,
                activity_level=activity_level,
                restrictions=restrictions,
                budget=budget
            )
            messages = [{"role": "user", "content": prompt_content}]

            # Llamamos al model
            completion = client.chat.completions.create(
                model="microsoft/Phi-3.5-mini-instruct",
                messages=messages,
                max_tokens=750
            )
            response = completion.choices[0].message.content

            # Evaluación de la calidad de la respuesta
            evaluation = evaluate_supplements(response)
            retries += 1

            if evaluation["aprobado"]:
                supplements = response
            else:
                print(f"Reintento {retries}: Evaluación de calidad fallida. Solicitando nueva respuesta...")

        # Si no se logró una respuesta válida
        if not supplements:
            raise HTTPException(status_code=500, detail="No se pudo generar una lista de suplementos válida tras varios intentos.")

        # Guardar la interacción en memoria
        memory.save_context(
            {
                "input": f"Objetivo: {goal}, Tipo de dieta: {diet_type}, Nivel de actividad: {activity_level}, Restricciones: {restrictions}, Presupuesto: {budget}"
            },
            {"output": supplements}
        )

        # Se guarda la lista de suplementos en la base de datos
        connection = get_connection()
        with connection.cursor() as cursor:
            insert_query = '''
            INSERT INTO supplements (goal, diet_type, activity_level, restrictions, budget, recommendations)
            VALUES (%s, %s, %s, %s, %s, %s);
            '''
            cursor.execute(insert_query, (goal, diet_type, activity_level, restrictions, budget, supplements))
            connection.commit()

        # Le aplicamos formato (negritas y colores) al contenido generado
        supplements = supplements.replace("Nombre del suplemento:", "<span class='font-bold text-pink-400'>Nombre del suplemento:</span>")
        supplements = supplements.replace("Beneficios clave:", "<span class='font-bold'>Beneficios clave:</span>")
        supplements = supplements.replace("Cómo y cuándo tomarlo:", "<span class='font-bold'>Cómo y cuándo tomarlo:</span>")

        # Renderizar la respuesta en HTML
        return templates.TemplateResponse(
            "supplements.html",
            {
                "request": request,
                "message": f"¡Aquí tienes tus recomendaciones personalizadas de suplementos alimenticios! Diseñadas para ayudarte a alcanzar tu objetivo de {goal.lower()} y adaptadas a tu dieta {diet_type.lower()} con un presupuesto {budget.lower()}.",
                "supplements": supplements,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar recomendaciones de suplementos: {e}")

    finally:
        if connection:
            connection.close()



