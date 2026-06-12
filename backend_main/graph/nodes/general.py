
from graph.state import GraphState
from langchain_core.messages import AIMessage, HumanMessage

# def general_node(state: GraphState):
#     print("General Node State:", state)

#     from services.llm_service import model

#     response = model.invoke(state["input_text"])

#     return {
#         "answer_en": response.content
#     }
def general_node(state: GraphState):

    print("General Node State:", state)

    from services.llm_service import model

    messages = state.get("messages", [])

    response = model.invoke(messages)

    return {
        # "messages": messages + [AIMessage(content=response.content)],
        "answer_en": response.content
    }