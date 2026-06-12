from rag.vectordb import load_vector_db

vectordb = load_vector_db()


def retrieve_documents(
    query: str,
    filters: dict = None,
    k: int = 5
):

    try:

        docs = vectordb.similarity_search(
            query=query,
            k=k,
            filter=filters
        )

        return docs

    except Exception:

        return []