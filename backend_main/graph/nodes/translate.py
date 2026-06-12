from services.sarvam_service import (
    translate_to_english,
    translate_to_user_language,
    text_to_speech
)

from langchain_core.messages import HumanMessage,AIMessage


def text_input_node(state):
    result = translate_to_english(
        state["input_text"]
    )
    print("user_lang",result["user_lang"])
    print("result",result)
    return {
        "query_en": result["query"],
        "user_lang": result["user_lang"],
        "messages": [
            HumanMessage(content=result["query"])
        ]
    }


def translate_node_for_user(state):

    print("Translate for user: ")
    print(state["user_lang"])
    translated = translate_to_user_language(
        state["answer_en"],
        state["user_lang"]
    )

    return {
        "final_answer": translated,
        "messages": [
            AIMessage(content=translated)
        ]
    }

def dictate_answer_node(state):
    print("Entered dictate node")
    result = text_to_speech(state)
    return {"filename":result}

def route_translation(state):
    if state["input_type"] == "text":
        return "text"

    return "audio"