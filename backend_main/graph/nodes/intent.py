from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from services.llm_service import model
from graph.state import GraphState


# class IntentSchema(BaseModel):

class GrievanceSchema(BaseModel):
    # intent: Literal["grievance", "rag", "general"] = Field(
    #     description="Overall intent of the query"
    # )

    issue_type: Optional[
        Literal["payment_delay", "application_issue"]
    ] = Field(
        default=None,
        description="Type of grievance if intent is grievance"
    )


parser = JsonOutputParser(
    pydantic_object=GrievanceSchema
)


# def run_intent_detection(state: GraphState):
def extract_grievance_type(state: GraphState):
    query = state["query_en"].lower()

#     prompt = f"""
# You are an intelligent intent classification engine for a government scheme assistant.

# Classify the user query into ONE of the following:

# 1. grievance
# - User is reporting an issue after applying
# - Examples:
#   payment not received, application rejected, status not updated

# 2. rag
# - User is asking about schemes
# - Examples:
#   eligibility, benefits, required documents, how to apply

# 3. general
# - Greetings
# - Small talk
# - Coding questions
# - Anything unrelated to government schemes or grievances

# RULES:
# - grievance ONLY if user is reporting a problem
# - rag ONLY if user is asking scheme information
# - general for everything else
# - issue_type ONLY when intent = grievance
# - issue_type must be null otherwise

# IMPORTANT:
# Return ONLY valid JSON matching the format below.

# {parser.get_format_instructions()}

# User Query:
# {query}
# """


    prompt = f"""
        You are a grievance classification engine.
        
        A user has already been identified as having a grievance related to a government scheme application.
        
        Classify the grievance into one of the following types:
        
        1. payment_delay
        - User has not received payment
        - Payment is pending
        - Amount not credited
        
        2. application_issue
        - Application rejected
        - Status not updated
        - Incorrect information
        - Any other application related problem
        
        Return only valid JSON.
        
        {parser.get_format_instructions()}
        
        User Query:
        {query}
        """

    response = model.invoke(prompt)

    return parser.parse(response.content)

    # response = model.invoke(prompt)

    # return parser.parse(response.content)


# def agent_node(state: GraphState):
def grievance_entry_node(state: GraphState):
    try:
        output = extract_grievance_type(state)

        # intent = output.get("intent", "general")
        issue_type = output.get("issue_type")

        print("Intent Detection:", output)

    except Exception as e:
        print("Grievance Detection Error:", e)
        issue_type = None

    return {
        # "intent": intent,
        "issue_type": issue_type,
        "complaint_data": {
            "issue_type": issue_type
        }
    }




# def route_from_agent(state: GraphState):

#     return state["intent"]

