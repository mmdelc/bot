# ==================== main.py ====================
import nest_asyncio
nest_asyncio.apply()
from fastapi import FastAPI
app=FastAPI()
from llm_engine import setup_query_engine
from config import OPENAI_API_KEY
from datetime import datetime
#from crewai import Assistant
#from crewai_tools import DuckDuckGo
from langchain_openai import ChatOpenAI as OpenAIChat
from phi.assistant import Assistant
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import csv

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["https://tu-url.ngrok.io"] si quieres limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


query_engine = setup_query_engine("ministros.xlsx")

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
    show_tool_calls=True
)

@app.get("/query/")
def query_llm(q: str):
    try:
        local_response = str(query_engine.query(q))
        agent_response = "".join(part for part in information_agent.chat(q))
        
        fusion = f"{local_response.strip()}\n\n{agent_response.strip()}"
        
        prompt_reescritura=("Dale más peso a {local_response} en la respuesta y reescribe esta información de forma clara, natural y unificada:\n\n"
                            f"{fusion}")

        final_response="".join(part for part in information_agent.chat(prompt_reescritura)).strip()

        with open("logs.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), q, fusion])

        return {"response": final_response}

    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "api_key_status": "Present" if os.getenv("OPENAI_API_KEY") else "Missing",
            "llama_key_status": "Present" if os.getenv("LLAMA_CLOUD_API_KEY") else "Missing"
        }
        return JSONResponse(status_code=500, content=error_details)


@app.post("/log")
async def guardar_log(item: dict):
    with open("logs.csv", mode="a", newline="", encoding="utf-8", errors="ignore") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), item.get("pregunta"), item.get("respuesta")])
    return {"status": "ok"}

@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))