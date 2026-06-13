from fastapi import APIRouter
from pydantic import BaseModel
import uuid
import traceback
from graph.graph_builder import graph
from db.thread_repository import save_thread
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    input_type: str


@router.post("/chat")
async def chat(req: ChatRequest):
    print(req)
    if req.thread_id == None:
        thread_id = req.thread_id or str(uuid.uuid4())
        save_thread(
            thread_id,
            title=req.message[:50]
        )
    else:
        thread_id = req.thread_id

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = {
        # "input_type": "text",
        "input_type": req.input_type,
        "input_text": req.message,
        "messages": [],
        "complaint_data": {}
    }

    try:
        result = graph.invoke(
            state,
            config=config
        )

        # Handle LangGraph interrupts
        if "__interrupt__" in result:

            interrupt_data = (
                result["__interrupt__"][0]
                .value
            )

            return {
                "success": True,
                "thread_id": thread_id,
                "interrupt": True,
                "data": interrupt_data
            }

        return {
            "success": True,
            "thread_id": thread_id,
            "interrupt": False,
            "answer": result.get("final_answer", ""),
            "audio": result.get("filename",""),
            "user_lang":result.get("user_lang")
        }
        

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "thread_id": thread_id,
            "error": str(e)
        }