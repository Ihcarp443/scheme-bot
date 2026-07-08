import json

from graph.state import GraphState
from services.llm_service import model
from rag.retriever import retrieve_documents

def rewrite_query(query,memory):
    print("Rewriting query")
    og_query=query
    memory=memory
    REWRITE_PROMPT = """
        You are a query rewriting engine for a government scheme assistant.

        You are given:
        1. User Query
        2. User Memory (may contain partial info)

        Task:
        Rewrite the query for document retrieval.

        IMPORTANT RULES:
        - DO NOT hallucinate or invent new attributes
        - ONLY use information present in memory
        - Keep original intent unchanged
        - Do NOT answer the question
        - Output must be retrieval optimized

        Return ONLY valid JSON.

        Format:
        {{
          "original_query": "...",
          "expanded_query": "...",
          "keywords": ["..."]
        }}

        User Memory:
        {memory}

        User Query:
        {query}
        """
    
    prompt = REWRITE_PROMPT.format(
        query=og_query,
        memory=json.dumps(memory, indent=2)
    )

    response = model.invoke(prompt)

    try:
        content = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(content)
    except Exception:
        result = {
            "original_query": og_query,
            "expanded_query": og_query,
            "keywords": []
        }

    print("Query Rewrite Result:", result)
    data= {
        "original_query":result["original_query"],
        "expanded_query": result["expanded_query"],
        "keywords": result.get("keywords", [])
    }
    return data


def retrieve_node(state: GraphState):
    print("Retrieving documents...")

    # 1. Get both queries
    original_query = state["query_en"]
    expanded_query = state.get("expanded_query", original_query)

    # 2. Merge queries (your chosen approach)
    query = f"{expanded_query}\n{original_query}"

    results = []

    # 4. Primary retrieval (hybrid)
    try:
        results = retrieve_documents(
            query=query,
        )
    except Exception:
        results = []

    print(f"Retrieved {len(results)} documents")

    return {"docs": results}