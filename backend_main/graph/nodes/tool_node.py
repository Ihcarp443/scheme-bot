from services.llm_service import model
# from services.llm_service import model
from graph.state import GraphState
from graph.nodes.router_nodes import(
    rag_router,
    grievance_router,
    general_router
)

tools = [
    rag_router,
    grievance_router,
    general_router
]

tool_model = model.bind_tools(tools)


def tool_agent(state: GraphState):
    query = state["query_en"]

    response = tool_model.invoke(query)

    if not response.tool_calls:
        return {
            "selected_route": "general"
        }

    tool_name = response.tool_calls[0]["name"]

    mapping = {
        "rag_router": "rag",
        "grievance_router": "grievance",
        "general_router": "general"
    }

    return {
        "selected_route": mapping.get(tool_name, "general")
    }