from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from db.sqlite import get_db_connection
from graph.state import GraphState

from graph.nodes.intent import (
    agent_node,
    route_from_agent
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

# checkpointer = MemorySaver()
conn = get_db_connection()

# checkpointer = SqliteSaver(conn)
checkpointer = SqliteSaver(conn=conn)

builder = StateGraph(GraphState)

# =========================
# Nodes
# =========================


builder.add_node(
    "text_input",
    text_input_node
)

builder.add_node(
    "agent",
    agent_node
)

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
    "general",
    general_node
)
# =========================
# Flow
# =========================

builder.add_edge(
    START,
    "text_input"
)

builder.add_edge(
    "text_input",
    "agent"
)

builder.add_conditional_edges(
    "agent",
    route_from_agent,
    {
        "rag": "filter",
        "grievance": "grievance",
        "general": "general"
    }
)

# =========================
# RAG Flow
# =========================

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
    "translate"
)

# =========================
# Grievance Flow
# =========================

builder.add_edge(
    "grievance",
    "grievance_formatter"
)

builder.add_edge(
    "grievance_formatter",
    "translate"
)

builder.add_edge("general", "translate")

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