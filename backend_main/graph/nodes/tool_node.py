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
    memory = state.get("memory", {})

    # prompt = f"""
    # You are an intent classifier for a government scheme assistant.
    
    # Available routes:
    
    # 1. rag
    # Use this when the user is:
    # - asking about government schemes
    # - asking eligibility
    # - asking benefits
    # - asking "what schemes can help me"
    # - asking a question that can be answered using their stored profile
    
    # 2. grievance
    # Use for complaints, application issues, payment issues.
    
    # 3. general
    # Use only for casual conversation, greetings, or unrelated topics.
    
    
    # User Profile:
    # {memory}
    
    
    # Current Query:
    # {query}
    
    
    # Important:
    # If the query is vague but the user profile gives enough information to search for relevant schemes,
    # choose "rag".
    
    # Return only one word:
    # rag, grievance, or general.
    # """
    prompt = f"""
        You are an intent classifier for a government scheme assistant.

        You must classify the user query into exactly ONE of the following routes:

        1. rag
        Use this when the user is:
        - asking about government schemes
        - asking eligibility
        - asking benefits
        - asking what schemes are available
        - asking which scheme they qualify for
        - asking questions that can be answered using their stored profile

        2. grievance
        Use this when the user is talking about:
        - payment not received or delayed
        - application status (approved / pending / rejected)
        - application tracking
        - scheme money issues
        - subsidy not credited
        - DBT / fund transfer issues
        - complaints or grievance raising
        - errors in application
        - asking for update using application ID / reference number
        - any numeric ID (application number, reference number, payment ID) if context is unclear
        - words like: "not received", "pending", "delayed", "stuck", "problem", "issue", "complaint", "status", "update"

        IMPORTANT RULE:
        If the message contains ANY sign of:
        - money
        - payment
        - application status
        - complaint
        - reference number or numeric ID
        ➡ ALWAYS choose "grievance"

        Even if the message is short like "12422", "status?", "not received", etc.

        3. general
        Use only for:
        - greetings (hi, hello, कैसे हो)
        - casual conversation
        - unrelated topics not connected to schemes or applications

        User Profile:
        {memory}

        Current Query:
        {query}


        Return only one word:
        rag, grievance, or general
        """
    response = tool_model.invoke(prompt)
    print("tool_call_response:",response)
    if not response.tool_calls:
        return {
            "selected_route": "general"
        }

    tool_name = response.tool_calls[0]["name"]

    mapping = {
        "rag_router": "rag",
        "grievance_router": "grievance",
        "general_router_    ": "general"
    }

    return {
        "selected_route": mapping.get(tool_name, "general")
    }