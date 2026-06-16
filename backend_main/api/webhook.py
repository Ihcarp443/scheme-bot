from fastapi import Request, APIRouter
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from graph.graph_builder import graph
from fastapi import BackgroundTasks, Request
router = APIRouter()
import os
from twilio.rest import Client
from dotenv import load_dotenv


load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
 

def process_message(user_msg):

    config = {
        "configurable": {
            "thread_id": "10001"
        }
    }

    state = {
        "user_id": "20002",
        "input_type": "text",
        "input_text": user_msg,
        "channel": "whatsapp",
        "messages": [],
        "complaint_data": {}
    }

    try:
        result = graph.invoke(state, config=config)

        answer = result.get(
            "final_answer",
            "Sorry, I couldn't process your request."
        )

    except Exception as e:
        print("BACKGROUND ERROR:", e)

        answer = (
            "❌ Sorry, something went wrong while processing your request. "
            "Please try again later."
        )
    user_number=os.getenv("USER_WHATSAPP_NUMBER")
    client.messages.create(
        from_=TWILIO_NUMBER,
        to=user_number,
        body=answer
    )
@router.post("/whatsapp/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks
):

    form = await request.form()

    user_msg = form.get("Body") or "Hi"

    print("Received WhatsApp message:", user_msg)

    background_tasks.add_task(
        process_message,
        user_msg,
    )

    return {"status": "received"}