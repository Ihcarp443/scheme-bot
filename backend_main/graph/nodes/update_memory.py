import json

from services.llm_service import model
from db.memory import save_memory
from graph.state import GraphState
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from typing import Optional

class UserMemory(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[str] = None
    preferred_language: Optional[str] = None
    family_category: Optional[str] = None
    
def memory_update_node(state: GraphState):

    user_id = state["user_id"]
    query = state["query_en"]
    parser = PydanticOutputParser(
        pydantic_object=UserMemory
    )
    prompt = f"""
You are a memory extraction system for a government scheme assistant.

Extract only information that is useful for future conversations.

Remember:
- Name
- State
- District
- Age
- Gender
- Occupation
- Income
- Preferred language
- Family category (farmer, student, worker, etc.)

Do not extract temporary questions or unrelated information.

{parser.get_format_instructions()}

User message:
{query}
"""
    try:
        response = model.invoke(prompt)
        memories = parser.parse(response.content)
        memory_dict = memories.model_dump(exclude_none=True)
        print("MEMORY UPDATE NODE:", memory_dict)
        for key, value in memory_dict.items():
            save_memory(
                user_id,
                key,
                str(value)
            )
    except Exception as e:
        print("Memory update error:", e)

    return {}

