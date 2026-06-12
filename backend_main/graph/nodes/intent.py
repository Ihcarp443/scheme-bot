from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from services.llm_service import model
from graph.state import GraphState


class IntentSchema(BaseModel):
    intent: Literal["grievance", "rag", "general"] = Field(
        description="Overall intent of the query"
    )

    issue_type: Optional[
        Literal["payment_delay", "application_issue"]
    ] = Field(
        default=None,
        description="Type of grievance if intent is grievance"
    )


parser = JsonOutputParser(
    pydantic_object=IntentSchema
)


def run_intent_detection(state: GraphState):

    query = state["query_en"].lower()

    prompt = f"""
You are an intelligent intent classification engine for a government scheme assistant.

Classify the user query into ONE of the following:

1. grievance
- User is reporting an issue after applying
- Examples:
  payment not received, application rejected, status not updated

2. rag
- User is asking about schemes
- Examples:
  eligibility, benefits, required documents, how to apply

3. general
- Greetings
- Small talk
- Coding questions
- Anything unrelated to government schemes or grievances

RULES:
- grievance ONLY if user is reporting a problem
- rag ONLY if user is asking scheme information
- general for everything else
- issue_type ONLY when intent = grievance
- issue_type must be null otherwise

IMPORTANT:
Return ONLY valid JSON matching the format below.

{parser.get_format_instructions()}

User Query:
{query}
"""

    response = model.invoke(prompt)

    return parser.parse(response.content)

    # response = model.invoke(prompt)

    # return parser.parse(response.content)


def agent_node(state: GraphState):

    try:
        output = run_intent_detection(state)

        intent = output.get("intent", "general")
        issue_type = output.get("issue_type")

        print("Intent Detection:", output)

    except Exception as e:

        print("Intent Detection Error:", e)

        intent = "general"
        issue_type = None

    return {
        "intent": intent,
        "issue_type": issue_type,
        "complaint_data": {
            "issue_type": issue_type
        }
    }

def route_from_agent(state: GraphState):

    return state["intent"]

# from typing import Optional, Literal

# from pydantic import BaseModel, Field
# from langchain_core.output_parsers import JsonOutputParser

# from services.llm_service import model
# from graph.state import GraphState


# class IntentSchema(BaseModel):
#     intent: Literal["grievance", "rag"] = Field(
#         description="Overall intent of the query"
#     )

#     issue_type: Optional[
#         Literal["payment_delay", "application_issue"]
#     ] = Field(
#         default=None,
#         description="Type of grievance if intent is grievance"
#     )


# parser = JsonOutputParser(
#     pydantic_object=IntentSchema
# )


# def run_intent_detection(state: GraphState):

#     query = state["query_en"].lower()

#     prompt = f"""
# You are an intelligent assistant for a government scheme chatbot.

# Your job is to classify the user query based on its intent and context.

# Categories:

# 1. grievance
# - User is reporting a problem after applying to a scheme
# - Examples:
#     - payment not received
#     - application rejected
#     - no status update

# For grievance identify issue_type:
#     - payment_delay
#     - application_issue

# 2. rag
# - User is asking for general information
# - Examples:
#     - scheme details
#     - eligibility
#     - benefits
#     - how to apply

# IMPORTANT RULES:
# - If user is reporting a problem, classify as grievance
# - If user is seeking information, classify as rag
# - Only assign issue_type when intent = grievance
# - Keep issue_type null for rag

# {parser.get_format_instructions()}

# User Query:
# {query}
# """

#     response = model.invoke(prompt)

#     return parser.parse(response.content)


# def agent_node(state: GraphState):

#     try:

#         output = run_intent_detection(state)

#         intent = output["intent"]
#         issue_type = output.get("issue_type")

#         print("Intent Detection:", output)

#     except Exception as e:

#         print("Intent Detection Error:", e)

#         intent = "rag"
#         issue_type = None

#     return {
#         "intent": intent,
#         "issue_type": issue_type,
#         "complaint_data": {
#             "issue_type": issue_type
#         }
#     }


# def route_from_agent(state: GraphState):

#     if state["intent"] == "grievance":
#         return "grievance"

#     return "rag"