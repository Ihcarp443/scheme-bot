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


def extract_filters_from_llm_node(state: GraphState):
    print('Extracting filters from LLM for query:', state["query_en"])
    FILTER_PROMPT = """
        You are an intelligent query parser for a government policy chatbot.

        You are given:
        - User Query
        - Expanded Query
        - User Memory

        Your task is to extract structured filters.

        User Memory:
        {memory}

        Original Query:
        {query}

        Expanded Query:
        {expanded_query}

        Extract:

        - policy_name
        - sector
        - section

        Rules:
        - Prefer memory ONLY for missing context
        - DO NOT assume new attributes
        - DO NOT hallucinate eligibility conditions
        - Only extract what is clearly supported
        - Normalize section to:
          eligibility, benefits, application_process, documents_required, faq, exclusions

        Return ONLY JSON.

        For example (may contains additional key_values):
        Query:
        "What are benefits of PM Kisan?"

        Output:
        {{
            "policy_name": "PM Kisan",
            "section": "benefits",
            "sector": null
        }}
        """
    query = state["query_en"]
    memory=state.get("memory",{})
    new_data=rewrite_query(query,memory)
    expanded_query=new_data["expanded_query"]
    prompt = FILTER_PROMPT.format(
        query=query,
        expanded_query=new_data["expanded_query"],
        memory=json.dumps(memory, indent=2)
    )
    # print("Filter Extraction Prompt:", prompt)
    response = model.invoke(prompt)
    # print("LLM Filter Extraction Response:", response.content)

    try:
        filters = json.loads(
            response.content
        )

    except Exception:

        filters = {}

    # print(type(filters))
    print("Extracted Filters:", filters)
    filters = {
        k: v
        for k, v in filters.items()
        if v not in [None, "", "null","None"]
    }

    print("Extracted Filters:", filters)

    return {
        "filters": filters,
        "expanded_query": expanded_query,
        "keywords": new_data["keywords"]
    }

def retrieve_node(state: GraphState):
    print("Retrieving documents...")

    # 1. Get both queries
    original_query = state["query_en"]
    expanded_query = state.get("expanded_query", original_query)

    # 2. Merge queries (your chosen approach)
    query = f"{expanded_query}\n{original_query}"

    # 3. Get filters
    filters = state.get("filters", {})

    results = []

    # 4. Primary retrieval (hybrid)
    try:
        results = retrieve_documents(
            query=query,
            filters=filters
        )
    except Exception:
        results = []

    # 5. Fallback 1: relaxed filter (ONLY policy_name)
    if not results:
        print("No results with filters. Trying fallback...")

        if "policy_name" in filters:
            try:
                results = retrieve_documents(
                    query=query,
                    filters={"policy_name": filters["policy_name"]}
                )
            except Exception:
                pass

    # 6. Fallback 2: semantic only
    if not results:
        print("No results from fallback. Using pure semantic search...")
        try:
            results = retrieve_documents(query)
        except Exception:
            results = []

    print(f"Retrieved {len(results)} documents")

    return {"docs": results}




# def retrieve_node(state: GraphState):
#     print('Retrieving documents for query:', state["query_en"])

#     query = state["query_en"]

#     filters = state.get(
#         "filters",
#         {}
#     )

#     if filters:
#         try:
#             results = retrieve_documents(query=query,filters=filters)
#         except Exception:
#             results = []
#     else:
#         results = retrieve_documents(query)

#     if not results:
#         print("No results with filters. Trying fallback...")

#         if "policy_name" in filters:
#             relaxed = {
#                 "policy_name":
#                 filters["policy_name"]
#                 }
#             try:
#                 results = retrieve_documents(
#                     query,
#                     filter=relaxed
#                 )

#             except Exception:
#                 pass
#     if not results:
#         print("No results from fallback. Using pure semantic search...")
#         results = retrieve_documents(query)

#     print( f"Retrieved {len(results)} documents")

#     return {"docs": results}
    
     # FILTER_PROMPT = """
    #     You are an intelligent query parser for a government policy chatbot.

    #     Your task is to extract structured filters from the user query.

    #     Extract the following fields if present:

    #     - policy_name
    #     - sector
    #     - section

    #     Rules:

    #     - Only extract values if clearly mentioned
    #     - Normalize section names to one of:
    #         eligibility
    #         benefits
    #         application_process
    #         documents_required
    #         faq
    #         exclusions

    #     - If not found, set value as null

    #     Return ONLY valid JSON.

    #     Example:

    #     Query:
    #     "What are benefits of PM Kisan?"

    #     Output:
    #     {{
    #         "policy_name": "PM Kisan",
    #         "section": "benefits",
    #         "sector": null
    #     }}

    #     Now process:

    #     Query:
    #     "{query}"
    #     """