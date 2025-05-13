# ==================== llm_engine.py ====================
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from config import OPENAI_API_KEY
from parser import load_documents

llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
Settings.embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)

def setup_query_engine(xlsx_path: str):
    documents = load_documents(xlsx_path)
    node_parser = MarkdownElementNodeParser(llm=llm, num_workers=4)
    nodes = node_parser.get_nodes_from_documents(documents[:5])
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
    index = VectorStoreIndex(nodes=base_nodes + objects, llm=llm)
    return index.as_query_engine(similarity_top_k=5, llm=llm)
