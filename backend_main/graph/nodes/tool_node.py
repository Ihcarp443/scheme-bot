# from services.llm_service import model
# from graph.state import GraphState
# from graph.nodes.router_nodes import(
#     rag_router,
#     grievance_router,
#     general_router
# )

# tools = [
#     rag_router,
#     grievance_router,
#     general_router
# ]

# tool_model = model.bind_tools(tools)


# def tool_agent(state: GraphState):
#     query = state["query_en"]
#     memory = state.get("memory", {})

#     prompt = f"""
#         Classify query into one word:
#         rag, grievance, general

#         Rules:
#         rag = schemes/eligibility/benefits
#         grievance = payment/status/issues/complaints
#         general = greetings or unrelated

#         User:
#         {memory}

#         Query:
#         {query}
#         """

#     response = model.invoke(prompt)

#     route = response.content.strip().lower()
#     print("This is routes selected: ",route)
#     return {
#         "selected_route": route
#     }

# from services.llm_service import model
# from graph.state import GraphState

