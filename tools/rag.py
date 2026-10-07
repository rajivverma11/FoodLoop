"""
tools/rag.py — Connect to the persistent FoodLoop vector database.
"""

from langchain_chroma import Chroma
from config import embeddings


CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "FoodLoopMenu"


vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)


menu_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)


