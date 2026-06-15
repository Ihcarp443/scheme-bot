from graph.state import GraphState
from langchain_core.tools import tool

@tool
def rag_router():
    """
    Select this capability when the user wants information about 
    government schemes.

    Use for:
    - Checking eligibility for a scheme
    - Understanding scheme benefits and financial assistance
    - Knowing required documents
    - Learning the application process
    - How to apply for a scheme
    - Comparing government schemes
    - Understanding rules, conditions, and official details

    Do NOT use this for users who have already applied and are
    facing issues such as payment delays or application problems.
    """
    print("Entered RAG router")
    return {}

@tool
def grievance_router():
    """
    Select this capability when the user has already submitted a 
    government scheme application and is facing an issue.

    Use for:
    - Payment not received
    - Payment delay or pending payment
    - Application rejection
    - Application status not updated
    - Incorrect information in a submitted application
    - Any complaint or issue after applying for a scheme

    Do NOT use this for asking about scheme eligibility, benefits,
    required documents, or the application procedure.
    """
    print("Entered GRIEVANCE router")
    return {}

@tool
def general_router():
    """
    Select this capability for conversations not related to 
    government schemes or grievances.

    Use for:
    - Greetings and introductions
    - Casual conversation
    - Questions about programming or technology
    - General knowledge questions
    - Any unrelated topic

    Do NOT use this for government scheme information or
    application-related issues.
    """
    print("Entered GENERAL ROUTER")
    return {}

def route_selected_tool(state: GraphState):
    return state["selected_route"]