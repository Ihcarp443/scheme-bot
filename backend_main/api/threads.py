from fastapi import APIRouter

from db.thread_repository import get_all_threads

router = APIRouter()

@router.get("/")
async def list_threads():

    return {
        "success": True,
        "threads": get_all_threads()
    }

from graph.graph_builder import graph
@router.get("/{thread_id}")
async def get_thread_messages(
    thread_id: str
):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:

        state = graph.get_state(config)

        return {
            "success": True,
            "thread_id": thread_id,
            "state": state.values
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }