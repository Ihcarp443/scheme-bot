from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.checkpoint.sqlite import SqliteSaver

from db.checkpoint import checkpoint_conn
from graph.state import GraphState

from graph.nodes.intent import (
    grievance_entry_node,
    intent,
    route_intent
)

from graph.nodes.retrieve import (
    extract_filters_from_llm_node,
    retrieve_node
)

from graph.nodes.answer import (
    answer_node
)

from graph.nodes.translate import (
    text_input_node,
    translate_node_for_user,
    dictate_answer_node,
    route_translation
)

from graph.nodes.grievance import (
    grievance_tool_node,
    grievance_formatter_node
)

from graph.nodes.general import (
    general_node
)

# from graph.nodes.tool_node import(
#     tool_agent
# )
# from graph.nodes.router_nodes import (
#     rag_router,
#     general_router,
#     grievance_router
#     # route_selected_tool
# )

from graph.nodes.fetch_memory import(
    memory_fetch_node
)

from graph.nodes.update_memory import(
    memory_update_node
)

from graph.nodes.feedback import (
    feedback_improve_node
)

def start_router(state):

    if state.get("feedback_mode"):
        return "feedback"

    return "normal"

checkpointer = SqliteSaver(conn=checkpoint_conn)

builder = StateGraph(GraphState)

# =========================
# Nodes
# =========================

builder.add_node(
    "text_input",
    text_input_node
)
 
# builder.add_node(
#     "tool_agent",
#     tool_agent
# )
builder.add_node(
    "intent_classifier",
    intent
)

builder.add_node(
    "fetch_memory",
    memory_fetch_node
)

builder.add_node(
    "grievance_entry",
    grievance_entry_node
)

# builder.add_node(
#     "rag_router",
#     rag_router
# )

builder.add_node(
    "general",
    general_node
)

# builder.add_node(
#     "grievance_router",
#     grievance_router
# )

# builder.add_node(
#     "general_router",
#     general_router
# )

builder.add_node(
    "filter",
    extract_filters_from_llm_node
)

builder.add_node(
    "retrieve",
    retrieve_node
)

builder.add_node(
    "answer",
    answer_node
)

builder.add_node(
    "grievance",
    grievance_tool_node
)

builder.add_node(
    "grievance_formatter",
    grievance_formatter_node
)

builder.add_node(
    "translate",
    translate_node_for_user
)

builder.add_node(
    "dictate",
    dictate_answer_node
)

builder.add_node(
    "update_memory",
    memory_update_node
)
builder.add_node(
    "feedback_improve",
    feedback_improve_node
)
# =========================
# Flow
# =========================

builder.add_conditional_edges(
    START,
    start_router,
    {
        "feedback": "feedback_improve",
        "normal": "text_input"
    }
)

builder.add_edge(
    "text_input",
    "fetch_memory"
)

# builder.add_edge(
#     "fetch_memory",
#     "tool_agent"
# )

builder.add_edge(
    "fetch_memory",
    "intent_classifier"
)

builder.add_conditional_edges(
    "intent_classifier",
    route_intent,
    {
        "rag": "filter",
        "grievance": "grievance_entry",
        "general": "general"
    }
)
# builder.add_conditional_edges(
#     "tool_agent",
#     route_selected_tool,
#     {
#         "rag": "rag_router",
#         "grievance": "grievance_router",
#         "general": "general_router"
#     }
# )

# =========================
# RAG Flow
# =========================
# builder.add_edge(
#     "rag_router",
#     "filter"
# )

builder.add_edge(
    "filter",
    "retrieve"
)

builder.add_edge(
    "retrieve",
    "answer"
)

builder.add_edge(
    "answer",
    "update_memory"
)

# =========================
# Grievance Flow
# =========================
# builder.add_edge(
#     "grievance_router",
#     "grievance_entry"
# )

builder.add_edge(
    "grievance_entry",
    "grievance"
)

builder.add_edge(
    "grievance",
    "grievance_formatter"
)

builder.add_edge(
    "grievance_formatter",
    "update_memory"
)

# =========================
# General Flow
# =========================

# builder.add_edge(
#     "general_router",
#     "general"
# )

builder.add_edge("general", "update_memory")

builder.add_edge(
    "feedback_improve",
    "translate"
)
builder.add_edge("update_memory", "translate")
# =========================
# End
# =========================

builder.add_conditional_edges(
    "translate",
    route_translation,
    {
        "text": END,
        "audio": "dictate"
    }
)


builder.add_edge(
    "dictate",
    END
)

graph = builder.compile(
    checkpointer=checkpointer
)

print("Graph Compiled")