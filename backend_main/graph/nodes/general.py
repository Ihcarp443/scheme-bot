
from graph.state import GraphState
from langchain_core.messages import AIMessage, HumanMessage

# def general_node(state: GraphState):
#     print("General Node State:", state)

#     from services.llm_service import model

#     response = model.invoke(state["input_text"])

#     return {
#         "answer_en": response.content
#     }





#CORRECT CODE

# def general_node(state: GraphState):

#     print("General Node State:", state)

#     from services.llm_service import model

#     messages = state.get("messages", [])

#     response = model.invoke(messages)

#     return {
#         # "messages": messages + [AIMessage(content=response.content)],
#         "answer_en": response.content
#     }





import json
from graph.state import GraphState


def general_node(state: GraphState):

    print("General Node State:", state)

    chat_history = state.get("chat_history", [])

    last_assistant_message = ""

    for msg in reversed(chat_history):
        if msg["role"] == "assistant":
            last_assistant_message = msg["text"]
            break


    SYSTEM_PROMPT = f"""
You are a helpful assistant.

Current user query:
{state["query_en"]}

Last assistant response:
{last_assistant_message}

Rules:

1. If the user is asking to translate the previous response into another language:
- Do not translate it.
- Return the previous assistant response in the "answer" field.
- Detect the requested language and return its language code.

Format:
{{
    "type": "translation_request",
    "answer": "text to be translated",
    "language_code": "language code"
}}

Language codes:
Hindi: hi-IN
English: en-IN
French: fr-FR
Tamil: ta-IN
Telugu: te-IN
Kannada: kn-IN
Malayalam: ml-IN
Marathi: mr-IN
Gujarati: gu-IN
Punjabi: pa-IN
Bengali: bn-IN


2. For all other user queries:
- Answer normally.
- Keep language code same as of the language of query
Format:
{{
    "type": "normal",
    "answer": "your response",
    "language_code": "language-code"
}}

Important:
- Always return only valid JSON.
- Never return markdown.
- Never add explanations.
- Never include any text outside JSON.
"""

    from services.llm_service import model

    response = model.invoke(SYSTEM_PROMPT)

    data = json.loads(response.content)

    print("General node data:", data)

    return {
        "answer_en": data.get("answer"),
        "user_lang": data.get("language_code"),
        "general_type": data.get("type")
    }