from services.llm_service import model
from langchain_core.messages import HumanMessage, AIMessage
def answer_node(state):

    context = "\n\n".join(
        doc.page_content
        for doc in state["docs"]
    )

    question = state["query_en"]

    history = state["messages"]

    prompt = f"""
  You are a helpful AI assistant.



  Use the following conversation history and retrieved context to answer the user's question accurately.



  ---------------------
  Conversation History:
  {history}



  ---------------------
  Retrieved Context:
  {context}



  ---------------------
  Current Question:
  {question}



  ---------------------
  Instructions:
  - Use retrieved context as primary source of truth
  - Use chat history for continuity
  - If answer is not in context, say "I don’t know based on available data"
  - Keep answer clear and concise



  Answer:
  """

    response = model.invoke(prompt)

    return {
        "answer_en": response.content
    }