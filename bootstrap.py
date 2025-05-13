# ==================== bootstrap.py ====================
import os
from dotenv import load_dotenv
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ⚠️ Desactivar uvloop
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Carga el .env
load_dotenv()

# Validación
if not os.getenv("OPENAI_API_KEY"):
    logger.error("❌ Falta OPENAI_API_KEY")
    raise ValueError("Falta OPENAI_API_KEY")
else:
    logger.info("✅ OPENAI_API_KEY encontrada")

if not os.getenv("LLAMA_CLOUD_API_KEY"):
    logger.error("❌ Falta LLAMA_CLOUD_API_KEY")
    raise ValueError("Falta LLAMA_CLOUD_API_KEY")
else:
    logger.info("✅ LLAMA_CLOUD_API_KEY encontrada")

import uvicorn

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        loop="asyncio",  # 👈 esto desactiva uvloop
        log_level="debug"
    )



