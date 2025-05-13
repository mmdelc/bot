# ==================== config.py ====================
import os
from dotenv import load_dotenv

# Cargar .env desde el directorio actual
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")


