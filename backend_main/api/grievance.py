# api/grievance.py
from fastapi import APIRouter
from pydantic import BaseModel
from langgraph.types import Command
from graph.graph_builder import graph

router = APIRouter()

class ResumeRequest(BaseModel):
    thread_id: str
    data: dict

@router.post("/resume")
async def resume_grievance(req: ResumeRequest):
    print(req)
    config = {
        "configurable": {
            "thread_id": req.thread_id
        }
    }

    current_state = graph.get_state(config)

    existing = current_state.values.get(
        "complaint_data",
        {}
    )

    result = graph.invoke(
        Command(
            resume=req.data,
            update={
                "complaint_data": {
                    **existing,
                    **req.data
                }
            }
        ),
        config=config
    )

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0].value

        return {
            "status": "interrupt",
            "interrupt": interrupt_data,
        }

    return {
        "status": "completed",
        "answer": result.get("final_answer"),
        "user_lang":result.get("user_lang")
    }