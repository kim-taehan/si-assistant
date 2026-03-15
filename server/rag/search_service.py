from rag.vector_store import load_vectorstore


def search(query: str, k: int = 10):

    vectorstore = load_vectorstore()

    return vectorstore.max_marginal_relevance_search(query, k=10, fetch_k=30)
