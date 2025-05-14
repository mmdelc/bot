# ==================== main.py ====================
import nest_asyncio
nest_asyncio.apply()

import csv
import logging
import os
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# FastAPI app & CORS
# ---------------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Ajusta en producción si lo necesitas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Variables globales que se llenan en startup
# ---------------------------------------------------------------------
query_engine: Optional[object] = None
information_agent: Optional[object] = None

# ---------------------------------------------------------------------
# Endpoints de salud y raíz
# ---------------------------------------------------------------------
@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

# ---------------------------------------------------------------------
# Carga diferida de componentes pesados
# ---------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    global query_engine, information_agent
    t0 = time.perf_counter()

    try:
        from llm_engine import setup_query_engine
        from phi.assistant import Assistant
        from phi.model.openai import OpenAIChat
        from phi.tools.duckduckgo import DuckDuckGo

        logger.info("Inicializando componentes …")

        # Motor de consulta local
        query_engine = setup_query_engine("ministros.xlsx")
        logger.info("Query engine initialized")

        # Asistente LLM (instrucciones originales en español)
        information_agent = Assistant(
            name="Informador Judicial",
            model=OpenAIChat(model="gpt-4o-mini"),
            tools=[DuckDuckGo()],
            instructions=[
                "Eres un asistente de información para tomar mejores decisiones en la elección judicial en México 2025 relativa a los candidatos de la Suprema Corte de Justicia. Ayuda a los usuarios a obtener la información más relevante:"
                "Contesta en español a menos que se te solicite otro idioma."
                "Eres especialista en analizar contenido legal, electoral y judicial relacionado con candidatos y procesos en la elección a la Suprema Corte de Justicia de la Nación en México 2025.",
                "Tu objetivo es ayudar a los usuarios a entender mejor la información pública sobre candidaturas, antecedentes legales y posturas institucionales del INE.",
                "Sigue estas directrices estrictamente:",
                "1. Explica los temas jurídicos y electorales de forma sencilla, pero mantén un nivel académico universitario.",
                "2. Mantén respuestas claras, concisas, ordenadas y sin rodeos innecesarios.",
                "3. Usa lenguaje neutral y evita juicios de valor o opiniones personales.",
                "4. Cita fuentes y proporciona enlaces directos a páginas oficiales, investigaciones y medios confiables.",
                "5. Divide los temas complejos en partes más pequeñas cuando sea necesario.",
                "6. Si no sabes la respuesta, di explícitamente que no sabes. Nunca inventes información.",
                "7. Verifica que la información esté actualizada antes de responder.",
                "8. Puedes usar buscadores o herramientas en línea para obtener información reciente.",
                "Termina siempre las respuestas con: 'Toda la información debe ser verificada y contrastada con las fuentes de información",
            ],
            show_tool_calls=True,
        )
        logger.info("Assistant initialized")
        logger.info("Startup completed in %.2f s", time.perf_counter() - t0)

    except Exception:
        logger.exception("Error during startup")

# ---------------------------------------------------------------------
# Endpoint principal de consulta
# ---------------------------------------------------------------------
@app.get("/query/")
def query_llm(q: str):
    if query_engine is None or information_agent is None:
        raise HTTPException(
            status_code=503,
            detail="El asistente aún se está inicializando. Intenta de nuevo en unos segundos.",
        )

    try:
        # Respuesta proveniente del motor local
        local_response = str(query_engine.query(q))

        # Respuesta del LLM
        agent_response = "".join(chunk for chunk in information_agent.chat(q))

        # Fusión de ambas respuestas
        fusion = f"{local_response.strip()}\n\n{agent_response.strip()}"

        # Prompt de reescritura (en español y correctamente interpolado)
        prompt_reescritura = (
            f"Dale más peso a la información proveniente de local_response y reescribe el siguiente texto de forma clara, natural y unificada:\n\n{fusion}"
        )

        final_response = "".join(
            chunk for chunk in information_agent.chat(prompt_reescritura)
        ).strip()

        # Registro en CSV
        with open("logs.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([datetime.utcnow().isoformat(), q, fusion])

        return {"response": final_response}

    except Exception as e:
        import traceback

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc(),
                "openai_api_key": "present" if os.getenv("OPENAI_API_KEY") else "missing",
                "llama_api_key": "present"
                if os.getenv("LLAMA_CLOUD_API_KEY")
                else "missing",
            },
        )

# ---------------------------------------------------------------------
# Endpoint de registro manual
# ---------------------------------------------------------------------
@app.post("/log")
async def guardar_log(item: dict):
    with open("logs.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            [datetime.utcnow().isoformat(), item.get("pregunta"), item.get("respuesta")]
        )
    return {"status": "ok"}
