from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import random
from app.database.database import get_connection
from app.config import client 


router = APIRouter()

memory = ConversationBufferMemory(return_messages=True, memory_key="history", input_key="input")

templates = Jinja2Templates(directory="app/templates")  # Configuración de templates

# Configurar memoria conversacional
memory = ConversationBufferMemory()

# PromptTemplate mejorado
template = """
Eres un asistente virtual experto en fitness y salud. Tu tarea es crear rutinas de ejercicios personalizadas 
según las necesidades del usuario. Cada rutina debe incluir un calentamiento inicial, ejercicios principales 
y un enfriamiento final. Proporciona la rutina de forma clara, organizada y adecuada para el nivel del usuario.
Recuerda poner la duración en cada ejercicio para que se adapte perfectamente al tiempo indicado por el usuario.
Los comentarios adicionales finales deben ser muy cortos y sencillos en caso de que los haya. En idioma español de España.

Información proporcionada:
- Nivel de experiencia: {level}
- Duración total: {time} minutos
- Equipamiento disponible: {equipment}
- Objetivo principal: {goal}

Estructura de la respuesta:
1. Calentamiento:
   - Ejercicio 1: Descripción breve
   - Ejercicio 2: Descripción breve
2. Ejercicios principales:
   - Ejercicio 1: Descripción breve
   - Ejercicio 2: Descripción breve
   - Ejercicio 3: Descripción breve
3. Enfriamiento:
   - Ejercicio 1: Descripción breve
   - Ejercicio 2: Descripción breve

Incluye comentarios adicionales si es necesario.
"""
prompt_template = PromptTemplate(input_variables=["level", "time", "equipment", "goal"], template=template)

# Función para evaluar la calidad de la respuesta
def evaluate_response(response: str) -> dict:
    """
    Evalúa la calidad de la respuesta generada por el modelo.
    Retorna un diccionario con los resultados de la evaluación.
    """
    evaluation = {
        "coherencia": "1. Calentamiento" in response and "3. Enfriamiento" in response,
        "relevancia": "Ejercicio" in response,
        "claridad": len(response.splitlines()) > 5,  # Debe tener varias líneas
        "completitud": len(response) > 100  # Mínimo de caracteres en la respuesta
    }
    evaluation["aprobado"] = all(evaluation.values())  # Aprueba solo si todos los criterios se cumplen
    return evaluation

# Ruta GET para renderizar el formulario
@router.get("/routine", response_class=HTMLResponse)
async def get_routine_page(request: Request):
    """
    Renderiza la página HTML para solicitar los datos de rutina.
    """
    return templates.TemplateResponse("routine.html", {"request": request})

# Ruta POST para procesar el formulario y mostrar el resultado
@router.post("/routine", response_class=HTMLResponse)
async def post_routine(request: Request, level: str = Form(...), time: int = Form(...), equipment: str = Form(...), goal: str = Form(...)):
    """
    Genera una rutina de ejercicios personalizada utilizando memoria conversacional.
    Evalúa su calidad y, si no cumple, solicita una nueva respuesta.
    Guarda la rutina generada en la base de datos y la muestra al usuario.
    """

    connection = None  # Inicializar la variable

    try:
        # Recuperar el historial de memoria
        context = memory.load_memory_variables({})
        previous_messages = context.get("history", "")

        # Generar el contenido del prompt con el historial incluido
        prompt_content = (
            f"Historial previo:\n{previous_messages}\n\n"
            + prompt_template.format(level=level, time=time, equipment=equipment, goal=goal)
        )

        # Inicializar variables
        max_retries = 3  # Número máximo de intentos para obtener una respuesta válida
        retries = 0
        evaluation = {"aprobado": False}
        routine = ""

        # Generar respuestas hasta cumplir los criterios o agotar intentos
        while not evaluation["aprobado"] and retries < max_retries:
            # Crear el mensaje para el modelo
            messages = [
                {
                    "role": "user",
                    "content": prompt_content
                }
            ]

            # Solicitar la respuesta al modelo
            completion = client.chat.completions.create(
                model="microsoft/Phi-3.5-mini-instruct",
                messages=messages,
                max_tokens=750
            )

            # Extraer la respuesta generada
            routine = completion.choices[0].message.content

            # Evaluar la calidad de la respuesta
            evaluation = evaluate_response(routine)
            retries += 1
            print(f"Intento número {retries}: Evaluación de calidad: {evaluation}")

        # Guardar la interacción en memoria
        memory.save_context(
            {"input": f"Nivel: {level}, Tiempo: {time}, Equipamiento: {equipment}, Objetivo: {goal}"},
            {"output": routine}
        )

        # Lista de mensajes motivacionales
        motivational_messages = [
            f"¡Genial! Hemos preparado una rutina personalizada para ti. Es perfecta para un nivel {level.lower()}, con una duración de {time} minutos. Usaremos {equipment.lower()} para ayudarte a alcanzar tu objetivo de {goal.lower()}. ¡A por ello!",
            f"¡Aquí tienes tu rutina! Diseñada especialmente para un nivel {level.lower()} y enfocada en tu meta de {goal.lower()}. Prepárate para {time} minutos de trabajo con {equipment.lower()} y logra tus objetivos.",
            f"¡Vamos a entrenar! Esta rutina está creada justo para ti: nivel {level.lower()}, {time} minutos, y utilizando {equipment.lower()} para que consigas {goal.lower()}. ¡Disfrútala y da lo mejor de ti!",
            f"¡Todo listo! Tu rutina personalizada para un nivel {level.lower()} está preparada. Con una duración de {time} minutos y utilizando {equipment.lower()}, estarás un paso más cerca de {goal.lower()}. ¡Es tu momento!",
            f"¡Rutina personalizada entregada! Perfecta para un nivel {level.lower()}, con {time} minutos de duración, enfocada en {goal.lower()} y usando {equipment.lower()}. ¡Éxito en tu entrenamiento!"
        ]

        # Elegir un mensaje al azar
        user_message = random.choice(motivational_messages)

        # Guardar la rutina generada en la base de datos
        connection = get_connection()
        connection.select_db("database_api_llm")  # Seleccionar la base de datos específica
        with connection.cursor() as cursor:
            insert_query = '''
            INSERT INTO routines (level, time, equipment, goal, routine)
            VALUES (%s, %s, %s, %s, %s);
            '''
            cursor.execute(insert_query, (level, time, equipment, goal, routine))
            connection.commit()

        # Responder al usuario con la rutina, mensaje motivacional y datos ingresados
        return templates.TemplateResponse("routine.html", {
            "request": request,
            "routine": routine,
            "message": user_message,  # Enviar el mensaje al template
            "level": level,
            "time": time,
            "equipment": equipment,
            "goal": goal
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar rutina: {e}")

    finally:
        if connection:
            connection.close()




