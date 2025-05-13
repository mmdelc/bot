import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

# Verificar la clave API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ No se encontró OPENAI_API_KEY en el archivo .env")
    exit(1)

print("✅ OPENAI_API_KEY encontrada")

# Crear cliente de OpenAI
client = OpenAI(api_key=api_key)

try:
    # Intentar una llamada simple a la API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hola, esto es una prueba."}]
    )
    print("✅ Conexión exitosa con OpenAI")
    print("Respuesta:", response.choices[0].message.content)
except Exception as e:
    print("❌ Error al conectar con OpenAI:")
    print(str(e)) 