import re
import random
def extract_application_data(
    query: str,
    required_fields: list
):

    data = {}

    match = re.search(r"\d+", query)

    if match:
        data["application_id"] = match.group()

    return data

def simulate_payment_status(data):

    responses = [
        {
            "status": "success",
            "message": "Payment already credited successfully."
        },
        {
            "status": "pending",
            "message": "Payment is under processing."
        },
        {
            "status": "failed",
            "message": "Bank account verification failed."
        }
    ]

    result = random.choice(responses)

    return {
        "application_id": data["application_id"],
        "status": result["status"],
        "message": result["message"]
    }