from fastapi import Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from fastapi import APIRouter
from graph.graph_builder import graph
router = APIRouter()
@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    user_msg = form.get("Body")
    if not user_msg:
        user_msg = "Hi"
    # user_number = form.get("From").replace("whatsapp:", "")
    thread_id = "103"
    config = {
    "configurable": {
        "thread_id": thread_id
    }
}
    # 1. Call your LangGraph pipeline
    state = {
        "user_id": "0007",
        "input_type": "text",
        "input_text": user_msg,
        "channel":"whatsapp",
        "messages": [],
        "complaint_data": {}
    }

    result = graph.invoke(state, config=config)

    bot_reply = result.get("final_answer", "Sorry, I couldn't process that.")

    # 2. Twilio response format
    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_reply)

    return Response(content=str(twilio_resp), media_type="application/xml")