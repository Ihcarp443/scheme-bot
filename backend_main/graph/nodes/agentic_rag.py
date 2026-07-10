"""
graph/nodes/agentic_rag.py

Real ReAct agent implementation for Agentic RAG.
The LLM decides which tool to call, sees the result, and decides
whether to call another tool or stop -- at every step, not just once.
"""

import json
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from services.llm_service import model
from graph.state import GraphState
from rag.retriever import retrieve_documents
from db.memory import get_memories
from ddgs import DDGS


# ==========================================================
# TOOLS
# Each tool is self-contained. The agent decides which to call,
# in what order, how many times, and when to stop.
# ==========================================================

@tool
def fetch_user_memory(user_id: str) -> str:
    """Retrieve the user's long-term profile (age, income, location, occupation, etc).
    Use this when the query is personal (e.g. 'my eligibility', 'schemes for me')
    and you don't yet have enough context to search effectively."""
    try:
        memories = get_memories(user_id)
        return json.dumps(memories) if memories else "No memory found for this user."
    except Exception as e:
        return f"Memory fetch failed: {e}"


@tool
def rewrite_query(query: str, memory_json: str = "{}") -> str:
    """Expand a vague query into a retrieval-optimized query, optionally using
    known user memory (pass as JSON string). Use this when the raw query is
    too short or ambiguous for good retrieval, e.g. 'scheme for farmers' with
    no location/sector specified."""
    memory = json.loads(memory_json) if memory_json else {}

    prompt = f"""
    You are a query rewriting engine for a government scheme assistant.
    Rewrite the query for document retrieval.

    RULES:
    - DO NOT hallucinate or invent new attributes
    - ONLY use information present in memory
    - Keep original intent unchanged
    - Do NOT answer the question

    Return ONLY valid JSON: {{"expanded_query": "...", "keywords": ["..."]}}

    User Memory: {json.dumps(memory)}
    User Query: {query}
    """
    response = model.invoke(prompt)
    try:
        content = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(content)
        return json.dumps(result)
    except Exception:
        return json.dumps({"expanded_query": query, "keywords": []})

# @tool
# def extract_filters(query: str) -> str:
#     """Extract structured filters (policy_name, sector, section) from the query.
#     Use this before FAISS retrieval when the query mentions a specific scheme
#     or a specific topic (eligibility, benefits, documents, etc)."""
#     prompt = f"""
#     Extract structured filters from this government scheme query.

#     Extract: policy_name, sector, section
#     Normalize section to: eligibility, benefits, application_process,
#     documents_required, faq, exclusions

#     Return ONLY JSON. Use null for anything not clearly present.

#     Query: {query}
#     """
#     response = model.invoke(prompt)
#     try:
#         content = response.content.strip().replace("```json", "").replace("```", "")
#         filters = json.loads(content)
#         filters = {k: v for k, v in filters.items() if v not in [None, "", "null", "None"]}
#         return json.dumps(filters)
#     except Exception:
#         return json.dumps({})

@tool
def retrieve_faiss(query: str) -> str:
    """Search the internal government scheme knowledge base (FAISS).
    This is the primary source and should usually be tried first."""
    try:
        results = retrieve_documents(query=query)
        results_content = [doc.page_content for doc in results]
    
    except Exception as e:
        return f"FAISS retrieval failed: {e}"

    if not results:
        return "No results found in internal knowledge base."
    return json.dumps(results_content)


@tool
def duckduckgo_search(query: str) -> str:
    """Search the web. ONLY use this for newly launched schemes, recent
    amendments, government notifications, or anything the internal
    knowledge base doesn't have -- i.e. after FAISS has come up empty
    or clearly insufficient. Do not use as the first tool."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No web results found."
        return json.dumps([
            {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
            for r in results
        ])
    except Exception as e:
        return f"Web search failed: {e}"


# ==========================================================
# AGENT
# ==========================================================

SYSTEM_PROMPT = """You are an Agentic RAG assistant for a Government Scheme Assistant.

Your goal is to gather enough context to answer the user's query about
government schemes, then stop.

Guidelines:
- retrieve_faiss (internal KB) is the primary source -- try it first for
  most queries.
- Use fetch_user_memory only when the query is personal/needs profile context.
- Use rewrite_query only if the raw query is too vague to search well.
- Use duckduckgo_search ONLY as a supplement -- for recent news, new
  schemes, or amendments, or when retrieve_faiss returns nothing useful.
- Do not call the same tool more than twice.
- Once you have enough context, stop calling tools and summarize what you
  found -- do not answer the user's original question yourself, just
  report the gathered context.
"""

agentic_rag_agent = create_agent(
    model,
    tools=[fetch_user_memory, rewrite_query, retrieve_faiss, duckduckgo_search],
    system_prompt=SYSTEM_PROMPT
)

# ==========================================================
# GRAPH NODE
# ==========================================================

def agentic_rag_node(state: GraphState):
    print("===== Agentic RAG (ReAct) Started =====")

    query = state["query_en"]
    user_id = state.get("user_id", "")

    result = agentic_rag_agent.invoke({
        "messages": [HumanMessage(content=f"user_id: {user_id}\nquery: {query}")]
    })
    # print('Agent result', result)

    messages = result["messages"]
    docs = []
    web_context = ""
    tool_calls_made = []

    # print("messages", messages)
    for msg in messages:
        # print('msg',msg)
        tool_name = getattr(msg, "name", None)
        if tool_name == "retrieve_faiss":
            try:
                parsed = json.loads(msg.content)
                print("parsed",parsed)
                if isinstance(parsed, list):
                    docs.extend(parsed)
            except Exception:
                pass
            tool_calls_made.append("retrieve_faiss")

        elif tool_name == "duckduckgo_search":
            try:
                parsed = json.loads(msg.content)
                if isinstance(parsed, list):
                    web_context += "\n\n".join(
                        f"{item['title']}\n{item['snippet']}" for item in parsed
                    )
            except Exception:
                pass
            tool_calls_made.append("duckduckgo_search")

        elif tool_name:
            tool_calls_made.append(tool_name)

    final_summary = messages[-1].content if messages else ""

    print("Tools actually used:", tool_calls_made)
    
    return {
        "docs": docs,
        "web_context": web_context,
        "agent_trace": tool_calls_made,  
        "agent_summary": final_summary
    }