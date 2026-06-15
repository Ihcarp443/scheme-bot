from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, AIMessage
from graph.state import GraphState
from services.grievance_service import (
    simulate_payment_status,
    extract_application_data
)
from services.llm_service import model


GRIEVANCE_TYPES = {
    "payment_delay": [
        "application_id"
    ],
    "application_issue": [
        "application_id"
    ]
}


def grievance_tool_node(state: GraphState):

    # print("FULL STATE")
    # print(state)

    print(
        "complaint_data:",
        state.get("complaint_data")
    )

    query = state.get("query_en")

    data = dict(
        state.get(
            "complaint_data",
            {}
        )
    )

    issue_type = state.get(
        "issue_type"
    )

    required = GRIEVANCE_TYPES.get(
        issue_type,
        []
    )

    extracted = extract_application_data(
        query,
        required
    )

    for k, v in extracted.items():

        if v and k not in data:

            data[k] = v

    missing = [
        f
        for f in required
        if not data.get(f)
    ]

    print("Missing:", missing)

    if missing:

        questions_map = {
            "application_id":
                "Please provide your application ID"
        }

        return interrupt({
            "type": "ASK_USER",
            "missing_fields": missing,
            "questions": [
                questions_map[f]
                for f in missing
            ],
            "partial_data": data
        })
    print("All data present, processing grievance...")

    if issue_type =="application_issue" :
    # if issue_type == "payment_delay":
        result = simulate_payment_status(
            data
        )

        return {
            "final_answer": f"""
            Status: {result['status'].upper()}
            Message: {result['message']}
            """
        }

    if issue_type == "payment_delay":
    # if issue_type =="application_issue":
        preview = f"""
            # Complaint Preview

            # Application ID:
            # {data['application_id']}

            # Issue:
            # {query}
            # """
        print("Preview:", preview)
        # if confirmed:

        ticket = (
            "TICKET-"
            + str(
                abs(
                    hash(
                        str(data)
                    )
                ) % 100000
            )
        )

        return {
            "final_answer":
            f"{preview}✅ Complaint submitted successfully.\nTicket: {ticket}"
        }

        # return {
        #     "final_answer":
        #     "❌ Complaint cancelled."
        # }

    return {
        "final_answer":
        "Unable to process grievance."
    }


def grievance_formatter_node(
    state: GraphState
):

    grievance_response = state.get(
        "final_answer",
        ""
    )

    prompt = f"""
Convert the following system response
into a user-friendly message.

Response:
{grievance_response}

Instructions:
- Keep it polite
- Keep it concise
- Do not change meaning
- Do not add information
"""

    response = model.invoke(
        prompt
    )

    return {
        "answer_en":
        response.content,
        "messages": [
            AIMessage(content=response.content)
        ]
    }


        # confirmed = state.get(
        #     "confirmed"
        # )

        # if confirmed is None:

            # preview = f"""
            # Complaint Preview

            # Application ID:
            # {data['application_id']}

            # Issue:
            # {query}
            # """

            # return interrupt({
            #     "type": "CONFIRM",
            #     "preview": preview,
            #     "data": data
            # })