
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def create_vector_db(documents):
    
    embedding = OpenAIEmbeddings()
    
    ids = [str(doc.metadata["id"]) for doc in documents]
    
    Chroma.from_documents(
        documents = documents,
        embedding = embedding,
        persist_directory="data/chroma_db",
        ids = ids
    )
    
    
    