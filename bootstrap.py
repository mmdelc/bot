# ==================== bootstrap.py ====================
import os
from dotenv import load_dotenv
import asyncio
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ⚠️ Desactivar uvloop
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Carga el .env
load_dotenv()
logger.info("Environment variables loaded")

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
    try:
        logger.info("🚀 Iniciando servidor...")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Files in directory: {os.listdir('.')}")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),  # Use PORT from Railway
            reload=False,  # Disable reload in production
            loop="asyncio",
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        raise



