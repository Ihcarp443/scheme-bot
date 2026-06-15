import json

from graph.state import GraphState
from services.llm_service import model
from rag.retriever import retrieve_documents


FILTER_PROMPT = """
You are an intelligent query parser for a government policy chatbot.

Your task is to extract structured filters from the user query.

Extract the following fields if present:

- policy_name
- sector
- section

Rules:

- Only extract values if clearly mentioned
- Normalize section names to one of:
    eligibility
    benefits
    application_process
    documents_required
    faq
    exclusions

- If not found, set value as null

Return ONLY valid JSON.

Example:

Query:
"What are benefits of PM Kisan?"

Output:
{{
    "policy_name": "PM Kisan",
    "section": "benefits",
    "sector": null
}}

Now process:

Query:
"{query}"
"""


def extract_filters_from_llm_node(state: GraphState):
    print('Extracting filters from LLM for query:', state["query_en"])

    query = state["query_en"]

    prompt = FILTER_PROMPT.format(
        query=query
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
        if v not in [None, "", "null"]
    }

    print("Extracted Filters:", filters)

    return {
        "filters": filters
    }


def retrieve_node(state: GraphState):
    print('Retrieving documents for query:', state["query_en"])

    query = state["query_en"]

    filters = state.get(
        "filters",
        {}
    )

    if filters:

        try:

            results = retrieve_documents(
                query=query,
                filters=filters
            )

        except Exception:

            results = []

    else:

        results = retrieve_documents(
            query
        )

    if not results:

        print(
            "No results with filters. Trying fallback..."
        )

        if "policy_name" in filters:

            relaxed = {
                "policy_name":
                filters["policy_name"]
            }

            try:

                results = retrieve_documents(
                    query,
                    filter=relaxed
                )

            except Exception:

                pass

    if not results:

        print(
            "No results from fallback. Using pure semantic search..."
        )

        results = retrieve_documents(
            query
        )

    print(
        f"Retrieved {len(results)} documents"
    )

    return {
        "docs": results
    }
    
    
# import json

# from graph.state import GraphState
# from services.llm_service import model
# from rag.retriever import retrieve_documents


# FILTER_PROMPT = """
# You are an intelligent query parser for a government policy chatbot.

# Your task is to extract structured filters from the user query.

# Extract the following fields if present:

# - policy_name
# - sector
# - section

# Rules:

# - Only extract values if clearly mentioned
# - Normalize section names to one of:
#     eligibility
#     benefits
#     application_process
#     documents_required
#     faq
#     exclusions

# - If not found, set value as null

# Return ONLY valid JSON.

# Example:

# Query:
# "What are benefits of PM Kisan?"

# Output:
# {{
#     "policy_name": "PM Kisan",
#     "section": "benefits",
#     "sector": null
# }}

# Now process:

# Query:
# "{query}"
# """




# def extract_filters_from_llm_node(state: GraphState):
#     print('Extracting filters from LLM for query:', state["query_en"])

#     query = state["query_en"]

#     prompt = FILTER_PROMPT.format(
#         query=query
#     )
#     print("Filter Extraction Prompt:", prompt)
#     response = model.invoke(prompt)
#     print("LLM Filter Extraction Response:", response.content)

#     try:

#         filters = json.loads(
#             response.content
#         )

#     except Exception:

#         filters = {}

#     # print(type(filters))
#     print("Extracted Filters:", filters)
#     filters = {
#         k: v
#         for k, v in filters.items()
#         if v not in [None, "", "null"]
#     }

#     print("Extracted Filters:", filters)

#     return {
#         "filters": filters
#     }


# def retrieve_node(state: GraphState):
#     print('Retrieving documents for query:', state["query_en"])

#     query = state["query_en"]

#     filters = state.get(
#         "filters",
#         {}
#     )

#     if filters:

#         try:

#             results = retrieve_documents(
#                 query=query,
#                 filters=filters
#             )

#         except Exception:

#             results = []

#     else:

#         results = retrieve_documents(
#             query
#         )

#     if not results:

#         print(
#             "No results with filters. Trying fallback..."
#         )

#         if "policy_name" in filters:

#             relaxed = {
#                 "policy_name":
#                 filters["policy_name"]
#             }

#             try:

#                 results = retrieve_documents(
#                     query,
#                     filter=relaxed
#                 )

#             except Exception:

#                 pass

#     if not results:

#         print(
#             "No results from fallback. Using pure semantic search..."
#         )

#         results = retrieve_documents(
#             query
#         )

#     print(
#         f"Retrieved {len(results)} documents ,{results}"
#     )

#     return {
#         "docs": results
#     }