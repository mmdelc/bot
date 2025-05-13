from llama_index.readers.llama_parse import LlamaParse
from llama_index.core.schema import Document
from config import LLAMA_CLOUD_API_KEY

def load_documents(file_path: str) -> list[Document]:
    parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="markdown")
    print(f"Iniciando parsing del archivo: {file_path}")
    documents = parser.load_data(file_path)
    print(f"Documentos parseados: {len(documents)}")
    return documents
