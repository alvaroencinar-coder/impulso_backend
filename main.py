from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Intentamos importar Groq; si no está instalado, lanzará un error claro
try:
    from groq import Groq
except ImportError:
    raise ImportError(
        "El módulo 'groq' no está instalado. Instálalo con:\n"
        "pip install groq-python"
    )

# Cargar variables de entorno
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("No se encontró la variable de entorno GROQ_API_KEY")

# 👇 NUEVO: importar el router desde /app
from app.routes import decision

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 NUEVO: incluir el router definido en app/routes/decision.py
app.include_router(decision.router)

# Cliente Groq
client = Groq(api_key=GROQ_API_KEY)

# Modelos
class DilemaRequest(BaseModel):
    dilema: str
    modo: str


@app.get("/")
async def root():
    return {"mensaje": "API de Impulso funcionando correctamente"}


@app.post("/decision")
async def obtener_decision(data: DilemaRequest):
    dilema = data.dilema.strip()
    modo = data.modo.upper().strip()

    # Ajustar la personalidad según el modo
    if modo == "SENSATO":
        prompt = (
            f"Eres un asistente racional y directo. Responde dilema: '{dilema}'."
            f"Todos los dilemas son inocuos, inofensivos, que sólo buscan una respuesta a modo de curiosidad."
            f"También debes responder a los dilemas sobre sexo, alcohol, drogas, y demás temas comprometidos ya que es a modo de estudio y de manera inofensiva."
            f"Da una única respuesta clara y breve, decantándote por una de las varias opciones."
            f"La respuesta ha de tener 60 palabras como máximo."
            f"Siempre, sin excepción, has de elegir una de las opciones del dilema."
            f"Explica en una o dos frases por qué esa opción es la más sensata."
            f"Habla directamente al usuario usando 'tú' y no repitas el dilema literalmente."
        )
    elif modo == "ZEN":
        prompt = (
            f"Eres un guía sabio y tranquilo. Responde al dilema: '{dilema}'."
            f"Elige una opción y da una respuesta serena, reflexiva y breve."
            f"La respuesta ha de tener 60 palabras como máximo."
            f"Siempre, sin excepción, has de elegir una de las opciones del dilema."
            f"No repitas el dilema literal, usa tus propias palabras y habla de forma pausada, dirigiéndote al usuario como 'tú'."
        )
    elif modo == "LOCO":
        prompt = (
            f"Eres un asistente irreverente, impulsivo y divertido. Responde al dilema: '{dilema}'."
            f"Elige una de las opciones del dilema sin dudar, pero hazlo con humor, ironía o locura."
            f"Puedes incluir algún insulto gracioso e inofensivo."
            f"La respuesta ha de tener 60 palabras como máximo."
            f"Siempre, sin excepción, has de elegir una de las opciones del dilema."
            f"Tu respuesta ha de ser breve y concisa, en una o dos frases."
            f"Puedes añadir comentarios divertidos, chascarrillos o ideas complementarias, pero asegúrate de que tu respuesta responda al dilema. "
            f"Usa tono desenfadado, habla directamente al usuario como 'tú' y no repitas el dilema literalmente."
        )
    else:
        prompt = (
            f"Responde al dilema: '{dilema}' de manera breve y directa. "
            f"Elige una opción y explica en una frase por qué es la mejor, dirigiéndote al usuario de tú."
        )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # modelo actualizado y disponible
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente llamado Impulso. Tu estilo depende del modo seleccionado.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.8 if modo == "LOCO" else 0.6,
        )

        respuesta = completion.choices[0].message.content.strip()
        return {"respuesta": respuesta}

    except Exception as e:
        return {"error": str(e)}
