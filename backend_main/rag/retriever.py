from rag.vectordb import load_vector_db

vectordb = load_vector_db()


def retrieve_documents(
    query: str,
    k: int = 5
):

    try:

        docs = vectordb.similarity_search(
            query=query,
            k=k
        )

        return docs

    except Exception:

        return []