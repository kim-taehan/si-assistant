from rag.loader import get_loader
from rag.splitter import split_documents
from rag.vector_store import load_vectorstore, save_vectorstore
from langchain_community.vectorstores import FAISS
from rag.vector_store import embeddings


def add_document(document):

    loader = get_loader(document)

    docs = loader.load()

    chunks = split_documents(docs)

    for chunk in chunks:
        chunk.metadata["document_id"] = document.id
        chunk.metadata["file_name"] = document.file_name

    vectorstore = load_vectorstore()

    if vectorstore:
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)

    save_vectorstore(vectorstore)
