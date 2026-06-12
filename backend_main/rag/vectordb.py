from langchain_community.vectorstores import FAISS

from rag.embeddings import embeddings


def load_vector_db():

    vectordb = FAISS.load_local(
        "data/Scheme_DB",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectordb


def get_retriever():

    vectordb = load_vector_db()

    return vectordb.as_retriever(
        search_kwargs={"k": 5}
    )