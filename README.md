# Salus AI

**Salus AI** es un asistente personal de salud inteligente desarrollado con FastAPI. Este proyecto permite a los usuarios generar rutinas de ejercicio personalizadas, planes de alimentación adaptados y recomendaciones de suplementos alimenticios. Utiliza inteligencia artificial (Hugging Face) para proporcionar respuestas personalizadas según las necesidades del usuario y está diseñado para ejecutarse de manera eficiente en Docker.

## Características

- **Generación de rutinas de ejercicio:**
  - Personalizadas según nivel, tiempo, equipamiento y objetivo del usuario.
- **Planes de alimentación:**
  - Adaptados a las preferencias y restricciones alimenticias.
- **Recomendaciones de suplementos alimenticios:**
  - Basadas en el objetivo, dieta, nivel de actividad física, restricciones y presupuesto.
- **Interfaz web amigable:**
  - Páginas diseñadas con **Tailwind CSS** para una experiencia de usuario moderna.
- **Dockerización:**
  - Portabilidad y fácil despliegue utilizando **Docker**.

---

## Requisitos

- **Python 3.10+**
- **Docker**
- Base de datos MySQL.
- API Key de Hugging Face.

---

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone "https://github.com/RubenVeledo/api_asistentesalud.git"
2. **Configurar variables de entorno:**
  - Ver archivo .env.example
    
3. **Iniciar la aplicación en local**
   - uvicorn app.main:app --reload

---

## Endpoints principales

**Página principal:**
- GET /
  - Renderiza la página inicial con opciones de navegación.

**Generar rutinas:**
- GET /routine
- POST /routine
  - Parámetros: level, time, equipment, goal

**Planes de alimentación:**
- GET /dieta
- POST /dieta
  - Parámetros: goal, preferences

**Recomendaciones de suplementos:**
- GET /suplementos
- POST /suplementos
  - Parámetros: goal, diet_type, activity_level, restrictions, budget
 
---

## Pruebas
Ejecutar los test con pytest (test_endpoints.py)

---

## Contacto
Si tienes dudas o sugerencias, no dudes en contactarme a través de mi perfil de GitHub o de mi LinkedIn https://www.linkedin.com/in/rubenveledo/.












