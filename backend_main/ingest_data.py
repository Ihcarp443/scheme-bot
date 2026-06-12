import os
import json

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from rag.embeddings import embeddings


SCHEMES_FOLDER = "data/schemes"
DB_FOLDER = "data/Scheme_DB"


def load_json_files(folder_path):

    all_chunks = []

    for file in os.listdir(folder_path):

        if not file.endswith(".json"):
            continue

        file_path = os.path.join(
            folder_path,
            file
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        policy_name = data["policy_name"]
        sector = data["sector"]

        for section, content in data["sections"].items():

            # String section
            if isinstance(content, str):

                all_chunks.append({
                    "text":
                    f"{policy_name} {section}: {content}",
                    "metadata": {
                        "policy_name": policy_name,
                        "sector": sector,
                        "section": section
                    }
                })

            # List section
            elif isinstance(content, list):

                if section == "faq":

                    for faq in content:

                        all_chunks.append({
                            "text":
                            f"{policy_name} FAQ\n"
                            f"Q: {faq['question']}\n"
                            f"A: {faq['answer']}",
                            "metadata": {
                                "policy_name": policy_name,
                                "sector": sector,
                                "section": "faq"
                            }
                        })

                else:

                    combined = "\n".join(
                        f"- {item}"
                        for item in content
                    )

                    all_chunks.append({
                        "text":
                        f"{policy_name} {section}\n{combined}",
                        "metadata": {
                            "policy_name": policy_name,
                            "sector": sector,
                            "section": section
                        }
                    })

    return all_chunks


def convert_to_documents(chunks):

    docs = []

    for chunk in chunks:

        docs.append(
            Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            )
        )

    return docs


def build_vectordb():

    print("Loading scheme files...")

    chunks = load_json_files(
        SCHEMES_FOLDER
    )

    print(
        f"Loaded {len(chunks)} chunks"
    )

    documents = convert_to_documents(
        chunks
    )

    print(
        f"Created {len(documents)} documents"
    )

    vectordb = FAISS.from_documents(
        documents,
        embeddings
    )

    os.makedirs(
        DB_FOLDER,
        exist_ok=True
    )

    vectordb.save_local(
        DB_FOLDER
    )

    print(
        f"Vector DB saved to {DB_FOLDER}"
    )


if __name__ == "__main__":
    build_vectordb()