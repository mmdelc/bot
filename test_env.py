import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print API keys (first few characters only)
openai_key = os.getenv("OPENAI_API_KEY")
llama_key = os.getenv("LLAMA_CLOUD_API_KEY")

print("OpenAI API Key:", openai_key[:10] + "..." if openai_key else "Not found")
print("Llama Cloud API Key:", llama_key[:10] + "..." if llama_key else "Not found") 