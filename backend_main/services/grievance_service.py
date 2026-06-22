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
            "status": "submitted",
            "message": "Application submitted successfully and awaiting review."
        },
        {
            "status": "under_review",
            "message": "Your application is currently under review by the concerned department."
        },
        {
            "status": "verification_in_progress",
            "message": "Field and document verification is in progress."
        },
        {
            "status": "approved",
            "message": "Your application has been approved."
        },
        {
            "status": "rejected",
            "message": "Your application has been rejected due to eligibility criteria not being met."
        },
        {
            "status": "payment_processing",
            "message": "Benefit disbursement has been initiated and is being processed."
        },
        {
            "status": "success",
            "message": "Payment has been credited successfully to your bank account."
        },
        {
            "status": "pending",
            "message": "Payment is under processing."
        },
        {
            "status": "failed",
            "message": "Bank account verification failed."
        },
        {
            "status": "payment_failed",
            "message": "Payment could not be processed due to bank account issues."
        },
        {
            "status": "on_hold",
            "message": "Application is temporarily on hold pending further verification."
        }
    ]

    result = random.choice(responses)

    return {
        "application_id": data["application_id"],
        "status": result["status"],
        "message": result["message"]
    }


