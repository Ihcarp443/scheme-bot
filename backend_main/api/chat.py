from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import uuid
import traceback
from graph.graph_builder import graph
from db.thread_repository import save_thread
from services.exceptions import(
    TranslationError,
    UnsupportedLanguageError
)

router = APIRouter()

print("Chat triggered successfully")

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    input_type: str
    user_id:str

@router.post("/chat")
async def chat(req: ChatRequest):
    print(req)
    if req.thread_id is None:
        thread_id = req.thread_id or str(uuid.uuid4())
        save_thread(
            thread_id,
            user_id=req.user_id,
            title=req.message[:50],
            
        )
    else:
        thread_id = req.thread_id
    
    user_id=req.user_id
    print("user_id",user_id)
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    state = {
        # "input_type": "text",
        "user_id":user_id,
        "input_type": req.input_type,
        "input_text": req.message,
        "channel":"website",
        "messages": [],
        "complaint_data": {},
        "suggested_ques":[]
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
            "user_lang":result.get("user_lang"),
            "suggested_ques":result.get("suggested_ques"),
            "input_type": result.get("input_type")
        }
    except UnsupportedLanguageError:
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail="Language not supported"
        )
    except TranslationError as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Unable to process your message. Please try again."
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )

