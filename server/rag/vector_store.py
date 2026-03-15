import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

VECTOR_DB_PATH = "vector_db"

embeddings = OllamaEmbeddings(model="bge-m3")


def load_vectorstore():

    if os.path.exists(VECTOR_DB_PATH):
        return FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    return None


def save_vectorstore(vectorstore):

    vectorstore.save_local(VECTOR_DB_PATH)
