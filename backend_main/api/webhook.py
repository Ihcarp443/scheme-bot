from fastapi import Request, APIRouter
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from graph.graph_builder import graph
from fastapi import BackgroundTasks, Request
router = APIRouter()
import os
from twilio.rest import Client
from dotenv import load_dotenv
from services.exceptions import(
    TranslationError,
    UnsupportedLanguageError
)


load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
interrupt = False


def process_message(user_msg, user_number):
    thread_id= user_number+'009'
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = {
        "user_id": "10005",
        "input_type": "text",
        "input_text": user_msg,
        "channel": "whatsapp",
        "messages": [],
        "complaint_data": {},
        "suggested_ques":[]
    }

    try:
        from langgraph.types import Command

        snapshot = graph.get_state(config)

        print("========== SNAPSHOT ==========")
        print(snapshot)

        # Resume interrupted flow
        if snapshot.interrupts:
            print("RESUMING INTERRUPTED FLOW")

            result = graph.invoke(
                Command(resume=user_msg),
                config=config
            )

        # Start new flow
        else:
            print("STARTING NEW FLOW")

            result = graph.invoke(
                state,
                config=config
            )

        print("========== RESULT ==========")
        print(result)

        if "__interrupt__" in result:

            interrupt_data = (
                result["__interrupt__"][0]
                .value
            )

            answer = interrupt_data.get(
                "question",
                "Please provide the required information."
            )

        else:

            answer = result.get(
                "final_answer"
            ) or result.get(
                "answer_en",
                "Sorry, I couldn't process your request."
            )

    except (
        TranslationError,
        UnsupportedLanguageError
    ) as e:

        print("Translation Error:", e)
        answer = (
            "Sorry, something wrong on our end."
        )

    except Exception as e:
        print("BACKGROUND ERROR")
        print("Error:",e)
        answer = (
            "Sorry, something went wrong. Please try again later."
        )

    user_number = os.getenv(
        "USER_WHATSAPP_NUMBER"
    )

    try:

        message = client.messages.create(
            from_=TWILIO_NUMBER,
            to=user_number,
            body=answer
        )

        print(
            "WhatsApp message sent:",
            message.sid
        )

    except Exception as e:

        print(
            "TWILIO SEND ERROR:",
            e
        )

@router.post("/whatsapp/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks
):

    form = await request.form()

    user_msg = form.get("Body") or "Hi"

    user_number = form.get("From")

    print("Message:", user_msg)
    print("From:", user_number)

    background_tasks.add_task(
        process_message,
        user_msg,
        user_number
    )

    return {"status": "received"}